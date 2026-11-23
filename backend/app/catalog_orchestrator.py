"""Aggregate explicitly enabled STAC adapters behind CatalogProvider."""

import asyncio
from datetime import UTC, datetime
from typing import Sequence
from urllib.parse import quote, unquote

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

    The caller supplies the enabled adapters explicitly. This class never reads
    client-provided URLs or selects a provider from implicit defaults.
    """

    def __init__(self, adapters: Sequence[StacCatalogAdapter] = ()) -> None:
        self._adapters = tuple(adapters)
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

        jobs: list[tuple[StacCatalogAdapter, list[str]]] = []
        statuses_by_id: dict[str, ProviderStatus] = {}
        checked_at = datetime.now(UTC)
        for adapter in selected:
            capability = self._capabilities[adapter.capabilities().provider_id]
            collections = [
                collection
                for collection in request.collections
                if collection in capability.supported_collections
            ]
            if not collections:
                statuses_by_id[capability.provider_id] = ProviderStatus(
                    id=capability.provider_id,
                    status="unavailable",
                    last_checked=checked_at,
                    reason="collection_not_supported",
                )
                continue
            jobs.append((adapter, collections))

        if not jobs:
            raise CatalogQueryNotSupportedError()

        outcomes = await asyncio.gather(
            *(self._search_one(adapter, request, collections) for adapter, collections in jobs),
            return_exceptions=True,
        )

        scenes: list[Scene] = []
        successful = 0
        failed_errors: list[Exception] = []
        partial = False
        for (adapter, _), outcome in zip(jobs, outcomes, strict=True):
            provider_id = adapter.capabilities().provider_id
            checked_at = datetime.now(UTC)
            if isinstance(outcome, Exception):
                failed_errors.append(outcome)
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
                continue

            page_scenes, has_more = outcome
            successful += 1
            scenes.extend(page_scenes)
            if has_more:
                partial = True
                statuses_by_id[provider_id] = ProviderStatus(
                    id=provider_id,
                    status="partial",
                    last_checked=checked_at,
                    reason="more_results_available",
                )
            else:
                statuses_by_id[provider_id] = ProviderStatus(
                    id=provider_id,
                    status="success",
                    last_checked=checked_at,
                )

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

        statuses = [
            statuses_by_id[adapter.capabilities().provider_id]
            for adapter in selected
        ]
        if any(status.status == "unavailable" for status in statuses):
            partial = True

        unique_scenes: dict[str, Scene] = {}
        for scene in scenes:
            unique_scenes.setdefault(scene.key, scene)

        return SearchResponse(
            items=list(unique_scenes.values())[: request.limit],
            next_cursor=None,
            providers=statuses,
            partial=partial,
        )

    async def _search_one(
        self,
        adapter: StacCatalogAdapter,
        request: SearchRequest,
        collections: list[str],
    ) -> tuple[list[Scene], bool]:
        provider_id = adapter.capabilities().provider_id
        adapter_request = request.model_copy(
            update={"collections": collections, "providers": None}
        )
        page = await adapter.search(adapter_request)
        collection_context = collections[0] if len(collections) == 1 else None
        scenes = [
            normalize_stac_item(
                feature,
                provider_id=provider_id,
                collection_id=collection_context,
            )
            for feature in page.features
        ]
        return scenes, page.next_href is not None

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
