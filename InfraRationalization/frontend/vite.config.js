// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend (vite.config.js)
// Date: 2026-06-14
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/infra/',
  server: {
    port: 5174,
    strictPort: true,
    proxy: {
      '/api': 'http://localhost:8083',
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (!id.includes('node_modules/')) return
          const seg = id.split('node_modules/').pop()
          const parts = seg.split('/')
          const pkg = parts[0].startsWith('@') ? `${parts[0]}/${parts[1]}` : parts[0]

          // Core React runtime — keep small, loaded first
          if (pkg === 'react' || pkg === 'react-dom' || pkg === 'scheduler') return 'vendor-react'

          // Router (small, often needed early)
          if (pkg === 'react-router-dom' || pkg.startsWith('@remix-run') || pkg === 'react-router') return 'vendor-router'

          // Recharts + all D3 sub-packages (largest vendor chunk, lazy-loaded with ScanDetailPage)
          if (pkg === 'recharts' || pkg.startsWith('d3-') || pkg === 'victory-vendor' || pkg === 'd3') return 'vendor-charts'

          // Icons
          if (pkg === 'lucide-react') return 'vendor-icons'

          // Small utility libs
          if (pkg === 'axios') return 'vendor-axios'
          if (pkg === 'react-hot-toast') return 'vendor-toast'

          // Everything else gets its own small chunk
          return `vendor-${pkg.replace(/^@/, '').replace('/', '-')}`
        },
      },
    },
  },
})
