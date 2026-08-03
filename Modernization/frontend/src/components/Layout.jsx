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
      .catch(() => setStatus({ available: false, recommended: 'qwen2.5-coder:3b' }))
  }, [])

  if (!status) return null

  return (
    <div className="flex items-start px-5 pt-4 pb-0">
      <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs shadow-sm ${
        status.available
          ? 'border-emerald-500/25 bg-emerald-500/[0.06] text-emerald-300'
          : 'border-amber-500/25 bg-amber-500/[0.06] text-amber-300'
      }`}>
        <span className={`h-2 w-2 shrink-0 rounded-full ${
          status.available ? 'animate-pulse bg-emerald-400' : 'bg-amber-400'
        }`} />
        {status.available ? (
          <>
            <strong className="font-semibold text-ink">{modelDisplayName(status.active_model || status.recommended)}</strong>
            <span className="text-ink-faint">·</span>
            <span className="text-ink-muted">GPU-powered</span>
          </>
        ) : (
          <>
            <span>LLM offline</span>
            <span className="text-ink-faint">·</span>
            <span className="text-[11px] text-amber-300">Install the configured OpenSource LLM in Ollama</span>
          </>
        )}
      </div>
    </div>
  )
}

// Function: Layout
export default function Layout({ children }) {
  return (
    <div className="flex h-screen overflow-hidden bg-bg">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <LlmStatusChip />
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  )
}
