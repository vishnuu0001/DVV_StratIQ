// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/hooks (useIncidents.ts)
// Date: 2025-11-12
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback } from 'react'
import { listIncidents } from '../api/agents'
import type { Incident, IncidentFilters } from '../api/agents'
import { useAppStore } from '../store/useAppStore'

// Function: useIncidents
export function useIncidents(filters?: IncidentFilters) {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const setCriticalCount = useAppStore((s) => s.setCriticalCount)
  const setOpenApprovals = useAppStore((s) => s.setOpenApprovals)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await listIncidents({ limit: 100, ...filters })
      setIncidents(result.items)

      const critical = result.items.filter(
        (i) => i.severity === 'critical' && i.state !== 'RESOLVED'
      ).length
      const approvals = result.items.filter(
        (i) => i.state === 'AWAITING_APPROVAL'
      ).length

      setCriticalCount(critical)
      setOpenApprovals(approvals)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }, [filters, setCriticalCount, setOpenApprovals])

  useEffect(() => {
    void load()
    const interval = setInterval(() => void load(), 15000)
    return () => clearInterval(interval)
  }, [load])

  const upsertIncident = useCallback((updated: Incident) => {
    setIncidents((prev) => {
      const idx = prev.findIndex((i) => i.id === updated.id)
      const next = idx >= 0
        ? prev.map((i, j) => (j === idx ? updated : i))
        : [updated, ...prev]
      // Sync store counts immediately so header stats reflect the change without waiting for next poll
      setCriticalCount(next.filter((i) => i.severity === 'critical' && i.state !== 'RESOLVED').length)
      setOpenApprovals(next.filter((i) => i.state === 'AWAITING_APPROVAL').length)
      return next
    })
  }, [setCriticalCount, setOpenApprovals])

  return { incidents, loading, error, reload: load, upsertIncident }
}
