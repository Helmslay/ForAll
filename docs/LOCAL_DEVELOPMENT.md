# Локальная разработка Sentinel Explorer Web

Эта инструкция описывает запуск текущего **development scaffold**: Vue/Vite frontend и FastAPI backend. Это ещё не полноценная ГИС: карта, каталог Sentinel-2, просмотр снимков и загрузка данных пока не реализованы.

## 1. Что понадобится

Основной и рекомендуемый способ — Docker Compose. Устанавливать Node.js и Python на компьютер для этого способа не требуется: контейнеры используют Node 24 и Python 3.12.

- **Docker Desktop** для Windows или macOS либо Docker Engine для Linux.
- Docker Compose v2 (команда `docker compose`, с пробелом).
- Git — если репозиторий ещё не получен локально.
- Свободные локальные порты **5173** (frontend) и **8000** (backend). Оба порта публикуются только на `127.0.0.1`.

Для Windows рекомендуется Docker Desktop с включённым WSL 2 backend. После установки запустите Docker Desktop и дождитесь состояния Running.

Проверьте установку в PowerShell, Windows Terminal или терминале Linux/macOS:

```sh
docker version
docker compose version
```

Команда `docker version` должна показывать как Client, так и Server. Если раздел Server недоступен, Docker Engine ещё не запущен.

## 2. Получить проект

Если репозиторий ещё не клонирован:

```sh
git clone https://github.com/Helmslay/ForAll.git
cd ForAll
```

Если проект уже клонирован, перейдите в его корневой каталог — туда, где находятся `compose.yaml`, `app/` и `backend/`, и обновите ветку:

```sh
git switch main
git pull
```

Если GitHub недоступен из вашей сети, получите репозиторий разрешённым для вас способом (например, через заранее подготовленный архив). Для запуска уже полученной копии доступ к GitHub не требуется, но Docker должен иметь возможность скачать базовые образы и зависимости при первом старте.

## 3. Переменные окружения

Для текущего dev-запуска отдельный файл `.env` не требуется. Compose задаёт адрес Vite внутри контейнера и адрес backend-сервиса во внутренней сети Compose.

Backend имеет безопасные значения по умолчанию и запускается без секретов. Не добавляйте токены, пароли или signed URLs в frontend, `compose.yaml`, Git или Docker image. Файл `.env` игнорируется Git; если позднее появятся необходимые локальные настройки, документируйте их отдельно и не публикуйте секреты.

## 4. Запустить приложение

Из корня репозитория выполните:

```sh
docker compose up -d
```

При первом запуске Docker скачает базовые образы, установит Python-зависимости backend и npm-зависимости frontend. Это может занять несколько минут и требует доступа к соответствующим registry/package repositories.

Посмотрите состояние сервисов:

```sh
docker compose ps
```

Дождитесь состояния `healthy` у сервисов `api` и `web`. Если сервис ещё запускается, повторите команду через некоторое время. Логи:

```sh
docker compose logs -f api web
```

Откройте frontend в браузере:

- http://localhost:5173/

Проверить backend напрямую:

- http://localhost:8000/api/v1/health

Проверить backend через тот же proxy-путь, которым пользуется frontend:

- http://localhost:5173/api/v1/health

Успешный health response содержит `status: "ok"`, `app_version` и UTC `timestamp`. Этот endpoint проверяет только работоспособность backend-процесса; он не проверяет внешние каталоги или источники спутниковых данных.

## 5. Проверки и тесты

Команды ниже выполняются из корня репозитория.

### Frontend

```sh
docker compose exec web npm run lint
docker compose exec web npm run format:check
docker compose exec web npm run typecheck
docker compose exec web npm test
docker compose exec web npm run build
```

### Backend

Сначала установите тестовые зависимости в работающий контейнер:

```sh
docker compose exec api python -m pip install --no-cache-dir -r requirements-dev.txt
```

Затем выполните тесты:

```sh
docker compose exec api python -m pytest -q
```

### Compose configuration

Проверить конфигурацию без запуска сервисов, включая ограничение публикации портов на localhost:

```sh
docker compose config --quiet
```

После изменения зависимостей или конфигурации пересоздайте сервисы:

```sh
docker compose up -d
```

Compose использует bind mounts для исходников, поэтому изменения файлов приложения доступны контейнерам без сборки собственного image. Vite и Uvicorn запущены в режиме разработки с autoreload.

## 6. Остановить приложение

Остановить и удалить контейнеры и сеть, сохранив именованный volume с frontend `node_modules`:

```sh
docker compose down
```

Запустить снова:

```sh
docker compose up -d
```

Если требуется полностью пересоздать volume зависимостей frontend (например, после проблем с npm install), используйте:

```sh
docker compose down --volumes
docker compose up -d
```

Удаление volumes удалит сохранённый `node_modules`; при следующем старте npm зависимости будут установлены заново. Не используйте `--volumes`, если в Compose появятся volumes с пользовательскими данными, не предназначенными для удаления.

## 7. Типичные проблемы

| Симптом | Что проверить |
|---|---|
| `Cannot connect to the Docker daemon` или отсутствует Server в `docker version` | Запущен ли Docker Desktop / Docker Engine; дождитесь состояния Running и повторите команду. |
| Ошибка скачивания образа или установки пакетов | Есть ли интернет-доступ к Docker registry и npm/Python package repositories; повторите запуск после восстановления доступа. |
| Порт 5173 или 8000 уже занят | Остановите процесс, занимающий порт, либо освободите порт перед запуском Compose. |
| Сервис долго остаётся `starting` или становится `unhealthy` | Выполните `docker compose logs api web`; проверьте ошибки установки зависимостей и повторите `docker compose ps`. |
| Frontend открывается, но `/api/v1/health` не отвечает | Проверьте, что `api` имеет статус `healthy`, затем изучите `docker compose logs api web`. |
| Изменения frontend не видны | Проверьте, что редактируете файлы внутри каталога `app/` именно того клона, из которого запущен Compose; посмотрите логи Vite. |
| Ошибка npm после изменения lockfile или зависимостей | Выполните `docker compose down --volumes`, затем `docker compose up -d`, чтобы создать volume `node_modules` заново. |

Для просмотра состояния и логов:

```sh
docker compose ps
docker compose logs --tail=100 api web
```

## 8. Ограничения текущей dev-сборки

- Это среда разработки, а не production deployment. Не публикуйте её как публичный сервис и не используйте для production.
- Compose публикует порты frontend и backend только на `127.0.0.1` хост-компьютера. Они не предназначены для доступа с других устройств локальной сети. Для удалённого доступа потребуется отдельное осознанное изменение конфигурации и проверка безопасности.
- В приложении пока нет рабочей карты, поиска Sentinel-2, raster viewer или загрузки сцен.
- Доступность источников данных и скачивание снимков из российских сетей без VPN не подтверждены. Запуск приложения через Compose этого не доказывает.
- Для реальной интеграции поставщиков данных остаётся обязательным gate G0: проверки каталога, чтения реальных raster assets с российского backend и отдельная проверка пользовательского пути из российских сетей.

## 9. Подтверждённые проверки

На 2026-11-17 GitHub Actions Frontend build run `44118409536` успешно выполнил npm install/lint/format/typecheck/tests/build, проверку конфигурации Compose, запуск обоих сервисов до healthy и smoke-check frontend и backend health через Vite proxy внутри Compose.

Локальный запуск на компьютере пользователя этой проверкой не подтверждён. После первого запуска на своей машине проверьте оба URL health endpoint из раздела 4 и сообщите результат, особенно если проверка выполняется из российской сети.
