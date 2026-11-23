import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent } from 'vue'
import App from './App.vue'
import { CatalogApiError, searchCatalog } from './api/catalog'
import type { SearchResponse } from './types/catalog'

vi.mock('./api/catalog', () => ({
  CatalogApiError: class CatalogApiError extends Error {},
  searchCatalog: vi.fn(),
}))

const MapCanvasStub = defineComponent({
  emits: ['aoi-change'],
  template: '<button class="map-aoi" @click="$emit(\'aoi-change\', [56.1, 58.9, 57.2, 59.8])">AOI</button>',
})

function mountApp() {
  return mount(App, { global: { stubs: { MapCanvas: MapCanvasStub } } })
}

const searchMock = vi.mocked(searchCatalog)
const scene = {
  key: 'provider:sentinel-2-l2a:scene-1',
  provider: 'configured-provider',
  collection: 'sentinel-2-l2a',
  item_id: 'scene-1',
  acquired_at: '2026-06-15T07:20:00Z',
  platform: 'sentinel-2b',
  cloud_cover: 12.5,
  bbox: [56.1, 58.9, 57.2, 59.8] as [number, number, number, number],
  geometry: null,
  available_bands: ['B02', 'B03', 'B04', 'B08'] as SearchResponse['items'][number]['available_bands'],
  preview_available: false,
}
const response: SearchResponse = {
  items: [scene],
  next_cursor: 'cursor-2',
  providers: [{ id: 'configured-provider', status: 'success' }],
  partial: false,
}

beforeEach(() => searchMock.mockReset())

async function submitSearch(wrapper: ReturnType<typeof mountApp>) {
  await wrapper.get('.map-aoi').trigger('click')
  await wrapper.get('#search-date-from').setValue('2026-06-01')
  await wrapper.get('#search-date-to').setValue('2026-06-30')
  await wrapper.get('form').trigger('submit')
}

describe('App', () => {
  it('renders the desktop GIS shell and its semantic landmarks', () => {
    const wrapper = mountApp()

    expect(wrapper.get('header').text()).toContain('Sentinel Explorer')
    expect(wrapper.get('aside[aria-label="Боковая панель приложения"]').element.tagName).toBe('ASIDE')
    expect(wrapper.get('nav[aria-label="Основная навигация"]').element.tagName).toBe('NAV')
    expect(wrapper.findAll('main')).toHaveLength(1)
    expect(wrapper.get('main#workspace').element.tagName).toBe('MAIN')
    expect(wrapper.get('h1').text()).toBe('Рабочая область')
    expect(wrapper.text()).toContain('Поиск сцен')
    expect(wrapper.text()).toContain('Слои')
    expect(wrapper.text()).toContain('Измерения')
    expect(wrapper.get('.panel-heading h2').text()).toBe('Поиск сцен')
    expect(wrapper.find('.search-form').exists()).toBe(true)
    expect(wrapper.get('.context-panel').text()).toContain('Нарисуйте прямоугольную область интереса на карте.')
    expect(wrapper.get('.app-statusbar').text()).toContain('Пустой холст OpenLayers')
    expect(wrapper.find('.map-aoi').exists()).toBe(true)
  })

  it('opens and closes the contextual panel using touch-sized controls', async () => {
    const wrapper = mountApp()
    const toggle = wrapper.get('.panel-toggle')

    expect(toggle.attributes('aria-expanded')).toBe('false')
    expect(toggle.attributes('aria-controls')).toBe('context-panel')

    await toggle.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.get('.context-panel').classes()).toContain('is-open')
    expect(wrapper.find('.panel-backdrop').exists()).toBe(true)

    await wrapper.get('.panel-close').trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('false')
    expect(wrapper.get('.context-panel').classes()).not.toContain('is-open')
    expect(wrapper.find('.panel-backdrop').exists()).toBe(false)
  })

  it('closes the contextual panel when its backdrop is activated', async () => {
    const wrapper = mountApp()

    await wrapper.get('.panel-toggle').trigger('click')
    await wrapper.get('.panel-backdrop').trigger('click')

    expect(wrapper.get('.panel-toggle').attributes('aria-expanded')).toBe('false')
  })

  it('shows loading state and disables the search submit button', async () => {
    let resolveSearch!: (value: SearchResponse) => void
    searchMock.mockReturnValueOnce(
      new Promise((resolve) => {
        resolveSearch = resolve
      }),
    )
    const wrapper = mountApp()
    await submitSearch(wrapper)

    expect(wrapper.text()).toContain('Выполняется поиск сцен')
    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    resolveSearch(response)
  })

  it('renders API scenes and provider status', async () => {
    searchMock.mockResolvedValue(response)
    const wrapper = mountApp()
    await submitSearch(wrapper)
    await vi.waitFor(() => expect(wrapper.text()).toContain('scene-1'))

    expect(searchMock).toHaveBeenCalledWith(expect.objectContaining({ cursor: null }))
    expect(wrapper.text()).toContain('configured-provider')
    expect(wrapper.text()).toContain('Найдено сцен: 1')
  })

  it('renders empty and partial-result states', async () => {
    searchMock.mockResolvedValueOnce({ ...response, items: [], next_cursor: null })
    const empty = mountApp()
    await submitSearch(empty)
    await vi.waitFor(() => expect(empty.text()).toContain('Каталог не вернул сцен'))

    searchMock.mockResolvedValueOnce({
      ...response,
      partial: true,
      providers: [{ id: 'configured-provider', status: 'partial', reason: 'more_results_available' }],
    })
    const partial = mountApp()
    await submitSearch(partial)
    await vi.waitFor(() => expect(partial.text()).toContain('Получены неполные результаты'))
    expect(partial.text()).toContain('more_results_available')
  })

  it('shows an error and retries', async () => {
    searchMock.mockRejectedValueOnce(new CatalogApiError('Каталог временно недоступен')).mockResolvedValueOnce(response)
    const wrapper = mountApp()
    await submitSearch(wrapper)
    await vi.waitFor(() => expect(wrapper.text()).toContain('Каталог временно недоступен'))
    await wrapper.get('.catalog-action').trigger('click')
    await vi.waitFor(() => expect(wrapper.text()).toContain('scene-1'))

    expect(searchMock).toHaveBeenCalledTimes(2)
  })

  it('loads cursor pages and deduplicates scene keys', async () => {
    searchMock.mockResolvedValueOnce(response).mockResolvedValueOnce({
      ...response,
      items: [scene, { ...scene, key: 'provider:sentinel-2-l2a:scene-2', item_id: 'scene-2' }],
      next_cursor: null,
    })
    const wrapper = mountApp()
    await submitSearch(wrapper)
    await vi.waitFor(() => expect(wrapper.text()).toContain('scene-1'))
    await wrapper.get('.catalog-action').trigger('click')
    await vi.waitFor(() => expect(wrapper.text()).toContain('scene-2'))

    expect(searchMock).toHaveBeenNthCalledWith(2, expect.objectContaining({ cursor: 'cursor-2' }))
    expect(wrapper.findAll('.scene-result')).toHaveLength(2)
  })

  it('does not show a pending response after search reset', async () => {
    let resolveSearch!: (value: SearchResponse) => void
    searchMock.mockReturnValueOnce(
      new Promise((resolve) => {
        resolveSearch = resolve
      }),
    )
    const wrapper = mountApp()
    await submitSearch(wrapper)
    await wrapper.get('.search-reset').trigger('click')
    resolveSearch(response)
    await Promise.resolve()

    expect(wrapper.find('.scene-result').exists()).toBe(false)
  })
})
