# Execution plan — для лёгких ИИ-моделей

## 1. Правило исполнения
Это главный индекс разработки. Подробные task cards расположены в docs/tasks/. Одна задача за один запрос модели. Не брать весь этап сразу.

Каждая задача должна иметь ID, dependencies, goal, scope, input context, result, tests, acceptance criteria и explicit non-goals. Если задача не помещается в маленькое изменение, сначала декомпозировать её и обновить этот индекс.

## 2. Dependency chain

    G0 Источники и доступность в России
      ↓
    G1 Каркас frontend/backend
      ↓
    G2 Карта и интерфейс
      ↓
    G3 Каталог и поиск
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
WEB-00.01 и WEB-00.02 — DONE; G0 остаётся открытым. По явному разрешению пользователя (ADR-010) разрешено продолжить G1 до первого локального dev-build, не дожидаясь российских сетевых проверок. Это исключение не снимает G0 gate: реальные provider adapters, STAC search, raster/imagery, downloads и no-VPN claims остаются заблокированы до соответствующих доказательств. STAC checker остаётся диагностической утилитой, а не приложением или provider adapter.

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
- WEB-00.03 — тестовый STAC search для Пермского края.
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
- WEB-01.08 — frontend proxy — **IN_PROGRESS** (Vite `/api` proxy, typed API config and health client; integration CI pending).
- WEB-01.09 — Docker Compose dev.
- WEB-01.10 — local setup guide.

Gate G1: новый разработчик запускает проект по инструкции, health и проверки проходят.

### Фаза 02 — карта и UI
Карточки: tasks/PHASE_02_MAP_UI.md
- WEB-02.01 — CSS tokens.
- WEB-02.02 — desktop app shell.
- WEB-02.03 — responsive panels.
- WEB-02.04 — OpenLayers lifecycle.
- WEB-02.05 — base map provider abstraction.
- WEB-02.06 — координаты и масштаб.
- WEB-02.07 — AOI draw/clear.
- WEB-02.08 — search form shell.

Gate G2: пользователь создаёт AOI и видит bbox.

### Фаза 03 — каталог и поиск
Карточки: tasks/PHASE_03_CATALOG.md
- WEB-03.01 — Scene/Search DTO.
- WEB-03.02 — CatalogProvider Protocol.
- WEB-03.03 — STAC fixtures.
- WEB-03.04 — STAC HTTP client.
- WEB-03.05 — primary provider adapter.
- WEB-03.06 — STAC Item normalizer.
- WEB-03.07 — search API endpoint.
- WEB-03.08 — catalog orchestrator.
- WEB-03.09 — cursor pagination.
- WEB-03.10 — provider partial status.
- WEB-03.11 — frontend search API client.
- WEB-03.12 — search form/results.
- WEB-03.13 — scene details/footprint.

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
- WEB-03.05 зависит от WEB-00.10.
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
