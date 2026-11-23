import type { AOIBbox } from '../components/openLayersMap'

export type SearchRequest = {
  bbox: [west: number, south: number, east: number, north: number]
  datetime: {
    from: string
    to: string
  }
  cloud_cover_lte?: number | null
  collections: string[]
  providers?: string[] | null
  limit: number
  cursor: string | null
}

export type Scene = {
  key: string
  provider: string
  collection: string
  item_id: string
  acquired_at: string
  platform: string | null
  cloud_cover: number | null
  bbox: [west: number, south: number, east: number, north: number] | null
  geometry: Record<string, unknown> | null
  available_bands: ('B02' | 'B03' | 'B04' | 'B08')[]
  preview_available: boolean
  resolution?: number | null
  crs?: string | null
  nodata?: number | null
  scale?: number | null
  offset?: number | null
}

export type ProviderStatus = {
  id: string
  status: 'success' | 'partial' | 'unavailable'
  last_checked?: string | null
  reason?: string | null
}

export type SearchResponse = {
  items: Scene[]
  next_cursor: string | null
  providers: ProviderStatus[]
  partial: boolean
}

export type ApiErrorEnvelope = {
  error: {
    code: string
    message: string
    request_id: string
    details: Record<string, unknown>
  }
}

export function createSearchRequest(input: {
  bbox: number[]
  dateFrom: string
  dateTo: string
  cloudCover: number
}): SearchRequest {
  if (
    input.bbox.length !== 4 ||
    !input.bbox.every(Number.isFinite) ||
    input.bbox[2] <= input.bbox[0] ||
    input.bbox[3] <= input.bbox[1]
  ) {
    throw new Error('Invalid AOI bbox')
  }

  if (!Number.isInteger(input.cloudCover) || input.cloudCover < 0 || input.cloudCover > 100) {
    throw new Error('Invalid cloud cover')
  }

  return {
    bbox: [input.bbox[0]!, input.bbox[1]!, input.bbox[2]!, input.bbox[3]!],
    datetime: {
      from: `${input.dateFrom}T00:00:00Z`,
      to: `${input.dateTo}T23:59:59Z`,
    },
    cloud_cover_lte: input.cloudCover,
    collections: ['sentinel-2-l2a'],
    limit: 20,
    cursor: null,
  }
}

export function normalizeAoiBbox(value: unknown): AOIBbox {
  if (!Array.isArray(value) || value.length !== 4) {
    return null
  }

  const [west, south, east, north] = value
  if (
    typeof west !== 'number' ||
    typeof south !== 'number' ||
    typeof east !== 'number' ||
    typeof north !== 'number' ||
    ![west, south, east, north].every(Number.isFinite) ||
    east <= west ||
    north <= south
  ) {
    return null
  }

  return [west, south, east, north]
}
