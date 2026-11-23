from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Callable

import pytest

from app.catalog_provider import (
    CatalogCapabilities,
    CatalogProvider,
    CatalogItemNotFoundError,
    CatalogQueryNotSupportedError,
    CatalogUnavailableError,
    CatalogRateLimitedError,
)
from app.schemas.catalog import SearchRequest
from app.stac_adapter import StacSearchPage
from app.catalog_orchestrator import CatalogOrchestrator

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "stac" / "valid_item.json").read_text()
)


def make_request(**changes: Any) -> SearchRequest:
    values: dict[str, Any] = {
        "bbox": [59.3, 56.7, 59.5, 56.9],
        "datetime": {
            "from": "2025-06-01T00:00:00Z",
            "to": "2025-06-30T23:59:59Z",
        },
        "collections": ["sentinel-2-l2a"],
        "providers": None,
        "limit": 20,
        "cursor": None,
    }
    values.update(changes)
    return SearchRequest.model_validate(values)


class FakeAdapter:
    def __init__(
        self,
        provider_id: str,
        *,
        collections: frozenset[str] = frozenset({"sentinel-2-l2a"}),
        features: list[dict[str, Any]] | None = None,
        error: Exception | None = None,
        next_href: str | None = None,
        on_search: Callable[[SearchRequest], Any] | None = None,
    ) -> None:
        self._capabilities = CatalogCapabilities(
            provider_id=provider_id,
            supported_collections=collections,
            supported_bands=frozenset({"B02", "B03", "B04", "B08"}),
        )
        self.features = features if features is not None else [FIXTURE]
        self.error = error
        self.next_href = next_href
        self.on_search = on_search
        self.requests: list[SearchRequest] = []
        self.item_requests: list[tuple[str, str]] = []

    def capabilities(self) -> CatalogCapabilities:
        return self._capabilities

    async def search(self, request: SearchRequest) -> StacSearchPage:
        self.requests.append(request)
        if self.on_search is not None:
            await self.on_search(request)
        if self.error is not None:
            raise self.error
        return StacSearchPage(tuple(self.features), self.next_href)

    async def get_item(self, collection_id: str, item_id: str) -> dict[str, Any]:
        self.item_requests.append((collection_id, item_id))
        if self.error is not None:
            raise self.error
        item = dict(FIXTURE)
        item["collection"] = collection_id
        item["id"] = item_id
        return item


@pytest.mark.asyncio
async def test_fans_out_concurrently_and_normalizes_results() -> None:
    started = 0
    both_started = asyncio.Event()

    async def wait_for_other(_: SearchRequest) -> None:
        nonlocal started
        started += 1
        if started == 2:
            both_started.set()
        await asyncio.wait_for(both_started.wait(), timeout=1)

    first = FakeAdapter("first", on_search=wait_for_other)
    second = FakeAdapter("second", on_search=wait_for_other)

    result = await CatalogOrchestrator([first, second]).search(make_request())

    assert started == 2
    assert [scene.provider for scene in result.items] == ["first", "second"]
    assert [status.id for status in result.providers] == ["first", "second"]
    assert all(status.status == "success" for status in result.providers)
    assert result.partial is False
    assert result.next_cursor is None


@pytest.mark.asyncio
async def test_provider_filter_and_collection_intersection() -> None:
    first = FakeAdapter(
        "first",
        collections=frozenset({"sentinel-2-l2a", "sentinel-2-l1c"}),
    )
    second = FakeAdapter("second")

    result = await CatalogOrchestrator([first, second]).search(
        make_request(
            providers=["first"],
            collections=["sentinel-2-l1c", "sentinel-2-l2a"],
        )
    )

    assert len(first.requests) == 1
    assert first.requests[0].collections == ["sentinel-2-l1c", "sentinel-2-l2a"]
    assert first.requests[0].providers is None
    assert second.requests == []
    assert [status.id for status in result.providers] == ["first"]


@pytest.mark.asyncio
async def test_deduplicates_by_scene_key_and_enforces_aggregate_limit() -> None:
    duplicate = FakeAdapter("first", features=[FIXTURE, FIXTURE, FIXTURE])
    second = FakeAdapter("second")

    result = await CatalogOrchestrator([duplicate, second]).search(
        make_request(limit=1)
    )

    assert len(result.items) == 1
    assert result.items[0].key == (
        "first:sentinel-2-l2a:synthetic-sentinel-2-valid-001"
    )


