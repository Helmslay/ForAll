# Project status

**Last updated:** 2026-11-17

## Repository state
- Presentation landing page: present at /index.html.
- Landing page README: updated with documentation links.
- Browser application source: WEB-01.02 frontend scaffold is in progress on `feat/web-01-02-frontend-scaffold`; no dev-build has been verified yet.
- Backend source: not created yet; only the empty `backend/` foundation directory exists.
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

## Current milestone
G1 — foundation work is temporarily authorized through the first local development build by ADR-010. G0 remains open and blocks real provider/raster implementation.

## Next task
WEB-01.02 — Vue/Vite/TypeScript frontend scaffold (in progress). After the first dev-build, pause for the user's Russian-network checks before continuing to provider/data integration.

## Important blockers
1. No provider has been approved as primary.
2. Real Sentinel-2 asset access from a Russian backend has not been proven.
3. Permission to cache and redistribute each candidate source's data must be reviewed.
4. The user-facing path from Russian home/mobile networks without VPN has not been tested.

## Status policy
Update this file when a milestone or material project decision changes. Do not mark a task DONE based only on generated code; follow the acceptance criteria in the task card.
