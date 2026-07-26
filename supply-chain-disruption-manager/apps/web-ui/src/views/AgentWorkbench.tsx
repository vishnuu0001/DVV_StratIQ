// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/views (AgentWorkbench.tsx)
// Date: 2025-08-09
// ---------------------------------------------------------------------------
import React, { useEffect, useState, useCallback, useRef } from 'react'
import {
  Bot, RefreshCw, Activity, Clock, Shield, AlertTriangle, Cpu,
  ChevronRight, X, Zap, History, ChevronDown, ChevronUp, Info,
  CheckCircle, Loader,
} from 'lucide-react'
import { listAgents, getAgentRuns, triggerDisruption, getIncidentStreamURL } from '../api/agents'
import type { AgentCard, AgentRun } from '../api/agents'
import { createSSEStream } from '../api/sse'
import { JsonViewer } from '../components/JsonViewer'

const DOMAIN_COLORS: Record<string, string> = {
  procurement: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
  logistics: 'text-purple-400 border-purple-500/30 bg-purple-500/10',
  warehouse: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10',
  production: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
  people: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
  system: 'text-yellow-300 border-yellow-400/30 bg-yellow-400/10',
  orchestrator: 'text-text-2 border-border bg-surface-3',
}

const DISRUPTION_TYPES = [
  'supplier_delay',
  'eta_slip',
  'qc_reject',
  'customs_hold',
  'short_pick',
  'demand_spike',
]

// Function: domainClass
function domainClass(domain: string): string {
  return DOMAIN_COLORS[domain.toLowerCase()] ?? DOMAIN_COLORS['system']
}

// Function: formatTs
function formatTs(ts: string | null): string {
  if (!ts) return 'Never'
  try {
    const d = new Date(ts)
    const diff = Date.now() - d.getTime()
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return ts
  }
}

// Function: formatFullTs
function formatFullTs(ts: string | null): string {
  if (!ts) return 'Never'
  try {
    return new Date(ts).toLocaleString('en-US', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
    })
  } catch {
    return ts
  }
}

