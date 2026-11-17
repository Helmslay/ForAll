from fastapi import FastAPI

from app.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the API application without connecting to external services."""
    app_settings = settings or get_settings()
    return FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
    )


app = create_app()
