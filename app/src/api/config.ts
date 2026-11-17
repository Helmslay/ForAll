export const API_BASE_PATH = '/api/v1' as const

export interface HealthResponse {
  status: 'ok'
  app_version: string
  timestamp: string
}
