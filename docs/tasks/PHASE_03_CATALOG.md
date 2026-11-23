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

## WEB-03.08 — catalog orchestrator — DONE

**Зависимости:** WEB-03.01–03.07 DONE. Использованы существующие `CatalogProvider` protocol, catalog DTO, STAC HTTP transport, configurable `StacCatalogAdapter` и STAC Item normalizer.

**Результат:** добавлен `CatalogOrchestrator`, реализующий `CatalogProvider` и принимающий явно настроенный серверный список адаптеров. Фабрика FastAPI принимает этот список через `create_app(..., catalog_adapters=...)`; по умолчанию список пуст, ни один upstream provider не выбран или активирован.

Поиск выполняется параллельно. Оркестратор фильтрует адаптеры по `providers`, передаёт каждому только поддерживаемые запрошенные collections, проверяет collection identity в ответах, нормализует Items в `Scene`, удаляет дубликаты по устойчивому `Scene.key` и ограничивает общий результат параметром `limit`. Порядок результатов и provider statuses детерминирован порядком адаптеров в конфигурации.

Сбой одного адаптера не удаляет результаты остальных: формируется `partial=true` и безопасный `ProviderStatus`. Если все адаптеры не справились, возвращается безопасная доменная ошибка; однородные ошибки unsupported query и rate limit сохраняют соответствующий тип. Поставщик с upstream next link помечается `partial/more_results_available`; сам next URL не возвращается. Реализован поиск отдельной сцены по существующему ключу provider:collection:item с проверкой канонической кодировки и идентичности.

**Изменённые файлы:**
- `backend/app/catalog_orchestrator.py`
- `backend/app/main.py`
- `backend/tests/test_catalog_orchestrator.py`
- `docs/API_CONTRACTS.md`
- эта карточка, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`

**Тесты:** offline tests cover app-factory wiring, CatalogProvider protocol, parallel fan-out, provider filtering, collection intersection, normalization, unexpected collection rejection, stable-key deduplication, aggregate limit, partial failures, all-failed/no-provider cases, rate-limit/query errors, safe handling of next links and scene-key routing including encoded identity components. Exact PR head `6de5f4d4a39e05c1ab3f442d1d52ba4624fb27e7`: Backend workflow run `45109923307` SUCCESS — **123 passed**, Uvicorn health smoke-check SUCCESS; GitLab mirror run `45109917509` SUCCESS.

**Критерии приёмки:** orchestrator satisfies `CatalogProvider`; no arbitrary URL/client-controlled adapter configuration; adapter failures are isolated; raw upstream links/exceptions are not exposed; deduplication uses normalized stable identity; result count does not exceed request limit; offline CI passed.

**PR:** #62 merged; merge commit `3090165dff88f25aa95dd42699a7fa6d752fcfa3`.

**Ограничения:** production configuration still enables no provider by default. Real provider traffic, credentials, licensing, Russian-network access and no-VPN availability were not tested. Cursor signing and fetching subsequent STAC pages remain WEB-03.09; until then a next link is represented only as a partial provider status.

## WEB-03.09 — encrypted aggregate cursor pagination — DONE

**Зависимости:** WEB-03.01–03.08 DONE. Existing `SearchRequest.cursor`, `SearchResponse.next_cursor`, STAC `next_href` and orchestrator provider fan-out are available. Existing HTTPS host allowlist remains mandatory for every continuation fetch.

**Цель:** реализовать безопасную pagination поверх всех выбранных STAC adapters, сохраняя текущий API DTO и не раскрывая upstream continuation state.

**Контракт и ограничения:**
- Cursor — opaque AES-256-GCM ciphertext, nonce + authenticated ciphertext, URL-safe base64. Canonical query hash binds bbox, datetime, cloud filter, collections, providers and limit; cursor itself is excluded.
- Server key: `SENTINEL_CURSOR_ENCRYPTION_KEY`, base64 encoding of exactly 32 random bytes. No default, generated-at-startup or frontend key. Missing/invalid key: no cursor issuance; continuation request fails closed. Key rotation invalidates outstanding cursors.
- TTL 15 minutes; expiry checked on every continuation. Payload versioned. Authentication, decoding, schema and query-binding failures map to `INVALID_CATALOG_CURSOR` (HTTP 422) without exposing reason details.
- Encrypted state contains each selected provider's internal next href, normalized scene buffer not yet emitted, and stable scene keys already emitted. No raw href/token in API response or logs. Every href is revalidated by the adapter HTTP allowlist on fetch.
- Preserve provider order, partial failures and global `limit`; never silently drop overflow scenes when merging provider pages. Deduplicate by `Scene.key` across page boundaries.
- Maximum encoded cursor size 64 KiB. If state exceeds cap, do not truncate state or issue a cursor; return safe partial provider status `pagination_state_limit`.
- Cursor is replayable until expiry (stateless token); no one-time-use guarantee.

**Фактически изменённые файлы:** `backend/app/catalog_cursor.py`, `backend/app/catalog_orchestrator.py`, `backend/app/config.py`, `backend/app/main.py`, `backend/requirements.txt`, `backend/tests/test_catalog_cursor.py`, `backend/tests/test_catalog_orchestrator.py`, `backend/tests/test_catalog_routes.py`, `backend/tests/test_app.py`, `.env.example`, `docs/API_CONTRACTS.md`, `docs/DECISIONS.md`, эта карточка, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`. Existing `StacCatalogAdapter.get_next_page` and its HTTPS allowlist validation are reused without changing its API.

