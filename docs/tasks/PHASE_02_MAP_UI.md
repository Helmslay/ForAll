# Phase 02 — карта и UI

Следовать UX_UI_GUIDE.md. WEB-02.01—WEB-02.03 — DONE; WEB-02.04 — READY; WEB-02.05—WEB-02.08 — PLANNED.

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

**Статус:** READY (2026-11-18).
**Зависимости:** WEB-02.02 — DONE; WEB-02.03 — DONE.
**Цель:** заменить карту-заглушку на пустой OpenLayers canvas и обеспечить предсказуемый жизненный цикл экземпляра карты.
**Scope:**
- Добавить закреплённую runtime-зависимость `ol` и синхронизировать `app/package-lock.json`.
- Создать один компонент `app/src/components/MapCanvas.vue`, который владеет одним экземпляром OpenLayers Map.
- Создавать карту после mount на DOM target; использовать минимальный View без реальных данных.
- Наблюдать за размером контейнера через `ResizeObserver` и вызывать обновление размера карты при изменении.
- На unmount отключать ResizeObserver, отсоединять target и освобождать экземпляр карты; все добавленные в рамках компонента OL event keys (если появятся) снимать.
- Подключить компонент в существующий workspace, сохранив responsive shell и доступное описание состояния.
**Входные контракты и модули:** отдельного backend/API контракта нет; DOM target — внутренний элемент компонента. Затрагиваются `app/package.json`, `app/package-lock.json`, `app/src/App.vue`, `app/src/style.css`, новый `app/src/components/MapCanvas.vue` и тест компонента.
**Тесты:** Vitest/jsdom уже настроен. Замокать OpenLayers Map и ResizeObserver; проверить создание ровно одного экземпляра, вызов updateSize при resize, disconnect observer, detach target и dispose при unmount. Проверить отсутствие console errors. Полный frontend CI: audit policy/audit, lint, format, typecheck, unit tests, production build и существующие proxy/Compose smoke checks.
**Критерии приёмки:**
1. В workspace смонтирован OpenLayers map target; компонент создаёт ровно один экземпляр карты.
2. Изменение размера контейнера вызывает updateSize.
3. После unmount observer отключён, target отсоединён, карта disposed; повторный mount создаёт новый независимый экземпляр.
4. Тесты lifecycle проходят без console errors; полный frontend CI проходит.
5. В production-коде нет URL базовой карты, tile layer, imagery, STAC или provider-запросов.
**Не входит:** выбор/подключение базовой карты, attribution провайдера, Sentinel imagery, координаты/масштаб, AOI interactions, backend/API и сетевые запросы. G0 остаётся открытым.
**Definition of Ready:** зависимости DONE; target и frontend test environment существуют; затрагиваемые модули и тесты перечислены; acceptance criteria измеримы; задача ограничена одним map component и подключением в shell.

## WEB-02.05 — base map provider abstraction
Зависимость: WEB-02.04 и сетевой gate для источника подложки. URL не хардкодить в component; attribution/license; tile error state. Приёмка: provider заменяем и проверен из РФ.

## WEB-02.06 — cursor coordinates/scale
Зависимость: WEB-02.04. Координаты WGS84 и масштаб/разрешение; корректный lon/lat order; empty state вне карты. Тест известной координаты.

## WEB-02.07 — AOI rectangle draw/clear
Зависимость: WEB-02.04. Rectangle interaction, geometry and WGS84 bbox, clear, validate non-empty area, remove interaction after mode exits. Приёмка: bbox имеет [west,south,east,north].

## WEB-02.08 — search form shell
Зависимости: WEB-02.02, WEB-02.07. Date range/cloud/AOI controls, validation, reset, typed SearchRequest. На этом шаге сетевого вызова нет.
