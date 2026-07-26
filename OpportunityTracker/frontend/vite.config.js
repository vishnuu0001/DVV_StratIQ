// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend (vite.config.js)
// Date: 2025-09-22
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/ot/',
  server: {
    port: 5183,
    host: '0.0.0.0',
    proxy: {
      '/api/ot': {
        target: 'http://localhost:8092',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ot/, '/api'),
      },
      '/health': { target: 'http://localhost:8092', changeOrigin: true },
    },
  },
  build: { outDir: 'dist', sourcemap: false },
});
