// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend (vite.config.js)
// Date: 2026-05-30
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/mod/',
  server: {
    port: 5175,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8084',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (!id.includes('node_modules/')) return;
          const seg = id.split('node_modules/').pop();
          const parts = seg.split('/');
          const pkg = parts[0].startsWith('@') ? `${parts[0]}/${parts[1]}` : parts[0];
          if (pkg === 'react' || pkg === 'react-dom') return 'vendor-react';
          if (pkg === 'react-router' || pkg === 'react-router-dom' || pkg.startsWith('@remix-run')) return 'vendor-router';
          if (pkg === 'recharts' || pkg.startsWith('d3-') || pkg === 'victory-vendor') return 'vendor-charts';
          if (pkg === 'lucide-react') return 'vendor-icons';
          return `vendor-${pkg.replace(/^@/, '').replace('/', '-')}`;
        },
      },
    },
  },
})
