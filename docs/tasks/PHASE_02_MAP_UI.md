# Phase 02 — карта и UI

Следовать UX_UI_GUIDE.md. WEB-02.01—WEB-02.04 — DONE; WEB-02.05 — BLOCKED by G0; WEB-02.06 — DONE; WEB-02.07 — DONE; WEB-02.08 — PLANNED.

## WEB-02.01 — CSS design tokens
**Статус:** DONE (2026-11-18).
**Зависимость:** WEB-01.04 — DONE.
**Goal:** семантические CSS-токены для цветов, spacing, radius и typography.
**Результат:** в `app/src/style.css` добавлены 71 semantic tokens; существующие компоненты переведены на токены без изменения палитры ADR-011; добавлен общий `:focus-visible`; `prefers-reduced-motion` сохранён.
**Проверки:** статический scan — нет recursive token declarations и hard-coded color literals вне `:root`; WCAG contrast ratios для основных text/background пар выше 4.5:1. Exact-head Frontend build CI run `44329428142` для commit `747b4ae1dd803263884cc8729a61047252d7b438` — SUCCESS: npm ci, temporary audit-policy tests, audit, lint, format check, typecheck, unit tests, production build, backend proxy smoke, Compose config, localhost port assertion, Compose start and frontend/API smoke all passed.
**Изменённые файлы:** `app/src/style.css`.
**Приёмка:** токены применены; контраст проверен; reduced-motion сохранён; полный frontend CI пройден.
**Ограничения:** задача не добавляет карту, каталоги, imagery, provider adapters или backend functionality; G0 остаётся открытым.
**PR:** #28 merged; merge commit `d7a13244e6d06615995f48561523149bb21f9c79`.

## WEB-02.02 — desktop app shell
Зависимость: WEB-02.01. Header, compact navigation rail, workspace, right panel, status bar. Без карты/поиска. Приёмка: карта placeholder получает максимум места и focus видим.

**Статус:** DONE (2026-11-18).
**Зависимость:** WEB-02.01 — DONE.
**Результат:** desktop shell собран из верхней панели, компактной 68 px навигационной полосы, центральной рабочей области, контекстной правой панели (280 px) и нижней строки состояния. Карта остаётся главным холстом; placeholder получает keyboard focus и видимый focus ring. На ширине до 900 px правая панель скрывается; на узком экране shell перестраивается в вертикальную компоновку. Функциональность карты/поиска не добавлялась.
**Изменённые файлы:** `app/src/App.vue`, `app/src/style.css`, `app/src/App.spec.ts`.
**Проверки:** PR #29 exact-head commit `4c4b3de3fa3f02c90185e7aa1bea4a527984923d`; Frontend build CI run `44331108330` — SUCCESS: npm audit policy, lint, Prettier, typecheck, unit tests, production build, Vite/backend proxy smoke, Compose config, localhost port assertion, Compose start and frontend/API smoke.
**Приёмка:** все элементы desktop shell присутствуют; центральный placeholder занимает гибкую основную область; keyboard focus доступен; CI прошёл.
**Ограничения:** визуальная проверка в реальном браузере не выполнялась; карта, поиск, network status, coordinates и scale остаются не реализованы. Это только оболочка.
**PR:** #29 merged; merge commit `3dc70e8df8e271ec2bacf60b70341a53b01eb9a7`.
## WEB-02.03 — responsive panels

**Статус:** DONE (2026-11-18).
**Зависимость:** WEB-02.02 — DONE.
**Результат:** контекстная панель сохраняется справа на desktop; на ширине до 900 px становится выдвижной правой панелью с затемнением фона; до 520 px превращается в нижний bottom sheet. Добавлены явные кнопки открытия/закрытия, закрытие по backdrop, aria-controls/aria-expanded, доступные имена и touch-action. Кнопки имеют минимальную высоту/ширину 44 px; переходы учитывают prefers-reduced-motion. Hover для открытия панели не требуется.
**Изменённые файлы:** app/src/App.vue, app/src/style.css, app/src/App.spec.ts.
**Проверки:** PR #30 exact-head commit 34cb4bb7a623929584bc9daac3695ede4addac9a; Frontend build CI run 44332026191 — SUCCESS. Успешны npm audit policy, audit, ESLint, Prettier, TypeScript, Vitest, production build, Vite/backend proxy smoke, Compose config, localhost port assertion, Compose start и frontend/API smoke.
**Приёмка:** responsive drawer/bottom sheet и touch-sized controls реализованы; open/close/backdrop взаимодействия покрыты unit tests; полный frontend CI прошёл.
**Ограничения:** автоматические unit tests не эмулируют реальный viewport/touch browser; ручная визуальная проверка на физических планшете/телефоне не выполнялась. Карта и инструменты пока заглушки.
**PR:** #30 merged; merge commit 39161d5c1cbedea6756e10ed711c139681313c24.

