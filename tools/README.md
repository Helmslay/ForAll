# STAC connectivity checker

The checker probes only the three configured public Sentinel-2 STAC catalog endpoints. It does not accept arbitrary URLs, credentials or signed asset links. It checks DNS, TCP, TLS, the STAC root document and the collections response. It does **not** test Sentinel-2 raster assets, HTTP Range, GDAL/Rasterio reads, Russian-network reachability or legal rights; those are later G0 tasks.

Requires Python 3.10+ and the standard library only.

```bash
# Check one catalog
python tools/check_stac.py --provider cdse

# Check all configured catalogs
python tools/check_stac.py --all

# Run offline mock-server tests (no provider traffic)
python -m unittest discover -s tools -p 'test_*.py' -v
```

Exit codes: `0` all requested checks passed; `1` at least one connectivity/HTTP/STAC check failed; `2` invalid command-line arguments. Reports contain hostnames and status/latency only; do not add credentials or signed URLs.

## CI offline tests

The offline tools suite also runs on a GitHub-hosted Ubuntu runner for pull requests and pushes to `main` via `.github/workflows/tools-offline-tests.yml`. It does not contact external STAC providers. The self-hosted Windows workflow remains an additional check on the user's Windows environment and is restricted to `main`.

## Автоматический запуск тестов на Windows-компьютере

Для запуска тестов на собственном компьютере используется self-hosted GitHub Actions Runner с меткой `sentinel-local`.

1. В репозитории откройте **Settings → Actions → Runners → New self-hosted runner**.
2. Выберите **Windows / x64** и выполните одноразовые команды, которые покажет GitHub. При конфигурации добавьте метку `sentinel-local`.
3. Рекомендуется установить runner как службу под отдельной стандартной учётной записью Windows с минимальными правами. Не используйте личную учётную запись с доступом к документам, браузерным профилям, SSH-ключам и секретам.
4. В **Actions → Local Windows tests** запустите workflow на ветке `main`. В дальнейшем он автоматически запускается после изменений в `tools/**` на `main`.

**Безопасность:** репозиторий публичный, поэтому workflow намеренно не запускается на Pull Request и принимает задания только для `main`. Не добавляйте триггеры для внешних PR/fork к workflow, который использует этот компьютер. Временный registration token не публикуйте и никому не отправляйте.

Workflow автоматически выбирает Python 3.12, запускает offline unit tests и проверку компиляции. Он не обращается к STAC-провайдерам и не подтверждает доступность каталогов или снимков из российской сети. Для реальных сетевых проверок будет отдельный контролируемый этап.

## Sentinel-2 L2A STAC Search diagnostic

The bounded pilot search is implemented separately from the root/collections checker. It reuses the same fixed provider allowlist and does not accept endpoint overrides or credentials.

Run from the repository root:

```bash
# Search all three catalogs
python tools/search_stac.py --all

# Search one catalog
python tools/search_stac.py --provider planetary-computer
```

The AOI is a 100 km radius around Berezniki (WGS84 center: longitude 56.8204, latitude 59.4091), represented as a 64-vertex GeoJSON polygon. The time window is the 30 days preceding the run, in UTC. Sentinel-2 L2A collection IDs are discovered from each catalog's collections metadata; they are not assumed to be identical.

The report contains provider/hostname, AOI and time window, discovered collection IDs, Item IDs, collection IDs, acquisition datetimes, cloud cover when supplied, result count, page count, latency and safe error classes. It deliberately omits Item asset hrefs and all URL query strings, tokens and authorization headers. Pagination is limited to three pages of at most 100 items each; next links and redirects must remain on the same allowlisted HTTPS hostname.

An empty search is a successful query with zero results. A provider failure is reported independently and causes exit code 1; invalid CLI arguments return 2. This diagnostic does not test raster assets, HTTP Range/COG reads, Russian backend access or data licensing. A successful search from one user's Russian ISP is evidence only for that specific user-network path.
