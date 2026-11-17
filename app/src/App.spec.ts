import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import App from './App.vue'

describe('App', () => {
  it('renders the GIS application shell with semantic landmarks', () => {
    const wrapper = mount(App)

    expect(wrapper.get('header').text()).toContain('Sentinel Explorer')
    expect(wrapper.get('aside[aria-label="Боковая панель приложения"]').exists()).toBe(true)
    expect(wrapper.get('nav[aria-label="Основная навигация"]').exists()).toBe(true)
    expect(wrapper.findAll('main')).toHaveLength(1)
    expect(wrapper.get('main#workspace').exists()).toBe(true)
    expect(wrapper.get('h1').text()).toBe('Рабочая область')
    expect(wrapper.text()).toContain('Поиск сцен')
    expect(wrapper.text()).toContain('Слои')
    expect(wrapper.text()).toContain('Измерения')
    expect(wrapper.get('[role="status"]').text()).toContain('Картографический модуль не подключён')
    expect(wrapper.get('#map-placeholder-title').text()).toContain('Карта будет подключена')
  })
})
