# Phase 01 — каркас

WEB-01.01 — DONE; WEB-01.02 — DONE; WEB-01.03 — DONE; WEB-01.04 — DONE; WEB-01.05 — DONE; WEB-01.06—WEB-01.10 — PLANNED. Не добавлять Sentinel business logic на этом этапе.

## WEB-01.01 — структура и ignore rules
Зависимости: нет. Scope: directories и .gitignore.
Создать app/, backend/, scripts/, deployment/. Игнорировать node_modules, build, venv, cache, temporary uploads и .env. Добавить .env.example без секретов.
Проверка: фиктивный .env и build не появляются в git status.
Приёмка: секреты/сборка игнорируются; структура минимальна.

### Результат WEB-01.01 (2026-11-17)
- Созданы `app/`, `backend/`, `scripts/`, `deployment/` с `.gitkeep`, чтобы Git сохранял пустые каталоги.
- Добавлен корневой `.gitignore` для Node/Python dependencies, build output, virtual environments, caches, logs, temporary uploads, local `.env` и editor/OS artifacts.
- Добавлен `.env.example` без credentials, tokens и signed URLs; конкретные переменные будут добавляться вместе с компонентами, которые их используют.
- **Изменённые файлы:** `.gitignore`, `.env.example`, `app/.gitkeep`, `backend/.gitkeep`, `scripts/.gitkeep`, `deployment/.gitkeep`, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`, `docs/tasks/PHASE_01_FOUNDATION.md`.
- **Проверки:** в изолированном временном Git-репозитории `git check-ignore` подтвердил игнорирование `.env`, `node_modules/`, `dist/` и `uploads/`; `.env.example` и исходный файл приложения не попали под ignore rules. Проверка приложения не применима: исходники frontend/backend этой задачей не создавались.
- **Приёмка:** каталоги созданы; правила для `.env`, build, dependencies, caches и временных uploads добавлены; `.env.example` не содержит секретов. Ограничение: фактический запуск frontend/backend не входит в WEB-01.01.
- **Оговорка:** задача выполнена досрочно по явному разрешению пользователя; G0 остаётся открытым, а дальнейшая реализация imagery заблокирована до прохождения gate.

## WEB-01.02 — frontend scaffold
**Статус:** DONE.  
**Зависимость:** WEB-01.01 — DONE.  
**Goal:** создать минимальный запускаемый frontend без бизнес-логики Sentinel.
**Scope:** Vue 3 + Vite + TypeScript в каталоге `app/`; strict TypeScript; lockfile; минимальный `App.vue`; локальный dev server и production build. Не добавлять OpenLayers, backend API, mock satellite scenes, external runtime CDN или provider logic.
**План проверки:** `npm ci`; `npm run build`; smoke-check dev server через HTTP; проверить, что production bundle не зависит от внешнего runtime CDN. Если локальная среда не имеет доступа к npm registry, выполнить те же проверки на GitHub-hosted runner и сохранить lockfile, созданный npm.
**Acceptance criteria:** package/config/entry созданы; TypeScript strict включён; lockfile зафиксирован; production build проходит; dev server отдаёт приложение; runtime assets собираются локально.
**Ограничение:** успешная сборка не подтверждает доступность приложения/источников из России. Российские проверки выполняются пользователем после выдачи dev-build; G0 остаётся открыт.

### Результат WEB-01.02 (2026-11-17)
- Создан frontend scaffold на Vue 3.5.45, Vite 8.3.8 и TypeScript 7.0.2; TypeScript strict включён.
- Добавлен минимальный Vue экран-заглушка на русском без фиктивных спутниковых данных, карты, provider logic или Sentinel business logic.
- Добавлен `app/package-lock.json`, сгенерированный npm 11.19.1 в CI и зафиксированный в `main`.
- Добавлен GitHub-hosted workflow: `npm ci`, production build и HTTP smoke-check dev server.
- **Изменённые файлы:** `app/package.json`, `app/package-lock.json`, `app/tsconfig.json`, `app/vite.config.ts`, `app/index.html`, `app/src/main.ts`, `app/src/App.vue`, `app/src/style.css`, `.github/workflows/frontend-build.yml`, `docs/DECISIONS.md`, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`, `docs/tasks/PHASE_01_FOUNDATION.md`, `README.md`.
- **Проверки:** GitHub Actions run #12 — `npm ci` PASS (37 packages, 0 vulnerabilities); `npm run build` PASS (Vite 8.3.8, 12 modules transformed); dev server PASS (HTTP 200, HTML содержит `#app`). Локальный npm install в текущей среде недоступен из-за timeout до registry, поэтому сборка проверена на GitHub-hosted runner.
- **Приёмка:** Vue/Vite/TS scaffold создан; strict TS config и lockfile присутствуют; production build проходит; dev server отвечает по HTTP; исходники не содержат внешних runtime CDN.
- **Ограничения:** сетевой интерфейс не отключался специально для отдельного offline build test; подтверждено отсутствие внешнего runtime CDN, но не проведён тест в network-isolated runner. Backend, карта, каталог, спутниковые assets и российская доступность не реализованы/не проверялись. G0 остаётся открытым.

