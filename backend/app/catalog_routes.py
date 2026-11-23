"""HTTP routes for catalog search."""

from fastapi import APIRouter, Depends, Request

from app.catalog_provider import CatalogProvider, CatalogUnavailableError
from app.schemas.catalog import SearchRequest, SearchResponse

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])


def get_catalog_provider(request: Request) -> CatalogProvider:
    """Resolve the configured catalog service without accepting client URLs."""
    provider = getattr(request.app.state, "catalog_provider", None)
    if provider is None:
        raise CatalogUnavailableError()
    return provider


@router.post("/search", response_model=SearchResponse)
async def search_catalog(
    search_request: SearchRequest,
    provider: CatalogProvider = Depends(get_catalog_provider),
) -> SearchResponse:
    """Search the configured catalog service using the public request DTO."""
    return await provider.search(search_request)