**Тесты:** codec round-trip; tampered ciphertext; wrong key/rotation; expiry; malformed/oversized token; mismatched query/provider/limit; multiple providers advancing independently; buffered overflow across pages; cross-page duplicate; one provider failure while another continues; off-host next href rejected; no href/key in response/logs; missing key fails closed.

**Progress:** AES-256-GCM codec is integrated into FastAPI through `Settings.cursor_encryption_key` (`SecretStr`, `repr=False`) and the server-only `SENTINEL_CURSOR_ENCRYPTION_KEY`; invalid/missing configuration disables issuance and continuation fails closed with HTTP 422 `INVALID_CATALOG_CURSOR`. The orchestrator binds cursors to a canonical request hash, preserves per-provider next hrefs and normalized buffers, fills the aggregate page from provider continuations, emits at most the global limit, deduplicates stable scene keys across pages, isolates continuation failures and reports state-size/key-unavailable partial reasons. Every next href is passed back through the adapter's existing allowlist-checked `get_next_page` transport. `.env.example` documents key generation without containing a secret. PR #63 is ready for merge at exact head `e2c6821e8a294374093de5cc9415974d246043b8`. Backend tests run `45112794228`: **145 passed** + Uvicorn smoke SUCCESS; Frontend build run `45112794178`: SUCCESS (audit policy, lint, formatting, typecheck, unit tests, production build, Vite proxy, Compose config/port checks and Compose frontend/API smoke); GitLab mirror run `45112788369`: SUCCESS.

**Acceptance:** AES-256-GCM codec, expiry/tamper/key/query binding, encrypted aggregate continuation, per-provider buffering, global limit, cross-page deduplication, continuation partial failure, allowlist revalidation, 64 KiB fail-closed behavior, secret settings and safe HTTP 422 mapping are covered by offline tests. Exact-head backend, frontend and mirror workflows all SUCCESS. No live provider or Russian availability claim was made. G0 remains deferred.

**Ограничения:** cursor is replayable until its 15-minute expiry; one-time-use protection is not implemented. No provider is enabled by default. Real provider traffic, licensing, raster assets and Russian-network/no-VPN access were not tested. The server must be configured with a stable base64-encoded 32-byte `SENTINEL_CURSOR_ENCRYPTION_KEY` to issue continuation cursors.\n\n**PR:** #63 merged; merge commit `8eff9ea88be22ccd57afb68de8acc377a658709e`.\n\n**Не входит:** provider selection, live source validation, one-time cursor replay prevention, frontend pagination UI, raster access.

## WEB-03.10 — provider partial status — DONE

**Зависимости:** WEB-03.01–03.09 DONE. `ProviderStatus` DTO, `SearchResponse` and `CatalogOrchestrator` are already part of the backend catalog implementation.

**Результат:** задача закрыта без дублирования существующей реализации. `ProviderStatus` supports exactly `success`, `partial` and `unavailable`, optional UTC `last_checked` and safe `reason`. DTO rejects unknown fields (including traceback-like fields). The orchestrator populates timestamps and safe reason codes for unsupported collections, provider failures, remaining provider pages, unavailable cursor encryption and pagination-state limits. A provider failure remains isolated from successful providers; `SearchResponse.partial` reflects non-success provider statuses. Raw upstream URLs and exception text are not copied into the response.

**Фактически изменённые файлы в рамках исходной реализации:** `backend/app/schemas/catalog.py`, `backend/app/catalog_orchestrator.py`, `backend/tests/test_catalog_schemas.py`, `backend/tests/test_catalog_orchestrator.py`. Эти файлы были реализованы и проверены в предыдущих задачах WEB-03.01/03.08/03.09; в рамках закрытия WEB-03.10 production-код не менялся.

**Проверки и evidence:**
- `test_provider_status_accepts_known_states_and_utc_timestamp` — проверяет допустимый статус, UTC timestamp и reason.
- `test_provider_status_rejects_unknown_state_and_extra_fields` — проверяет отклонение неизвестного статуса и дополнительного поля traceback.
- `test_one_provider_failure_does_not_erase_successful_results` — проверяет независимость провайдеров, safe reason, unavailable/success и partial.
- `test_unsupported_collection_is_reported_without_blocking_other_provider` и `test_provider_with_next_page_is_explicitly_marked_partial` — проверяют безопасные причины partial/unavailable.
- Exact PR #63 head `97cb8d199d1508895bc343aca3c8096614181985`: Backend tests run `45113001119` — **145 passed**, Uvicorn smoke SUCCESS. Этот запуск включает указанные тесты; отдельный новый backend workflow для документационного закрытия не требуется.

