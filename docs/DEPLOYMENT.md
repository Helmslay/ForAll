# Deployment and operations

## 1. Target
Production in Russian data center. Minimum:
- reverse proxy such as Nginx;
- frontend static build;
- FastAPI backend;
- PostgreSQL + PostGIS;
- raster worker;
- Russian object/file storage;
- backups;
- logging and monitoring.

Early MVP may run frontend and backend on one server if resources allow. Storage remains a separate logical module. CDN is optional and only enabled after tests from Russian networks. No Kubernetes at start.

## 2. Domains and network
- One primary application domain.
- Prefer same-origin API under /api.
- HTTPS mandatory.
- No external CDN/fonts/analytics/JS SDK required for core UI.
- DNS/TLS provider must be checked from Russia.
- No mandatory foreign reverse proxy/tunnel.
- GitHub is source control, not runtime dependency.

## 3. Containers
Docker Compose first. Services: web, api, worker, db; redis only when queue/cache warrants it; object storage may be external managed service in РФ.

Each container: pinned versions, non-root where possible, healthcheck, CPU/RAM limits, persistent volumes, secrets outside image.

## 4. Configuration
Environment config for database, storage backend, provider enable flags/credentials, timeouts, cache TTL/limits, max bbox/export size, CORS, log level. Commit only .env.example. Validate required config on startup.

## 5. Migrations and storage
- PostgreSQL schema via migrations.
- Backups separate from runtime.
- Object storage retention policy.
- Large assets record checksum, size, creation date, source attribution and rights status.
- Test restore, not just backup creation.

## 6. Release
1. Build release candidate.
2. Run tests.
3. Verify backup.
4. Deploy staging.
5. Smoke test.
6. Deploy production.
7. Check health/logs.
8. Preserve rollback instructions and compatible migration plan.

## 7. Observability
Structured JSON logs with request_id, job_id, provider_id, duration, status, cache hit/miss, storage/raster errors. Never log API keys, access tokens, signed URLs, passwords or uploaded file contents.

## 8. Security checklist
HTTPS, restricted CORS, rate limits, upload validation, ZIP bomb/path traversal protection, SSRF controls, AOI/export caps, download access checks, backups, dependency scanning, data retention notice.

## 9. GitHub Pages
Use only for the landing page. Do not host backend, API secrets, raster data, user uploads or database there.
