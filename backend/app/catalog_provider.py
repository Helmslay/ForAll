from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.schemas.catalog import BandName, Scene, SearchRequest, SearchResponse


@dataclass(frozen=True, slots=True)
class CatalogCapabilities:
    """Provider-declared catalog scope; values must come from provider configuration."""

    provider_id: str
    supported_collections: frozenset[str]
    supported_bands: frozenset[BandName]

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise ValueError("provider_id must not be empty")
        if any(not collection.strip() for collection in self.supported_collections):
            raise ValueError("supported collection identifiers must not be empty")


@runtime_checkable
class CatalogProvider(Protocol):
    """Transport-independent interface implemented by catalog providers."""

    def capabilities(self) -> CatalogCapabilities:
        """Return the provider's declared, non-secret capabilities."""
        ...

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Search scenes using the normalized application request/response DTOs."""
        ...

    async def get_item(self, scene_key: str) -> Scene:
        """Return one normalized scene or raise CatalogItemNotFoundError."""
        ...


class CatalogProviderError(Exception):
    """Base domain error; deliberately contains no HTTP-specific status or response."""

    code = "CATALOG_PROVIDER_ERROR"
    safe_message = "Ошибка поставщика каталога"

    def __init__(self, provider_id: str | None = None) -> None:
        self.provider_id = provider_id
        super().__init__(self.safe_message)


class CatalogUnavailableError(CatalogProviderError):
    code = "PROVIDER_UNAVAILABLE"
    safe_message = "Каталог временно недоступен"


class CatalogItemNotFoundError(CatalogProviderError):
    code = "SCENE_NOT_FOUND"
    safe_message = "Сцена не найдена"


class CatalogQueryNotSupportedError(CatalogProviderError):
    code = "CATALOG_QUERY_NOT_SUPPORTED"
    safe_message = "Поставщик не поддерживает указанные параметры поиска"


class CatalogRateLimitedError(CatalogProviderError):
    code = "PROVIDER_RATE_LIMITED"
    safe_message = "Поставщик временно ограничил частоту запросов"


class CatalogConfigurationError(CatalogProviderError):
    code = "PROVIDER_CONFIGURATION_ERROR"
    safe_message = "Поставщик каталога настроен некорректно"
