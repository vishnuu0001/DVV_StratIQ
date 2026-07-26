// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (ChangeRisk.jsx)
// Date: 2026-03-04
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  GitBranch,
  Zap,
  TrendingDown,
  CheckCircle,
  Clock,
  RefreshCw,
  BarChart2,
  AlertTriangle,
  Shield,
} from 'lucide-react'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import KPICard from '../components/KPICard'
import ChartImage from '../components/ChartImage'
import InsightPanel from '../components/InsightPanel'
import DrilldownDrawer from '../components/DrilldownDrawer'
import ExportPDFButton from '../components/ExportPDFButton'
import { getChanges, getInsights } from '../api'
import { useDashboard } from '../context/DashboardContext'

const TYPE_COLORS = {
  Normal: '#38bdf8',
  Standard: '#818cf8',
  Emergency: '#f87171',
}
const TYPE_FALLBACK = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa']

// Function: CustomTooltipDark
const CustomTooltipDark = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800/90 border border-slate-700 backdrop-blur rounded-lg px-3 py-2 text-xs shadow-xl">
        <p className="text-slate-200 font-medium mb-1">{label}</p>
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

// Function: CustomPieLabel
const CustomPieLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  const RADIAN = Math.PI / 180
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  if (percent < 0.05) return null
  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={12} fontWeight={600}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

// Function: emergencyPctValue
function emergencyPctValue(d) {
  if (d.risk?.emergency_pct != null) return `${Number(d.risk.emergency_pct).toFixed(1)}%`
  if (d.summary?.emergency_pct != null) return `${Number(d.summary.emergency_pct).toFixed(1)}%`
  return '—'
}

// Function: successRateValue
function successRateValue(d) {
  const pct = d.risk?.implementation_success_pct ?? d.summary?.implementation_success_pct
  return pct != null ? `${Number(pct).toFixed(1)}%` : '—'
}

// Function: ChangeKPIRow
function ChangeKPIRow({ loading, total, byType, d, openDrawer }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      <KPICard
        title="Total Changes"
        value={loading ? null : total > 0 ? total.toLocaleString() : '—'}
        subtitle="All change records"
        icon={GitBranch}
        color="indigo"
        loading={loading}
        onClick={() => openDrawer('change-risk', 'Total Changes — L2 / L3')}
      />
      <KPICard
        title="Emergency Changes"
        value={loading ? null : byType.Emergency != null ? Number(byType.Emergency).toLocaleString() : '—'}
        subtitle="Emergency changes"
        icon={Zap}
        color="rose"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('change-risk', 'Emergency Changes — L2 / L3')}
      />
      <KPICard
        title="Emergency %"
        value={loading ? null : emergencyPctValue(d)}
        subtitle="% of total changes"
        icon={TrendingDown}
        color="amber"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('change-risk', 'Emergency % — L2 / L3')}
      />
      <KPICard
        title="Success Rate"
        value={loading ? null : successRateValue(d)}
        subtitle="Changes implemented OK"
        icon={CheckCircle}
        color="emerald"
        loading={loading}
        onClick={() => openDrawer('change-risk', 'Success Rate — L2 / L3')}
      />
      <KPICard
        title="Avg Duration"
        value={loading ? null : d.cycle_time?.avg != null ? `${Number(d.cycle_time.avg).toFixed(1)}h` : '—'}
        subtitle="Mean change duration"
        icon={Clock}
        color="cyan"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('change-risk', 'Avg Duration — L2 / L3')}
      />
    </div>
  )
}

