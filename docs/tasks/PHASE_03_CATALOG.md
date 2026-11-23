# Phase 03 — STAC и поиск

Контракты в API_CONTRACTS.md. G0/provider decision отложены по прямому решению пользователя до проверки через готовое приложение; это не разрешает обходить allowlist, лицензии или заявлять доступность источника. Статусы ведутся по каждой задаче.

## WEB-03.01 — Pydantic DTO — DONE

**Результат:** добавлены `Scene`, `SearchRequest`, `SearchResponse`, `ProviderStatus` и вложенная `DateTimeRange`. Максимальный `SearchRequest.limit` зафиксирован как 100 сцен (диапазон 1–100 включительно). Bbox проверяется по EPSG:4326 и порядку west/south/east/north; даты должны быть timezone-aware UTC и упорядочены; облачность ограничена 0–100. Каналы ограничены B02/B03/B04/B08. Неизвестные поля отклоняются (`extra=forbid`), signed URL не входит в DTO. Необязательные `platform`, `cloud_cover`, `bbox`, `geometry`, `resolution`, `crs`, `nodata`, `scale`, `offset` остаются `None`, если источник их не предоставил.

**Изменённые файлы:** `backend/app/schemas/__init__.py`, `backend/app/schemas/catalog.py`, `backend/tests/test_catalog_schemas.py`, `docs/API_CONTRACTS.md`, `docs/tasks/PHASE_03_CATALOG.md`.

**Тесты:** 13 unit-test функций с параметризацией; backend CI run `44576619525` — SUCCESS (30 tests passed, Uvicorn smoke-check passed); frontend build CI run `44576619705` — SUCCESS (audit, lint, format, typecheck, unit tests, production build, proxy smoke и Compose smoke).

**Критерии приёмки:** DTO соответствуют зафиксированным полям контракта; значения bbox/date/cloud/limit проверяются; максимальный limit равен 100; optional source metadata не подменяется выдуманными значениями.

**Ограничения:** provider, STAC HTTP client, normalizer и search endpoint не реализуются в этой задаче. Значения необязательных raster metadata не вычисляются и не подменяются: DTO принимает их только из фактических данных источника. Реальный STAC Search и доступность без VPN не проверялись.

## WEB-03.02 — CatalogProvider Protocol — DONE

**Цель:** определить transport-independent интерфейс `capabilities`, `search`, `get_item` и общие доменные ошибки. Использовать существующие `SearchRequest`, `SearchResponse` и `Scene`; не включать HTTP library-specific детали.

**Результат:** добавлен async `CatalogProvider` Protocol с методами `capabilities`, `search(SearchRequest)`, `get_item(scene_key)`; типы возвращаемых значений используют существующие DTO `CatalogCapabilities`, `SearchResponse` и `Scene`. `CatalogCapabilities` — неизменяемая структура с provider ID, явно заявленными коллекциями и поддерживаемыми каналами. Добавлены общие доменные ошибки `CatalogProviderError`, `CatalogUnavailableError`, `CatalogItemNotFoundError`, `CatalogQueryNotSupportedError`, `CatalogRateLimitedError`, `CatalogConfigurationError` со стабильными безопасными кодами/сообщениями. В модуле нет зависимости от HTTP-клиента или FastAPI.

**Изменённые файлы:** `backend/app/catalog_provider.py`, `backend/tests/test_catalog_provider.py`, `docs/tasks/PHASE_03_CATALOG.md`, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`.

**Тесты:** 5 тестовых функций, включая параметризованную проверку шести доменных ошибок; backend CI run `44589067499` — SUCCESS (40 passed, Uvicorn smoke-check passed); frontend build CI run `44589067504` — SUCCESS (audit, lint, format, typecheck, frontend tests, production build, proxy и Compose smoke).

**Критерии приёмки:** fake provider без сетевого клиента соответствует Protocol; методы используют общие DTO; capability metadata неизменяема; ошибки имеют безопасные коды/сообщения и не содержат HTTP-specific полей. Все проверки прошли.

**PR:** #54 merged; merge commit `ccd9f52d449b5322fadc8ff4b582d076ce01cbe5`.

**Ограничения:** реальные provider capabilities не объявлялись и не проверялись; STAC HTTP client, provider adapter, search endpoint, orchestration и pagination не реализованы. G0 остаётся открытым.

## WEB-03.03 — STAC fixtures — DONE

**Зависимости:** WEB-03.01 DONE, WEB-03.02 DONE.

**Результат:** добавлены пять синтетических JSON fixtures: корректный STAC Item с B02/B03/B04/B08; Item без `eo:cloud_cover`; Item без B08; Polygon с незамкнутым кольцом; безопасная ошибка provider. Asset href используют локальные fixture URN `urn:sentinel-explorer:fixture:*`; сетевые URL, signed URLs, токены и секреты отсутствуют. Добавлены offline-тесты для структуры Item, отсутствующего cloud cover, отсутствующего B08, некорректного кольца, безопасной provider error и отсутствия сетевых URL/секретов.

**Изменённые файлы:** пять JSON fixtures в `backend/tests/fixtures/stac/`, `backend/tests/test_stac_fixtures.py`, эта карточка, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`.

