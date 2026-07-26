// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src (main.tsx)
// Date: 2025-09-21
// ---------------------------------------------------------------------------
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { consumePortalTokenFromHash } from './lib/portalAuth'
import './index.css'

// Function: retryTransientQuery
function retryTransientQuery(failureCount: number, error: any): boolean {
  const status = error?.response?.status
  if ([401, 403].includes(status)) return false
  if ([502, 503, 504].includes(status)) return failureCount < 3
  return failureCount < 1
}

// Consume the portal SSO token before React Query children mount and issue
// their initial API requests.
consumePortalTokenFromHash()

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: retryTransientQuery,
      retryDelay: (attempt) => Math.min(500 * 2 ** attempt, 3000),
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename="/tf">
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
