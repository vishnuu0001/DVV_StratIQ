// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (OmnichannelPage.jsx)
// Date: 2025-08-19
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback, useRef } from 'react'
import api from '../services/api.js'
import {
  Globe, Mail, MessageSquare, Phone, Smartphone, Activity, Code2,
  RefreshCw, Play, Zap, Plus, CheckCircle2, AlertTriangle,
  Clock, Users, BarChart3, ChevronRight, X, Layers,
} from 'lucide-react'

const CHANNEL_ICONS = { Globe, Mail, MessageSquare, Phone, Smartphone, Activity, Code2 }
const PRIORITY_COLORS = { P1: 'text-red-400 bg-red-400/10 border-red-500/25', P2: 'text-orange-400 bg-orange-400/10 border-orange-500/25', P3: 'text-yellow-400 bg-yellow-400/10 border-yellow-500/25', P4: 'text-gray-400 bg-gray-400/10 border-gray-500/25' }
const STATUS_DOT = { active: 'bg-emerald-400', degraded: 'bg-amber-400', down: 'bg-red-400' }
const CHANNEL_ACCENT = {
  blue:   'from-blue-600 to-blue-700',
  orange: 'from-orange-600 to-orange-700',
  purple: 'from-purple-600 to-purple-700',
  green:  'from-green-600 to-green-700',
  cyan:   'from-cyan-600 to-cyan-700',
  red:    'from-red-600 to-red-700',
  violet: 'from-violet-600 to-violet-700',
}
const CHANNEL_RING = {
  blue: 'ring-blue-500/40', orange: 'ring-orange-500/40', purple: 'ring-purple-500/40',
  green: 'ring-green-500/40', cyan: 'ring-cyan-500/40', red: 'ring-red-500/40', violet: 'ring-violet-500/40',
}
const CHANNEL_TEXT = {
  blue: 'text-blue-400', orange: 'text-orange-400', purple: 'text-purple-400',
  green: 'text-green-400', cyan: 'text-cyan-400', red: 'text-red-400', violet: 'text-violet-400',
}

