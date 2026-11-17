import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import App from './App.vue'

describe('App', () => {
  it('renders the application name and current scaffold status', () => {
    const wrapper = mount(App)

    expect(wrapper.get('h1').text()).toBe('Sentinel Explorer')
    expect(wrapper.get('.eyebrow').text()).toBe('Браузерная ГИС · разработка')
    expect(wrapper.get('[role="status"]').text()).toContain(
      'Функции карты и спутниковых данных ещё не подключены.',
    )
  })
})
