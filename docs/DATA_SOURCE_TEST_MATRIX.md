# Data source test matrix

**Scope:** Sentinel-2 L2A pilot, Perm Krai. Catalog discovery and raster asset access are tracked separately.  
**Rule:** all operational statuses start as `UNKNOWN`; legal/terms review starts as `PENDING`. Change a status only with reproducible evidence, report path and verification date. Public documentation of an endpoint is not evidence of reachability from a Russian backend.

## Candidate catalog endpoints

| Provider | Purpose | Catalog hostname | Catalog endpoint | Catalog auth (documented) | Catalog status from RU | Notes / evidence |
|---|---|---|---|---|---|---|
| Earth Search / Element 84 | STAC catalog and search | `earth-search.aws.element84.com` | `https://earth-search.aws.element84.com/v1/` | Anonymous | PARTIAL PASS (RU VPS: root + collections) | VPS diagnostic 2026-11-20 04:25 UTC: DNS/TCP/TLS/root/collections PASS; HTTP 200 for root and collections; 9 collections. Issue [#58](https://github.com/Helmslay/sentinel-explorer-agent/issues/58). STAC Search and user-side access remain unverified. [Official API documentation](https://earth-search.aws.element84.com/v1/api.html); [Element 84 endpoint reference](https://element84.com/earth-search/examples/) |
| Copernicus Data Space Ecosystem (CDSE) | STAC catalog and search | `stac.dataspace.copernicus.eu` | `https://stac.dataspace.copernicus.eu/v1/` | Anonymous root/collections test | PARTIAL PASS (RU VPS: root + collections) | VPS diagnostic 2026-11-20 04:25 UTC: DNS/TCP/TLS/root/collections PASS; HTTP 200 for root and collections; 10 collections. Issue [#58](https://github.com/Helmslay/sentinel-explorer-agent/issues/58). Search/assets and user-side access remain unverified. [Official STAC documentation](https://documentation.dataspace.copernicus.eu/APIs/STAC.html). The legacy `catalogue.dataspace.copernicus.eu/stac` endpoint is deprecated. |
| Microsoft Planetary Computer | STAC catalog and search | `planetarycomputer.microsoft.com` | `https://planetarycomputer.microsoft.com/api/stac/v1` | Anonymous test | PARTIAL / FAIL (RU VPS) | VPS diagnostic 2026-11-20 04:25 UTC: DNS/TCP/TLS/root PASS (root HTTP 200); collections response exceeded checker size limit (`ResponseTooLarge`), so collections are UNKNOWN and provider check is FAIL. Issue [#58](https://github.com/Helmslay/sentinel-explorer-agent/issues/58). Do not infer Search or asset access. [Official documentation](https://planetarycomputer.microsoft.com/docs/). Asset access may have separate signing/throttling requirements. |

## Raster asset endpoints — deliberately separate from catalogs

| Provider | Purpose | Hostname / endpoint | Auth and URL lifetime | B02 | B03 | B04 | B08 | HTTP Range / COG read | Status |
|---|---|---|---|---|---|---|---|---|---|
| Earth Search / Element 84 | Read Sentinel-2 L2A assets | Not fixed here: obtain actual `assets.*.href` from a test Item; record hostname only after inspection | UNKNOWN; inspect returned href and any signing/expiry behavior | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| CDSE | Read Sentinel-2 L2A assets | Not fixed here: inspect actual Item asset hrefs and official download path | UNKNOWN; determine whether OAuth/token is required and how long URLs remain valid | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Microsoft Planetary Computer | Read Sentinel-2 L2A assets | Not fixed here: inspect actual Item asset hrefs; do not assume catalog hostname is the asset host | UNKNOWN; determine signing/token requirements, expiry and throttling | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Other reviewed source | Catalog and raster assets | Not identified | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## Storage and application path

| Dependency | Purpose | Hostname / endpoint | Status | Evidence required |
|---|---|---|---|---|
| Russian backend → provider catalog | DNS, TCP, TLS, STAC root/collections/search | Per catalog row above | PARTIAL | VPS egress independently reported as RU / AS44112 by two metadata services at 2026-11-20 04:26 UTC (Issue [#60](https://github.com/Helmslay/sentinel-explorer-agent/issues/60)); root/collections outcomes are recorded per provider above. STAC Search is not yet tested from VPS. |
| Russian backend → provider assets | HEAD and GET Range; read real raster window | Per actual Item asset href | UNKNOWN | HTTP status, Content-Range, bytes, GDAL/Rasterio read and timing |
| Backend → Russian object/file storage | Store permitted test output and serve it back | Not selected / not provisioned | UNKNOWN | Write, read, checksum, Range and delete test |
| User in Russia → application | Website, API, preview and download | Not deployed | UNKNOWN | Tests from independent Russian home and mobile networks without VPN |

## Rights and operational review

| Provider | Sentinel-2 L2A coverage for Perm Krai | Caching allowed | Redistribution / user downloads allowed | Attribution / limits | Legal status | Decision |
|---|---|---|---|---|---|---|
| Earth Search / Element 84 | UNKNOWN | PENDING | PENDING | PENDING | PENDING | Candidate only |
| Copernicus Data Space | UNKNOWN | PENDING | PENDING | PENDING | PENDING | Candidate only |
| Microsoft Planetary Computer | UNKNOWN | PENDING | PENDING | PENDING | PENDING | Candidate only |
| Other reviewed source | UNKNOWN | PENDING | PENDING | PENDING | PENDING | Not selected |

## Required test report fields

Provider ID; endpoint category (`catalog` / `asset` / `storage` / `user-app`); hostname without token or signed query; RU server region or RU ISP/region; test timestamp UTC; DNS; TCP; TLS; HTTP status; latency; bytes requested/received; Range status and Content-Range; STAC collection/item if safe; band key and media type; raster read result; checksum; auth and signed-URL expiry behavior; caching/legal status; PASS/FAIL/UNKNOWN; error class; script version; report path.

Never store credentials, access tokens or signed asset query strings in this matrix or reports. Do not infer asset hostnames from catalog hostnames. Never mark a source PASS based only on HTTP 200 from a STAC root or successful search. A band is confirmed only after asset metadata is inspected; a raster read is confirmed only after real bytes are read and the raster is opened.
