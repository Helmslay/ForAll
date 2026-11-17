import { afterEach, describe, expect, it, vi } from 'vitest'
import { getHealth } from './health'

describe('getHealth', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('requests the relative health endpoint and returns its typed payload', async () => {
    const payload = {
      status: 'ok' as const,
      app_version: '0.1.0',
      timestamp: '2026-11-17T12:00:00Z',
    }
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(payload), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await expect(getHealth()).resolves.toEqual(payload)
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/health')
  })

  it('rejects unsuccessful HTTP responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 503 })))

    await expect(getHealth()).rejects.toThrow('Health request failed with HTTP 503')
  })
})
