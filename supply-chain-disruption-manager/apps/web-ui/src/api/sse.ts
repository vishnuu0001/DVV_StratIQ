// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/api (sse.ts)
// Date: 2025-12-07
// ---------------------------------------------------------------------------
// Function: createSSEStream
export function createSSEStream(
  url: string,
  onEvent: (type: string, data: unknown) => void,
  onHeartbeat?: () => void
): () => void {
  let es: EventSource | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let stopped = false
  let reconnectDelay = 1000

  // Function: connect
  function connect() {
    if (stopped) return
    try {
      es = new EventSource(url)

      es.onopen = () => {
        reconnectDelay = 1000
        onHeartbeat?.()
      }

      es.onmessage = (e) => {
        reconnectDelay = 1000
        try {
          const parsed = JSON.parse(e.data as string) as unknown
          onEvent('message', parsed)
        } catch {
          onEvent('message', e.data)
        }
      }

      es.addEventListener('heartbeat', () => {
        onHeartbeat?.()
      })

      es.addEventListener('event', (e: MessageEvent) => {
        reconnectDelay = 1000
        try {
          const parsed = JSON.parse(e.data as string) as unknown
          onEvent('event', parsed)
        } catch {
          onEvent('event', e.data)
        }
      })

      es.addEventListener('canonical_event', (e: MessageEvent) => {
        reconnectDelay = 1000
        onHeartbeat?.()
        try {
          const parsed = JSON.parse(e.data as string) as unknown
          onEvent('event', parsed)
        } catch {
          onEvent('event', e.data)
        }
      })

      es.addEventListener('incident', (e: MessageEvent) => {
        reconnectDelay = 1000
        try {
          const parsed = JSON.parse(e.data as string) as unknown
          onEvent('incident', parsed)
        } catch {
          onEvent('incident', e.data)
        }
      })

      es.addEventListener('incident_state', (e: MessageEvent) => {
        reconnectDelay = 1000
        try {
          const parsed = JSON.parse(e.data as string) as unknown
          onEvent('incident_state', parsed)
        } catch {
          onEvent('incident_state', e.data)
        }
      })

      es.onerror = () => {
        es?.close()
        es = null
        if (!stopped) {
          reconnectTimer = setTimeout(() => {
            reconnectDelay = Math.min(reconnectDelay * 2, 30000)
            connect()
          }, reconnectDelay)
        }
      }
    } catch {
      if (!stopped) {
        reconnectTimer = setTimeout(() => {
          reconnectDelay = Math.min(reconnectDelay * 2, 30000)
          connect()
        }, reconnectDelay)
      }
    }
  }

  connect()

  return () => {
    stopped = true
    if (reconnectTimer) clearTimeout(reconnectTimer)
    es?.close()
    es = null
  }
}
