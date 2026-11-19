import pytest
from pydantic import ValidationError

from app.schemas.catalog import ProviderStatus, Scene, SearchRequest, SearchResponse

VALID_SEARCH = {
    "bbox": [56.0, 57.0, 58.0, 59.0],
    "datetime": {
        "from": "2025-06-01T00:00:00Z",
        "to": "2025-09-01T23:59:59Z",
    },
    "cloud_cover_lte": 20,
    "collections": ["sentinel-2-l2a"],
    "providers": ["earth-search"],
    "limit": 100,
    "cursor": None,
}

VALID_SCENE = {
    "key": "opaque-scene-key",
    "provider": "earth-search",
    "collection": "sentinel-2-l2a",
    "item_id": "provider-item-id",
    "acquired_at": "2025-06-15T07:20:00Z",
    "platform": "sentinel-2b",
    "cloud_cover": 12.5,
    "bbox": [56.0, 57.0, 58.0, 59.0],
    "geometry": {},
    "available_bands": ["B02", "B03", "B04", "B08"],
    "preview_available": True,
}


def test_search_request_accepts_contract_payload_and_limit_100() -> None:
    request = SearchRequest.model_validate(VALID_SEARCH)

    assert request.bbox == (56.0, 57.0, 58.0, 59.0)
    assert request.limit == 100
    assert request.datetime.start.isoformat() == "2025-06-01T00:00:00+00:00"
    serialized = request.model_dump(mode="json", by_alias=True)
    assert serialized["datetime"]["from"].endswith("+00:00")


@pytest.mark.parametrize(
    "bbox",
    [
        [56.0, 57.0, 58.0],
        [58.0, 57.0, 56.0, 59.0],
        [56.0, 59.0, 58.0, 57.0],
        [-181.0, 57.0, 58.0, 59.0],
        [56.0, -91.0, 58.0, 59.0],
        [56.0, 57.0, float("inf"), 59.0],
    ],
)
def test_search_request_rejects_invalid_bbox(bbox: list[float]) -> None:
    with pytest.raises(ValidationError):
        SearchRequest.model_validate({**VALID_SEARCH, "bbox": bbox})


@pytest.mark.parametrize(
    "datetime_range",
    [
        {"from": "2025-09-01T00:00:00Z", "to": "2025-06-01T00:00:00Z"},
        {"from": "2025-06-01T00:00:00", "to": "2025-09-01T00:00:00Z"},
        {"from": "2025-06-01T03:00:00+03:00", "to": "2025-09-01T00:00:00Z"},
    ],
)
def test_search_request_rejects_invalid_datetime_range(
    datetime_range: dict[str, str],
) -> None:
    with pytest.raises(ValidationError):
        SearchRequest.model_validate({**VALID_SEARCH, "datetime": datetime_range})


@pytest.mark.parametrize("cloud_cover", [-0.1, 100.1, float("nan")])
def test_search_request_rejects_invalid_cloud_cover(cloud_cover: float) -> None:
    with pytest.raises(ValidationError):
        SearchRequest.model_validate(
            {**VALID_SEARCH, "cloud_cover_lte": cloud_cover}
        )


@pytest.mark.parametrize("limit", [0, 101, 1.5])
def test_search_request_rejects_invalid_limit(limit: int | float) -> None:
    with pytest.raises(ValidationError):
        SearchRequest.model_validate({**VALID_SEARCH, "limit": limit})


def test_search_request_allows_optional_providers_and_cloud_cover() -> None:
    payload = {
        key: value
        for key, value in VALID_SEARCH.items()
        if key not in {"providers", "cloud_cover_lte"}
    }

    request = SearchRequest.model_validate(payload)

    assert request.providers is None
    assert request.cloud_cover_lte is None


def test_scene_accepts_missing_optional_metadata() -> None:
    scene = Scene.model_validate(
        {
            key: value
            for key, value in VALID_SCENE.items()
            if key in {
                "key",
                "provider",
                "collection",
                "item_id",
                "acquired_at",
                "available_bands",
                "preview_available",
            }
        }
    )

    assert scene.platform is None
    assert scene.cloud_cover is None
    assert scene.bbox is None
    assert scene.geometry is None


def test_scene_rejects_unsupported_or_duplicate_bands() -> None:
    with pytest.raises(ValidationError):
        Scene.model_validate({**VALID_SCENE, "available_bands": ["B02", "B05"]})

    with pytest.raises(ValidationError):
        Scene.model_validate({**VALID_SCENE, "available_bands": ["B02", "B02"]})


def test_scene_rejects_signed_url_and_non_utc_acquisition_time() -> None:
    with pytest.raises(ValidationError):
        Scene.model_validate(
            {**VALID_SCENE, "signed_url": "https://example.invalid/x"}
        )

    with pytest.raises(ValidationError):
        Scene.model_validate(
            {**VALID_SCENE, "acquired_at": "2025-06-15T10:20:00"}
        )


def test_provider_status_accepts_known_states_and_utc_timestamp() -> None:
    status = ProviderStatus.model_validate(
        {
            "id": "earth-search",
            "status": "partial",
            "last_checked": "2025-06-15T07:20:00Z",
            "reason": "Some records were unavailable",
        }
    )

    assert status.status == "partial"
    assert status.last_checked is not None
    assert status.last_checked.utcoffset().total_seconds() == 0


def test_provider_status_rejects_unknown_state_and_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ProviderStatus.model_validate(
            {"id": "earth-search", "status": "healthy"}
        )

    with pytest.raises(ValidationError):
        ProviderStatus.model_validate(
            {"id": "earth-search", "status": "success", "traceback": "private"}
        )


def test_search_response_nests_scene_and_provider_dtos() -> None:
    response = SearchResponse.model_validate(
        {
            "items": [VALID_SCENE],
            "next_cursor": None,
            "providers": [{"id": "earth-search", "status": "success"}],
            "partial": False,
        }
    )

    assert response.items[0].key == "opaque-scene-key"
    assert response.providers[0].status == "success"
    assert response.partial is False
