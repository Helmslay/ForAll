import Map from 'ol/Map.js'
import { unByKey } from 'ol/Observable.js'
import { getPointResolution, toLonLat, transformExtent } from 'ol/proj.js'
import Draw, { createBox } from 'ol/interaction/Draw.js'
import VectorLayer from 'ol/layer/Vector.js'
import View from 'ol/View.js'
import VectorSource from 'ol/source/Vector.js'
import type { EventsKey } from 'ol/events.js'

export type MapReadout = {
  longitude: number
  latitude: number
  resolutionMeters: number
} | null

export type AOIBbox = [west: number, south: number, east: number, north: number] | null

export type OpenLayersMapController = {
  setAoiDrawing: (enabled?: boolean) => void
  clearAoi: () => void
  dispose: () => void
}

export function createOpenLayersMap(
  target: HTMLElement,
  onReadout: (readout: MapReadout) => void = () => {},
  onAoiChange: (bbox: AOIBbox) => void = () => {},
): OpenLayersMapController {
  const map = new Map({
    target,
    layers: [],
    view: new View({
      center: [0, 0],
      zoom: 2,
    }),
  })

  const aoiSource = new VectorSource()
  const aoiLayer = new VectorLayer({ source: aoiSource })
  map.addLayer(aoiLayer)

  const handlePointerMove = (event: { coordinate: number[] }) => {
    const view = map.getView()
    const resolution = view.getResolution()

    if (resolution === undefined) {
      onReadout(null)
      return
    }

    const projection = view.getProjection()
    const [longitude, latitude] = toLonLat(event.coordinate, projection)
    const resolutionMeters = getPointResolution(projection, resolution, event.coordinate, 'm')

    onReadout({ longitude, latitude, resolutionMeters })
  }
  const handlePointerLeave = () => onReadout(null)

  const pointerMoveKey = map.on('pointermove', handlePointerMove)
  target.addEventListener('pointerleave', handlePointerLeave)

  let drawInteraction: Draw | null = null
  let drawEndKey: EventsKey | null = null

  const removeDrawInteraction = () => {
    if (drawEndKey) {
      unByKey(drawEndKey)
      drawEndKey = null
    }

    if (drawInteraction) {
      map.removeInteraction(drawInteraction)
      drawInteraction = null
    }
  }

  const clearAoi = () => {
    removeDrawInteraction()
    aoiSource.clear()
    onAoiChange(null)
  }

  const setAoiDrawing = (enabled = false) => {
    removeDrawInteraction()

    if (!enabled) {
      return
    }

    clearAoi()

    const interaction = new Draw({
      source: aoiSource,
      type: 'Circle',
      geometryFunction: createBox(),
    })
    drawInteraction = interaction

    drawEndKey = interaction.on('drawend', (event) => {
      const geometry = event.feature.getGeometry()

      if (!geometry) {
        aoiSource.removeFeature(event.feature)
        onAoiChange(null)
        removeDrawInteraction()
        return
      }

      const [west, south, east, north] = transformExtent(
        geometry.getExtent(),
        map.getView().getProjection(),
        'EPSG:4326',
      )

      if (![west, south, east, north].every(Number.isFinite) || east <= west || north <= south) {
        aoiSource.removeFeature(event.feature)
        onAoiChange(null)
      } else {
        onAoiChange([west, south, east, north])
      }

      removeDrawInteraction()
    })

    map.addInteraction(interaction)
  }

  const resizeObserver = new ResizeObserver(() => {
    map.updateSize()
  })
  resizeObserver.observe(target)

  const dispose = () => {
    resizeObserver.disconnect()
    removeDrawInteraction()
    aoiSource.clear()
    map.removeLayer(aoiLayer)
    unByKey(pointerMoveKey)
    target.removeEventListener('pointerleave', handlePointerLeave)
    onReadout(null)
    onAoiChange(null)
    map.setTarget(undefined)
    map.dispose()
  }

  return { setAoiDrawing, clearAoi, dispose }
}
