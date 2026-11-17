# Phase 00 — проверка источников и российского доступа

WEB-00.01 — DONE; WEB-00.02 — DONE; WEB-00.03—WEB-00.10 — PLANNED. Это обязательный gate. Выполнять по одной.

## WEB-00.01 — каталог сетевых зависимостей
**Цель:** список endpoint и hostnames для проверки.
**Зависимости:** нет.
**Контекст:** DATA_ACCESS_RUSSIA.md.
**Scope:** только docs/DATA_SOURCE_TEST_MATRIX.md.
**Шаги:** создать таблицу provider/purpose/hostname/endpoint/auth/assets/rights/status; добавить Earth Search, CDSE, Planetary Computer как кандидатов; отделить catalog от asset endpoints; выставить UNKNOWN.
**Приёмка:** нет неподтверждённых PASS, каталог и файлы имеют отдельные статусы. Подтверждено проверкой матрицы.

**Результат выполнения (2026-11-17):**
- Добавлены документированные STAC endpoints и hostnames для Earth Search, CDSE и Microsoft Planetary Computer.
- Каталог и raster assets вынесены в отдельные таблицы; asset hostnames оставлены UNKNOWN до получения реального STAC Item.
- Для B02/B03/B04/B08 заведены независимые статусы; покрытие, Range/COG, российская доступность и юридические условия не объявлены подтверждёнными.
- Добавлены сетевые зависимости backend → catalog/assets/storage и user → app.
- **Изменённые файлы:** `docs/DATA_SOURCE_TEST_MATRIX.md`, `docs/EXECUTION_PLAN.md`, `docs/tasks/PHASE_00_SOURCE_ACCESS.md`.
- **Проверки:** повторное чтение файлов из GitHub; проверены наличие трёх catalog hostnames, разделение catalog/assets, четыре band-колонки, сохранение UNKNOWN и отсутствие неподтверждённых PASS. Все проверки документации прошли.
- **Ограничение:** сетевые запросы из российского backend, получение реального Item/assets и проверка лицензий в рамках этой задачи не выполнялись; это последующие задачи WEB-00.02—WEB-00.10.

## WEB-00.02 — STAC root/collections checker
**Цель:** скрипт проверяет STAC API без credentials.
**Зависимости:** WEB-00.01.
**Scope:** один script + короткая инструкция.
**Шаги:** endpoint только из allowlist/config; DNS/TLS/status/timeout; STAC root и collections; latency; безопасный output.
**Тесты:** mock server для 200, timeout, DNS/TLS error, invalid JSON.
**Приёмка:** корректные exit codes; секретные заголовки не печатаются.

**Результат выполнения (2026-11-17):**
- Добавлен `tools/check_stac.py`: проверка DNS, TCP, TLS, STAC root и collections для трёх заранее заданных Sentinel-2 каталогов (Earth Search, CDSE, Microsoft Planetary Computer).
- Endpoint нельзя передать через CLI; произвольные hostnames и внешние redirect блокируются. Проверка не использует credentials и не выводит response body, query strings или signed URLs.
- Отчёт содержит hostname, стадии PASS/FAIL, HTTP status, latency и безопасный класс ошибки.
- Добавлены offline mock-server tests и инструкция запуска.
- **Изменённые файлы:** `tools/check_stac.py`, `tools/test_check_stac.py`, `tools/README.md`.
- **Проверки:** `python -m unittest discover -s tools -p 'test_*.py' -v` — 7 tests PASS; `python -m py_compile tools/check_stac.py tools/test_check_stac.py` — PASS; `python tools/check_stac.py --help` — PASS.
- **Приёмка:** allowlist, DNS/TCP/TLS, STAC root/collections, latency, безопасный вывод и exit codes 0/1/2 покрыты реализацией и тестами.
- **Ограничения:** реальные запросы к провайдерам не запускались; российская доступность, реальный STAC search, Sentinel-2 assets, HTTP Range/COG, четыре канала и лицензии не проверялись. Успех этого checker не является доказательством доступности данных из России.
