import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import SearchPanel from './SearchPanel.vue'

const aoi: [number, number, number, number] = [56.1, 58.9, 57.2, 59.8]

function mountPanel(props: { aoi: typeof aoi | null } = { aoi }) {
  return mount(SearchPanel, { props })
}

describe('SearchPanel', () => {
  it('requires an AOI and valid date range before enabling submit', () => {
    const wrapper = mountPanel({ aoi: null })

    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Нарисуйте прямоугольную область интереса на карте.')
    expect(wrapper.text()).toContain('Укажите начальную дату.')
    expect(wrapper.text()).toContain('Укажите конечную дату.')
  })

  it('emits a typed Sentinel-2 L2A request with UTC day boundaries', async () => {
    const wrapper = mountPanel()

    await wrapper.get('#search-date-from').setValue('2026-06-01')
    await wrapper.get('#search-date-to').setValue('2026-06-30')
    await wrapper.get('#search-cloud-cover').setValue('25')

    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeUndefined()
    await wrapper.get('form').trigger('submit')

    expect(wrapper.emitted('submit')?.[0]?.[0]).toEqual({
      bbox: aoi,
      datetime: {
        from: '2026-06-01T00:00:00Z',
        to: '2026-06-30T23:59:59Z',
      },
      cloud_cover_lte: 25,
      collections: ['sentinel-2-l2a'],
      limit: 20,
      cursor: null,
    })
  })

  it('rejects a reversed date range and cloud cover outside the contract', async () => {
    const wrapper = mountPanel()

    await wrapper.get('#search-date-from').setValue('2026-07-02')
    await wrapper.get('#search-date-to').setValue('2026-07-01')
    await wrapper.get('#search-cloud-cover').setValue('101')

    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Начальная дата не может быть позже конечной.')
    expect(wrapper.text()).toContain('Облачность должна быть целым числом от 0 до 100%.')
  })

  it('does not emit a request when the browser rejects an invalid calendar date', async () => {
    const wrapper = mountPanel()

    await wrapper.get('#search-date-from').setValue('2026-02-30')
    await wrapper.get('#search-date-to').setValue('2026-03-01')

    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.emitted('submit')).toBeUndefined()
  })

  it('resets date and cloud filters while preserving the map AOI', async () => {
    const wrapper = mountPanel()

    await wrapper.get('#search-date-from').setValue('2026-06-01')
    await wrapper.get('#search-date-to').setValue('2026-06-30')
    await wrapper.get('#search-cloud-cover').setValue('20')
    await wrapper.get('.search-reset').trigger('click')

    expect((wrapper.get('#search-date-from').element as HTMLInputElement).value).toBe('')
    expect((wrapper.get('#search-date-to').element as HTMLInputElement).value).toBe('')
    expect((wrapper.get('#search-cloud-cover').element as HTMLInputElement).value).toBe('100')
    expect(wrapper.get('.aoi-value').text()).toContain('W 56.10000')
    expect(wrapper.emitted('reset')).toHaveLength(1)
  })
})
