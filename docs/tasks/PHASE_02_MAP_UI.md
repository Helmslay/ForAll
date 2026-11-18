# Phase 02 — карта и UI

Следовать UX_UI_GUIDE.md. WEB-02.01—WEB-02.04 — DONE; WEB-02.05 — BLOCKED by G0; WEB-02.06 — DONE; WEB-02.07—WEB-02.08 — PLANNED.

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

## WEB-02.07 — AOI rectangle draw/clear
Зависимость: WEB-02.04. Rectangle interaction, geometry and WGS84 bbox, clear, validate non-empty area, remove interaction after mode exits. Приёмка: bbox имеет [west,south,east,north].

## WEB-02.08 — search form shell
Зависимости: WEB-02.02, WEB-02.07. Date range/cloud/AOI controls, validation, reset, typed SearchRequest. На этом шаге сетевого вызова нет.
