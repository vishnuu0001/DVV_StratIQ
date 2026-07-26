// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/views (Overview.tsx)
// Date: 2025-08-23
// ---------------------------------------------------------------------------
import React, { useEffect, useState, useRef, useCallback } from 'react'
import {
  AlertTriangle,
  Activity,
  Clock,
  CheckCircle,
  Database,
  GitBranch,
  Bot,
  Inbox,
  X,
} from 'lucide-react'
import { StatCard } from '../components/StatCard'
import { SeverityBadge } from '../components/SeverityBadge'
import { JsonViewer } from '../components/JsonViewer'
import { useAppStore } from '../store/useAppStore'
import { listIncidents, getIncidentStreamURL } from '../api/agents'
import { listEvents, getEventStreamURL } from '../api/inspector'
import { getKGHealth, listEntities, traverseKG } from '../api/kg'
import { createSSEStream } from '../api/sse'
import type { Incident, SpecialistRun } from '../api/agents'
import type { CanonicalEvent } from '../api/inspector'
import type { KGEdge, KGEntity } from '../api/kg'

const MAX_EVENTS = 10
const KG_DRILLDOWN_KINDS = ['Supplier', 'PurchaseOrder', 'Warehouse', 'Shipment', 'ProductionOrder', 'Material']
type DrilldownKey = 'active' | 'critical' | 'events' | 'approvals' | 'resolved' | 'kgNodes' | 'kgEdges' | 'agentRuns'

interface AgentRunDrilldown extends SpecialistRun {
  incident_id: string
  incident_type: string
}

interface KgDrilldownData {
  nodes: KGEntity[]
  edges: KGEdge[]
}

// Function: loadKgSamples
async function loadKgSamples(): Promise<KgDrilldownData> {
  const results = await Promise.allSettled(KG_DRILLDOWN_KINDS.map((kind) => listEntities(kind, 10)))
  const nodes = results.flatMap((result) => result.status === 'fulfilled' ? result.value : [])
  const edgeMap = new Map<string, KGEdge>()

  for (const root of nodes.slice(0, 6)) {
    try {
      const graph = await traverseKG(root.id, ['flow', 'meta', 'owns'], 2)
      graph.nodes.forEach((node) => {
        if (!nodes.some((existing) => existing.id === node.id)) nodes.push(node)
      })
      graph.edges.forEach((edge) => edgeMap.set(`${edge.from}->${edge.to}:${edge.verb}`, edge))
    } catch {
      // Skip roots that cannot be traversed.
    }
  }

  return { nodes, edges: Array.from(edgeMap.values()) }
}

// Function: formatTs
function formatTs(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ts
  }
}

const STATE_COLORS: Record<string, string> = {
  RESOLVED: 'text-green-400 bg-green-500/10 border-green-500/20',
  CLASSIFIED: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  DISPATCHED: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  IN_PROGRESS: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  AWAITING_APPROVAL: 'text-yellow-300 bg-yellow-400/10 border-yellow-400/20',
  ESCALATED: 'text-red-400 bg-red-500/10 border-red-500/20',
  NEW: 'text-text-2 bg-surface-3 border-border',
  FAILED: 'text-red-400 bg-red-600/10 border-red-600/20',
}