## WEB-01.03 — frontend quality scripts
**Статус:** DONE.  
**Зависимость:** WEB-01.02 — DONE.  
**Goal:** добавить локальные проверки качества frontend и один unit test без Sentinel business logic.
**Scope:** ESLint + eslint-config-prettier, Prettier, vue-tsc, Vitest + Vue Test Utils + jsdom; scripts `lint`, `format:check`, `typecheck`, `test`. Подключить команды к frontend GitHub Actions. Добавить один render test для существующего App. Не менять архитектуру приложения.
**Совместимость:** TypeScript закреплён на 6.0.3, так как проверка выявила несовместимость `vue-tsc@3.3.14` с TypeScript 7.0.2: CLI завершался с `ERR_PACKAGE_PATH_NOT_EXPORTED` до выполнения проверки. Возврат на TS 6 — временное техническое ограничение до поддержки TS 7 инструментами Vue.
**Изменённые файлы:** `app/package.json`, `app/package-lock.json`, `app/eslint.config.js`, `app/.prettierrc.json`, `app/vite.config.ts`, `app/src/App.spec.ts`, `app/src/App.vue`, `app/src/style.css`, `.github/workflows/frontend-build.yml`, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`, `docs/tasks/PHASE_01_FOUNDATION.md`.
**Проверки:** GitHub Actions run #25 — `npm ci` PASS (250 packages installed); `npm run lint` PASS без warnings; `npm run format:check` PASS; `npm run typecheck` PASS; `npm test` PASS (1 test); `npm run build` PASS (Vite 8.3.8, 12 modules); dev-server HTTP smoke-check PASS. Lockfile обновлён npm 11.19.1.
**Acceptance criteria:** все четыре scripts запускаются после установки зависимостей; Vue/TS typecheck проходит; unit test успешно проверяет имя приложения, eyebrow и status; проверки включены в CI. Скрипты используют локально установленные binaries и не обращаются к внешним сервисам по своей конфигурации.
**Ограничения и follow-up:** отдельный запуск с принудительно отключённым сетевым интерфейсом не выполнялся. `npm ci` сообщил о 7 moderate severity vulnerabilities в dependency tree; точные advisory paths ещё не исследованы, `npm audit fix --force` не запускался. Backend, карта, Sentinel data и доступность из России этой задачей не затрагивались.

## WEB-01.04 — app shell placeholder
**Статус:** DONE.  
**Зависимость:** WEB-01.02 — DONE; WEB-01.03 — DONE.  
**Goal:** заменить одиночный экран-заглушку базовой оболочкой рабочей ГИС.
**Scope:** семантическая верхняя панель приложения, компактная левая навигация, центральная рабочая область под будущую карту и статусная строка; русские подписи; адаптивное перестроение на узких экранах; доступные имена навигационных элементов и видимый focus. Центральная область должна прямо сообщать, что карта ещё не подключена. Не добавлять правую функциональную панель, интерактивные инструменты, карту, fake scenes, imagery или Sentinel business logic.
**Тест:** Vue render test проверяет landmarks (banner/header, navigation, main), подписи и placeholder-состояние; существующий scaffold status test сохранить или объединить.
**Acceptance criteria:** ровно один основной `main`; header/banner, nav и main семантически доступны; названия разделов на русском; центральная рабочая область помечена как место будущей карты и не выдаёт себя за реальную карту; нет выдуманных сцен/координат/статистики; responsive CSS и keyboard focus доступны.
**Не входит:** CSS token system (WEB-02.01), полноценный desktop layout и панели (WEB-02.02/03), OpenLayers (WEB-02.04), search/RGB workflows.

## WEB-01.05 — FastAPI scaffold
Зависимость: WEB-01.01. Создать Python package, app factory, pinned deps, env settings, uvicorn entry. Не подключать БД или rasterio.
Тест: import и TestClient.
Приёмка: backend стартует без secrets.

## WEB-01.06 — error contract/request ID
**Статус:** READY (проверены зависимости и контракт; 2026-11-17).
Зависимость: WEB-01.05 — DONE. API contract: `docs/API_CONTRACTS.md`, разделы 2 и 12.
Scope: request ID для каждого запроса; возвращать его в `X-Request-ID` и в JSON-ошибках; единый формат ошибок для HTTP, validation и непредвиденных исключений. Непредвиденные исключения логировать на сервере с traceback, клиенту возвращать безопасное сообщение. Не добавлять зависимости.
Тесты: TestClient проверяет request ID/header/body, HTTP error, validation error и скрытие traceback при внутренней ошибке.
Приёмка: все ошибки соответствуют `{"error":{"code":"...","message":"...","request_id":"...","details":{}}}`; request ID присутствует в ответе; traceback отсутствует в теле ответа.
Не входит: health endpoint, structured logging framework, новые API endpoints и Sentinel business logic.

## WEB-01.07 — health endpoint
Зависимость: WEB-01.05. GET /api/v1/health: status/version/time. Не проверять upstream при каждом health и не раскрывать private details.
Тест: TestClient.
Приёмка: работает без внешней сети.

## WEB-01.08 — Vite proxy
Зависимости: WEB-01.02, WEB-01.07. Настроить /api proxy; typed API config; один health client.
Тест: frontend dev server получает backend health.
Приёмка: UI component не содержит жёсткий localhost.

## WEB-01.09 — Docker Compose dev
Зависимости: WEB-01.02, WEB-01.05. Web + API, healthchecks, volumes, env local ignored; no secrets in image.
Тест: compose config/up.
Приёмка: оба сервиса запускаются одной командой.

## WEB-01.10 — local development guide
Зависимость: WEB-01.09. Создать docs/LOCAL_DEVELOPMENT.md: prerequisites, install, env, run, test, troubleshooting. Не указывать непроверенные команды как verified.
Приёмка: чистое окружение повторяет setup.


### Результат WEB-01.04 (2026-11-17)
- Реализована базовая оболочка ГИС: верхняя шапка, компактная левая навигация, центральная рабочая область и статусная строка.
- Добавлены русские подписи; будущие инструменты явно отмечены как пока недоступные.
- Центральная область прямо сообщает, что карта, каталог, снимки и геоданные не подключены. Фальшивых сцен, координат и статистики нет.
- Добавлены responsive layouts для узких экранов и видимый keyboard focus.
- Render test проверяет header, aside, nav, ровно один main, основные названия разделов и состояние placeholder.
- **Изменённые файлы:** `app/src/App.vue`, `app/src/style.css`, `app/src/App.spec.ts`, `.github/workflows/frontend-build.yml` (временный formatter step удалён; итоговый workflow без изменения поведения), `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`, `docs/tasks/PHASE_01_FOUNDATION.md`.
- **Проверки:** GitHub Actions Frontend build run `44102025691` для HEAD `65bec3ac993469f115eb4dbaf9975887ed4faf51` — SUCCESS: `npm ci`, ESLint, Prettier check, vue-tsc typecheck, Vitest, production build и Vite dev-server HTTP smoke-check прошли.
- **Acceptance:** все критерии WEB-01.04 подтверждены кодом и успешным frontend CI.
- **Ограничения:** реальная карта и интерактивные инструменты не входят в WEB-01.04. Ручная проверка браузеров/устройств не выполнялась. В dependency tree сохраняются 7 moderate npm advisories, ранее отмеченные в STATUS.
- **PR:** https://github.com/Helmslay/ForAll/pull/10. CI пройден; PR готов к merge.


### Результат WEB-01.05 (2026-11-17)
- Создан минимальный backend package на FastAPI: `backend/app/`, фабрика `create_app()` и экспортируемый ASGI entry point `app.main:app`.
- Добавлены настройки Pydantic Settings с префиксом `SENTINEL_`, необязательным локальным `.env` и безопасными значениями по умолчанию; для старта секреты не требуются.
- Runtime и test зависимости закреплены точными версиями в `backend/requirements.txt` и `backend/requirements-dev.txt`.
- Добавлены два теста: импорт/работа через TestClient без secrets и настройка метаданных через Settings.
- Добавлен отдельный GitHub Actions workflow для Python 3.12: установка зависимостей, pytest и реальный запуск Uvicorn с HTTP smoke-check.
- **Изменённые файлы:** `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/app/__init__.py`, `backend/app/config.py`, `backend/app/main.py`, `backend/tests/test_app.py`, `.github/workflows/backend-tests.yml`, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`, `docs/tasks/PHASE_01_FOUNDATION.md`.
- **Проверки:** GitHub Actions Backend tests run `44106506251` для commit `1411317e0090a1a49f04cb10af33c43308098fa3` — SUCCESS. `python -m pytest -q`: 2 passed; один upstream DeprecationWarning от связки Starlette/AnyIO. Smoke-check `uvicorn app.main:app --host 127.0.0.1 --port 8000` — сервер запустился без secrets, `GET /openapi.json` вернул HTTP 200.
- **Acceptance criteria:** Python package и app factory созданы; runtime/test зависимости закреплены; environment settings работают; ASGI entry point импортируется; TestClient проходит; Uvicorn фактически стартует без secrets. Все критерии подтверждены hosted CI.
- **Ограничения:** endpoints бизнес-логики, health, error contract/request ID, БД, Rasterio/GDAL, provider adapters и Sentinel-функции не добавлялись — это следующие/заблокированные задачи. Локальный запуск на машине пользователя отдельно не выполнялся. G0 остаётся открытым.
- **PR:** https://github.com/Helmslay/ForAll/pull/12 — merged; merge commit `b2a8898c006380ad89df8e6c84a84bad3a0aed04`.
