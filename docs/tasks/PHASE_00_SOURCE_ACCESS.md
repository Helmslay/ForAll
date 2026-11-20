# Phase 00 — проверка источников и российского доступа

WEB-00.01 — DONE; WEB-00.02 — DONE; WEB-00.03 — IN_PROGRESS; WEB-00.04—WEB-00.10 — PLANNED. Это обязательный gate. Выполнять по одной.

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

## WEB-00.03 — тестовый STAC Search для Березников

**Статус:** IN_PROGRESS  
**Зависимости:** WEB-00.02 — DONE.  
**Цель:** безопасно выполнить настоящий STAC Search по согласованной тестовой территории и периоду для трёх каталогов-кандидатов. Это диагностический инструмент, не provider adapter и не часть production API.

### Согласованные параметры
- **AOI:** центр около Березников, Пермский край, WGS84 (longitude 56.8204, latitude 59.4091), радиус 100 км. Для STAC Search AOI передаётся как GeoJSON Polygon, аппроксимирующий круг; геометрия строится локально без внешнего геокодирования.
- **Период:** последние 30 календарных суток относительно UTC-времени запуска; интервал передаётся в STAC как UTC ISO-8601.
- **Данные:** Sentinel-2 Level-2A. Коллекции обнаруживаются из ответа `/collections` по идентификаторам/описаниям, относящимся к Sentinel-2 L2A; не угадывать ID коллекции и не запрашивать весь каталог без фильтра коллекции.
- **Каталоги:** только существующий allowlist `earth-search`, `cdse`, `planetary-computer` из `tools/check_stac.py`.
- **Сеть для основного пользовательского испытания:** Windows-компьютер пользователя в России, VPN и proxy отключены. GitHub-hosted runner не является доказательством российской доступности.

### Scope
1. Добавить STAC Search в существующий диагностический tool, не меняя его allowlist и не добавляя credentials.
2. Получить коллекции и определить Sentinel-2 L2A collection IDs по фактическим метаданным каждого каталога.
3. Выполнить ограниченный поиск по AOI, периоду и найденным коллекциям; обработать pagination безопасно с ограничением числа страниц/items/размера ответа.
4. Сформировать JSON-отчёт: provider, hostname, AOI параметры, временной интервал, collection IDs, число найденных Items, безопасные поля Item (ID, collection, datetime, cloud cover при наличии), latency, error stage/class. Не включать asset href, query strings, токены, заголовки авторизации и signed URLs.
5. Добавить offline mock tests для успешного поиска, пустого результата, ошибок HTTP/timeout/invalid schema, неизвестной коллекции и pagination/лимитов.
6. Обновить README и матрицу тестирования только по фактически подтверждённым результатам.

### Не входит
- Получение raster assets и проверка B02/B03/B04/B08.
- HTTP Range, COG/GDAL/Rasterio, preview, скачивание и RGB.
- Проверка российского backend/server-to-upstream маршрута.
- Юридическое заключение о лицензиях/кэшировании/redistribution.
- Выбор primary provider и любые production adapters.

### План выполнения
1. Реализовать ограниченный STAC Search в allowlist checker с безопасным отчётом.
2. Добавить mock tests, включая запрет утечки asset URLs и корректную обработку ошибок/лимитов.
3. Запустить offline unit tests и compile/help checks локально.
4. Передать пользователю одну команду для реального запуска из PowerShell в российской сети без VPN/proxy.
5. По полученному отчёту обновить `docs/DATA_SOURCE_TEST_MATRIX.md` и критерии задачи; не считать задачу DONE, пока реальный Search не подтверждён.

### Критерии приёмки
- [ ] Search идёт только на три allowlisted STAC hostnames; произвольные URL и внешние redirects заблокированы.
- [ ] AOI соответствует согласованному центру и радиусу 100 км; даты — последние 30 суток UTC на момент запуска.
- [ ] Sentinel-2 L2A collection IDs подтверждены ответом каталога, а не захардкожены по предположению.
- [ ] Отчёт содержит реальные Item IDs/даты/collection/cloud cover (если доступны), число результатов и безопасные ошибки.
- [ ] Ни один asset href, signed URL, токен или auth header не попадает в отчёт.
- [ ] Offline tests и compile/help checks проходят.
- [ ] Получен воспроизводимый реальный Search report с пользовательского компьютера в России при выключенных VPN/proxy для каждого доступного каталога; недоступность остальных зафиксирована как FAIL/UNKNOWN, не маскируется.
- [ ] Матрица обновлена по фактическим результатам; отсутствие asset/raster/legal проверки явно сохранено.

