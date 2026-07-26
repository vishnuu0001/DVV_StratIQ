// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (ITSMDashboardPage.jsx)
// Date: 2025-08-15
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback, useRef } from 'react'
import api from '../services/api.js'
import {
  BarChart3, RefreshCw, Zap, TrendingUp, TrendingDown, Minus,
  Clock, CheckCircle2, AlertTriangle, XCircle, Shield, Activity,
  RotateCcw, Settings, ChevronRight, Play, X, ArrowLeft, User, Server,
} from 'lucide-react'

const SCENARIOS = [
  { id: 'normal',   label: 'Normal',   color: 'bg-blue-600',    ring: 'ring-blue-500'   },
  { id: 'good',     label: 'Good',     color: 'bg-emerald-600', ring: 'ring-emerald-500'},
  { id: 'degraded', label: 'Degraded', color: 'bg-amber-600',   ring: 'ring-amber-500'  },
  { id: 'critical', label: 'Critical', color: 'bg-red-600',     ring: 'ring-red-500'    },
]

// Function: healthColor
function healthColor(score) {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-amber-400'
  return 'text-red-400'
}
// Function: healthBg
function healthBg(score) {
  if (score >= 80) return 'bg-emerald-500'
  if (score >= 60) return 'bg-amber-500'
  return 'bg-red-500'
}
// Function: healthLabel
function healthLabel(score) {
  if (score >= 80) return 'Healthy'
  if (score >= 60) return 'Degraded'
  return 'Critical'
}

// Function: colorClassLowerIsBetter
function colorClassLowerIsBetter(value, goodMax, warnMax) {
  if (value <= goodMax) return 'text-emerald-400'
  if (value <= warnMax) return 'text-amber-400'
  return 'text-red-400'
}

// Function: colorClassHigherIsBetter
function colorClassHigherIsBetter(value, goodMin, warnMin) {
  if (value >= goodMin) return 'text-emerald-400'
  if (value >= warnMin) return 'text-amber-400'
  return 'text-red-400'
}

// Function: TrendIcon
function TrendIcon({ dir }) {
  if (dir === 'up')   return <TrendingUp   size={12} className="text-red-400 inline" />
  if (dir === 'down') return <TrendingDown size={12} className="text-emerald-400 inline" />
  return <Minus size={12} className="text-gray-500 inline" />
}

// Function: KPICard
function KPICard({ label, value, unit, sub, trend, color = 'text-white', icon: Icon, onClick }) {
  const Tag = onClick ? 'button' : 'div'
  return (
    <Tag
      onClick={onClick}
      className={`bg-white/[0.04] border border-white/10 rounded-2xl p-4 flex flex-col gap-1.5 min-w-0 text-left w-full transition-colors ${
        onClick ? 'hover:bg-white/[0.07] hover:border-white/20 cursor-pointer' : ''
      }`}
    >
      <div className="flex items-center gap-1.5 text-gray-400">
        {Icon && <Icon size={13} />}
        <span className="text-[10px] font-semibold uppercase tracking-widest truncate">{label}</span>
      </div>
      <div className={`text-2xl font-black ${color} leading-none`}>
        {value ?? <span className="text-gray-600 text-base">—</span>}
        {unit && <span className="text-xs font-normal text-gray-500 ml-1">{unit}</span>}
      </div>
      {sub && <div className="text-[10px] text-gray-500 truncate">{sub}</div>}
      {trend && (
        <div className="text-[10px] text-gray-500 flex items-center gap-1 mt-0.5">
          <TrendIcon dir={trend} /> vs last period
        </div>
      )}
    </Tag>
  )
}

// Function: SectionHeader
function SectionHeader({ title, accent = 'from-blue-500 to-cyan-500' }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <span className={`w-1 h-4 rounded-full bg-gradient-to-b ${accent} block`} />
      <h3 className="text-xs font-black uppercase tracking-widest text-white">{title}</h3>
      <span className="h-px flex-1 bg-white/8" />
    </div>
  )
}

// Function: ServiceBar
function ServiceBar({ service, total, max, onClick }) {
  const pct = max ? Math.round((total / max) * 100) : 0
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-3 text-xs w-full text-left group"
    >
      <span className="w-32 text-gray-400 truncate shrink-0 group-hover:text-white transition-colors">{service}</span>
      <div className="flex-1 h-2.5 bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-500 group-hover:brightness-125"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-white font-semibold w-6 text-right shrink-0">{total}</span>
    </button>
  )
}