## WEB-02.04 — OpenLayers lifecycle

**Статус:** DONE (2026-11-18); PR #32 merged.
**Зависимости:** WEB-02.02 — DONE; WEB-02.03 — DONE.
**Результат:** закреплён `ol@10.11.0`; npm lockfile сформирован штатным npm. `MapCanvas.vue` + `openLayersMap.ts` создают один экземпляр OpenLayers Map только после mount, с пустым списком слоёв и минимальным View (center [0, 0], zoom 2). `ResizeObserver` вызывает updateSize; cleanup отключает observer, отсоединяет target через setTarget(undefined) и вызывает dispose. Компонент подключён в существующий workspace; responsive shell сохранён.
**Изменённые файлы:** `app/package.json`, `app/package-lock.json`, `app/src/App.vue`, `app/src/App.spec.ts`, `app/src/components/MapCanvas.vue`, `app/src/components/MapCanvas.spec.ts`, `app/src/components/openLayersMap.ts`.
**Проверки:** временный isolated bootstrap workflow run `44338609135` — SUCCESS: npm install --save-exact ol@latest, npm ci, npm audit policy tests, audit, ESLint, Prettier, vue-tsc, Vitest и production build. Стандартный Frontend build CI run `44339512145` для точного PR head `eaf40cc86ec1d2d1d78b600690a5a780a9f18c79` — SUCCESS: npm ci, audit policy, audit, ESLint, Prettier, vue-tsc, Vitest, production build, Vite/backend proxy smoke, Compose config, localhost port assertion, Compose start и frontend/API smoke.
**Критерии приёмки:** map target и один экземпляр карты реализованы; resize/updateSize и полный cleanup покрыты lifecycle tests; remount создаёт независимый экземпляр; тест проверяет отсутствие console errors; в production-коде нет tile/base-map URL, imagery, STAC или provider-запросов. Все критерии приёмки подтверждены кодом, lifecycle tests и exact-head frontend CI.
**Ограничения:** ручная проверка в реальном браузере и на физических устройствах не выполнялась. Холст пустой: базовая карта, Sentinel imagery, координаты, AOI и сетевые запросы не добавлены. G0 остаётся открытым.
**PR:** #32 merged; merge commit `331b06dd9c82fa0a5ee39691a767b71a52da94fe`.
**Временная автоматизация:** оба bootstrap workflow удалены из рабочей ветки после генерации lockfile и предварительных проверок.

## WEB-02.05 — base map provider abstraction
Зависимость: WEB-02.04 и сетевой gate для источника подложки. URL не хардкодить в component; attribution/license; tile error state. Приёмка: provider заменяем и проверен из РФ.

## WEB-02.06 — cursor coordinates/scale

