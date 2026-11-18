# Phase 02 — карта и UI

Следовать UX_UI_GUIDE.md. WEB-02.01 — BLOCKED; WEB-02.02—WEB-02.08 — PLANNED.

## WEB-02.01 — CSS design tokens
Зависимость: WEB-01.04. Один CSS token file: background/surfaces/text/primary/warning/error/spacing/radius/type. Проверить контраст и prefers-reduced-motion. Приёмка: компоненты используют tokens.

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


### WEB-02.01 — progress (2026-11-18)

- Проверены существующие `app/src/style.css` и `docs/UX_UI_GUIDE.md`: палитра уже соответствует ADR-011 и секции 8 UX guide, но значительная часть цветов/типографики/отступов оставалась hardcoded.
- В `app/src/style.css` введены semantic tokens для фонов, поверхностей, текста, границ, primary/secondary/info/warning/error, RGB alpha channels, spacing, radius и typography.
- Существующие правила переведены на tokens без изменения согласованных значений палитры; добавлен общий `:focus-visible` для ссылок и интерактивных элементов. `prefers-reduced-motion` сохранён.
- Контраст токенов на background/surface проверен по WCAG formula: text 14.52/12.73, muted 8.31/7.29, primary 9.58/8.41, info 9.57/8.39, warning 10.26/9.00, error 8.08/7.08; subtle 5.40/4.73 (background/surface соответственно). Все превышают 4.5:1.
- Полный frontend CI ещё не завершён; задача не DONE до успешных exact-head checks.
- G0 остаётся открытым; изменения не подключают карту, provider или внешние данные.

- **CI blocker:** exact-head Frontend build run `44311648232` for `d5aaba2a44935f97d0a90ebed936762070e81215` failed at `npm audit --audit-level=high` before lint/format/typecheck/unit/build steps. Audit reported 13 advisories (7 high, 6 moderate), including high `picomatch` through Vite/Vue tooling. No CSS-related failure was reached. Do not bypass audit or use `npm audit fix --force`; WEB-02.01 is BLOCKED pending a separately reviewed dependency remediation and rerun of exact-head frontend CI.
