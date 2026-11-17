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
