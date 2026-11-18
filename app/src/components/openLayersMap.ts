import Map from 'ol/Map.js'
import View from 'ol/View.js'

export function createOpenLayersMap(target: HTMLElement): () => void {
  const map = new Map({
    target,
    layers: [],
    view: new View({
      center: [0, 0],
      zoom: 2,
    }),
  })

  const resizeObserver = new ResizeObserver(() => {
    map.updateSize()
  })
  resizeObserver.observe(target)

  return () => {
    resizeObserver.disconnect()
    map.setTarget(undefined)
    map.dispose()
  }
}
