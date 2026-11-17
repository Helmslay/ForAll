# Data source test matrix

Initial status of every source is UNKNOWN. Change only with reproducible evidence, report path and date.

| Provider | Catalog from RU backend | L2A pilot coverage | B02/B03/B04/B08 assets | Range/COG read | Terms reviewed | Decision |
|---|---|---|---|---|---|---|
| Earth Search / Element 84 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | PENDING | Candidate |
| Copernicus Data Space | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | PENDING | Candidate |
| Microsoft Planetary Computer | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | PENDING | Candidate |
| Other reviewed source | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | PENDING | Not selected |

## Required report fields
provider id; endpoint category; hostname without token/query secret; RU server region or RU ISP/region; test timestamp UTC; DNS; TLS; HTTP status; latency; bytes requested/received; Range status/Content-Range; STAC collection/item if safe; band key/media type; raster read result; checksum; caching/legal status; PASS/FAIL/UNKNOWN; error class; script version.

Never mark a source PASS based only on HTTP 200 from the STAC root.
