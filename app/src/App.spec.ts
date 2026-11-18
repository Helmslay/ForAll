import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import App from './App.vue'

describe('App', () => {
  it('renders the desktop GIS shell and its semantic landmarks', () => {
    const wrapper = mount(App)

    expect(wrapper.get('header').text()).toContain('Sentinel Explorer')
    expect(wrapper.get('aside[aria-label="Боковая панель приложения"]').element.tagName).toBe('ASIDE')
    expect(wrapper.get('nav[aria-label="Основная навигация"]').element.tagName).toBe('NAV')
    expect(wrapper.findAll('main')).toHaveLength(1)
    expect(wrapper.get('main#workspace').element.tagName).toBe('MAIN')
    expect(wrapper.get('h1').text()).toBe('Рабочая область')
    expect(wrapper.text()).toContain('Поиск сцен')
    expect(wrapper.text()).toContain('Слои')
    expect(wrapper.text()).toContain('Измерения')
    expect(wrapper.get('.context-panel').text()).toContain('Панель инструментов')
    expect(wrapper.get('[role="status"]').text()).toContain('Карта не подключена')
    expect(wrapper.get('#map-placeholder-title').text()).toContain('Карта будет подключена')
    expect(wrapper.get('.map-placeholder').attributes('tabindex')).toBe('0')
  })

  it('opens and closes the contextual panel using touch-sized controls', async () => {
    const wrapper = mount(App)
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
    const wrapper = mount(App)

    await wrapper.get('.panel-toggle').trigger('click')
    await wrapper.get('.panel-backdrop').trigger('click')

    expect(wrapper.get('.panel-toggle').attributes('aria-expanded')).toBe('false')
  })
})
