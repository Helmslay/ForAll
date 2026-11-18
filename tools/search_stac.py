#!/usr/bin/env python3
"""Run a bounded, allowlisted Sentinel-2 L2A STAC search for the Perm Krai pilot AOI."""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from check_stac import PROVIDERS, Provider, CheckError, get_json, USER_AGENT, AllowlistedRedirectHandler

CENTER_LON = 56.8204
CENTER_LAT = 59.4091
RADIUS_KM = 100
PAGE_LIMIT = 100
MAX_PAGES = 3
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


def make_circle_polygon(lon: float = CENTER_LON, lat: float = CENTER_LAT,
                        radius_km: float = RADIUS_KM, vertices: int = 64) -> dict[str, Any]:
    """Approximate a geodesic circle with a WGS84 polygon."""
    if not (-180 <= lon <= 180 and -90 <= lat <= 90 and radius_km > 0 and vertices >= 8):
        raise ValueError("Invalid AOI parameters")
    angular = radius_km / 6371.0088
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    ring = []
    for index in range(vertices):
        bearing = 2 * math.pi * index / vertices
        lat2 = math.asin(math.sin(lat_r) * math.cos(angular) +
                         math.cos(lat_r) * math.sin(angular) * math.cos(bearing))
        lon2 = lon_r + math.atan2(
            math.sin(bearing) * math.sin(angular) * math.cos(lat_r),
            math.cos(angular) - math.sin(lat_r) * math.sin(lat2),
        )
        ring.append([((math.degrees(lon2) + 540) % 360) - 180, math.degrees(lat2)])
    ring.append(ring[0])
    return {"type": "Polygon", "coordinates": [ring]}


def is_l2a_collection(collection: dict[str, Any]) -> bool:
    text = " ".join(str(collection.get(key, "")) for key in ("id", "title", "description")).lower()
    normalized = text.replace("_", " ").replace("-", " ")
    sentinel = "sentinel 2" in normalized or "sentinel2" in normalized
    level2a = "l2a" in normalized or "level 2a" in normalized or "level-2a" in normalized
    return sentinel and level2a


