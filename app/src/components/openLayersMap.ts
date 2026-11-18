import Map from 'ol/Map.js'
import { unByKey } from 'ol/Observable.js'
import { getPointResolution, toLonLat } from 'ol/proj.js'
import View from 'ol/View.js'

export type MapReadout = {
  longitude: number
  latitude: number
  resolutionMeters: number
} | null

export function createOpenLayersMap(
  target: HTMLElement,
  onReadout: (readout: MapReadout) => void = () => {},
): () => void {
  const map = new Map({
    target,
    layers: [],
    view: new View({
      center: [0, 0],
      zoom: 2,
    }),
  })

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

  const resizeObserver = new ResizeObserver(() => {
    map.updateSize()
  })
  resizeObserver.observe(target)

  return () => {
    resizeObserver.disconnect()
    unByKey(pointerMoveKey)
    target.removeEventListener('pointerleave', handlePointerLeave)
    onReadout(null)
    map.setTarget(undefined)
    map.dispose()
  }
}