**Критерии приёмки:** три состояния DTO; UTC `last_checked`; optional safe `reason`; запрет лишних полей; корректные статусы и partial при частичном сбое; отсутствие upstream URL/traceback в ответе — подтверждены существующими тестами и exact-head CI.

**Ограничение / не входит в задачу:** `GET /api/v1/health/providers` из раздела Health в `docs/API_CONTRACTS.md` в приложении отсутствует. WEB-03.10 сформулирована как provider status DTO и статусы в ответе Search, поэтому отдельный health endpoint не добавлялся. Контракт называет его внутренним/защищённым, но проект пока не задаёт механизм аутентификации/авторизации; endpoint нельзя безопасно реализовать до отдельного согласования этого механизма и отдельной задачи. Никаких health details публично не раскрывается.

**Итог:** DONE по scope WEB-03.10; production diff отсутствует. Следующая задача — WEB-03.11 (typed frontend search client).

## WEB-03.11 — typed frontend search client — DONE

**Dependencies:** WEB-03.01–03.10 DONE. Backend contract exists at `POST /api/v1/catalog/search`; frontend request builder and relative API base path already exist.

**Scope/result:** Implemented typed DTOs and a dedicated `searchCatalog` client. It POSTs the exact SearchRequest JSON to the relative endpoint, preserves opaque cursors, validates SearchResponse at runtime, parses the standard safe error envelope into `CatalogApiError`, sanitizes malformed/network errors, and aborts the previous in-flight search. AbortError remains cancellation. No Vue component performs direct catalog fetch; no UI wiring, mock scene data, or provider activation was added.

**Changed files:**
- `app/src/api/catalog.ts` — typed client and runtime validation.
- `app/src/types/catalog.ts` — SearchResponse, Scene, ProviderStatus, ApiErrorEnvelope and nullable filter types.
- `app/src/api/catalog.spec.ts` — six offline tests.
- `docs/tasks/PHASE_03_CATALOG.md`, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md` — task evidence and tracking.

**Acceptance:** Request serialization, DTO shape validation, safe HTTP error parsing, malformed success/error handling, cancellation, and absence of direct catalog fetch in Vue components are covered by tests. No live provider traffic is part of this task.

**GitHub Actions:** Exact PR head `3b3c7a5e657777f4bbcf3e4f125850a4c9d7e9fd`. Frontend Build #235 / run `45165905441` — SUCCESS; all 19 steps passed, including audit policy, audit, lint, format, typecheck, unit tests, production build, Vite proxy smoke, Compose config/localhost checks, Compose startup and frontend/API smoke. Mirror workflow run `45165898039` — SUCCESS. Both check-runs for the exact SHA completed successfully.

**Review/merge:** PR #65 had no review threads or requested changes and was mergeable. Merged using squash with expected-head guard. Merge commit: `d7a5d99c18b0b21030a9e84c7e5905c95ea4e248`.

**Limitations:** No provider is enabled or selected. Live provider traffic, asset access, licensing and user-side no-VPN availability were not tested; G0 remains deferred by owner decision. Buildkite is not part of Sentinel Explorer Web CI.

**Status:** DONE.

## WEB-03.12A — search UI states and cursor pagination

**Статус:** READY; owner explicitly authorized splitting WEB-03.12 on 2026-11-23.

**Зависимости:** WEB-03.11 DONE; typed `searchCatalog`, SearchRequest/SearchResponse DTO and backend route exist.

**Scope:** Connect SearchPanel to `searchCatalog`; implement loading, empty, safe error/retry, partial provider status and cursor pagination. Render only fields present in returned Scene DTO. Merge pages by stable `Scene.key` and prevent stale responses from replacing reset/newer state.

**Test strategy:** Use synthetic typed SearchResponse objects only inside frontend unit tests. They are not application data or claims of real source availability. Mock the API client; do not activate or select a provider.

**Acceptance:** Search request uses the typed client; loading state and disabled submit are visible; empty/error/partial/provider states render; retry works; next cursor is passed unchanged; duplicate scene keys are not rendered twice; reset prevents stale responses from reappearing; no fabricated thumbnails/metadata or production mock data; frontend lint/format/typecheck/unit tests/build pass.

**Non-goals:** Real-provider E2E, provider approval/activation, asset access, scene footprint/selection, thumbnails, and G0/no-VPN claims.

## WEB-03.12B — real provider search acceptance — BLOCKED

**Dependencies:** WEB-03.12A DONE; provider approval/selection (WEB-00.10) and G0 owner-side source validation.

**Scope:** Verify that the configured, explicitly approved provider returns real Sentinel-2 records through the application. Preserve truthful provider partial/unavailable statuses.

**Blocker:** No primary provider is approved or enabled. User deferred WEB-00.10/G0 until testing the completed app. Do not choose or activate a provider without owner approval.

**Acceptance:** At least one real Sentinel-2 scene is returned and displayed from the approved provider; provider status/errors are truthful; evidence records provider/configuration and test context. Synthetic records do not count.

**Status:** BLOCKED pending provider approval and G0 validation.

## WEB-03.13 — scene detail/footprint
Select result, highlight real geometry, fit extent, details panel, clear. Verify selection and map remain synchronized.
