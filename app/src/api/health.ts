import { API_BASE_PATH, type HealthResponse } from './config'

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(API_BASE_PATH + '/health')

  if (!response.ok) {
    throw new Error('Health request failed with HTTP ' + response.status)
  }

  return (await response.json()) as HealthResponse
}