// Function: TypeDrilldownTable
function TypeDrilldownTable({ typeDrilldown, onClose }) {
  return (
    <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-accent-cyan">L2: {typeDrilldown.title}</span>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-900 text-lg leading-none">×</button>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table text-xs w-full">
          <thead>
            <tr>
              {typeDrilldown.columns.map((col, i) => (
                <th key={i} className="text-left px-2 py-1 text-slate-600 font-semibold">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {typeDrilldown.rows.map((row, i) => (
              <tr key={i} className="border-t border-slate-200">
                <td className="px-2 py-1 text-slate-700">{row.month}</td>
                <td className="px-2 py-1 tabular-nums text-slate-900">{typeof row.count === 'number' ? row.count.toLocaleString() : row.count}</td>
                <td className="px-2 py-1 tabular-nums text-slate-600">{typeof row.total === 'number' ? row.total.toLocaleString() : row.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Function: ChangeTypeSplitPanel
function ChangeTypeSplitPanel({ loading, typeSplit, volumeTrend, typeDrilldown, setTypeDrilldown, setPriorityDrilldown }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-52">
        <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }
  if (typeSplit.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-12">No data</p>
  }

  // Function: handlePieClick
  function handlePieClick(data) {
    if (!data) return
    const typeName = data.type
    const monthRows = volumeTrend.map((m) => ({
      month: m.month,
      count: m[typeName.toLowerCase()] ?? '—',
      total: m.total ?? '—',
    }))
    setTypeDrilldown({
      title: `${typeName} — Monthly Volume`,
      rows: monthRows,
      columns: ['Month', typeName + ' Count', 'Total'],
    })
    setPriorityDrilldown(null)
  }

  return (
    <>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={typeSplit}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={105}
            paddingAngle={2}
            dataKey="count"
            nameKey="type"
            labelLine={false}
            label={<CustomPieLabel />}
            onClick={handlePieClick}
          >
            {typeSplit.map((entry, idx) => (
              <Cell
                key={idx}
                fill={TYPE_COLORS[entry.type] || TYPE_FALLBACK[idx % TYPE_FALLBACK.length]}
                style={{ cursor: 'pointer' }}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltipDark />} />
        </PieChart>
      </ResponsiveContainer>
      <div className="space-y-1.5 mt-2">
        {typeSplit.map((entry, idx) => (
          <div key={idx} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: TYPE_COLORS[entry.type] || TYPE_FALLBACK[idx % TYPE_FALLBACK.length] }} />
              <span className="text-xs text-slate-600">{entry.type}</span>
            </div>
            <span className="text-xs font-bold text-slate-900 tabular-nums">{entry.count?.toLocaleString()}</span>
          </div>
        ))}
      </div>
      <p className="text-xs text-slate-600 mt-2">Click a slice for monthly breakdown</p>
      {typeDrilldown && (
        <TypeDrilldownTable typeDrilldown={typeDrilldown} onClose={() => setTypeDrilldown(null)} />
      )}
    </>
  )
}

// Function: MonthlyVolumePanel
function MonthlyVolumePanel({ loading, volumeTrend }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-52">
        <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }
  if (volumeTrend.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-12">No data</p>
  }
  return (
    <ResponsiveContainer width="100%" height={380}>
      <BarChart data={volumeTrend} margin={{ left: 0, right: 8, top: 4, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
        <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} angle={-30} textAnchor="end" height={40} />
        <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
        <Tooltip content={<CustomTooltipDark />} />
        <Legend wrapperStyle={{ paddingTop: '8px', fontSize: '12px', color: '#94a3b8' }} />
        <Bar dataKey="normal" name="Normal" stackId="a" fill={TYPE_COLORS.Normal} radius={[0, 0, 0, 0]} />
        <Bar dataKey="standard" name="Standard" stackId="a" fill={TYPE_COLORS.Standard} radius={[0, 0, 0, 0]} />
        <Bar dataKey="emergency" name="Emergency" stackId="a" fill={TYPE_COLORS.Emergency} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

const PRIORITY_TYPE_COLOR_MAP = {
  Emergency: { color: 'text-accent-rose', bg: 'bg-rose-900/30', border: 'border-rose-700/50', icon: AlertTriangle },
  Normal: { color: 'text-accent-cyan', bg: 'bg-cyan-900/20', border: 'border-cyan-700/40', icon: Shield },
  Standard: { color: 'text-accent-indigo', bg: 'bg-indigo-900/20', border: 'border-indigo-700/40', icon: CheckCircle },
}

// Function: PriorityFallbackList
function PriorityFallbackList({ typeSplit }) {
  return (
    <div className="space-y-3">
      {typeSplit.map(({ type, count }, idx) => {
        const cfg = PRIORITY_TYPE_COLOR_MAP[type] || { color: 'text-slate-700', bg: 'bg-slate-100', border: 'border-slate-200', icon: BarChart2 }
        const Icon = cfg.icon
        return (
          <div key={idx} className={`flex items-center justify-between px-4 py-3 rounded-lg border ${cfg.bg} ${cfg.border}`}>
            <div className="flex items-center gap-2">
              <Icon className={`w-4 h-4 ${cfg.color}`} />
              <span className={`text-sm font-medium ${cfg.color}`}>{type}</span>
            </div>
            <span className="text-lg font-bold text-slate-900 tabular-nums">{count?.toLocaleString() ?? '—'}</span>
          </div>
        )
      })}
    </div>
  )
}

// Function: PriorityDrilldownCards
function PriorityDrilldownCards({ priorityDrilldown, onClose }) {
  return (
    <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-accent-cyan">L2: {priorityDrilldown.title}</span>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-900 text-lg leading-none">×</button>
      </div>
      {priorityDrilldown.rows.map((row, i) => (
        <div key={i} className="grid grid-cols-2 gap-2">
          <div className="rounded-lg bg-white border border-slate-200 p-2">
            <p className="text-xs text-slate-500">Count</p>
            <p className="text-lg font-bold text-slate-900 tabular-nums">{row.count?.toLocaleString() ?? '—'}</p>
          </div>
          <div className="rounded-lg bg-white border border-slate-200 p-2">
            <p className="text-xs text-slate-500">% of Total</p>
            <p className="text-lg font-bold text-cyan-300 tabular-nums">
              {row.pct != null ? `${Number(row.pct).toFixed(1)}%` : '—'}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}

// Function: PriorityChartPanel
function PriorityChartPanel({ priorityDist, priorityDrilldown, setPriorityDrilldown, setTypeDrilldown }) {
  // Function: handleBarClick
  function handleBarClick(data) {
    if (!data?.activePayload?.[0]) return
    const row = data.activePayload[0].payload
    setPriorityDrilldown({ title: row.priority, rows: [row] })
    setTypeDrilldown(null)
  }

  return (
    <>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={priorityDist} margin={{ left: 0, right: 8, top: 4, bottom: 4 }} onClick={handleBarClick}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="priority" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltipDark />} />
          <Bar dataKey="count" name="Count" fill="#818cf8" radius={[4, 4, 0, 0]} style={{ cursor: 'pointer' }} />
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-600 mt-2">Click a bar for details</p>
      {priorityDrilldown && (
        <PriorityDrilldownCards priorityDrilldown={priorityDrilldown} onClose={() => setPriorityDrilldown(null)} />
      )}
    </>
  )
}

// Function: PrioritySummaryStats
function PrioritySummaryStats({ d, loading, total }) {
  return (
    <div className="pt-3 mt-3 border-t border-slate-200 space-y-2">
      {d.risk?.expedited_pct != null && (
        <div className="flex items-center justify-between px-1">
          <span className="text-xs text-slate-500">Expedited %</span>
          <span className="text-sm font-bold text-amber-300 tabular-nums">
            {Number(d.risk.expedited_pct).toFixed(1)}%
          </span>
        </div>
      )}
      {d.risk?.rescheduled_pct != null && (
        <div className="flex items-center justify-between px-1">
          <span className="text-xs text-slate-500">Rescheduled %</span>
          <span className="text-sm font-bold text-rose-300 tabular-nums">
            {Number(d.risk.rescheduled_pct).toFixed(1)}%
          </span>
        </div>
      )}
      <div className="flex items-center justify-between px-1">
        <span className="text-xs text-slate-500">Total Changes</span>
        <span className="text-sm font-bold text-slate-900 tabular-nums">
          {loading ? '—' : total > 0 ? total.toLocaleString() : '—'}
        </span>
      </div>
    </div>
  )
}

// Function: PriorityBreakdownPanel
function PriorityBreakdownPanel({
  loading, priorityDist, typeSplit, priorityDrilldown, setPriorityDrilldown, setTypeDrilldown, d, total,
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-4 h-4 text-accent-amber" />
        <span className="text-lg font-semibold text-slate-700 uppercase tracking-wider">Priority Breakdown</span>
      </div>
      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-14 rounded-lg w-full" />
          ))}
        </div>
      ) : priorityDist.length === 0 ? (
        <PriorityFallbackList typeSplit={typeSplit} />
      ) : (
        <PriorityChartPanel
          priorityDist={priorityDist}
          priorityDrilldown={priorityDrilldown}
          setPriorityDrilldown={setPriorityDrilldown}
          setTypeDrilldown={setTypeDrilldown}
        />
      )}

      <PrioritySummaryStats d={d} loading={loading} total={total} />
    </div>
  )
}

// Function: ChangeRisk
export default function ChangeRisk() {
  const { dateRange } = useDashboard()
  const printRef = useRef(null)
  const [chgData, setChgData] = useState(null)
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)
  const [insightsLoading, setInsightsLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)
  const [refreshing, setRefreshing] = useState(false)
  const [typeDrilldown, setTypeDrilldown] = useState(null)
  const [priorityDrilldown, setPriorityDrilldown] = useState(null)
  const [drawer, setDrawer] = useState({ open: false, chartType: null, title: '' })
  // Function: openDrawer
  function openDrawer(chartType, title) { setDrawer({ open: true, chartType, title }) }
  // Function: closeDrawer
  function closeDrawer() { setDrawer((d) => ({ ...d, open: false })) }

  const fetchData = useCallback(async () => {
    try {
      const res = await getChanges(dateRange)
      setChgData(res.data)
    } catch (e) {
      console.error('Failed to load change data', e)
    } finally {
      setLoading(false)
    }
    try {
      const insRes = await getInsights({}, dateRange)
      setInsights(insRes.data)
    } catch (e) {
      console.error('Failed to load insights', e)
    } finally {
      setInsightsLoading(false)
    }
  }, [dateRange])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Function: handleRefresh
  async function handleRefresh() {
    setRefreshing(true)
    await fetchData()
    setRefreshKey((k) => k + 1)
    setTypeDrilldown(null)
    setPriorityDrilldown(null)
    setRefreshing(false)
  }

  const d = chgData || {}

  // FIXED: compute typeSplit from d.risk?.by_type dict
  const byType = d.risk?.by_type || d.summary?.by_type || {}
  const typeSplit = Object.entries(byType).map(([type, count]) => ({ type, count }))

  // FIXED: use d.volume_trend instead of d.monthly_volume
  const volumeTrend = Array.isArray(d.volume_trend) ? d.volume_trend : []

  // FIXED: use d.priority_dist for risk indicators panel
  const priorityDist = Array.isArray(d.priority_dist) ? d.priority_dist : []

  // FIXED: compute total from by_type dict
  const total = (byType.Normal || 0) + (byType.Standard || 0) + (byType.Emergency || 0)

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-lg gradient-bg-primary shadow-glow-md">
              <GitBranch className="w-7 h-7 text-white" />
            </div>
            Change & Release Risk Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-3">Emergency change tracking, success rates, cycle times, and release risk indicators</p>
        </div>
        <div className="flex items-center gap-2">
          <ExportPDFButton printRef={printRef} title="Change Risk" />
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

      <ChangeKPIRow loading={loading} total={total} byType={byType} d={d} openDrawer={openDrawer} />

      {/* Row 2 — Change risk Matplotlib chart — BIGGER */}
      <div className="mb-6">
        <ChartImage
          endpoint="change-risk"
          title="Change & Release Risk Analysis"
          height={600}
          refreshKey={refreshKey}
          onDrilldown={() => openDrawer('change-risk', 'Change & Release Risk Analysis')}
        />
      </div>

      {/* Row 3 — Three columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 className="w-4 h-4 text-accent-indigo" />
            <span className="text-lg font-semibold text-slate-700 uppercase tracking-wider">Change Type Split</span>
          </div>
          <ChangeTypeSplitPanel
            loading={loading}
            typeSplit={typeSplit}
            volumeTrend={volumeTrend}
            typeDrilldown={typeDrilldown}
            setTypeDrilldown={setTypeDrilldown}
            setPriorityDrilldown={setPriorityDrilldown}
          />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 className="w-4 h-4 text-accent-cyan" />
            <span className="text-lg font-semibold text-slate-700 uppercase tracking-wider">Monthly Change Volume</span>
          </div>
          <MonthlyVolumePanel loading={loading} volumeTrend={volumeTrend} />
        </div>

        <PriorityBreakdownPanel
          loading={loading}
          priorityDist={priorityDist}
          typeSplit={typeSplit}
          priorityDrilldown={priorityDrilldown}
          setPriorityDrilldown={setPriorityDrilldown}
          setTypeDrilldown={setTypeDrilldown}
          d={d}
          total={total}
        />
      </div>

      {/* Row 4 — Leadership insights */}
      <InsightPanel
        title="Change & Release — Leadership Insights"
        insights={insights?.changes || []}
        loading={insightsLoading}
      />

      {/* Drilldown drawer */}
      <DrilldownDrawer
        open={drawer.open}
        onClose={closeDrawer}
        title={drawer.title}
        chartType={drawer.chartType}
        data={{ risk: d.risk, volume_trend: volumeTrend }}
      />
    </div>
  )
}
