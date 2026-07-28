// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src (main.jsx)
// Date: 2026-06-02
// ---------------------------------------------------------------------------
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

const SHARED_THEME_HREF = `${import.meta.env.BASE_URL}strat-aqorynth-azure-theme.css?v=20260728-1`

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
    <BrowserRouter basename={routerBaseName}>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)
