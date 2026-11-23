# Project status

**Last updated:** 2026-11-23

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

- WEB-02.03 — responsive panels: DONE (PR #30; exact-head frontend CI run `44332026191` SUCCESS; merge commit `39161d5c1cbedea6756e10ed711c139681313c24`).

- WEB-02.04 — OpenLayers lifecycle — DONE (PR #32; exact-head CI run `44339512145` SUCCESS; merge commit `331b06dd9c82fa0a5ee39691a767b71a52da94fe`).

- WEB-02.05 — base map provider abstraction remains deferred pending source/network and licensing verification; this does not block catalog/API work.
- WEB-02.06 — cursor coordinates and map resolution — DONE (PR #35 merged as `b3870808b0b6ada015d5f1cc158abedd86c9621c`; exact-head Frontend build CI run `44358215174` SUCCESS for `3b03c7cbd18a9c5165e2d498c9aca637f28ee900`; tools offline tests run `44357847194` SUCCESS). WGS84 longitude/latitude, local ground resolution and pointerleave empty state are implemented. The audit command was aligned with the existing high/critical threshold; moderate dev-tool findings remain reported.
- WEB-02.07 — AOI rectangle draw/clear — DONE (PR #36 merged as `b485dfb429f50292702410bb43d4283cf9c3a8e9`; exact-head Frontend build CI run `44359722241` SUCCESS for `6223561722c18c079037da171da4f945fadc6c44`). Local Draw interaction, single AOI feature, WGS84 bbox `[west,south,east,north]`, cancel/clear and zero-area validation are implemented.
- WEB-02.08 — search form shell — DONE (PR #52 merged; merge commit `f6b75e6071b3779f693abdeb1a35c62015ffeea3`; exact-head Frontend CI run `44552193095` SUCCESS; 17/17 unit tests PASS; lint/format/typecheck/build and Compose smoke PASS). Search parameters are prepared locally; network search is intentionally not connected.

- WEB-03.01 — Scene/Search DTO — DONE (PR #53 merged; exact-head backend CI run `44576619525` SUCCESS, 30 tests + Uvicorn smoke; exact-head frontend CI run `44576619705` SUCCESS; merge commit `8ca882cc7cde1769d0293f92a5d9f39f3b86b79e`). WEB-03.02 — CatalogProvider Protocol — DONE (PR #54 merged; exact-head backend CI run `44589067499` SUCCESS, 40 passed + Uvicorn smoke; exact-head frontend CI run `44589067504` SUCCESS; merge commit `ccd9f52d449b5322fadc8ff4b582d076ce01cbe5`). WEB-03.03 — STAC fixtures — DONE (PR #56 merged; merge commit `4738710c6baf5fdfb7ce530d5b6fceac35ef0fb6`; exact-head backend tests, frontend build and mirror SUCCESS). WEB-03.04 — STAC HTTP client — DONE (PR #58 merged as `ad0b06b0c7b01f06796cda9e3df62061c622217f`; exact-head backend tests `44724633948`, frontend build `44724633952` and mirror `44724626930` all SUCCESS). WEB-03.05 — configurable STAC adapter — DONE (PR #59 merged as `87a97534c4a3ce8b8fdecb76052e6f7210ca59a2`; exact-head backend tests `44725439719` and mirror `44725430664` SUCCESS). WEB-03.06 — STAC Item normalizer — DONE (PR #60 merged as `29fd0c5e757b6d69b9214d4086f1c7d496ba88df`; exact-head Backend tests `44726072118` — 91 passed + Uvicorn smoke SUCCESS; mirror `44726047813` SUCCESS). WEB-03.07 — search API endpoint — DONE (PR #61 merged as `b4de0685dce0d6e9c1cde1250a9dbf21c851d9b0`; exact-head Backend tests `45108920988` — 106 passed + Uvicorn smoke SUCCESS; mirror `45108914359` SUCCESS). Next: WEB-03.09 — encrypted aggregate cursor pagination (IN_PROGRESS; draft PR #63; codec and aggregate orchestration integrated, continuation tests/CI in progress). WEB-00.10/provider selection remains deferred; do not claim a primary source or no-VPN availability.
- WEB-00.03 remains IN_PROGRESS; Russian-network STAC Search is deferred until the user tests through the usable application. Do not repeat diagnostic-agent work or already completed base GET checks. G0 is OPEN but deferred from the current development critical path by explicit user decision.

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
WEB-03.09 — encrypted aggregate cursor pagination — IN_PROGRESS; draft PR #63. AES-256-GCM codec is wired to the API and the orchestrator now maintains encrypted per-provider continuation/buffer state, global result limits and cross-page deduplication. Exact-head backend CI on `5f29f21b88526d3ad5c27e4efc8d0e0ba29178c2`: 140 passed + Uvicorn smoke SUCCESS; mirror SUCCESS. Additional cursor-state overflow/opacity tests are committed after that verified head and await a fresh exact-head CI run. Do not mark DONE until all acceptance checks pass. G0 remains OPEN and deferred from the development critical path by explicit user decision.
