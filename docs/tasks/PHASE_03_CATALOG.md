# Phase 03 — STAC и поиск

До реального adapter пройти WEB-00.10. Контракты в API_CONTRACTS.md. Статусы ведутся по каждой задаче.

## WEB-03.01 — Pydantic DTO — DONE

**Результат:** добавлены `Scene`, `SearchRequest`, `SearchResponse`, `ProviderStatus` и вложенная `DateTimeRange`. Максимальный `SearchRequest.limit` зафиксирован как 100 сцен (диапазон 1–100 включительно). Bbox проверяется по EPSG:4326 и порядку west/south/east/north; даты должны быть timezone-aware UTC и упорядочены; облачность ограничена 0–100. Каналы ограничены B02/B03/B04/B08. Неизвестные поля отклоняются (`extra=forbid`), signed URL не входит в DTO. Optional metadata остаётся `None`, если источник её не предоставил.

**Изменённые файлы:** `backend/app/schemas/__init__.py`, `backend/app/schemas/catalog.py`, `backend/tests/test_catalog_schemas.py`, `docs/API_CONTRACTS.md`, `docs/tasks/PHASE_03_CATALOG.md`.

**Тесты:** backend CI run `44576619525` — SUCCESS (30 tests + Uvicorn smoke); frontend CI run `44576619705` — SUCCESS.

**PR:** #53 merged; merge commit `8ca882cc7cde1769d0293f92a5d9f39f3b86b79e`.

**Ограничения:** provider, STAC HTTP client, normalizer и search endpoint не реализованы; реальный STAC Search и доступность без VPN не проверялись.

## WEB-03.02 — CatalogProvider Protocol — DONE

**Результат:** добавлен async `CatalogProvider` Protocol с методами `capabilities`, `search(SearchRequest)`, `get_item(scene_key)`; типы используют `CatalogCapabilities`, `SearchResponse` и `Scene`. `CatalogCapabilities` — неизменяемая структура с provider ID, явно заявленными коллекциями и поддерживаемыми каналами. Добавлены общие доменные ошибки с безопасными кодами/сообщениями. В модуле нет зависимости от HTTP-клиента или FastAPI.

**Изменённые файлы:** `backend/app/catalog_provider.py`, `backend/tests/test_catalog_provider.py`, `docs/tasks/PHASE_03_CATALOG.md`, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`.

**Тесты:** backend CI run `44589067499` — SUCCESS (40 passed + Uvicorn smoke); frontend CI run `44589067504` — SUCCESS.

**PR:** #54 merged; merge commit `ccd9f52d449b5322fadc8ff4b582d076ce01cbe5`.

**Ограничения:** реальные provider capabilities не объявлялись и не проверялись; STAC HTTP client, provider adapter, search endpoint, orchestration и pagination не реализованы. G0 остаётся открытым.

## WEB-03.03 — STAC fixtures — IN_REVIEW

**Зависимости:** WEB-03.01 DONE, WEB-03.02 DONE.

**Результат:** добавлены пять синтетических JSON fixtures: корректный STAC Item с B02/B03/B04/B08; Item без `eo:cloud_cover`; Item без B08; Polygon с незамкнутым кольцом; безопасная ошибка provider. Все asset href — локальные fixture URN, сетевые URL и учётные данные отсутствуют. Добавлены offline-тесты, проверяющие структуру корректного Item, сохранение отсутствующего cloud cover как `None`, отсутствие подстановки недостающего канала, обнаружение некорректного кольца, безопасный доменный provider error и отсутствие URL/секретов в fixtures.

**Изменённые файлы:**
- `backend/tests/fixtures/stac/valid_item.json`
- `backend/tests/fixtures/stac/missing_cloud_cover.json`
- `backend/tests/fixtures/stac/missing_mvp_band.json`
- `backend/tests/fixtures/stac/malformed_geometry.json`
- `backend/tests/fixtures/stac/provider_error.json`
- `backend/tests/test_stac_fixtures.py`
- `docs/tasks/PHASE_03_CATALOG.md`
- `docs/EXECUTION_PLAN.md`
- `docs/STATUS.md`

**Тесты:** автоматический локальный запуск в этой сессии не выполнялся; ожидается backend CI для PR. До завершения CI задача не считается DONE.

**Критерии приёмки:** все пять сценариев представлены отдельными fixtures; проверки offline-only; нет сетевых запросов, signed URLs, токенов и секретов; отсутствующие cloud cover и B08 не подменяются выдуманными значениями.

**Ограничения:** fixtures синтетические и не являются ответами реального поставщика. Геометрическая проверка в этой задаче ограничена тестовой проверкой замыкания Polygon ring; production normalizer/geometry validator не реализуется. Нет STAC HTTP client или реального provider adapter. G0 остаётся открытым.

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
