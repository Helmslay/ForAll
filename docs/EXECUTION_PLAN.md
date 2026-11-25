# Execution plan — для лёгких ИИ-моделей

## 1. Правило исполнения
Это главный индекс разработки. Подробные task cards расположены в docs/tasks/. Одна задача за один запрос модели. Не брать весь этап сразу.

Каждая задача должна иметь ID, dependencies, goal, scope, input context, result, tests, acceptance criteria и explicit non-goals. Если задача не помещается в маленькое изменение, сначала декомпозировать её и обновить этот индекс.

## 2. Dependency chain

    G1 Каркас frontend/backend
      ↓
    G2 Карта и интерфейс
      ↓
    G3 Каталог и поиск
      ↓
    G0 пользовательская проверка источников (отложена; не DONE)
      ↓
    G4 Растры, каналы, RGB
      ↓
    G5 Экспорт и хранение
      ↓
    G6 Векторы и лесные данные
      ↓
    G7 Offline и аналитика
      ↓
    G8 Production release

## 3. Текущий статус
WEB-00.01 и WEB-00.02 — DONE; WEB-00.03 — IN_PROGRESS. Первый локальный Windows dev-build проверен 2026-11-18. По прямому решению пользователя G0 отложен до проверки источников через готовое приложение и НЕ считается DONE. G0 не блокирует разработку каталога/API: реализуем STAC-клиент и интеграцию без заявления о доступности конкретного источника или работы без VPN. Реальные provider errors/status должны отображаться честно. STAC checker остаётся диагностической утилитой, а не приложением или provider adapter.

