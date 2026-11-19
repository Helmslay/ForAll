from datetime import UTC, datetime, timedelta
from math import isfinite
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BandName = Literal["B02", "B03", "B04", "B08"]
BBox = tuple[float, float, float, float]
ProviderState = Literal["success", "partial", "unavailable"]


def _validate_bbox(value: BBox) -> BBox:
    west, south, east, north = value
    if not all(isfinite(coordinate) for coordinate in value):
        raise ValueError("bbox coordinates must be finite")
    if not (-180 <= west <= 180 and -180 <= east <= 180):
        raise ValueError("bbox longitude must be between -180 and 180")
    if not (-90 <= south <= 90 and -90 <= north <= 90):
        raise ValueError("bbox latitude must be between -90 and 90")
    if west >= east:
        raise ValueError("bbox west must be less than east")
    if south >= north:
        raise ValueError("bbox south must be less than north")
    return value


def _validate_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("datetime must include a UTC timezone")
    return value.astimezone(UTC)


class DTOModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class DateTimeRange(DTOModel):
    start: datetime = Field(alias="from")
    end: datetime = Field(alias="to")

    @field_validator("start", "end")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        return _validate_utc_datetime(value)

    @model_validator(mode="after")
    def require_ordered_range(self) -> "DateTimeRange":
        if self.start > self.end:
            raise ValueError("datetime.from must not be after datetime.to")
        return self


class SearchRequest(DTOModel):
    bbox: BBox
    datetime: DateTimeRange
    cloud_cover_lte: float | None = Field(
        default=None, ge=0, le=100, allow_inf_nan=False
    )
    collections: list[str]
    providers: list[str] | None = None
    limit: int = Field(ge=1, le=100, strict=True)
    cursor: str | None

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, value: BBox) -> BBox:
        return _validate_bbox(value)


class Scene(DTOModel):
    key: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    collection: str = Field(min_length=1)
    item_id: str = Field(min_length=1)
    acquired_at: datetime
    platform: str | None = None
    cloud_cover: float | None = Field(
        default=None, ge=0, le=100, allow_inf_nan=False
    )
    bbox: BBox | None = None
    geometry: dict[str, Any] | None = None
    available_bands: list[BandName]
    preview_available: bool
    resolution: float | None = Field(default=None, allow_inf_nan=False)
    crs: str | None = None
    nodata: float | None = Field(default=None, allow_inf_nan=False)
    scale: float | None = Field(default=None, allow_inf_nan=False)
    offset: float | None = Field(default=None, allow_inf_nan=False)

    @field_validator("acquired_at")
    @classmethod
    def require_utc_acquired_at(cls, value: datetime) -> datetime:
        return _validate_utc_datetime(value)

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, value: BBox | None) -> BBox | None:
        return _validate_bbox(value) if value is not None else None

    @field_validator("available_bands")
    @classmethod
    def require_unique_bands(cls, value: list[BandName]) -> list[BandName]:
        if len(value) != len(set(value)):
            raise ValueError("available_bands must not contain duplicates")
        return value


class ProviderStatus(DTOModel):
    id: str = Field(min_length=1)
    status: ProviderState
    last_checked: datetime | None = None
    reason: str | None = None

    @field_validator("last_checked")
    @classmethod
    def require_utc_last_checked(cls, value: datetime | None) -> datetime | None:
        return _validate_utc_datetime(value) if value is not None else None


class SearchResponse(DTOModel):
    items: list[Scene]
    next_cursor: str | None
    providers: list[ProviderStatus]
    partial: bool
