// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend (vite.config.js)
// Date: 2025-11-07
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/novastra-itsm/',
  server: {
    port: 5177,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8086',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8086',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react':   ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui':      ['lucide-react', 'clsx'],
          'vendor-network': ['axios'],
        },
      },
    },
  }
})