**Проверки:** exact PR head `882af6eea218bf601ce4bbce3048c0c7ccc6529c`: backend tests run `44719855813` SUCCESS; frontend build run `44719855787` SUCCESS; mirror run `44719846069` SUCCESS. PR #56 merged as `4738710c6baf5fdfb7ce530d5b6fceac35ef0fb6`. Backend workflow включает pytest и Uvicorn health smoke-check. Локальный запуск в рабочей сессии не выполнялся.

**Критерии приёмки:** пять сценариев представлены; проверки offline-only; network URLs/credentials отсутствуют; cloud cover и B08 не подменяются выдуманными значениями. Exact-head CI passed. Геометрическая проверка ограничена замыканием Polygon ring; production geometry validator не реализуется.

**Ограничения:** fixtures синтетические и не являются ответами реального поставщика. Нет STAC HTTP client или provider adapter. G0 остаётся OPEN и отложен до пользовательской проверки через приложение.

## WEB-03.04 — STAC HTTP client — DONE

**Зависимости:** WEB-03.01, WEB-03.02 и WEB-03.03 DONE. `httpx==0.28.1` добавлен в runtime `requirements.txt`; `pytest-asyncio==0.25.3` добавлен в dev requirements.

**Результат:** добавлен `StacHttpClient`: async GET/POST JSON transport; exact-host HTTPS allowlist (только стандартный порт 443, без userinfo/fragments); redirects отключены; ограничение размера ответа; JSON/content-type/object validation; конечные retry для transport timeout/errors и HTTP 429/всех 5xx; Retry-After ограничен одной секундой; безопасные доменные ошибки и логи без URL/query/body. HTTP 5xx распознаются диапазоном 500–599, а не фиксированным списком кодов.

**Изменённые файлы:** `backend/app/stac_http.py`, `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/tests/test_stac_http.py`.

**Тесты:** offline mock tests покрывают success, host/scheme/port/userinfo allowlist, redirect, retry 5xx, non-retryable 4xx, exhausted 5xx/429, timeout, invalid content-type/JSON, oversized body, sanitized logs and unsupported method. На exact PR head `1adbe0721a9da8f3c2aa935f9a00790eaa34d741`: Backend tests run `44724633948` SUCCESS; Frontend build run `44724633952` SUCCESS; mirror run `44724626930` SUCCESS.

**Критерии приёмки:** HTTPS host allowlist, bounded retries, response-size cap, JSON validation, redirect denial and sanitized transport errors реализованы; все exact-head CI checks прошли.

**PR:** #58 merged; merge commit `ad0b06b0c7b01f06796cda9e3df62061c622217f`.

**Ограничения:** реальный provider endpoint и доступность без VPN не проверялись; HTTP client сам по себе не выбирает и не одобряет поставщика.

## WEB-03.05 — configurable STAC adapter — DONE

**Зависимости:** WEB-03.01–03.04 DONE.

**Результат:** добавлены `StacAdapterConfig` и `StacCatalogAdapter`. Endpoint задаётся явно; конфигурация принимает только HTTPS endpoint на hostname из точного allowlist, стандартный порт 443, без userinfo/query/fragment. Конфигурация явно объявляет коллекции и доступные каналы. Реализованы STAC `GET /collections`, `POST /search`, получение Item по collection/item ID и переход по provider `rel=next` ссылке. Все запросы идут через `StacHttpClient`; redirect и выход на hostname вне allowlist блокируются. Cloud-cover filter отправляется только при явном включении Query Extension; неподдерживаемый фильтр/collection/cursor отклоняется доменной ошибкой. Ответы проверяются на базовую STAC-структуру. Временные next href используются только внутри backend вызова и не записываются в логи/хранилище.

**Изменённые файлы:** `backend/app/stac_adapter.py`, `backend/tests/test_stac_adapter.py`.

**Тесты:** offline HTTPX MockTransport tests: explicit HTTPS/allowlist validation, collections, STAC Search payload, pagination next link, rejection of off-host next link, escaped Item path, configured/unsupported query extension, unsupported collection/cursor and safe provider failure/invalid payload. Exact PR head `30604a43ac2d1f0b2acb30939a840b146dc99fe1`: Backend tests run `44725439719` SUCCESS (including Uvicorn smoke-check); mirror run `44725430664` SUCCESS.

**Критерии приёмки:** explicit configured endpoint and exact-host allowlist; collection/search/item requests; backend-only next-link traversal; safe error handling; mocked tests without real provider traffic. Все критерии этой задачи проверены CI.

**PR:** #59 merged; merge commit `87a97534c4a3ce8b8fdecb76052e6f7210ca59a2`.

**Ограничения:** adapter возвращает raw STAC Items; mapping в Scene DTO выполняется в WEB-03.06. Opaque cursor/signature/expiry остаются в WEB-03.09. Provider approval, live availability, asset access, licensing and no-VPN access не проверялись. Не реализована автоматическая обработка provider-specific POST pagination links; next link fetch сейчас выполняется GET.



