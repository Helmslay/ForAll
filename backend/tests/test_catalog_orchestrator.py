from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient

from app.catalog_cursor import CatalogCursorCodec, InvalidCatalogCursor
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
from app.main import create_app

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
        next_pages: list[StacSearchPage] | None = None,
        next_page_error: Exception | None = None,
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
        self.next_pages = list(next_pages or [])
        self.next_page_error = next_page_error
        self.next_page_requests: list[str] = []
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

    async def get_next_page(self, next_href: str) -> StacSearchPage:
        self.next_page_requests.append(next_href)
        if self.next_page_error is not None:
            raise self.next_page_error
        if not self.next_pages:
            raise AssertionError("unexpected next-page request")
        return self.next_pages.pop(0)

    async def get_item(self, collection_id: str, item_id: str) -> dict[str, Any]:
        self.item_requests.append((collection_id, item_id))
        if self.error is not None:
            raise self.error
        item = dict(FIXTURE)
        item["collection"] = collection_id
        item["id"] = item_id
        return item


def test_app_factory_wires_explicit_adapters_to_search_route() -> None:
    adapter = FakeAdapter("configured")
    app = create_app(catalog_adapters=[adapter])

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/catalog/search",
            json={
                "bbox": [59.3, 56.7, 59.5, 56.9],
                "datetime": {
                    "from": "2025-06-01T00:00:00Z",
                    "to": "2025-06-30T23:59:59Z",
                },
                "collections": ["sentinel-2-l2a"],
                "providers": None,
                "limit": 20,
                "cursor": None,
            },
        )

    assert response.status_code == 200
    assert response.json()["items"][0]["provider"] == "configured"
    assert response.json()["providers"][0]["id"] == "configured"


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
async def test_unrequested_collection_in_provider_response_is_rejected() -> None:
    unexpected = dict(FIXTURE)
    unexpected["collection"] = "not-requested"
    bad_provider = FakeAdapter("bad", features=[unexpected])
    good_provider = FakeAdapter("good")

    result = await CatalogOrchestrator([bad_provider, good_provider]).search(
        make_request()
    )

    assert [scene.provider for scene in result.items] == ["good"]
    assert result.providers[0].status == "unavailable"
    assert result.providers[0].reason == "CATALOG_PROVIDER_ERROR"
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
async def test_get_item_preserves_encoded_identity_components() -> None:
    adapter = FakeAdapter("provider")
    orchestrator = CatalogOrchestrator([adapter])

    scene = await orchestrator.get_item(
        "provider:sentinel-2-l2a:item%2Fwith%3Aseparators"
    )

    assert scene.item_id == "item/with:separators"
    assert scene.key == "provider:sentinel-2-l2a:item%2Fwith%3Aseparators"


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


def make_feature(item_id: str) -> dict[str, Any]:
    feature = json.loads(json.dumps(FIXTURE))
    feature["id"] = item_id
    return feature


def make_cursor_codec() -> CatalogCursorCodec:
    return CatalogCursorCodec(b"c" * 32)


@pytest.mark.asyncio
async def test_cursor_paginates_buffered_aggregate_results() -> None:
    adapter = FakeAdapter("provider", features=[make_feature("item-1"), make_feature("item-2")])
    orchestrator = CatalogOrchestrator([adapter], cursor_codec=make_cursor_codec())
    first = await orchestrator.search(make_request(limit=1))
    assert [scene.item_id for scene in first.items] == ["item-1"]
    assert first.next_cursor is not None
    second = await orchestrator.search(make_request(limit=1, cursor=first.next_cursor))
    assert [scene.item_id for scene in second.items] == ["item-2"]
    assert second.next_cursor is None


