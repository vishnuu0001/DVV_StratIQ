// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend (vite.config.js)
// Date: 2026-06-15
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/ca/',
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8082',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/codeanalysis/, '/api'),
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (!id.includes('node_modules/')) return;
          const seg = id.split('node_modules/').pop();
          const parts = seg.split('/');
          const pkg = parts[0].startsWith('@') ? `${parts[0]}/${parts[1]}` : parts[0];
          if (pkg === 'react' || pkg === 'react-dom') return 'vendor-react';
          if (pkg === 'recharts' || pkg.startsWith('d3-') || pkg === 'victory-vendor') return 'vendor-charts';
          if (pkg === 'framer-motion') return 'vendor-animation';
          if (pkg === 'lucide-react') return 'vendor-icons';
          return `vendor-${pkg.replace(/^@/, '').replace('/', '-')}`;
        },
      },
    },
  },
})
