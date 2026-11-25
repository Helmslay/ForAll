# Project status

**Last updated:** 2026-11-25

## Repository state
- Presentation landing page: present at `/index.html`; GIS-first redesign LP-01 is complete in PR #9. The concept map is explicitly illustrative; browser GIS functionality is not claimed as implemented.
- Landing page README: updated with documentation links.
- Browser application source: Vue 3/Vite/TypeScript shell is present under `app/`; hosted production build and Vite dev-server HTTP smoke-check passed. OpenLayers empty map canvas/lifecycle (WEB-02.04), WGS84 cursor readout/local resolution (WEB-02.06) and local rectangle AOI draw/clear (WEB-02.07) are implemented. Base map, catalog API orchestration/UI and imagery are not implemented; generic STAC HTTP client and configurable adapter exist, but no provider endpoint is enabled or approved. WEB-01.08 connects the frontend development server to the backend health endpoint through a proxy.
- Frontend quality tooling: ESLint, Prettier, vue-tsc and Vitest are configured; hosted CI checks pass. One render test covers the scaffold. npm audit retains a fail-closed high/critical gate with one temporary, exact dev-tool advisory exception (ADR-013).
- Backend source: FastAPI scaffold, request ID middleware, normalized error responses and `GET /api/v1/health` are implemented under `backend/`; WEB-01.08 added the Vite development proxy and typed health client (PR #15 merged; CI run `44115192957` SUCCESS). WEB-01.09 added a two-service Docker Compose development stack (PR #16 merged; CI run `44118409536` SUCCESS), including healthy dependencies and a successful frontend-to-API proxy smoke-check. WEB-01.10 (PR #17 merged; frontend CI run `44126893666` SUCCESS) hardens host port publication to localhost only and adds a CI assertion; the local development guide is available in `docs/LOCAL_DEVELOPMENT.md`. No database or raster dependencies are included yet.
- Root structure placeholders `scripts/` and `deployment/`, `.gitignore`, and a secret-free `.env.example` were added by WEB-01.01.
- A standalone allowlisted STAC connectivity checker and offline mock tests are present under /tools; this is a diagnostic utility, not the application or a provider adapter.
- Database and storage: not provisioned.
- Russian VPS → STAC catalog: partially verified on 2026-11-20. Earth Search and CDSE root/collections passed; Planetary Computer root passed but collections exceeded the diagnostic response-size limit. VPS egress country/ASN reported RU/AS44112 by two services. Real STAC Search, raster assets, COG reads and storage remain unverified (Issues #58 and #60; details in `docs/DATA_SOURCE_TEST_MATRIX.md`).
- User-side access from Russian networks without VPN: not verified.
- First user-side local Windows dev-build verified on 2026-11-18: frontend production build succeeded; FastAPI started on `127.0.0.1:8000`; direct `/api/v1/health` and proxied `http://127.0.0.1:5173/api/v1/health` both returned `status=ok`, version `0.1.0`; app opened in Chrome; no other Console errors were reported besides missing `/favicon.ico` (404). This verifies the local scaffold only, not GIS features or Russian network access.

## Documentation state
- Product requirements: documented.
- Architecture: documented.
- UX/UI guide: documented.
- Data source and Russia access gate: documented.
- API contracts: drafted.
- Testing and QA: documented.
- Deployment: documented.
- AI task workflow: documented.
- Roadmap: documented.
- Phase task cards: documented for phases 00–08.
- WEB-00.01 and WEB-00.02: completed as documentation/diagnostic tasks; no provider has been validated.
- WEB-01.01: completed early with explicit user authorization as an independent repository bootstrap; this does not bypass G0.
- WEB-01.02: frontend scaffold completed and CI-verified.
- WEB-01.03: frontend quality scripts and one unit test completed and CI-verified.
- WEB-01.04: semantic GIS application shell completed; frontend CI run `44102025691` passed all checks.
- UX-01: unified soft neutral palette applied to landing and app; frontend CI run `44102877694` and landing CI run `44102877715` passed.
- WEB-01.10: local development guide and dev-port hardening completed; PR #17 merged, exact-head frontend CI run `44126893666` SUCCESS, merge commit `9936f6af3942ff929867478bbeb237b7c5fce29b`.
- WEB-01.11: dependency audit gate added in PR #19; initial audit CI run `44132980902` SUCCESS; final exact-head CI run `44133991243` SUCCESS. Seven moderate findings were classified as devDependency/transitive paths; no forced updates.
- WEB-01.12: temporary user-approved risk acceptance for GHSA-fc5q-39xc-vjpf implemented in PR #27, merged as `f65060be3a9f862a20e2473cc2e4ea3ed26471aa`; exact-head frontend CI run `44328382848` SUCCESS. Exception is limited to the reviewed dev-only picomatch dependency graph and expires/requires review by 2026-12-02. This is not a vulnerability fix.
- WEB-02.01: semantic CSS design tokens completed in PR #28, merged as `d7a13244e6d06615995f48561523149bb21f9c79`; exact-head frontend CI run `44329428142` SUCCESS, including npm audit policy tests, lint, format, typecheck, unit tests, production build, backend proxy smoke, Compose config/localhost binding and Compose frontend/API smoke.
- WEB-02.02: desktop app shell completed in PR #29, merged as `3dc70e8df8e271ec2bacf60b70341a53b01eb9a7`; exact-head frontend CI run `44331108330` SUCCESS, including lint, format, typecheck, unit tests, production build, backend proxy smoke and Compose frontend/API smoke.
- WEB-02.03: responsive contextual panels completed in PR #30, merged as `39161d5c1cbedea6756e10ed711c139681313c24`; exact-head frontend CI run `44332026191` SUCCESS. Tablet drawer, mobile bottom sheet, explicit touch-sized controls and backdrop dismissal are implemented; physical-device visual review remains outstanding.
- WEB-02.04: DONE; PR #32 merged as `331b06dd9c82fa0a5ee39691a767b71a52da94fe`. OpenLayers `10.11.0`, empty map canvas, ResizeObserver cleanup and lifecycle tests are implemented. Exact-head Frontend build CI run `44339512145` SUCCESS, including npm audit policy/audit, lint, format, typecheck, unit tests, production build, backend proxy smoke, Compose config/localhost binding, Compose startup and frontend/API smoke. Temporary bootstrap workflows were removed before PR creation.

## Current milestone
G1 — first local frontend/backend development build verified on the user's Windows computer on 2026-11-18. По прямому решению пользователя G0 отложен до проверки доступности через готовое приложение; он остаётся OPEN и не блокирует разработку каталога/API. Доступность без VPN не подтверждена.

## Next task

WEB-03.12A — search UI states and cursor pagination — DONE. PR #66 merged as `8a669b28c7c9973bfd51ee17eed04a75320312df`; exact PR head `7d6ab3ca16ad3a73d1557f5b8823cbb72a19e573`; GitHub Actions Frontend Build run `45175830402` SUCCESS (5 files / 30 tests passed); mirror run `45175821338` SUCCESS.

WEB-03.12B — real provider search acceptance — BLOCKED pending explicit provider approval and G0 validation. No provider was selected or activated in WEB-03.12A. Do not claim live Sentinel-2 results or no-VPN availability.

## Important blockers
1. No provider has been approved as primary; provider selection is deferred until application-level testing.
2. Real Sentinel-2 asset access from a Russian backend has not been proven.
3. Permission to cache and redistribute each candidate source's data must be reviewed.
4. The user-facing path from Russian home/mobile networks without VPN has not been tested. Do not claim no-VPN availability.
5. One high-severity advisory GHSA-fc5q-39xc-vjpf remains present in the frontend development toolchain (`picomatch@4.0.7` and exact transitive paths). It is temporarily accepted under ADR-013; npm audit continues to block all other high/critical findings. Review/remove the exception by 2026-12-02 or earlier when an upstream fix is available. No production dependency is affected; no forced upgrade or audit suppression was used.

## Status policy
Update this file when a milestone or material project decision changes. Do not mark a task DONE based only on generated code; follow the acceptance criteria in the task card.


## User decisions recorded — 2026-11-20
- G0/provider selection is deferred until the user tests the completed application. Do not spend development sessions on VPS or diagnostic-agent maintenance; continue application development with explicit allowlisted endpoints and mocked tests.
- No primary provider is approved. Provider availability, real asset access, licensing and no-VPN user access remain unverified.


## Current task

WEB-03.12A — search UI states and cursor pagination — DONE (PR #66 merged). Next: WEB-03.12B — real provider search acceptance — BLOCKED pending explicit provider approval/G0.

## Supporting automation — 2026-11-25
- OPS-CTRL-01 — public hash-only approval relay for the separate private Sentinel Agent is merged in ForAll PRs #72/#73; current ForAll main trust anchor is `0bac23ea77ccddc2332aae070a80c412912d9405`. Private Sentinel verifier merged in Sentinel PR #89 (`170b316f52d61e4d4d0f7eb73d92d580b5e686ef`); CircleCI Python 3.11/3.14 passed on the PR head. Module is isolated under `tools/sentinel_control_relay/`; public workflow emits a hash-only attestation and does not sign or execute commands. Status: IN_REVIEW pending post-merge CI confirmation, manual workflow-dispatch smoke, guarded VPS deployment and read-only E2E. This does not change the browser GIS roadmap or G0–G8 status.
