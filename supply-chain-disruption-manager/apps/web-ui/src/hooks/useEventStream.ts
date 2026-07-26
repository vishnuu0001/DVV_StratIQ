// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/hooks (useEventStream.ts)
// Date: 2026-05-26
// ---------------------------------------------------------------------------
import { useEffect, useRef, useCallback } from 'react'
import { createSSEStream } from '../api/sse'
import { useAppStore } from '../store/useAppStore'
import { listEvents, type CanonicalEvent } from '../api/inspector'

const MAX_BUFFER = 200
const FALLBACK_AFTER_MS = 5000
const POLL_INTERVAL_MS = 5000
const EVENT_RATE_WINDOW_MS = 60000

// Function: isRecentEvent
function isRecentEvent(event: CanonicalEvent): boolean {
  const timestamp = Date.parse(event.ingested_at || event.source_timestamp || '')
  return Number.isFinite(timestamp) && Date.now() - timestamp < EVENT_RATE_WINDOW_MS
}

// Function: useEventStream
export function useEventStream(
  url: string,
  onEvent: (event: CanonicalEvent) => void
) {
  const incrementEventCount = useAppStore((s) => s.incrementEventCount)
  const setEventsPerMin = useAppStore((s) => s.setEventsPerMin)
  const setSseConnected = useAppStore((s) => s.setSseConnected)
  const callbackRef = useRef(onEvent)
  const seenEventIdsRef = useRef<Set<string>>(new Set())
  const eventWindowRef = useRef<number[]>([])
  callbackRef.current = onEvent

  const recordLiveEvent = useCallback((event: CanonicalEvent) => {
    callbackRef.current(event)
    incrementEventCount()

    const now = Date.now()
    eventWindowRef.current = [
      ...eventWindowRef.current.filter((timestamp) => now - timestamp < EVENT_RATE_WINDOW_MS),
      now,
    ]
    setEventsPerMin(eventWindowRef.current.length)
  }, [incrementEventCount, setEventsPerMin])

  const handleEvent = useCallback(
    (type: string, data: unknown) => {
      if (type === 'event' || type === 'message') {
        const evt = data as CanonicalEvent
        if (evt && evt.event_id) {
          if (!seenEventIdsRef.current.has(evt.event_id)) {
            seenEventIdsRef.current.add(evt.event_id)
            if (isRecentEvent(evt)) recordLiveEvent(evt)
          }
          setSseConnected(true)
        }
      }
    },
    [recordLiveEvent, setSseConnected]
  )

  useEffect(() => {
    let receivedStreamData = false
    let polling = false
    let fallbackTimer: ReturnType<typeof setTimeout> | null = null
    let pollTimer: ReturnType<typeof setInterval> | null = null
    let stopped = false

    // Function: pollEvents
    const pollEvents = async () => {
      try {
        const response = await listEvents({ limit: 25 })
        if (stopped) return
        setSseConnected(true)

        const items = [...response.items].reverse()
        for (const evt of items) {
          if (!evt.event_id || seenEventIdsRef.current.has(evt.event_id)) continue
          seenEventIdsRef.current.add(evt.event_id)
          if (isRecentEvent(evt)) recordLiveEvent(evt)
        }
      } catch {
        if (!receivedStreamData) setSseConnected(false)
      }
    }

    // Function: startPollingFallback
    const startPollingFallback = () => {
      if (polling || stopped) return
      polling = true
      void pollEvents()
      pollTimer = setInterval(() => void pollEvents(), POLL_INTERVAL_MS)
    }

    const cleanup = createSSEStream(
      url,
      (type, data) => {
        receivedStreamData = true
        handleEvent(type, data)
      },
      () => {
        receivedStreamData = true
        setSseConnected(true)
      }
    )

    fallbackTimer = setTimeout(() => {
      if (!receivedStreamData) startPollingFallback()
    }, FALLBACK_AFTER_MS)

    return () => {
      stopped = true
      if (fallbackTimer) clearTimeout(fallbackTimer)
      if (pollTimer) clearInterval(pollTimer)
      cleanup()
      setSseConnected(false)
    }
  }, [url, handleEvent, recordLiveEvent, setSseConnected])
}

export { MAX_BUFFER }
