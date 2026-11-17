<script setup lang="ts">
const projectName = 'Sentinel Explorer'

const navigationItems = [
  { label: 'Обзор', symbol: '⌖', active: true },
  { label: 'Поиск сцен', symbol: '⌕', active: false },
  { label: 'Слои', symbol: '▱', active: false },
  { label: 'Измерения', symbol: '⌁', active: false },
  { label: 'Локальные данные', symbol: '▤', active: false },
]
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
        <div class="sidebar-heading">Инструменты</div>
        <nav class="sidebar-nav" aria-label="Основная навигация">
          <ul>
            <li v-for="item in navigationItems" :key="item.label">
              <a
                v-if="item.active"
                class="nav-item active"
                href="#workspace"
                aria-current="page"
              >
                <span class="nav-symbol" aria-hidden="true">{{ item.symbol }}</span>
                <span>{{ item.label }}</span>
              </a>
              <span v-else class="nav-item unavailable" aria-disabled="true">
                <span class="nav-symbol" aria-hidden="true">{{ item.symbol }}</span>
                <span>{{ item.label }}</span>
                <span class="nav-soon">Позже</span>
              </span>
            </li>
          </ul>
        </nav>

        <div class="sidebar-note">
          <span class="note-indicator" aria-hidden="true"></span>
          <p>Инструменты будут подключаться по мере развития проекта.</p>
        </div>
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
          <span class="workspace-badge">Предварительная версия</span>
        </div>

        <section class="map-placeholder" aria-labelledby="map-placeholder-title">
          <div class="placeholder-grid" aria-hidden="true"></div>
          <div class="placeholder-content">
            <span class="placeholder-icon" aria-hidden="true">⌖</span>
            <h2 id="map-placeholder-title">Карта будет подключена на следующем этапе</h2>
            <p>
              Сейчас подготовлена только оболочка приложения. Спутниковые снимки, базовая карта,
              каталог и геоданные ещё не подключены.
            </p>
          </div>
          <span class="placeholder-caption">РАБОЧИЙ ХОЛСТ · ОЖИДАЕТ ПОДКЛЮЧЕНИЯ КАРТЫ</span>
        </section>

        <footer class="workspace-status" role="status">
          <span><i class="status-dot" aria-hidden="true"></i> Интерфейс запущен</span>
          <span>Картографический модуль не подключён</span>
        </footer>
      </main>
    </div>
  </div>
</template>
