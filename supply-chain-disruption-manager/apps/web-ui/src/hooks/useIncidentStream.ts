// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/hooks (useIncidentStream.ts)
// Date: 2026-07-07
// ---------------------------------------------------------------------------
import { useEffect, useCallback, useRef } from 'react'
import { createSSEStream } from '../api/sse'
import { useAppStore } from '../store/useAppStore'
import type { Incident } from '../api/agents'

// Function: useIncidentStream
export function useIncidentStream(
  url: string,
  onIncident: (incident: Incident) => void
) {
  const setCriticalCount = useAppStore((s) => s.setCriticalCount)
  const setOpenApprovals = useAppStore((s) => s.setOpenApprovals)
  const callbackRef = useRef(onIncident)
  callbackRef.current = onIncident

  const handleEvent = useCallback(
    (type: string, data: unknown) => {
      if (type === 'incident' || type === 'message') {
        const incident = data as Incident
        if (incident && incident.id) {
          callbackRef.current(incident)
          if (incident.severity === 'critical' && incident.state !== 'RESOLVED') {
            // This is a partial update; the full count will be computed from the list
          }
          if (incident.state === 'AWAITING_APPROVAL') {
            // Count increment handled by the consumer
          }
        }
      }
    },
    [setCriticalCount, setOpenApprovals]
  )

  useEffect(() => {
    const cleanup = createSSEStream(url, handleEvent)
    return cleanup
  }, [url, handleEvent])
}
