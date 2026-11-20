import logging

import httpx
import pytest

from app.catalog_provider import (
    CatalogConfigurationError,
    CatalogProviderError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)
from app.stac_http import StacHttpClient


HOSTS = {"catalog.example"}
URL = "https://catalog.example/stac"


def make_client(handler, **kwargs):
    transport = httpx.MockTransport(handler)
    return StacHttpClient(
        provider_id="test-catalog",
        allowed_hosts=HOSTS,
        transport=transport,
        retry_backoff_seconds=0,
        **kwargs,
    ), transport


@pytest.mark.asyncio
async def test_returns_json_for_successful_stac_response():
    async def handler(request):
        assert request.method == "GET"
        return httpx.Response(
            200,
            headers={"content-type": "application/geo+json"},
            json={"type": "Feature", "id": "scene-1"},
        )

    client, transport = make_client(handler)
    try:
        assert await client.request_json("GET", URL) == {
            "type": "Feature",
            "id": "scene-1",
        }
    finally:
        await client.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "http://catalog.example/stac",
        "https://other.example/stac",
        "https://catalog.example:8443/stac",
        "https://user:pass@catalog.example/stac",
        "https://catalog.example/stac#fragment",
    ],
)
async def test_rejects_urls_outside_https_host_allowlist(url):
    client, transport = make_client(lambda request: httpx.Response(200, json={}))
    try:
        with pytest.raises(CatalogConfigurationError):
            await client.request_json("GET", url)
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_rejects_redirects_without_following_them():
    async def handler(request):
        return httpx.Response(302, headers={"location": "https://other.example/"})

    client, transport = make_client(handler)
    try:
        with pytest.raises(CatalogProviderError):
            await client.request_json("GET", URL)
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_retries_transient_server_error_then_returns_json():
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(503)
        return httpx.Response(200, headers={"content-type": "application/json"}, json={"ok": True})

    client, transport = make_client(handler, max_retries=1)
    try:
        assert await client.request_json("POST", URL, json_body={"query": {}}) == {"ok": True}
        assert calls == 2
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_does_not_retry_non_transient_client_error():
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(400)

    client, transport = make_client(handler, max_retries=3)
    try:
        with pytest.raises(CatalogProviderError):
            await client.request_json("GET", URL)
        assert calls == 1
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_exhausted_server_errors_become_safe_unavailable_error():
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(500)

    client, transport = make_client(handler, max_retries=2)
    try:
        with pytest.raises(CatalogUnavailableError):
            await client.request_json("GET", URL)
        assert calls == 3
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_exhausted_rate_limit_becomes_rate_limited_error():
    async def handler(request):
        return httpx.Response(429, headers={"retry-after": "0"})

    client, transport = make_client(handler, max_retries=1)
    try:
        with pytest.raises(CatalogRateLimitedError):
            await client.request_json("GET", URL)
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_timeout_is_retried_only_a_finite_number_of_times():
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("private url data")

    client, transport = make_client(handler, max_retries=1)
    try:
        with pytest.raises(CatalogUnavailableError):
            await client.request_json("GET", URL)
        assert calls == 2
    finally:
        await transport.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, headers={"content-type": "text/html"}, text="<html/>"),
        httpx.Response(200, headers={"content-type": "application/json"}, text="{bad"),
        httpx.Response(
            200,
            headers={"content-type": "application/json", "content-length": "100"},
            content=b"{}",
        ),
    ],
)
async def test_rejects_invalid_content_type_json_and_declared_oversize(response):
    async def handler(request):
        return response

    client, transport = make_client(handler, max_response_bytes=10)
    try:
        with pytest.raises(CatalogProviderError):
            await client.request_json("GET", URL)
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_rejects_streamed_response_that_exceeds_size_limit():
    async def handler(request):
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=b'{"payload":"too long"}',
        )

    client, transport = make_client(handler, max_response_bytes=10)
    try:
        with pytest.raises(CatalogProviderError):
            await client.request_json("GET", URL)
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_logs_do_not_include_signed_url_query_or_exception_text(caplog):
    async def handler(request):
        raise httpx.ConnectError("failed https://catalog.example/stac?token=secret")

    client, transport = make_client(handler, max_retries=0)
    try:
        with caplog.at_level(logging.WARNING):
            with pytest.raises(CatalogUnavailableError):
                await client.request_json(
                    "GET", "https://catalog.example/stac?token=secret"
                )
        assert "token=secret" not in caplog.text
        assert "catalog.example/stac" not in caplog.text
        assert "failed https" not in caplog.text
    finally:
        await transport.aclose()


@pytest.mark.asyncio
async def test_rejects_unsupported_method_and_empty_allowlist():
    client, transport = make_client(lambda request: httpx.Response(200, json={}))
    try:
        with pytest.raises(CatalogConfigurationError):
            await client.request_json("DELETE", URL)
    finally:
        await transport.aclose()

    with pytest.raises(CatalogConfigurationError):
        StacHttpClient(provider_id="test-catalog", allowed_hosts=set())
