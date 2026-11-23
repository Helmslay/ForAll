"""Aggregate explicitly enabled STAC adapters behind CatalogProvider."""

import asyncio
import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Sequence
from urllib.parse import quote, unquote

from app.catalog_cursor import CatalogCursorCodec, InvalidCatalogCursor
from app.catalog_provider import (
    CatalogCapabilities,
    CatalogItemNotFoundError,
    CatalogProviderError,
    CatalogQueryNotSupportedError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)
from app.schemas.catalog import ProviderStatus, Scene, SearchRequest, SearchResponse
from app.stac_adapter import StacCatalogAdapter
from app.stac_normalizer import normalize_stac_item


class CatalogOrchestrator:
    """Fan out catalog searches and merge normalized results deterministically.

    The caller supplies enabled adapters explicitly. Continuation state is
    encrypted server-side and never returned as an upstream URL.
    """

    def __init__(
        self,
        adapters: Sequence[StacCatalogAdapter] = (),
        *,
        cursor_codec: CatalogCursorCodec | None = None,
    ) -> None:
        self._adapters = tuple(adapters)
        self._cursor_codec = cursor_codec
        capabilities = [adapter.capabilities() for adapter in self._adapters]
        provider_ids = [capability.provider_id for capability in capabilities]
        if len(provider_ids) != len(set(provider_ids)):
            raise ValueError("catalog provider IDs must be unique")
        self._capabilities: dict[str, CatalogCapabilities] = {
            capability.provider_id: capability for capability in capabilities
        }
        self._by_provider = {
            capability.provider_id: adapter
            for capability, adapter in zip(capabilities, self._adapters, strict=True)
        }

    def capabilities(self) -> CatalogCapabilities:
        """Return the union of configured adapter capabilities."""
        return CatalogCapabilities(
            provider_id="catalog-orchestrator",
            supported_collections=frozenset(
                collection
                for capability in self._capabilities.values()
                for collection in capability.supported_collections
            ),
            supported_bands=frozenset(
                band
                for capability in self._capabilities.values()
                for band in capability.supported_bands
            ),
        )

    async def search(self, request: SearchRequest) -> SearchResponse:
        selected = [
            adapter
            for adapter in self._adapters
            if request.providers is None
            or adapter.capabilities().provider_id in request.providers
        ]
        if not selected:
            raise CatalogUnavailableError()

        provider_ids = [adapter.capabilities().provider_id for adapter in selected]
        query_hash = self._query_hash(request)
        if request.cursor is not None:
            if self._cursor_codec is None:
                raise InvalidCatalogCursor("cursor encryption is unavailable")
            payload = self._cursor_codec.decode(
                request.cursor, expected_query_hash=query_hash
            )
            provider_states = self._validate_state(payload, provider_ids, request)
        else:
            provider_states = {
                provider_id: {"next_href": None, "buffer": []}
                for provider_id in provider_ids
            }

        statuses_by_id: dict[str, ProviderStatus] = {}
        checked_at = datetime.now(UTC)
        jobs: list[tuple[StacCatalogAdapter, list[str]]] = []
        for adapter in selected:
            provider_id = adapter.capabilities().provider_id
            capability = self._capabilities[provider_id]
            collections = [
                collection
                for collection in request.collections
                if collection in capability.supported_collections
            ]
            if not collections:
                statuses_by_id[provider_id] = ProviderStatus(
                    id=provider_id,
                    status="unavailable",
                    last_checked=checked_at,
                    reason="collection_not_supported",
                )
                continue
            jobs.append((adapter, collections))

        if not jobs:
            raise CatalogQueryNotSupportedError()

        # Fetch first pages, or advance providers that still need results.
        should_fetch = {
            adapter.capabilities().provider_id
            for adapter, _ in jobs
            if request.cursor is None
            or (
                not provider_states[adapter.capabilities().provider_id]["buffer"]
                and provider_states[adapter.capabilities().provider_id]["next_href"]
            )
        }
        outcomes = await asyncio.gather(
            *(
                self._fetch_provider_page(
                    adapter,
                    request,
                    collections,
                    provider_states[adapter.capabilities().provider_id].get("next_href")
                    if request.cursor is not None
                    else None,
                )
                for adapter, collections in jobs
                if adapter.capabilities().provider_id in should_fetch
            ),
            return_exceptions=True,
        )

        successful = 0
        failed_errors: list[Exception] = []
        outcome_index = 0
        for adapter, collections in jobs:
            provider_id = adapter.capabilities().provider_id
            state = provider_states[provider_id]
            if provider_id not in should_fetch:
                if state["buffer"]:
                    successful += 1
                continue
            outcome = outcomes[outcome_index]
            outcome_index += 1
            checked_at = datetime.now(UTC)
            if isinstance(outcome, asyncio.CancelledError):
                raise outcome
            if isinstance(outcome, Exception):
                failed_errors.append(outcome)
                state["next_href"] = None
                statuses_by_id[provider_id] = ProviderStatus(
                    id=provider_id,
                    status="unavailable",
                    last_checked=checked_at,
                    reason=(
                        outcome.code
                        if isinstance(outcome, CatalogProviderError)
                        else "provider_error"
                    ),
                )
                if state["buffer"]:
                    successful += 1
                continue

            scenes, next_href = outcome
            successful += 1
            state["buffer"].extend(
                scene.model_dump(mode="json") for scene in scenes
            )
            state["next_href"] = next_href

        if successful == 0:
            if failed_errors and all(
                isinstance(error, CatalogQueryNotSupportedError)
                for error in failed_errors
            ):
                raise CatalogQueryNotSupportedError()
            if failed_errors and all(
                isinstance(error, CatalogRateLimitedError)
                for error in failed_errors
            ):
                raise CatalogRateLimitedError()
            raise CatalogUnavailableError()

        emitted_keys = list(
            payload.get("emitted_keys", []) if request.cursor is not None else []
        )
        emitted = set(emitted_keys)
        ordered_scenes: list[Scene] = []
        seen = set(emitted)
        for provider_id in provider_ids:
            for raw_scene in provider_states[provider_id]["buffer"]:
                scene = Scene.model_validate(raw_scene)
                if scene.provider != provider_id:
                    raise InvalidCatalogCursor("cursor provider state mismatch")
                if scene.key not in seen:
                    seen.add(scene.key)
                    ordered_scenes.append(scene)

        items = ordered_scenes[: request.limit]
        emitted_keys.extend(scene.key for scene in items)
        consumed = set(emitted_keys)
        for provider_id in provider_ids:
            retained: list[dict[str, Any]] = []
            local_seen: set[str] = set()
            for raw_scene in provider_states[provider_id]["buffer"]:
                scene = Scene.model_validate(raw_scene)
                if scene.key in consumed or scene.key in local_seen:
                    continue
                local_seen.add(scene.key)
                retained.append(raw_scene)
            provider_states[provider_id]["buffer"] = retained

        has_more = any(
            state["next_href"] is not None or state["buffer"]
            for state in provider_states.values()
        )
        next_cursor = None
        if has_more:
            if self._cursor_codec is None:
                self._mark_pagination_limit(
                    statuses_by_id, provider_states, provider_ids,
                    "cursor_encryption_unavailable",
                )
            else:
                try:
                    next_cursor = self._cursor_codec.encode(
                        {
                            "providers": [
                                {
                                    "id": provider_id,
                                    **provider_states[provider_id],
                                }
                                for provider_id in provider_ids
                            ],
                            "emitted_keys": emitted_keys,
                        },
                        query_hash=query_hash,
                    )
                except InvalidCatalogCursor:
                    self._mark_pagination_limit(
                        statuses_by_id, provider_states, provider_ids,
                        "pagination_state_limit",
                    )

        statuses: list[ProviderStatus] = []
        for adapter in selected:
            provider_id = adapter.capabilities().provider_id
            existing = statuses_by_id.get(provider_id)
            if existing is not None and existing.status == "unavailable":
                statuses.append(existing)
                continue
            state = provider_states[provider_id]
            if state["next_href"] is not None or state["buffer"]:
                statuses.append(
                    ProviderStatus(
                        id=provider_id,
                        status="partial",
                        last_checked=datetime.now(UTC),
                        reason=(
                            "more_results_available"
                            if next_cursor is not None
                            else (
                                "cursor_encryption_unavailable"
                                if self._cursor_codec is None
                                else "pagination_state_limit"
                            )
                        ),
                    )
                )
            else:
                statuses.append(
                    ProviderStatus(
                        id=provider_id,
                        status="success",
                        last_checked=datetime.now(UTC),
                    )
                )

        return SearchResponse(
            items=items,
            next_cursor=next_cursor,
            providers=statuses,
            partial=any(status.status != "success" for status in statuses),
        )

    @staticmethod
    def _query_hash(request: SearchRequest) -> str:
        query = request.model_dump(mode="json", exclude={"cursor"})
        canonical = json.dumps(
            query, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @staticmethod
    def _validate_state(
        payload: dict[str, Any],
        provider_ids: list[str],
        request: SearchRequest,
    ) -> dict[str, dict[str, Any]]:
        providers = payload.get("providers")
        emitted = payload.get("emitted_keys")
        if (
            not isinstance(providers, list)
            or not isinstance(emitted, list)
            or any(not isinstance(key, str) for key in emitted)
            or len(emitted) != len(set(emitted))
            or len(providers) != len(provider_ids)
        ):
            raise InvalidCatalogCursor("invalid cursor state")
        states: dict[str, dict[str, Any]] = {}
        for expected_id, entry in zip(provider_ids, providers, strict=True):
            if (
                not isinstance(entry, dict)
                or entry.get("id") != expected_id
                or set(entry) != {"id", "next_href", "buffer"}
                or (
                    entry["next_href"] is not None
                    and not isinstance(entry["next_href"], str)
                )
                or not isinstance(entry["buffer"], list)
            ):
                raise InvalidCatalogCursor("invalid cursor provider state")
            buffer: list[dict[str, Any]] = []
            for raw_scene in entry["buffer"]:
                try:
                    scene = Scene.model_validate(raw_scene)
                except Exception as exc:
                    raise InvalidCatalogCursor("invalid buffered scene") from exc
                if (
                    scene.provider != expected_id
                    or scene.collection not in request.collections
                ):
                    raise InvalidCatalogCursor("invalid buffered scene identity")
                buffer.append(scene.model_dump(mode="json"))
            states[expected_id] = {
                "next_href": entry["next_href"],
                "buffer": buffer,
            }
        return states

    async def _fetch_provider_page(
        self,
        adapter: StacCatalogAdapter,
        request: SearchRequest,
        collections: list[str],
        next_href: str | None,
    ) -> tuple[list[Scene], str | None]:
        provider_id = adapter.capabilities().provider_id
        if next_href is None:
            adapter_request = request.model_copy(
                update={"collections": collections, "providers": None, "cursor": None}
            )
            page = await adapter.search(adapter_request)
        else:
            page = await adapter.get_next_page(next_href)
        collection_context = collections[0] if len(collections) == 1 else None
        scenes: list[Scene] = []
        for feature in page.features:
            item_collection = feature.get("collection")
            if item_collection is not None and item_collection not in collections:
                raise CatalogProviderError(provider_id)
            scenes.append(
                normalize_stac_item(
                    feature,
                    provider_id=provider_id,
                    collection_id=collection_context,
                )
            )
        return scenes, page.next_href

    @staticmethod
    def _mark_pagination_limit(
        statuses: dict[str, ProviderStatus],
        states: dict[str, dict[str, Any]],
        provider_ids: list[str],
        reason: str,
    ) -> None:
        for provider_id in provider_ids:
            state = states[provider_id]
            if state["next_href"] is not None or state["buffer"]:
                statuses[provider_id] = ProviderStatus(
                    id=provider_id,
                    status="partial",
                    last_checked=datetime.now(UTC),
                    reason=reason,
                )

    async def get_item(self, scene_key: str) -> Scene:
        parts = scene_key.split(":", 2)
        if len(parts) != 3:
            raise CatalogItemNotFoundError()
        provider_id, collection_id, item_id = (unquote(part) for part in parts)
        canonical_key = ":".join(
            quote(part, safe="") for part in (provider_id, collection_id, item_id)
        )
        adapter = self._by_provider.get(provider_id)
        if (
            not provider_id
            or not collection_id
            or not item_id
            or canonical_key != scene_key
            or adapter is None
        ):
            raise CatalogItemNotFoundError()

        item = await adapter.get_item(collection_id, item_id)
        scene = normalize_stac_item(
            item,
            provider_id=provider_id,
            collection_id=collection_id,
        )
        if scene.key != scene_key:
            raise CatalogItemNotFoundError()
        return scene
