from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.catalog_provider import (
    CatalogConfigurationError,
    CatalogProvider,
    CatalogProviderError,
    CatalogQueryNotSupportedError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)
from app.main import create_app
from app.schemas.catalog import SearchRequest, SearchResponse

VALID_SEARCH: dict[str, Any] = {
    "bbox": [56.0, 57.0, 58.0, 59.0],
    "datetime": {
        "from": "2025-06-01T00:00:00Z",
        "to": "2025-09-01T23:59:59Z",
    },
    "cloud_cover_lte": 20,
    "collections": ["sentinel-2-l2a"],
    "providers": None,
    "limit": 20,
    "cursor": None,
}


class FakeCatalogProvider:
    def __init__(self, error: Exception | None = None) -> None:
        self.calls: list[SearchRequest] = []
        self.error = error

    def capabilities(self):
        raise NotImplementedError

    async def search(self, request: SearchRequest) -> SearchResponse:
        self.calls.append(request)
        if self.error is not None:
            raise self.error
        return SearchResponse(
            items=[],
            next_cursor=None,
            providers=[],
            partial=False,
        )

    async def get_item(self, scene_key: str):
        raise NotImplementedError


def test_search_endpoint_passes_validated_request_to_provider() -> None:
    app = create_app()
    provider = FakeCatalogProvider()
    app.state.catalog_provider = provider

    with TestClient(app) as client:
        response = client.post("/api/v1/catalog/search", json=VALID_SEARCH)

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "next_cursor": None,
        "providers": [],
        "partial": False,
    }
    assert len(provider.calls) == 1
    assert provider.calls[0].bbox == (56.0, 57.0, 58.0, 59.0)
    assert response.headers["X-Request-ID"]


@pytest.mark.parametrize(
    "changes",
    [
        {"bbox": [56.0, 57.0, 55.0, 59.0]},
        {
            "datetime": {
                "from": "2025-09-01T00:00:00Z",
                "to": "2025-06-01T00:00:00Z",
            }
        },
        {
            "datetime": {
                "from": "2025-06-01T00:00:00",
                "to": "2025-09-01T00:00:00Z",
            }
        },
        {"cloud_cover_lte": 100.1},
        {"limit": 0},
        {"limit": 101},
        {"limit": 1.5},
        {"endpoint": "https://catalog.example.invalid"},
    ],
)
def test_search_endpoint_rejects_invalid_or_untrusted_input(
    changes: dict[str, Any],
) -> None:
    app = create_app()
    provider = FakeCatalogProvider()
    app.state.catalog_provider = provider

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/catalog/search",
            json={**VALID_SEARCH, **changes},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.headers["X-Request-ID"]
    assert provider.calls == []


def test_search_endpoint_returns_safe_unavailable_when_unconfigured() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/v1/catalog/search", json=VALID_SEARCH)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "PROVIDER_UNAVAILABLE"
    assert response.json()["error"]["message"] == "Каталог временно недоступен"
    assert response.headers["X-Request-ID"]


@pytest.mark.parametrize(
    ("error", "status_code", "error_code"),
    [
        (CatalogUnavailableError("provider"), 503, "PROVIDER_UNAVAILABLE"),
        (CatalogConfigurationError("provider"), 503, "PROVIDER_CONFIGURATION_ERROR"),
        (CatalogRateLimitedError("provider"), 429, "PROVIDER_RATE_LIMITED"),
        (
            CatalogQueryNotSupportedError("provider"),
            422,
            "CATALOG_QUERY_NOT_SUPPORTED",
        ),
        (CatalogProviderError("provider"), 502, "CATALOG_PROVIDER_ERROR"),
    ],
)
def test_search_endpoint_maps_provider_errors_to_safe_contract(
    error: Exception,
    status_code: int,
    error_code: str,
) -> None:
    app = create_app()
    app.state.catalog_provider = FakeCatalogProvider(error=error)

    with TestClient(app) as client:
        response = client.post("/api/v1/catalog/search", json=VALID_SEARCH)

    assert response.status_code == status_code
    body = response.json()
    assert body["error"]["code"] == error_code
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]
    assert body["error"]["details"] == {}
    assert "provider" not in response.text
    assert "traceback" not in response.text.lower()
