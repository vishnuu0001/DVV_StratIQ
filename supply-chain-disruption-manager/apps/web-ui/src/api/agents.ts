// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/api (agents.ts)
// Date: 2025-09-18
// ---------------------------------------------------------------------------
const AGENT_URL = import.meta.env.VITE_AGENT_API_URL || '/api/agents'
const AGENT_KEY = import.meta.env.VITE_AGENT_API_KEY || 'agent-dev-key'

export interface SpecialistRun {
  agent_name: string
  domain?: string
  status: string
  confidence: number
  findings: string
  actions: Array<string | Record<string, unknown>>
  started_at?: string | null
  completed_at: string | null
  scope_violations: string[]
  token_usage?: { prompt: number; completion: number; total: number }
}

export interface HumanDecision {
  decision: 'approved' | 'rejected'
  reason: string
  decided_by: string
  decided_at: string
}

export interface BlastRadius {
  nodes: Array<{ id: string; kind: string; domain: string; properties: Record<string, unknown> }>
  edges: Array<{ from: string; to: string; kind: string; verb: string }>
}

export interface OrchestratorPlan {
  steps: Array<{ step: number; agent: string; action: string; rationale: string }>
  estimated_impact: string
  recommended_action: string
}

export interface Incident {
  id: string
  source_event_id: string
  state: string
  type: string
  severity: string
  confidence: number
  root_node_id: string
  blast_radius: BlastRadius | null
  owners: Array<{ id: string; name: string; role: string; email: string }>
  plan: OrchestratorPlan | null
  specialist_runs: SpecialistRun[]
  human_decisions: HumanDecision[]
  final_summary: string
  created_at: string
  updated_at: string
  resolved_at: string | null
}

interface AgentIncidentResponse extends Omit<Incident, 'id' | 'blast_radius'> {
  id?: string
  incident_id?: string
  blast_radius?: BlastRadius | null
  blast_radius_node_count?: number
}

export interface IncidentFilters {
  state?: string
  severity?: string
  type?: string
  cursor?: string
  limit?: number
}

export interface TimelineEvent {
  id: string
  incident_id: string
  event_type: string
  message: string
  actor: string
  data: Record<string, unknown>
  created_at: string
}

export interface AgentCard {
  name: string
  role: string
  domain: string
  last_run_at: string | null
  status: 'idle' | 'running' | 'completed' | 'error'
  last_confidence: number | null
  tools: string[]
  last_actions: Array<string | Record<string, unknown>>
  scope_violations: string[]
  token_usage?: { prompt: number; completion: number; total: number }
  findings?: string
  last_incident_id?: string
  duration_ms?: number | null
}

export interface AgentRun {
  incident_id: string
  incident_type: string
  incident_state: string
  status: string
  confidence: number | null
  findings: string
  recommendation: string
  actions: Array<string | Record<string, unknown>>
  scope_violations: string[]
  started_at: string | null
  completed_at: string | null
  duration_ms: number | null
  token_usage?: { prompt: number; completion: number; total: number }
}

// Function: headers
function headers(): HeadersInit {
  return { 'X-API-Key': AGENT_KEY, 'Content-Type': 'application/json' }
}

type RawSpecialistRun = Partial<SpecialistRun> & {
  actions_taken?: Array<string | Record<string, unknown>>
  blockers?: string[]
  recommendation?: string
  role?: string
}

// Function: normalizeSpecialistRun
function normalizeSpecialistRun(raw: RawSpecialistRun): SpecialistRun {
  return {
    agent_name: raw.agent_name ?? raw.role ?? 'Unknown agent',
    domain: raw.domain,
    status: raw.status ?? 'unknown',
    confidence: raw.confidence ?? 0,
    findings: raw.findings ?? raw.recommendation ?? '',
    actions: Array.isArray(raw.actions)
      ? raw.actions
      : Array.isArray(raw.actions_taken)
        ? raw.actions_taken
        : [],
    started_at: raw.started_at ?? null,
    completed_at: raw.completed_at ?? null,
    scope_violations: Array.isArray(raw.scope_violations)
      ? raw.scope_violations
      : Array.isArray(raw.blockers)
        ? raw.blockers
        : [],
    token_usage: raw.token_usage,
  }
}

