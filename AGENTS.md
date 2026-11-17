# Instructions for coding agents

**Read first:** [docs/START_HERE.md](docs/START_HERE.md). It is the compact project guide and new-session entrypoint.

Then read only:
1. docs/STATUS.md
2. the relevant task entry in docs/EXECUTION_PLAN.md
3. its single docs/tasks/PHASE_*.md card
4. only linked sections of supporting docs
5. actual code and tests for the affected module

Do not load all documentation into context. Execute exactly one READY task per session; dependencies must be DONE. Keep changes small and do not implement future phases.

## Non-negotiable rules
- Inspect the actual repository before assuming application code exists.
- Do not invent data, metadata, API responses, statistics or provider capabilities.
- Production provider traffic goes through backend adapters; use normalized Scene objects.
- MVP bands are B02, B03, B04 and B08, each independently assignable to RGB.
- Handle CRS, nodata, masks, scale/offset and differing raster grids correctly.
- Never put credentials, tokens or signed URLs in frontend code or logs.
- Respect provider authentication, licensing, caching and redistribution terms.
- Russian hosting does not prove upstream or end-user access. Do not claim no-VPN availability until the checks in docs/DATA_ACCESS_RUSSIA.md pass.
- NBR requires SWIR; do not claim it works on the four-band baseline.
- Never change architecture or API contracts silently.

## Completion
Run the task's required checks. Mark DONE only when every acceptance criterion is verified. Update docs/EXECUTION_PLAN.md, docs/STATUS.md when material status changes, and the task card. Report exact commands/results, limitations and next task as specified in docs/START_HERE.md.
