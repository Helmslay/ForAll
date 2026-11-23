import { afterEach, describe, expect, it, vi } from 'vitest'
import { CatalogApiError, searchCatalog } from './catalog'
import type { SearchRequest, SearchResponse } from '../types/catalog'

const request: SearchRequest = {
  bbox: [56.1, 58.9, 57.2, 59.8],
  datetime: { from: '2026-06-01T00:00:00Z', to: '2026-06-30T23:59:59Z' },
  cloud_cover_lte: 25,
  collections: ['sentinel-2-l2a'],
  limit: 20,
  cursor: null,
}

const result: SearchResponse = {
  items: [
    {
      key: 'earth-search:sentinel-2-l2a:item-1',
      provider: 'earth-search',
      collection: 'sentinel-2-l2a',
      item_id: 'item-1',
      acquired_at: '2026-06-15T07:20:00Z',
      platform: 'sentinel-2b',
      cloud_cover: 12.5,
      bbox: [56.1, 58.9, 57.2, 59.8],
      geometry: { type: 'Polygon', coordinates: [] },
      available_bands: ['B02', 'B03', 'B04', 'B08'],
      preview_available: true,
      resolution: null,
      crs: null,
      nodata: null,
      scale: null,
      offset: null,
    },
  ],
  next_cursor: 'opaque-cursor',
  providers: [
    {
      id: 'earth-search',
      status: 'partial',
      last_checked: '2026-06-15T08:00:00Z',
      reason: 'more_results_available',
    },
  ],
  partial: true,
}

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('searchCatalog', () => {
  it('posts the exact request DTO to the relative catalog endpoint and parses the response', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(result))
    vi.stubGlobal('fetch', fetchMock)

    await expect(searchCatalog(request)).resolves.toEqual(result)
    expect(fetchMock).toHaveBeenCalledOnce()
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/catalog/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: expect.any(AbortSignal),
    })
  })

  it('parses the standard safe API error envelope', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse(
          {
            error: {
              code: 'PROVIDER_UNAVAILABLE',
              message: 'Каталог временно недоступен',
              request_id: 'req-1',
              details: {},
            },
          },
          503,
        ),
      ),
    )

    await expect(searchCatalog(request)).rejects.toMatchObject({
      name: 'CatalogApiError',
      status: 503,
      code: 'PROVIDER_UNAVAILABLE',
      requestId: 'req-1',
      message: 'Каталог временно недоступен',
    })
  })

  it('sanitizes malformed non-JSON HTTP error responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response('private upstream detail', { status: 502 })),
    )

    await expect(searchCatalog(request)).rejects.toMatchObject({
      name: 'CatalogApiError',
      status: 502,
      code: 'HTTP_ERROR',
      message: 'Catalog request failed with HTTP 502',
      requestId: null,
    })
  })

  it('rejects malformed successful JSON with a typed safe response error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ items: [{ fake: true }] })))

    await expect(searchCatalog(request)).rejects.toMatchObject({
      name: 'CatalogApiError',
      status: 200,
      code: 'INVALID_CATALOG_RESPONSE',
    })
  })

  it('rejects non-JSON successful responses safely', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('not json', { status: 200 })))

    await expect(searchCatalog(request)).rejects.toMatchObject({
      name: 'CatalogApiError',
      code: 'INVALID_CATALOG_RESPONSE',
    })
  })

  it('aborts the previous in-flight search when a new search starts', async () => {
    const signals: AbortSignal[] = []
    const pending = new Map<AbortSignal, (response: Response) => void>()
    const fetchMock = vi.fn((_url: string, options: RequestInit) => {
      const signal = options.signal as AbortSignal
      signals.push(signal)
      return new Promise<Response>((resolve, reject) => {
        pending.set(signal, resolve)
        signal.addEventListener(
          'abort',
          () => reject(new DOMException('Aborted', 'AbortError')),
          { once: true },
        )
      })
    })
    vi.stubGlobal('fetch', fetchMock)

    const first = searchCatalog(request)
    const second = searchCatalog({ ...request, cursor: 'next-page' })

    expect(signals).toHaveLength(2)
    expect(signals[0]?.aborted).toBe(true)
    expect(signals[1]?.aborted).toBe(false)
    pending.get(signals[1]!)?.(jsonResponse({ ...result, next_cursor: null }))
    await expect(first).rejects.toMatchObject({ name: 'AbortError' })
    await expect(second).resolves.toMatchObject({ next_cursor: null })
  })
})
