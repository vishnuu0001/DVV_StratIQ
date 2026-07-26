// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend (vite.config.js)
// Date: 2025-12-02
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/lab/',
  build: {
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom'],
          three: ['three', '@react-three/fiber', '@react-three/drei'],
          vendor: ['axios'],
        },
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 7000,
    strictPort: true,
    allowedHosts: ['lab.stratapp.org'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
