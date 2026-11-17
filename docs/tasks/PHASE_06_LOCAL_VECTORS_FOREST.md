# Phase 06 — local data and forest overlays

All tasks PLANNED. External forest source requires legal and technical review.

## WEB-06.01 — vector layer model
Frontend model: id/name/source/visibility/opacity/z-order/status/attribution. Typed and independent of OpenLayers internals.

## WEB-06.02 — GeoJSON import
Validate file size, syntax, geometry, CRS policy and feature count. Tests valid/malformed/oversized files.

## WEB-06.03 — GeoJSON display
Render point/line/polygon; normal/selected style; layer cleanup. Test fixtures.

## WEB-06.04 — feature identify/attributes
Hit-test selected feature, show safe text/null/long values, stable feature ID. Do not render untrusted attributes as HTML.

## WEB-06.05 — attribute table
Column selection, basic sorting, map/table selection sync, bounded rows or virtualization. Test selection sync.

## WEB-06.06 — Shapefile ZIP
Reject zip-slip, nested archive, extreme compression, excessive entries. Require shp/shx/dbf; handle absent/uncertain prj and encoding explicitly. Security tests.

## WEB-06.07 — local GeoTIFF
Inspect metadata; size cap; browser memory/storage strategy; render without decoding entire large raster into RAM. Test file removal and memory bounds.

## WEB-06.08 — ForestDataProvider contract
BBOX query, layer metadata, features, attributes, auth/error and attribution. Interface only.

## WEB-06.09 — official forest service research
Investigate official docs/authorized endpoints, authentication, terms, coverage, stability, BBOX. Do not assume observed browser endpoints are a public API. Record decision/evidence.

## WEB-06.10 — verified forest layer
Only after legal/network gate. Implement one layer (e.g. forest blocks), normalized features, safe cache and clear errors. No fixture fallback in production.

## WEB-06.11 — forest attributes
Show source-backed attributes for selected feature. Unknown remains unknown; include source attribution.
