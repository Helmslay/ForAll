import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.catalog_cursor import CatalogCursorCodec, InvalidCatalogCursor
from app.catalog_provider import (
    CatalogConfigurationError,
    CatalogItemNotFoundError,
    CatalogProviderError,
    CatalogQueryNotSupportedError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)
from app.catalog_routes import router as catalog_router
from app.catalog_orchestrator import CatalogOrchestrator
from app.stac_adapter import StacCatalogAdapter

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    *,
    catalog_adapters: Sequence[StacCatalogAdapter] = (),
) -> FastAPI:
    """Build the API application without connecting to external services."""
    app_settings = settings or get_settings()
    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
    )
    try:
        cursor_codec = CatalogCursorCodec.from_env()
    except ValueError:
        cursor_codec = None
    app.state.catalog_provider = CatalogOrchestrator(
        catalog_adapters, cursor_codec=cursor_codec
    )
    app.include_router(catalog_router)

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = uuid4().hex
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    def error_response(
        request: Request,
        *,
        status_code: int,
        code: str,
        message: str,
    ) -> JSONResponse:
        response = JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": code,
                    "message": message,
                    "request_id": request.state.request_id,
                    "details": {},
                }
            },
        )
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        messages = {
            400: "Некорректный запрос",
            401: "Требуется авторизация",
            403: "Доступ запрещён",
            404: "Ресурс не найден",
            405: "Метод не поддерживается",
        }
        response = error_response(
            request,
            status_code=exc.status_code,
            code=f"HTTP_{exc.status_code}",
            message=messages.get(exc.status_code, "Не удалось выполнить запрос"),
        )
        if exc.headers:
            response.headers.update(exc.headers)
        return response

    @app.exception_handler(CatalogProviderError)
    async def handle_catalog_provider_error(
        request: Request, exc: CatalogProviderError
    ) -> JSONResponse:
        if isinstance(exc, (CatalogUnavailableError, CatalogConfigurationError)):
            status_code = 503
        elif isinstance(exc, CatalogRateLimitedError):
            status_code = 429
        elif isinstance(exc, CatalogQueryNotSupportedError):
            status_code = 422
        elif isinstance(exc, CatalogItemNotFoundError):
            status_code = 404
        else:
            status_code = 502
        return error_response(
            request,
            status_code=status_code,
            code=exc.code,
            message=exc.safe_message,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            request,
            status_code=422,
            code="VALIDATION_ERROR",
            message="Некорректные параметры запроса",
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled request error",
            extra={"request_id": request.state.request_id},
        )
        return error_response(
            request,
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message="Внутренняя ошибка сервера",
        )

    @app.get("/api/v1/health")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "app_version": app_settings.app_version,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }

    return app


app = create_app()