**Статус:** DONE (2026-11-18).
**Зависимости:** WEB-02.04 — DONE; G0 не требуется, так как задача не подключает внешние источники.
**Цель:** показывать координаты курсора в WGS84 и текущее разрешение карты, не завися от наличия базовой подложки.
**Scope:** обработка pointer move на OpenLayers map; преобразование координат из проекции карты в WGS84 с явным порядком longitude/latitude; отображение координат и разрешения в доступной строке состояния; явное пустое состояние, когда курсор вне карты; очистка обработчиков при unmount.
**Тесты:** известная projected coordinate преобразуется в ожидаемые longitude/latitude; форматирование координат и разрешения проверяется; pointerleave очищает координаты; cleanup удаляет события; существующие lifecycle tests остаются зелёными.
**Критерии приёмки:** координаты всегда отображаются в порядке lon, lat; разрешение выводится в метрах на пиксель с корректной локальной point-resolution; вне карты отображается пустое состояние; подписки и DOM listeners снимаются при unmount; полный frontend CI проходит.
**Не входит:** базовая карта, imagery, provider URLs, AOI, измерительные инструменты, backend/API и сетевые запросы.
**Результат:** pointermove преобразует координаты из проекции карты в WGS84; локальное разрешение рассчитывается через OpenLayers `getPointResolution` в метрах на пиксель. В readout отображаются longitude/latitude в явном порядке lon, lat и разрешение; pointerleave показывает пустое состояние. Event key и DOM listener снимаются при cleanup.
**Изменённые файлы:** `app/src/components/MapCanvas.vue`, `app/src/components/openLayersMap.ts`, `app/src/components/MapCanvas.spec.ts`, `tools/check_npm_audit.mjs`.
**Проверки:** lifecycle tests проверяют известную координату EPSG:3857 → WGS84, локальное разрешение, pointerleave и cleanup. Exact-head Frontend build CI run `44357847121` для commit `7d59c768bcf8302847923f828548063ddec12a6f` — SUCCESS: audit policy, npm audit high threshold, ESLint, Prettier, vue-tsc, Vitest, production build, backend proxy smoke, Compose config/localhost binding, Compose startup and frontend/API smoke. Tools offline tests run `44357847194` — SUCCESS.
**Дополнительное исправление CI:** `tools/check_npm_audit.mjs` теперь явно использует `--audit-level=high`, что соответствует существующей политике high/critical gate; семь moderate dev-tool findings остаются видимыми в отчёте и не принимаются как новые исключения.
**Ограничения:** ручная проверка на физических устройствах не выполнялась. Карта остаётся пустой; разрешение рассчитывается в точке курсора для текущего view, не для конкретного спутникового источника. G0 остаётся открытым.
**Приёмка:** WGS84 lon/lat order, локальное разрешение, empty state вне карты, listener cleanup и полный exact-head CI подтверждены.
**PR:** #35 merged; merge commit `b3870808b0b6ada015d5f1cc158abedd86c9621c`.
**Временная автоматизация:** временные audit-diagnostic и Prettier workflows удалены после использования.

## WEB-02.07 — AOI rectangle draw/clear

**Статус:** DONE (2026-11-18).
**Зависимости:** WEB-02.04 — DONE; WEB-02.06 — DONE. G0 не требуется: AOI drawing is local and uses the empty canvas.
**Цель:** пользователь включает режим прямоугольника, рисует одну AOI и получает bbox WGS84.
**Scope:** явные controls Start/Finish/Clear; OpenLayers `Draw` interaction with rectangle geometry; vector source/layer for one selected AOI; transform extent into WGS84 and return `[west, south, east, north]`; reject zero-area/invalid geometry; remove Draw interaction immediately after draw completes or mode exits; clear stored feature and bbox; cleanup interaction/layer/source on unmount. No persistence or API calls.
**Тесты:** drawing mode adds one Draw interaction; completing one rectangle emits a correctly ordered WGS84 bbox; drawing interaction is removed after completion; Clear removes geometry and resets bbox; invalid/zero-area geometry is rejected; leaving mode and unmount clean up interactions/listeners.
**Критерии приёмки:** only one AOI is active; bbox order is exactly `[west, south, east, north]`; all four values are finite and bounds are non-empty; interaction is not left active after completion or mode exit; Clear returns to empty state; full frontend CI passes.
**Не входит:** AOI persistence, backend/API, STAC search, imagery, provider adapters, multiple AOIs, polygon/freehand drawing, network calls.
**Результат:** добавлены локальные vector source/layer и Draw interaction с прямоугольной геометрией. После завершения геометрия переводится в WGS84 bbox `[west, south, east, north]`; непустой bbox проверяется на конечность и положительную площадь. Draw interaction удаляется после drawend, отмены режима и cleanup; Clear удаляет feature и сбрасывает bbox.
**Изменённые файлы:** `app/src/components/MapCanvas.vue`, `app/src/components/openLayersMap.ts`, `app/src/components/MapCanvas.spec.ts`.
**Проверки:** tests проверяют порядок bbox, завершение/удаление Draw interaction, clear, отмену и нулевую площадь. Exact-head Frontend build CI run `44359722241` для commit `6223561722c18c079037da171da4f945fadc6c44` — SUCCESS: audit policy, npm audit high threshold, ESLint, Prettier, vue-tsc, Vitest, production build, backend proxy smoke, Compose config/localhost binding, Compose startup and frontend/API smoke.
**Приёмка:** один активный AOI; bbox имеет порядок `[west, south, east, north]`; координаты конечные, площадь ненулевая; Draw interaction снимается после завершения, отмены и unmount; Clear возвращает пустое состояние; полный exact-head frontend CI пройден.
**Ограничения:** ручная проверка в реальном браузере/на физических устройствах не выполнялась. AOI отображается на пустом холсте; нет persistence, API, imagery или base map; G0 остаётся открытым.
**PR:** #36 merged; merge commit `b485dfb429f50292702410bb43d4283cf9c3a8e9`.
**Временная автоматизация:** временный formatter workflow удалён после форматирования тестов.

