<script setup lang="ts">
import { computed, ref } from 'vue'
import { createSearchRequest } from '../types/catalog'

const props = defineProps({
  aoi: {
    type: Array,
    default: null,
  },
})

const emit = defineEmits(['submit', 'reset'])

const dateFrom = ref('')
const dateTo = ref('')
const cloudCover = ref('100')

/** @param {string} value */
function isCalendarDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return false
  }

  const parsed = new Date(`${value}T00:00:00Z`)
  return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value
}

const errors = computed(() => {
  const result = {
    dateFrom: '',
    dateTo: '',
    dateRange: '',
    cloudCover: '',
    aoi: '',
  }

  if (!dateFrom.value) {
    result.dateFrom = 'Укажите начальную дату.'
  } else if (!isCalendarDate(dateFrom.value)) {
    result.dateFrom = 'Проверьте начальную дату.'
  }

  if (!dateTo.value) {
    result.dateTo = 'Укажите конечную дату.'
  } else if (!isCalendarDate(dateTo.value)) {
    result.dateTo = 'Проверьте конечную дату.'
  }

  if (!result.dateFrom && !result.dateTo && dateFrom.value > dateTo.value) {
    result.dateRange = 'Начальная дата не может быть позже конечной.'
  }

  const cloudValue = Number(cloudCover.value)
  if (
    cloudCover.value.trim() === '' ||
    !Number.isInteger(cloudValue) ||
    cloudValue < 0 ||
    cloudValue > 100
  ) {
    result.cloudCover = 'Облачность должна быть целым числом от 0 до 100%.'
  }

  if (
    !props.aoi ||
    props.aoi.length !== 4 ||
    !props.aoi.every(Number.isFinite) ||
    props.aoi[2] <= props.aoi[0] ||
    props.aoi[3] <= props.aoi[1]
  ) {
    result.aoi = 'Нарисуйте прямоугольную область интереса на карте.'
  }

  return result
})

const canSubmit = computed(() => Object.values(errors.value).every((message) => !message))

function submit() {
  if (!canSubmit.value || !props.aoi) {
    return
  }

  const request = createSearchRequest({
    bbox: props.aoi,
    dateFrom: dateFrom.value,
    dateTo: dateTo.value,
    cloudCover: Number(cloudCover.value),
  })
  emit('submit', request)
}

function reset() {
  dateFrom.value = ''
  dateTo.value = ''
  cloudCover.value = '100'
  emit('reset')
}
</script>

<template>
  <form class="search-form" @submit.prevent="submit">
    <p class="search-intro">Параметры поиска Sentinel-2 L2A. Отправка запроса пока не подключена.</p>

    <div class="search-field">
      <label for="search-date-from">Дата от</label>
      <input
        id="search-date-from"
        v-model="dateFrom"
        type="date"
        :aria-invalid="Boolean(errors.dateFrom || errors.dateRange)"
      />
      <p v-if="errors.dateFrom" class="field-error" role="alert">
        {{ errors.dateFrom }}
      </p>
    </div>

    <div class="search-field">
      <label for="search-date-to">Дата до</label>
      <input
        id="search-date-to"
        v-model="dateTo"
        type="date"
        :aria-invalid="Boolean(errors.dateTo || errors.dateRange)"
      />
      <p v-if="errors.dateTo" class="field-error" role="alert">
        {{ errors.dateTo }}
      </p>
      <p v-if="errors.dateRange" class="field-error" role="alert">
        {{ errors.dateRange }}
      </p>
    </div>

    <div class="search-field">
      <label for="search-cloud-cover">Максимальная облачность, %</label>
      <input
        id="search-cloud-cover"
        v-model="cloudCover"
        type="number"
        min="0"
        max="100"
        step="1"
        inputmode="numeric"
        :aria-invalid="Boolean(errors.cloudCover)"
      />
      <p v-if="errors.cloudCover" class="field-error" role="alert">
        {{ errors.cloudCover }}
      </p>
    </div>

    <section class="search-aoi" aria-labelledby="search-aoi-title">
      <h3 id="search-aoi-title">Область интереса</h3>
      <p v-if="props.aoi" class="aoi-value">
        W {{ props.aoi[0].toFixed(5) }} · S {{ props.aoi[1].toFixed(5) }} · E {{ props.aoi[2].toFixed(5) }} · N
        {{ props.aoi[3].toFixed(5) }}
      </p>
      <p v-else class="aoi-empty">Область не выбрана.</p>
      <p v-if="errors.aoi" class="field-error" role="alert">
        {{ errors.aoi }}
      </p>
    </section>

    <div class="search-actions">
      <button class="search-submit" type="submit" :disabled="!canSubmit">Подготовить поиск</button>
      <button class="search-reset" type="button" @click="reset">Сбросить</button>
    </div>

    <p class="search-note" role="status">Здесь формируется SearchRequest. Сетевой поиск не выполняется.</p>
  </form>
</template>

<style scoped>
.search-form {
  display: grid;
  gap: var(--space-11);
  padding-top: var(--space-13);
}

.search-intro,
.search-note,
.aoi-empty,
.aoi-value {
  margin: 0;
  color: var(--color-muted);
  font-size: var(--font-size-md);
  line-height: 1.6;
}

.search-field {
  display: grid;
  gap: var(--space-5);
}

.search-field label,
.search-aoi h3 {
  color: var(--color-text);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

.search-field input {
  width: 100%;
  min-height: 42px;
  padding: 0 var(--space-7);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  background: var(--color-background-deep);
  font: inherit;
  color-scheme: dark;
}

.search-field input[aria-invalid='true'] {
  border-color: var(--color-error);
}

.field-error {
  margin: 0;
  color: var(--color-error);
  font-size: var(--font-size-sm);
  line-height: 1.5;
}

.search-aoi {
  display: grid;
  gap: var(--space-5);
  padding: var(--space-9);
  border: 1px solid rgba(var(--color-border-rgb), 0.18);
  border-radius: var(--radius-md);
  background: rgba(var(--color-background-rgb), 0.35);
}

.search-aoi h3 {
  margin: 0;
}

.aoi-value {
  overflow-wrap: anywhere;
  font-variant-numeric: tabular-nums;
}

.search-actions {
  display: grid;
  gap: var(--space-5);
}

.search-actions button {
  min-height: 44px;
  padding: 0 var(--space-9);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  background: var(--color-surface-raised);
  font: inherit;
  cursor: pointer;
  touch-action: manipulation;
}

.search-actions .search-submit {
  border-color: rgba(var(--color-primary-rgb), 0.4);
  color: var(--color-background-deep);
  background: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.search-actions .search-submit:disabled {
  border-color: var(--color-border);
  color: var(--color-subtle);
  background: var(--color-surface);
  cursor: not-allowed;
}

.search-note {
  padding-top: var(--space-5);
  border-top: 1px solid rgba(var(--color-border-rgb), 0.12);
}
</style>