// Function: formatDuration
function formatDuration(ms: number | null | undefined): string {
  if (!ms) return '—'
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`
}

// Function: formatAction
function formatAction(action: string | Record<string, unknown>): string {
  if (typeof action === 'string') return action
  if (typeof action.tool === 'string') return action.tool
  if (typeof action.action === 'string') return action.action
  try { return JSON.stringify(action) } catch { return 'Action' }
}

type DetailItem =
  | { kind: 'tool'; label: string; data: { name: string; agent: string; domain: string } }
  | { kind: 'action'; label: string; data: string | Record<string, unknown> }
  | { kind: 'scope'; label: string; data: string }
  | { kind: 'run'; label: string; data: AgentRun }

const MOCK_AGENTS: AgentCard[] = [
  {
    name: 'Orchestrator', role: 'Master coordinator', domain: 'orchestrator',
    last_run_at: null, status: 'idle', last_confidence: null,
    tools: ['classify_incident', 'dispatch_specialist', 'await_approval', 'resolve_incident'],
    last_actions: [], scope_violations: [],
  },
  {
    name: 'Procurement Specialist', role: 'Supplier & PO analysis', domain: 'procurement',
    last_run_at: null, status: 'idle', last_confidence: null,
    tools: ['query_kg', 'assess_supplier_risk', 'find_alternative_suppliers', 'evaluate_po_impact'],
    last_actions: [], scope_violations: [],
  },
  {
    name: 'Logistics Specialist', role: 'Shipment & transit analysis', domain: 'logistics',
    last_run_at: null, status: 'idle', last_confidence: null,
    tools: ['query_kg', 'check_shipment_status', 'find_alternate_routes', 'assess_customs_risk'],
    last_actions: [], scope_violations: [],
  },
  {
    name: 'Warehouse Specialist', role: 'Inventory & WH operations', domain: 'warehouse',
    last_run_at: null, status: 'idle', last_confidence: null,
    tools: ['query_kg', 'check_inventory_levels', 'assess_qc_impact', 'find_alternative_stock'],
    last_actions: [], scope_violations: [],
  },
  {
    name: 'Production Specialist', role: 'Production line analysis', domain: 'production',
    last_run_at: null, status: 'idle', last_confidence: null,
    tools: ['query_kg', 'assess_production_impact', 'find_component_alternatives', 'evaluate_schedule'],
    last_actions: [], scope_violations: [],
  },
  {
    name: 'People Specialist', role: 'Staffing & HR analysis', domain: 'people',
    last_run_at: null, status: 'idle', last_confidence: null,
    tools: ['query_kg', 'assess_staffing_needs', 'find_coverage', 'evaluate_compliance'],
    last_actions: [], scope_violations: [],
  },
]

// ─── Trigger Disruption Modal ──────────────────────────────────────────────

// Function: TriggerDisruptionModal
function TriggerDisruptionModal({
  agentName,
  onClose,
  onSuccess,
}: {
  agentName: string
  onClose: () => void
  onSuccess: (incidentId: string) => void
}) {
  const [type, setType] = useState(DISRUPTION_TYPES[0])
  const [rootNodeId, setRootNodeId] = useState('')
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Function: submit
  async function submit() {
    setSubmitting(true)
    setError(null)
    try {
      const sourceEventId = `manual-${agentName.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`
      const result = await triggerDisruption({
        source_event_id: sourceEventId,
        type,
        event_type: type,
        root_node_id: rootNodeId || undefined,
        payload: { description: description || `Manually triggered via Agent Workbench (${agentName})` },
      })
      onSuccess(result.incident_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Trigger failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-surface border border-border rounded-lg shadow-2xl w-full max-w-md mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap size={16} className="text-amber-400" />
            <span className="font-medium text-sm">Trigger Disruption</span>
          </div>
          <button onClick={onClose} className="p-1.5 rounded hover:bg-surface-2 text-text-3 hover:text-text">
            <X size={15} />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <div>
            <label className="block text-[10px] text-text-3 uppercase tracking-wider mb-1.5">Disruption Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full bg-surface-2 border border-border rounded px-3 py-2 text-xs text-text-2 focus:outline-none focus:border-border-hi"
            >
              {DISRUPTION_TYPES.map((t) => (
                <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-text-3 uppercase tracking-wider mb-1.5">Root Node ID <span className="normal-case text-text-3">(optional)</span></label>
            <input
              type="text"
              value={rootNodeId}
              onChange={(e) => setRootNodeId(e.target.value)}
              placeholder="e.g. SUP-004, WH-003, PO-10019"
              className="w-full bg-surface-2 border border-border rounded px-3 py-2 text-xs text-text-2 placeholder-text-3 focus:outline-none focus:border-border-hi"
            />
          </div>

          <div>
            <label className="block text-[10px] text-text-3 uppercase tracking-wider mb-1.5">Description <span className="normal-case text-text-3">(optional)</span></label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the disruption scenario…"
              rows={3}
              className="w-full bg-surface-2 border border-border rounded px-3 py-2 text-xs text-text-2 placeholder-text-3 resize-none focus:outline-none focus:border-border-hi"
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded px-3 py-2">
              <AlertTriangle size={13} />
              {error}
            </div>
          )}
        </div>

        <div className="px-5 py-4 border-t border-border flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded border border-border text-xs text-text-3 hover:text-text hover:border-border-hi transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => void submit()}
            disabled={submitting}
            className="px-4 py-1.5 rounded bg-amber-500/20 border border-amber-500/30 text-amber-300 hover:bg-amber-500/30 text-xs font-medium transition-colors disabled:opacity-50 flex items-center gap-1.5"
          >
            {submitting ? <Loader size={12} className="animate-spin" /> : <Zap size={12} />}
            {submitting ? 'Triggering…' : 'Trigger'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Agent Card ────────────────────────────────────────────────────────────

// Function: cardBorderClass
function cardBorderClass(agent: AgentCard, selected: boolean): string {
  if (agent.status === 'running') return 'border-amber-500/40'
  if (agent.status === 'error') return 'border-red-500/30'
  if (selected) return 'border-cyan-500/40'
  return 'border-border'
}

// Function: statusDotClass
function statusDotClass(status: string): string {
  if (status === 'running') return 'bg-amber-400 dot-blink'
  if (status === 'completed') return 'bg-green-400'
  if (status === 'error') return 'bg-red-500'
  return 'bg-green-400/50'
}

// Function: statusTextClass
function statusTextClass(status: string): string {
  if (status === 'running') return 'text-amber-400'
  if (status === 'completed') return 'text-green-400'
  if (status === 'error') return 'text-red-400'
  return 'text-text-3'
}

// Function: AgentCardComponent
function AgentCardComponent({
  agent,
  selected,
  onOpen,
  onInspect,
}: {
  agent: AgentCard
  selected: boolean
  onOpen: (agent: AgentCard) => void
  onInspect: (agent: AgentCard, detail: DetailItem) => void
}) {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onOpen(agent)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpen(agent) }
      }}
      className={`bg-surface border rounded-lg p-4 space-y-3 text-left cursor-pointer transition-colors hover:border-border-hi hover:bg-surface-2/40 focus:outline-none focus:border-cyan-500/50 ${cardBorderClass(agent, selected)}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-surface-2">
            <Bot size={16} className="text-text-2" />
          </div>
          <div>
            <div className="text-sm font-medium">{agent.name}</div>
            <div className="text-xs text-text-3">{agent.role}</div>
          </div>
        </div>
        <div className={`text-[10px] px-2 py-0.5 rounded border font-mono uppercase ${domainClass(agent.domain)}`}>
          {agent.domain}
        </div>
      </div>

      <div className="flex items-center gap-3 text-xs">
        <div className="flex items-center gap-1.5">
          <div className={`w-1.5 h-1.5 rounded-full ${statusDotClass(agent.status)}`} />
          <span className={statusTextClass(agent.status)}>{agent.status}</span>
        </div>
        {agent.last_confidence !== null && (
          <div className="flex items-center gap-1 text-text-2">
            <Activity size={11} className="text-cyan-400/70" />
            <span>{(agent.last_confidence * 100).toFixed(0)}% conf</span>
          </div>
        )}
        {agent.duration_ms != null && (
          <span className="text-text-3 text-[10px]">{formatDuration(agent.duration_ms)}</span>
        )}
        <div className="flex items-center gap-1 text-text-3 ml-auto">
          <Clock size={11} />
          <span>{formatTs(agent.last_run_at)}</span>
        </div>
      </div>

      {agent.tools.length > 0 && (
        <div>
          <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1.5 flex items-center gap-1">
            <Cpu size={10} /> Tools
          </div>
          <div className="flex flex-wrap gap-1">
            {agent.tools.map((tool) => (
              <button
                key={tool}
                onClick={(e) => {
                  e.stopPropagation()
                  onInspect(agent, { kind: 'tool', label: tool, data: { name: tool, agent: agent.name, domain: agent.domain } })
                }}
                className="text-[10px] font-mono bg-surface-2 border border-border px-1.5 py-0.5 rounded text-text-3 hover:text-text-2 hover:border-border-hi transition-colors"
              >
                {tool}
              </button>
            ))}
          </div>
        </div>
      )}

      {agent.findings && (
        <p className="text-[10px] text-text-3 line-clamp-2 leading-relaxed">{agent.findings}</p>
      )}

      {agent.last_actions.length > 0 && (
        <div>
          <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1.5 flex items-center gap-1">
            <Activity size={10} /> Last Actions
          </div>
          <div className="space-y-1">
            {agent.last_actions.slice(0, 3).map((action, i) => (
              <button
                key={i}
                onClick={(e) => {
                  e.stopPropagation()
                  onInspect(agent, { kind: 'action', label: formatAction(action), data: action })
                }}
                className="w-full text-xs text-text-2 flex items-center gap-1.5 hover:text-cyan-300 transition-colors text-left"
              >
                <span className="w-1 h-1 rounded-full bg-cyan-400/50 shrink-0" />
                <span className="truncate">{formatAction(action)}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {agent.scope_violations.length > 0 && (
        <div className="border border-red-500/30 rounded bg-red-500/5 px-3 py-2">
          <div className="text-[10px] text-red-400 uppercase tracking-wider mb-1 flex items-center gap-1">
            <AlertTriangle size={10} /> Scope Violations
          </div>
          {agent.scope_violations.map((v, i) => (
            <button
              key={i}
              onClick={(e) => {
                e.stopPropagation()
                onInspect(agent, { kind: 'scope', label: 'Scope violation', data: v })
              }}
              className="block w-full text-left text-xs text-red-400/80 hover:text-red-300 transition-colors"
            >
              {v}
            </button>
          ))}
        </div>
      )}

      {agent.token_usage && (
        <div className="flex items-center gap-3 text-[10px] text-text-3 border-t border-border/50 pt-2">
          <Shield size={10} />
          <span>Prompt: {agent.token_usage.prompt.toLocaleString()}</span>
          <span>Completion: {agent.token_usage.completion.toLocaleString()}</span>
          <span className="text-text-2">Total: {agent.token_usage.total.toLocaleString()}</span>
        </div>
      )}

      <div className="flex items-center justify-end text-[10px] text-text-3 border-t border-border/40 pt-2">
        <ChevronRight size={12} />
      </div>
    </div>
  )
}

// ─── Agent Detail Panel ────────────────────────────────────────────────────

// Function: statusColorClass
function statusColorClass(status: string): string {
  if (status === 'completed') return 'text-green-400'
  if (status === 'running') return 'text-amber-400'
  if (status === 'error') return 'text-red-400'
  return 'text-text'
}

// Function: runStatusClass
function runStatusClass(status: string): string {
  if (status === 'completed') return 'text-green-400 border-green-500/30 bg-green-500/10'
  if (status === 'running') return 'text-amber-400 border-amber-500/30 bg-amber-500/10'
  return 'text-text-3 border-border'
}

// Function: RunHistorySection
function RunHistorySection({
  runs,
  runsLoading,
  runsExpanded,
  onToggle,
  onDetail,
}: {
  runs: AgentRun[]
  runsLoading: boolean
  runsExpanded: boolean
  onToggle: () => void
  onDetail: (detail: DetailItem) => void
}) {
  return (
    <div>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between text-[10px] text-text-3 uppercase tracking-wider hover:text-text-2 transition-colors"
      >
        <span className="flex items-center gap-1"><History size={11} /> Run History</span>
        {runsLoading ? <Loader size={11} className="animate-spin" /> : runsExpanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
      </button>
      {runsExpanded && (
        <div className="mt-2 space-y-2">
          {runs.length === 0 && !runsLoading ? (
            <div className="text-sm text-text-3">No historical runs found</div>
          ) : (
            runs.map((run, i) => (
              <button
                key={i}
                onClick={() => onDetail({ kind: 'run', label: `Run — ${run.incident_type}`, data: run })}
                className="w-full bg-surface-2 border border-border rounded px-3 py-2.5 text-left hover:border-border-hi transition-colors"
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="text-xs font-mono text-text-3 truncate">{run.incident_id}</span>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="text-[10px] text-text-3">{(run.confidence ?? 0) * 100 | 0}%</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border font-mono ${runStatusClass(run.status)}`}>{run.status}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs text-text-2 truncate">{run.incident_type.replace(/_/g, ' ')}</span>
                  <span className="text-[10px] text-text-3 shrink-0">{formatTs(run.completed_at)}</span>
                </div>
                {run.findings && (
                  <p className="text-[10px] text-text-3 mt-1 line-clamp-1 leading-relaxed">{run.findings}</p>
                )}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  )
}

// Function: DetailInspectorSection
function DetailInspectorSection({
  detail,
  onDetail,
}: {
  detail: DetailItem
  onDetail: (detail: DetailItem | null) => void
}) {
  return (
    <div className="border-t border-border pt-5">
      <div className="flex items-center justify-between gap-2 mb-3">
        <div>
          <div className="text-[10px] text-text-3 uppercase tracking-wider">{detail.kind}</div>
          <div className="text-sm font-medium text-text">{detail.label}</div>
        </div>
        <button onClick={() => onDetail(null)} className="p-1 rounded hover:bg-surface-2 text-text-3 hover:text-text">
          <X size={13} />
        </button>
      </div>
      {detail.kind === 'run' ? (
        <div className="space-y-3">
          {detail.data.findings && (
            <div>
              <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1">Findings</div>
              <div className="bg-surface-2 border border-border rounded px-3 py-2 text-xs text-text-2 whitespace-pre-wrap leading-relaxed">
                {detail.data.findings}
              </div>
            </div>
          )}
          {detail.data.recommendation && detail.data.recommendation !== detail.data.findings && (
            <div>
              <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1">Recommendation</div>
              <div className="bg-surface-2 border border-border rounded px-3 py-2 text-xs text-text-2 whitespace-pre-wrap leading-relaxed">
                {detail.data.recommendation}
              </div>
            </div>
          )}
          <JsonViewer data={detail.data} collapsed />
        </div>
      ) : typeof detail.data === 'string' ? (
        <div className="bg-surface-2 border border-border rounded px-3 py-2 text-sm text-text-2">{detail.data}</div>
      ) : (
        <JsonViewer data={detail.data} collapsed={false} />
      )}
    </div>
  )
}

// Function: AgentDetailPanel
function AgentDetailPanel({
  agent,
  detail,
  onClose,
  onDetail,
  onTrigger,
}: {
  agent: AgentCard
  detail: DetailItem | null
  onClose: () => void
  onDetail: (detail: DetailItem | null) => void
  onTrigger: () => void
}) {
  const [runs, setRuns] = useState<AgentRun[]>([])
  const [runsLoading, setRunsLoading] = useState(false)
  const [runsExpanded, setRunsExpanded] = useState(false)
  const [triggerSuccess, setTriggerSuccess] = useState<string | null>(null)

  const loadRuns = useCallback(async () => {
    setRunsLoading(true)
    try {
      const data = await getAgentRuns(agent.name)
      setRuns(data)
    } catch {
      // ignore — history unavailable
    } finally {
      setRunsLoading(false)
    }
  }, [agent.name])

  // Function: toggleRuns
  function toggleRuns() {
    if (!runsExpanded && runs.length === 0) void loadRuns()
    setRunsExpanded((v) => !v)
  }

  return (
    <div className="fixed inset-y-0 right-0 z-30 w-full max-w-xl bg-surface border-l border-border shadow-2xl flex flex-col">
      {/* Header */}
      <div className="px-5 py-4 border-b border-border flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="font-display text-lg text-text truncate">{agent.name}</div>
          <div className="text-sm text-text-3">{agent.role}</div>
        </div>
        <button onClick={onClose} className="p-1.5 rounded hover:bg-surface-2 text-text-3 hover:text-text">
          <X size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Metrics grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-surface-2 border border-border rounded p-3">
            <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1">Status</div>
            <div className={`text-sm font-medium ${statusColorClass(agent.status)}`}>{agent.status}</div>
          </div>
          <div className="bg-surface-2 border border-border rounded p-3">
            <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1">Last Run</div>
            <div className="text-sm text-text">{formatFullTs(agent.last_run_at)}</div>
          </div>
          <div className="bg-surface-2 border border-border rounded p-3">
            <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1">Confidence</div>
            <div className="text-sm text-text">
              {agent.last_confidence === null ? 'n/a' : `${(agent.last_confidence * 100).toFixed(0)}%`}
            </div>
          </div>
          <div className="bg-surface-2 border border-border rounded p-3">
            <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1">Domain</div>
            <div className={`inline-flex text-[10px] px-2 py-0.5 rounded border font-mono uppercase ${domainClass(agent.domain)}`}>
              {agent.domain}
            </div>
          </div>
          {agent.duration_ms != null && (
            <div className="bg-surface-2 border border-border rounded p-3">
              <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1">Duration</div>
              <div className="text-sm text-text">{formatDuration(agent.duration_ms)}</div>
            </div>
          )}
          {agent.last_incident_id && (
            <div className="bg-surface-2 border border-border rounded p-3">
              <div className="text-[10px] text-text-3 uppercase tracking-wider mb-1">Last Incident</div>
              <div className="text-xs font-mono text-cyan-400 truncate">{agent.last_incident_id}</div>
            </div>
          )}
        </div>

        {/* Findings */}
        {agent.findings && (
          <div>
            <div className="text-[10px] text-text-3 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Info size={11} /> Findings
            </div>
            <div className="bg-surface-2 border border-border rounded px-3 py-2.5 text-xs text-text-2 leading-relaxed whitespace-pre-wrap">
              {agent.findings}
            </div>
          </div>
        )}

        {/* Tools */}
        <div>
          <div className="text-[10px] text-text-3 uppercase tracking-wider mb-2 flex items-center gap-1">
            <Cpu size={11} /> Tools
          </div>
          {agent.tools.length === 0 ? (
            <span className="text-sm text-text-3">No tools registered</span>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {agent.tools.map((tool) => (
                <button
                  key={tool}
                  onClick={() => onDetail({ kind: 'tool', label: tool, data: { name: tool, agent: agent.name, domain: agent.domain } })}
                  className="text-xs font-mono bg-surface-2 border border-border px-2 py-1 rounded text-text-2 hover:border-border-hi hover:text-cyan-300 transition-colors"
                >
                  {tool}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Last Actions */}
        <div>
          <div className="text-[10px] text-text-3 uppercase tracking-wider mb-2 flex items-center gap-1">
            <Activity size={11} /> Last Actions
          </div>
          {agent.last_actions.length === 0 ? (
            <div className="text-sm text-text-3">No actions recorded</div>
          ) : (
            <div className="space-y-2">
              {agent.last_actions.map((action, i) => (
                <button
                  key={i}
                  onClick={() => onDetail({ kind: 'action', label: formatAction(action), data: action })}
                  className="w-full flex items-center justify-between gap-3 bg-surface-2 border border-border rounded px-3 py-2 text-left hover:border-border-hi transition-colors"
                >
                  <span className="text-xs text-text-2 truncate">{formatAction(action)}</span>
                  <ChevronRight size={13} className="text-text-3 shrink-0" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Scope Violations */}
        {agent.scope_violations.length > 0 && (
          <div>
            <div className="text-[10px] text-red-400 uppercase tracking-wider mb-2 flex items-center gap-1">
              <AlertTriangle size={11} /> Scope Violations
            </div>
            <div className="space-y-2">
              {agent.scope_violations.map((violation, i) => (
                <button
                  key={i}
                  onClick={() => onDetail({ kind: 'scope', label: 'Scope violation', data: violation })}
                  className="w-full bg-red-500/5 border border-red-500/30 rounded px-3 py-2 text-left text-xs text-red-300 hover:bg-red-500/10 transition-colors"
                >
                  {violation}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Run History */}
        <RunHistorySection
          runs={runs}
          runsLoading={runsLoading}
          runsExpanded={runsExpanded}
          onToggle={toggleRuns}
          onDetail={onDetail}
        />

        {/* Token Usage */}
        {agent.token_usage && (
          <div>
            <div className="text-[10px] text-text-3 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Shield size={11} /> Token Usage
            </div>
            <JsonViewer data={agent.token_usage} collapsed={false} />
          </div>
        )}

        {/* Detail Inspector */}
        {detail && <DetailInspectorSection detail={detail} onDetail={onDetail} />}
      </div>

      {/* Actions footer */}
      <div className="px-5 py-4 border-t border-border space-y-2">
        {triggerSuccess && (
          <div className="flex items-center gap-2 text-xs text-green-400 bg-green-500/10 border border-green-500/20 rounded px-3 py-2">
            <CheckCircle size={13} />
            Incident triggered: <span className="font-mono truncate">{triggerSuccess}</span>
          </div>
        )}
        <button
          onClick={() => { setTriggerSuccess(null); onTrigger() }}
          className="w-full flex items-center justify-center gap-2 py-2 rounded bg-amber-500/15 border border-amber-500/25 text-amber-300 hover:bg-amber-500/25 text-sm font-medium transition-colors"
        >
          <Zap size={14} /> Trigger Disruption
        </button>
      </div>
    </div>
  )
}

// ─── Agent Workbench ───────────────────────────────────────────────────────

// Function: AgentWorkbench
export function AgentWorkbench() {
  const [agents, setAgents] = useState<AgentCard[]>([])
  const [loading, setLoading] = useState(true)
  const [useMock, setUseMock] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<AgentCard | null>(null)
  const [selectedDetail, setSelectedDetail] = useState<DetailItem | null>(null)
  const [showTrigger, setShowTrigger] = useState(false)
  const [triggerSuccess, setTriggerSuccess] = useState<string | null>(null)
  const loadingRef = useRef(false)

  const load = useCallback(async () => {
    if (loadingRef.current) return
    loadingRef.current = true
    setLoading(true)
    try {
      const data = await listAgents()
      setAgents(data)
      setSelectedAgent((current) => current ? (data.find((a) => a.name === current.name) ?? current) : null)
      setUseMock(false)
    } catch {
      setAgents(MOCK_AGENTS)
      setUseMock(true)
    } finally {
      setLoading(false)
      loadingRef.current = false
    }
  }, [])

  useEffect(() => {
    void load()
    const interval = setInterval(() => void load(), 30000)
    return () => clearInterval(interval)
  }, [load])

  // Live refresh on incident state changes
  useEffect(() => {
    const url = getIncidentStreamURL()
    return createSSEStream(url, (type) => {
      if (type === 'incident_state') void load()
    })
  }, [load])

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-6 space-y-4">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <h1 className="font-display text-xl text-text mb-1">Agent Workbench</h1>
            <p className="text-sm text-text-3">
              {useMock
                ? 'Showing default agent definitions — connect backend for live data'
                : `${agents.length} agents monitored`}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowTrigger(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-amber-500/30 bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 text-xs font-medium transition-colors"
            >
              <Zap size={13} /> Trigger Disruption
            </button>
            <button
              onClick={() => void load()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-border hover:border-border-hi text-text-2 text-xs transition-colors"
            >
              <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
        </div>

        {triggerSuccess && (
          <div className="flex items-center gap-2 text-xs text-green-400 bg-green-500/10 border border-green-500/20 rounded px-4 py-2.5">
            <CheckCircle size={14} />
            Disruption triggered — incident <span className="font-mono">{triggerSuccess}</span> is being processed
            <button onClick={() => setTriggerSuccess(null)} className="ml-auto text-text-3 hover:text-text">
              <X size={13} />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentCardComponent
              key={agent.name}
              agent={agent}
              selected={selectedAgent?.name === agent.name}
              onOpen={(next) => { setSelectedAgent(next); setSelectedDetail(null) }}
              onInspect={(next, detail) => { setSelectedAgent(next); setSelectedDetail(detail) }}
            />
          ))}
        </div>
      </div>

      {selectedAgent && (
        <AgentDetailPanel
          agent={selectedAgent}
          detail={selectedDetail}
          onClose={() => { setSelectedAgent(null); setSelectedDetail(null) }}
          onDetail={setSelectedDetail}
          onTrigger={() => setShowTrigger(true)}
        />
      )}

      {showTrigger && (
        <TriggerDisruptionModal
          agentName={selectedAgent?.name ?? 'Workbench'}
          onClose={() => setShowTrigger(false)}
          onSuccess={(id) => {
            setShowTrigger(false)
            setTriggerSuccess(id)
            void load()
          }}
        />
      )}
    </div>
  )
}