**Промежуточный результат (2026-11-18):**
- Задача формализована по ранее согласованным параметрам. Предварительный root/collections baseline с компьютера пользователя в России без VPN: Planetary Computer PASS; Earth Search root PASS / collections timeout; CDSE RemoteDisconnected. Это не является STAC Search.
- Добавлен диагностический `tools/search_stac.py`: AOI polygon 64 vertices, rolling UTC 30-day window, L2A collection discovery из фактического `/collections`, STAC POST Search, ограничение 3 страниц × 100 Items, same-host HTTPS pagination/redirect checks и отчёт без asset hrefs.
- Добавлен `tools/test_search_stac.py` с тестами геометрии, обнаружения коллекций, safe Item summary, пустого поиска, HTTP/timeout/schema errors, внешнего next-link rejection и pagination cap.
- Обновлён `tools/README.md` с командами и ограничениями.
- **Изменённые файлы:** `tools/search_stac.py`, `tools/test_search_stac.py`, `tools/README.md`, эта карточка и `docs/EXECUTION_PLAN.md`.
- **Проверки:** автоматические тесты и py_compile ещё не запускались: в текущей рабочей среде нет сетевого доступа к GitHub для получения checkout репозитория. Требуется запуск пользователем из локальной копии: `python -m unittest discover -s tools -p 'test_*.py' -v`, затем `python -m py_compile tools/search_stac.py tools/test_search_stac.py`.
- **Следующий шаг:** получить результат offline tests; исправить ошибки, если будут. После этого запустить `python tools/search_stac.py --all` на Windows-компьютере в России при выключенных VPN/proxy и сохранить фактический отчёт.
- **Статус приёмки:** реализация добавлена, но не проверена исполнением; реальные STAC Search results ещё не получены.



### Дополнительное hardening WEB-00.03 — 2026-11-18

- В `tools/search_stac.py` добавлена отдельная redirect policy: только HTTPS на точный allowlisted hostname, стандартный порт 443, без userinfo.
- Pagination теперь проверяет тип `links`, требует object body для POST next-link и отклоняет страницу, если сервер вернул больше 100 Items вопреки запрошенному лимиту.
- В `tools/test_search_stac.py` добавлены четыре регрессионных теста на redirect port/userinfo, превышение лимита Items, некорректный links schema и некорректное POST body.
- Проверки в изолированной Python-среде по коду, полученному из ветки: 16 тестов PASS; compile для `search_stac.py` и `test_search_stac.py` PASS. Для изолированного запуска импорт `check_stac` предоставлялся минимальным тестовым stub; полный запуск из checkout репозитория ещё не подтверждён.
- Реальные запросы к провайдерам не выполнялись. Российский STAC Search без VPN/proxy остаётся обязательным пользовательским испытанием.
- Статус WEB-00.03 остаётся IN_PROGRESS; критерии приёмки по реальным Item и пользовательской сети не закрыты.

- Чтобы офлайн-проверки выполнялись на каждом PR, добавлен GitHub-hosted workflow `.github/workflows/tools-offline-tests.yml` (Ubuntu, Python 3.12, только offline suite и py_compile); Windows workflow также компилирует STAC Search script/tests. Workflow не обращается к провайдерам. Результат CI для текущего PR ожидается отдельно.


### PR #24 — hardening и CI (2026-11-18)

- PR: https://github.com/Helmslay/ForAll/pull/24 — merged.
- Merge commit: `2159f17756883c2f51222e89012c5d285081d749`.
- Exact PR head: `fbedcb76319d4bc53fe9d61adc3cb629e549af76`.
- GitHub Actions `Tools offline tests`, run `44310541026` на exact PR head: SUCCESS; полный набор `tools/test_*.py` — 23 tests PASS; `py_compile` для обоих STAC checker/search модулей и тестов — PASS.
- Изменения: строгая same-host HTTPS redirect policy для STAC Search; validation pagination schema/POST body; enforcement 100 Items per page; четыре регрессионных теста; hosted Ubuntu offline CI; расширена Windows compile-проверка.
- Подтверждено: offline implementation/tests/compile. Не подтверждено: реальные provider Search results из российской сети без VPN/proxy, Sentinel-2 asset access, raster reads и licensing.
- WEB-00.03 остаётся IN_PROGRESS до реального пользовательского Search. Следующее действие: выполнить `python tools/search_stac.py --all` на Windows в России при выключенных VPN и proxy и передать JSON-отчёт без редактирования asset href (их скрипт не выводит).

- Дополнительная проверка после merge: main push workflow `Tools offline tests`, run `44310622444`, SUCCESS; 23 tests и py_compile выполнены на merge commit. `Local Windows tests` run `44310622370` остаётся QUEUED (self-hosted runner); его результат не заявляется как PASS.


### Российский VPS: catalog connectivity baseline — 2026-11-20

- VPS egress identity was checked through two independent metadata services: both reported country `RU` and ASN `AS44112`; country and ASN agreement PASS. The report does not independently establish the physical city or test end-user networks. Evidence: [sentinel-explorer-agent Issue #60](https://github.com/Helmslay/sentinel-explorer-agent/issues/60).
- Earth Search: DNS, TCP, TLS, STAC root and collections PASS; root/collections HTTP 200; 9 collections.
- CDSE: DNS, TCP, TLS, STAC root and collections PASS; root/collections HTTP 200; 10 collections.
- Planetary Computer: DNS, TCP, TLS and root PASS (HTTP 200); collections response exceeded the diagnostic response-size limit (`ResponseTooLarge`), so collections remain UNKNOWN and the provider check is FAIL.
- Evidence for provider checks: [sentinel-explorer-agent Issue #58](https://github.com/Helmslay/sentinel-explorer-agent/issues/58), run 2026-11-20 04:25 UTC.
- **Interpretation:** this establishes only partial catalog transport/reachability from the Russian VPS. No STAC Search, real Item, asset metadata, B02/B03/B04/B08 bytes, HTTP Range, COG read, preview or storage operation was performed. It does not establish access from Russian home/mobile networks without VPN. WEB-00.03 remains IN_PROGRESS.
