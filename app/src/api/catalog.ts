import { API_BASE_PATH } from './config'
import type { ApiErrorEnvelope, ProviderStatus, Scene, SearchRequest, SearchResponse } from '../types/catalog'

let activeSearch: AbortController | null = null

export class CatalogApiError extends Error {
  readonly status: number
  readonly code: string
  readonly requestId: string | null

  constructor(message: string, status: number, code: string, requestId: string | null = null) {
    super(message)
    this.name = 'CatalogApiError'
    this.status = status
    this.code = code
    this.requestId = requestId
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isProviderStatus(value: unknown): value is ProviderStatus {
  if (!isRecord(value)) return false
  return (
    typeof value.id === 'string' &&
    value.id.length > 0 &&
    (value.status === 'success' || value.status === 'partial' || value.status === 'unavailable') &&
    (value.last_checked === undefined || value.last_checked === null || typeof value.last_checked === 'string') &&
    (value.reason === undefined || value.reason === null || typeof value.reason === 'string')
  )
}

function isScene(value: unknown): value is Scene {
  if (!isRecord(value)) return false
  const bands = value.available_bands
  return (
    typeof value.key === 'string' &&
    value.key.length > 0 &&
    typeof value.provider === 'string' &&
    value.provider.length > 0 &&
    typeof value.collection === 'string' &&
    value.collection.length > 0 &&
    typeof value.item_id === 'string' &&
    value.item_id.length > 0 &&
    typeof value.acquired_at === 'string' &&
    (value.platform === null || typeof value.platform === 'string') &&
    (value.cloud_cover === null || typeof value.cloud_cover === 'number') &&
    (value.bbox === null ||
      (Array.isArray(value.bbox) && value.bbox.length === 4 && value.bbox.every(Number.isFinite))) &&
    (value.geometry === null || isRecord(value.geometry)) &&
    Array.isArray(bands) &&
    bands.every((band) => band === 'B02' || band === 'B03' || band === 'B04' || band === 'B08') &&
    typeof value.preview_available === 'boolean' &&
    (value.resolution === undefined || value.resolution === null || typeof value.resolution === 'number') &&
    (value.crs === undefined || value.crs === null || typeof value.crs === 'string') &&
    (value.nodata === undefined || value.nodata === null || typeof value.nodata === 'number') &&
    (value.scale === undefined || value.scale === null || typeof value.scale === 'number') &&
    (value.offset === undefined || value.offset === null || typeof value.offset === 'number')
  )
}

function isSearchResponse(value: unknown): value is SearchResponse {
  return (
    isRecord(value) &&
    Array.isArray(value.items) &&
    value.items.every(isScene) &&
    (value.next_cursor === null || typeof value.next_cursor === 'string') &&
    Array.isArray(value.providers) &&
    value.providers.every(isProviderStatus) &&
    typeof value.partial === 'boolean'
  )
}

function isApiErrorEnvelope(value: unknown): value is ApiErrorEnvelope {
  if (!isRecord(value) || !isRecord(value.error)) return false
  const error = value.error
  return (
    typeof error.code === 'string' &&
    typeof error.message === 'string' &&
    typeof error.request_id === 'string' &&
    isRecord(error.details)
  )
}

function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === 'AbortError'
}

export async function searchCatalog(request: SearchRequest): Promise<SearchResponse> {
  activeSearch?.abort()
  const controller = new AbortController()
  activeSearch = controller

  try {
    const response = await fetch(API_BASE_PATH + '/catalog/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: controller.signal,
    })

    if (!response.ok) {
      let payload: unknown
      try {
        payload = await response.json()
      } catch {
        payload = null
      }

      if (isApiErrorEnvelope(payload)) {
        throw new CatalogApiError(payload.error.message, response.status, payload.error.code, payload.error.request_id)
      }

      throw new CatalogApiError('Catalog request failed with HTTP ' + response.status, response.status, 'HTTP_ERROR')
    }

    let payload: unknown
    try {
      payload = await response.json()
    } catch {
      throw new CatalogApiError('Catalog returned an invalid response', response.status, 'INVALID_CATALOG_RESPONSE')
    }

    if (!isSearchResponse(payload)) {
      throw new CatalogApiError(
        'Catalog returned an invalid response',
        response.status,
        'INVALID_CATALOG_RESPONSE',
      )
    }

    return payload
  } catch (error) {
    if (isAbortError(error)) throw error
    if (error instanceof CatalogApiError) throw error
    throw new CatalogApiError('Catalog request failed', 0, 'NETWORK_ERROR')
  } finally {
    if (activeSearch === controller) activeSearch = null
  }
}
