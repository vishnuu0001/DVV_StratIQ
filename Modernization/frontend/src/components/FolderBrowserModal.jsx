// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/components (FolderBrowserModal.jsx)
// Date: 2026-04-04
// ---------------------------------------------------------------------------
import { useCallback, useEffect, useState } from 'react'
import { getFsLs } from '../api/client.js'

// Function: FolderBrowserModal
export default function FolderBrowserModal({ onSelect, onClose }) {
  const [current, setCurrent] = useState('')
  const [parent, setParent]   = useState(null)
  const [dirs, setDirs]       = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  const browse = useCallback(async (path) => {
    setLoading(true)
    setError('')
    try {
      const data = await getFsLs(path || '')
      setCurrent(data.current || '')
      setParent(data.parent ?? null)
      setDirs(data.dirs || [])
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not list directory')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { browse('') }, [browse])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="flex max-h-[80vh] w-full max-w-xl flex-col overflow-hidden rounded-2xl border border-hairline bg-surface shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-hairline px-5 py-4">
          <h3 className="text-sm font-semibold text-ink">Browse Folders</h3>
          <button type="button" onClick={onClose} className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-faint hover:bg-white/10 hover:text-ink text-lg leading-none">×</button>
        </div>
        {/* Path bar */}
        <div className="flex items-center gap-2 border-b border-hairline bg-white/[0.02] px-4 py-2">
          <button
            type="button"
            disabled={!parent || loading}
            onClick={() => browse(parent)}
            className="shrink-0 rounded-lg bg-white/[0.05] px-2.5 py-1 text-xs font-medium text-ink-dim ring-1 ring-hairline transition hover:bg-white/[0.1] disabled:cursor-not-allowed disabled:opacity-30"
          >
            ↑ Up
          </button>
          <span className="flex-1 truncate font-mono text-xs text-ink-muted">{current || 'My Computer'}</span>
        </div>
        {/* Dir list */}
        <div className="min-h-[220px] flex-1 overflow-y-auto px-3 py-2">
          {loading && (
            <div className="flex h-32 items-center justify-center">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-gold border-t-transparent" />
            </div>
          )}
          {!loading && error && <p className="py-8 text-center text-sm text-red-400">{error}</p>}
          {!loading && !error && dirs.length === 0 && <p className="py-8 text-center text-sm text-ink-faint">No subfolders found.</p>}
          {!loading && !error && dirs.map((dir) => (
            <button
              key={dir.path}
              type="button"
              onClick={() => browse(dir.path)}
              className="group mb-0.5 flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left transition hover:bg-white/[0.06]"
            >
              <span className="shrink-0 text-base">{dir.is_drive ? '💾' : '📁'}</span>
              <span className="flex-1 truncate font-mono text-sm text-ink-dim">{dir.name}</span>
              <span className="shrink-0 text-ink-faint group-hover:text-ink-dim">›</span>
            </button>
          ))}
        </div>
        {/* Selected path */}
        <div className="border-t border-hairline bg-white/[0.02] px-5 py-3">
          <p className="mb-1 text-xs text-ink-faint">Selected folder:</p>
          <p className="min-h-[1.25rem] truncate font-mono text-xs text-gold-soft">{current || '—'}</p>
        </div>
        {/* Actions */}
        <div className="flex justify-end gap-2 border-t border-hairline px-5 py-3">
          <button type="button" onClick={onClose} className="rounded-xl bg-white/[0.06] px-4 py-2 text-sm font-medium text-ink-dim transition hover:bg-white/[0.1]">Cancel</button>
          <button
            type="button"
            disabled={!current}
            onClick={() => { onSelect(current); onClose() }}
            className="rounded-xl bg-gold px-5 py-2 text-sm font-semibold text-bg transition hover:bg-gold-soft disabled:cursor-not-allowed disabled:opacity-40"
          >
            Select folder
          </button>
        </div>
      </div>
    </div>
  )
}
