// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (AutomationMining.jsx)
// Date: 2026-01-29
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Cpu,
  Target,
  Clock,
  RefreshCw,
  BarChart2,
  Zap,
  Trophy,
  Brain,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import KPICard from '../components/KPICard'
import ChartImage from '../components/ChartImage'
import DrilldownDrawer from '../components/DrilldownDrawer'
import ExportPDFButton from '../components/ExportPDFButton'
import { getAutomationCandidates } from '../api'
import { useDashboard } from '../context/DashboardContext'

const PRIORITY_CONFIG = {
  High: { bg: 'bg-rose-900/40', text: 'text-rose-300', border: 'border-rose-700/60' },
  Medium: { bg: 'bg-amber-900/40', text: 'text-amber-300', border: 'border-amber-700/60' },
  Low: { bg: 'bg-emerald-900/40', text: 'text-emerald-300', border: 'border-emerald-700/60' },
  Monitor: { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-300' },
}

const CHART_COLORS = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#67e8f9', '#86efac', '#fcd34d', '#fca5a5']

// Function: CustomTooltipDark
const CustomTooltipDark = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800/90 border border-slate-700 backdrop-blur rounded-lg px-3 py-2 text-xs max-w-xs shadow-xl">
        <p className="text-slate-200 font-medium mb-1 truncate">{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color }}>
            {p.name}: <span className="font-bold text-white">{typeof p.value === 'number' ? p.value.toLocaleString() : p.value}</span>
          </p>
        ))}
      </div>
    )
  }
  return null
}

