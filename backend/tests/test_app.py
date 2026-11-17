from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_application_can_be_imported_and_served_without_secrets() -> None:
    application = create_app(Settings())

    with TestClient(application) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Sentinel Explorer API"
    assert response.json()["info"]["version"] == "0.1.0"


def test_settings_can_be_overridden_without_environment_secrets() -> None:
    settings = Settings(app_name="Test API", app_version="9.9.9")
    application = create_app(settings)

    assert application.title == "Test API"
    assert application.version == "9.9.9"
