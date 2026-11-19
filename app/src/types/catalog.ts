export type SearchRequest = {
  bbox: [west: number, south: number, east: number, north: number]
  datetime: {
    from: string
    to: string
  }
  cloud_cover_lte: number
  collections: string[]
  providers?: string[]
  limit: number
  cursor: string | null
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

  if (
    !Number.isInteger(input.cloudCover) ||
    input.cloudCover < 0 ||
    input.cloudCover > 100
  ) {
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