// Function: normalizeIncident
function normalizeIncident(raw: AgentIncidentResponse): Incident {
  const blastRadius = raw.blast_radius
    ? {
        nodes: Array.isArray(raw.blast_radius.nodes) ? raw.blast_radius.nodes : [],
        edges: Array.isArray(raw.blast_radius.edges) ? raw.blast_radius.edges : [],
      }
    : null

  return {
    ...raw,
    id: raw.id ?? raw.incident_id ?? '',
    confidence: raw.confidence ?? 0,
    root_node_id: raw.root_node_id ?? '',
    owners: Array.isArray(raw.owners) ? raw.owners : [],
    blast_radius: blastRadius,
    specialist_runs: Array.isArray(raw.specialist_runs)
      ? raw.specialist_runs.map(normalizeSpecialistRun)
      : [],
    human_decisions: Array.isArray(raw.human_decisions) ? raw.human_decisions : [],
    final_summary: raw.final_summary ?? '',
  }
}

// Function: listIncidents
export async function listIncidents(
  filters?: IncidentFilters
): Promise<{ items: Incident[]; cursor: string | null }> {
  const params = new URLSearchParams()
  if (filters?.state) params.set('state', filters.state)
  if (filters?.severity) params.set('severity', filters.severity)
  if (filters?.type) params.set('type', filters.type)
  if (filters?.cursor) params.set('cursor', filters.cursor)
  if (filters?.limit) params.set('limit', String(filters.limit))
  const r = await fetch(`${AGENT_URL}/incidents?${params.toString()}`, { headers: headers() })
  if (!r.ok) throw new Error(`Agent listIncidents failed: ${r.status}`)
  const data = (await r.json()) as { items: AgentIncidentResponse[]; cursor?: string | null; next_cursor?: string | null }
  return {
    items: (data.items ?? []).map(normalizeIncident),
    cursor: data.cursor ?? data.next_cursor ?? null,
  }
}

// Function: getIncident
export async function getIncident(id: string): Promise<Incident> {
  const r = await fetch(`${AGENT_URL}/incident/${encodeURIComponent(id)}`, { headers: headers() })
  if (!r.ok) throw new Error(`Agent getIncident failed: ${r.status}`)
  return normalizeIncident((await r.json()) as AgentIncidentResponse)
}

// Function: getIncidentTimeline
export async function getIncidentTimeline(id: string): Promise<TimelineEvent[]> {
  const r = await fetch(`${AGENT_URL}/incident/${encodeURIComponent(id)}/timeline`, { headers: headers() })
  if (!r.ok) throw new Error(`Agent getIncidentTimeline failed: ${r.status}`)
  const data = await r.json() as TimelineEvent[] | { events?: TimelineEvent[] }
  return Array.isArray(data) ? data : data.events ?? []
}

// Function: approveIncident
export async function approveIncident(
  id: string,
  reason: string,
  decidedBy: string
): Promise<Incident> {
  const r = await fetch(`${AGENT_URL}/incident/${encodeURIComponent(id)}/approve`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ reason, decided_by: decidedBy }),
  })
  if (!r.ok) throw new Error(`Agent approveIncident failed: ${r.status}`)
  return getIncident(id)
}

// Function: rejectIncident
export async function rejectIncident(
  id: string,
  reason: string,
  decidedBy: string
): Promise<Incident> {
  const r = await fetch(`${AGENT_URL}/incident/${encodeURIComponent(id)}/reject`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ reason, decided_by: decidedBy }),
  })
  if (!r.ok) throw new Error(`Agent rejectIncident failed: ${r.status}`)
  return getIncident(id)
}

// Function: triggerDisruption
export async function triggerDisruption(payload: object): Promise<{ incident_id: string }> {
  const r = await fetch(`${AGENT_URL}/disruption`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(payload),
  })
  if (!r.ok) throw new Error(`Agent triggerDisruption failed: ${r.status}`)
  return r.json() as Promise<{ incident_id: string }>
}

// Function: getAgentHealth
export async function getAgentHealth(): Promise<object> {
  const r = await fetch(`${AGENT_URL}/health`, { headers: headers() })
  if (!r.ok) throw new Error(`Agent health failed: ${r.status}`)
  return r.json() as Promise<object>
}

// Function: listAgents
export async function listAgents(): Promise<AgentCard[]> {
  const r = await fetch(`${AGENT_URL}/agents`, { headers: headers() })
  if (!r.ok) throw new Error(`Agent listAgents failed: ${r.status}`)
  return r.json() as Promise<AgentCard[]>
}

// Function: getAgentRuns
export async function getAgentRuns(name: string, limit = 10): Promise<AgentRun[]> {
  const r = await fetch(
    `${AGENT_URL}/agents/${encodeURIComponent(name)}/runs?limit=${limit}`,
    { headers: headers() }
  )
  if (!r.ok) throw new Error(`Agent getAgentRuns failed: ${r.status}`)
  return r.json() as Promise<AgentRun[]>
}

// Function: getIncidentStreamURL
export function getIncidentStreamURL(): string {
  return `${AGENT_URL}/incidents/stream?api_key=${encodeURIComponent(AGENT_KEY)}`
}
