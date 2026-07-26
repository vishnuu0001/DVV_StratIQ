// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (ServiceRequests.jsx)
// Date: 2025-08-04
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Ticket,
  Inbox,
  Clock,
  Timer,
  Users,
  RefreshCw,
  BarChart2,
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
import InsightPanel from '../components/InsightPanel'
import DrilldownDrawer from '../components/DrilldownDrawer'
import ExportPDFButton from '../components/ExportPDFButton'
import { getServiceRequests, getAssignmentGroupHotspots, getInsights } from '../api'
import { useDashboard } from '../context/DashboardContext'

const COLORS = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#67e8f9', '#86efac']

// Function: CustomTooltipDark
const CustomTooltipDark = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800/90 border border-slate-700 backdrop-blur rounded-lg px-3 py-2 text-xs shadow-xl">
        <p className="text-slate-200 font-medium mb-1">{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color }}>
            {p.name}: <span className="font-bold text-white">{p.value?.toLocaleString()}</span>
          </p>
        ))}
      </div>
    )
  }
  return null
}

// Function: SectionTitle
function SectionTitle({ icon: Icon, title, color = 'text-accent-cyan' }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <Icon className={`w-4 h-4 ${color}`} />
      <h2 className="text-lg font-semibold text-slate-700 uppercase tracking-wider">{title}</h2>
    </div>
  )
}

// Function: ageingDictToArray
function ageingDictToArray(ageing) {
  if (!ageing || typeof ageing !== 'object' || Array.isArray(ageing)) return []
  return [
    { bucket: '<7 days', count: ageing.lt_7d ?? 0 },
    { bucket: '7-30 days', count: ageing['7_30d'] ?? 0 },
    { bucket: '30-90 days', count: ageing['30_90d'] ?? 0 },
    { bucket: '>90 days', count: ageing.gt_90d ?? 0 },
  ]
}

// Function: SRKPIRow
function SRKPIRow({ loading, d, avgClosureDays, openDrawer }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
      <KPICard
        title="Total SRs"
        value={loading ? null : d.summary?.total?.toLocaleString() ?? '—'}
        subtitle="All service requests"
        icon={Ticket}
        color="cyan"
        loading={loading}
        onClick={() => openDrawer('service-request-productivity', 'Total SRs — L2 / L3')}
      />
      <KPICard
        title="Open Backlog"
        value={loading ? null : d.summary?.backlog_count?.toLocaleString() ?? '—'}
        subtitle="Unresolved tickets"
        icon={Inbox}
        color="amber"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('service-request-productivity', 'Open Backlog — L2 / L3')}
      />
      <KPICard
        title="Avg Closure Days"
        value={loading ? null : avgClosureDays != null ? `${avgClosureDays.toFixed(1)}d` : '—'}
        subtitle="Mean days to close"
        icon={Clock}
        color="rose"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('service-request-productivity', 'Avg Closure Days — L2 / L3')}
      />
      <KPICard
        title="Median Closure"
        value={loading ? null : d.summary?.median_closure_hours != null
          ? `${Number(d.summary.median_closure_hours).toFixed(1)}h`
          : '—'}
        subtitle="Median hours to close"
        icon={Timer}
        color="indigo"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('service-request-productivity', 'Median Closure — L2 / L3')}
      />
    </div>
  )
}

