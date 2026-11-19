<script setup lang="ts">
import { ref } from 'vue'
import MapCanvas from './components/MapCanvas.vue'
import SearchPanel from './components/SearchPanel.vue'
import type { AOIBbox } from './components/openLayersMap'
import type { SearchRequest } from './types/catalog'

const projectName = 'Sentinel Explorer'
const panelOpen = ref(false)
const aoiBbox = ref<AOIBbox>(null)
const preparedSearch = ref<SearchRequest | null>(null)

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

function handleSearch(request: SearchRequest) {
  preparedSearch.value = request
}

function resetSearch() {
  preparedSearch.value = null
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
            <p class="workspace-description">Подготовлен пустой холст карты; источники данных пока не подключены.</p>
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

        <MapCanvas @aoi-change="aoiBbox = $event" />
      </main>

      <aside id="context-panel" class="context-panel" :class="{ 'is-open': panelOpen }" aria-label="Контекстная панель">
        <div class="panel-heading">
          <div>
            <span class="eyebrow">КАТАЛОГ SENTINEL-2</span>
            <h2>Поиск сцен</h2>
          </div>
          <button class="panel-close" type="button" aria-label="Закрыть панель инструментов" @click="closePanel">
            <span aria-hidden="true">×</span>
          </button>
        </div>
        <SearchPanel :aoi="aoiBbox" @submit="handleSearch" @reset="resetSearch" />
        <p v-if="preparedSearch" class="search-prepared" role="status">
          Параметры подготовлены. Сетевой поиск пока не подключён.
        </p>
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
      <span>Пустой холст OpenLayers</span>
      <span>Источники данных не подключены</span>
    </footer>
  </div>
</template>
