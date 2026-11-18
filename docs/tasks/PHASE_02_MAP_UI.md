# Phase 02 — карта и UI

Следовать UX_UI_GUIDE.md. WEB-02.01 — DONE; WEB-02.02 — READY; WEB-02.03—WEB-02.08 — PLANNED.

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

## WEB-02.03 — responsive panels
Зависимость: WEB-02.02. Desktop side panel; tablet drawer; mobile bottom sheet. Никаких hover-only controls. Проверить narrow viewport и touch. Приёмка: основные действия доступны на телефоне.

## WEB-02.04 — OpenLayers lifecycle
Зависимость: WEB-02.02. Один map component/composable: create on mount, dispose listeners/map on unmount, resize observer. Тест mount/unmount без console errors и утечек.

## WEB-02.05 — base map provider abstraction
Зависимость: WEB-02.04 и сетевой gate для источника подложки. URL не хардкодить в component; attribution/license; tile error state. Приёмка: provider заменяем и проверен из РФ.

## WEB-02.06 — cursor coordinates/scale
Зависимость: WEB-02.04. Координаты WGS84 и масштаб/разрешение; корректный lon/lat order; empty state вне карты. Тест известной координаты.

## WEB-02.07 — AOI rectangle draw/clear
Зависимость: WEB-02.04. Rectangle interaction, geometry and WGS84 bbox, clear, validate non-empty area, remove interaction after mode exits. Приёмка: bbox имеет [west,south,east,north].

## WEB-02.08 — search form shell
Зависимости: WEB-02.02, WEB-02.07. Date range/cloud/AOI controls, validation, reset, typed SearchRequest. На этом шаге сетевого вызова нет.