@pytest.mark.asyncio
async def test_one_provider_failure_does_not_erase_successful_results() -> None:
    successful = FakeAdapter("working")
    failed = FakeAdapter("offline", error=CatalogUnavailableError("offline"))

    result = await CatalogOrchestrator([successful, failed]).search(make_request())

    assert [scene.provider for scene in result.items] == ["working"]
    assert [(status.id, status.status, status.reason) for status in result.providers] == [
        ("working", "success", None),
        ("offline", "unavailable", "PROVIDER_UNAVAILABLE"),
    ]
    assert result.partial is True


@pytest.mark.asyncio
async def test_unsupported_collection_is_reported_without_blocking_other_provider() -> None:
    supported = FakeAdapter("supported")
    unsupported = FakeAdapter(
        "unsupported", collections=frozenset({"other-collection"})
    )

    result = await CatalogOrchestrator([supported, unsupported]).search(make_request())

    assert [scene.provider for scene in result.items] == ["supported"]
    assert [(status.id, status.status, status.reason) for status in result.providers] == [
        ("supported", "success", None),
        ("unsupported", "unavailable", "collection_not_supported"),
    ]
    assert result.partial is True


@pytest.mark.asyncio
async def test_all_unsupported_queries_preserve_domain_error() -> None:
    adapter = FakeAdapter("provider", error=CatalogQueryNotSupportedError("provider"))

    with pytest.raises(CatalogQueryNotSupportedError):
        await CatalogOrchestrator([adapter]).search(make_request())


@pytest.mark.asyncio
async def test_all_rate_limited_providers_preserve_rate_limit_error() -> None:
    adapter = FakeAdapter("provider", error=CatalogRateLimitedError("provider"))

    with pytest.raises(CatalogRateLimitedError):
        await CatalogOrchestrator([adapter]).search(make_request())


@pytest.mark.asyncio
async def test_all_provider_failures_return_safe_unavailable_error() -> None:
    first = FakeAdapter("first", error=RuntimeError("secret upstream url"))
    second = FakeAdapter("second", error=CatalogUnavailableError("second"))

    with pytest.raises(CatalogUnavailableError) as error:
        await CatalogOrchestrator([first, second]).search(make_request())

    assert str(error.value) == "Каталог временно недоступен"


@pytest.mark.asyncio
async def test_no_enabled_or_matching_adapter_returns_unavailable() -> None:
    with pytest.raises(CatalogUnavailableError):
        await CatalogOrchestrator().search(make_request())
    with pytest.raises(CatalogUnavailableError):
        await CatalogOrchestrator([FakeAdapter("first")]).search(
            make_request(providers=["not-enabled"])
        )


@pytest.mark.asyncio
async def test_provider_with_next_page_is_explicitly_marked_partial() -> None:
    adapter = FakeAdapter(
        "provider", next_href="https://catalog.example/search?page=2&token=secret"
    )

    result = await CatalogOrchestrator([adapter]).search(make_request())

    assert result.partial is True
    assert result.providers[0].status == "partial"
    assert result.providers[0].reason == "more_results_available"
    assert "catalog.example" not in result.model_dump_json()
    assert "secret" not in result.model_dump_json()


@pytest.mark.asyncio
async def test_get_item_routes_by_composite_key_and_checks_identity() -> None:
    adapter = FakeAdapter("provider")
    orchestrator = CatalogOrchestrator([adapter])
    scene = await orchestrator.get_item(
        "provider:sentinel-2-l2a:synthetic-sentinel-2-valid-001"
    )

    assert scene.provider == "provider"
    assert adapter.item_requests == [
        ("sentinel-2-l2a", "synthetic-sentinel-2-valid-001")
    ]


@pytest.mark.asyncio
async def test_get_item_rejects_unknown_provider_and_noncanonical_key() -> None:
    orchestrator = CatalogOrchestrator([FakeAdapter("provider")])

    with pytest.raises(CatalogItemNotFoundError):
        await orchestrator.get_item("unknown:sentinel-2-l2a:item")
    with pytest.raises(CatalogItemNotFoundError):
        await orchestrator.get_item("provider:sentinel-2-l2a:item%2fone")


def test_orchestrator_exposes_aggregate_catalog_capabilities() -> None:
    orchestrator = CatalogOrchestrator([FakeAdapter("provider")])

    assert isinstance(orchestrator, CatalogProvider)
    capabilities = orchestrator.capabilities()
    assert capabilities.provider_id == "catalog-orchestrator"
    assert capabilities.supported_collections == frozenset({"sentinel-2-l2a"})
    assert capabilities.supported_bands == frozenset({"B02", "B03", "B04", "B08"})


def test_duplicate_provider_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="provider IDs must be unique"):
        CatalogOrchestrator([FakeAdapter("same"), FakeAdapter("same")])
