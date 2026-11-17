# Phase 00 — проверка источников и российского доступа

Все задачи PLANNED. Это обязательный gate. Выполнять по одной.

## WEB-00.01 — каталог сетевых зависимостей
**Цель:** список endpoint и hostnames для проверки.
**Зависимости:** нет.
**Контекст:** DATA_ACCESS_RUSSIA.md.
**Scope:** только docs/DATA_SOURCE_TEST_MATRIX.md.
**Шаги:** создать таблицу provider/purpose/hostname/endpoint/auth/assets/rights/status; добавить Earth Search, CDSE, Planetary Computer как кандидатов; отделить catalog от asset endpoints; выставить UNKNOWN.
**Приёмка:** нет неподтверждённых PASS, каталог и файлы имеют отдельные статусы.

## WEB-00.02 — STAC root/collections checker
**Цель:** скрипт проверяет STAC API без credentials.
**Зависимости:** WEB-00.01.
**Scope:** один script + короткая инструкция.
**Шаги:** endpoint только из allowlist/config; DNS/TLS/status/timeout; STAC root и collections; latency; безопасный output.
**Тесты:** mock server для 200, timeout, DNS/TLS error, invalid JSON.
**Приёмка:** корректные exit codes; секретные заголовки не печатаются.

## WEB-00.03 — STAC search для Пермского края
**Цель:** реальный поиск Sentinel-2 L2A.
**Зависимости:** WEB-00.02.
**Шаги:** bbox/datetime из test config; search; вывести item id, collection, datetime, cloud cover, asset keys; отличить no results от network error; не сохранять signed href.
**Приёмка:** real Item или причина отсутствия записана; no results не считается network failure.

## WEB-00.04 — sanitized Item fixture
**Цель:** fixture для unit tests.
**Зависимости:** WEB-00.03.
**Шаги:** удалить токены/signed query; сохранить properties/geometry/assets shape; временные href заменить placeholder; записать источник и дату; fixture не должен инициировать network access.
**Приёмка:** тестовый JSON без секретов и пригоден для offline tests.

## WEB-00.05 — проверить B02/B03/B04/B08
**Цель:** проверить фактические band assets.
**Зависимости:** WEB-00.03.
**Шаги:** сопоставлять band по metadata, не угадывать по URL; вывести status/media type/resolution/host для каждого band; missing metadata помечать unknown.
**Приёмка:** каждый band имеет явный status и evidence.

## WEB-00.06 — HTTP Range и COG read
**Цель:** доказать получение реальных байтов с российского backend.
**Зависимости:** WEB-00.05.
**Шаги:** получить asset только из test item; HEAD/GET Range bytes=0-16383; проверить status, Content-Range, size; Rasterio/GDAL open; прочитать небольшое окно; замерить время; скрыть signed URL.
**Приёмка:** окно прочитано для каждого band или источник FAIL. STAC 200 не считается raster success.

## WEB-00.07 — preview из реальных пикселей
**Цель:** проверить RGB на реальной сцене.
**Зависимости:** WEB-00.06.
**Шаги:** AOI window; зафиксированная RGB комбинация; nodata; scale/offset только по metadata; PNG + JSON params; проверить размеры и не-пустое изображение.
**Приёмка:** известно происхождение каждого канала и реальный scene item.

## WEB-00.08 — российское хранилище smoke test
**Цель:** проверить выбранное storage.
**Зависимости:** WEB-00.06; тестовые доступы.
**Шаги:** создать маленький файл; записать; прочитать; сравнить checksum; проверить Range; удалить временный объект.
**Приёмка:** read/write/checksum pass; endpoint и ограничения описаны.

## WEB-00.09 — инструкция тестирования из российских сетей
**Цель:** повторяемая проверка без VPN.
**Зависимости:** WEB-00.01—WEB-00.08.
**Scope:** docs/RUSSIA_NETWORK_RUNBOOK.md.
**Шаги:** отдельно сервер РФ, домашняя сеть, мобильная сеть; проверить DNS/TLS/app/search/asset/RGB/download; добавить report template; не собирать избыточные персональные данные.
**Приёмка:** тест может повторить другой человек.

## WEB-00.10 — provider decision
**Цель:** выбрать primary/fallback.
**Зависимости:** предыдущие задачи.
**Шаги:** собрать сетевые и raster results; проверить права на использование/кэш/redistribution; оценить покрытие; зафиксировать primary/fallback или BLOCKED; указать дату повторной проверки.
**Приёмка:** primary не назначен только по STAC root; доказан raster read и reviewed terms.
