import logging

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
    assert response.headers["X-Request-ID"]


def test_settings_can_be_overridden_without_environment_secrets() -> None:
    settings = Settings(app_name="Test API", app_version="9.9.9")
    application = create_app(settings)

    assert application.title == "Test API"
    assert application.version == "9.9.9"


def test_http_errors_use_the_api_error_contract() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/missing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "HTTP_404",
            "message": "Ресурс не найден",
            "request_id": response.headers["X-Request-ID"],
            "details": {},
        }
    }


def test_validation_errors_use_the_api_error_contract() -> None:
    application = create_app()
    application.add_api_route("/items", lambda count: {"count": count}, methods=["GET"])

    with TestClient(application) as client:
        response = client.get("/items", params={"count": "not-an-integer"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]
    assert "traceback" not in response.text.lower()


def test_unexpected_errors_hide_traceback_and_are_logged(caplog) -> None:
    application = create_app()

    def fail() -> None:
        raise RuntimeError("private internal detail")

    application.add_api_route("/failure", fail, methods=["GET"])

    with caplog.at_level(logging.ERROR), TestClient(application) as client:
        response = client.get("/failure")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Внутренняя ошибка сервера",
            "request_id": response.headers["X-Request-ID"],
            "details": {},
        }
    }
    assert "traceback" not in response.text.lower()
    assert "private internal detail" not in response.text
    assert "Unhandled request error" in caplog.text
    assert "private internal detail" in caplog.text