@pytest.mark.asyncio
async def test_multiple_providers_advance_independently_and_preserve_buffers() -> None:
    first = FakeAdapter("first", features=[make_feature("first-1")], next_href="https://first.example/search?page=2", next_pages=[StacSearchPage((make_feature("first-2"),), None)])
    second = FakeAdapter("second", features=[make_feature("second-1")])
    orchestrator = CatalogOrchestrator([first, second], cursor_codec=make_cursor_codec())
    page1 = await orchestrator.search(make_request(limit=1))
    assert page1.items[0].key == "first:sentinel-2-l2a:first-1"
    page2 = await orchestrator.search(make_request(limit=1, cursor=page1.next_cursor))
    assert page2.items[0].key == "first:sentinel-2-l2a:first-2"
    assert first.next_page_requests == ["https://first.example/search?page=2"]
    page3 = await orchestrator.search(make_request(limit=1, cursor=page2.next_cursor))
    assert page3.items[0].key == "second:sentinel-2-l2a:second-1"
    assert page3.next_cursor is None


@pytest.mark.asyncio
async def test_cursor_deduplicates_scene_keys_across_provider_pages() -> None:
    adapter = FakeAdapter("provider", features=[make_feature("duplicate")], next_href="https://catalog.example/search?page=2", next_pages=[StacSearchPage((make_feature("duplicate"), make_feature("new-item")), None)])
    orchestrator = CatalogOrchestrator([adapter], cursor_codec=make_cursor_codec())
    first = await orchestrator.search(make_request(limit=1))
    second = await orchestrator.search(make_request(limit=1, cursor=first.next_cursor))
    assert [scene.item_id for scene in first.items] == ["duplicate"]
    assert [scene.item_id for scene in second.items] == ["new-item"]


@pytest.mark.asyncio
async def test_cursor_rejects_query_and_provider_changes() -> None:
    adapter = FakeAdapter("provider", features=[make_feature("item-1"), make_feature("item-2")])
    orchestrator = CatalogOrchestrator([adapter], cursor_codec=make_cursor_codec())
    first = await orchestrator.search(make_request(limit=1))
    with pytest.raises(InvalidCatalogCursor):
        await orchestrator.search(make_request(limit=1, cursor=first.next_cursor, bbox=[59.2, 56.7, 59.5, 56.9]))
    other = CatalogOrchestrator([FakeAdapter("different")], cursor_codec=make_cursor_codec())
    with pytest.raises(InvalidCatalogCursor):
        await other.search(make_request(limit=1, cursor=first.next_cursor))


@pytest.mark.asyncio
async def test_missing_cursor_key_fails_closed_without_exposing_upstream_href() -> None:
    adapter = FakeAdapter("provider", next_href="https://catalog.example/search?page=2&token=secret")
    result = await CatalogOrchestrator([adapter]).search(make_request(limit=1))
    assert result.next_cursor is None
    assert result.partial is True
    assert result.providers[0].reason == "cursor_encryption_unavailable"
    assert "catalog.example" not in result.model_dump_json()
    assert "secret" not in result.model_dump_json()
    with pytest.raises(InvalidCatalogCursor):
        await CatalogOrchestrator([adapter]).search(make_request(limit=1, cursor="opaque"))


@pytest.mark.asyncio
async def test_provider_failure_during_continuation_preserves_other_provider_buffer() -> None:
    failed = FakeAdapter(
        "failed",
        features=[make_feature("failed-first")],
        next_href="https://failed.example/search?page=2",
        next_page_error=CatalogUnavailableError("failed"),
    )
    working = FakeAdapter("working", features=[make_feature("working-first")])
    orchestrator = CatalogOrchestrator([failed, working], cursor_codec=make_cursor_codec())
    first = await orchestrator.search(make_request(limit=1))
    second = await orchestrator.search(make_request(limit=1, cursor=first.next_cursor))
    assert [scene.key for scene in first.items] == ["failed:sentinel-2-l2a:failed-first"]
    assert [scene.key for scene in second.items] == ["working:sentinel-2-l2a:working-first"]
    assert second.providers[0].status == "unavailable"
    assert second.providers[1].status == "success"
    assert second.partial is True
