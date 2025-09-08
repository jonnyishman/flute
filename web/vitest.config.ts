import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  cacheDir: '.vitest',
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    // Skip CSS processing in tests for speed
    css: false,
    // Faster file watching
    watch: false,
    // Reduce test timeout for faster feedback
    testTimeout: 10000
  },
  resolve: {
    alias: {
      'virtual:pwa-register/react': new URL('./src/test/mocks/pwa-register.ts', import.meta.url).pathname
    }
  }
})