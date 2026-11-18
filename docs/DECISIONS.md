# Architecture decision log

Use this log for decisions affecting more than one module. Format: status, context, decision and consequences.

## ADR-001 — modular monolith
**Status:** Accepted. Vue frontend + FastAPI backend with internal modules. No microservices initially. Easier for small tasks and local testing; split only when measured need appears.

## ADR-002 — browser never calls upstream catalog directly
**Status:** Accepted. Production search/imagery/download use the app backend. Centralizes auth, availability, caching and avoids exposing secrets.

## ADR-003 — provider adapters
**Status:** Accepted. Each STAC/raster provider maps to common Scene model. UI is provider-independent.

## ADR-004 — Russian hosting and network gate
**Status:** Accepted. App/API/cache in Russia. Upstream reachability and end-user access are separate test gates. No no-VPN claim before evidence.

## ADR-005 — four baseline bands
**Status:** Accepted. MVP B02/B03/B04/B08 and free assignment to RGB. Extra bands require explicit decision. NBR needs SWIR.

## ADR-006 — COG and GDAL/Rasterio
**Status:** Accepted with validation. COG/GeoTIFF primary read path; test real Range/COG on selected source.

## ADR-007 — PostGIS and object storage
**Status:** Accepted. Metadata/geometries/jobs in PostGIS; large rasters/exports in file or S3-compatible storage behind interface.

## ADR-008 — background export
**Status:** Accepted. Long exports are jobs with worker, checksum and file delivery, not long blocking HTTP calls.

## ADR-009 — browser offline scope
**Status:** Accepted with limits. Cache shell and bounded offline packages; local data works offline; no promise of unlimited browser storage.

## ADR-010 — G1 foundation may proceed before G0 completion
**Status:** Accepted by explicit user authorization (2026-11-17).  
**Context:** The user will perform Russian-network acceptance checks after the first development build. Completing the frontend/backend development foundation does not require implementing satellite-data access.  
**Decision:** Continue G1 foundation tasks through the first local development build while G0 remains open. Do not implement provider adapters, real STAC search, raster access, imagery rendering, downloads, or claim no-VPN availability before the applicable G0 checks pass. Russian-network tests are deferred until the user receives the dev-build.  
**Consequences:** G1 work is temporarily authorized as a sequencing exception. G0 remains an independent hard gate for all real data/provider functionality and release claims.


## ADR-011 — единая мягкая нейтральная палитра интерфейса
**Status:** Accepted by explicit user direction (2026-11-17).
**Context:** Пользователь отклонил зелёную тему и попросил более мягкие цвета во всём проекте.
**Decision:** Использовать единую холодную графитово-сине-серую палитру с приглушённым голубым основным акцентом и лавандовым дополнительным акцентом для публичного лендинга и браузерного приложения. Не использовать зелёный в UI.
**Consequences:** Цвета реальных спутниковых изображений и тематических геоданных не перекрашиваются. Состояния warning/error сохраняют семантически различимые оттенки; контраст проверяется по WCAG для текста и интерактивных состояний.

## ADR-012 — потоковый просмотр спутниковых снимков без постоянного хранения полных сцен
**Status:** Accepted by explicit user direction (2026-11-18).
**Context:** Полное скачивание спутниковых сцен на сервер ради отображения создаёт ненужную нагрузку на диск и сеть. На VPS ограниченный объём диска; просмотр должен подгружать данные по мере перемещения и масштабирования карты.
**Decision:**
- Основной путь отображения — потоковое чтение только необходимых частей исходных растров и формирование картографических тайлов по запросу, без постоянного скачивания и хранения полных сцен на сервере.
- Предпочтительный технический путь — COG/GeoTIFF с HTTP Range и оконным чтением через backend, если конкретный источник действительно поддерживает этот режим. Совместимость каждого источника должна быть подтверждена испытаниями.
- Все обращения к каталогам и raster assets выполняются через backend; браузер не обращается к upstream-поставщикам напрямую.
- Временный кэш готовых тайлов и промежуточных данных допустим только с ограничениями по объёму и сроку хранения, безопасной очисткой и запретом удалять данные, используемые активными операциями.
- Полное скачивание исходных данных допускается для явно запрошенного экспорта или отдельно согласованного offline-пакета, но не как скрытый этап обычного просмотра.
**Consequences:**
- При проектировании raster reader и tile endpoint учитывать частичное чтение, повторное использование тайлов, ограниченный кэш и его автоматическую очистку.
- Проверить HTTP Range/COG, доступность каналов B02/B03/B04/B08, производительность, лицензии и российскую сетевую доступность до выбора production-поставщика.
- Это архитектурное решение не означает, что потоковый просмотр уже реализован, что любой кандидат поддерживает Range/COG или что доступ без VPN подтверждён.
- Текущая задача WEB-00.03 не расширяется: испытания raster assets и Range/COG выполняются отдельными последующими задачами фазы 00.


## ADR-013 — временное принятие одного риска npm audit для devDependency
**Status:** Accepted temporarily by explicit user authorization (2026-11-18); implemented in PR #27, merged as `f65060be3a9f862a20e2473cc2e4ea3ed26471aa`; exact-head CI run `44328382848` SUCCESS.
**Context:** GitHub-reviewed advisory GHSA-fc5q-39xc-vjpf affects `picomatch@4.0.7`, which is present only in the frontend development toolchain. The advisory did not list a patched release at the time of review; forcing a Vite downgrade or unverified override would create additional compatibility risk.
**Decision:** Temporarily allow only the exact high-severity dependency graph propagated from advisory GHSA-fc5q-39xc-vjpf on `picomatch@4.0.7`: `picomatch`, `@vue/language-core`, `fdir`, `tinyglobby`, `vite`, `vitest`, and `vue-tsc`, each at its reviewed exact lockfile version and exact `npm audit` dependency edges. Every other high/critical advisory, package, version, dependency scope or path remains a CI failure. Dependency scope is verified from `package-lock.json`; the npm audit severity report remains visible. This is risk acceptance, not a security fix.
**Review/expiry:** Recheck upstream advisory/release status within 14 days (by 2026-12-02) and remove the exception as soon as a patched compatible version is available. Revert the exception if the package moves into production dependencies or the dependency path changes.
**Consequences:** This does not authorize downgrading Vite, force-updating packages, weakening production controls, or claiming the vulnerability is fixed. The exception is tested by five Node policy tests and full frontend CI. Review/remove by 2026-12-02, or earlier as soon as an upstream patched release is available.
