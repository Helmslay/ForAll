import json
from pathlib import Path

import httpx
import pytest

from app.catalog_provider import (
    CatalogConfigurationError,
    CatalogProviderError,
    CatalogQueryNotSupportedError,
    CatalogUnavailableError,
)
from app.schemas.catalog import SearchRequest
from app.stac_adapter import StacAdapterConfig, StacCatalogAdapter

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "stac" / "valid_item.json").read_text()
)
COLLECTIONS = frozenset({"sentinel-2-l2a"})
HOSTS = frozenset({"catalog.example"})


def make_config(**kwargs):
    values = {
        "provider_id": "test-catalog",
        "endpoint": "https://catalog.example/v1",
        "allowed_hosts": HOSTS,
        "collections": COLLECTIONS,
    }
    values.update(kwargs)
    return StacAdapterConfig(**values)


def make_request(**kwargs):
    values = {
        "bbox": [59.3, 56.7, 59.5, 56.9],
        "datetime": {
            "from": "2025-06-01T00:00:00Z",
            "to": "2025-06-30T23:59:59Z",
        },
        "collections": ["sentinel-2-l2a"],
        "limit": 20,
        "cursor": None,
    }
    values.update(kwargs)
    return SearchRequest.model_validate(values)


@pytest.mark.asyncio
async def test_lists_stac_collections_using_configured_endpoint():
    async def handler(request):
        assert request.url == "https://catalog.example/v1/collections"
        return httpx.Response(200, json={"collections": [{"id": "sentinel-2-l2a"}]})

    adapter = StacCatalogAdapter(make_config(), transport=httpx.MockTransport(handler))
    try:
        result = await adapter.list_collections()
        assert result == ({"id": "sentinel-2-l2a"},)
        assert adapter.capabilities().supported_collections == COLLECTIONS
        assert adapter.capabilities().provider_id == "test-catalog"
    finally:
        await adapter.aclose()


def test_configuration_requires_explicit_allowlisted_https_endpoint():
    with pytest.raises(CatalogConfigurationError):
        make_config(endpoint="http://catalog.example/v1")
    with pytest.raises(CatalogConfigurationError):
        make_config(endpoint="https://unlisted.example/v1")
    with pytest.raises(CatalogConfigurationError):
        make_config(endpoint="https://user:pass@catalog.example/v1")


@pytest.mark.asyncio
async def test_search_posts_stac_query_and_exposes_backend_next_link_only():
    calls = []

    async def handler(request):
        calls.append(request)
        if request.method == "POST":
            assert request.url == "https://catalog.example/v1/search"
            body = json.loads(request.content)
            assert body == {
                "bbox": [59.3, 56.7, 59.5, 56.9],
                "datetime": "2025-06-01T00:00:00Z/2025-06-30T23:59:59Z",
                "collections": ["sentinel-2-l2a"],
                "limit": 20,
            }
            return httpx.Response(
                200,
                json={
                    "type": "FeatureCollection",
                    "features": [{"type": "Feature", "id": "item-1"}],
                    "links": [{"rel": "next", "href": "/v1/search?page=2&token=ephemeral"}],
                },
            )
        assert request.method == "GET"
        assert request.url.path == "/v1/search"
        assert request.url.params["page"] == "2"
        return httpx.Response(
            200,
            json={
                "type": "FeatureCollection",
                "features": [{"type": "Feature", "id": "item-2"}],
                "links": [],
            },
        )

    adapter = StacCatalogAdapter(make_config(), transport=httpx.MockTransport(handler))
    try:
        first = await adapter.search(make_request())
        assert [item["id"] for item in first.features] == ["item-1"]
        assert first.next_href is not None
        second = await adapter.get_next_page(first.next_href)
        assert [item["id"] for item in second.features] == ["item-2"]
        assert second.next_href is None
        assert len(calls) == 2
    finally:
        await adapter.aclose()


@pytest.mark.asyncio
async def test_next_link_cannot_escape_configured_host_allowlist():
    async def handler(request):
        return httpx.Response(
            200,
            json={
                "type": "FeatureCollection",
                "features": [],
                "links": [{"rel": "next", "href": "https://evil.example/steal"}],
            },
        )

    adapter = StacCatalogAdapter(make_config(), transport=httpx.MockTransport(handler))
    try:
        page = await adapter.search(make_request())
        with pytest.raises(CatalogConfigurationError):
            await adapter.get_next_page(page.next_href)
    finally:
        await adapter.aclose()


@pytest.mark.asyncio
async def test_get_item_uses_escaped_path_and_returns_stac_item():
    async def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/v1/collections/sentinel-2-l2a/items/item%2Fone"
        return httpx.Response(200, json=FIXTURE)

    adapter = StacCatalogAdapter(make_config(), transport=httpx.MockTransport(handler))
    try:
        item = await adapter.get_item("sentinel-2-l2a", "item/one")
        assert item["id"] == FIXTURE["id"]
        assert set(item["assets"]) == {"B02", "B03", "B04", "B08"}
    finally:
        await adapter.aclose()


@pytest.mark.asyncio
async def test_rejects_unsupported_collection_cursor_and_cloud_query():
    async def handler(request):
        pytest.fail("request must not be sent")

    adapter = StacCatalogAdapter(make_config(), transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(CatalogQueryNotSupportedError):
            await adapter.search(make_request(collections=["unknown"]))
        with pytest.raises(CatalogQueryNotSupportedError):
            await adapter.search(make_request(cursor="opaque"))
        with pytest.raises(CatalogQueryNotSupportedError):
            await adapter.search(make_request(cloud_cover_lte=20))
        with pytest.raises(CatalogQueryNotSupportedError):
            await adapter.get_item("unknown", "item")
    finally:
        await adapter.aclose()


@pytest.mark.asyncio
async def test_cloud_cover_query_is_sent_only_when_extension_is_configured():
    async def handler(request):
        body = json.loads(request.content)
        assert body["query"] == {"eo:cloud_cover": {"lte": 15}}
        return httpx.Response(
            200, json={"type": "FeatureCollection", "features": [], "links": []}
        )

    adapter = StacCatalogAdapter(
        make_config(supports_query_extension=True),
        transport=httpx.MockTransport(handler),
    )
    try:
        await adapter.search(make_request(cloud_cover_lte=15))
    finally:
        await adapter.aclose()


@pytest.mark.asyncio
async def test_maps_provider_failures_to_safe_domain_errors():
    async def unavailable(request):
        return httpx.Response(503)

    adapter = StacCatalogAdapter(
        make_config(),
        transport=httpx.MockTransport(unavailable),
        max_retries=0,
    )
    try:
        with pytest.raises(CatalogUnavailableError):
            await adapter.list_collections()
    finally:
        await adapter.aclose()


@pytest.mark.asyncio
async def test_rejects_malformed_stac_collection_and_search_payloads():
    async def malformed(request):
        return httpx.Response(200, json={"collections": [{"title": "missing id"}]})

    adapter = StacCatalogAdapter(make_config(), transport=httpx.MockTransport(malformed))
    try:
        with pytest.raises(CatalogProviderError):
            await adapter.list_collections()
    finally:
        await adapter.aclose()

    async def invalid_search(request):
        return httpx.Response(200, json={"type": "FeatureCollection", "features": "bad"})

    adapter = StacCatalogAdapter(
        make_config(), transport=httpx.MockTransport(invalid_search)
    )
    try:
        with pytest.raises(CatalogProviderError):
            await adapter.search(make_request())
    finally:
        await adapter.aclose()
