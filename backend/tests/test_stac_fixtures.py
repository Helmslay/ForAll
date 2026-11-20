import json
from pathlib import Path
from typing import Any

from app.catalog_provider import CatalogUnavailableError
from app.schemas.catalog import Scene

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "stac"
MVP_BANDS = {"B02", "B03", "B04", "B08"}


def load_fixture(name: str) -> dict[str, Any]:
    path = FIXTURE_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def polygon_ring_is_closed(geometry: dict[str, Any]) -> bool:
    if geometry.get("type") != "Polygon":
        return False
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or not coordinates:
        return False
    ring = coordinates[0]
    return (
        isinstance(ring, list)
        and len(ring) >= 4
        and ring[0] == ring[-1]
        and all(
            isinstance(position, list)
            and len(position) == 2
            and all(isinstance(value, (int, float)) for value in position)
            for position in ring
        )
    )


def test_valid_synthetic_stac_item_contains_four_mvp_assets() -> None:
    item = load_fixture("valid_item.json")

    assert item["type"] == "Feature"
    assert item["stac_version"] == "1.0.0"
    assert item["sentinel_explorer_fixture"] is True
    assert item["properties"]["datetime"].endswith("Z")
    assert item["properties"]["eo:cloud_cover"] == 12.5
    assert set(item["assets"]) == MVP_BANDS
    assert polygon_ring_is_closed(item["geometry"])


def test_missing_cloud_cover_is_not_replaced_with_a_default() -> None:
    item = load_fixture("missing_cloud_cover.json")

    assert "eo:cloud_cover" not in item["properties"]

    scene = Scene.model_validate(
        {
            "key": "fixture:missing-cloud-cover",
            "provider": "synthetic-provider",
            "collection": item["collection"],
            "item_id": item["id"],
            "acquired_at": item["properties"]["datetime"],
            "cloud_cover": item["properties"].get("eo:cloud_cover"),
            "available_bands": sorted(set(item["assets"]) & MVP_BANDS),
            "preview_available": False,
        }
    )

    assert scene.cloud_cover is None


def test_missing_mvp_band_remains_unavailable() -> None:
    item = load_fixture("missing_mvp_band.json")
    available_bands = set(item["assets"]) & MVP_BANDS

    assert available_bands == {"B02", "B03", "B04"}
    assert "B08" not in available_bands

    scene = Scene.model_validate(
        {
            "key": "fixture:missing-b08",
            "provider": "synthetic-provider",
            "collection": item["collection"],
            "item_id": item["id"],
            "acquired_at": item["properties"]["datetime"],
            "available_bands": sorted(available_bands),
            "preview_available": False,
        }
    )

    assert set(scene.available_bands) == available_bands
    assert "B08" not in scene.available_bands


def test_malformed_polygon_fixture_is_detected_as_invalid() -> None:
    item = load_fixture("malformed_geometry.json")

    assert item["sentinel_explorer_fixture"] is True
    assert not polygon_ring_is_closed(item["geometry"])


def test_provider_error_fixture_maps_to_safe_domain_error() -> None:
    fixture = load_fixture("provider_error.json")
    error = CatalogUnavailableError(provider_id=fixture["provider_id"])

    assert fixture["code"] == error.code
    assert fixture["message"] == str(error)
    assert error.provider_id == "synthetic-provider"
    assert "traceback" not in fixture
    assert "raw_response" not in fixture


def test_stac_fixtures_contain_no_network_urls_or_credentials() -> None:
    for path in FIXTURE_DIR.glob("*.json"):
        raw = path.read_text(encoding="utf-8").lower()
        item = json.loads(raw)

        assert item["sentinel_explorer_fixture"] is True
        assert "https://" not in raw
        assert "http://" not in raw
        assert '"token"' not in raw
        assert '"secret"' not in raw
        assert '"signature"' not in raw
        for asset in item.get("assets", {}).values():
            assert asset["href"].startswith("urn:sentinel-explorer:fixture:")
