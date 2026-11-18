<script setup lang="ts">
import { ref } from 'vue'

const projectName = 'Sentinel Explorer'
const panelOpen = ref(false)

const navigationItems = [
  { label: 'Обзор', symbol: '⌖', active: true },
  { label: 'Поиск сцен', symbol: '⌕', active: false },
  { label: 'Слои', symbol: '▱', active: false },
  { label: 'Измерения', symbol: '⌁', active: false },
  { label: 'Локальные данные', symbol: '▤', active: false },
]

function closePanel() {
  panelOpen.value = false
}
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <a class="brand" href="#workspace" :aria-label="`${projectName} — к рабочей области`">
        <span class="brand-mark" aria-hidden="true">⌖</span>
        <span class="brand-name">Sentinel <span>Explorer</span></span>
      </a>

      <div class="header-context">
        <span class="context-label">Рабочее пространство</span>
        <span class="development-state">Режим разработки</span>
      </div>
    </header>

    <div class="app-layout">
      <aside class="sidebar" aria-label="Боковая панель приложения">
        <nav class="sidebar-nav" aria-label="Основная навигация">
          <ul>
            <li v-for="item in navigationItems" :key="item.label">
              <a
                v-if="item.active"
                class="nav-item active"
                href="#workspace"
                :aria-label="item.label"
                aria-current="page"
                :title="item.label"
              >
                <span class="nav-symbol" aria-hidden="true">{{ item.symbol }}</span>
                <span class="nav-label">{{ item.label }}</span>
              </a>
              <span
                v-else
                class="nav-item unavailable"
                :aria-label="`${item.label}, будет доступно позже`"
                aria-disabled="true"
                :title="`${item.label} — позже`"
              >
                <span class="nav-symbol" aria-hidden="true">{{ item.symbol }}</span>
                <span class="nav-label">{{ item.label }}</span>
              </span>
            </li>
          </ul>
        </nav>
      </aside>

      <main id="workspace" class="workspace" aria-labelledby="workspace-title">
        <div class="workspace-heading">
          <div>
            <p class="eyebrow">SENTINEL EXPLORER / GIS</p>
            <h1 id="workspace-title">Рабочая область</h1>
            <p class="workspace-description">
              Здесь будет карта для исследования территории и работы со спутниковыми данными.
            </p>
          </div>
          <div class="workspace-actions">
            <button
              class="panel-toggle"
              type="button"
              aria-controls="context-panel"
              :aria-expanded="panelOpen"
              @click="panelOpen = !panelOpen"
            >
              {{ panelOpen ? 'Скрыть панель' : 'Инструменты' }}
            </button>
            <span class="workspace-badge">Предварительная версия</span>
          </div>
        </div>

        <section class="map-placeholder" aria-labelledby="map-placeholder-title" tabindex="0">
          <div class="placeholder-grid" aria-hidden="true"></div>
          <div class="placeholder-content">
            <span class="placeholder-icon" aria-hidden="true">⌖</span>
            <h2 id="map-placeholder-title">Карта будет подключена на следующем этапе</h2>
            <p>
              Сейчас подготовлена только оболочка приложения. Спутниковые снимки, базовая карта, каталог и геоданные ещё
              не подключены.
            </p>
          </div>
          <span class="placeholder-caption">РАБОЧИЙ ХОЛСТ · ОЖИДАЕТ ПОДКЛЮЧЕНИЯ КАРТЫ</span>
        </section>
      </main>

      <aside id="context-panel" class="context-panel" :class="{ 'is-open': panelOpen }" aria-label="Контекстная панель">
        <div class="panel-heading">
          <div>
            <span class="eyebrow">РАБОЧАЯ ПАНЕЛЬ</span>
            <h2>Контекст</h2>
          </div>
          <button class="panel-close" type="button" aria-label="Закрыть панель инструментов" @click="closePanel">
            <span aria-hidden="true">×</span>
          </button>
        </div>
        <div class="panel-empty">
          <span class="panel-empty-symbol" aria-hidden="true">⌑</span>
          <h3>Панель инструментов</h3>
          <p>Здесь будут параметры выбранного инструмента, слоя или спутниковой сцены.</p>
        </div>
      </aside>
    </div>

    <button
      v-if="panelOpen"
      class="panel-backdrop"
      type="button"
      aria-label="Закрыть панель инструментов"
      @click="closePanel"
    ></button>

    <footer class="app-statusbar" role="status" aria-label="Состояние приложения">
      <span><i class="status-dot" aria-hidden="true"></i> Интерфейс запущен</span>
      <span>Карта не подключена</span>
      <span>Координаты и масштаб недоступны</span>
    </footer>
  </div>
</template>
