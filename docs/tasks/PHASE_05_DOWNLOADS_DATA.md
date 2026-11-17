# Phase 05 — exports and storage

All tasks PLANNED. Terms/cache rules in DATA_ACCESS_RUSSIA.md.

## WEB-05.01 — StorageBackend contract
Define put/read/stat/delete/exists; return stable key, size, checksum. No secret credentials. Interface only.

## WEB-05.02 — local filesystem backend
Safe root; path traversal protection; atomic writes; checksum; temp cleanup. Test read/write/delete, bad path, interrupted write.

## WEB-05.03 — production storage config
Settings for endpoint/bucket/region/credentials via env; TLS verify; timeouts; safe logs. Real credentials not committed.

## WEB-05.04 — Export DTO
Scene key, bbox, bands, format, CRS, resolution; job status enum; validation; align with API contract.

## WEB-05.05 — jobs migration/repository
Persist status, parameters, timestamps, result key, size, checksum, safe error code. Migration and repository tests. No secrets.

## WEB-05.06 — worker lifecycle
Claim job with safe lock/concurrency, queued→running→succeeded/failed; finite retries; test duplicate worker cannot run same job.

## WEB-05.07 — AOI and size limits
Estimate area/output pixels/bands; enforce config caps before enqueue. Test too-large AOI.

## WEB-05.08 — single-band GeoTIFF export
Crop/reproject option, transform/CRS/nodata, temp write, validate and atomic store. Independent GDAL read test.

## WEB-05.09 — multiband export
Align grid, correct band order/descriptions, metadata. Test four channel values/order.

## WEB-05.10 — jobs API and UI
Create job, show queued/running/succeeded/failed; poll with backoff; progress only if measurable; download appears only after file verified.

## WEB-05.11 — secure file Range delivery
Authorize job, verify exists/checksum, Content-Disposition, Range, no path guessing. Test full and partial download.

## WEB-05.12 — independent GeoTIFF QA
Check CRS, transform, bands, dtype, nodata, metadata, checksum; open in GIS if available; save report.
