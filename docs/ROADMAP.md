# Roadmap — Sentinel Explorer Web

Roadmap описывает порядок поставки, а не календарное обещание. Переход между этапами определяется gate criteria.

## G0 — prove data access
Проверить STAC root/collections/search, реальный item над Пермским краем, assets B02/B03/B04/B08, Range/COG, raster read, российский storage, российские сети, правовые условия.
**Gate:** минимум один разрешённый provider прошёл catalog + actual raster read с российского backend; пользовательский путь тестируется отдельно. Иначе imagery pipeline BLOCKED.

## G1 — runnable foundation
Vue 3/TS/Vite, FastAPI, config, health, tests, development Compose.
**Gate:** clean setup запускает frontend/backend, проверки проходят.

## G2 — map and shell
OpenLayers, base map с проверенной доступностью в РФ, AOI drawing, search panel, network/provider states.
**Gate:** можно задать AOI и получить валидный bbox.

## G3 — real catalog
STAC provider abstraction, adapter источника G0, search by AOI/date/cloud, Scene normalizer, pagination, partial states.
**Gate:** реальные сцены отображаются, не mock.

## G4 — imagery
Четыре bands, reflectance handling, RGB renderer, tile API, selectors, cache.
**Gate:** real scene видна на карте; любой band переназначается на R/G/B.

## G5 — export
Jobs/worker, AOI crop, GeoTIFF, Russian storage, checksum, Range/resume.
**Gate:** реальный файл скачан и проверен независимым raster tool.

## G6 — GIS data
GeoJSON/Shapefile, attributes, local GeoTIFF, layer tree, verified forest overlay.
**Gate:** локальные данные и attributes работают; внешний лесной источник имеет подтверждённый разрешённый API.

## G7 — offline and analytics
PWA shell, offline packages, local operations, NDVI, scene comparison, forest-change test datasets.
**Gate:** offline проверен при полном отключении сети; индексы проверены на известных fixtures.

## G8 — release
Production deployment, security, monitoring, backups, Russia network acceptance, runbook.
**Gate:** выполнен release checklist и сохранён тестовый отчёт.

## Ограничения
- MVP: B02/B03/B04/B08.
- NBR требует SWIR; базовые четыре канала недостаточны.
- Российский hosting не гарантирует upstream доступ.
- Кэш/репликация только при соблюдении условий источника.
- Browser offline ограничен storage quota; пакет имеет лимит размера.
