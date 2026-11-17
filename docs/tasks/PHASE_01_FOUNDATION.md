# Phase 01 — каркас

WEB-01.01 — DONE; WEB-01.02 — IN_PROGRESS; WEB-01.03—WEB-01.10 — PLANNED. Не добавлять Sentinel business logic на этом этапе.

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
**Статус:** IN_PROGRESS.  
**Зависимость:** WEB-01.01 — DONE.  
**Goal:** создать минимальный запускаемый frontend без бизнес-логики Sentinel.
**Scope:** Vue 3 + Vite + TypeScript в каталоге `app/`; strict TypeScript; lockfile; минимальный `App.vue`; локальный dev server и production build. Не добавлять OpenLayers, backend API, mock satellite scenes, external runtime CDN или provider logic.
**План проверки:** `npm ci`; `npm run build`; smoke-check dev server через HTTP; проверить, что production bundle не зависит от внешнего runtime CDN. Если локальная среда не имеет доступа к npm registry, выполнить те же проверки на GitHub-hosted runner и сохранить lockfile, созданный npm.
**Acceptance criteria:** package/config/entry созданы; TypeScript strict включён; lockfile зафиксирован; production build проходит; dev server отдаёт приложение; runtime assets собираются локально.
**Ограничение:** успешная сборка не подтверждает доступность приложения/источников из России. Российские проверки выполняются пользователем после выдачи dev-build; G0 остаётся открыт.

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
