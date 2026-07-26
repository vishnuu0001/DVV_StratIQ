// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/api (inspector.ts)
// Date: 2025-07-28
// ---------------------------------------------------------------------------
const INSPECTOR_URL = import.meta.env.VITE_INSPECTOR_API_URL || '/api/inspector'
const INSPECTOR_KEY = import.meta.env.VITE_INSPECTOR_API_KEY || 'inspector-dev-key'

export interface CanonicalEvent {
  event_id: string
  event_type: string
  severity: 'info' | 'low' | 'med' | 'high' | 'critical'
  source_system: string
  ingested_at: string
  source_timestamp: string
  root_node_id: string | null
  payload: Record<string, unknown>
  tags: Record<string, string>
  stream_name?: string | null
  publish_status?: string | null
  validation_status?: string | null
  validation_errors?: string[]
  replay_count?: number
}

export interface EventFilters {
  severity?: string
  source_system?: string
  event_type?: string
  root_node_id?: string
  publish_status?: string
  validation_status?: string
  cursor?: string
  limit?: number
}

export interface AdapterHealth {
  name: string
  status: 'healthy' | 'degraded' | 'down'
  events_last_5m: number
  error_rate: number
  last_event_at: string | null
  enabled: boolean
}

export interface SchemaEntry {
  event_type: string
  version: string
  recent_count: number
}

interface InspectorSchemaEntry {
  event_type: string
  file?: string
  version?: string
  recent_count?: number
}

interface InspectorAdapterHealth {
  adapter_name?: string
  name?: string
  enabled?: boolean
  status?: string
  last_event_at?: string | null
  events_last_5m?: number
  error_rate_5m?: number
  error_rate?: number
}

// Function: normalizeAdapterStatus
function normalizeAdapterStatus(status: string | undefined, enabled: boolean): AdapterHealth['status'] {
  if (!enabled || status === 'disabled' || status === 'error' || status === 'down') return 'down'
  if (status === 'degraded') return 'degraded'
  return 'healthy'
}

// Function: normalizeAdapter
function normalizeAdapter(raw: InspectorAdapterHealth): AdapterHealth {
  const enabled = raw.enabled ?? true
  return {
    name: raw.name ?? raw.adapter_name ?? 'unknown',
    status: normalizeAdapterStatus(raw.status, enabled),
    events_last_5m: raw.events_last_5m ?? 0,
    error_rate: raw.error_rate ?? raw.error_rate_5m ?? 0,
    last_event_at: raw.last_event_at ?? null,
    enabled,
  }
}

// Function: headers
function headers(): HeadersInit {
  return { 'X-API-Key': INSPECTOR_KEY, 'Content-Type': 'application/json' }
}

// Function: listEvents
export async function listEvents(
  filters?: EventFilters
): Promise<{ items: CanonicalEvent[]; cursor: string | null }> {
  const params = new URLSearchParams()
  if (filters?.severity) params.set('severity', filters.severity)
  if (filters?.source_system) params.set('source_system', filters.source_system)
  if (filters?.event_type) params.set('event_type', filters.event_type)
  if (filters?.root_node_id) params.set('root_node_id', filters.root_node_id)
  if (filters?.publish_status) params.set('publish_status', filters.publish_status)
  if (filters?.validation_status) params.set('validation_status', filters.validation_status)
  if (filters?.cursor) params.set('cursor', filters.cursor)
  if (filters?.limit) params.set('limit', String(filters.limit))
  const r = await fetch(`${INSPECTOR_URL}/events?${params.toString()}`, { headers: headers() })
  if (!r.ok) throw new Error(`Inspector listEvents failed: ${r.status}`)
  return r.json() as Promise<{ items: CanonicalEvent[]; cursor: string | null }>
}

// Function: getEvent
export async function getEvent(eventId: string): Promise<CanonicalEvent> {
  const r = await fetch(`${INSPECTOR_URL}/event/${encodeURIComponent(eventId)}`, { headers: headers() })
  if (!r.ok) throw new Error(`Inspector getEvent failed: ${r.status}`)
  return r.json() as Promise<CanonicalEvent>
}

// Function: replayEvent
export async function replayEvent(eventId: string): Promise<{ status: string }> {
  const r = await fetch(`${INSPECTOR_URL}/event/${encodeURIComponent(eventId)}/replay`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ replayed_by: 'operator' }),
  })
  if (!r.ok) throw new Error(`Inspector replayEvent failed: ${r.status}`)
  return r.json() as Promise<{ status: string }>
}

// Function: getAdapters
export async function getAdapters(): Promise<AdapterHealth[]> {
  const r = await fetch(`${INSPECTOR_URL}/adapters`, { headers: headers() })
  if (!r.ok) throw new Error(`Inspector getAdapters failed: ${r.status}`)
  const data = (await r.json()) as InspectorAdapterHealth[] | { adapters?: InspectorAdapterHealth[] }
  const adapters = Array.isArray(data) ? data : data.adapters ?? []
  return adapters.map(normalizeAdapter)
}

// Function: getSchemas
export async function getSchemas(): Promise<SchemaEntry[]> {
  const r = await fetch(`${INSPECTOR_URL}/schemas`, { headers: headers() })
  if (!r.ok) throw new Error(`Inspector getSchemas failed: ${r.status}`)
  const data = (await r.json()) as InspectorSchemaEntry[] | { schemas?: InspectorSchemaEntry[] }
  const schemas = Array.isArray(data) ? data : data.schemas ?? []
  return schemas.map((schema) => ({
    event_type: schema.event_type,
    version: schema.version ?? '1',
    recent_count: schema.recent_count ?? 0,
  }))
}

// Function: getSchema
export async function getSchema(eventType: string): Promise<object> {
  const r = await fetch(`${INSPECTOR_URL}/schemas/${encodeURIComponent(eventType)}`, { headers: headers() })
  if (!r.ok) throw new Error(`Inspector getSchema failed: ${r.status}`)
  return r.json() as Promise<object>
}

// Function: ingestManual
export async function ingestManual(event: object): Promise<{ event_id: string }> {
  const r = await fetch(`${INSPECTOR_URL}/ingest/manual`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(event),
  })
  if (!r.ok) throw new Error(`Inspector ingestManual failed: ${r.status}`)
  return r.json() as Promise<{ event_id: string }>
}

// Function: getInspectorHealth
export async function getInspectorHealth(): Promise<object> {
  const r = await fetch(`${INSPECTOR_URL}/health`, { headers: headers() })
  if (!r.ok) throw new Error(`Inspector health failed: ${r.status}`)
  return r.json() as Promise<object>
}

// Function: replayById
export async function replayById(eventId: string): Promise<{ status: string }> {
  return replayEvent(eventId)
}

// Function: getEventStreamURL
export function getEventStreamURL(): string {
  return `${INSPECTOR_URL}/events/stream`
}
