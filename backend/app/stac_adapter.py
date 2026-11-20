"""Configurable STAC API adapter; no provider is selected by default."""

from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import quote, urljoin, urlsplit

import httpx

from app.catalog_provider import (
    CatalogCapabilities,
    CatalogConfigurationError,
    CatalogProviderError,
    CatalogQueryNotSupportedError,
)
from app.schemas.catalog import BandName, SearchRequest
from app.stac_http import StacHttpClient


@dataclass(frozen=True, slots=True)
class StacAdapterConfig:
    """Explicit, non-secret configuration for one STAC API endpoint."""

    provider_id: str
    endpoint: str
    allowed_hosts: frozenset[str]
    collections: frozenset[str]
    supported_bands: frozenset[BandName] = frozenset(
        {"B02", "B03", "B04", "B08"}
    )
    supports_query_extension: bool = False

    def __post_init__(self) -> None:
        if not self.provider_id.strip() or not self.collections:
            raise ValueError("provider_id and collections must not be empty")
        hosts = frozenset(host.strip().lower() for host in self.allowed_hosts)
        object.__setattr__(self, "allowed_hosts", hosts)
        parsed = urlsplit(self.endpoint)
        try:
            port = parsed.port
        except ValueError as exc:
            raise CatalogConfigurationError(self.provider_id) from exc
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.hostname.lower() not in hosts
            or port not in (None, 443)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise CatalogConfigurationError(self.provider_id)
        if any(not collection.strip() for collection in self.collections):
            raise ValueError("collection identifiers must not be empty")


@dataclass(frozen=True, slots=True)
class StacSearchPage:
    """Raw STAC features and an internal-only next link for backend pagination."""

    features: tuple[dict[str, Any], ...]
    next_href: str | None


class StacCatalogAdapter:
    """Small STAC API adapter using the shared allowlisted HTTP transport."""

    def __init__(
        self,
        config: StacAdapterConfig,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout_seconds: float = 15.0,
        max_retries: int = 2,
        max_response_bytes: int = 2_000_000,
    ) -> None:
        self.config = config
        self._base_url = config.endpoint.rstrip("/") + "/"
        self._http = StacHttpClient(
            provider_id=config.provider_id,
            allowed_hosts=config.allowed_hosts,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            max_response_bytes=max_response_bytes,
            transport=transport,
        )

    def capabilities(self) -> CatalogCapabilities:
        return CatalogCapabilities(
            provider_id=self.config.provider_id,
            supported_collections=self.config.collections,
            supported_bands=self.config.supported_bands,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "StacCatalogAdapter":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def list_collections(self) -> tuple[dict[str, Any], ...]:
        payload = await self._http.request_json(
            "GET", urljoin(self._base_url, "collections")
        )
        collections = payload.get("collections")
        if not isinstance(collections, list) or any(
            not isinstance(item, dict) or not isinstance(item.get("id"), str)
            for item in collections
        ):
            raise CatalogProviderError(self.config.provider_id)
        return tuple(collections)

    async def search(self, request: SearchRequest) -> StacSearchPage:
        """Run the first STAC Item Search page; cursor signing is a later task."""
        if request.cursor is not None:
            raise CatalogQueryNotSupportedError(self.config.provider_id)
        if not set(request.collections).issubset(self.config.collections):
            raise CatalogQueryNotSupportedError(self.config.provider_id)
        body: dict[str, Any] = {
            "bbox": list(request.bbox),
            "datetime": (
                f"{request.datetime.start.isoformat().replace('+00:00', 'Z')}/"
                f"{request.datetime.end.isoformat().replace('+00:00', 'Z')}"
            ),
            "collections": request.collections,
            "limit": request.limit,
        }
        if request.cloud_cover_lte is not None:
            if not self.config.supports_query_extension:
                raise CatalogQueryNotSupportedError(self.config.provider_id)
            body["query"] = {"eo:cloud_cover": {"lte": request.cloud_cover_lte}}

        payload = await self._http.request_json(
            "POST", urljoin(self._base_url, "search"), json_body=body
        )
        return self._parse_search_page(payload)

    async def get_next_page(self, next_href: str) -> StacSearchPage:
        """Fetch a provider-supplied next link; HTTP transport rechecks its host."""
        payload = await self._http.request_json("GET", next_href)
        return self._parse_search_page(payload)

    async def get_item(self, collection_id: str, item_id: str) -> dict[str, Any]:
        if collection_id not in self.config.collections:
            raise CatalogQueryNotSupportedError(self.config.provider_id)
        path = (
            f"collections/{quote(collection_id, safe='')}/items/"
            f"{quote(item_id, safe='')}"
        )
        payload = await self._http.request_json("GET", urljoin(self._base_url, path))
        if (
            payload.get("type") != "Feature"
            or not isinstance(payload.get("id"), str)
            or not isinstance(payload.get("properties"), dict)
            or not isinstance(payload.get("assets"), dict)
        ):
            raise CatalogProviderError(self.config.provider_id)
        return payload

    def _parse_search_page(self, payload: Mapping[str, Any]) -> StacSearchPage:
        if payload.get("type") != "FeatureCollection":
            raise CatalogProviderError(self.config.provider_id)
        features = payload.get("features")
        links = payload.get("links", [])
        if (
            not isinstance(features, list)
            or any(
                not isinstance(feature, dict)
                or feature.get("type") != "Feature"
                or not isinstance(feature.get("id"), str)
                for feature in features
            )
            or not isinstance(links, list)
        ):
            raise CatalogProviderError(self.config.provider_id)

        next_links = [
            link
            for link in links
            if isinstance(link, dict) and link.get("rel") == "next"
        ]
        if len(next_links) > 1:
            raise CatalogProviderError(self.config.provider_id)
        next_href = None
        if next_links:
            href = next_links[0].get("href")
            if not isinstance(href, str) or not href:
                raise CatalogProviderError(self.config.provider_id)
            next_href = urljoin(self._base_url, href)
        return StacSearchPage(tuple(features), next_href)
