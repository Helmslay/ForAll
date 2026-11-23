<script setup lang="ts">
import { ref } from 'vue'
import MapCanvas from './components/MapCanvas.vue'
import SearchPanel from './components/SearchPanel.vue'
import { CatalogApiError, searchCatalog } from './api/catalog'
import type { SearchRequest, SearchResponse } from './types/catalog'
import { normalizeAoiBbox } from './types/catalog'

const projectName = 'Sentinel Explorer'
const panelOpen = ref(false)
const aoiBbox = ref(normalizeAoiBbox(null))
const searchLoading = ref(false)
const searchError = ref('')
const searchResponse = ref<SearchResponse | null>(null)
const activeRequest = ref<SearchRequest | null>(null)
let searchSequence = 0

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

function isAbortError(error: unknown) {
  return error instanceof Error && error.name === 'AbortError'
}

async function runSearch(request: SearchRequest, append = false) {
  const sequence = ++searchSequence
  searchLoading.value = true
  searchError.value = ''
  if (!append) {
    activeRequest.value = { ...request, cursor: null }
    searchResponse.value = null
  }
  try {
    const response = await searchCatalog(request)
    if (sequence !== searchSequence) return
    if (append && searchResponse.value) {
      const existing = new Set(searchResponse.value.items.map((scene) => scene.key))
      const uniqueItems = response.items.filter((scene) => !existing.has(scene.key))
      searchResponse.value = {
        ...response,
        items: [...searchResponse.value.items, ...uniqueItems],
        partial: response.partial || searchResponse.value.partial,
      }
    } else {
      searchResponse.value = response
    }
  } catch (error) {
    if (sequence !== searchSequence || isAbortError(error)) return
    searchError.value = error instanceof CatalogApiError ? error.message : 'Не удалось выполнить поиск каталога.'
  } finally {
    if (sequence === searchSequence) searchLoading.value = false
  }
}

function handleSearch(request: SearchRequest) {
  void runSearch(request)
}

function loadMore() {
  const cursor = searchResponse.value?.next_cursor
  if (!cursor || !activeRequest.value || searchLoading.value) return
  void runSearch({ ...activeRequest.value, cursor }, true)
}

function retrySearch() {
  if (activeRequest.value) void runSearch(activeRequest.value)
}

function resetSearch() {
  searchSequence += 1
  searchLoading.value = false
  searchError.value = ''
  searchResponse.value = null
  activeRequest.value = null
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
        <SearchPanel :aoi="aoiBbox || undefined" :loading="searchLoading" @submit="handleSearch" @reset="resetSearch" />
        <section v-if="searchLoading" class="catalog-state" role="status" aria-live="polite">Выполняется поиск сцен…</section>
        <section v-else-if="searchError" class="catalog-state catalog-error" role="alert">
          <p>{{ searchError }}</p>
          <button type="button" class="catalog-action" @click="retrySearch">Повторить поиск</button>
        </section>
        <section v-else-if="searchResponse" class="catalog-results" aria-label="Результаты поиска">
          <p v-if="searchResponse.partial" class="catalog-partial" role="status">Получены неполные результаты: один или несколько источников вернули частичный ответ.</p>
          <div v-if="searchResponse.providers.length" class="provider-statuses" aria-label="Состояние источников">
            <p v-for="provider in searchResponse.providers" :key="provider.id">{{ provider.id }}: {{ provider.status }}<span v-if="provider.reason"> ({{ provider.reason }})</span></p>
          </div>
          <p v-if="searchResponse.items.length === 0" class="catalog-empty" role="status">Каталог не вернул сцен по заданным параметрам.</p>
          <template v-else>
            <p class="catalog-count">Найдено сцен: {{ searchResponse.items.length }}</p>
            <article v-for="scene in searchResponse.items" :key="scene.key" class="scene-result">
              <h3>{{ scene.item_id }}</h3>
              <p>{{ new Date(scene.acquired_at).toLocaleString() }}</p>
              <p>{{ scene.platform || 'Платформа не указана' }} · {{ scene.cloud_cover === null ? 'Облачность не указана' : scene.cloud_cover + '%' }}</p>
              <p class="scene-provider">{{ scene.provider }} · {{ scene.collection }} · {{ scene.available_bands.join(', ') }}</p>
            </article>
          </template>
          <button v-if="searchResponse.next_cursor" type="button" class="catalog-action" :disabled="searchLoading" @click="loadMore">Загрузить ещё</button>
        </section>
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
