# UX-01 — единая мягкая нейтральная палитра

**Статус:** DONE.  
**Зависимости:** LP-01 — DONE; WEB-01.04 — DONE.  
**Основание:** явное требование пользователя от 2026-11-17 убрать зелёный и использовать более мягкие цвета во всём проекте; ADR-011.

## Goal
Привести публичный лендинг и браузерное приложение к единой спокойной холодной палитре без зелёных UI-оттенков.

## Scope
- Обновить CSS лендинга `index.html`.
- Обновить CSS приложения `app/src/style.css`.
- Синхронизировать цветовые роли и правила в `docs/UX_UI_GUIDE.md`.
- Сохранить естественные цвета реальных спутниковых снимков и пользовательских геоданных; не применять тему к raster/vector content.
- Сохранить различимость focus, warning и error states.

## Palette direction
- Background: `#171C26`; deep background: `#111620`.
- Surfaces: `#202735`, `#293445`.
- Text: `#E8EDF5`; muted: `#AAB6C7`.
- Primary: muted blue `#A9C5E4`; secondary: soft lavender `#C1B5D8`.
- Warning: muted sand `#D8C7A4`; error remains muted red.
- No green hue in UI chrome, buttons, icons, badges, gradients or decorative map placeholder.

## Tests and acceptance
- Existing frontend lint, Prettier, typecheck, Vitest and production build pass.
- Landing static checks pass.
- Inspect both stylesheets for remaining green UI colors; no green palette values remain.
- Verify visible keyboard focus and readable text/control contrast; document any contrast limitation rather than claiming unmeasured compliance.
- Responsive rules and GIS map-first layout remain unchanged.

## Non-goals
- Do not change product layout, application behavior, map/data colors or Sentinel functionality.
- Do not add a light theme or theme switcher.

## Result (2026-11-17)
- Лендинг и приложение переведены на единую графитово-сине-серую тему с приглушённым голубым акцентом и лавандовым дополнительным цветом.
- Цветовая гамма декоративной карты лендинга и заглушки приложения изменена; реальные raster/vector data styles не затрагивались.
- В CSS двух интерфейсов не осталось цветов с зелёным hue в диапазоне 65–165° по проверке цветовых литералов.
- Сохранены responsive rules и видимый focus outline.
- **Contrast spot-check** относительно фона `#171C26`: основной текст `#E8EDF5` — 14.52:1; muted `#AAB6C7` — 8.31:1; subtle `#8492A6` — 5.40:1; primary `#A9C5E4` — 9.58:1; secondary `#C1B5D8` — 8.83:1. Эти значения выше WCAG AA порога для обычного текста (4.5:1); это проверка выбранных базовых пар, не полный аудит всех состояний/элементов.
- **CI:** frontend run `44102877694` SUCCESS (lint, format, typecheck, Vitest, production build, dev-server smoke-check); landing run `44102877715` SUCCESS (HTML structure/navigation checks).
- **Изменённые файлы:** `index.html`, `app/src/style.css`, `docs/UX_UI_GUIDE.md`, `docs/DECISIONS.md`, `docs/EXECUTION_PLAN.md`, `docs/STATUS.md`, `docs/tasks/UX_01_SOFT_NEUTRAL_PALETTE.md`.
- **Ограничения:** ручная визуальная проверка в браузерах и на физических мобильных устройствах не проводилась. Формальный полный WCAG audit не выполнялся.
- **PR:** https://github.com/Helmslay/ForAll/pull/11.
