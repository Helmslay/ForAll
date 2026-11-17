# Phase 01 — каркас

Все задачи PLANNED. Не добавлять Sentinel business logic на этом этапе.

## WEB-01.01 — структура и ignore rules
Зависимости: нет. Scope: directories и .gitignore.
Создать app/, backend/, scripts/, deployment/. Игнорировать node_modules, build, venv, cache, temporary uploads и .env. Добавить .env.example без секретов.
Проверка: фиктивный .env и build не появляются в git status.
Приёмка: секреты/сборка игнорируются; структура минимальна.

## WEB-01.02 — frontend scaffold
Зависимость: WEB-01.01. Scope: app package/config/entry.
Создать Vue 3 + Vite + TypeScript, strict TS, lockfile, минимальный App.vue. Не добавлять OpenLayers.
Тест: install, dev, production build.
Приёмка: проект собирается offline после установки зависимостей и не использует external runtime CDN.

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
