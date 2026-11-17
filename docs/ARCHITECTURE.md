# Architecture — Sentinel Explorer Web

## 1. Решение верхнего уровня
Начальная архитектура — модульный монолит: один frontend, один FastAPI backend, PostgreSQL/PostGIS, растровый движок и отдельный worker для длительных jobs. Модули разделены логически, но не развёртываются как микросервисы без измеренной причины.

Браузер общается только с backend API приложения. Backend скрывает детали каталогов, storage и raster processing.

## 2. Стек

### Frontend
- Vue 3 + TypeScript + Vite.
- OpenLayers для карты, слоёв и геометрий.
- Pinia — только для состояния, реально разделяемого между компонентами.
- Vitest для unit/component tests.
- Playwright для ключевых browser E2E.

### Backend
- Python, версия фиксируется в конфигурации проекта.
- FastAPI, Pydantic.
- PostgreSQL + PostGIS.
- Rasterio/GDAL для растровых операций.
- rio-tiler может использоваться как tile engine после проверки совместимости.
- Shapely/pyproj для геометрии и CRS.
- pytest.
- Worker и очередь для длительных экспортов/подготовки данных. Redis вводить на этапе очередей, не раньше без необходимости.

### Storage
- StorageBackend interface.
- Локальная файловая реализация для dev/test.
- S3-compatible production storage в российской инфраструктуре после сетевой проверки.
- Метаданные, геометрии, jobs и записи кэша — в PostgreSQL.
- Большие растры не хранить в таблицах БД.

## 3. Backend modules
- api: routes, validation, error mapping, versioning.
- catalog: CatalogProvider и STAC adapters.
- scenes: нормализованная Scene.
- imagery: COG read, channel inspect, stats, RGB, tiles.
- downloads: export jobs, AOI clip, packaging.
- storage: local/object backends.
- cache: metadata, tile и export cache.
- vectors: локальные и будущие внешние слои.
- jobs: job states и worker.
- observability: logs, metrics, health.

Не класть всё в main.py и не создавать пустые абстракции на каждый метод.

## 4. Frontend modules
- app shell;
- map lifecycle, sources и layers;
- search;
- scene details;
- renderer/RGB;
- layer tree;
- downloads;
- local data;
- settings;
- typed API client;
- stores для общего состояния.

Vue components не должны напрямую обращаться к STAC, GDAL, S3 или foreign providers.

## 5. CatalogProvider contract
Адаптер:
1. Ищет по bbox, datetime и параметрам.
2. Нормализует внешнюю запись в Scene.
3. Сохраняет provider, collection и item id.
4. Возвращает внутренние server-side asset references, не секретные URL.
5. Описывает capabilities и неполные возможности.
6. Нормализует ошибки, сохраняя техническую причину в серверном логе.

Scene key включает provider + collection + item. Не считать item id глобально уникальным без контекста.

## 6. Нормализованная Scene
Минимум:
- key — внутренний непрозрачный ID;
- provider;
- collection;
- item_id;
- acquired_at UTC;
- platform если есть;
- cloud_cover number or null;
- geometry GeoJSON WGS84;
- bbox WGS84;
- assets map;
- ограниченный набор полезных source properties.

Asset содержит href reference, media type, roles, band identity, GSD/resolution, CRS, nodata, scale, offset и доступность. Поля могут отсутствовать. Не придумывать значения.

## 7. Search data flow
1. Browser отправляет POST /api/v1/catalog/search.
2. Backend валидирует bbox, даты, облачность, limit.
3. Orchestrator вызывает включённые провайдеры.
4. Адаптеры выполняют STAC-запросы.
5. Normalizer формирует Scene.
6. Дубли удаляются только по надёжному ключу.
7. Response содержит items, cursor, providers status и partial flag.
8. Ошибка одного источника может дать partial result, если другой успешен; ошибки всех источников — ясная ошибка доступности.

## 8. Imagery flow
1. Клиент выбирает scene key и RGB assignment.
2. Клиент запрашивает тайл у собственного API.
3. Backend проверяет сцену и assets через allowlist.
4. Raster engine читает необходимые данные из COG или локального кэша.
5. Для каждого канала учитываются nodata, masks, scale/offset, если они заданы.
6. Каналы приводятся к согласованной сетке по документированному правилу.
7. Формируется PNG/WebP tile.
8. Tile cache key включает scene, z/x/y, RGB и все rendering parameters.

Три RGB-слота могут иметь повторяющиеся каналы, если UI позволяет. Каждый слот независимо выбирает B02/B03/B04/B08.

## 9. Каналы и grid
Базовый набор MVP: B02/B03/B04/B08. Не считать любое внешнее описание источника полным: проверять фактические CRS, dimensions, pixel size, transform, dtype и masks каждого asset. При различии сеток выполнить явный resampling и записать метод. Экспорт сохраняет корректную геопривязку.

Дополнительные bands не добавлять молча. NBR требует SWIR; четырёх базовых каналов недостаточно.

## 10. Raster engine
- Первичная поддержка COG/GeoTIFF.
- Обязательна проверка HTTP Range/COG.
- Учитывать nodata/masks.
- Scale/offset применять только по metadata, не придумывать коэффициенты и не применять дважды.
- Статистика отдельная для каждого канала.
- Некорректная статистика не должна молча давать чёрное изображение.
- Большие AOI обрабатывать в worker, не блокировать HTTP.

## 11. Cache
Типы:
- catalog cache;
- RGB tile cache;
- разрешённый source cache;
- export cache.

Ключ включает все параметры, влияющие на результат. Нужны TTL, квоты, очистка, логирование. Кэширование не означает автоматического права на бессрочное зеркало данных.

## 12. Security
- Секреты поставщиков только на backend.
- Asset resolver только по allowlist.
- SSRF protection: запрет произвольных URL, localhost/private/link-local IP, опасных redirects.
- Лимиты bbox/площади/разрешения/экспорта.
- Upload ZIP защита от zip-slip и decompression bombs.
- Rate limits для search/tiles/export.
- Не логировать tokens и signed URLs.
- Проверять права на кэширование и распространение.

## 13. Развёртывание
Production в российской инфраструктуре. Backend вызывает разрешённые upstream endpoints и/или отдаёт российский cache. Если upstream недоступен — локально сохранённые данные остаются доступными в пределах правил хранения.

GitHub — source control; GitHub Pages — только лендинг.

## 14. Нельзя менять без ADR
- browser → own versioned API;
- provider adapters;
- no mandatory direct browser ↔ foreign provider access;
- scene identity = provider + collection + item;
- four baseline bands;
- Russian hosting/cache;
- no no-VPN promise before network tests;
- no microservices/Kubernetes without demonstrated need.