// Function: TicketCard
function TicketCard({ ticket, onDismiss, onOpenDetail }) {
  const pCls = PRIORITY_COLORS[ticket.priority] || PRIORITY_COLORS.P4
  // Drill-down tickets (GET /tickets) carry a flat servicenow_number; freshly
  // simulated feed tickets (POST /simulate) carry a nested servicenow.number.
  // Once a ticket has a real ServiceNow number, THAT'S the id shown — it's the
  // one that's actually searchable in the Synced Incidents Dashboard. The
  // synthetic id this ticket was generated with only shows for tickets that
  // never made it into ServiceNow (skipped/failed), so there's still something
  // to reference.
  const snNumber = ticket.servicenow_number ?? ticket.servicenow?.number
  const displayId = snNumber || ticket.ticket_id
  // A real <button> wrapper broke here whenever onDismiss was ALSO passed (Feed
  // tab does both) — its own dismiss <button> nested inside made invalid HTML
  // (React warns: button cannot appear inside button) and unreliable clicks. A
  // div with role="button" is clickable/keyboard-accessible without that problem.
  return (
    <div
      role={onOpenDetail ? 'button' : undefined}
      tabIndex={onOpenDetail ? 0 : undefined}
      onClick={onOpenDetail ? () => onOpenDetail(ticket) : undefined}
      onKeyDown={onOpenDetail ? (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpenDetail(ticket) } } : undefined}
      className={`relative bg-white/[0.04] border border-white/10 rounded-xl p-3 text-xs animate-in fade-in slide-in-from-top-1 duration-200 w-full text-left ${onOpenDetail ? 'hover:border-white/25 hover:bg-white/[0.06] transition-colors cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5 min-w-0">
          <span className={`shrink-0 text-[9px] font-black px-1.5 py-0.5 rounded border ${pCls}`}>{ticket.priority}</span>
          <span className={`font-mono shrink-0 ${snNumber ? 'text-cyan-400' : 'text-gray-400'}`}>{displayId}</span>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="text-[9px] bg-white/5 border border-white/10 rounded px-1.5 py-0.5 text-gray-400">{ticket.channel_label}</span>
          {onDismiss && (
            <button onClick={(e) => { e.stopPropagation(); onDismiss(ticket.ticket_id) }} className="text-gray-600 hover:text-gray-400 transition-colors">
              <X size={10} />
            </button>
          )}
        </div>
      </div>
      <p className="text-white font-medium leading-snug mb-1 truncate">{ticket.subject}</p>
      <div className="flex items-center gap-3 text-gray-500">
        <span>→ {ticket.suggested_assignee}</span>
        <span>SLA {ticket.sla_hours}h</span>
        {ticket.confidence_score != null && <span>{Math.round(ticket.confidence_score * 100)}% conf</span>}
        {ticket.similar_ticket_count > 0 && <span>{ticket.similar_ticket_count} similar</span>}
      </div>
    </div>
  )
}

/** L2 — list of the real tickets behind a clicked stat (channel count, P1/P2 count, etc). */
// Function: DrilldownModal
function DrilldownModal({ drilldown, onClose, onOpenDetail }) {
  if (!drilldown) return null
  const { title, subtitle, tickets, loading } = drilldown
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-white/10 rounded-xl w-full max-w-2xl shadow-2xl flex flex-col max-h-[85vh]">
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10 shrink-0">
          <BarChart3 size={16} className="text-violet-400 shrink-0" />
          <div className="flex-1 min-w-0">
            <h2 className="text-sm font-bold text-white truncate">{title}</h2>
            {subtitle && <p className="text-[11px] text-gray-500 truncate">{subtitle}</p>}
          </div>
          {!loading && <span className="text-[10px] text-gray-500 shrink-0">{tickets.length} ticket{tickets.length !== 1 ? 's' : ''}</span>}
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors shrink-0">
            <X size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto min-h-0 p-3 space-y-2">
          {loading && (
            <div className="flex items-center justify-center py-12 text-gray-500 text-sm">
              <RefreshCw size={16} className="animate-spin mr-2" /> Loading tickets…
            </div>
          )}
          {!loading && tickets.length === 0 && (
            <div className="py-12 text-center text-xs text-gray-500">
              No tickets in this window yet — simulate some intake to populate it.
            </div>
          )}
          {!loading && tickets.map(t => (
            <TicketCard key={t.ticket_id} ticket={t} onOpenDetail={onOpenDetail} />
          ))}
        </div>
      </div>
    </div>
  )
}

/** L3 — full detail for a single ticket, reached from the L2 drill-down list. */
// Function: TicketDetailModal
function TicketDetailModal({ ticket, onClose }) {
  if (!ticket) return null
  const snNumber = ticket.servicenow_number ?? ticket.servicenow?.number
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-white/10 rounded-xl w-full max-w-lg shadow-2xl flex flex-col max-h-[85vh]">
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10 shrink-0">
          <div className="flex-1 min-w-0">
            <h2 className="text-sm font-bold text-cyan-400 font-mono">{snNumber || ticket.ticket_id}</h2>
            {snNumber && ticket.ticket_id !== snNumber && (
              <p className="text-[11px] text-gray-500">Simulated as: <span className="text-gray-400 font-mono">{ticket.ticket_id}</span></p>
            )}
            {!snNumber && (
              <p className="text-[11px] text-amber-500">Not created in ServiceNow{ticket.servicenow?.error ? ` — ${ticket.servicenow.error}` : ''}</p>
            )}
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors shrink-0">
            <X size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4 min-h-0">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-white/[0.04] border border-white/8 rounded-lg p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Priority</p>
              <p className={`font-bold ${(PRIORITY_COLORS[ticket.priority] || '').split(' ')[0]}`}>{ticket.priority}</p>
            </div>
            <div className="bg-white/[0.04] border border-white/8 rounded-lg p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Status</p>
              <p className="font-bold text-white">{ticket.status}</p>
            </div>
            <div className="bg-white/[0.04] border border-white/8 rounded-lg p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Channel</p>
              <p className="font-bold text-white">{ticket.channel_label}</p>
            </div>
            <div className="bg-white/[0.04] border border-white/8 rounded-lg p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">SLA</p>
              <p className="font-bold text-white">{ticket.sla_hours}h</p>
            </div>
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1.5">Subject</p>
            <p className="text-xs text-gray-300 leading-relaxed">{ticket.subject}</p>
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1.5">AI Summary</p>
            <p className="text-xs text-gray-300 leading-relaxed">{ticket.ai_summary}</p>
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1.5">Suggested Assignee</p>
            <p className="text-xs text-gray-300">{ticket.suggested_assignee}</p>
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1.5">Created</p>
            <p className="text-xs text-gray-300">{ticket.created_at ? new Date(ticket.created_at).toLocaleString() : 'Unknown'}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Function: ChannelCard
function ChannelCard({ chId, info, onSimulate, loading, onDrilldown }) {
  const Icon = CHANNEL_ICONS[info.icon] || Globe
  const accent = CHANNEL_ACCENT[info.color] || CHANNEL_ACCENT.blue
  const ring   = CHANNEL_RING[info.color]   || CHANNEL_RING.blue
  const tColor = CHANNEL_TEXT[info.color]   || 'text-blue-400'
  const dot    = STATUS_DOT[info.status]    || STATUS_DOT.degraded

  return (
    <div className={`bg-white/[0.03] border border-white/10 rounded-2xl p-4 flex flex-col gap-3 hover:border-white/20 transition-all ${loading ? 'opacity-60' : ''}`}>
      {/* Icon + header */}
      <div className="flex items-start justify-between">
        <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${accent} flex items-center justify-center shrink-0`}>
          <Icon size={17} className="text-white" />
        </div>
        <div className="flex items-center gap-1">
          <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
          <span className="text-[9px] text-gray-500 capitalize">{info.status}</span>
        </div>
      </div>

      <div>
        <p className="text-sm font-bold text-white">{info.label}</p>
        <p className="text-[10px] text-gray-400 leading-relaxed mt-0.5">{info.description}</p>
        <p className="text-[10px] text-gray-600 italic mt-1">{info.example}</p>
      </div>

      {/* Stats row — last hour / today are drillable to the real tickets behind them */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <button
          onClick={() => onDrilldown(chId, info.label, 1, 'last hour')}
          disabled={!info.tickets_last_hour}
          className="rounded-lg py-0.5 hover:bg-white/5 transition-colors disabled:hover:bg-transparent"
        >
          <p className={`text-base font-black ${tColor}`}>{info.tickets_last_hour ?? '—'}</p>
          <p className="text-[9px] text-gray-600">last hour</p>
        </button>
        <button
          onClick={() => onDrilldown(chId, info.label, 24, 'today')}
          disabled={!info.tickets_today}
          className="rounded-lg py-0.5 hover:bg-white/5 transition-colors disabled:hover:bg-transparent"
        >
          <p className={`text-base font-black ${tColor}`}>{info.tickets_today ?? '—'}</p>
          <p className="text-[9px] text-gray-600">today</p>
        </button>
        <div>
          <p className={`text-base font-black ${tColor}`}>{info.avg_response_secs ?? '—'}s</p>
          <p className="text-[9px] text-gray-600">avg resp</p>
        </div>
      </div>

      {/* Simulate button */}
      <button
        onClick={() => onSimulate(chId)}
        disabled={loading}
        className={`w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all ring-1 ${ring} text-white bg-gradient-to-r ${accent} hover:opacity-90 disabled:opacity-40`}
      >
        {loading ? <RefreshCw size={10} className="animate-spin" /> : <Play size={10} />}
        Simulate Intake
      </button>
    </div>
  )
}

