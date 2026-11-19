import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import App from './App.vue'

function mountApp() {
  return mount(App, { global: { stubs: { MapCanvas: true } } })
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
    expect(wrapper.find('map-canvas-stub').exists()).toBe(true)
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
})
