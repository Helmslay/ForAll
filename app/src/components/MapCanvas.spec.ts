import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import MapCanvas from './MapCanvas.vue'

const mapMocks = vi.hoisted(() => ({
  instances: [] as Array<{
    updateSize: ReturnType<typeof vi.fn>
    setTarget: ReturnType<typeof vi.fn>
    dispose: ReturnType<typeof vi.fn>
    on: ReturnType<typeof vi.fn>
    getView: ReturnType<typeof vi.fn>
    pointerMoveHandler?: (event: { coordinate: number[] }) => void
  }>,
}))

vi.mock('ol/Map.js', () => ({
  default: class MockMap {
    updateSize = vi.fn()
    setTarget = vi.fn()
    dispose = vi.fn()
    getView = vi.fn(() => ({
      getResolution: () => 12.34,
      getProjection: () => 'EPSG:3857',
    }))
    on = vi.fn((_type: string, handler: (event: { coordinate: number[] }) => void) => {
      this.pointerMoveHandler = handler
      return { target: this }
    })
    pointerMoveHandler?: (event: { coordinate: number[] }) => void

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

vi.mock('ol/Observable.js', () => ({
  unByKey: vi.fn(),
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

  it('disconnects the observer, map event, pointer listener and map on unmount', async () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)
    const { unByKey } = await import('ol/Observable.js')
    const wrapper = mount(MapCanvas)
    const map = mapMocks.instances[0]
    const observer = resizeObservers[0]
    const target = wrapper.get('.map-canvas-target').element
    const removeListener = vi.spyOn(target, 'removeEventListener')

    wrapper.unmount()

    expect(observer?.disconnect).toHaveBeenCalledOnce()
    expect(unByKey).toHaveBeenCalledOnce()
    expect(removeListener).toHaveBeenCalledWith('pointerleave', expect.any(Function))
    expect(map?.setTarget).toHaveBeenCalledWith(undefined)
    expect(map?.dispose).toHaveBeenCalledOnce()
  })

  it('shows WGS84 longitude/latitude and local map resolution for the cursor', () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)

    const wrapper = mount(MapCanvas)
    mapMocks.instances[0]?.pointerMoveHandler?.({ coordinate: [1113194.9, 2273030.9] })

    expect(wrapper.get('.map-readout').text()).toContain('Lon 10.00000, Lat 20.00000')
    expect(wrapper.get('.map-readout').text()).toContain('м/px')

    wrapper.get('.map-canvas-target').element.dispatchEvent(new Event('pointerleave'))
    expect(wrapper.get('.map-readout').text()).toBe('Курсор вне карты')

    wrapper.unmount()
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
