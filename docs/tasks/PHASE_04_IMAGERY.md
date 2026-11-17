# Phase 04 — real imagery and RGB

All tasks PLANNED. Read ARCHITECTURE.md and API_CONTRACTS.md. Provider and assets must pass G0.

## WEB-04.01 — RasterAsset model
Fields: internal href ref, band, media type, CRS, GSD, dimensions, nodata, scale, offset. Optional remain optional. Tests.

## WEB-04.02 — safe asset resolver
Resolve scene key + band through provider allowlist. Validate hostname/redirects; reject arbitrary URL, localhost/private IP. Test SSRF cases. Signed URLs server-only.

## WEB-04.03 — raster inspect
Rasterio/GDAL metadata: dims, CRS, transform, dtype, nodata, block layout, band metadata. Test actual item and unsupported asset behavior.

## WEB-04.04 — read one band window
Bounded AOI window, transform, pixel cap, data+mask. Synthetic raster test verifies exact pixels.

## WEB-04.05 — nodata/scale/offset
Apply only explicit metadata, once. Keep raw values where export requires. Test known raw values and nodata.

## WEB-04.06 — one-band statistics
Ignore nodata, deterministic sample, min/max/percentiles/count. Empty valid pixel set returns explicit error. No fallback guessing.

## WEB-04.07 — statistics QA
Fixtures: constant, gradient, nodata-heavy, all-nodata, outlier, offset. Tolerance tests; offline.

## WEB-04.08 — RGB composite window
Read and align three bands, handle mask/nodata, stretch, gamma, compose RGB. Synthetic distinct channel tests prove ordering.

## WEB-04.09 — render validation
Pydantic allowed bands, stretch, percentiles, min/max, gamma. Invalid params 422 before raster work.

## WEB-04.10 — PNG tile endpoint
Validate scene/z/x/y and render params; output tile; safe errors before streaming. Tests decode PNG and check dimensions.

## WEB-04.11 — tile cache
Key includes scene/z/x/y/bands/stretch/gamma/version. TTL and size cap. Test changed R band produces a different key.

## WEB-04.12 — OpenLayers imagery layer
Tile source uses same-origin API. Update when scene/render settings change; remove old source/layer; display loading/error. No upstream URL in browser.

## WEB-04.13 — independent RGB selectors
Three independent controls with B02/B03/B04/B08; each updates only its slot. Repeated channel assignment follows UX contract.

## WEB-04.14 — stretch/gamma controls
Percentile/manual/gamma/reset, loading/error. Control state must match request parameters actually sent.

## WEB-04.15 — real-scene smoke test
Open real item; render default; change R/G/B separately; pan/zoom; inspect nodata, georeferencing and cache. Save report. Acceptance requires real data, not fixtures only.
