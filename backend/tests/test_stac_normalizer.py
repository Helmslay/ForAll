import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.catalog_provider import CatalogProviderError
from app.schemas.catalog import Scene
from app.stac_normalizer import normalize_stac_item

FIXTURES = Path(__file__).parent / "fixtures" / "stac"


def load_item(name="valid_item.json"):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_normalizes_valid_stac_item_and_uses_stable_composite_key():
    item = load_item()
    scene = normalize_stac_item(item, provider_id="test-provider")

    assert scene == Scene(
        key="test-provider:sentinel-2-l2a:synthetic-sentinel-2-valid-001",
        provider="test-provider",
        collection="sentinel-2-l2a",
        item_id="synthetic-sentinel-2-valid-001",
        acquired_at="2025-06-15T07:20:00Z",
        platform="sentinel-2b",
        cloud_cover=12.5,
        bbox=(59.3, 56.7, 59.5, 56.9),
        geometry=item["geometry"],
        available_bands=["B02", "B03", "B04", "B08"],
        preview_available=False,
    )


def test_missing_cloud_cover_and_band_are_not_invented():
    item = load_item("missing_cloud_cover.json")
    scene = normalize_stac_item(item, provider_id="test-provider")

    assert scene.cloud_cover is None

    item = load_item("missing_mvp_band.json")
    scene = normalize_stac_item(item, provider_id="test-provider")
    assert scene.available_bands == ["B02", "B03", "B04"]


def test_malformed_geometry_is_omitted_not_forwarded():
    item = load_item("malformed_geometry.json")
    scene = normalize_stac_item(item, provider_id="test-provider")

    assert scene.geometry is None


def test_optional_invalid_metadata_is_omitted():
    item = load_item()
    item["bbox"] = [59.5, 56.7, 59.3, 56.9]
    item["properties"]["eo:cloud_cover"] = 120
    item["properties"]["platform"] = ""
    scene = normalize_stac_item(item, provider_id="test-provider")

    assert scene.bbox is None
    assert scene.cloud_cover is None
    assert scene.platform is None


def test_datetime_is_normalized_to_utc_without_changing_instant():
    item = load_item()
    item["properties"]["datetime"] = "2025-06-15T10:20:00+03:00"

    scene = normalize_stac_item(item, provider_id="test-provider")

    assert scene.acquired_at.isoformat() == "2025-06-15T07:20:00+00:00"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda item: item.pop("id"),
        lambda item: item.pop("collection"),
        lambda item: item["properties"].pop("datetime"),
        lambda item: item["properties"].update(datetime="not-a-date"),
        lambda item: item["properties"].update(datetime="2025-06-15T07:20:00"),
        lambda item: item.update(type="FeatureCollection"),
    ],
)
def test_missing_or_invalid_required_item_fields_raise_safe_error(mutate):
    item = load_item()
    mutate(item)

    with pytest.raises(CatalogProviderError) as error:
        normalize_stac_item(item, provider_id="test-provider")

    assert str(error.value) == "Ошибка поставщика каталога"


def test_collection_context_can_fill_missing_item_collection_only():
    item = load_item()
    item.pop("collection")

    scene = normalize_stac_item(
        item,
        provider_id="test-provider",
        collection_id="sentinel-2-l2a",
    )
    assert scene.collection == "sentinel-2-l2a"


def test_collection_context_mismatch_is_rejected():
    item = load_item()

    with pytest.raises(CatalogProviderError):
        normalize_stac_item(
            item,
            provider_id="test-provider",
            collection_id="different-collection",
        )


def test_preview_is_detected_from_declared_preview_role():
    item = load_item()
    item["assets"]["thumbnail"] = {
        "href": "urn:sentinel-explorer:fixture:thumbnail",
        "roles": ["thumbnail"],
    }

    scene = normalize_stac_item(item, provider_id="test-provider")

    assert scene.preview_available is True


def test_asset_hrefs_are_not_exposed_in_scene_dto():
    item = load_item()
    scene = normalize_stac_item(item, provider_id="test-provider")
    serialized = scene.model_dump_json()

    for asset in item["assets"].values():
        assert asset["href"] not in serialized
    assert "assets" not in serialized
