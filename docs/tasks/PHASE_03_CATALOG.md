# Phase 03 — STAC и поиск

До реального adapter пройти WEB-00.10. Контракты в API_CONTRACTS.md. Статусы ведутся по каждой задаче.

## WEB-03.01 — Pydantic DTO — DONE

**Результат:** добавлены `Scene`, `SearchRequest`, `SearchResponse`, `ProviderStatus` и вложенная `DateTimeRange`. Максимальный `SearchRequest.limit` зафиксирован как 100 сцен (диапазон 1–100 включительно). Bbox проверяется по EPSG:4326 и порядку west/south/east/north; даты должны быть timezone-aware UTC и упорядочены; облачность ограничена 0–100. Каналы ограничены B02/B03/B04/B08. Неизвестные поля отклоняются (`extra=forbid`), signed URL не входит в DTO. Необязательные `platform`, `cloud_cover`, `bbox`, `geometry`, `resolution`, `crs`, `nodata`, `scale`, `offset` остаются `None`, если источник их не предоставил.

**Изменённые файлы:** `backend/app/schemas/__init__.py`, `backend/app/schemas/catalog.py`, `backend/tests/test_catalog_schemas.py`, `docs/API_CONTRACTS.md`, `docs/tasks/PHASE_03_CATALOG.md`.

**Тесты:** 13 unit-test функций с параметризацией; backend CI run `44576619525` — SUCCESS (30 tests passed, Uvicorn smoke-check passed); frontend build CI run `44576619705` — SUCCESS (audit, lint, format, typecheck, unit tests, production build, proxy smoke и Compose smoke).

**Критерии приёмки:** DTO соответствуют зафиксированным полям контракта; значения bbox/date/cloud/limit проверяются; максимальный limit равен 100; optional source metadata не подменяется выдуманными значениями.

**Ограничения:** provider, STAC HTTP client, normalizer и search endpoint не реализуются в этой задаче. Значения необязательных raster metadata не вычисляются и не подменяются: DTO принимает их только из фактических данных источника. Реальный STAC Search и доступность без VPN не проверялись.

## WEB-03.02 — CatalogProvider Protocol — IN_PROGRESS

**Цель:** определить transport-independent интерфейс `capabilities`, `search`, `get_item` и общие доменные ошибки. Использовать существующие `SearchRequest`, `SearchResponse` и `Scene`; не включать HTTP library-specific детали.

**Планируемые файлы:** `backend/app/catalog_provider.py`, `backend/tests/test_catalog_provider.py` и эта карточка/индексные документы.

**Критерии приёмки:** тестовая реализация без сетевого клиента структурно соответствует Protocol; методы используют общие DTO; capability metadata неизменяемы и описывают только явно объявленные возможности; ошибки имеют стабильные безопасные коды/сообщения и не зависят от HTTP framework; тесты проходят.

**Не входит:** STAC HTTP client, provider adapter, реальные capability values, search endpoint, orchestration и pagination.

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
