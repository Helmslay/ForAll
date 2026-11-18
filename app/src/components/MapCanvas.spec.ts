import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import MapCanvas from './MapCanvas.vue'

const mapMocks = vi.hoisted(() => ({
  instances: [] as Array<{
    updateSize: ReturnType<typeof vi.fn>
    setTarget: ReturnType<typeof vi.fn>
    dispose: ReturnType<typeof vi.fn>
  }>,
}))

vi.mock('ol/Map.js', () => ({
  default: class MockMap {
    updateSize = vi.fn()
    setTarget = vi.fn()
    dispose = vi.fn()

    constructor(_options: { target: HTMLElement }) {
      mapMocks.instances.push(this)
    }
  },
}))

vi.mock('ol/View.js', () => ({
  default: class MockView {
    constructor(_options: { center: number[]; zoom: number }) {}
  },
}))

const resizeObservers: MockResizeObserver[] = []

class MockResizeObserver implements ResizeObserver {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()

  constructor(private readonly callback: ResizeObserverCallback) {
    resizeObservers.push(this)
  }

  trigger() {
    this.callback([], this)
  }
}

afterEach(() => {
  mapMocks.instances.length = 0
  resizeObservers.length = 0
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('MapCanvas', () => {
  it('creates one map and updates its size when the container resizes', () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)

    const wrapper = mount(MapCanvas)

    expect(mapMocks.instances).toHaveLength(1)
    expect(resizeObservers).toHaveLength(1)
    expect(resizeObservers[0]?.observe).toHaveBeenCalledWith(wrapper.get('.map-canvas-target').element)

    resizeObservers[0]?.trigger()
    expect(mapMocks.instances[0]?.updateSize).toHaveBeenCalledOnce()

    wrapper.unmount()
  })

  it('disconnects the observer, detaches and disposes the map on unmount', () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)

    const wrapper = mount(MapCanvas)
    const map = mapMocks.instances[0]
    const observer = resizeObservers[0]

    wrapper.unmount()

    expect(observer?.disconnect).toHaveBeenCalledOnce()
    expect(map?.setTarget).toHaveBeenCalledWith(undefined)
    expect(map?.dispose).toHaveBeenCalledOnce()
  })

  it('creates an independent map instance after a remount without console errors', () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

    const first = mount(MapCanvas)
    first.unmount()
    const second = mount(MapCanvas)

    expect(mapMocks.instances).toHaveLength(2)
    expect(mapMocks.instances[0]).not.toBe(mapMocks.instances[1])
    expect(consoleError).not.toHaveBeenCalled()

    second.unmount()
  })
})
