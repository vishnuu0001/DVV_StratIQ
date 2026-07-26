// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src (main.tsx)
// Date: 2025-09-12
// ---------------------------------------------------------------------------
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'

const SHARED_THEME_HREF = '/strat-aqorynth-azure-theme.css?v=20260726-6'

// Function: ensureSharedTheme
function ensureSharedTheme() {
  if (document.querySelector(`link[data-stratiq-theme][href="${SHARED_THEME_HREF}"]`)) {
    return
  }
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = SHARED_THEME_HREF
  link.setAttribute('data-stratiq-theme', 'true')
  document.head.appendChild(link)
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

ensureSharedTheme()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
