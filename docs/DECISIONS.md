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

## ADR-010 — G1 foundation may proceed before G0 completion
**Status:** Accepted by explicit user authorization (2026-11-17).  
**Context:** The user will perform Russian-network acceptance checks after the first development build. Completing the frontend/backend development foundation does not require implementing satellite-data access.  
**Decision:** Continue G1 foundation tasks through the first local development build while G0 remains open. Do not implement provider adapters, real STAC search, raster access, imagery rendering, downloads, or claim no-VPN availability before the applicable G0 checks pass. Russian-network tests are deferred until the user receives the dev-build.  
**Consequences:** G1 work is temporarily authorized as a sequencing exception. G0 remains an independent hard gate for all real data/provider functionality and release claims.
