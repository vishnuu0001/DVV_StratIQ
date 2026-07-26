// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src (main.jsx)
// Date: 2026-01-14
// ---------------------------------------------------------------------------
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
    <Toaster
      position="bottom-right"
      toastOptions={{
        style: {
          background: '#1a1d26',
          color: '#e0e0e0',
          border: '1px solid #2a2d3e',
          borderRadius: '12px',
          fontSize: '14px',
        },
      }}
    />
  </React.StrictMode>
)
