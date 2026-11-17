# Phase 08 — production release

All tasks PLANNED. Read DEPLOYMENT.md, TESTING_QA.md, DATA_ACCESS_RUSSIA.md.

## WEB-08.01 — production Docker config
Multi-stage build, non-root runtime, pinned deps, persistent data, worker, healthcheck. Verify image contains no secrets/dev dependencies.

## WEB-08.02 — Nginx proxy
Same-origin static frontend/API/downloads. Body limits, timeouts, Range passthrough, request ID, safe headers. Test large partial downloads.

## WEB-08.03 — HTTPS and security headers
TLS and renewal; HSTS only after HTTPS is stable; CSP; nosniff; Referrer-Policy; no mixed content. Browser verification.

## WEB-08.04 — Russian database/storage
Deploy PostGIS and storage; verify actual data location, migrations, read/write/checksum/Range; credentials external to git.

## WEB-08.05 — logs/metrics
Structured logs with request/job/provider ID, duration, cache status and errors. Redact secrets. Test failures can be diagnosed.

## WEB-08.06 — rate and upload limits
Limit search/tile/download; file size; archive expansion; processing quotas; safe 429/413 errors. Abuse test and normal path test.

## WEB-08.07 — backup/restore
Database + object storage policy, retention, restore steps. Perform restore drill and record evidence; backup existence alone is not pass.

## WEB-08.08 — Russian staging
Deploy staging with test credentials and limited AOI; migrations; smoke tests; no production user data. Verify access from Russia.

## WEB-08.09 — Russian network acceptance
Without VPN test fixed and mobile network: app, API, real search, asset, RGB, export, checksum and cache. Record operator/region/date/version. Only then make no-VPN claim for tested scenarios.

## WEB-08.10 — MVP acceptance
Fresh browser; search; scene; four channels; RGB remapping; pan/zoom; export; independent GeoTIFF validation; upstream outage behavior; Russian network test. Every requirement PASS or explicit accepted limitation.

## WEB-08.11 — release notes/rollback
Version, feature list, known issues, source attribution, infra requirements, migration rollback, previous working version. Another operator must be able to follow it.
