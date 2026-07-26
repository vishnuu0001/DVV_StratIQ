// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/views (ReplayDLQ.tsx)
// Date: 2026-01-12
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback } from 'react'
import { RotateCcw, Upload, AlertCircle, CheckCircle, RefreshCw, Inbox } from 'lucide-react'
import { replayById, listEvents, ingestManual } from '../api/inspector'
import type { CanonicalEvent } from '../api/inspector'
import { SeverityBadge } from '../components/SeverityBadge'
import { useAppStore } from '../store/useAppStore'

// Function: formatTs
function formatTs(ts: string): string {
  try {
    return new Date(ts).toLocaleString('en-US', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
    })
  } catch {
    return ts
  }
}

const SAMPLE_MANUAL_EVENT = JSON.stringify({
  event_type: 'supplier.delivery.delayed',
  source_system: 'manual',
  severity: 'high',
  root_node_id: 'SUP-001',
  payload: {
    supplier_id: 'SUP-001',
    delay_days: 5,
    reason: 'Weather event',
  },
  tags: { source: 'manual', environment: 'prod' },
}, null, 2)

// Function: ReplayDLQ
export function ReplayDLQ() {
  const selectEvent = useAppStore((s) => s.selectEvent)

  // Replay by ID
  const [replayId, setReplayId] = useState('')
  const [replayStatus, setReplayStatus] = useState<'idle' | 'loading' | 'ok' | 'error'>('idle')
  const [replayMsg, setReplayMsg] = useState('')

  // Manual ingest
  const [manualJson, setManualJson] = useState(SAMPLE_MANUAL_EVENT)
  const [manualStatus, setManualStatus] = useState<'idle' | 'loading' | 'ok' | 'error'>('idle')
  const [manualResult, setManualResult] = useState('')
  const [jsonError, setJsonError] = useState('')

  // DLQ events
  const [dlqEvents, setDlqEvents] = useState<CanonicalEvent[]>([])
  const [dlqLoading, setDlqLoading] = useState(false)

  // Per-row replay state
  const [replayingIds, setReplayingIds] = useState<Set<string>>(new Set())
  const [replayResults, setReplayResults] = useState<Map<string, 'ok' | 'error'>>(new Map())

  // Invalid events
  const [invalidEvents, setInvalidEvents] = useState<CanonicalEvent[]>([])

  const loadDLQ = useCallback(async () => {
    setDlqLoading(true)
    try {
      const [dlqResult, invalidResult] = await Promise.allSettled([
        listEvents({ publish_status: 'dlq', limit: 20 }),
        listEvents({ validation_status: 'invalid', limit: 20 }),
      ])
      if (dlqResult.status === 'fulfilled') setDlqEvents(dlqResult.value.items)
      if (invalidResult.status === 'fulfilled') setInvalidEvents(invalidResult.value.items)
    } finally {
      setDlqLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadDLQ()
    const interval = setInterval(() => void loadDLQ(), 20000)
    return () => clearInterval(interval)
  }, [loadDLQ])

  // Function: handleReplay
  async function handleReplay() {
    if (!replayId.trim()) return
    setReplayStatus('loading')
    setReplayMsg('')
    try {
      const result = await replayById(replayId.trim())
      setReplayStatus('ok')
      setReplayMsg(`Replayed: ${result.status}`)
    } catch (err) {
      setReplayStatus('error')
      setReplayMsg(err instanceof Error ? err.message : 'Replay failed')
    }
  }

  // Function: handleManualIngest
  async function handleManualIngest() {
    setJsonError('')
    let parsed: unknown
    try {
      parsed = JSON.parse(manualJson)
    } catch {
      setJsonError('Invalid JSON')
      return
    }
    setManualStatus('loading')
    setManualResult('')
    try {
      const result = await ingestManual(parsed as object)
      setManualStatus('ok')
      setManualResult(`Ingested event_id: ${result.event_id}`)
    } catch (err) {
      setManualStatus('error')
      setManualResult(err instanceof Error ? err.message : 'Ingest failed')
    }
  }

  // Function: replayDLQEvent
  async function replayDLQEvent(eventId: string) {
    setReplayingIds((prev) => new Set(prev).add(eventId))
    setReplayResults((prev) => { const m = new Map(prev); m.delete(eventId); return m })
    try {
      await replayById(eventId)
      setReplayResults((prev) => new Map(prev).set(eventId, 'ok'))
      void loadDLQ()
    } catch {
      setReplayResults((prev) => new Map(prev).set(eventId, 'error'))
    } finally {
      setReplayingIds((prev) => { const s = new Set(prev); s.delete(eventId); return s })
    }
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
        <div>
          <h1 className="font-display text-xl text-text mb-1">Replay & DLQ</h1>
          <p className="text-sm text-text-3">Replay events, ingest manually, manage dead-letter queue</p>
        </div>

        {/* Two columns top */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Replay by ID */}
          <div className="bg-surface border border-border rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2">
              <RotateCcw size={16} className="text-cyan-400" />
              <span className="text-sm font-medium">Replay by Event ID</span>
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={replayId}
                onChange={(e) => { setReplayId(e.target.value); setReplayStatus('idle') }}
                placeholder="evt-uuid-here…"
                className="flex-1 bg-surface-2 border border-border rounded px-3 py-1.5 text-xs text-text placeholder-text-3 font-mono focus:outline-none focus:border-border-hi"
              />
              <button
                onClick={() => void handleReplay()}
                disabled={replayStatus === 'loading' || !replayId.trim()}
                className="px-3 py-1.5 rounded border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 text-xs font-medium transition-colors disabled:opacity-40"
              >
                {replayStatus === 'loading' ? 'Replaying…' : 'Replay'}
              </button>
            </div>
            {replayMsg && (
              <div className={`flex items-center gap-2 text-xs ${replayStatus === 'ok' ? 'text-green-400' : 'text-red-400'}`}>
                {replayStatus === 'ok' ? <CheckCircle size={12} /> : <AlertCircle size={12} />}
                {replayMsg}
              </div>
            )}
          </div>

          {/* Manual ingest */}
          <div className="bg-surface border border-border rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Upload size={16} className="text-amber-400" />
              <span className="text-sm font-medium">Upload JSON Event</span>
            </div>
            <div className="relative">
              <textarea
                value={manualJson}
                onChange={(e) => { setManualJson(e.target.value); setJsonError(''); setManualStatus('idle') }}
                className="w-full bg-surface-2 border border-border rounded px-3 py-2 text-xs text-text font-mono resize-none focus:outline-none focus:border-border-hi"
                rows={7}
                spellCheck={false}
              />
              {jsonError && (
                <div className="text-xs text-red-400 mt-1 flex items-center gap-1">
                  <AlertCircle size={11} /> {jsonError}
                </div>
              )}
            </div>
            <button
              onClick={() => void handleManualIngest()}
              disabled={manualStatus === 'loading'}
              className="w-full py-1.5 rounded border border-amber-500/30 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 text-xs font-medium transition-colors disabled:opacity-40"
            >
              {manualStatus === 'loading' ? 'Ingesting…' : 'Ingest Event'}
            </button>
            {manualResult && (
              <div className={`flex items-center gap-2 text-xs ${manualStatus === 'ok' ? 'text-green-400' : 'text-red-400'}`}>
                {manualStatus === 'ok' ? <CheckCircle size={12} /> : <AlertCircle size={12} />}
                <span className="font-mono">{manualResult}</span>
              </div>
            )}
          </div>
        </div>

        {/* DLQ Events */}
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle size={15} className="text-red-400" />
              <span className="text-sm font-medium">Dead Letter Queue</span>
              <span className="text-xs font-mono text-text-3">{dlqEvents.length} events</span>
            </div>
            <button
              onClick={() => void loadDLQ()}
              className="p-1.5 rounded hover:bg-surface-2 text-text-3"
            >
              <RefreshCw size={13} className={dlqLoading ? 'animate-spin' : ''} />
            </button>
          </div>
          {dlqEvents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-text-3 gap-2">
              <Inbox size={28} className="opacity-30" />
              <div className="text-sm">DLQ is empty</div>
            </div>
          ) : (
            <div className="divide-y divide-border/30">
              {dlqEvents.map((evt) => (
                <div key={evt.event_id} className="px-4 py-3 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-mono text-xs text-text-3 truncate">{evt.event_id}</span>
                      <SeverityBadge severity={evt.severity} />
                    </div>
                    <div className="text-xs text-text-2">{evt.event_type}</div>
                    <div className="text-[10px] text-text-3 font-mono">{formatTs(evt.ingested_at)}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => selectEvent(evt)}
                      className="text-xs px-2 py-1 rounded border border-border hover:border-border-hi text-text-2 hover:text-text transition-colors"
                    >
                      Inspect
                    </button>
                    {replayResults.get(evt.event_id) === 'ok' && (
                      <span title="Replayed successfully"><CheckCircle size={13} className="text-green-400 shrink-0" /></span>
                    )}
                    {replayResults.get(evt.event_id) === 'error' && (
                      <span title="Replay failed"><AlertCircle size={13} className="text-red-400 shrink-0" /></span>
                    )}
                    <button
                      onClick={() => void replayDLQEvent(evt.event_id)}
                      disabled={replayingIds.has(evt.event_id)}
                      className="text-xs px-2 py-1 rounded border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      {replayingIds.has(evt.event_id) ? 'Replaying…' : 'Replay'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Invalid events */}
        {invalidEvents.length > 0 && (
          <div className="bg-surface border border-red-500/20 rounded-lg overflow-hidden">
            <div className="px-4 py-3 border-b border-border flex items-center gap-2">
              <AlertCircle size={15} className="text-red-400" />
              <span className="text-sm font-medium">Invalid Events</span>
              <span className="text-xs font-mono text-text-3">{invalidEvents.length}</span>
            </div>
            <div className="divide-y divide-border/30">
              {invalidEvents.map((evt) => (
                <div key={evt.event_id} className="px-4 py-3 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <span className="font-mono text-xs text-text-3">{evt.event_id}</span>
                    <div className="text-xs text-red-400/70">{evt.event_type}</div>
                    <div className="text-[10px] text-text-3">{formatTs(evt.ingested_at)}</div>
                  </div>
                  <button
                    onClick={() => selectEvent(evt)}
                    className="text-xs px-2 py-1 rounded border border-border text-text-2 hover:text-text transition-colors"
                  >
                    Inspect
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
