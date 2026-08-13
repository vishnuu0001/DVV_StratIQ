// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/views (IncidentCenter.tsx)
// Date: 2025-08-27
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback } from 'react'
import * as d3 from 'd3'
import { RefreshCw, Filter, CheckCircle, XCircle, ChevronRight, AlertTriangle, UserRound, Activity } from 'lucide-react'
import { SeverityBadge } from '../components/SeverityBadge'
import { Timeline } from '../components/Timeline'
import { JsonViewer } from '../components/JsonViewer'
import { useIncidents } from '../hooks/useIncidents'
import { getIncidentTimeline, approveIncident, rejectIncident } from '../api/agents'
import { useAppStore } from '../store/useAppStore'
import type { Incident, TimelineEvent, SpecialistRun } from '../api/agents'

const STATE_COLORS: Record<string, string> = {
  RESOLVED: 'text-green-400 bg-green-500/10 border-green-500/20',
  CLASSIFIED: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  DISPATCHED: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  IN_PROGRESS: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  AWAITING_APPROVAL: 'text-yellow-300 bg-yellow-400/10 border-yellow-400/20',
  AWAITING_HUMAN_APPROVAL: 'text-yellow-300 bg-yellow-400/10 border-yellow-400/20',
  ESCALATED: 'text-red-400 bg-red-500/10 border-red-500/20',
  BLOCKED: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  NEW: 'text-text-2 bg-surface-3 border-border',
  FAILED: 'text-red-400 bg-red-600/10 border-red-600/20',
  REJECTED: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
}

// Function: StateChip
function StateChip({ state }: { state: string }) {
  const cls = STATE_COLORS[state] ?? STATE_COLORS['NEW']
  return (
    <span className={`scm-status-chip ${cls}`}>
      {humanize(state)}
    </span>
  )
}

