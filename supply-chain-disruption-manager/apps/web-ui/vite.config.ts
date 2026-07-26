// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui (vite.config.ts)
// Date: 2026-01-12
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE_PATH || '/scm/',
  server: {
    port: 5173,
    proxy: {
      '/api/kg': { target: process.env.VITE_KG_API_URL || 'http://localhost:8001', rewrite: (p) => p.replace('/api/kg', '') },
      '/api/inspector': { target: process.env.VITE_INSPECTOR_API_URL || 'http://localhost:8003', rewrite: (p) => p.replace('/api/inspector', '') },
      '/api/agents': { target: process.env.VITE_AGENT_API_URL || 'http://localhost:8002', rewrite: (p) => p.replace('/api/agents', '') },
    }
  }
})
