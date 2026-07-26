// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (AdapterHealthCard.tsx)
// Date: 2026-06-20
// ---------------------------------------------------------------------------
import React from 'react'
import { Activity, AlertTriangle, WifiOff, Zap } from 'lucide-react'
import type { AdapterHealth } from '../api/inspector'
import { ingestManual } from '../api/inspector'

interface Props {
  adapter: AdapterHealth
}

// Function: StatusIcon
function StatusIcon({ status }: { status: AdapterHealth['status'] }) {
  if (status === 'healthy') return <div className="w-2 h-2 rounded-full bg-green-400" />
  if (status === 'degraded') return <div className="w-2 h-2 rounded-full bg-amber-400" />
  return <div className="w-2 h-2 rounded-full bg-red-500 dot-blink" />
}

// Function: formatTime
function formatTime(ts: string | null): string {
  if (!ts) return 'Never'
  try {
    const d = new Date(ts)
    const now = Date.now()
    const diff = now - d.getTime()
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' })
  } catch {
    return ts
  }
}

// Function: AdapterHealthCard
export function AdapterHealthCard({ adapter }: Props) {
  const [triggering, setTriggering] = React.useState(false)
  const [triggered, setTriggered] = React.useState(false)

  // Function: handleTriggerTest
  async function handleTriggerTest() {
    setTriggering(true)
    try {
      await ingestManual({
        event_type: `${adapter.name.toLowerCase().replace(/\s+/g, '.')}.test`,
        source_system: adapter.name,
        severity: 'info',
        payload: { test: true, adapter: adapter.name, triggered_at: new Date().toISOString() },
        tags: { source: 'manual-test' },
      })
      setTriggered(true)
      setTimeout(() => setTriggered(false), 3000)
    } catch {
      // ignore
    } finally {
      setTriggering(false)
    }
  }

  return (
    <div className={`bg-surface border rounded-lg p-4 flex flex-col gap-3 ${
      adapter.status === 'down'
        ? 'border-red-500/30'
        : adapter.status === 'degraded'
        ? 'border-amber-500/30'
        : 'border-border'
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <StatusIcon status={adapter.status} />
          <span className="font-medium text-sm">{adapter.name}</span>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded font-mono uppercase ${
          adapter.status === 'healthy' ? 'text-green-400 bg-green-500/10 border border-green-500/20' :
          adapter.status === 'degraded' ? 'text-amber-400 bg-amber-500/10 border border-amber-500/20' :
          'text-red-400 bg-red-500/10 border border-red-500/20'
        }`}>
          {adapter.status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-1.5 text-text-2">
          <Activity size={12} className="text-cyan-400/70" />
          <span>{adapter.events_last_5m} events/5m</span>
        </div>
        <div className="flex items-center gap-1.5 text-text-2">
          <AlertTriangle size={12} className="text-amber-400/70" />
          <span>{(adapter.error_rate * 100).toFixed(1)}% errors</span>
        </div>
        <div className="flex items-center gap-1.5 text-text-2 col-span-2">
          <WifiOff size={12} className="text-text-3" />
          <span>Last event: {formatTime(adapter.last_event_at)}</span>
        </div>
      </div>

      {!adapter.enabled && (
        <div className="text-xs text-text-3 font-mono uppercase bg-surface-2 rounded px-2 py-1 text-center">
          Disabled
        </div>
      )}

      <button
        onClick={() => void handleTriggerTest()}
        disabled={triggering || !adapter.enabled}
        className="flex items-center justify-center gap-1.5 text-xs py-1.5 px-3 rounded border border-border hover:border-border-hi hover:bg-surface-2 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Zap size={12} className={triggered ? 'text-green-400' : 'text-amber-400'} />
        {triggering ? 'Sending…' : triggered ? 'Sent!' : 'Trigger Test'}
      </button>
    </div>
  )
}