## 4. Сквозные UX-задачи
Карточка: tasks/UX_01_SOFT_NEUTRAL_PALETTE.md.
- UX-01 — единая мягкая нейтральная палитра для лендинга и приложения — **DONE** (PR #11; frontend и landing CI прошли).

## 5. Реестр задач

### Публичный лендинг
Карточка: `tasks/LANDING_PAGE.md`.
- LP-01 — GIS-first переработка публичного лендинга — **DONE** (PR #9; статические проверки CI прошли; ручной cross-browser visual review не выполнялся).


### Фаза 00 — источники и российская доступность
Карточки: tasks/PHASE_00_SOURCE_ACCESS.md
- WEB-00.01 — каталог сетевых зависимостей — **DONE**.
- WEB-00.02 — безопасная проверка STAC root/collections — **DONE**.
- WEB-00.03 — тестовый STAC Search для Березников (радиус 100 км, последние 30 суток UTC, Sentinel-2 L2A; три allowlisted каталога) — **IN_PROGRESS**. PR #24 merged (`2159f17756883c2f51222e89012c5d285081d749`); exact-head CI run `44310541026` SUCCESS, 23 offline tests PASS и py_compile PASS. Остался обязательный реальный Search с Windows-компьютера пользователя в России без VPN/proxy. Карточка: `tasks/PHASE_00_SOURCE_ACCESS.md`.
- WEB-00.04 — безопасный snapshot test item.
- WEB-00.05 — проверка четырёх каналов и asset metadata.
- WEB-00.06 — HTTP Range и COG read.
- WEB-00.07 — preview реальной сцены.
- WEB-00.08 — тест российского storage.
- WEB-00.09 — runbook проверки из российских сетей.
- WEB-00.10 — provider decision.

Gate G0: законный source проходит catalog + real raster read с российского backend; пользовательский путь отдельно проверяется. До этого imagery implementation BLOCKED.

### Фаза 01 — foundation
Карточки: tasks/PHASE_01_FOUNDATION.md
- WEB-01.01 — структура и ignore rules — **DONE** (выполнена досрочно как независимая подготовительная задача; G0 остаётся открытым).
- WEB-01.02 — Vue/Vite/TS frontend scaffold — **DONE** (hosted `npm ci`, production build и dev-server smoke-check прошли).
- WEB-01.03 — frontend lint/format/typecheck/test — **DONE** (ESLint, Prettier, vue-tsc, Vitest; hosted CI passed).
- WEB-01.04 — базовая оболочка — **DONE** (PR #10; frontend CI run `44102025691` SUCCESS).
- WEB-01.05 — FastAPI scaffold — **DONE** (PR #12; backend tests and Uvicorn smoke-check passed in GitHub Actions run `44106506251`).
- WEB-01.06 — error contract и request ID — **DONE** (PR #13 merged; backend CI run `44112056437` SUCCESS; merge commit `f950dd69d69142368203be8637adf990f300a072`).
- WEB-01.07 — health endpoint — **DONE** (PR #14; backend CI run `44113221569` SUCCESS; merge commit `4894f13558ae09db0fc0f0cedb8ce710c218110c`).
- WEB-01.08 — frontend proxy — **DONE** (PR #15; frontend CI run `44115192957` SUCCESS; merge commit `680c3845a0bc21bce0bb29543073c6262594409f`).
- WEB-01.09 — Docker Compose dev — **DONE** (PR #16; CI run `44118409536` SUCCESS; merge commit `3914c94ba3f8e267307b0ad092283bcd8af76dac`).
- WEB-01.10 — local setup guide and dev-port hardening — **DONE** (PR #17 merged; exact-head frontend CI run `44126893666` SUCCESS; merge commit `9936f6af3942ff929867478bbeb237b7c5fce29b`; WEB-01.09 DONE).
- WEB-01.11 — frontend dependency audit and severity gate — **DONE** (PR #19; initial audit CI run `44132980902` SUCCESS; final exact-head CI run `44133991243` SUCCESS; 7 moderate findings classified as development-tool dependencies; no high/critical findings; no forced upgrades).

Gate G1: новый разработчик запускает проект по инструкции, health и проверки проходят.

### Фаза 02 — карта и UI
Карточки: tasks/PHASE_02_MAP_UI.md
- WEB-02.01 — CSS design tokens — **DONE** (PR #28 merged; exact-head frontend CI run `44329428142` SUCCESS; merge commit `d7a13244e6d06615995f48561523149bb21f9c79`).
- WEB-02.02 — desktop app shell — **DONE** (PR #29 merged; exact-head frontend CI run `44331108330` SUCCESS; merge commit `3dc70e8df8e271ec2bacf60b70341a53b01eb9a7`).
- WEB-02.03 — responsive panels — **DONE** (PR #30 merged; exact-head frontend CI run `44332026191` SUCCESS; merge commit `39161d5c1cbedea6756e10ed711c139681313c24`).
- WEB-02.04 — OpenLayers lifecycle — **DONE** (PR #32 merged; exact-head Frontend build CI run `44339512145` SUCCESS; merge commit `331b06dd9c82fa0a5ee39691a767b71a52da94fe`).
- WEB-02.05 — base map provider abstraction — **BLOCKED** (G0/source network and licensing gate remains open).
- WEB-02.06 — cursor coordinates and map resolution — **DONE** (PR #35 merged; exact-head Frontend build CI run `44358215174` SUCCESS for `3b03c7cbd18a9c5165e2d498c9aca637f28ee900`; tools offline tests run `44357847194` SUCCESS; merge commit `b3870808b0b6ada015d5f1cc158abedd86c9621c`).
- WEB-02.07 — AOI rectangle draw/clear — **DONE** (PR #36 merged; exact-head Frontend build CI run `44359722241` SUCCESS for `6223561722c18c079037da171da4f945fadc6c44`; merge commit `b485dfb429f50292702410bb43d4283cf9c3a8e9`).
- WEB-02.08 — search form shell — **DONE** (PR #52 merged; exact-head Frontend build CI run `44552193095` SUCCESS; 17/17 unit tests PASS; merge commit `f6b75e6071b3779f693abdeb1a35c62015ffeea3`; G0 не затронут).

Gate G2: пользователь создаёт AOI и видит bbox.

### Фаза 03 — каталог и поиск
Карточки: tasks/PHASE_03_CATALOG.md
- WEB-03.01 — Scene/Search DTO — **DONE** (PR #53 merged; exact-head Backend tests run `44576619525` SUCCESS, 30 tests + Uvicorn smoke; Frontend build run `44576619705` SUCCESS; merge commit `8ca882cc7cde1769d0293f92a5d9f39f3b86b79e`).
- WEB-03.02 — CatalogProvider Protocol — **DONE** (PR #54 merged; exact-head Backend tests run `44589067499` SUCCESS, 40 passed + Uvicorn smoke; Frontend build run `44589067504` SUCCESS; merge commit `ccd9f52d449b5322fadc8ff4b582d076ce01cbe5`).
- WEB-03.03 — STAC fixtures — **DONE** (PR #56 merged as `4738710c6baf5fdfb7ce530d5b6fceac35ef0fb6`; exact-head backend tests, frontend build and mirror SUCCESS).
- WEB-03.04 — STAC HTTP client — **DONE** (PR #58 merged as `ad0b06b0c7b01f06796cda9e3df62061c622217f`; exact-head backend tests run `44724633948`, frontend build run `44724633952`, mirror run `44724626930` — all SUCCESS; retries cover all HTTP 5xx).
- WEB-03.05 — configurable STAC adapter — **DONE** (PR #59 merged as `87a97534c4a3ce8b8fdecb76052e6f7210ca59a2`; exact-head backend tests run `44725439719` and mirror run `44725430664` SUCCESS).
- WEB-03.06 — STAC Item normalizer — **DONE** (PR #60 merged as `29fd0c5e757b6d69b9214d4086f1c7d496ba88df`; exact-head Backend tests run `44726072118` — 91 passed + Uvicorn smoke SUCCESS; mirror run `44726047813` SUCCESS).
- WEB-03.07 — search API endpoint — **DONE** (PR #61 merged as `b4de0685dce0d6e9c1cde1250a9dbf21c851d9b0`; exact-head backend CI run `45108920988` SUCCESS — 106 passed + Uvicorn smoke; mirror run `45108914359` SUCCESS).
- WEB-03.08 — catalog orchestrator — **DONE** (PR #62 merged as `3090165dff88f25aa95dd42699a7fa6d752fcfa3`; exact-head backend CI run `45109923307` SUCCESS — 123 passed + Uvicorn smoke; mirror run `45109917509` SUCCESS).
- WEB-03.09 — encrypted aggregate cursor pagination — **DONE** (PR #63 merged as `8eff9ea88be22ccd57afb68de8acc377a658709e`; exact-head Backend tests run `45113001119` — 145 passed + Uvicorn smoke SUCCESS; Frontend build run `45113001304` SUCCESS; GitLab mirror run `45112996458` SUCCESS).
- WEB-03.10 — provider partial status — **DONE** (реализация и offline tests уже входят в backend DTO/orchestrator; exact-head Backend CI run `45113001119`: 145 passed + Uvicorn smoke SUCCESS; отдельный health status endpoint не входит в scope и требует отдельного решения по auth).
- WEB-03.11 — frontend search API client — **DONE** (PR #65 merged as `d7a5d99c18b0b21030a9e84c7e5905c95ea4e248`; exact-head `3b3c7a5e657777f4bbcf3e4f125850a4c9d7e9fd`; GitHub Actions Frontend Build #235 / run `45165905441` and mirror run `45165898039` SUCCESS; all exact-SHA check-runs passed).
- WEB-03.12A — search UI states and cursor pagination — **DONE** (PR #66 merged as `8a669b28c7c9973bfd51ee17eed04a75320312df`; exact-head `7d6ab3ca16ad3a73d1557f5b8823cbb72a19e573`; GitHub Actions Frontend Build run `45175830402` SUCCESS — 30 tests passed; mirror run `45175821338` SUCCESS).
- WEB-03.12B — real provider search acceptance — **BLOCKED** (requires WEB-03.12A and explicit provider approval/G0; real scenes required).
- WEB-03.13 — scene details/footprint (depends on WEB-03.12B real-scene acceptance).

Gate G3: реальные сцены возвращаются и отображаются; fixtures покрывают unit tests.

### Фаза 04 — imagery/RGB
Карточки: tasks/PHASE_04_IMAGERY.md
- WEB-04.01 — RasterAsset model.
- WEB-04.02 — allowlisted asset resolver.
- WEB-04.03 — raster inspect.
- WEB-04.04 — read one band window.
- WEB-04.05 — nodata/scale/offset.
- WEB-04.06 — one-band statistics.
- WEB-04.07 — stats QA fixtures.
- WEB-04.08 — RGB composite window.
- WEB-04.09 — render parameter validation.
- WEB-04.10 — tile endpoint.
- WEB-04.11 — tile cache.
- WEB-04.12 — OpenLayers imagery layer.
- WEB-04.13 — independent RGB selectors.
- WEB-04.14 — stretch/gamma controls.
- WEB-04.15 — real-scene smoke test.

Gate G4: реальный снимок отображается; любой канал меняется корректно, геопривязка не ломается.

### Фаза 05 — downloads/storage
Карточки: tasks/PHASE_05_DOWNLOADS_DATA.md
- WEB-05.01 — StorageBackend contract.
- WEB-05.02 — local filesystem backend.
- WEB-05.03 — production storage config.
- WEB-05.04 — Export DTO.
- WEB-05.05 — jobs database migration.
- WEB-05.06 — export worker.
- WEB-05.07 — size estimate/AOI limits.
- WEB-05.08 — export one band.
- WEB-05.09 — multiband export.
- WEB-05.10 — jobs API and UI.
- WEB-05.11 — secure file delivery/Range.
- WEB-05.12 — independent GeoTIFF QA.

Gate G5: экспорт реально скачивается и открывается в ГИС.

### Фаза 06 — vectors/forest
Карточки: tasks/PHASE_06_LOCAL_VECTORS_FOREST.md
- WEB-06.01 — vector layer model.
- WEB-06.02 — GeoJSON import.
- WEB-06.03 — GeoJSON display.
- WEB-06.04 — feature attributes.
- WEB-06.05 — attribute table.
- WEB-06.06 — Shapefile ZIP import.
- WEB-06.07 — local GeoTIFF layer.
- WEB-06.08 — ForestDataProvider contract.
- WEB-06.09 — official forest service research.
- WEB-06.10 — one verified forest layer.
- WEB-06.11 — forest attributes panel.

Gate G6: local vector/raster и attributes работают; внешний лесной слой подключён только при подтверждённом разрешённом API.

### Фаза 07 — offline/analytics
Карточки: tasks/PHASE_07_OFFLINE_ANALYTICS.md
- WEB-07.01 — PWA manifest.
- WEB-07.02 — app shell cache.
- WEB-07.03 — network/server state UI.
- WEB-07.04 — offline tile package.
- WEB-07.05 — offline package import.
- WEB-07.06 — local GeoTIFF offline use.
- WEB-07.07 — spectral index contract.
- WEB-07.08 — NDVI calculation.
- WEB-07.09 — NDVI visualization.
- WEB-07.10 — two-scene selection.
- WEB-07.11 — before/after viewer.
- WEB-07.12 — forest-change test dataset.

Gate G7: offline tested without network; analytic outputs checked against fixtures.

### Фаза 08 — release
Карточки: tasks/PHASE_08_RELEASE.md
- WEB-08.01 — production Docker config.
- WEB-08.02 — Nginx reverse proxy.
- WEB-08.03 — HTTPS/security headers.
- WEB-08.04 — Russian DB/storage.
- WEB-08.05 — logging/metrics.
- WEB-08.06 — rate/upload limits.
- WEB-08.07 — backup/restore runbook.
- WEB-08.08 — staging in Russia.
- WEB-08.09 — Russian network acceptance.
- WEB-08.10 — MVP acceptance.
- WEB-08.11 — release notes/rollback.

Gate G8: release checklist and data-access report are complete.

## 6. Зависимости, которые нельзя обходить
- Выбор primary provider (WEB-00.10) и G0 отложены до пользовательской проверки готового приложения. Это не блокирует generic STAC adapter: endpoint задаётся явно, hostname проходит allowlist, интеграция проверяется mock-тестами. Не представлять провайдера как одобренного/доступного.
- Внешний raster reader зависит от WEB-00.06.
- Tile endpoint зависит от asset model, safe resolver и RGB tests.
- Export зависит от storage/job contracts.
- Offline claim зависит от теста после полного отключения сети.
- No-VPN claim зависит от WEB-08.09.

## 7. Definition of Ready
Dependencies DONE; карточка ясна; input contracts существуют; список затрагиваемых модулей определён; критерии измеримы; fixtures/test env известны.

## 8. Definition of Done
Scope выполнен; архитектура соблюдена; lint/typecheck/tests pass; критерии карточки pass; нет secrets/mock в production; docs обновлены при смене контрактов; diff просмотрен; commit SHA записан.

## 9. Размер задачи
Одна задача — одна законченная функция/компонент/adapter/test. Ориентир 1–3 production files плюс тесты. Лёгкой модели выдавать только одну карточку.

## 10. Инструменты разработки
- DEV-00.01 — локальный Windows Runner для автоматических тестов — **IN_PROGRESS** (зависимость WEB-00.02 DONE; требуется однократная регистрация Windows x64 runner и первый успешный запуск).

## 11. Supporting automation (outside the Sentinel Explorer Web product roadmap)

These tasks support the separately maintained private Sentinel Explorer Agent; they do not implement browser-GIS features and must not alter product gates G0–G8.

- OPS-CTRL-01 — public hash-only Sentinel command approval relay in `tools/sentinel_control_relay/` — **IN_REVIEW** (PR work in progress; public workflow and offline tests added; private Sentinel verifier integration and live read-only acceptance are separate follow-up work). Card: `tasks/SENTINEL_COMMAND_RELAY.md`.
