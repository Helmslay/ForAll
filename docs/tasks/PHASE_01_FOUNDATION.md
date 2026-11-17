# Phase 01 — каркас

WEB-01.01 — DONE; WEB-01.02 — DONE; WEB-01.03—WEB-01.10 — PLANNED. Не добавлять Sentinel business logic на этом этапе.

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
Зависимость: WEB-01.02. Добавить formatter/linter, Vitest, scripts lint/format-check/typecheck/test. Один простой unit test.
Приёмка: каждый script запускается без сети после install.

## WEB-01.04 — app shell placeholder
Зависимость: WEB-01.02. Создать header/sidebar/workspace placeholders на русском. Без фиктивных сцен и спутниковых данных. Render test.
Приёмка: семантические regions корректны.

## WEB-01.05 — FastAPI scaffold
Зависимость: WEB-01.01. Создать Python package, app factory, pinned deps, env settings, uvicorn entry. Не подключать БД или rasterio.
Тест: import и TestClient.
Приёмка: backend стартует без secrets.

## WEB-01.06 — error contract/request ID
Зависимость: WEB-01.05. Middleware request ID и error JSON из API_CONTRACTS. Stack trace только в серверном логировании.
Тест: endpoint с ошибкой и проверка response.
Приёмка: no traceback в клиентском ответе.

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