// Function: OmnichannelPage
export default function OmnichannelPage() {
  const [channelStatus, setChannelStatus] = useState(null)
  const [queue, setQueue]                 = useState([])
  const [feed, setFeed]                   = useState([])
  const [stats, setStats]                 = useState(null)
  const [loadingCh, setLoadingCh]         = useState({})
  const [burstLoading, setBurstLoading]   = useState(false)
  const [triageSummary, setTriageSummary] = useState(null)
  const [activeTab, setActiveTab]         = useState('channels')
  const [drilldown, setDrilldown]         = useState(null)   // L2: { title, subtitle, tickets, loading }
  const [selectedTicket, setSelectedTicket] = useState(null) // L3
  const feedRef = useRef(null)

  // Function: openDrilldown
  const openDrilldown = async (channel, title, hours, periodLabel) => {
    setDrilldown({ title, subtitle: `${periodLabel} · real tickets created via Omnichannel Intake`, tickets: [], loading: true })
    try {
      const params = { hours }
      if (channel && channel !== 'all') params.channel = channel
      const { data } = await api.get('/omnichannel/tickets', { params })
      setDrilldown({ title, subtitle: `${periodLabel} · ${data.total} ticket${data.total !== 1 ? 's' : ''}`, tickets: data.tickets || [], loading: false })
    } catch (err) {
      console.error('Drilldown fetch failed', err)
      setDrilldown({ title, subtitle: 'Failed to load tickets', tickets: [], loading: false })
    }
  }
  // Function: closeDrilldown
  const closeDrilldown = () => setDrilldown(null)
  // Function: closeTicketDetail
  const closeTicketDetail = () => setSelectedTicket(null)

  const loadStatus = useCallback(async () => {
    try {
      const [cs, q, st] = await Promise.all([
        api.get('/omnichannel/channels/status').then(r => r.data),
        api.get('/omnichannel/queue').then(r => r.data),
        api.get('/omnichannel/stats/summary').then(r => r.data),
      ])
      setChannelStatus(cs)
      setQueue(q.queue || [])
      setStats(st)
    } catch (err) {
      console.error('Omnichannel load failed', err)
    }
  }, [])

  useEffect(() => {
    loadStatus()
    // Real tickets now arrive continuously from the Email channel's IMAP poller
    // (backend/services/email_intake.py, 60s cycle) with no user action to react
    // to — without polling here, this page only ever reflected whatever was true
    // at the moment it happened to be loaded.
    const interval = setInterval(loadStatus, 60_000)
    return () => clearInterval(interval)
  }, [loadStatus])

  // Function: simulateChannel
  const simulateChannel = async (chId) => {
    setLoadingCh(p => ({ ...p, [chId]: true }))
    try {
      const { data } = await api.post('/omnichannel/simulate', { channel: chId, count: 3 })
      const newTickets = data.tickets || []
      setFeed(prev => [...newTickets, ...prev].slice(0, 50))
      if (data.llm_triage) setTriageSummary(data.llm_triage)
      setActiveTab('feed')
      setTimeout(() => feedRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100)
      // The backend has already persisted successfully-created tickets to local
      // storage by the time this response comes back — refresh Queue/Channel
      // Overview/24h Stats now instead of leaving them stale until the user
      // happens to click "Refresh" or switches tabs and back.
      await loadStatus()
    } catch (err) {
      console.error('Simulate channel failed', err)
    } finally {
      setLoadingCh(p => ({ ...p, [chId]: false }))
    }
  }

  // Function: simulateBurst
  const simulateBurst = async () => {
    setBurstLoading(true)
    try {
      const { data } = await api.post('/omnichannel/simulate', { channel: 'all', count: 10 })
      const newTickets = data.tickets || []
      setFeed(prev => [...newTickets, ...prev].slice(0, 50))
      if (data.llm_triage) setTriageSummary(data.llm_triage)
      setActiveTab('feed')
      await loadStatus()
    } catch (err) {
      console.error('Burst simulate failed', err)
    } finally {
      setBurstLoading(false)
    }
  }

  // Function: dismissFeedItem
  const dismissFeedItem = (id) => setFeed(prev => prev.filter(t => t.ticket_id !== id))
  // Function: clearFeed
  const clearFeed = () => { setFeed([]); setTriageSummary(null) }

  const channels = channelStatus?.channels || {}

  const TABS = [
    { id: 'channels', label: 'Channel Overview' },
    { id: 'feed',     label: `Incoming Feed${feed.length ? ` (${feed.length})` : ''}` },
    { id: 'queue',    label: `Open Queue${queue.length ? ` (${queue.length})` : ''}` },
    { id: 'stats',    label: '24h Stats' },
  ]

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 text-white">

      {/* Header */}
      <div className="sticky top-0 z-10 bg-gray-950/95 backdrop-blur border-b border-white/8 px-6 py-3 flex items-center gap-3">
        <Layers size={18} className="text-violet-400" />
        <div className="flex-1 min-w-0">
          <h1 className="text-xs font-black text-white">Omnichannel Ticket Intake</h1>
          <p className="text-[10px] text-gray-500">Web Portal · Email · Chat · Phone · Mobile · Monitoring · API</p>
        </div>
        <button
          onClick={simulateBurst}
          disabled={burstLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 text-white text-[10px] font-black uppercase tracking-wider hover:opacity-90 transition-all disabled:opacity-50"
        >
          {burstLoading ? <RefreshCw size={11} className="animate-spin" /> : <Zap size={11} />}
          Simulate Burst (All)
        </button>
        <button onClick={loadStatus} className="p-2 rounded-lg bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white transition-colors">
          <RefreshCw size={14} />
        </button>
      </div>

      {/* Tabs */}
      <div className="px-6 pt-4 flex gap-1 border-b border-white/8 pb-0">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-colors border-b-2 -mb-px ${
              activeTab === t.id
                ? 'text-white border-violet-500 bg-white/5'
                : 'text-gray-500 border-transparent hover:text-gray-300'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="px-6 py-6 max-w-7xl mx-auto">

        {/* ── Channel Overview ─────────────────────────────────── */}
        {activeTab === 'channels' && (
          <div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {Object.entries(channels).map(([chId, info]) => (
                <ChannelCard
                  key={chId}
                  chId={chId}
                  info={info}
                  onSimulate={simulateChannel}
                  loading={!!loadingCh[chId]}
                  onDrilldown={openDrilldown}
                />
              ))}
              {Object.keys(channels).length === 0 && (
                <div className="col-span-4 flex flex-col items-center justify-center py-16 text-gray-600">
                  <Layers size={32} strokeWidth={1} className="mb-2" />
                  <p className="text-sm">Loading channel status…</p>
                </div>
              )}
            </div>

            {/* How it works */}
            <div className="mt-8 bg-white/[0.02] border border-white/8 rounded-2xl p-5">
              <p className="text-[10px] font-black uppercase tracking-widest text-violet-400 mb-3">How Omnichannel Intake Works</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-gray-400">
                <div>
                  <p className="text-white font-semibold mb-1">1. Multi-channel ingestion</p>
                  <p>Tickets arrive via 7 channels. Each channel has its own adapter normalizing payloads into a unified ticket schema with auto-detected priority weights.</p>
                </div>
                <div>
                  <p className="text-white font-semibold mb-1">2. AI classification</p>
                  <p>Every ticket is instantly classified for category, sub-category, priority, and suggested assignee using the local Ollama LLM with 92%+ accuracy.</p>
                </div>
                <div>
                  <p className="text-white font-semibold mb-1">3. Intelligent routing</p>
                  <p>P1/P2 tickets page on-call immediately. P3/P4 enter the L1 queue. Similar tickets are linked automatically. SLA clock starts on intake.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Incoming Feed ────────────────────────────────────── */}
        {activeTab === 'feed' && (
          <div ref={feedRef}>
            {triageSummary && (
              <div className="mb-5 bg-violet-500/10 border border-violet-500/25 rounded-2xl p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-violet-400 mb-2">AI Triage Summary</p>
                <p className="text-sm text-gray-200 mb-2">{triageSummary.triage_summary}</p>
                {triageSummary.urgent_tickets?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {triageSummary.urgent_tickets.map(id => (
                      <span key={id} className="text-[10px] bg-red-500/10 border border-red-500/25 text-red-300 rounded px-2 py-0.5 font-mono">{id}</span>
                    ))}
                  </div>
                )}
                {triageSummary.suggested_routing && (
                  <p className="text-[10px] text-gray-400 mt-2 border-t border-white/8 pt-2">
                    Routing: {triageSummary.suggested_routing}
                  </p>
                )}
              </div>
            )}

            <div className="flex items-center justify-between mb-4">
              <p className="text-xs text-gray-500">{feed.length} tickets in feed</p>
              <div className="flex gap-2">
                <button
                  onClick={simulateBurst}
                  disabled={burstLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-violet-600/20 text-violet-300 text-[10px] font-semibold hover:bg-violet-600/30 transition-colors disabled:opacity-50"
                >
                  {burstLoading ? <RefreshCw size={10} className="animate-spin" /> : <Zap size={10} />} Simulate More
                </button>
                {feed.length > 0 && (
                  <button onClick={clearFeed} className="px-3 py-1.5 rounded-lg bg-white/5 text-gray-400 text-[10px] hover:bg-white/10 transition-colors">
                    Clear
                  </button>
                )}
              </div>
            </div>

            {feed.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-gray-600">
                <Play size={32} strokeWidth={1} className="mb-3" />
                <p className="text-sm font-semibold">No tickets yet</p>
                <p className="text-xs mt-1">Click a channel's "Simulate Intake" or use "Simulate Burst (All)"</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {feed.map(t => (
                  <TicketCard key={t.ticket_id + t.created_at} ticket={t} onDismiss={dismissFeedItem} onOpenDetail={setSelectedTicket} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Open Queue ───────────────────────────────────────── */}
        {activeTab === 'queue' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs text-gray-500">{queue.length} tickets open · sorted by priority</p>
              <button onClick={loadStatus} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 text-gray-400 text-[10px] hover:bg-white/10 transition-colors">
                <RefreshCw size={10} /> Refresh Queue
              </button>
            </div>
            {queue.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-gray-600">
                <CheckCircle2 size={32} strokeWidth={1} className="mb-2" />
                <p className="text-sm">Queue empty</p>
              </div>
            ) : (
              <div className="bg-white/[0.03] border border-white/8 rounded-2xl overflow-hidden">
                <div className="grid grid-cols-6 px-4 py-2.5 text-[10px] font-semibold text-gray-500 uppercase tracking-wider border-b border-white/8">
                  <span>ID</span><span className="col-span-2">Subject</span><span>Priority</span><span>Channel</span><span>SLA</span>
                </div>
                {queue.map(t => (
                  <button
                    key={t.ticket_id}
                    onClick={() => setSelectedTicket(t)}
                    className="w-full grid grid-cols-6 px-4 py-2.5 border-b border-white/5 last:border-0 text-xs hover:bg-white/[0.03] items-center text-left"
                  >
                    <span className="text-blue-400 font-mono">{t.ticket_id}</span>
                    <span className="col-span-2 text-gray-300 truncate pr-2">{t.subject}</span>
                    <span className={`font-black ${t.priority === 'P1' ? 'text-red-400' : t.priority === 'P2' ? 'text-orange-400' : t.priority === 'P3' ? 'text-yellow-400' : 'text-gray-500'}`}>
                      {t.priority}
                    </span>
                    <span className="text-gray-400">{t.channel_label}</span>
                    <span className="text-gray-400">{t.sla_hours}h</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── 24h Stats ───────────────────────────────────────── */}
        {activeTab === 'stats' && stats && (
          <div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {Object.entries(stats.stats).map(([chId, s]) => {
                const Icon = CHANNEL_ICONS[channels[chId]?.icon] || Globe
                const accent = CHANNEL_ACCENT[s.color] || CHANNEL_ACCENT.blue
                const tColor = CHANNEL_TEXT[s.color] || 'text-blue-400'
                return (
                  <div key={chId} className="bg-white/[0.03] border border-white/10 rounded-2xl p-4 space-y-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-8 h-8 rounded-xl bg-gradient-to-br ${accent} flex items-center justify-center`}>
                        <Icon size={14} className="text-white" />
                      </div>
                      <p className="text-sm font-bold text-white">{s.label}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-center">
                      <button
                        onClick={() => openDrilldown(chId, s.label, 24, 'last 24h')}
                        disabled={!s.total_24h}
                        className="bg-white/5 rounded-xl py-2 hover:bg-white/10 transition-colors disabled:hover:bg-white/5"
                      >
                        <p className={`text-xl font-black ${tColor}`}>{s.total_24h}</p>
                        <p className="text-[9px] text-gray-600">total tickets</p>
                      </button>
                      <div className="bg-white/5 rounded-xl py-2">
                        <p className={`text-xl font-black ${tColor}`}>{s.auto_classified}</p>
                        <p className="text-[9px] text-gray-600">auto-classified</p>
                      </div>
                    </div>
                    <div className="flex justify-between text-[10px] text-gray-500">
                      <span>P1: <span className="text-red-400 font-bold">{s.p1_count}</span></span>
                      <span>P2: <span className="text-orange-400 font-bold">{s.p2_count}</span></span>
                      <span>CSAT: <span className="text-emerald-400 font-bold">{s.satisfaction_score ?? '—'}</span>{s.satisfaction_score != null ? '/5' : ''}</span>
                    </div>
                    <div className="text-[10px] text-gray-600">Avg response: {s.avg_response_secs}s</div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

      </div>

      <DrilldownModal
        drilldown={drilldown}
        onClose={closeDrilldown}
        onOpenDetail={setSelectedTicket}
      />
      <TicketDetailModal ticket={selectedTicket} onClose={closeTicketDetail} />
    </div>
  )
}
