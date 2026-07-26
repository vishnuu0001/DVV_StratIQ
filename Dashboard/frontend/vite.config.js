// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend (vite.config.js)
// Date: 2026-04-08
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/dash/',
  server: {
    port: 5178,
    proxy: {
      '/api': {
        target: 'http://localhost:8087',
        changeOrigin: true,
        secure: false,
      },
      '/render': {
        target: 'http://localhost:8087',
        changeOrigin: true,
        secure: false,
      },
      '/metrics': {
        target: 'http://localhost:8087',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