def _safe_url(url: str, hostname: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != hostname or parsed.username or parsed.password:
        raise CheckError("PAGINATION", "ExternalOrUnsafeLinkBlocked")
    return url


def _request_json(url: str, hostname: str, timeout: float, method: str,
                  payload: dict[str, Any] | None = None) -> tuple[int, Any, float]:
    _safe_url(url, hostname)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/geo+json, application/json", "User-Agent": USER_AGENT}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    started = time.monotonic()
    try:
        opener = urllib.request.build_opener(AllowlistedRedirectHandler(hostname))\n        with opener.open(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            status = response.status
    except urllib.error.HTTPError as exc:
        raise CheckError("SEARCH_HTTP", "HTTPError", exc.code) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", None)
        error_class = type(reason).__name__ if reason is not None else type(exc).__name__
        raise CheckError("SEARCH_HTTP", error_class) from None
    elapsed = round((time.monotonic() - started) * 1000, 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise CheckError("SEARCH_JSON", "ResponseTooLarge", status)
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise CheckError("SEARCH_JSON", "InvalidJSON", status) from None
    return status, parsed, elapsed


def _item_summary(item: dict[str, Any]) -> dict[str, Any]:
    properties = item.get("properties") if isinstance(item.get("properties"), dict) else {}
    summary: dict[str, Any] = {
        "id": item.get("id") if isinstance(item.get("id"), str) else None,
        "collection": item.get("collection") if isinstance(item.get("collection"), str) else None,
        "datetime": properties.get("datetime") or properties.get("start_datetime"),
    }
    cloud = properties.get("eo:cloud_cover")
    if isinstance(cloud, (int, float)) and not isinstance(cloud, bool):
        summary["cloud_cover"] = cloud
    return summary


def search_provider(provider: Provider, timeout: float = 20.0,
                    now: datetime | None = None,
                    json_getter=get_json, request_json=_request_json) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    end = now.astimezone(timezone.utc)
    start = end - timedelta(days=30)
    root = provider.endpoint.rstrip("/") + "/"
    report: dict[str, Any] = {
        "provider": provider.provider_id,
        "hostname": provider.hostname,
        "aoi": {"center_lon": CENTER_LON, "center_lat": CENTER_LAT, "radius_km": RADIUS_KM},
        "datetime": f"{start.isoformat().replace('+00:00', 'Z')}/{end.isoformat().replace('+00:00', 'Z')}",
        "collections": [],
        "item_count": 0,
        "items": [],
        "pages_checked": 0,
        "has_more": False,
        "status": "FAIL",
    }
    try:
        _, collection_payload, _ = json_getter(
            urllib.parse.urljoin(root, "collections"), provider.hostname, timeout
        )
        collections = collection_payload.get("collections") if isinstance(collection_payload, dict) else None
        if not isinstance(collections, list):
            raise CheckError("COLLECTIONS_SCHEMA", "InvalidCollectionsResponse")
        collection_ids = [
            item["id"] for item in collections
            if isinstance(item, dict) and isinstance(item.get("id"), str) and is_l2a_collection(item)
        ]
        if not collection_ids:
            raise CheckError("COLLECTION_DISCOVERY", "Sentinel2L2ACollectionNotFound")
        report["collections"] = collection_ids

        search_url = urllib.parse.urljoin(root, "search")
        payload = {
            "collections": collection_ids,
            "intersects": make_circle_polygon(),
            "datetime": report["datetime"],
            "limit": PAGE_LIMIT,
        }
        summaries = []
        pages = 0
        elapsed_total = 0.0
        method = "POST"
        while pages < MAX_PAGES:
            _, page, elapsed = request_json(search_url, provider.hostname, timeout, method, payload)
            elapsed_total += elapsed
            if not isinstance(page, dict) or page.get("type") != "FeatureCollection" or not isinstance(page.get("features"), list):
                raise CheckError("SEARCH_SCHEMA", "InvalidFeatureCollection")
            pages += 1
            for feature in page["features"]:
                if isinstance(feature, dict):
                    summaries.append(_item_summary(feature))
            next_link = next((link for link in page.get("links", [])
                              if isinstance(link, dict) and link.get("rel") == "next"), None)
            if not next_link:
                break
            report["has_more"] = True
            href = next_link.get("href")
            if not isinstance(href, str):
                raise CheckError("PAGINATION", "InvalidNextLink")
            search_url = _safe_url(urllib.parse.urljoin(search_url, href), provider.hostname)
            method = str(next_link.get("method", "GET")).upper()
            if method not in {"GET", "POST"}:
                raise CheckError("PAGINATION", "UnsupportedNextMethod")
            payload = next_link.get("body") if method == "POST" else None
        report["pages_checked"] = pages
        report["item_count"] = len(summaries)
        report["items"] = summaries
        report["search_latency_ms"] = elapsed_total
        report["status"] = "PASS"
        report["has_more"] = bool(next_link and pages >= MAX_PAGES)
    except CheckError as exc:
        report["error_stage"] = exc.stage
        report["error_class"] = exc.error_class
        if exc.http_status is not None:
            report["error_http_status"] = exc.http_status
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded Sentinel-2 L2A STAC Search for the Perm Krai pilot AOI.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--provider", choices=sorted(PROVIDERS))
    selection.add_argument("--all", action="store_true", help="search every configured provider")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args(argv)
    if not 0.1 <= args.timeout <= 60:
        parser.error("--timeout must be between 0.1 and 60 seconds")
    selected = list(PROVIDERS.values()) if args.all else [PROVIDERS[args.provider]]
    reports = [search_provider(provider, args.timeout) for provider in selected]
    print(json.dumps(reports if args.all else reports[0], ensure_ascii=False, indent=2))
    return 0 if all(item["status"] == "PASS" for item in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
