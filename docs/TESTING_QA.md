# Testing and QA strategy

## 1. Принцип
Каждая задача имеет проверяемые критерии приёмки. Сгенерированный код и сообщение модели не являются доказательством корректности.

## 2. Test layers

### Unit
- STAC Item → Scene normalization;
- bbox/date/cloud/band validators;
- RGB assignment and cache key;
- nodata/scale/offset;
- statistics;
- scene identity;
- DTO and error mapping.

### Integration
- API + test database;
- provider adapters using saved fixtures;
- Rasterio/GDAL on small COG/GeoTIFF fixtures;
- storage adapter;
- jobs/worker;
- Range download;
- PostGIS migrations.

### E2E
- map opens;
- AOI selection;
- search;
- select scene;
- RGB update;
- export job;
- download file.

### Network
Mark separately (for example, network test marker). Run controlled/manual or scheduled with approved credentials. Unit tests must not fail because a foreign provider is temporarily unavailable.

## 3. Fixtures
Use small synthetic rasters with known CRS, transform, dimensions, dtype, nodata, scale/offset and pixel values. RGB fixtures must have different values per band to expose channel swaps. Use a test HTTP server for Range and error scenarios.

Real Sentinel scenes are for limited integration/network smoke tests. Record item ID, date, provider and permitted use. Do not store credentials or signed hrefs in fixtures.

## 4. Raster QA
Check:
- B02/B03/B04/B08 map to correct inputs;
- RGB order is correct;
- nodata doesn't become false color;
- channel grid alignment/resampling is explicit;
- scale/offset applied from metadata and exactly once;
- percentile stretch uses valid pixels;
- bad stats create an error state, not random black output;
- cache key changes on any render change;
- export CRS/transform checked independently;
- GeoTIFF opens in desktop GIS.

## 5. Russia QA
Follow DATA_ACCESS_RUSSIA.md. Maintain two reports:
- backend connectivity from Russian infrastructure;
- user accessibility from Russian networks without VPN.

Do not merge these results. Report date, app version, non-identifying provider/region, DNS/TLS/API/asset/tile/download result.

## 6. Task acceptance
Before READY: dependencies DONE, scope and expected behavior clear, tests known.
Before DONE: lint/format, typecheck, target tests, existing tests, card acceptance, diff review, docs update where contracts changed.

If a test could not run, report exact reason. Never claim all tests passed if not run.

## 7. Release smoke tests
1. Open clean browser profile.
2. Check health.
3. Open map.
4. Execute real search.
5. Open real scene with four channels.
6. Change each RGB assignment.
7. Pan/zoom and request new tiles.
8. Export limited AOI.
9. Inspect GeoTIFF with independent GDAL/Rasterio.
10. Verify checksum and Range download.
11. Repeat on Russian network without VPN.
12. Test cached data when upstream is disconnected.

## 8. Severity
P0: security, secret leak, wrong/substituted data, application cannot start.
P1: MVP search/view/export failure, wrong georeferencing, channel order wrong.
P2: major UX/performance issue not blocking core data.
P3: cosmetic/improvement.
