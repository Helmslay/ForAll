import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')

  return {
    plugins: [vue()],
    server: {
      proxy: {
        '/api': {
          target: env.SENTINEL_API_PROXY_TARGET || 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
    test: {
      environment: 'jsdom',
      include: ['src/**/*.spec.ts'],
    },
  }
})
