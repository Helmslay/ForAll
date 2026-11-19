import asyncio
from dataclasses import FrozenInstanceError

import pytest

from app.catalog_provider import (
    CatalogCapabilities,
    CatalogConfigurationError,
    CatalogItemNotFoundError,
    CatalogProvider,
    CatalogProviderError,
    CatalogQueryNotSupportedError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)
from app.schemas.catalog import Scene, SearchRequest, SearchResponse

SEARCH_REQUEST = SearchRequest.model_validate(
    {
        "bbox": [56.0, 57.0, 58.0, 59.0],
        "datetime": {
            "from": "2025-06-01T00:00:00Z",
            "to": "2025-06-30T23:59:59Z",
        },
        "collections": ["sentinel-2-l2a"],
        "limit": 20,
        "cursor": None,
    }
)
SCENE = Scene.model_validate(
    {
        "key": "earth-search:sentinel-2-l2a:item-1",
        "provider": "earth-search",
        "collection": "sentinel-2-l2a",
        "item_id": "item-1",
        "acquired_at": "2025-06-15T07:20:00Z",
        "available_bands": ["B02", "B03", "B04", "B08"],
        "preview_available": False,
    }
)


class FakeCatalogProvider:
    def capabilities(self) -> CatalogCapabilities:
        return CatalogCapabilities(
            provider_id="fake",
            supported_collections=frozenset({"sentinel-2-l2a"}),
            supported_bands=frozenset({"B02", "B03", "B04", "B08"}),
        )

    async def search(self, request: SearchRequest) -> SearchResponse:
        assert request == SEARCH_REQUEST
        return SearchResponse(
            items=[SCENE],
            next_cursor=None,
            providers=[{"id": "fake", "status": "success"}],
            partial=False,
        )

    async def get_item(self, scene_key: str) -> Scene:
        if scene_key != SCENE.key:
            raise CatalogItemNotFoundError("fake")
        return SCENE


def test_fake_provider_satisfies_transport_independent_protocol() -> None:
    provider = FakeCatalogProvider()

    assert isinstance(provider, CatalogProvider)
    assert provider.capabilities().provider_id == "fake"
    assert provider.capabilities().supported_collections == frozenset(
        {"sentinel-2-l2a"}
    )
    assert provider.capabilities().supported_bands == frozenset(
        {"B02", "B03", "B04", "B08"}
    )


def test_provider_search_uses_shared_dtos() -> None:
    response = asyncio.run(FakeCatalogProvider().search(SEARCH_REQUEST))

    assert response.items == [SCENE]
    assert response.providers[0].id == "fake"
    assert response.partial is False


def test_provider_get_item_returns_scene_or_domain_not_found_error() -> None:
    provider = FakeCatalogProvider()

    assert asyncio.run(provider.get_item(SCENE.key)) == SCENE

    with pytest.raises(CatalogItemNotFoundError) as exc_info:
        asyncio.run(provider.get_item("missing"))

    assert exc_info.value.code == "SCENE_NOT_FOUND"
    assert exc_info.value.provider_id == "fake"


def test_capabilities_are_immutable_and_validate_identifiers() -> None:
    capabilities = CatalogCapabilities(
        provider_id="fake",
        supported_collections=frozenset({"sentinel-2-l2a"}),
        supported_bands=frozenset({"B04"}),
    )

    with pytest.raises(FrozenInstanceError):
        capabilities.provider_id = "changed"  # type: ignore[misc]

    with pytest.raises(ValueError, match="provider_id"):
        CatalogCapabilities("", frozenset(), frozenset())

    with pytest.raises(ValueError, match="collection"):
        CatalogCapabilities("fake", frozenset({""}), frozenset())


@pytest.mark.parametrize(
    ("error_type", "expected_code", "expected_message"),
    [
        (
            CatalogProviderError,
            "CATALOG_PROVIDER_ERROR",
            "Ошибка поставщика каталога",
        ),
        (
            CatalogUnavailableError,
            "PROVIDER_UNAVAILABLE",
            "Каталог временно недоступен",
        ),
        (CatalogItemNotFoundError, "SCENE_NOT_FOUND", "Сцена не найдена"),
        (
            CatalogQueryNotSupportedError,
            "CATALOG_QUERY_NOT_SUPPORTED",
            "Поставщик не поддерживает указанные параметры поиска",
        ),
        (
            CatalogRateLimitedError,
            "PROVIDER_RATE_LIMITED",
            "Поставщик временно ограничил частоту запросов",
        ),
        (
            CatalogConfigurationError,
            "PROVIDER_CONFIGURATION_ERROR",
            "Поставщик каталога настроен некорректно",
        ),
    ],
)
def test_domain_errors_have_safe_transport_independent_attributes(
    error_type: type[CatalogProviderError],
    expected_code: str,
    expected_message: str,
) -> None:
    error = error_type("fake")

    assert error.code == expected_code
    assert str(error) == expected_message
    assert error.provider_id == "fake"
    assert "http" not in error.__dict__
    assert "status_code" not in error.__dict__