## WEB-03.06 — STAC Item normalizer — DONE

**Зависимости:** WEB-03.01–03.05 DONE.

**Результат:** добавлена функция `normalize_stac_item`, преобразующая STAC Feature Item в существующий `Scene` DTO без изменения API-контракта. Ключ сцены стабилен и формируется как `provider:collection:item` с URL-encoding компонентов. Collection берётся из Item; если поле отсутствует, разрешён только переданный вызывающей стороной доверенный collection context. Конфликт коллекции отклоняется. Дата `properties.datetime` обязательна, должна быть timezone-aware и приводится к UTC. Platform, cloud cover, bbox и geometry остаются необязательными; некорректные optional values опускаются, а не подменяются. Геометрия проходит структурную проверку GeoJSON типов и координат, включая замкнутость Polygon rings. Доступные каналы извлекаются только из явно названных B02/B03/B04/B08 asset key или `eo:bands[].name`, при наличии непустого href. `preview_available` определяется по assets с ролями `thumbnail` или `overview`. Asset href и исходный assets объект не входят в Scene DTO.

**Изменённые файлы:** `backend/app/stac_normalizer.py`, `backend/tests/test_stac_normalizer.py`.

**Тесты:** новые unit tests покрывают корректный Item и стабильный key, missing cloud cover/B08, malformed geometry, invalid optional fields, timezone conversion, invalid required fields, collection fallback/mismatch, preview role и отсутствие href в сериализованном DTO. Exact PR head `16787f5452f88943b595a26e6de25ff9b58556d8`: Backend tests run `44726072118` SUCCESS — **91 passed**, Uvicorn smoke-check SUCCESS; mirror run `44726047813` SUCCESS.

**Критерии приёмки:** STAC identity/date/platform/geometry/bbox/cloud/assets mapped to existing Scene; stable provider:collection:item key; optional/invalid metadata not invented; only four MVP bands exposed; asset hrefs not exposed; offline tests pass.

**PR:** #60 merged; merge commit `29fd0c5e757b6d69b9214d4086f1c7d496ba88df`.

**Ограничения:** отсутствующие/невалидные обязательные identity, collection или datetime приводят к безопасному `CatalogProviderError`; optional invalid geometry/bbox/cloud/platform are omitted. Geometry check is structural and does not replace a full topology/CRS validator. Raster resolution/CRS/nodata/scale/offset are not inferred from assets. Band detection deliberately requires explicit B02/B03/B04/B08 naming; ambiguous common_name aliases such as `nir` are not guessed. Real provider data and no-VPN access were not tested.

## WEB-03.07 — search API endpoint — DONE

**Зависимости:** WEB-03.01–03.06 DONE. FastAPI app, request-ID middleware, standard error envelope, SearchRequest/SearchResponse DTO and transport-independent CatalogProvider Protocol were already available. WEB-03.08 orchestration was kept separate; the route resolves an injected CatalogProvider.

**Результат:** реализован `POST /api/v1/catalog/search` по контракту `/api/v1`. Route принимает существующий `SearchRequest`, передаёт провайдеру только валидированный DTO и возвращает `SearchResponse`. Provider берётся из server-side `app.state.catalog_provider`; если он не настроен, API возвращает HTTP 503 `PROVIDER_UNAVAILABLE`, а не фиктивный успешный ответ. Добавлен единый mapping доменных ошибок в стандартный error envelope: unavailable/configuration → 503, rate limited → 429, unsupported query → 422, item not found → 404, generic provider error → 502. Client-supplied endpoint URL не принимается. Конкретный provider не выбран и не включён.

**Изменённые файлы:** `backend/app/catalog_routes.py`, `backend/app/main.py`, `backend/tests/test_catalog_routes.py`, `docs/API_CONTRACTS.md`, эта карточка, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`.

**Тесты:** offline route tests cover valid DTO pass-through, invalid bbox/date/cloud/limit, unknown endpoint field, provider not configured, safe mapping of provider errors and request ID. Exact PR head `7b01470a7e0153826ca5f43914e6a2f78d1e40f5`: Backend tests workflow run `45108920988` SUCCESS — **106 passed**, Uvicorn health smoke-check SUCCESS; mirror workflow run `45108914359` SUCCESS.

**Критерии приёмки:** POST route зарегистрирован; existing DTO contracts retained; validation precedes provider invocation; injected provider receives SearchRequest; missing provider and domain errors use safe error envelope; client cannot supply provider URL; no provider secrets/hrefs/tracebacks exposed. Exact-head CI passed.

**PR:** #61 merged; merge commit `b4de0685dce0d6e9c1cde1250a9dbf21c851d9b0`.

**Ограничения:** production app currently has no configured CatalogProvider, so endpoint honestly returns 503 until WEB-03.08 orchestration/server-side wiring is implemented. No real provider traffic, provider approval, cursor pagination, frontend integration or no-VPN availability was tested.

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
