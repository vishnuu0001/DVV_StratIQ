// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/views (AdapterOps.tsx)
// Date: 2026-04-11
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react'
import { RefreshCw, Plug } from 'lucide-react'
import { AdapterHealthCard } from '../components/AdapterHealthCard'
import { getAdapters } from '../api/inspector'
import type { AdapterHealth } from '../api/inspector'

// Mock adapters for when backend is unavailable
const MOCK_ADAPTERS: AdapterHealth[] = [
  { name: 'Supplier ERP', status: 'healthy', events_last_5m: 0, error_rate: 0, last_event_at: null, enabled: true },
  { name: 'Logistics TMS', status: 'healthy', events_last_5m: 0, error_rate: 0, last_event_at: null, enabled: true },
  { name: 'Warehouse WMS', status: 'healthy', events_last_5m: 0, error_rate: 0, last_event_at: null, enabled: true },
  { name: 'Production MES', status: 'healthy', events_last_5m: 0, error_rate: 0, last_event_at: null, enabled: true },
  { name: 'Demand Planning', status: 'healthy', events_last_5m: 0, error_rate: 0, last_event_at: null, enabled: true },
  { name: 'Finance ERP', status: 'healthy', events_last_5m: 0, error_rate: 0, last_event_at: null, enabled: true },
  { name: 'HR System', status: 'healthy', events_last_5m: 0, error_rate: 0, last_event_at: null, enabled: false },
  { name: 'Customs Broker', status: 'healthy', events_last_5m: 0, error_rate: 0, last_event_at: null, enabled: true },
]

// Function: AdapterOps
export function AdapterOps() {
  const [adapters, setAdapters] = useState<AdapterHealth[]>([])
  const [loading, setLoading] = useState(true)
  const [useMock, setUseMock] = useState(false)

  // Function: load
  async function load() {
    setLoading(true)
    try {
      const data = await getAdapters()
      setAdapters(data)
      setUseMock(false)
    } catch {
      setAdapters(MOCK_ADAPTERS)
      setUseMock(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    const interval = setInterval(() => void load(), 30000)
    return () => clearInterval(interval)
  }, [])

  const healthy = adapters.filter((a) => a.status === 'healthy').length
  const degraded = adapters.filter((a) => a.status === 'degraded').length
  const down = adapters.filter((a) => a.status === 'down').length

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-xl text-text mb-1">Adapter Operations</h1>
            <p className="text-sm text-text-3">
              {useMock
                ? 'Showing default adapters — connect Inspector service for live data'
                : `${adapters.length} adapters · ${healthy} healthy · ${degraded} degraded · ${down} down`}
            </p>
          </div>
          <button
            onClick={() => void load()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-border hover:border-border-hi text-text-2 text-xs transition-colors"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>

        {/* Summary bar */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded px-3 py-1.5">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            <span className="text-xs text-green-400">{healthy} Healthy</span>
          </div>
          {degraded > 0 && (
            <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded px-3 py-1.5">
              <div className="w-2 h-2 rounded-full bg-amber-400" />
              <span className="text-xs text-amber-400">{degraded} Degraded</span>
            </div>
          )}
          {down > 0 && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded px-3 py-1.5">
              <div className="w-2 h-2 rounded-full bg-red-500 dot-blink" />
              <span className="text-xs text-red-400">{down} Down</span>
            </div>
          )}
        </div>

        {/* Adapter grid */}
        {adapters.length === 0 && !loading ? (
          <div className="flex flex-col items-center justify-center py-16 text-text-3 gap-3">
            <Plug size={40} className="opacity-30" />
            <div className="text-sm">No adapters found</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
            {adapters.map((adapter) => (
              <AdapterHealthCard key={adapter.name} adapter={adapter} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
