import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { fromLonLat } from 'ol/proj.js'
import MapCanvas from './MapCanvas.vue'

const mapMocks = vi.hoisted(() => ({
  instances: [] as Array<{
    updateSize: ReturnType<typeof vi.fn>
    setTarget: ReturnType<typeof vi.fn>
    dispose: ReturnType<typeof vi.fn>
    addLayer: ReturnType<typeof vi.fn>
    removeLayer: ReturnType<typeof vi.fn>
    addInteraction: ReturnType<typeof vi.fn>
    removeInteraction: ReturnType<typeof vi.fn>
    on: ReturnType<typeof vi.fn>
    getView: ReturnType<typeof vi.fn>
    pointerMoveHandler?: (event: { coordinate: number[] }) => void
  }>,
}))

const drawMocks = vi.hoisted(() => ({
  instances: [] as Array<{
    on: ReturnType<typeof vi.fn>
    drawEndHandler?: (event: {
      feature: {
        getGeometry: () => { getExtent: () => number[] } | null
      }
    }) => void
  }>,
}))

const vectorSourceMocks = vi.hoisted(() => ({
  instances: [] as Array<{
    clear: ReturnType<typeof vi.fn>
    removeFeature: ReturnType<typeof vi.fn>
  }>,
}))

const vectorLayerMocks = vi.hoisted(() => ({
  instances: [] as Array<{ source: unknown }>,
}))

vi.mock('ol/Map.js', () => ({
  default: class MockMap {
    updateSize = vi.fn()
    setTarget = vi.fn()
    dispose = vi.fn()
    addLayer = vi.fn()
    removeLayer = vi.fn()
    addInteraction = vi.fn()
    removeInteraction = vi.fn()
    getView = vi.fn(() => ({
      getResolution: () => 12.34,
      getProjection: () => 'EPSG:3857',
    }))
    on = vi.fn((type: string, handler: (event: { coordinate: number[] }) => void) => {
      if (type === 'pointermove') {
        this.pointerMoveHandler = handler
      }
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

vi.mock('ol/interaction/Draw.js', () => ({
  createBox: vi.fn(() => 'box-geometry-function'),
  default: class MockDraw {
    on = vi.fn(
      (
        _type: string,
        handler: (event: { feature: { getGeometry: () => { getExtent: () => number[] } | null } }) => void,
      ) => {
        this.drawEndHandler = handler
        return { target: this }
      },
    )
    drawEndHandler?: (event: {
      feature: {
        getGeometry: () => { getExtent: () => number[] } | null
      }
    }) => void

    constructor(_options: { source: unknown; type: string; geometryFunction: unknown }) {
      drawMocks.instances.push(this)
    }
  },
}))

vi.mock('ol/source/Vector.js', () => ({
  default: class MockVectorSource {
    clear = vi.fn()
    removeFeature = vi.fn()

    constructor() {
      vectorSourceMocks.instances.push(this)
    }
  },
}))

vi.mock('ol/layer/Vector.js', () => ({
  default: class MockVectorLayer {
    constructor(options: { source: unknown }) {
      vectorLayerMocks.instances.push(options)
    }
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
  drawMocks.instances.length = 0
  vectorSourceMocks.instances.length = 0
  vectorLayerMocks.instances.length = 0
  resizeObservers.length = 0
  vi.unstubAllGlobals()
  vi.clearAllMocks()
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
    expect(map?.removeLayer).toHaveBeenCalledOnce()
    expect(map?.setTarget).toHaveBeenCalledWith(undefined)
    expect(map?.dispose).toHaveBeenCalledOnce()
  })

  it('shows WGS84 longitude/latitude and local map resolution for the cursor', async () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)

    const wrapper = mount(MapCanvas)
    mapMocks.instances[0]?.pointerMoveHandler?.({ coordinate: [1113194.9, 2273030.9] })
    await nextTick()

    expect(wrapper.get('.map-readout').text()).toContain('Lon 10.00000, Lat 20.00000')
    expect(wrapper.get('.map-readout').text()).toContain('м/px')

    wrapper.get('.map-canvas-target').element.dispatchEvent(new Event('pointerleave'))
    await nextTick()
    expect(wrapper.get('.map-readout').text()).toBe('Курсор вне карты')

    wrapper.unmount()
  })

  it('draws a rectangle and reports WGS84 bbox in west, south, east, north order', async () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)

    const wrapper = mount(MapCanvas)
    const map = mapMocks.instances[0]
    await wrapper.get('.aoi-draw-button').trigger('click')

    expect(map?.addInteraction).toHaveBeenCalledOnce()
    expect(drawMocks.instances).toHaveLength(1)

    const [west, south] = fromLonLat([10, 20])
    const [east, north] = fromLonLat([11, 21])
    const draw = drawMocks.instances[0]
    draw?.drawEndHandler?.({
      feature: {
        getGeometry: () => ({
          getExtent: () => [west, south, east, north],
        }),
      },
    })
    await nextTick()

    expect(wrapper.get('.aoi-bbox').text()).toContain('W 10.00000')
    expect(wrapper.get('.aoi-bbox').text()).toContain('S 20.00000')
    expect(wrapper.get('.aoi-bbox').text()).toContain('E 11.00000')
    expect(wrapper.get('.aoi-bbox').text()).toContain('N 21.00000')
    expect(map?.removeInteraction).toHaveBeenCalledWith(draw)
    expect(wrapper.get('.aoi-draw-button').attributes('aria-pressed')).toBe('false')

    wrapper.unmount()
  })

  it('clears the drawn AOI and returns to the empty state', async () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)

    const wrapper = mount(MapCanvas)
    const [west, south] = fromLonLat([10, 20])
    const [east, north] = fromLonLat([11, 21])
    await wrapper.get('.aoi-draw-button').trigger('click')
    drawMocks.instances[0]?.drawEndHandler?.({
      feature: {
        getGeometry: () => ({
          getExtent: () => [west, south, east, north],
        }),
      },
    })
    await nextTick()

    await wrapper.get('.aoi-clear-button').trigger('click')
    await nextTick()

    expect(vectorSourceMocks.instances[0]?.clear).toHaveBeenCalled()
    expect(wrapper.find('.aoi-bbox').exists()).toBe(false)
    expect(wrapper.get('.aoi-draw-button').text()).toBe('Нарисовать AOI')

    wrapper.unmount()
  })

  it('cancels drawing mode and rejects a zero-area rectangle', async () => {
    vi.stubGlobal('ResizeObserver', MockResizeObserver)

    const wrapper = mount(MapCanvas)
    const map = mapMocks.instances[0]

    await wrapper.get('.aoi-draw-button').trigger('click')
    const draw = drawMocks.instances[0]
    await wrapper.get('.aoi-draw-button').trigger('click')

    expect(map?.removeInteraction).toHaveBeenCalledWith(draw)
    expect(wrapper.get('.aoi-draw-button').attributes('aria-pressed')).toBe('false')

    await wrapper.get('.aoi-draw-button').trigger('click')
    const [x, y] = fromLonLat([10, 20])
    const feature = {
      getGeometry: () => ({
        getExtent: () => [x, y, x, y],
      }),
    }
    drawMocks.instances[1]?.drawEndHandler?.({ feature })
    await nextTick()

    expect(vectorSourceMocks.instances[0]?.removeFeature).toHaveBeenCalledWith(feature)
    expect(wrapper.find('.aoi-bbox').exists()).toBe(false)
    expect(map?.removeInteraction).toHaveBeenCalledWith(drawMocks.instances[1])

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
