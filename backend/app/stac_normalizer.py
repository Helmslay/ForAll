"""Normalize STAC Items into the public, secret-free Scene DTO."""

from datetime import UTC, datetime
from math import isfinite
from typing import Any, Mapping
from urllib.parse import quote

from app.catalog_provider import CatalogProviderError
from app.schemas.catalog import BandName, Scene

_MVP_BANDS: tuple[BandName, ...] = ("B02", "B03", "B04", "B08")
_GEOMETRY_TYPES = {
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
    "GeometryCollection",
}


def _is_position(value: Any) -> bool:
    return (
        isinstance(value, (list, tuple))
        and len(value) >= 2
        and all(
            isinstance(coordinate, (int, float))
            and not isinstance(coordinate, bool)
            and isfinite(coordinate)
            for coordinate in value
        )
    )


def _is_ring(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= 4
        and all(_is_position(position) for position in value)
        and value[0] == value[-1]
    )


def _valid_geometry(geometry: Any) -> bool:
    if not isinstance(geometry, Mapping):
        return False
    geometry_type = geometry.get("type")
    if not isinstance(geometry_type, str) or geometry_type not in _GEOMETRY_TYPES:
        return False
    if geometry_type == "GeometryCollection":
        geometries = geometry.get("geometries")
        return isinstance(geometries, list) and all(
            _valid_geometry(child) for child in geometries
        )

    coordinates = geometry.get("coordinates")
    if geometry_type == "Point":
        return _is_position(coordinates)
    if geometry_type == "MultiPoint":
        return isinstance(coordinates, list) and bool(coordinates) and all(
            _is_position(position) for position in coordinates
        )
    if geometry_type == "LineString":
        return isinstance(coordinates, list) and len(coordinates) >= 2 and all(
            _is_position(position) for position in coordinates
        )
    if geometry_type == "MultiLineString":
        return isinstance(coordinates, list) and bool(coordinates) and all(
            isinstance(line, list)
            and len(line) >= 2
            and all(_is_position(position) for position in line)
            for line in coordinates
        )
    if geometry_type == "Polygon":
        return isinstance(coordinates, list) and bool(coordinates) and all(
            _is_ring(ring) for ring in coordinates
        )
    if geometry_type == "MultiPolygon":
        return isinstance(coordinates, list) and bool(coordinates) and all(
            isinstance(polygon, list)
            and bool(polygon)
            and all(_is_ring(ring) for ring in polygon)
            for polygon in coordinates
        )
    return False


def _optional_bbox(value: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) not in (4, 6):
        return None
    coordinates = value[:4]
    if any(
        not isinstance(coordinate, (int, float))
        or isinstance(coordinate, bool)
        or not isfinite(coordinate)
        for coordinate in coordinates
    ):
        return None
    west, south, east, north = coordinates
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        return None
    return (float(west), float(south), float(east), float(north))


def _optional_cloud_cover(value: Any) -> float | None:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not isfinite(value)
        or not 0 <= value <= 100
    ):
        return None
    return float(value)


def _acquired_at(value: Any, provider_id: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise CatalogProviderError(provider_id)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CatalogProviderError(provider_id) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CatalogProviderError(provider_id)
    return parsed.astimezone(UTC)


def _available_bands(assets: Any) -> list[BandName]:
    if not isinstance(assets, Mapping):
        return []
    available: set[str] = set()
    for asset_key, asset in assets.items():
        if not isinstance(asset_key, str) or not isinstance(asset, Mapping):
            continue
        href = asset.get("href")
        if not isinstance(href, str) or not href.strip():
            continue
        if asset_key.upper() in _MVP_BANDS:
            available.add(asset_key.upper())
        eo_bands = asset.get("eo:bands")
        if isinstance(eo_bands, list):
            for band in eo_bands:
                if isinstance(band, Mapping):
                    name = band.get("name")
                    if isinstance(name, str) and name.upper() in _MVP_BANDS:
                        available.add(name.upper())
    return [band for band in _MVP_BANDS if band in available]


def normalize_stac_item(
    item: Mapping[str, Any],
    *,
    provider_id: str,
    collection_id: str | None = None,
) -> Scene:
    """Map one STAC Item to Scene without exposing asset hrefs or inventing metadata.

    collection_id is an optional trusted collection context supplied by the caller
    when a STAC Item omits its collection member.
    """
    if not provider_id.strip() or item.get("type") != "Feature":
        raise CatalogProviderError(provider_id or None)

    item_id = item.get("id")
    item_collection = item.get("collection")
    if not isinstance(item_id, str) or not item_id.strip():
        raise CatalogProviderError(provider_id)
    if item_collection is None:
        item_collection = collection_id
    elif collection_id is not None and item_collection != collection_id:
        raise CatalogProviderError(provider_id)
    if not isinstance(item_collection, str) or not item_collection.strip():
        raise CatalogProviderError(provider_id)

    properties = item.get("properties")
    if not isinstance(properties, Mapping):
        raise CatalogProviderError(provider_id)
    acquired_at = _acquired_at(properties.get("datetime"), provider_id)

    platform = properties.get("platform")
    if not isinstance(platform, str) or not platform.strip():
        platform = None

    geometry = item.get("geometry")
    if not _valid_geometry(geometry):
        geometry = None

    key = ":".join(
        quote(part, safe="") for part in (provider_id, item_collection, item_id)
    )
    return Scene(
        key=key,
        provider=provider_id,
        collection=item_collection,
        item_id=item_id,
        acquired_at=acquired_at,
        platform=platform,
        cloud_cover=_optional_cloud_cover(properties.get("eo:cloud_cover")),
        bbox=_optional_bbox(item.get("bbox")),
        geometry=dict(geometry) if geometry is not None else None,
        available_bands=_available_bands(item.get("assets")),
        preview_available=_has_preview(item.get("assets")),
    )


def _has_preview(assets: Any) -> bool:
    if not isinstance(assets, Mapping):
        return False
    for asset in assets.values():
        if not isinstance(asset, Mapping):
            continue
        href = asset.get("href")
        roles = asset.get("roles")
        if (
            isinstance(href, str)
            and href.strip()
            and isinstance(roles, list)
            and any(isinstance(role, str) and role in {"thumbnail", "overview"} for role in roles)
        ):
            return True
    return False
