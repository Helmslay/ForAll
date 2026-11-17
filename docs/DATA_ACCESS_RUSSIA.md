# Data access and Russia connectivity plan

## 1. Статус
Доступность приложения, каталога и исходных файлов Sentinel-2 из России на момент создания документа НЕ ПОДТВЕРЖДЕНА. Это критический открытый риск и первый технический gate.

Размещение сайта в российском дата-центре решает только путь User → App. Upstream каталог и файлы могут быть недоступны самому серверу.

## 2. Четыре независимых пути
A. User → App: DNS, HTTPS, HTML/JS/CSS, API.
B. Backend RU → Catalog: STAC root/collections/search, авторизация.
C. Backend RU → Assets: B02/B03/B04/B08, HTTP Range, COG read, скорость и полная загрузка.
D. Backend RU → Storage RU: запись, чтение, Range, checksum и выдача пользователю.

Успех A не доказывает B/C. Успех STAC search не доказывает получение пикселей.

## 3. Кандидаты, не гарантированные источники
- Earth Search / Element 84 STAC.
- Copernicus Data Space Ecosystem.
- Microsoft Planetary Computer.
- Иные официальные/открытые/коммерческие источники после проверки прав, покрытия и российского сетевого пути.

Ссылки для старта:
- STAC API specification: https://api.stacspec.org/
- Earth Search: https://earth-search.aws.element84.com/v1/
- Earth Search code/docs: https://github.com/Element84/earth-search
- Copernicus Data Space: https://dataspace.copernicus.eu/
- CDSE docs: https://documentation.dataspace.copernicus.eu/
- Microsoft Planetary Computer: https://planetarycomputer.microsoft.com/docs/
- COG: https://www.cogeo.org/

Ссылки не являются доказательством доступности из РФ.

## 4. Тест для каждого provider с российского backend
1. DNS resolve.
2. TCP connect.
3. TLS handshake и сертификат.
4. STAC root/collections.
5. Поиск по тестовому bbox Пермского края и периоду.
6. Получить реальный item.
7. Проверить реальные assets B02/B03/B04/B08.
8. HEAD/GET Range bytes=0-16383 для каждого asset.
9. Проверить status, Content-Range, длину и валидность байтов.
10. Открыть файл через GDAL/Rasterio.
11. Прочитать реальное небольшое окно.
12. Построить тестовый preview.
13. Измерить latency и throughput с размером sample.
14. Проверить истечение/обновление временной ссылки, если используется.
15. Сохранить безопасный отчёт без токенов и signed URL.

HTTP 200 от STAC root не равен успешному raster test.

## 5. Тест пользовательского доступа
После staging в России проверить минимум:
- фиксированный домашний провайдер;
- мобильный оператор;
- желательно ещё один независимый регион/провайдер.

VPN/proxy выключены, чистый браузер. Проверить открытие сайта, API, реальный поиск, открытие RGB, смену каналов, экспорт, checksum и повторное открытие через cache. Отдельно протестировать поведение при временной недоступности upstream.

Отчёт содержит дату, версию приложения, браузер, оператор/регион в неперсональном виде, результаты DNS/TLS/API/asset/tile/download.

## 6. Рекомендуемая схема
Браузер → домен приложения в РФ → backend в РФ → разрешённый upstream и/или российское хранилище.

Браузер не получает прямые upstream COG URL как обязательную production-зависимость. Backend проверяет данные, применяет разрешённую авторизацию, кэширует допустимые производные/исходные материалы и отдаёт свой API.

## 7. Кэширование и права
До хранения/распространения проверить:
- условия использования;
- можно ли кэшировать и на какой срок;
- можно ли отдавать полученные файлы третьим лицам;
- требования атрибуции;
- региональные ограничения;
- удаление/обновление материалов.

Не обходить авторизацию, геоблокировки, санкционные и договорные ограничения. Если условия не разрешают передачу или кэширование — не строить прокси для обхода; искать легальный альтернативный источник или согласованный способ доступа.

## 8. Деградация
- provider unavailable: пометить источник недоступным;
- partial failure: вернуть успешные результаты с partial status;
- asset unavailable: не обещать preview/download;
- cached asset: разрешить доступ в пределах срока и прав хранения;
- no upstream + no cache: понятная ошибка, никаких fake images;
- storage unavailable: экспорт не считается готовым до проверки записи и checksum.

## 9. Решение по provider
В DATA_SOURCE_TEST_MATRIX.md заполнить:
legal_status, catalog_access_ru, assets_access_ru, range_support, band_coverage, l2a_coverage, speed, auth, caching_allowed, redistribution_allowed, last_verified_at, report path.

Primary provider выбирается только при legal_status=reviewed и успешных сетевых/raster checks.

## 10. Gate для фразы «без VPN в России»
Необходимо:
- frontend/API/storage размещены в РФ;
- проверены минимум две независимые российские сети, предпочтительно три;
- реальный поиск;
- чтение всех четырёх channels;
- реальный RGB;
- скачивание и checksum;
- повторный запуск после очистки browser cache;
- протокол с датой и версиями.

Тест только с одного российского VPS подтверждает серверный исходящий доступ, но не доступ всех пользователей России.
