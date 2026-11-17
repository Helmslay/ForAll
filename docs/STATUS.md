# Project status

**Last updated:** 2026-11-17

## Repository state
- Presentation landing page: present at `/index.html`; GIS-first redesign LP-01 is complete in PR #9. The concept map is explicitly illustrative; browser GIS functionality is not claimed as implemented.
- Landing page README: updated with documentation links.
- Browser application source: minimal Vue 3/Vite/TypeScript scaffold is present under `app/`; hosted production build and Vite dev-server HTTP smoke-check passed. No map, catalog, backend API or imagery is implemented yet.
- Frontend quality tooling: ESLint, Prettier, vue-tsc and Vitest are configured; hosted CI checks pass. One render test covers the scaffold.
- Backend source: FastAPI scaffold, request ID middleware, normalized error responses and `GET /api/v1/health` are implemented under `backend/`; health endpoint passed CI (run `44113221569`). No database or raster dependencies are included yet.
- Root structure placeholders `scripts/` and `deployment/`, `.gitignore`, and a secret-free `.env.example` were added by WEB-01.01.
- A standalone allowlisted STAC connectivity checker and offline mock tests are present under /tools; this is a diagnostic utility, not the application or a provider adapter.
- Database and storage: not provisioned.
- Russian upstream access: not verified.
- User-side access from Russian networks without VPN: not verified.

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

## Current milestone
G1 — foundation work is temporarily authorized through the first local development build by ADR-010. G0 remains open and blocks real provider/raster implementation.

## Next task
WEB-01.05 — FastAPI scaffold — DONE (PR #12; merge commit `b2a8898c006380ad89df8e6c84a84bad3a0aed04`). WEB-01.06 — error contract/request ID — DONE (PR #13; CI `44112056437` SUCCESS; merge commit `f950dd69d69142368203be8637adf990f300a072`). WEB-01.07 — health endpoint — DONE (PR #14; CI `44113221569` SUCCESS; merge commit `4894f13558ae09db0fc0f0cedb8ce710c218110c`). Next: WEB-01.08 — Vite proxy (READY). G1 remains authorized through the first local frontend/backend dev-build; after that build, pause for the user's Russian-network checks before provider/data integration.

## Important blockers
1. No provider has been approved as primary.
2. Real Sentinel-2 asset access from a Russian backend has not been proven.
3. Permission to cache and redistribute each candidate source's data must be reviewed.
4. The user-facing path from Russian home/mobile networks without VPN has not been tested.
5. `npm ci` currently reports 7 moderate-severity dependency advisories; the affected dependency paths have not yet been triaged. No forced audit fix was applied.

## Status policy
Update this file when a milestone or material project decision changes. Do not mark a task DONE based only on generated code; follow the acceptance criteria in the task card.
