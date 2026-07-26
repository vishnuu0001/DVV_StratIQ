// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src (main.jsx)
// Date: 2026-04-25
// ---------------------------------------------------------------------------
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import { AuthProvider } from './contexts/AuthContext.jsx'
import { ChatProvider } from './contexts/ChatContext.jsx'
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

const routerBaseName = import.meta.env.BASE_URL.replace(/\/$/, '') || '/'

ensureSharedTheme()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter basename={routerBaseName} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <ChatProvider>
          <App />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: { fontSize: '14px' },
            }}
          />
        </ChatProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
)

