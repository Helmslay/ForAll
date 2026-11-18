<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { createOpenLayersMap } from './openLayersMap'

const target = ref(null)
const readout = ref(/** @type {import('./openLayersMap').MapReadout} */ null)
let cleanup = () => {}

/** @param {number} resolutionMeters */
function formatResolution(resolutionMeters) {
  return resolutionMeters >= 1000
    ? `${(resolutionMeters / 1000).toFixed(2)} км/px`
    : `${resolutionMeters.toFixed(1)} м/px`
}

onMounted(() => {
  if (target.value) {
    cleanup = createOpenLayersMap(target.value, (nextReadout) => {
      readout.value = nextReadout
    })
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
    <div class="map-readout" aria-label="Координаты курсора и разрешение карты">
      <template v-if="readout">
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
