<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { createOpenLayersMap } from './openLayersMap'

const target = ref(null)
let cleanup = () => {}

onMounted(() => {
  if (target.value) {
    cleanup = createOpenLayersMap(target.value)
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
    <span class="placeholder-caption">OPENLAYERS · ПУСТОЙ ХОЛСТ</span>
  </section>
</template>

<style scoped>
.map-canvas-target {
  position: absolute;
  inset: 0;
}
</style>
