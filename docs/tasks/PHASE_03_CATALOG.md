# Phase 03 — STAC и поиск

До реального adapter пройти WEB-00.10. Контракты в API_CONTRACTS.md. Все задачи PLANNED.

## WEB-03.01 — Pydantic DTO
Scene, SearchRequest/Response, ProviderStatus; validate bbox/date/cloud/limit; optional metadata не придумывать. Unit tests. Приёмка: DTO соответствуют контракту.

## WEB-03.02 — CatalogProvider Protocol
Interface search/get_item/capabilities и общие domain errors. Не включать HTTP library-specific детали. Приёмка: provider можно заменить.

## WEB-03.03 — STAC fixtures
Valid item, missing cloud cover, missing required band, malformed geometry, provider error. Fixtures sanitized; offline-only tests.

## WEB-03.04 — STAC HTTP client
Timeouts, finite retries for transient failures, JSON validation, safe logs, endpoint allowlist/config. Mock tests for 200/500/timeout/invalid JSON. No infinite retry.

## WEB-03.05 — primary adapter
Зависит от WEB-00.10. Implement one tested provider adapter; request, collection, pagination links, provider errors. Не хранить временный href в коде. Integration tests. Приёмка: real sanitized item normalizes.

## WEB-03.06 — STAC normalizer
Pure map id/collection/datetime/platform/geometry/bbox/cloud/assets; stable provider:collection:item key. Tests optional/invalid fields. No invented metadata.

## WEB-03.07 — search endpoint
POST /catalog/search, validation and standard errors. Tests invalid bbox/date/cloud/limit and valid input. No arbitrary URL.

## WEB-03.08 — catalog orchestrator
Call enabled adapters, normalize, deduplicate by real identity, track partial status. Provider failure doesn't erase another provider's results. All fail → clear provider error.

## WEB-03.09 — cursor pagination
Opaque cursor bound to query/provider signature, expiry and tamper protection. Tests duplicate page and mismatched query. Never expose signed next links.

## WEB-03.10 — provider status DTO
Success/partial/unavailable, safe reason and last checked. Hide secrets and raw trace.

## WEB-03.11 — typed frontend search client
Serialize request, parse errors, abort previous query, DTO types. Tests; no direct fetch in components.

## WEB-03.12 — search form/results
Connect real API; loading/empty/error/partial/pagination states. No mock thumbnails/scene fields. Acceptance: real provider records appear.

## WEB-03.13 — scene detail/footprint
Select result, highlight real geometry, fit extent, details panel, clear. Verify selection and map remain synchronized.
