# Phase 03 — STAC и поиск

До реального adapter пройти WEB-00.10. Контракты в API_CONTRACTS.md. Статусы ведутся по каждой задаче.

## WEB-03.01 — Pydantic DTO — IN_REVIEW

**Результат:** добавлены `Scene`, `SearchRequest`, `SearchResponse`, `ProviderStatus` и вложенная `DateTimeRange`. Максимальный `SearchRequest.limit` зафиксирован как 100 сцен (диапазон 1–100 включительно). Bbox проверяется по EPSG:4326 и порядку west/south/east/north; даты должны быть timezone-aware UTC и упорядочены; облачность ограничена 0–100. Каналы ограничены B02/B03/B04/B08. Неизвестные поля отклоняются (`extra=forbid`), signed URL не входит в DTO. Необязательные `platform`, `cloud_cover`, `bbox`, `geometry`, `resolution`, `crs`, `nodata`, `scale`, `offset` остаются `None`, если источник их не предоставил.

**Изменённые файлы:** `backend/app/schemas/__init__.py`, `backend/app/schemas/catalog.py`, `backend/tests/test_catalog_schemas.py`, `docs/API_CONTRACTS.md`, `docs/tasks/PHASE_03_CATALOG.md`.

**Тесты:** добавлены 12 unit-test функций с параметризацией для валидного/невалидного bbox, дат, облачности, limit, опциональных полей, списка каналов, ProviderStatus и вложенного SearchResponse. Результат CI будет зафиксирован после проверки PR.

**Критерии приёмки:** DTO соответствуют зафиксированным полям контракта; значения bbox/date/cloud/limit проверяются; максимальный limit равен 100; optional source metadata не подменяется выдуманными значениями.

**Ограничения:** provider, STAC HTTP client, normalizer и search endpoint не реализуются в этой задаче. Значения необязательных raster metadata не вычисляются и не подменяются: DTO принимает их только из фактических данных источника.

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
