# Sentinel Explorer Web — preview container stack

This stack is a bounded deployment baseline for the current frontend and FastAPI
scaffold. It is not yet the complete production environment described in
`docs/DEPLOYMENT.md`.

## What it runs

- A multi-stage build of the Vue/Vite frontend, served by unprivileged Nginx.
- The existing FastAPI application, also running as a non-root user.
- Same-origin `/api/` proxying from the frontend container to the API container.
- The web container is published only on host loopback, default
  `127.0.0.1:8080`. It does not claim or bind public ports 80 or 443.
- Both containers use read-only root filesystems, dropped Linux capabilities,
  bounded temporary filesystems, and bounded JSON-file logs.

The image tags are versioned: Node 24.22.3, Nginx 1.30.8 stable, and Python
3.12.16. Review and update them through normal dependency/image maintenance.

## Start and verify

Run from the repository root:

```sh
docker compose -p sentinel-preview -f deployment/compose.preview.yaml config --quiet
docker compose -p sentinel-preview -f deployment/compose.preview.yaml up -d --build --wait
curl --fail http://127.0.0.1:8080/healthz
curl --fail http://127.0.0.1:8080/api/v1/health
```

Open the site through the existing host Nginx after a reviewed TLS virtual-host
configuration has been installed. A starting template is
`deployment/nginx/vps-proxy.conf.example`. Replace the example hostname and
certificate paths, validate with `nginx -t`, and only then reload the host
Nginx. Do not overwrite an existing default virtual host or certificate.

Stop the preview stack:

```sh
docker compose -p sentinel-preview -f deployment/compose.preview.yaml down
```

## Important limitations

The application currently starts with no configured catalog adapters. Therefore
`POST /api/v1/catalog/search` deliberately returns HTTP 503 with
`PROVIDER_UNAVAILABLE`. This is expected fail-closed behaviour, not a successful
Sentinel search. No provider is enabled by this stack.

This preview stack does not provision PostGIS, raster workers, object storage,
backups, metrics, or a TLS certificate. It does not configure the host Nginx,
firewall, DNS, SSH, or the existing website document root. Those Phase 08
production acceptance tasks remain open.

Never expose the API container directly to the public network. Do not bind the
preview web port to `0.0.0.0`; the host reverse proxy is the public entry point.