// Function: PriorityBadge
function PriorityBadge({ priority }) {
  const cfg = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG.Monitor
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${cfg.bg} ${cfg.text} ${cfg.border}`}>
      {priority}
    </span>
  )
}

// Function: SummaryCard
function SummaryCard({ title, value, subtitle, icon: Icon, color = 'cyan', loading, onClick }) {
  const colorMap = {
    cyan: 'text-accent-cyan border-cyan-500/20 bg-cyan-500/10',
    indigo: 'text-accent-indigo border-indigo-500/20 bg-indigo-500/10',
    emerald: 'text-accent-emerald border-emerald-500/20 bg-emerald-500/10',
    amber: 'text-accent-amber border-amber-500/20 bg-amber-500/10',
    rose: 'text-accent-rose border-rose-500/20 bg-rose-500/10',
  }
  const valueColor = {
    cyan: 'text-cyan-300',
    indigo: 'text-indigo-300',
    emerald: 'text-emerald-300',
    amber: 'text-amber-300',
    rose: 'text-rose-300',
  }
  const border = {
    cyan: 'border-t-cyan-400',
    indigo: 'border-t-indigo-400',
    emerald: 'border-t-emerald-400',
    amber: 'border-t-amber-400',
    rose: 'border-t-rose-400',
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-5 border-t-2 border-t-slate-300">
        <div className="skeleton h-8 w-8 rounded-lg mb-3" />
        <div className="skeleton h-8 w-20 rounded mb-2" />
        <div className="skeleton h-4 w-28 rounded mb-1" />
        <div className="skeleton h-3 w-24 rounded" />
      </div>
    )
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left rounded-xl border border-slate-200 bg-white p-5 border-t-2 ${border[color]} bg-gradient-to-br from-white to-slate-50 hover:-translate-y-0.5 transition-all ${onClick ? 'cursor-pointer' : ''}`}
    >
      {Icon && (
        <div className={`inline-flex p-2 rounded-lg border mb-3 ${colorMap[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      )}
      <p className={`text-3xl font-bold ${valueColor[color]}`}>{value ?? '—'}</p>
      <p className="text-sm font-semibold text-slate-700 mt-1">{title}</p>
      {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
    </button>
  )
}

// Function: SummaryCardsRow
function SummaryCardsRow({ loading, totalCandidates, highPriority, totalHoursSaved, avgOpportunityScore, openDrawer }) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <SummaryCard
        title="Total Candidates"
        value={loading ? null : totalCandidates.toLocaleString()}
        subtitle="AI-identified patterns"
        icon={Cpu}
        color="cyan"
        loading={loading}
        onClick={() => openDrawer('automation-opportunities', 'Total Candidates — L2 / L3')}
      />
      <SummaryCard
        title="High Priority"
        value={loading ? null : highPriority.toLocaleString()}
        subtitle="LLM-predicted high potential"
        icon={Target}
        color="rose"
        loading={loading}
        onClick={() => openDrawer('automation-opportunities', 'High Priority — L2 / L3')}
      />
      <SummaryCard
        title="Est. Hours Saved/Month"
        value={loading ? null : totalHoursSaved > 0 ? `${Math.round(totalHoursSaved).toLocaleString()}h` : '—'}
        subtitle="Potential monthly savings"
        icon={Clock}
        color="emerald"
        loading={loading}
        onClick={() => openDrawer('automation-opportunities', 'Hours Saved — L2 / L3')}
      />
      <SummaryCard
        title="Avg Opportunity"
        value={loading ? null : `${avgOpportunityScore.toFixed(1)}`}
        subtitle="LLM automation score /100"
        icon={Brain}
        color="amber"
        loading={loading}
        onClick={() => openDrawer('automation-opportunities', 'LLM Opportunity Score — L2 / L3')}
      />
    </div>
  )
}

// Function: CandidateRow
function CandidateRow({ c, index }) {
  return (
    <tr>
      <td className="text-slate-500 tabular-nums w-8">{index + 1}</td>
      <td className="font-medium text-slate-700">{c.category || '—'}</td>
      <td className="text-slate-700">{c.work_type || '—'}</td>
      <td className="text-right tabular-nums font-medium">{c.volume != null ? Number(c.volume).toLocaleString() : '—'}</td>
      <td className="text-right tabular-nums">
        {c.repetition_score != null ? (
          <span className={Number(c.repetition_score) >= 0.7 ? 'text-accent-emerald font-medium' : 'text-slate-600'}>
            {Number(c.repetition_score).toFixed(2)}
          </span>
        ) : '—'}
      </td>
      <td className="text-right tabular-nums text-slate-600">
        {c.avg_cycle_time != null ? `${Number(c.avg_cycle_time).toFixed(1)}h` : '—'}
      </td>
      <td className="text-right tabular-nums font-semibold text-cyan-300">
        {c.llm_opportunity_score != null ? Number(c.llm_opportunity_score).toFixed(1) : '—'}
      </td>
      <td className="text-right tabular-nums text-slate-600">
        {c.llm_confidence != null ? `${Number(c.llm_confidence).toFixed(0)}%` : '—'}
      </td>
      <td className="text-slate-700">{c.llm_automation_type || '—'}</td>
      <td>
        <PriorityBadge priority={c.priority || 'Monitor'} />
      </td>
      <td className="text-right tabular-nums">
        {c.est_hours_saved != null ? (
          <span className="text-accent-emerald font-medium">
            {Number(c.est_hours_saved).toFixed(0)}h
          </span>
        ) : '—'}
      </td>
      <td className="text-slate-600 max-w-[280px] truncate" title={c.llm_rationale || ''}>
        {c.llm_rationale || '—'}
      </td>
      <td className="text-slate-600 max-w-[240px] truncate" title={c.llm_next_step || ''}>
        {c.llm_next_step || '—'}
      </td>
    </tr>
  )
}

// Function: CandidatesTableBody
function CandidatesTableBody({ loading, sorted }) {
  if (loading) {
    return [...Array(8)].map((_, i) => (
      <tr key={i}>
        {[...Array(13)].map((__, j) => (
          <td key={j}><div className="skeleton h-4 rounded w-full" /></td>
        ))}
      </tr>
    ))
  }
  if (sorted.length === 0) {
    return (
      <tr>
        <td colSpan={13} className="text-center text-slate-500 py-10">No automation candidates found</td>
      </tr>
    )
  }
  return sorted.map((c, i) => <CandidateRow key={i} c={c} index={i} />)
}

// Function: CandidatesTable
function CandidatesTable({ loading, sorted }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden mb-6">
      <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-accent-cyan" />
          <span className="text-sm font-medium text-slate-700">Automation Candidates</span>
          <span className="text-xs text-slate-500">({sorted.length} total, sorted by score)</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Category</th>
              <th>Work Type</th>
              <th className="text-right">Volume</th>
              <th className="text-right">Repetition</th>
              <th className="text-right">Avg Cycle Time</th>
              <th className="text-right">LLM Opp.Score</th>
              <th className="text-right">Confidence</th>
              <th>Automation Type</th>
              <th>Priority</th>
              <th className="text-right">Est. Hours Saved</th>
              <th>Rationale</th>
              <th>Next Step</th>
            </tr>
          </thead>
          <tbody>
            <CandidatesTableBody loading={loading} sorted={sorted} />
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Function: RankedBarChartPanel
function RankedBarChartPanel({ icon: Icon, iconColor, title, loading, data, dataKey, name }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-2 mb-4">
        <Icon className={`w-4 h-4 ${iconColor}`} />
        <span className="text-lg font-semibold text-slate-700 uppercase tracking-wider">{title}</span>
      </div>
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data.length === 0 ? (
        <p className="text-slate-500 text-sm text-center py-12">No data</p>
      ) : (
        <ResponsiveContainer width="100%" height={380}>
          <BarChart data={data} layout="vertical" margin={{ left: 4, right: 20, top: 4, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
            <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis
              dataKey="name"
              type="category"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={130}
            />
            <Tooltip content={<CustomTooltipDark />} />
            <Bar dataKey={dataKey} name={name} radius={[0, 4, 4, 0]}>
              {data.map((_, idx) => (
                <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

// Function: AutomationMining
export default function AutomationMining() {
  const { dateRange } = useDashboard()
  const printRef = useRef(null)
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [enriching, setEnriching] = useState(false)
  const [loadError, setLoadError] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)
  const [refreshing, setRefreshing] = useState(false)
  const [drawer, setDrawer] = useState({ open: false, chartType: null, title: '' })

  // Function: openDrawer
  function openDrawer(chartType, title) { setDrawer({ open: true, chartType, title }) }
  // Function: closeDrawer
  function closeDrawer() { setDrawer((d) => ({ ...d, open: false })) }

  const fetchData = useCallback(async (isRefresh = false) => {
    if (!isRefresh) setLoading(true)
    setLoadError('')
    setEnriching(false)

    // Phase 1 — instant heuristic results
    let phase1Data = []
    try {
      const res = await getAutomationCandidates(20, { deepAnalysis: false }, dateRange)
      phase1Data = Array.isArray(res.data) ? res.data : res.data?.candidates || []
      setCandidates(phase1Data)
    } catch (e) {
      console.error('Failed to load automation candidates', e)
      setCandidates([])
      setLoadError('Failed to load automation candidates. Please check backend connectivity.')
      setLoading(false)
      return
    } finally {
      setLoading(false)
    }

    // Phase 2 — LLM enrichment (best-effort, does not block Phase 1 display)
    // Skipped when date-filtered (backend bypasses LLM cache in that mode)
    if (phase1Data.length > 0) {
      setEnriching(true)
      try {
        const enrichedRes = await getAutomationCandidates(20, {
          deepAnalysis: true,
          useOllama: true,
        }, dateRange)
        const enrichedData = Array.isArray(enrichedRes.data)
          ? enrichedRes.data
          : enrichedRes.data?.candidates || []
        if (enrichedData.length > 0) setCandidates(enrichedData)
      } catch (enrichErr) {
        console.warn('LLM enrichment unavailable, keeping heuristic results', enrichErr)
      } finally {
        setEnriching(false)
      }
    }
  }, [dateRange])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Function: handleRefresh
  async function handleRefresh() {
    setRefreshing(true)
    await fetchData(true)
    setRefreshKey((k) => k + 1)
    setRefreshing(false)
  }

  // Compute summary stats
  const totalCandidates = candidates.length
  const highPriority = candidates.filter(
    (c) => c.priority === 'High' || Number(c.llm_opportunity_score || 0) >= 75
  ).length
  const totalHoursSaved = candidates.reduce((acc, c) => acc + (Number(c.est_hours_saved) || 0), 0)
  const avgOpportunityScore = candidates.length
    ? candidates.reduce((acc, c) => acc + Number(c.llm_opportunity_score || 0), 0) / candidates.length
    : 0

  // Top category by volume
  const catCounts = {}
  candidates.forEach((c) => {
    const cat = c.category || 'Other'
    catCounts[cat] = (catCounts[cat] || 0) + (Number(c.volume) || 1)
  })
  const topCategory = Object.entries(catCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '—'

  // Sorted candidates
  const sorted = [...candidates].sort(
    (a, b) => (Number(b.llm_opportunity_score) || Number(b.total_score) || 0)
      - (Number(a.llm_opportunity_score) || Number(a.total_score) || 0)
  )

  // Top 10 by volume
  const topByVolume = [...candidates]
    .sort((a, b) => (Number(b.volume) || 0) - (Number(a.volume) || 0))
    .slice(0, 10)
    .map((c) => ({ name: c.work_type || c.category || 'Unknown', volume: Number(c.volume) || 0 }))

  // Top 10 by hours saved
  const topByHours = [...candidates]
    .sort((a, b) => (Number(b.est_hours_saved) || 0) - (Number(a.est_hours_saved) || 0))
    .slice(0, 10)
    .map((c) => ({ name: c.work_type || c.category || 'Unknown', hours: Number(c.est_hours_saved) || 0 }))

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
      <div className="flex items-start justify-between mb-2">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-lg gradient-bg-primary shadow-glow-md">
              <Cpu className="w-7 h-7 text-white" />
            </div>
            Automation Opportunity Mining
          </h1>
          <p className="text-slate-400 text-sm mt-3">
            AI-identified repetitive, high-volume, low-complexity work patterns that are prime automation candidates.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ExportPDFButton printRef={printRef} title="Automation Mining" />
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700/30 hover:bg-slate-700/50 border border-slate-600/30 text-slate-200 text-xs rounded-lg transition-all hover:shadow-elevation-1 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="mb-4 p-3 rounded-lg glass border-indigo-500/30">
        <p className="text-xs text-indigo-300 flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5" />
          Two-phase analysis: heuristic results load instantly, then Ollama LLM enrichment updates scores in the background.
        </p>
      </div>

      {enriching && (
        <div className="mb-4 p-3 rounded-lg border border-cyan-500/30 bg-cyan-500/10 flex items-center gap-2">
          <div className="w-3.5 h-3.5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin flex-shrink-0" />
          <p className="text-xs text-cyan-200">AI analysis in progress — scores will update when complete…</p>
        </div>
      )}

      {loadError && (
        <div className="mb-6 p-3 rounded-lg border border-rose-500/30 bg-rose-500/10">
          <p className="text-xs text-rose-200">{loadError}</p>
        </div>
      )}

      <SummaryCardsRow
        loading={loading}
        totalCandidates={totalCandidates}
        highPriority={highPriority}
        totalHoursSaved={totalHoursSaved}
        avgOpportunityScore={avgOpportunityScore}
        openDrawer={openDrawer}
      />

      {/* Row 2 — Matplotlib chart — INCREASED height */}
      <div className="mb-6">
        <ChartImage
          endpoint="automation-opportunities"
          title="Automation Opportunity Analysis"
          height={600}
          refreshKey={refreshKey}
          onDrilldown={() => openDrawer('automation-opportunities', 'Automation Opportunity Analysis')}
        />
      </div>

      <CandidatesTable loading={loading} sorted={sorted} />

      {/* Row 4 — Two charts — INCREASED heights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <RankedBarChartPanel
          icon={BarChart2}
          iconColor="text-accent-cyan"
          title="Top 10 by Volume"
          loading={loading}
          data={topByVolume}
          dataKey="volume"
          name="Volume"
        />
        <RankedBarChartPanel
          icon={BarChart2}
          iconColor="text-accent-emerald"
          title="Top 10 by Hours Saved"
          loading={loading}
          data={topByHours}
          dataKey="hours"
          name="Hours Saved"
        />
      </div>

      {/* Drilldown drawer */}
      <DrilldownDrawer
        open={drawer.open}
        onClose={closeDrawer}
        title={drawer.title}
        chartType={drawer.chartType}
        data={candidates}
      />
    </div>
  )
}
