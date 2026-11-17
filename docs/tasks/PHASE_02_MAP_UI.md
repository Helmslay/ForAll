# Phase 02 — карта и UI

Следовать UX_UI_GUIDE.md. Все задачи PLANNED.

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
