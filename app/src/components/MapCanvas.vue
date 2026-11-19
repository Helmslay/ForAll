<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { createOpenLayersMap, type AOIBbox } from './openLayersMap'

const emit = defineEmits<{
  'aoi-change': [bbox: AOIBbox]
}>()

const target = ref(null)
const readout = reactive({ longitude: 0, latitude: 0, resolutionMeters: 0, hasCursor: false })
const aoi = reactive({ west: 0, south: 0, east: 0, north: 0, hasAoi: false, drawing: false })
let cleanup = () => {}
let setAoiDrawing = (enabled = false) => {
  void enabled
}
let clearAoiOnMap = () => {}

function formatResolution(resolutionMeters = readout.resolutionMeters) {
  return resolutionMeters >= 1000
    ? `${(resolutionMeters / 1000).toFixed(2)} км/px`
    : `${resolutionMeters.toFixed(1)} м/px`
}

function toggleAoiDrawing() {
  if (aoi.drawing) {
    setAoiDrawing(false)
    aoi.drawing = false
    return
  }

  setAoiDrawing(true)
  aoi.drawing = true
}

function clearAoi() {
  clearAoiOnMap()
}

onMounted(() => {
  if (target.value) {
    const controller = createOpenLayersMap(
      target.value,
      (nextReadout) => {
        readout.longitude = nextReadout?.longitude ?? 0
        readout.latitude = nextReadout?.latitude ?? 0
        readout.resolutionMeters = nextReadout?.resolutionMeters ?? 0
        readout.hasCursor = nextReadout !== null
      },
      (bbox) => {
        emit('aoi-change', bbox)
        aoi.hasAoi = bbox !== null
        aoi.drawing = false

        if (bbox) {
          ;[aoi.west, aoi.south, aoi.east, aoi.north] = bbox
        }
      },
    )
    setAoiDrawing = controller.setAoiDrawing
    clearAoiOnMap = controller.clearAoi
    cleanup = controller.dispose
  }
})

onBeforeUnmount(() => {
  cleanup()
})
</script>

<template>
  <section class="map-placeholder" aria-labelledby="map-canvas-title" tabindex="0">
    <div ref="target" class="map-canvas-target" aria-hidden="true"></div>
    <div class="placeholder-grid" aria-hidden="true"></div>
    <div class="placeholder-content">
      <span class="placeholder-icon" aria-hidden="true">⌖</span>
      <h2 id="map-canvas-title">Пустой холст карты</h2>
      <p>OpenLayers инициализирован. Базовая карта, спутниковые снимки и геоданные пока не подключены.</p>
    </div>
    <div class="map-tools" aria-label="Инструменты области интереса">
      <button class="aoi-draw-button" type="button" :aria-pressed="aoi.drawing" @click="toggleAoiDrawing">
        {{ aoi.drawing ? 'Отменить рисование' : aoi.hasAoi ? 'Изменить AOI' : 'Нарисовать AOI' }}
      </button>
      <button v-if="aoi.hasAoi" class="aoi-clear-button" type="button" @click="clearAoi">Очистить AOI</button>
    </div>
    <div v-if="aoi.hasAoi" class="aoi-bbox" role="status">
      W {{ aoi.west.toFixed(5) }} · S {{ aoi.south.toFixed(5) }} · E {{ aoi.east.toFixed(5) }} · N
      {{ aoi.north.toFixed(5) }}
    </div>
    <div class="map-readout" aria-label="Координаты курсора и разрешение карты">
      <template v-if="readout.hasCursor">
        <span>Lon {{ readout.longitude.toFixed(5) }}, Lat {{ readout.latitude.toFixed(5) }}</span>
        <span>{{ formatResolution(readout.resolutionMeters) }}</span>
      </template>
      <span v-else>Курсор вне карты</span>
    </div>
    <span class="placeholder-caption">OPENLAYERS · ПУСТОЙ ХОЛСТ</span>
  </section>
</template>

<style scoped>
.map-canvas-target {
  position: absolute;
  z-index: 1;
  inset: 0;
}

.placeholder-grid,
.placeholder-content,
.placeholder-caption {
  pointer-events: none;
}

.map-tools {
  position: absolute;
  z-index: 3;
  top: 12px;
  left: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.map-tools button {
  min-height: 44px;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  background: var(--color-background);
  font: inherit;
  cursor: pointer;
}

.map-tools button[aria-pressed='true'] {
  border-color: var(--color-accent);
}

.aoi-bbox {
  position: absolute;
  z-index: 3;
  bottom: 34px;
  left: 12px;
  max-width: calc(100% - 24px);
  padding: 7px 10px;
  border: 1px solid rgba(var(--color-border-rgb), 0.35);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  background: rgba(var(--color-background-rgb), 0.88);
  font-size: var(--font-size-xs);
  font-variant-numeric: tabular-nums;
  pointer-events: none;
}

.map-readout {
  position: absolute;
  z-index: 2;
  right: 12px;
  bottom: 34px;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px 12px;
  max-width: calc(100% - 24px);
  padding: 7px 10px;
  border: 1px solid rgba(var(--color-border-rgb), 0.35);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  background: rgba(var(--color-background-rgb), 0.88);
  font-size: var(--font-size-xs);
  font-variant-numeric: tabular-nums;
  pointer-events: none;
}
</style>
