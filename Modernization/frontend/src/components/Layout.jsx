// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/components (Layout.jsx)
// Date: 2026-03-29
// ---------------------------------------------------------------------------
import { useEffect, useState } from 'react'
import { getLlmStatus } from '../api/client.js'
import Sidebar from './Sidebar.jsx'
import { modelDisplayName } from '../modelDisplay.js'

// Function: LlmStatusChip
function LlmStatusChip() {
  const [status, setStatus] = useState(null)

  useEffect(() => {
    getLlmStatus()
      .then(setStatus)
      .catch(() => setStatus({ available: false, recommended: 'deepseek-coder:6.7b' }))
  }, [])

  if (!status) return null

  return (
      <div className={`inline-flex items-center gap-2 rounded-full border px-3.5 py-2 text-xs shadow-sm backdrop-blur ${
        status.available
          ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
          : 'border-amber-200 bg-amber-50 text-amber-700'
      }`}>
        <span className={`h-2 w-2 shrink-0 rounded-full ${
          status.available ? 'animate-pulse bg-emerald-400' : 'bg-amber-400'
        }`} />
        {status.available ? (
          <>
            <strong className="font-semibold text-ink">{modelDisplayName(status.active_model || status.recommended)}</strong>
            <span className="text-ink-faint">·</span>
            <span className="text-ink-muted">GPU accelerated</span>
          </>
        ) : (
          <>
            <span>LLM offline</span>
            <span className="text-ink-faint">·</span>
            <span className="text-[11px] text-amber-300">Install the configured OpenSource LLM in Ollama</span>
          </>
        )}
      </div>
  )
}

// Function: Layout
export default function Layout({ children }) {
  return (
    <div className="flex h-screen overflow-hidden bg-bg">
      <Sidebar />
      <div className="relative flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="flex h-16 shrink-0 items-center justify-end border-b border-slate-200/80 bg-white/90 px-6 backdrop-blur-xl lg:px-8">
          <LlmStatusChip />
        </header>
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  )
}
