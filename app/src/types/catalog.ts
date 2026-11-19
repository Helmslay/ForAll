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
