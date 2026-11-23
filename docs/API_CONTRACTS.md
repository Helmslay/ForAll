# API contracts — Sentinel Explorer Web

## 1. Общие правила
- Prefix: /api/v1.
- JSON UTF-8, кроме tile/file responses.
- Время: ISO 8601 UTC.
- География: EPSG:4326; bbox order [west, south, east, north].
- DTO не содержат токены, signed upstream URL и локальные пути.
- API сначала фиксируется здесь, потом реализуется.
- Несовместимые изменения требуют версии/согласованной миграции.

## 2. Error format

    {
      "error": {
        "code": "PROVIDER_UNAVAILABLE",
        "message": "Каталог временно недоступен",
        "request_id": "opaque-request-id",
        "details": {}
      }
    }

message безопасен для пользователя. Stack trace и адреса — только в серверном логе. details не содержит secrets.

## 3. Health
GET /api/v1/health — status, app_version, timestamp; без секретов и sensitive host details.
GET /api/v1/health/providers — внутренний/защищённый status sources, last check и safe reason; не делать подробный мониторинг публичным.

## 4. Search
POST /api/v1/catalog/search

Request:

    {
      "bbox": [56.0, 57.0, 58.0, 59.0],
      "datetime": {
        "from": "2025-06-01T00:00:00Z",
        "to": "2025-09-01T23:59:59Z"
      },
      "cloud_cover_lte": 20,
      "collections": ["sentinel-2-l2a"],
      "providers": ["earth-search"],
      "limit": 20,
      "cursor": null
    }

Rules: bbox contains four finite coordinates in [west, south, east, north] order; longitude is within -180..180, latitude within -90..90, west < east and south < north. `datetime.from` and `datetime.to` must be timezone-aware UTC values, with from <= to. `cloud_cover_lte` is optional and, when present, is 0..100. `limit` is an integer from 1 to 100 inclusive (server-enforced maximum: 100). `providers` is optional; `cursor` is opaque and bound to the query signature. Never accept an arbitrary catalog URL.

Response:

    {
      "items": [
        {
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
          "preview_available": true
        }
      ],
      "next_cursor": null,
      "providers": [{"id": "earth-search", "status": "success"}],
      "partial": false
    }

This is an illustrative DTO, not a real scene response.

Search endpoint behavior:
- An unconfigured catalog service returns HTTP 503 with `PROVIDER_UNAVAILABLE`; it never returns a fabricated empty success.
- Provider domain errors use the standard error envelope: `PROVIDER_UNAVAILABLE` and `PROVIDER_CONFIGURATION_ERROR` → 503; `PROVIDER_RATE_LIMITED` → 429; `CATALOG_QUERY_NOT_SUPPORTED` → 422; other catalog provider errors → 502.
- Request validation errors return HTTP 422 with `VALIDATION_ERROR`.
- The endpoint accepts no provider endpoint URL. Provider wiring is server-side only.
- The server-side catalog orchestrator fans out to explicitly configured adapters; no provider is selected by default. `providers`, when supplied, filters the configured adapters.
- Each adapter receives only the requested collections it declares as supported. The merged item list is deduplicated by normalized `Scene.key` and capped at the request `limit`.
- A failed adapter does not discard another adapter's successful items. The response sets `partial=true` and includes a safe per-provider status/reason. Raw upstream exception text and next-link URLs are never returned.
- If an upstream STAC page advertises another page before cursor support is implemented, that provider is marked `partial` with reason `more_results_available`; `next_cursor` remains null until WEB-03.09.
- If all selected adapters fail, the endpoint returns a safe domain error rather than a fabricated empty success. An empty or unmatched adapter selection returns `PROVIDER_UNAVAILABLE`.

## 5. Scene
GET /api/v1/catalog/scenes/{scene_key}

Return the normalized Scene, band availability and optional `resolution`, `crs`, `nodata`, `scale` and `offset` metadata when the source provides them. `platform`, `cloud_cover`, `bbox` and `geometry` may be absent when the source does not provide them; do not synthesize values. The only band identifiers exposed by this DTO are B02, B03, B04 and B08. Never return signed URLs or local paths. Unknown scene key → 404. Provider temporarily unavailable with no cached metadata → 503.

## 6. RGB tiles
GET /api/v1/imagery/{scene_key}/tiles/{z}/{x}/{y}.png

Query:
- r, g, b: B02|B03|B04|B08;
- stretch: percentile|manual;
- p_low/p_high or min/max for selected mode;
- gamma: positive bounded value.

Every pixel-affecting parameter is in cache key. Validate band availability. Unknown parameter → 422. Missing asset → safe domain error. Return image/png; JSON errors before streaming begins.

## 7. Statistics
GET /api/v1/imagery/{scene_key}/statistics?band=B04

Return band, method, sample/percentile metadata, min, max, p2, p98 if calculated, nodata count and status. Never invent values. Invalid/empty statistics is an explicit state.

## 8. Export
POST /api/v1/downloads

Request:

    {
      "scene_key": "opaque-scene-key",
      "bbox": [56.0, 57.0, 58.0, 59.0],
      "bands": ["B02", "B03", "B04", "B08"],
      "format": "geotiff",
      "target_crs": "EPSG:32640",
      "resolution": null
    }

Validate AOI area, size estimate, bands, CRS and resolution before enqueue. Return job_id, status, created_at, estimated_size_bytes if available. Do not block HTTP until raster processing ends.

## 9. Jobs and file
GET /api/v1/jobs/{job_id}: queued, running, succeeded, failed, cancelled. Progress only when measurable; otherwise null.
GET /api/v1/downloads/{job_id}/file: only after succeeded and checksum verified; supports Range where possible; check authorization and file existence.

## 10. Vector APIs (future)
POST /api/v1/vectors/upload — multipart with size/format limits.
GET /api/v1/vectors/{layer_id} — layer metadata.
GET /api/v1/vectors/{layer_id}/features?bbox=... — features.
GET /api/v1/vectors/{layer_id}/features/{feature_id} — geometry and attributes.

Do not implement before corresponding roadmap phase.

## 11. IDs and pagination
Internal scene key must not include raw signed URLs. Cursor opaque, signed or server-stored, bound to query/provider. Do not use offset pagination if provider supports cursor/next link. Deduplicate only with reliable identity.

## 12. Request ID
Every request has request_id. Include in errors and structured logs with provider/job id. Never log secrets or full signed href.
