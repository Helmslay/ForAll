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
WEB-00.01 и WEB-00.02 — DONE; WEB-00.03 — IN_PROGRESS (безопасный STAC Search для тестового AOI Березников); G0 остаётся открытым. Первый локальный Windows dev-build пользователя успешно проверен 2026-11-18. По ADR-010 разрешено продолжить G1 до первого локального dev-build; это не снимает G0 gate для provider/raster/imagery/download/no-VPN claims.

## 4. Сквозные UX-задачи
Карточка: `tasks/UX_01_SOFT_NEUTRAL_PALETTE.md`.
- UX-01 — DONE (PR #11; frontend и landing CI прошли).

## 5. Реестр задач

### Публичный лендинг
Карточка: `tasks/LANDING_PAGE.md`.
- LP-01 — DONE (PR #9).

### Фаза 00 — источники и российская доступность
Карточки: `tasks/PHASE_00_SOURCE_ACCESS.md`.
- WEB-00.01 — DONE.
- WEB-00.02 — DONE.
- WEB-00.03 — IN_PROGRESS. PR #24 merged; exact-head CI `44310541026` SUCCESS; 23 offline tests PASS. Остался реальный Search с Windows-компьютера в России без VPN/proxy.
- WEB-00.04 — безопасный snapshot test item.
- WEB-00.05 — проверка четырёх каналов и asset metadata.
- WEB-00.06 — HTTP Range и COG read.
- WEB-00.07 — preview реальной сцены.
- WEB-00.08 — тест российского storage.
- WEB-00.09 — runbook проверки из российских сетей.
- WEB-00.10 — provider decision.

Gate G0: законный source проходит catalog + real raster read с российского backend; пользовательский путь проверяется отдельно. До этого imagery implementation BLOCKED.

### Фаза 01 — foundation
Карточки: `tasks/PHASE_01_FOUNDATION.md`.
- WEB-01.01 — DONE.
- WEB-01.02 — DONE.
- WEB-01.03 — DONE.
- WEB-01.04 — DONE.
- WEB-01.05 — DONE.
- WEB-01.06 — DONE.
- WEB-01.07 — DONE.
- WEB-01.08 — DONE.
- WEB-01.09 — DONE.
- WEB-01.10 — DONE (PR #17; exact-head frontend CI `44126893666` SUCCESS; merge `9936f6af3942ff929867478bbeb237b7c5fce29b`).
- WEB-01.11 — DONE (PR #19; exact-head CI `44133991243` SUCCESS).
- WEB-01.12 — DONE (PR #27; exact-head CI `44328382848` SUCCESS; temporary dev-only advisory exception expires/requires review 2026-12-02).

Gate G1: новый разработчик запускает проект по инструкции, health и проверки проходят.

### Фаза 02 — карта и UI
Карточки: `tasks/PHASE_02_MAP_UI.md`.
- WEB-02.01 — DONE (PR #28; CI `44329428142` SUCCESS).
- WEB-02.02 — DONE (PR #29; CI `44331108330` SUCCESS).
- WEB-02.03 — DONE (PR #30; CI `44332026191` SUCCESS).
- WEB-02.04 — DONE (PR #32; CI `44339512145` SUCCESS).
- WEB-02.05 — BLOCKED (G0/source network and licensing gate).
- WEB-02.06 — DONE (PR #35; CI `44358215174` SUCCESS; merge `b3870808b0b6ada015d5f1cc158abedd86c9621c`).
- WEB-02.07 — DONE (PR #36; CI `44359722241` SUCCESS; merge `b485dfb429f50292702410bb43d4283cf9c3a8e9`).
- WEB-02.08 — DONE (PR #52; CI `44552193095` SUCCESS; merge `f6b75e6071b3779f693abdeb1a35c62015ffeea3`).

Gate G2: пользователь создаёт AOI и видит bbox.

### Фаза 03 — каталог и поиск
Карточки: `tasks/PHASE_03_CATALOG.md`.
- WEB-03.01 — DONE (PR #53; backend CI `44576619525` SUCCESS, 30 tests + Uvicorn smoke; frontend CI `44576619705` SUCCESS; merge `8ca882cc7cde1769d0293f92a5d9f39f3b86b79e`).
- WEB-03.02 — DONE (PR #54; backend CI `44589067499` SUCCESS, 40 tests + Uvicorn smoke; frontend CI `44589067504` SUCCESS; merge `ccd9f52d449b5322fadc8ff4b582d076ce01cbe5`).
- WEB-03.03 — IN_REVIEW (synthetic offline STAC fixtures and tests added; PR CI pending).
- WEB-03.04 — STAC HTTP client.
- WEB-03.05 — primary provider adapter; depends on WEB-00.10.
- WEB-03.06 — STAC normalizer.
- WEB-03.07 — search API endpoint.
- WEB-03.08 — catalog orchestrator.
- WEB-03.09 — cursor pagination.
- WEB-03.10 — provider partial status.
- WEB-03.11 — frontend search API client.
- WEB-03.12 — search form/results.
- WEB-03.13 — scene details/footprint.

Gate G3: реальные сцены возвращаются и отображаются; fixtures покрывают unit tests.

### Фаза 04 — imagery/RGB
Карточки: `tasks/PHASE_04_IMAGERY.md`.
- WEB-04.01–WEB-04.15 — PLANNED; blocked by G0 and their declared dependencies.

### Фаза 05 — downloads/storage
Карточки: `tasks/PHASE_05_DOWNLOADS_DATA.md`.
- WEB-05.01–WEB-05.12 — PLANNED.

### Фаза 06 — vectors/forest
Карточки: `tasks/PHASE_06_LOCAL_VECTORS_FOREST.md`.
- WEB-06.01–WEB-06.11 — PLANNED.

### Фаза 07 — offline/analytics
Карточки: `tasks/PHASE_07_OFFLINE_ANALYTICS.md`.
- WEB-07.01–WEB-07.12 — PLANNED.

### Фаза 08 — release
Карточки: `tasks/PHASE_08_RELEASE.md`.
- WEB-08.01–WEB-08.11 — PLANNED.

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
- DEV-00.01 — локальный Windows Runner для автоматических тестов — IN_PROGRESS (требуется однократная регистрация runner и первый успешный запуск).
