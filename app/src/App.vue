<script setup lang="ts">
const projectName = 'Sentinel Explorer'
</script>

<template>
  <main class="page">
    <section class="intro" aria-labelledby="page-title">
      <p class="eyebrow">Браузерная ГИС · разработка</p>
      <h1 id="page-title">{{ projectName }}</h1>
      <p class="description">
        Основа приложения создана. Здесь будет рабочее пространство для поиска, просмотра и анализа спутниковых снимков
        Sentinel-2.
      </p>
      <p class="status" role="status">Каркас frontend запущен. Функции карты и спутниковых данных ещё не подключены.</p>
    </section>
  </main>
</template>
