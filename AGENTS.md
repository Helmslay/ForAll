# Instructions for coding agents

You are working in the Sentinel Explorer repository.

## Before coding
1. Read docs/AI_WORKFLOW.md.
2. Read docs/STATUS.md.
3. Read docs/EXECUTION_PLAN.md.
4. Read only the relevant docs/tasks/PHASE_*.md card and linked contract documents.
5. Inspect the actual repository files before assuming an application module exists.

## Work limits
- Execute exactly one task ID per work session.
- Do not start a task until its dependencies are DONE and it is READY.
- Keep changes small: normally 1–3 production files plus tests.
- Do not implement future phases early.
- Do not invent data, metadata, API responses, statistics or provider capabilities.
- Test fixtures/mocks are allowed only in tests or explicitly marked demos.
- Never put provider credentials, signed URLs or secrets in frontend code or logs.
- Never change API contracts or architecture silently.
- Do not bypass provider authentication, access controls, contractual restrictions or legal limits.

## Sentinel-specific invariants
- Browser production traffic goes through this application's backend.
- Provider integrations use adapters and normalized Scene objects.
- MVP bands are B02, B03, B04 and B08, each independently assignable to RGB.
- Correctly handle CRS, nodata, masks, scale/offset and differing raster grids.
- Russian hosting does not prove upstream availability. No no-VPN claim before the tests in docs/DATA_ACCESS_RUSSIA.md pass.
- NBR requires SWIR; do not claim it works on the four-band baseline.

## Completion
Run the checks required by the task card. Report exact commands and outcomes. Mark a task DONE only when every acceptance criterion is verified. Use the final report template in docs/AI_WORKFLOW.md.
