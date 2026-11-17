# Phase 07 — offline and analytics

All tasks PLANNED. An offline claim requires testing with network fully disabled.

## WEB-07.01 — PWA manifest
Add name/theme/icons from actual project assets. Verify browser install metadata.

## WEB-07.02 — app shell cache
Versioned Service Worker caches shell only. Safe update/old cache deletion. Do not cache private authenticated data by default.

## WEB-07.03 — network state UI
Distinguish browser offline, backend unavailable, upstream unavailable and locally cached content. navigator.onLine alone is insufficient.

## WEB-07.04 — offline tile package
Bounded AOI/zoom package; estimate size; quota; manifest, tile params, scene, attribution, expiry; cancellation. Enforce cap.

## WEB-07.05 — offline package import
Validate manifest/checksums; reject traversal/oversize; register local tiles; report corrupt/missing items. Test valid and corrupted files.

## WEB-07.06 — local GeoTIFF offline
Open previously imported local raster without backend; show metadata; dispose resources. Test with network off.

## WEB-07.07 — spectral index contract
Define formula, required bands, units, nodata policy and metadata. Missing bands must fail explicitly.

## WEB-07.08 — NDVI calculation
Formula (B08 - B04) / (B08 + B04). Handle nodata, zero denominator, float output, output range and provenance. Synthetic-array tests.

## WEB-07.09 — NDVI visualization
Add palette/legend and map layer. Document values/range; do not claim NDVI alone identifies logging.

## WEB-07.10 — choose two scenes
Explicit before/after selections, date labels, shared AOI and grid compatibility. Test.

## WEB-07.11 — before/after viewer
Swipe/split view only; don't alter pixels. Divider reveals two actual layers. Test responsive and keyboard controls.

## WEB-07.12 — forest change test set
Document known areas, dates, reference labels, sources, terms, controls without change, uncertainty. No ML model in this task. Provenance required.
