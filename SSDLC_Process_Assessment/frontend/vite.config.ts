// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend (vite.config.ts)
// Date: 2025-09-25
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/ssdlc/',
  server: {
    port: 5182,
    strictPort: true,
    proxy: {
      // CSM API calls: /api/csm/* → SSDLC backend (port 8091)
      '/api/csm': {
        target: 'http://localhost:8091',
        changeOrigin: true,
      },
      // Legacy SSDLC API calls (kept for backward compat)
      '/api/ssdlc': {
        target: 'http://localhost:8091',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ssdlc/, '/api'),
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})
