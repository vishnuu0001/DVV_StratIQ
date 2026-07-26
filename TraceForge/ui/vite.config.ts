// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui (vite.config.ts)
// Date: 2025-07-31
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/tf/',
  server: {
    port: 5186,
    strictPort: true,
    proxy: {
      '/api/tf': {
        target: 'http://localhost:8095',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/tf/, '/api'),
      },
    },
  },
  build: {
    outDir: 'dist',
    // IIS serves this directory live. Vite's default emptyOutDir=true creates a
    // deployment gap where /tf/index.html or a chunk can disappear while a
    // rebuild is running. Hashed assets are safe to retain; index.html is
    // replaced only after the new bundle has been written.
    emptyOutDir: false,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined
          if (id.includes('@monaco-editor')) return 'editor'
          if (id.includes('reactflow')) return 'diagrams'
          return 'vendor'
        },
      },
    },
  },
})