// Function: Overview
export function Overview() {
  const { criticalCount, openApprovals, eventsPerMin, setEventsPerMin, setCriticalCount, setOpenApprovals } = useAppStore()
  const selectEvent = useAppStore((s) => s.selectEvent)
  const selectIncident = useAppStore((s) => s.selectIncident)

  const [incidents, setIncidents] = useState<Incident[]>([])
  const [recentEvents, setRecentEvents] = useState<CanonicalEvent[]>([])
  const [kgStats, setKgStats] = useState({ node_count: 0, edge_count: 0 })
  const [kgSamples, setKgSamples] = useState<KGEntity[]>([])
  const [kgEdgeSamples, setKgEdgeSamples] = useState<KGEdge[]>([])
  const [resolvedToday, setResolvedToday] = useState(0)
  const [activeCount, setActiveCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [drilldown, setDrilldown] = useState<DrilldownKey | null>(null)
  const [selectedDrilldownItem, setSelectedDrilldownItem] = useState<Incident | CanonicalEvent | KGEntity | KGEdge | AgentRunDrilldown | null>(null)

  const eventCountRef = useRef(0)
  const eventWindowRef = useRef<number[]>([])
  const newEventIds = useRef<Set<string>>(new Set())

  const addEvent = useCallback((evt: CanonicalEvent) => {
    setRecentEvents((prev) => {
      if (prev.some((e) => e.event_id === evt.event_id)) return prev
      newEventIds.current.add(evt.event_id)
      setTimeout(() => newEventIds.current.delete(evt.event_id), 600)
      return [evt, ...prev].slice(0, MAX_EVENTS)
    })
    // Track events per minute
    const now = Date.now()
    eventWindowRef.current = [...eventWindowRef.current.filter((t) => now - t < 60000), now]
    setEventsPerMin(eventWindowRef.current.length)
    eventCountRef.current++
  }, [setEventsPerMin])

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [incResult, evResult, kgResult, kgSampleResult] = await Promise.allSettled([
        listIncidents({ limit: 50 }),
        listEvents({ limit: MAX_EVENTS }),
        getKGHealth(),
        loadKgSamples(),
      ])

      if (incResult.status === 'fulfilled') {
        const items = incResult.value.items
        setIncidents(items)
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        setResolvedToday(items.filter((i) => i.resolved_at && new Date(i.resolved_at) >= today).length)
        setActiveCount(items.filter((i) => !['RESOLVED', 'REJECTED', 'FAILED'].includes(i.state)).length)
        setCriticalCount(items.filter((i) =>
          ['critical', 'high'].includes(i.severity?.toLowerCase?.() ?? '') &&
          !['RESOLVED', 'REJECTED', 'FAILED'].includes(i.state)
        ).length)
        setOpenApprovals(items.filter((i) => i.state === 'AWAITING_APPROVAL').length)
      }
      if (evResult.status === 'fulfilled') setRecentEvents(evResult.value.items)
      if (kgResult.status === 'fulfilled') setKgStats(kgResult.value)
      if (kgSampleResult.status === 'fulfilled') {
        setKgSamples(kgSampleResult.value.nodes)
        setKgEdgeSamples(kgSampleResult.value.edges)
      }
    } finally {
      setLoading(false)
    }
  }, [setCriticalCount, setOpenApprovals])

  useEffect(() => {
    void load()
    const interval = setInterval(() => void load(), 20000)
    return () => clearInterval(interval)
  }, [load])

  useEffect(() => {
    const url = getEventStreamURL()
    const cleanup = createSSEStream(url, (type, data) => {
      if (type === 'event' || type === 'message') {
        addEvent(data as CanonicalEvent)
      }
    })
    return cleanup
  }, [addEvent])

  useEffect(() => {
    const url = getIncidentStreamURL()
    const cleanup = createSSEStream(url, (type) => {
      if (type === 'incident_state') void load()
    })
    return cleanup
  }, [load])

  const statsData = [
    {
      key: 'active' as const,
      title: 'Active Disruptions',
      value: loading ? '…' : activeCount,
      icon: AlertTriangle,
      color: activeCount > 0 ? 'text-red-400' : 'text-text-2',
      pulse: activeCount > 0,
    },
    {
      key: 'critical' as const,
      title: 'Critical Incidents',
      value: loading ? '…' : criticalCount,
      icon: AlertTriangle,
      color: criticalCount > 0 ? 'text-red-400' : 'text-text-2',
      pulse: criticalCount > 0,
    },
    {
      key: 'events' as const,
      title: 'Events / Min',
      value: eventsPerMin.toFixed(1),
      icon: Activity,
      color: 'text-cyan-400',
    },
    {
      key: 'approvals' as const,
      title: 'Open Approvals',
      value: loading ? '…' : openApprovals,
      icon: Clock,
      color: openApprovals > 0 ? 'text-amber-400' : 'text-text-2',
    },
    {
      key: 'resolved' as const,
      title: 'Resolved Today',
      value: loading ? '…' : resolvedToday,
      icon: CheckCircle,
      color: 'text-green-400',
    },
    {
      key: 'kgNodes' as const,
      title: 'KG Nodes',
      value: loading ? '…' : kgStats.node_count.toLocaleString(),
      icon: Database,
      color: 'text-purple-400',
    },
    {
      key: 'kgEdges' as const,
      title: 'KG Edges',
      value: loading ? '…' : kgStats.edge_count.toLocaleString(),
      icon: GitBranch,
      color: 'text-cyan-400',
    },
    {
      key: 'agentRuns' as const,
      title: 'Agent Runs',
      value: loading ? '…' : incidents.reduce((a, i) => a + i.specialist_runs.length, 0),
      icon: Bot,
      color: 'text-purple-400',
    },
  ]

  const activeIncidents = incidents.filter((i) => !['RESOLVED', 'REJECTED', 'FAILED'].includes(i.state))
  const criticalIncidents = incidents.filter((i) => ['critical', 'high'].includes(i.severity?.toLowerCase?.() ?? ''))
  const approvalIncidents = incidents.filter((i) => i.state === 'AWAITING_APPROVAL')
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const resolvedIncidents = incidents.filter((i) => i.resolved_at && new Date(i.resolved_at) >= today)
  const agentRuns: AgentRunDrilldown[] = incidents.flatMap((incident) =>
    incident.specialist_runs.map((run) => ({
      ...run,
      incident_id: incident.id,
      incident_type: incident.type,
    }))
  )

  const drilldownTitles: Record<DrilldownKey, string> = {
    active: 'Active Disruptions',
    critical: 'Critical Incidents',
    events: 'Live Events',
    approvals: 'Open Approvals',
    resolved: 'Resolved Today',
    kgNodes: 'KG Nodes',
    kgEdges: 'KG Edges',
    agentRuns: 'Agent Runs',
  }

  // Function: openDrilldown
  function openDrilldown(key: DrilldownKey) {
    setDrilldown(key)
    setSelectedDrilldownItem(null)
  }

  // Function: getDrilldownItems
  function getDrilldownItems(): Array<Incident | CanonicalEvent | KGEntity | KGEdge | AgentRunDrilldown> {
    switch (drilldown) {
      case 'active':
        return activeIncidents
      case 'critical':
        return criticalIncidents
      case 'events':
        return recentEvents
      case 'approvals':
        return approvalIncidents
      case 'resolved':
        return resolvedIncidents
      case 'kgNodes':
        return kgSamples
      case 'kgEdges':
        return kgEdgeSamples
      case 'agentRuns':
        return agentRuns
      default:
        return []
    }
  }

  // Function: renderDrilldownRow
  function renderDrilldownRow(item: Incident | CanonicalEvent | KGEntity | KGEdge | AgentRunDrilldown) {
    if ('event_id' in item) {
      return (
        <button key={item.event_id} onClick={() => { setSelectedDrilldownItem(item); selectEvent(item) }} className="w-full px-3 py-2.5 text-left hover:bg-surface-2 border-b border-border/50">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs text-text truncate">{item.event_type}</span>
            <SeverityBadge severity={item.severity} />
          </div>
          <div className="mt-1 flex justify-between gap-2 text-[10px] text-text-3 font-mono">
            <span className="truncate">{item.source_system}</span>
            <span>{formatTs(item.ingested_at)}</span>
          </div>
        </button>
      )
    }

    if ('root_node_id' in item) {
      return (
        <button key={item.id} onClick={() => { setSelectedDrilldownItem(item); selectIncident(item) }} className="w-full px-3 py-2.5 text-left hover:bg-surface-2 border-b border-border/50">
          <div className="flex items-center justify-between gap-2">
            <span className="font-mono text-xs text-text-3 truncate">{item.id}</span>
            <SeverityBadge severity={item.severity} />
          </div>
          <div className="mt-1 flex items-center justify-between gap-2">
            <span className="text-xs text-text-2 truncate">{(item.type ?? 'incident').replace(/_/g, ' ')}</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded border font-mono uppercase ${STATE_COLORS[item.state] ?? STATE_COLORS['NEW']}`}>
              {item.state}
            </span>
          </div>
        </button>
      )
    }

    if ('agent_name' in item) {
      return (
        <button key={`${item.incident_id}-${item.agent_name}-${item.started_at}`} onClick={() => setSelectedDrilldownItem(item)} className="w-full px-3 py-2.5 text-left hover:bg-surface-2 border-b border-border/50">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs text-text truncate">{item.agent_name}</span>
            <span className="text-[10px] text-text-3 font-mono uppercase">{item.status}</span>
          </div>
          <div className="mt-1 flex justify-between gap-2 text-[10px] text-text-3">
            <span className="truncate">{item.domain} / {(item.incident_type ?? 'incident').replace(/_/g, ' ')}</span>
            <span className="font-mono">{((item.confidence ?? 0) * 100).toFixed(0)}%</span>
          </div>
        </button>
      )
    }

    if ('from' in item) {
      return (
        <button key={`${item.from}-${item.to}-${item.verb}`} onClick={() => setSelectedDrilldownItem(item)} className="w-full px-3 py-2.5 text-left hover:bg-surface-2 border-b border-border/50">
          <div className="text-xs text-text font-mono truncate">{item.from} {'->'} {item.to}</div>
          <div className="mt-1 flex justify-between gap-2 text-[10px] text-text-3">
            <span className="uppercase">{item.kind}</span>
            <span className="font-mono">{item.verb}</span>
          </div>
        </button>
      )
    }

    return (
      <button key={item.id} onClick={() => setSelectedDrilldownItem(item)} className="w-full px-3 py-2.5 text-left hover:bg-surface-2 border-b border-border/50">
        <div className="flex items-center justify-between gap-2">
          <span className="font-mono text-xs text-text truncate">{item.id}</span>
          <span className="text-[10px] text-text-3 uppercase">{item.kind}</span>
        </div>
        <div className="mt-1 text-[10px] text-text-3 truncate">{item.domain}</div>
      </button>
    )
  }

  // Function: renderDrilldownDetail
  function renderDrilldownDetail() {
    if (!selectedDrilldownItem) {
      return <div className="h-full flex items-center justify-center text-sm text-text-3">Select an L2 row for L3 detail.</div>
    }

    if ('event_id' in selectedDrilldownItem) {
      return (
        <div className="space-y-3">
          <div>
            <div className="font-mono text-xs text-text-3">{selectedDrilldownItem.event_id}</div>
            <div className="text-sm font-medium mt-1">{selectedDrilldownItem.event_type}</div>
          </div>
          <JsonViewer data={selectedDrilldownItem} collapsed />
        </div>
      )
    }

    if ('root_node_id' in selectedDrilldownItem) {
      return (
        <div className="space-y-3">
          <div className="flex items-start justify-between gap-2">
            <div>
              <div className="font-mono text-xs text-text-3">{selectedDrilldownItem.id}</div>
              <div className="text-sm font-medium mt-1">{(selectedDrilldownItem.type ?? 'incident').replace(/_/g, ' ')}</div>
            </div>
            <SeverityBadge severity={selectedDrilldownItem.severity} />
          </div>
          <JsonViewer data={selectedDrilldownItem} collapsed />
        </div>
      )
    }

    if ('agent_name' in selectedDrilldownItem) {
      return (
        <div className="space-y-3">
          <div>
            <div className="font-mono text-xs text-text-3">{selectedDrilldownItem.incident_id}</div>
            <div className="text-sm font-medium mt-1">{selectedDrilldownItem.agent_name}</div>
          </div>
          <JsonViewer data={selectedDrilldownItem} collapsed />
        </div>
      )
    }

    if ('from' in selectedDrilldownItem) {
      return (
        <div className="space-y-3">
          <div>
            <div className="font-mono text-xs text-text-3">{selectedDrilldownItem.from} {'->'} {selectedDrilldownItem.to}</div>
            <div className="text-sm font-medium mt-1">{selectedDrilldownItem.verb}</div>
          </div>
          <JsonViewer data={selectedDrilldownItem} collapsed />
        </div>
      )
    }

    return (
      <div className="space-y-3">
        <div>
          <div className="font-mono text-xs text-text-3">{selectedDrilldownItem.id}</div>
          <div className="text-sm font-medium mt-1">{selectedDrilldownItem.kind}</div>
        </div>
        <JsonViewer data={selectedDrilldownItem.properties} collapsed />
      </div>
    )
  }

  if (loading && incidents.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-text-3 text-sm">
        <div className="text-center space-y-2">
          <Inbox size={32} className="mx-auto text-text-3/40" />
          <div>Loading overview…</div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div>
        <h1 className="font-display text-xl text-text mb-1">Command Overview</h1>
        <p className="text-sm text-text-3">Real-time supply chain disruption status</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {statsData.map((s) => (
          <StatCard
            key={s.title}
            title={s.title}
            value={s.value}
            icon={s.icon}
            color={s.color}
            pulse={s.pulse}
            onClick={() => openDrilldown(s.key)}
            active={drilldown === s.key}
          />
        ))}
      </div>

      {drilldown && (
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">{drilldownTitles[drilldown]}</span>
              <span className="ml-2 text-xs text-text-3 font-mono">L2 / L3</span>
            </div>
            <button
              onClick={() => { setDrilldown(null); setSelectedDrilldownItem(null) }}
              className="p-1 rounded hover:bg-surface-2 text-text-3 hover:text-text transition-colors"
              aria-label="Close drilldown"
            >
              <X size={16} />
            </button>
          </div>
          <div className="grid grid-cols-1 xl:grid-cols-[minmax(280px,420px)_1fr] min-h-[320px]">
            <div className="border-b xl:border-b-0 xl:border-r border-border max-h-[420px] overflow-y-auto">
              {getDrilldownItems().length === 0 ? (
                <div className="px-4 py-8 text-center text-text-3 text-sm">No records available for this drilldown.</div>
              ) : (
                getDrilldownItems().map(renderDrilldownRow)
              )}
            </div>
            <div className="p-4 max-h-[420px] overflow-y-auto">
              {renderDrilldownDetail()}
            </div>
          </div>
        </div>
      )}

      {/* Two columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent incidents */}
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <span className="text-sm font-medium">Recent Incidents</span>
            <span className="text-xs text-text-3 font-mono">Last 5</span>
          </div>
          <div className="divide-y divide-border/50">
            {incidents.length === 0 ? (
              <div className="px-4 py-6 text-center text-text-3 text-sm">
                No incidents. Connect backend to begin.
              </div>
            ) : (
              incidents.slice(0, 5).map((inc) => (
                <button
                  key={inc.id}
                  onClick={() => selectIncident(inc)}
                  className="w-full px-4 py-3 hover:bg-surface-2 transition-colors text-left"
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="font-mono text-xs text-text-3 truncate">{inc.id}</span>
                    <SeverityBadge severity={inc.severity} />
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs text-text-2 truncate">{inc.type.replace(/_/g, ' ')}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border font-mono uppercase ${STATE_COLORS[inc.state] ?? STATE_COLORS['NEW']}`}>
                      {inc.state}
                    </span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Recent events */}
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <span className="text-sm font-medium">Live Events</span>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 dot-blink" />
              <span className="text-xs text-text-3 font-mono">Stream</span>
            </div>
          </div>
          <div className="divide-y divide-border/50">
            {recentEvents.length === 0 ? (
              <div className="px-4 py-6 text-center text-text-3 text-sm">
                Waiting for events…
              </div>
            ) : (
              recentEvents.map((evt) => (
                <button
                  key={evt.event_id}
                  onClick={() => selectEvent(evt)}
                  className={`w-full px-4 py-2.5 hover:bg-surface-2 transition-colors text-left ${
                    newEventIds.current.has(evt.event_id) ? 'row-new' : ''
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-0.5">
                    <span className="text-xs text-text truncate">{evt.event_type}</span>
                    <SeverityBadge severity={evt.severity} />
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[10px] text-text-3 font-mono truncate">{evt.source_system}</span>
                    <span className="text-[10px] text-text-3 font-mono">{formatTs(evt.ingested_at)}</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
