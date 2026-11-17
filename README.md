# Sentinel Explorer

Репозиторий содержит презентационный лендинг Sentinel Explorer и проектную документацию для разработки самостоятельной браузерной ГИС-версии.

## С чего начать
- Лендинг: index.html.
- Документация: [docs/README.md](docs/README.md).
- Локальный запуск frontend/backend: [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md).
- Главный пошаговый план: [docs/EXECUTION_PLAN.md](docs/EXECUTION_PLAN.md).
- Правила работы лёгких ИИ-моделей: [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md).
- Доступность материалов из России: [docs/DATA_ACCESS_RUSSIA.md](docs/DATA_ACCESS_RUSSIA.md).

## Статус
- Лендинг существует.
- Создан минимальный frontend scaffold на Vue 3 + Vite + TypeScript; backend, карта, каталог и просмотр снимков ещё не реализованы.
- Архитектура и план разработки зафиксированы в docs/.
- Доступность зарубежных каталогов и исходных файлов Sentinel-2 из российских сетей не подтверждена и должна быть проверена до разработки загрузчика.

GitHub Pages можно использовать для лендинга, но не для рабочего сервиса с API, растровой обработкой и хранением данных.