const TREND_LABEL = { increasing: '↑ Increasing', decreasing: '↓ Decreasing', stable: '→ Stable' }
const TREND_CLS   = { increasing: 'text-red-400', decreasing: 'text-emerald-400', stable: 'text-gray-400' }

// Function: prioClass
function prioClass(p) {
  return p === 'P1' ? 'text-red-400' : p === 'P2' ? 'text-orange-400' : p === 'P3' ? 'text-yellow-400' : 'text-gray-400'
}

/** L2 — list of the actual records (tickets or changes) behind a clicked KPI/service/problem. */
// Function: DrilldownModal
function DrilldownModal({ drilldown, onClose, onSelectTicket }) {
  if (!drilldown) return null
  const { kind, title, subtitle, items } = drilldown
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-white/10 rounded-xl w-full max-w-3xl shadow-2xl flex flex-col max-h-[85vh]">
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10 shrink-0">
          <BarChart3 size={16} className="text-blue-400 shrink-0" />
          <div className="flex-1 min-w-0">
            <h2 className="text-sm font-bold text-white truncate">{title}</h2>
            {subtitle && <p className="text-[11px] text-gray-500 truncate">{subtitle}</p>}
          </div>
          <span className="text-[10px] text-gray-500 shrink-0">{items.length} record{items.length !== 1 ? 's' : ''}</span>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors shrink-0">
            <X size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto min-h-0">
          {kind === 'tickets' ? (
            <>
              <div className="grid grid-cols-[90px_1fr_50px_80px_70px_100px] gap-2 px-4 py-2 text-[10px] font-semibold text-gray-500 uppercase tracking-wider border-b border-white/5 sticky top-0 bg-gray-900 z-10">
                <span>Ticket</span><span>Summary</span><span>Prio</span><span>Status</span><span>Age/MTTR</span><span>Flags</span>
              </div>
              {items.map(t => (
                <button
                  key={t.id}
                  onClick={() => onSelectTicket(t.id)}
                  className="w-full grid grid-cols-[90px_1fr_50px_80px_70px_100px] gap-2 px-4 py-2.5 border-b border-white/5 last:border-0 text-xs text-left hover:bg-white/[0.04] transition-colors"
                >
                  <span className="text-blue-400 font-mono truncate">{t.id}</span>
                  <span className="text-gray-300 truncate pr-2">{t.summary} <span className="text-gray-600">· {t.service}</span></span>
                  <span className={`font-bold ${prioClass(t.priority)}`}>{t.priority}</span>
                  <span className="text-gray-400 truncate">{t.status}</span>
                  <span className="text-gray-300">{t.resolved ? `${t.resolve_hours}h` : `${t.age_hours}h`}</span>
                  <span className="flex items-center gap-1 flex-wrap">
                    {t.sla_breached && <span className="text-[8px] bg-red-500/15 text-red-300 border border-red-500/25 rounded px-1 py-0.5 font-bold">SLA</span>}
                    {t.reopened && <span className="text-[8px] bg-amber-500/15 text-amber-300 border border-amber-500/25 rounded px-1 py-0.5 font-bold">RO</span>}
                    {t.known_error && <span className="text-[8px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/25 rounded px-1 py-0.5 font-bold">KE</span>}
                  </span>
                </button>
              ))}
              {items.length === 0 && <div className="px-4 py-8 text-center text-xs text-gray-500">No tickets match this view.</div>}
            </>
          ) : (
            <>
              <div className="grid grid-cols-[100px_1fr_90px_90px_150px] gap-2 px-4 py-2 text-[10px] font-semibold text-gray-500 uppercase tracking-wider border-b border-white/5 sticky top-0 bg-gray-900 z-10">
                <span>Change</span><span>Summary</span><span>Type</span><span>Status</span><span>Implemented</span>
              </div>
              {items.map(c => (
                <div key={c.id} className="grid grid-cols-[100px_1fr_90px_90px_150px] gap-2 px-4 py-2.5 border-b border-white/5 last:border-0 text-xs">
                  <span className="text-blue-400 font-mono">{c.id}</span>
                  <span className="text-gray-300 truncate">{c.summary}</span>
                  <span className="text-gray-400">{c.type}</span>
                  <span className={`font-semibold ${c.status === 'Success' ? 'text-emerald-400' : c.status === 'Failed' ? 'text-red-400' : 'text-amber-400'}`}>{c.status}</span>
                  <span className="text-gray-500">{new Date(c.implemented_at).toLocaleString()}</span>
                </div>
              ))}
              {items.length === 0 && <div className="px-4 py-8 text-center text-xs text-gray-500">No changes match this view.</div>}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

/** L3 — full detail for a single ticket, reached from a drill-down list or the backlog table. */
// Function: TicketDetailModal
function TicketDetailModal({ ticketId, ticket, loading, onClose }) {
  if (!ticketId) return null
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-white/10 rounded-xl w-full max-w-xl shadow-2xl flex flex-col max-h-[85vh]">
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10 shrink-0">
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors shrink-0">
            <ArrowLeft size={16} />
          </button>
          <div className="flex-1 min-w-0">
            <h2 className="text-sm font-bold text-blue-400 font-mono">{ticketId}</h2>
            {ticket && !ticket.error && <p className="text-[11px] text-gray-500 truncate">{ticket.category} · {ticket.service}</p>}
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors shrink-0">
            <X size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4 min-h-0">
          {loading && (
            <div className="flex items-center justify-center h-32 text-gray-500 text-sm">
              <RefreshCw size={16} className="animate-spin mr-2" /> Loading ticket…
            </div>
          )}
          {!loading && ticket?.error && (
            <div className="text-xs text-red-400">
              Could not load this ticket — it may no longer be in the current simulated population. Refresh the dashboard and try again.
            </div>
          )}
          {!loading && ticket && !ticket.error && (
            <>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-white/[0.04] border border-white/8 rounded-lg p-3">
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Priority</p>
                  <p className={`font-bold ${prioClass(ticket.priority)}`}>{ticket.priority}</p>
                </div>
                <div className="bg-white/[0.04] border border-white/8 rounded-lg p-3">
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Status</p>
                  <p className="font-bold text-white">{ticket.status}</p>
                </div>
                <div className="bg-white/[0.04] border border-white/8 rounded-lg p-3 flex items-center gap-2">
                  <User size={12} className="text-gray-500 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider">Assignee</p>
                    <p className="font-bold text-white truncate">{ticket.assignee}</p>
                  </div>
                </div>
                <div className="bg-white/[0.04] border border-white/8 rounded-lg p-3 flex items-center gap-2">
                  <Server size={12} className="text-gray-500 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider">Service</p>
                    <p className="font-bold text-white truncate">{ticket.service}</p>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1.5">Description</p>
                <p className="text-xs text-gray-300 leading-relaxed">{ticket.description}</p>
              </div>

              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1.5">Timeline</p>
                <div className="space-y-2">
                  {ticket.timeline?.map((ev, i) => (
                    <div key={i} className="flex items-start gap-2.5 text-xs">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-gray-300">{ev.event}</p>
                        <p className="text-[10px] text-gray-500">{new Date(ev.time).toLocaleString()} · {ev.actor}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1.5">Resolution</p>
                <p className="text-xs text-gray-300 leading-relaxed">{ticket.resolution_notes}</p>
              </div>

              <div className="flex flex-wrap gap-1.5">
                {ticket.sla_breached && <span className="text-[9px] bg-red-500/15 text-red-300 border border-red-500/25 rounded px-1.5 py-0.5 font-bold">SLA BREACHED</span>}
                {ticket.reopened && <span className="text-[9px] bg-amber-500/15 text-amber-300 border border-amber-500/25 rounded px-1.5 py-0.5 font-bold">REOPENED</span>}
                {ticket.first_contact_resolved && <span className="text-[9px] bg-cyan-500/15 text-cyan-300 border border-cyan-500/25 rounded px-1.5 py-0.5 font-bold">FIRST CONTACT</span>}
                {ticket.known_error && <span className="text-[9px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/25 rounded px-1.5 py-0.5 font-bold">KNOWN ERROR</span>}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// Function: ITSMDashboardPage
export default function ITSMDashboardPage() {
  const [metrics, setMetrics]       = useState(null)
  const [services, setServices]     = useState(null)
  const [problems, setProblems]     = useState(null)
  const [backlog, setBacklog]       = useState(null)
  const [allTickets, setAllTickets] = useState([])
  const [allChanges, setAllChanges] = useState([])
  const [loading, setLoading]       = useState(false)
  const [scenario, setScenario]     = useState('normal')
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [lastRefresh, setLastRefresh] = useState(null)
  const intervalRef = useRef(null)

  // L2/L3 drill-down state
  const [drilldown, setDrilldown]       = useState(null)   // { kind, title, subtitle, items }
  const [detailTicketId, setDetailTicketId] = useState(null)
  const [detailTicket, setDetailTicket]     = useState(null)
  const [detailLoading, setDetailLoading]   = useState(false)

  const fetchAll = useCallback(async (sc = scenario) => {
    setLoading(true)
    try {
      // /dashboard/simulate regenerates the underlying ticket population — it
      // must complete first so the reads below aggregate the SAME data (and
      // stay consistent with what the KPI cards show).
      const m = await api.post('/itsm-ops/dashboard/simulate', { scenario: sc }).then(r => r.data)
      const [s, p, b, t, c] = await Promise.all([
        api.get('/itsm-ops/incidents/by-service').then(r => r.data),
        api.get('/itsm-ops/problems/recurring').then(r => r.data),
        api.get('/itsm-ops/backlog/aging').then(r => r.data),
        api.get('/itsm-ops/tickets').then(r => r.data),
        api.get('/itsm-ops/changes').then(r => r.data),
      ])
      setMetrics(m)
      setServices(s)
      setProblems(p)
      setBacklog(b)
      setAllTickets(t.tickets || [])
      setAllChanges(c.changes || [])
      setLastRefresh(new Date())
    } catch (err) {
      console.error('ITSM dashboard fetch failed', err)
    } finally {
      setLoading(false)
    }
  }, [scenario])

  // L3: fetch full ticket detail whenever a ticket id is selected
  useEffect(() => {
    if (!detailTicketId) { setDetailTicket(null); return }
    let cancelled = false
    setDetailLoading(true)
    api.get(`/itsm-ops/tickets/${detailTicketId}`)
      .then(r => { if (!cancelled) setDetailTicket(r.data) })
      .catch(err => {
        console.error('ticket detail fetch failed', err)
        if (!cancelled) setDetailTicket({ error: true })
      })
      .finally(() => { if (!cancelled) setDetailLoading(false) })
    return () => { cancelled = true }
  }, [detailTicketId])

  // Function: openTicketDrilldown
  const openTicketDrilldown = (title, subtitle, items) => setDrilldown({ kind: 'tickets', title, subtitle, items })
  // Function: openChangeDrilldown
  const openChangeDrilldown = (title, subtitle, items) => setDrilldown({ kind: 'changes', title, subtitle, items })
  // Function: openTicketDetail
  const openTicketDetail = (id) => setDetailTicketId(id)
  // Function: closeDrilldown
  const closeDrilldown = () => setDrilldown(null)
  // Function: closeDetail
  const closeDetail = () => setDetailTicketId(null)

  // Function: openKpiDrilldown
  const openKpiDrilldown = (key) => {
    const resolved = allTickets.filter(t => t.resolved)
    const openTickets = allTickets.filter(t => !t.resolved)
    if (key === 'mtta') {
      openTicketDrilldown('MTTA — Tickets by Time to Acknowledge', 'Slowest acknowledgements first',
        [...allTickets].sort((a, b) => b.mtta_hours - a.mtta_hours))
    } else if (key === 'mttr') {
      openTicketDrilldown('MTTR — Resolved Tickets by Resolution Time', 'Slowest resolutions first',
        [...resolved].sort((a, b) => b.resolve_hours - a.resolve_hours))
    } else if (key === 'sla') {
      openTicketDrilldown('SLA Compliance — Resolved Tickets', 'SLA breaches first',
        [...resolved].sort((a, b) => Number(b.sla_breached) - Number(a.sla_breached)))
    } else if (key === 'fcr') {
      openTicketDrilldown('First Contact Resolution — Resolved Tickets', 'Non first-contact resolutions first',
        [...resolved].sort((a, b) => Number(a.first_contact_resolved) - Number(b.first_contact_resolved)))
    } else if (key === 'reopen') {
      openTicketDrilldown('Reopen Rate — Resolved Tickets', 'Reopened tickets first',
        [...resolved].sort((a, b) => Number(b.reopened) - Number(a.reopened)))
    } else if (key === 'backlog') {
      openTicketDrilldown('Backlog Aging — Open Tickets', 'Oldest tickets first',
        [...openTickets].sort((a, b) => b.age_hours - a.age_hours))
    } else if (key === 'change') {
      openChangeDrilldown('Change Success Rate — Changes', 'Failed / rolled-back changes first',
        [...allChanges].sort((a, b) => (a.status === 'Success') - (b.status === 'Success')))
    } else if (key === 'total') {
      openTicketDrilldown('All Tickets', `${allTickets.length} tickets in ${metrics?.period || 'the current period'}`, allTickets)
    } else if (key === 'resolved') {
      openTicketDrilldown('Resolved Tickets', `${resolved.length} of ${allTickets.length} total`, resolved)
    }
  }

  // Function: openServiceDrilldown
  const openServiceDrilldown = (svc) => {
    openTicketDrilldown(`${svc.service} — Incidents`, `${svc.total} tickets · ${svc.resolved_pct}% resolved · avg MTTR ${svc.avg_mttr_hours}h`,
      allTickets.filter(t => t.service === svc.service))
  }

  // Function: openProblemDrilldown
  const openProblemDrilldown = (p) => {
    openTicketDrilldown(p.problem, `${p.count} occurrences · ${p.service} most affected · avg ${p.avg_resolution_hours}h resolution`,
      allTickets.filter(t => t.category === p.problem))
  }

  useEffect(() => { fetchAll(scenario) }, [])

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    if (autoRefresh) {
      intervalRef.current = setInterval(() => fetchAll(scenario), 15000)
    }
    return () => clearInterval(intervalRef.current)
  }, [autoRefresh, scenario, fetchAll])

  // Function: handleScenario
  const handleScenario = (sc) => {
    setScenario(sc)
    fetchAll(sc)
  }

  const health = metrics?.health_score ?? 0
  const maxService = services ? Math.max(...services.services.map(s => s.total)) : 1

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 text-white">

      {/* Header */}
      <div className="sticky top-0 z-10 bg-gray-950/95 backdrop-blur border-b border-white/8 px-6 py-3 flex items-center gap-3">
        <BarChart3 size={18} className="text-blue-400" />
        <div className="flex-1 min-w-0">
          <h1 className="text-xs font-black text-white">ITSM Operations Dashboard</h1>
          <p className="text-[10px] text-gray-500">
            Real-time KPIs · MTTA · MTTR · SLA · FCR · Backlog Aging · Change Success
            {lastRefresh && ` · Updated ${lastRefresh.toLocaleTimeString()}`}
          </p>
        </div>

        {/* Scenario Buttons */}
        <div className="flex items-center gap-1">
          {SCENARIOS.map(sc => (
            <button
              key={sc.id}
              onClick={() => handleScenario(sc.id)}
              className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all ${
                scenario === sc.id
                  ? `${sc.color} text-white ring-1 ${sc.ring}`
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {sc.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => setAutoRefresh(p => !p)}
          className={`px-3 py-1.5 rounded-lg text-[10px] font-semibold transition-all flex items-center gap-1.5 ${
            autoRefresh ? 'bg-emerald-600/30 text-emerald-300 ring-1 ring-emerald-500/50' : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          <Activity size={11} /> {autoRefresh ? 'Live ●' : 'Auto'}
        </button>

        <button
          onClick={() => fetchAll(scenario)}
          disabled={loading}
          className="p-2 rounded-lg bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {loading && !metrics && (
        <div className="flex items-center justify-center h-64 text-gray-500 text-sm">
          <RefreshCw size={18} className="animate-spin mr-2" /> Loading dashboard…
        </div>
      )}

      {metrics && (
        <div className="px-6 py-6 space-y-8 max-w-7xl mx-auto">

          {/* Health Score + Executive Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Health gauge */}
            <div className="bg-white/[0.04] border border-white/10 rounded-2xl p-5 flex flex-col items-center justify-center text-center">
              <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-3">Operational Health</p>
              <div className={`text-6xl font-black ${healthColor(health)}`}>{health}</div>
              <div className={`text-xs font-black mt-1 ${healthColor(health)}`}>{healthLabel(health)}</div>
              <div className="w-full mt-3 h-2 bg-white/8 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${healthBg(health)}`}
                  style={{ width: `${health}%` }}
                />
              </div>
              <div className="text-[10px] text-gray-600 mt-1">/100</div>
            </div>

            {/* Executive summary */}
            <div className="md:col-span-2 bg-white/[0.04] border border-white/10 rounded-2xl p-5">
              <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-2">
                {metrics.llm_used ? 'AI Executive Summary' : 'Operations Summary'}
              </p>
              <p className="text-sm text-gray-200 leading-relaxed mb-3">{metrics.executive_summary}</p>
              {metrics.risk_flags?.length > 0 && (
                <div className="space-y-1">
                  {metrics.risk_flags.map((f, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-amber-300">
                      <AlertTriangle size={11} className="mt-0.5 shrink-0" /> {f}
                    </div>
                  ))}
                </div>
              )}
              {metrics.quick_wins?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {metrics.quick_wins.map((w, i) => (
                    <span key={i} className="text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 rounded-lg px-2 py-0.5">
                      {w}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Primary KPIs — 9 from the spec */}
          <section>
            <SectionHeader title="Key Performance Indicators" accent="from-blue-500 to-cyan-500" />
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              <KPICard
                label="MTTA" icon={Clock}
                value={metrics.mtta_hours} unit="hrs"
                sub="Mean Time to Acknowledge"
                trend={metrics.trends?.mtta}
                color={colorClassLowerIsBetter(metrics.mtta_hours, 2, 4)}
                onClick={() => openKpiDrilldown('mtta')}
              />
              <KPICard
                label="MTTR" icon={RotateCcw}
                value={metrics.mttr_hours} unit="hrs"
                sub="Mean Time to Resolve"
                trend={metrics.trends?.mttr}
                color={colorClassLowerIsBetter(metrics.mttr_hours, 8, 24)}
                onClick={() => openKpiDrilldown('mttr')}
              />
              <KPICard
                label="SLA Compliance" icon={Shield}
                value={`${metrics.sla_compliance_pct}%`}
                sub="% resolved within SLA"
                trend={metrics.trends?.sla}
                color={colorClassHigherIsBetter(metrics.sla_compliance_pct, 85, 70)}
                onClick={() => openKpiDrilldown('sla')}
              />
              <KPICard
                label="First Contact Res." icon={CheckCircle2}
                value={`${metrics.fcr_pct}%`}
                sub="Service desk effectiveness"
                trend={metrics.trends?.fcr}
                color={colorClassHigherIsBetter(metrics.fcr_pct, 70, 50)}
                onClick={() => openKpiDrilldown('fcr')}
              />
              <KPICard
                label="Reopen Rate" icon={AlertTriangle}
                value={`${metrics.reopen_rate_pct}%`}
                sub="Poor resolution indicator"
                trend={metrics.trends?.reopen}
                color={colorClassLowerIsBetter(metrics.reopen_rate_pct, 5, 12)}
                onClick={() => openKpiDrilldown('reopen')}
              />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 mt-3">
              <KPICard
                label="Backlog Aging" icon={Clock}
                value={metrics.avg_backlog_age_hours} unit="hrs avg"
                sub={`${metrics.backlog_count} tickets in backlog`}
                color={colorClassLowerIsBetter(metrics.avg_backlog_age_hours, 24, 72)}
                onClick={() => openKpiDrilldown('backlog')}
              />
              <KPICard
                label="Change Success Rate" icon={TrendingUp}
                value={`${metrics.change_success_rate_pct}%`}
                sub={`${metrics.change_success}/${metrics.change_total} changes`}
                color={colorClassHigherIsBetter(metrics.change_success_rate_pct, 90, 75)}
                onClick={() => openKpiDrilldown('change')}
              />
              <KPICard
                label="Total Tickets" icon={BarChart3}
                value={metrics.total_tickets}
                sub={`${metrics.resolved_tickets} resolved · ${metrics.period}`}
                color="text-white"
                onClick={() => openKpiDrilldown('total')}
              />
              <KPICard
                label="Tickets Resolved" icon={CheckCircle2}
                value={`${metrics.resolved_tickets}`}
                sub={`of ${metrics.total_tickets} total (${Math.round(metrics.resolved_tickets / metrics.total_tickets * 100)}%)`}
                color="text-cyan-300"
                onClick={() => openKpiDrilldown('resolved')}
              />
            </div>
          </section>

          {/* Incident Volume by Service + Recurring Problems */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Incident volume by service */}
            <section>
              <SectionHeader title="Incident Volume by Service" accent="from-violet-500 to-purple-500" />
              <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-4 space-y-3">
                {services?.services.slice(0, 10).map(svc => (
                  <ServiceBar
                    key={svc.service} service={svc.service} total={svc.total} max={maxService}
                    onClick={() => openServiceDrilldown(svc)}
                  />
                ))}
              </div>
            </section>

            {/* Top Recurring Problems */}
            <section>
              <SectionHeader title="Top Recurring Problems" accent="from-orange-500 to-amber-500" />
              <div className="bg-white/[0.03] border border-white/8 rounded-2xl overflow-hidden">
                {problems?.problems.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => openProblemDrilldown(p)}
                    className="w-full flex items-center gap-3 px-4 py-2.5 border-b border-white/5 last:border-0 hover:bg-white/[0.03] text-left transition-colors"
                  >
                    <span className="text-xs font-black text-gray-600 w-4">{i + 1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-semibold text-white truncate">{p.problem}</p>
                      <p className="text-[10px] text-gray-500">{p.service} · avg {p.avg_resolution_hours}h</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-xs font-black text-white">{p.count}</span>
                      <span className={`text-[9px] font-semibold ${TREND_CLS[p.trend]}`}>{TREND_LABEL[p.trend]}</span>
                      {p.known_error && (
                        <span className="text-[8px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/25 rounded px-1.5 py-0.5 font-bold">KE</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </section>
          </div>

          {/* Backlog Aging */}
          {backlog && (
            <section>
              <SectionHeader title="Backlog Aging Distribution" accent="from-red-500 to-rose-500" />
              <div className="grid grid-cols-6 gap-3 mb-4">
                {Object.entries(backlog.buckets).map(([bucket, count]) => (
                  <div key={bucket} className="bg-white/[0.04] border border-white/8 rounded-xl p-3 text-center">
                    <p className="text-xs font-black text-white">{count}</p>
                    <p className="text-[10px] text-gray-500 mt-0.5">{bucket}</p>
                  </div>
                ))}
              </div>
              <div className="bg-white/[0.03] border border-white/8 rounded-2xl overflow-hidden">
                <div className="grid grid-cols-5 px-4 py-2 text-[10px] font-semibold text-gray-500 uppercase tracking-wider border-b border-white/5">
                  <span>Ticket</span><span>Summary</span><span>Priority</span><span>Age</span><span>Risk</span>
                </div>
                {backlog.tickets.slice(0, 8).map(t => (
                  <button
                    key={t.id}
                    onClick={() => openTicketDetail(t.id)}
                    className="w-full grid grid-cols-5 px-4 py-2.5 border-b border-white/5 last:border-0 text-xs text-left hover:bg-white/[0.03] transition-colors"
                  >
                    <span className="text-blue-400 font-mono">{t.id}</span>
                    <span className="text-gray-300 truncate pr-2">{t.summary}</span>
                    <span className={`font-bold ${prioClass(t.priority)}`}>
                      {t.priority}
                    </span>
                    <span className={t.age_hours > 72 ? 'text-red-400 font-semibold' : 'text-gray-300'}>{t.age_hours}h</span>
                    <span className={`font-semibold text-[10px] ${t.risk === 'Critical' ? 'text-red-400' : t.risk === 'High' ? 'text-orange-400' : t.risk === 'Medium' ? 'text-amber-400' : 'text-gray-400'}`}>
                      {t.risk}
                    </span>
                  </button>
                ))}
              </div>
            </section>
          )}

        </div>
      )}

      <DrilldownModal drilldown={drilldown} onClose={closeDrilldown} onSelectTicket={openTicketDetail} />
      <TicketDetailModal ticketId={detailTicketId} ticket={detailTicket} loading={detailLoading} onClose={closeDetail} />
    </div>
  )
}
