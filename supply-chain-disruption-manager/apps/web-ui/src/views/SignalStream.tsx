// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/views (SignalStream.tsx)
// Date: 2025-09-08
// ---------------------------------------------------------------------------
import React, { useState, useRef, useCallback, useEffect } from 'react'
import { Filter, Play, Pause, RefreshCw } from 'lucide-react'
import { SeverityBadge } from '../components/SeverityBadge'
import { useAppStore } from '../store/useAppStore'
import { listEvents, getEventStreamURL } from '../api/inspector'
import { createSSEStream } from '../api/sse'
import type { CanonicalEvent } from '../api/inspector'
import { MAX_BUFFER } from '../hooks/useEventStream'

const SEVERITIES = ['', 'critical', 'high', 'med', 'low', 'info']

// Function: formatTs
function formatTs(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString('en-US', {
      hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit',
    })
  } catch {
    return ts
  }
}

// Function: SignalStream
export function SignalStream() {
  const selectEvent = useAppStore((s) => s.selectEvent)
  const [events, setEvents] = useState<CanonicalEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [autoScroll, setAutoScroll] = useState(true)
  const [severityFilter, setSeverityFilter] = useState('')
  const [sourceFilter, setSourceFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [nodeFilter, setNodeFilter] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const newIds = useRef<Set<string>>(new Set())
  const incrementCount = useAppStore((s) => s.incrementEventCount)

  const addEvent = useCallback((evt: CanonicalEvent) => {
    setEvents((prev) => {
      if (prev.some((e) => e.event_id === evt.event_id)) return prev
      newIds.current.add(evt.event_id)
      setTimeout(() => newIds.current.delete(evt.event_id), 500)
      incrementCount()
      return [evt, ...prev].slice(0, MAX_BUFFER)
    })
  }, [incrementCount])

  useEffect(() => {
    // Function: loadInitial
    async function loadInitial() {
      setLoading(true)
      try {
        const result = await listEvents({ limit: 50 })
        setEvents(result.items)
      } catch {
        // ignore
      } finally {
        setLoading(false)
      }
    }
    void loadInitial()
  }, [])

  useEffect(() => {
    const cleanup = createSSEStream(getEventStreamURL(), (type, data) => {
      if (type === 'event' || type === 'message') {
        addEvent(data as CanonicalEvent)
      }
    })
    return cleanup
  }, [addEvent])

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = 0
    }
  }, [events, autoScroll])

  const filtered = events.filter((e) => {
    if (severityFilter && e.severity !== severityFilter) return false
    if (sourceFilter && !e.source_system.toLowerCase().includes(sourceFilter.toLowerCase())) return false
    if (typeFilter && !e.event_type.toLowerCase().includes(typeFilter.toLowerCase())) return false
    if (nodeFilter && (!e.root_node_id || !e.root_node_id.toLowerCase().includes(nodeFilter.toLowerCase()))) return false
    return true
  })

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Filter bar */}
      <div className="px-4 py-3 border-b border-border bg-surface flex items-center gap-3 flex-wrap">
        <Filter size={14} className="text-text-3 shrink-0" />

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-2 focus:outline-none focus:border-border-hi"
        >
          <option value="">All severities</option>
          {SEVERITIES.filter(Boolean).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Source system…"
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
          className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-2 placeholder-text-3 focus:outline-none focus:border-border-hi w-32"
        />

        <input
          type="text"
          placeholder="Event type…"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-2 placeholder-text-3 focus:outline-none focus:border-border-hi w-36"
        />

        <input
          type="text"
          placeholder="Root node ID…"
          value={nodeFilter}
          onChange={(e) => setNodeFilter(e.target.value)}
          className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-2 placeholder-text-3 focus:outline-none focus:border-border-hi w-32"
        />

        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-text-3 font-mono">{filtered.length} events</span>
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded border text-xs transition-colors ${
              autoScroll
                ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-400'
                : 'border-border text-text-3 hover:text-text'
            }`}
          >
            {autoScroll ? <Pause size={11} /> : <Play size={11} />}
            {autoScroll ? 'Auto-scroll' : 'Paused'}
          </button>
          <button
            onClick={async () => {
              setLoading(true)
              try {
                const result = await listEvents({ limit: 50 })
                setEvents(result.items)
              } catch {
                // ignore
              } finally {
                setLoading(false)
              }
            }}
            className="p-1.5 rounded border border-border hover:border-border-hi text-text-3 hover:text-text transition-colors"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Table header */}
      <div className="px-4 py-2 border-b border-border bg-surface-2 grid grid-cols-[120px_1fr_100px_120px_120px] gap-3 text-[10px] text-text-3 uppercase tracking-widest">
        <span>Time</span>
        <span>Event Type</span>
        <span>Severity</span>
        <span>Source</span>
        <span>Root Node</span>
      </div>

      {/* Table body */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {loading && filtered.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-text-3 text-sm">
            Loading events…
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-text-3 text-sm gap-2">
            <div>No events match filters</div>
            <div className="text-xs">Connect backend to stream live events</div>
          </div>
        ) : (
          <div className="divide-y divide-border/30">
            {filtered.map((evt) => (
              <button
                key={evt.event_id}
                onClick={() => selectEvent(evt)}
                className={`w-full px-4 py-2.5 grid grid-cols-[120px_1fr_100px_120px_120px] gap-3 text-left hover:bg-surface-2 transition-colors ${
                  newIds.current.has(evt.event_id) ? 'row-new' : ''
                }`}
              >
                <span className="font-mono text-xs text-text-3 tabular-nums">{formatTs(evt.ingested_at)}</span>
                <span className="text-xs text-text truncate">{evt.event_type}</span>
                <span><SeverityBadge severity={evt.severity} /></span>
                <span className="text-xs text-text-2 truncate">{evt.source_system}</span>
                <span className="font-mono text-xs text-text-3 truncate">{evt.root_node_id ?? '—'}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
