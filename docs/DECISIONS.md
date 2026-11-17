# Architecture decision log

Use this log for decisions affecting more than one module. Format: status, context, decision and consequences.

## ADR-001 — modular monolith
**Status:** Accepted. Vue frontend + FastAPI backend with internal modules. No microservices initially. Easier for small tasks and local testing; split only when measured need appears.

## ADR-002 — browser never calls upstream catalog directly
**Status:** Accepted. Production search/imagery/download use the app backend. Centralizes auth, availability, caching and avoids exposing secrets.

## ADR-003 — provider adapters
**Status:** Accepted. Each STAC/raster provider maps to common Scene model. UI is provider-independent.

## ADR-004 — Russian hosting and network gate
**Status:** Accepted. App/API/cache in Russia. Upstream reachability and end-user access are separate test gates. No no-VPN claim before evidence.

## ADR-005 — four baseline bands
**Status:** Accepted. MVP B02/B03/B04/B08 and free assignment to RGB. Extra bands require explicit decision. NBR needs SWIR.

## ADR-006 — COG and GDAL/Rasterio
**Status:** Accepted with validation. COG/GeoTIFF primary read path; test real Range/COG on selected source.

## ADR-007 — PostGIS and object storage
**Status:** Accepted. Metadata/geometries/jobs in PostGIS; large rasters/exports in file or S3-compatible storage behind interface.

## ADR-008 — background export
**Status:** Accepted. Long exports are jobs with worker, checksum and file delivery, not long blocking HTTP calls.

## ADR-009 — browser offline scope
**Status:** Accepted with limits. Cache shell and bounded offline packages; local data works offline; no promise of unlimited browser storage.
