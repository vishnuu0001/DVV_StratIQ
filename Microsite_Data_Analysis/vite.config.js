// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Microsite_Data_Analysis — vite.config (vite.config.js)
// Date: 2025-07-30
// ---------------------------------------------------------------------------
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/mda/',
  server: { port: 5187, host: '0.0.0.0' },
  preview: { port: 5187, host: '0.0.0.0' },
});