## WEB-02.08 — search form shell

**Статус:** IN_REVIEW (2026-11-19; PR #41).  
**Зависимости:** WEB-02.02 — DONE; WEB-02.07 — DONE.  
**Goal:** подготовить пользовательские параметры Sentinel-2 L2A поиска и типизированный SearchRequest без сетевого вызова.

### Scope
- Добавить frontend SearchRequest type, точно соответствующий разделу 4 `docs/API_CONTRACTS.md`: bbox WGS84 [west, south, east, north], datetime.from/to UTC, cloud_cover_lte, collections, limit и cursor.
- Добавить панель поиска с датой начала/окончания, максимальной облачностью 0–100 и состоянием текущего AOI.
- Передавать AOI прямоугольника из OpenLayers MapCanvas в SearchPanel.
- Проверять обязательные даты, корректность календарных дат, порядок from <= to, целочисленную облачность 0–100 и наличие непустого AOI.
- По submit выдавать типизированный SearchRequest с коллекцией sentinel-2-l2a, лимитом 20 и cursor=null.
- Сброс очищает даты и возвращает cloud cover к 100%; AOI очищается отдельным действием карты.
- Ясно показывать, что параметры подготовлены, но реальный сетевой поиск пока не подключён.

### Не входит
- HTTP/API запросы, provider adapters, pagination, результаты и карточки сцен.
- Автоматический поиск при перемещении карты.
- Изменения backend или API-контракта.
- Base map, raster assets, RGB и обход G0.

### Тесты
- Валидный ввод создаёт точный SearchRequest с UTC границами суток и текущим bbox.
- Неполные/некорректные даты, обратный диапазон, cloud cover вне 0–100 и отсутствие AOI блокируют submit.
- Reset очищает фильтры, не подменяя AOI.
- MapCanvas передаёт bbox и null при очистке.
- Существующие frontend tests и полный Frontend build CI проходят.

### Критерии приёмки
- [ ] DTO соответствует API_CONTRACTS.md без изменения backend API.
- [ ] AOI отображается в порядке W/S/E/N и используется в запросе.
- [ ] Даты валидны, from не позже to; UTC start/end сформированы детерминированно.
- [ ] Cloud cover ограничен целыми значениями 0–100.
- [ ] Reset восстанавливает пустые даты и cloud cover 100%.
- [ ] Submit выдаёт typed SearchRequest; ни одного сетевого вызова нет.
- [ ] Unit tests, lint, format, typecheck и production build проходят.

### Фактический результат
- Добавлены `SearchRequest` и `SearchPanel.vue` по существующему API/UX контракту.
- MapCanvas передаёт WGS84 AOI bbox в App и панель поиска.
- Реализованы date range, cloud cover 0–100, AOI validation, reset и локальная подготовка typed request.
- Сетевые вызовы и изменения backend не добавлялись.
- **Изменённые файлы:** `app/src/types/catalog.ts`, `app/src/components/SearchPanel.vue`, `app/src/components/SearchPanel.spec.ts`, `app/src/components/MapCanvas.vue`, `app/src/components/MapCanvas.spec.ts`, `app/src/App.vue`, `app/src/App.spec.ts`, `app/src/style.css`, эта карточка и `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`.
- **Проверки:** unit tests добавлены; локальное выполнение в этой среде недоступно. Exact-head Frontend build CI ожидается; критерии DONE пока не подтверждены.
- **PR:** #37 — https://github.com/Helmslay/ForAll/pull/41.
- **Ограничения:** G0 остаётся открытым; каталог, provider, assets и no-VPN доступ не проверялись.

**Приёмка:** код и тесты добавлены; ожидается exact-head CI для подтверждения всех критериев.
