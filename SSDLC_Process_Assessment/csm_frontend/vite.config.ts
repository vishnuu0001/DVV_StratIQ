// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend (vite.config.ts)
// Date: 2025-10-15
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8092',
    },
  },
  build: {
    outDir: 'dist',
  },
})