// Function: humanize
function humanize(value: string): string {
  return value
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

// Function: shortId
function shortId(value: string): string {
  return value.length > 18 ? `${value.slice(0, 8)}…${value.slice(-6)}` : value
}

interface SummarySection {
  role: string
  text: string
}

// Function: parseSummary
function parseSummary(summary: string): { overview: string; actions: SummarySection[] } {
  const actionPattern = /\[([A-Z][A-Z _-]+)\]\s*([^[]+)/g
  const actions: SummarySection[] = []
  let match: RegExpExecArray | null
  while ((match = actionPattern.exec(summary)) !== null) {
    actions.push({ role: humanize(match[1].trim()), text: match[2].trim() })
  }
  const firstAction = summary.search(/\[[A-Z][A-Z _-]+\]/)
  const overview = (firstAction >= 0 ? summary.slice(0, firstAction) : summary)
    .replace(/_/g, ' ')
    .replace(/\s*\|\s*/g, ' · ')
    .replace(/\s+/g, ' ')
    .trim()
  return { overview, actions }
}

// Function: IncidentSummary
function IncidentSummary({ summary }: { summary: string }) {
  const parsed = parseSummary(summary)
  return (
    <div className="scm-incident-summary">
      <div className="scm-section-heading"><Activity size={14} /> Incident summary</div>
      {parsed.overview && <p className="scm-summary-lead">{parsed.overview}</p>}
      {parsed.actions.length > 0 && (
        <div className="scm-response-grid">
          {parsed.actions.map((action, index) => (
            <div className="scm-response-card" key={`${action.role}-${index}`}>
              <div className="scm-response-role">{action.role}</div>
              <p>{action.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

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

// Mini D3 blast radius graph
// Function: BlastRadiusGraph
function BlastRadiusGraph({ nodes, edges }: { nodes: Incident['blast_radius'] extends null ? never : NonNullable<Incident['blast_radius']>['nodes']; edges: NonNullable<Incident['blast_radius']>['edges'] }) {
  const svgRef = React.useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return
    const width = svgRef.current.clientWidth || 400
    const height = 260

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    interface BRNode extends d3.SimulationNodeDatum { id: string; domain: string }
    interface BRLink { source: string | BRNode; target: string | BRNode }

    const nodeIds = new Set(nodes.map((n) => n.id))
    const d3nodes: BRNode[] = nodes.map((n) => ({ id: n.id, domain: n.domain }))
    const d3links: BRLink[] = edges
      .filter((e) => nodeIds.has(e.from) && nodeIds.has(e.to))
      .map((e) => ({ source: e.from, target: e.to }))

    const sim = d3.forceSimulation<BRNode>(d3nodes)
      .force('link', d3.forceLink<BRNode, BRLink>(d3links).id((d) => d.id).distance(60))
      .force('charge', d3.forceManyBody().strength(-150))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide(20))

    const g = svg.append('g')

    const linkEl = g.append('g').selectAll<SVGLineElement, BRLink>('line')
      .data(d3links).join('line')
      .attr('stroke', '#f59e0b').attr('stroke-width', 1.5).attr('opacity', 0.6)

    const nodeEl = g.append('g').selectAll<SVGCircleElement, BRNode>('circle')
      .data(d3nodes).join('circle')
      .attr('r', 10)
      .attr('fill', (d) => `${domainColor(d.domain)}33`)
      .attr('stroke', (d) => domainColor(d.domain))
      .attr('stroke-width', 2)

    g.append('g').selectAll<SVGTextElement, BRNode>('text')
      .data(d3nodes).join('text')
      .attr('dy', 22).attr('text-anchor', 'middle')
      .attr('font-size', '9px').attr('fill', '#8b9bac')
      .text((d) => d.id)

    sim.on('tick', () => {
      linkEl
        .attr('x1', (d) => (d.source as BRNode).x ?? 0)
        .attr('y1', (d) => (d.source as BRNode).y ?? 0)
        .attr('x2', (d) => (d.target as BRNode).x ?? 0)
        .attr('y2', (d) => (d.target as BRNode).y ?? 0)
      nodeEl.attr('cx', (d) => d.x ?? 0).attr('cy', (d) => d.y ?? 0)
      g.selectAll<SVGTextElement, BRNode>('text')
        .attr('x', (d) => d.x ?? 0).attr('y', (d) => d.y ?? 0)
    })

    return () => { sim.stop() }
  }, [nodes, edges])

  if (nodes.length === 0) {
    return <div className="text-text-3 text-sm py-4 text-center">No blast radius data</div>
  }

  return <svg ref={svgRef} className="w-full h-64" />
}

// Function: domainColor
function domainColor(domain: string): string {
  const colors: Record<string, string> = {
    procurement: '#f59e0b', logistics: '#a78bfa', warehouse: '#06b6d4',
    production: '#10b981', people: '#f43f5e', system: '#facc15',
  }
  return colors[domain.toLowerCase()] ?? '#8b9bac'
}

// Function: formatAction
function formatAction(action: string | Record<string, unknown>): string {
  if (typeof action === 'string') return action
  if (typeof action.tool === 'string') return action.tool
  try {
    return JSON.stringify(action)
  } catch {
    return 'Action'
  }
}

type TabId = 'overview' | 'blast' | 'runs' | 'timeline' | 'decisions'

// Function: IncidentDetail
function IncidentDetail({ incident, onUpdate }: { incident: Incident; onUpdate: (i: Incident) => void }) {
  const [tab, setTab] = useState<TabId>('overview')
  const [timeline, setTimeline] = useState<TimelineEvent[]>([])
  const [tlLoading, setTlLoading] = useState(false)
  const [approving, setApproving] = useState(false)
  const [reason, setReason] = useState('')

  useEffect(() => {
    if (tab === 'timeline') {
      setTlLoading(true)
      getIncidentTimeline(incident.id)
        .then((t) => setTimeline(t))
        .catch(() => setTimeline([]))
        .finally(() => setTlLoading(false))
    }
  }, [tab, incident.id])

  const TABS: { id: TabId; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'blast', label: 'Blast Radius' },
    { id: 'runs', label: `Specialist Runs (${incident.specialist_runs.length})` },
    { id: 'timeline', label: 'Timeline' },
    { id: 'decisions', label: 'Decisions' },
  ]

  return (
    <div className="scm-incident-detail">
      {/* Incident header */}
      <div className="scm-incident-header">
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="scm-incident-id" title={incident.id}>{shortId(incident.id)}</div>
            <div className="scm-incident-title">{humanize(incident.type)}</div>
          </div>
          <div className="flex items-center gap-2">
            <SeverityBadge severity={incident.severity} />
            <StateChip state={incident.state} />
          </div>
        </div>
        <div className="scm-incident-meta">
          <span><strong>Root resource</strong>{incident.root_node_id || 'Not specified'}</span>
          <span><strong>Confidence</strong>{(incident.confidence * 100).toFixed(0)}%</span>
          <span><strong>Created</strong>{formatTs(incident.created_at)}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="scm-incident-tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`scm-incident-tab ${
              tab === t.id
                ? 'scm-incident-tab-active'
                : ''
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="scm-incident-content">
        {tab === 'overview' && (
          <div className="space-y-4">
            {incident.final_summary && (
              <IncidentSummary summary={incident.final_summary} />
            )}
            {incident.owners.length > 0 && (
              <div>
                <div className="scm-section-heading"><UserRound size={14} /> Owners</div>
                <div className="space-y-1.5">
                  {incident.owners.map((o) => (
                    <div key={o.id} className="scm-owner-row">
                      <div>
                        <div className="text-xs font-medium">{o.name}</div>
                        <div className="text-[10px] text-text-3">{o.role}</div>
                      </div>
                      <a href={`mailto:${o.email}`}>{o.email}</a>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {incident.plan && (
              <div>
                <div className="scm-section-heading">Orchestrator plan</div>
                <JsonViewer data={incident.plan} collapsed />
              </div>
            )}
          </div>
        )}

        {tab === 'blast' && (
          <div>
            <div className="text-xs text-text-3 mb-3">
              {incident.blast_radius
                ? `${incident.blast_radius.nodes.length} nodes, ${incident.blast_radius.edges.length} edges affected`
                : 'No blast radius computed yet'}
            </div>
            {incident.blast_radius && (
              <div className="bg-surface-2 border border-border rounded overflow-hidden">
                <BlastRadiusGraph
                  nodes={incident.blast_radius.nodes}
                  edges={incident.blast_radius.edges}
                />
              </div>
            )}
          </div>
        )}

        {tab === 'runs' && (
          <div className="space-y-3">
            {incident.specialist_runs.length === 0 ? (
              <div className="text-text-3 text-sm text-center py-4">No specialist runs yet</div>
            ) : (
              incident.specialist_runs.map((run: SpecialistRun, i: number) => (
                <div key={i} className="bg-surface-2 border border-border rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{run.agent_name}</span>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-mono ${
                        run.status === 'completed' ? 'text-green-400' : run.status === 'failed' ? 'text-red-400' : 'text-amber-400'
                      }`}>{run.status}</span>
                      <span className="text-xs text-text-3">{(run.confidence * 100).toFixed(0)}% conf</span>
                    </div>
                  </div>
                  <div className="text-xs text-text-2 leading-relaxed">{run.findings}</div>
                  {run.actions.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {run.actions.map((a, j) => (
                        <span key={j} className="text-[10px] font-mono bg-surface-3 border border-border px-1.5 py-0.5 rounded">{formatAction(a)}</span>
                      ))}
                    </div>
                  )}
                  {run.scope_violations.length > 0 && (
                    <div className="text-xs text-red-400">⚠ Scope violations: {run.scope_violations.join(', ')}</div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {tab === 'timeline' && (
          <div>
            {tlLoading ? (
              <div className="text-text-3 text-sm text-center py-4">Loading timeline…</div>
            ) : (
              <Timeline events={timeline} />
            )}
          </div>
        )}

        {tab === 'decisions' && (
          <div className="space-y-4">
            {incident.human_decisions.length > 0 && (
              <div className="space-y-2">
                {incident.human_decisions.map((d, i) => (
                  <div key={i} className={`rounded border p-3 ${d.decision === 'approved' ? 'border-green-500/30 bg-green-500/5' : 'border-red-500/30 bg-red-500/5'}`}>
                    <div className="flex items-center gap-2 mb-1">
                      {d.decision === 'approved'
                        ? <CheckCircle size={13} className="text-green-400" />
                        : <XCircle size={13} className="text-red-400" />}
                      <span className="text-xs font-medium capitalize">{d.decision}</span>
                      <span className="text-xs text-text-3">by {d.decided_by}</span>
                      <span className="text-xs text-text-3 ml-auto">{formatTs(d.decided_at)}</span>
                    </div>
                    {d.reason && <p className="text-xs text-text-2">{d.reason}</p>}
                  </div>
                ))}
              </div>
            )}

            {incident.state === 'AWAITING_APPROVAL' && (
              <div className="space-y-3 border-t border-border pt-4">
                <div className="text-xs text-text-3 uppercase tracking-wider">Pending Decision</div>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Reason / notes…"
                  className="w-full bg-surface-2 border border-border rounded px-3 py-2 text-xs text-text placeholder-text-3 resize-none focus:outline-none focus:border-border-hi"
                  rows={3}
                />
                <div className="flex gap-2">
                  <button
                    disabled={approving}
                    onClick={async () => {
                      setApproving(true)
                      try {
                        const updated = await approveIncident(incident.id, reason || 'Approved', 'operator')
                        onUpdate(updated)
                      } catch {
                        // ignore
                      } finally {
                        setApproving(false)
                      }
                    }}
                    className="flex-1 flex items-center justify-center gap-2 py-2 rounded bg-green-500/20 border border-green-500/30 text-green-400 hover:bg-green-500/30 text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    <CheckCircle size={14} /> Approve
                  </button>
                  <button
                    disabled={approving}
                    onClick={async () => {
                      setApproving(true)
                      try {
                        const updated = await rejectIncident(incident.id, reason || 'Rejected', 'operator')
                        onUpdate(updated)
                      } catch {
                        // ignore
                      } finally {
                        setApproving(false)
                      }
                    }}
                    className="flex-1 flex items-center justify-center gap-2 py-2 rounded bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30 text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    <XCircle size={14} /> Reject
                  </button>
                </div>
              </div>
            )}

            {incident.human_decisions.length === 0 && incident.state !== 'AWAITING_APPROVAL' && (
              <div className="text-text-3 text-sm text-center py-4">No decisions yet</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Function: IncidentCenter
export function IncidentCenter() {
  const { incidents, loading, reload, upsertIncident } = useIncidents()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [stateFilter, setStateFilter] = useState('')
  const [severityFilter, setSeverityFilter] = useState('')

  const selected = incidents.find((i) => i.id === selectedId) ?? null

  const filtered = incidents.filter((i) => {
    if (stateFilter && i.state !== stateFilter) return false
    if (severityFilter && i.severity !== severityFilter) return false
    return true
  })

  const handleUpdate = useCallback((updated: Incident) => {
    upsertIncident(updated)
    setSelectedId(updated.id)
  }, [upsertIncident])

  const STATES = ['', 'NEW', 'CLASSIFIED', 'DISPATCHED', 'IN_PROGRESS', 'AWAITING_APPROVAL', 'RESOLVED', 'ESCALATED', 'BLOCKED', 'REJECTED', 'FAILED']
  const SEVERITIES = ['', 'critical', 'high', 'med', 'low', 'info']

  return (
    <div className="scm-incident-center">
      {/* Left: incident list */}
      <div className="scm-incident-list-pane">
        {/* Filters */}
        <div className="scm-incident-filters">
          <div className="flex items-center gap-2">
            <Filter size={12} className="text-text-3" />
            <span className="scm-filter-title">Filters</span>
            <span className="scm-result-count">{filtered.length} incidents</span>
            <button onClick={() => void reload()} className="ml-auto p-1 rounded hover:bg-surface-2 text-text-3">
              <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
          <select
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            className="w-full bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-2 focus:outline-none"
          >
            <option value="">All states</option>
            {STATES.filter(Boolean).map((s) => <option key={s} value={s}>{humanize(s)}</option>)}
          </select>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-full bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-2 focus:outline-none"
          >
            <option value="">All severities</option>
            {SEVERITIES.filter(Boolean).map((s) => <option key={s} value={s}>{humanize(s)}</option>)}
          </select>
        </div>

        {/* List */}
        <div className="scm-incident-list">
          {loading && filtered.length === 0 ? (
            <div className="p-4 text-center text-text-3 text-sm">Loading…</div>
          ) : filtered.length === 0 ? (
            <div className="p-4 text-center text-text-3 text-sm">No incidents. Connect backend to begin.</div>
          ) : (
            filtered.map((inc) => (
              <button
                key={inc.id}
                onClick={() => setSelectedId(inc.id)}
                className={`scm-incident-list-item ${selectedId === inc.id ? 'scm-incident-list-item-active' : ''}`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="scm-list-id" title={inc.id}>{shortId(inc.id)}</span>
                  <SeverityBadge severity={inc.severity} />
                </div>
                <div className="scm-list-title">{humanize(inc.type)}</div>
                <div className="flex items-center justify-between">
                  <StateChip state={inc.state} />
                  <ChevronRight size={12} className="text-text-3" />
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Right: detail */}
      <div className="scm-incident-detail-pane">
        {selected ? (
          <IncidentDetail incident={selected} onUpdate={handleUpdate} />
        ) : (
          <div className="scm-empty-detail">
            <AlertTriangle size={28} />
            <strong>No incident selected</strong>
            <span>Select an incident from the list to view its impact, response plan, and decisions.</span>
          </div>
        )}
      </div>
    </div>
  )
}
