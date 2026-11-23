import { ref } from 'vue'
import { CatalogApiError, searchCatalog } from '../api/catalog'
import type { SearchRequest, SearchResponse } from '../types/catalog'

export function useCatalogSearch() {
  const loading = ref(false)
  const error = ref('')
  const response = ref<SearchResponse | null>(null)
  const activeRequest = ref<SearchRequest | null>(null)
  let sequence = 0

  function isAbortError(value: unknown) {
    return value instanceof Error && value.name === 'AbortError'
  }

  async function runSearch(request: SearchRequest, append = false) {
    const currentSequence = ++sequence
    loading.value = true
    error.value = ''
    if (!append) {
      activeRequest.value = { ...request, cursor: null }
      response.value = null
    }

    try {
      const result = await searchCatalog(request)
      if (currentSequence !== sequence) return

      if (append && response.value) {
        const existing = new Set(response.value.items.map((scene) => scene.key))
        const uniqueItems = result.items.filter((scene) => !existing.has(scene.key))
        response.value = {
          ...result,
          items: [...response.value.items, ...uniqueItems],
          partial: result.partial || response.value.partial,
        }
      } else {
        response.value = result
      }
    } catch (cause) {
      if (currentSequence !== sequence || isAbortError(cause)) return
      error.value = cause instanceof CatalogApiError ? cause.message : 'Не удалось выполнить поиск каталога.'
    } finally {
      if (currentSequence === sequence) loading.value = false
    }
  }

  function handleSearch(request: SearchRequest) {
    void runSearch(request)
  }

  function loadMore() {
    const cursor = response.value?.next_cursor
    if (!cursor || !activeRequest.value || loading.value) return
    void runSearch({ ...activeRequest.value, cursor }, true)
  }

  function retrySearch() {
    if (activeRequest.value) void runSearch(activeRequest.value)
  }

  function resetSearch() {
    sequence += 1
    loading.value = false
    error.value = ''
    response.value = null
    activeRequest.value = null
  }

  return { loading, error, response, handleSearch, loadMore, retrySearch, resetSearch }
}
