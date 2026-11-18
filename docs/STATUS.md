# Project status

**Last updated:** 2026-11-18

## Repository state
- Presentation landing page: present at `/index.html`; GIS-first redesign LP-01 is complete in PR #9. The concept map is explicitly illustrative; browser GIS functionality is not claimed as implemented.
- Landing page README: updated with documentation links.
- Browser application source: minimal Vue 3/Vite/TypeScript scaffold is present under `app/`; hosted production build and Vite dev-server HTTP smoke-check passed. No map, catalog or imagery is implemented yet; WEB-01.08 now connects the frontend development server to the backend health endpoint through a proxy.
- Frontend quality tooling: ESLint, Prettier, vue-tsc and Vitest are configured; hosted CI checks pass. One render test covers the scaffold.
- Backend source: FastAPI scaffold, request ID middleware, normalized error responses and `GET /api/v1/health` are implemented under `backend/`; WEB-01.08 added the Vite development proxy and typed health client (PR #15 merged; CI run `44115192957` SUCCESS). WEB-01.09 added a two-service Docker Compose development stack (PR #16 merged; CI run `44118409536` SUCCESS), including healthy dependencies and a successful frontend-to-API proxy smoke-check. WEB-01.10 (PR #17 merged; frontend CI run `44126893666` SUCCESS) hardens host port publication to localhost only and adds a CI assertion; the local development guide is available in `docs/LOCAL_DEVELOPMENT.md`. No database or raster dependencies are included yet.
- Root structure placeholders `scripts/` and `deployment/`, `.gitignore`, and a secret-free `.env.example` were added by WEB-01.01.
- A standalone allowlisted STAC connectivity checker and offline mock tests are present under /tools; this is a diagnostic utility, not the application or a provider adapter.
- Database and storage: not provisioned.
- Russian upstream access: not verified.
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
- WEB-01.11: dependency audit gate added in PR #19; initial audit CI run `44132980902` SUCCESS; final exact-head CI run `44133991243` SUCCESS. Seven moderate findings were classified as devDependency/transitive paths; zero high/critical findings; no forced updates.

## Current milestone
G1 — first local frontend/backend development build verified on the user's Windows computer on 2026-11-18. G0 remains open and blocks real provider/raster implementation.

## Next task
- WEB-01.09 — Docker Compose dev — DONE (PR #16; CI run `44118409536` SUCCESS; merge commit `3914c94ba3f8e267307b0ad092283bcd8af76dac`).
- WEB-01.10 — local setup guide and dev-port hardening — DONE (PR #17; exact-head CI run `44126893666` SUCCESS; merge commit `9936f6af3942ff929867478bbeb237b7c5fce29b`; depends on WEB-01.09).
- WEB-01.11 — frontend dependency audit — DONE (PR #19; exact-head CI run `44132980902` SUCCESS).
- First local frontend/backend development build on the user's Windows computer: VERIFIED 2026-11-18 (manual smoke test). G1 local-run milestone is complete for the current scaffold.
- Current implementation task: WEB-02.01 — CSS design tokens (G2 UI foundation). G1 prerequisites are DONE and the first local frontend/backend dev-build was verified on the user's Windows computer. WEB-02.01 is independent of provider/data access; G0 remains open and still blocks base-map provider selection, real STAC/provider integration, raster/imagery and downloads. In parallel, WEB-00.03 remains IN_PROGRESS pending the user's real `python tools/search_stac.py --all` run from a Windows computer in Russia with VPN/proxy disabled. PR #24 merged (`2159f17756883c2f51222e89012c5d285081d749`); exact-head and post-merge offline CI passed 23 tests and py_compile.

## Important blockers
1. No provider has been approved as primary.
2. Real Sentinel-2 asset access from a Russian backend has not been proven.
3. Permission to cache and redistribute each candidate source's data must be reviewed.
4. The user-facing path from Russian home/mobile networks without VPN has not been tested.
5. Dependency-audit status needs follow-up: PR #19 previously recorded 7 moderate and 0 high findings, but a newer frontend CI run `44310366619` on an intermediate PR head failed `npm audit --audit-level=high` with 13 findings (7 high, 6 moderate), including high-severity `picomatch` in transitive frontend tooling paths (`vite` / `vue-tsc`). No app dependencies were changed by that PR. This requires a separate reviewed dependency-security task; no forced upgrades or `npm audit fix --force` were applied.

## Status policy
Update this file when a milestone or material project decision changes. Do not mark a task DONE based only on generated code; follow the acceptance criteria in the task card.