// Function: TopCategoriesPanel
function TopCategoriesPanel({ loading, categories, categoryDrilldown, setCategoryDrilldown, d }) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="skeleton h-6 rounded w-full" />
        ))}
      </div>
    )
  }
  if (categories.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-8">No category data available</p>
  }

  // Function: handleBarClick
  function handleBarClick(data) {
    if (!data) return
    setCategoryDrilldown({
      title: data.category || 'Category',
      count: data.count,
    })
  }

  const pctOfTotal = d.summary?.total && categoryDrilldown?.count
    ? `${((categoryDrilldown.count / d.summary.total) * 100).toFixed(1)}%`
    : '—'

  return (
    <>
      <ResponsiveContainer width="100%" height={380}>
        <BarChart
          data={categories}
          layout="vertical"
          margin={{ left: 8, right: 20, top: 4, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
          <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis
            dataKey="category"
            type="category"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={130}
          />
          <Tooltip content={<CustomTooltipDark />} />
          <Bar
            dataKey="count"
            name="Count"
            radius={[0, 4, 4, 0]}
            style={{ cursor: 'pointer' }}
            onClick={handleBarClick}
          >
            {categories.map((_, idx) => (
              <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-600 mt-2">Click a bar for details</p>
      {categoryDrilldown && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-accent-cyan">L2: {categoryDrilldown.title}</span>
            <button onClick={() => setCategoryDrilldown(null)} className="text-slate-500 hover:text-slate-900 text-lg leading-none">×</button>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg bg-white border border-slate-200 p-3">
              <p className="text-xs text-slate-500 mb-1">Request Count</p>
              <p className="text-2xl font-bold text-slate-900 tabular-nums">
                {categoryDrilldown.count?.toLocaleString() ?? '—'}
              </p>
            </div>
            <div className="rounded-lg bg-white border border-slate-200 p-3">
              <p className="text-xs text-slate-500 mb-1">% of Total SRs</p>
              <p className="text-2xl font-bold text-cyan-300 tabular-nums">{pctOfTotal}</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

// Function: AgeingBarPanel
function AgeingBarPanel({ loading, ageingArr }) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="skeleton h-6 rounded w-full" />
        ))}
      </div>
    )
  }
  if (ageingArr.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-8">No ageing data available</p>
  }
  return (
    <ResponsiveContainer width="100%" height={380}>
      <BarChart data={ageingArr} margin={{ left: 8, right: 20, top: 4, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
        <XAxis dataKey="bucket" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
        <Tooltip content={<CustomTooltipDark />} />
        <Bar dataKey="count" name="Tickets" fill="#f87171" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

// Function: CycleTimeSummaryRow
function CycleTimeSummaryRow({ cycleTime }) {
  if (!cycleTime) return null
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
      <div className="rounded-xl border border-slate-200 bg-white p-4 bg-gradient-to-br from-white to-slate-50">
        <p className="text-xs text-slate-500 mb-1">Avg Cycle Time</p>
        <p className="text-2xl font-bold text-cyan-300 tabular-nums">
          {cycleTime.avg != null ? `${Number(cycleTime.avg).toFixed(1)}h` : '—'}
        </p>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-4 bg-gradient-to-br from-white to-slate-50">
        <p className="text-xs text-slate-500 mb-1">Median Cycle Time</p>
        <p className="text-2xl font-bold text-indigo-300 tabular-nums">
          {cycleTime.median != null ? `${Number(cycleTime.median).toFixed(1)}h` : '—'}
        </p>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-4 bg-gradient-to-br from-white to-slate-50">
        <p className="text-xs text-slate-500 mb-1">P90 Cycle Time</p>
        <p className="text-2xl font-bold text-amber-300 tabular-nums">
          {cycleTime.p90 != null ? `${Number(cycleTime.p90).toFixed(1)}h` : '—'}
        </p>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-4 bg-gradient-to-br from-white to-slate-50">
        <p className="text-xs text-slate-500 mb-1">P95 Cycle Time</p>
        <p className="text-2xl font-bold text-rose-300 tabular-nums">
          {cycleTime.p95 != null ? `${Number(cycleTime.p95).toFixed(1)}h` : '—'}
        </p>
      </div>
    </div>
  )
}

// Function: slaPctColor
function slaPctColor(pct) {
  if (pct >= 90) return 'text-accent-emerald'
  if (pct >= 75) return 'text-accent-amber'
  return 'text-accent-rose'
}

// Function: GroupLoadTableBody
function GroupLoadTableBody({ loading, groups }) {
  if (loading) {
    return [...Array(6)].map((_, i) => (
      <tr key={i}>
        {[...Array(5)].map((__, j) => (
          <td key={j}><div className="skeleton h-4 rounded w-full" /></td>
        ))}
      </tr>
    ))
  }
  if (groups.length === 0) {
    return (
      <tr>
        <td colSpan={5} className="text-center text-slate-500 py-8">No group data available</td>
      </tr>
    )
  }
  return groups.map((g, i) => (
    <tr key={i}>
      <td className="font-medium text-slate-700">{g.group || g.assignment_group || '—'}</td>
      <td className="text-right tabular-nums">{g.total?.toLocaleString() ?? '—'}</td>
      <td className="text-right tabular-nums">{g.open?.toLocaleString() ?? '—'}</td>
      <td className="text-right tabular-nums text-slate-600">
        {g.avg_days != null ? `${Number(g.avg_days).toFixed(1)}d` : '—'}
      </td>
      <td className="text-right tabular-nums">
        {g.sla_pct != null ? (
          <span className={`font-medium ${slaPctColor(Number(g.sla_pct))}`}>
            {Number(g.sla_pct).toFixed(1)}%
          </span>
        ) : '—'}
      </td>
    </tr>
  ))
}

// Function: GroupLoadTable
function GroupLoadTable({ loading, groups }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
        <Users className="w-4 h-4 text-accent-indigo" />
        <span className="text-sm font-medium text-slate-700">Assignment Group Load</span>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Assignment Group</th>
              <th className="text-right">Total</th>
              <th className="text-right">Open</th>
              <th className="text-right">Avg Days</th>
              <th className="text-right">SLA %</th>
            </tr>
          </thead>
          <tbody>
            <GroupLoadTableBody loading={loading} groups={groups} />
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Function: ServiceRequests
export default function ServiceRequests() {
  const { dateRange } = useDashboard()
  const printRef = useRef(null)
  const [srData, setSrData] = useState(null)
  const [groups, setGroups] = useState([])
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)
  const [insightsLoading, setInsightsLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)
  const [refreshing, setRefreshing] = useState(false)
  const [categoryDrilldown, setCategoryDrilldown] = useState(null)
  const [drawer, setDrawer] = useState({ open: false, chartType: null, title: '' })
  // Function: openDrawer
  function openDrawer(chartType, title) { setDrawer({ open: true, chartType, title }) }
  // Function: closeDrawer
  function closeDrawer() { setDrawer((d) => ({ ...d, open: false })) }

  const fetchData = useCallback(async () => {
    try {
      const [srRes, grpRes] = await Promise.all([
        getServiceRequests(dateRange),
        getAssignmentGroupHotspots(10, dateRange),
      ])
      setSrData(srRes.data)
      setGroups(Array.isArray(grpRes.data) ? grpRes.data : grpRes.data?.groups || [])
    } catch (e) {
      console.error('Failed to load SR data', e)
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
    setCategoryDrilldown(null)
    setRefreshing(false)
  }

  const d = srData || {}

  // FIXED: d.summary?.top_categories instead of d.categories
  const categories = Array.isArray(d.summary?.top_categories)
    ? d.summary.top_categories.slice(0, 10)
    : []

  // FIXED: d.ageing is a dict — convert to array
  const ageingArr = ageingDictToArray(d.ageing)

  // FIXED: avg_closure_days derived from avg_closure_hours / 24
  const avgClosureDays = d.summary?.avg_closure_hours != null
    ? d.summary.avg_closure_hours / 24
    : null

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-lg gradient-bg-primary shadow-glow-md">
              <Ticket className="w-7 h-7 text-white" />
            </div>
            Service Request & Inquiry Productivity
          </h1>
          <p className="text-slate-400 text-sm mt-3">Backlog health, closure velocity, cycle times, and assignment group load</p>
        </div>
        <div className="flex items-center gap-2">
          <ExportPDFButton printRef={printRef} title="Service Requests" />
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

      <SRKPIRow loading={loading} d={d} avgClosureDays={avgClosureDays} openDrawer={openDrawer} />

      {/* Row 2 — Matplotlib chart full width — BIGGER */}
      <div className="mb-6">
        <ChartImage
          endpoint="service-request-productivity"
          title="Service Request Productivity Dashboard"
          height={600}
          onDrilldown={() => openDrawer('service-request-productivity', 'Service Request Productivity')}
          refreshKey={refreshKey}
        />
      </div>

      {/* Row 3 — Top categories + Ageing analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <SectionTitle icon={BarChart2} title="Top Request Categories" />
          <TopCategoriesPanel
            loading={loading}
            categories={categories}
            categoryDrilldown={categoryDrilldown}
            setCategoryDrilldown={setCategoryDrilldown}
            d={d}
          />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <SectionTitle icon={Clock} title="Open Ticket Ageing Analysis" color="text-accent-rose" />
          <AgeingBarPanel loading={loading} ageingArr={ageingArr} />
        </div>
      </div>

      {/* Row 4 — Cycle time summary */}
      <CycleTimeSummaryRow cycleTime={d.cycle_time} />

      {/* Row 5 — Leadership insights */}
      <div className="mb-6">
        <InsightPanel
          title="Service Requests — Leadership Insights"
          insights={insights?.service_requests || []}
          loading={insightsLoading}
        />
      </div>

      {/* Row 6 — Assignment group load table */}
      <GroupLoadTable loading={loading} groups={groups} />

      {/* Drilldown drawer */}
      <DrilldownDrawer
        open={drawer.open}
        onClose={closeDrawer}
        title={drawer.title}
        chartType={drawer.chartType}
        data={{ summary: d.summary, ageing: d.ageing }}
      />
    </div>
  )
}
