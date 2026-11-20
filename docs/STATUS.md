# Project status

**Last updated:** 2026-11-20

## Repository state
- Landing page, frontend shell, backend scaffold, OpenLayers empty map lifecycle, cursor coordinate/resolution readout and AOI rectangle interaction are implemented as recorded in the task history.
- Catalog DTOs and the transport-independent CatalogProvider Protocol are implemented. STAC fixtures are now present on the WEB-03.03 review branch; they are synthetic and offline-only.
- No STAC HTTP client, production provider adapter, search endpoint, catalog orchestration, raster viewer or image download is implemented.
- Database and raster storage are not provisioned.
- Russian upstream access, end-user access from Russian networks without VPN, and a primary provider choice remain unverified.
- The first local Windows development scaffold was verified on 2026-11-18; this does not verify provider access or GIS imagery.

## Current milestone
G1 — first local frontend/backend development build verified. G0 remains open and blocks real provider/raster/imagery implementation.

## Current task
WEB-03.03 — STAC fixtures — IN_REVIEW.
Five synthetic fixtures and offline tests have been added on branch `feat/web-03-03-stac-fixtures`. Backend CI for the pull request has not yet completed. Do not mark DONE until the exact PR head CI and all task acceptance criteria pass.

## Important blockers
1. WEB-00.03 still requires a real STAC Search from a Windows computer in Russia with VPN/proxy disabled.
2. No primary provider has been approved; WEB-03.05 depends on WEB-00.10.
3. Real Sentinel-2 asset access from a Russian backend has not been proven.
4. Provider caching/redistribution terms require review.
5. The user-facing path from Russian home/mobile networks without VPN has not been tested.
6. Frontend dev-tool advisory GHSA-fc5q-39xc-vjpf remains temporarily accepted under ADR-013 and must be reviewed by 2026-12-02.

## Status policy
Mark a task DONE only after exact-head CI, tests and all acceptance criteria pass. Do not claim real provider or no-VPN availability without the required external tests.
