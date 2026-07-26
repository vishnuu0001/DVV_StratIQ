// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (IncidentCommand.jsx)
// Date: 2026-02-01
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  AlertTriangle,
  Inbox,
  Clock,
  Timer,
  BarChart2,
  RefreshCw,
  CheckCircle,
} from 'lucide-react'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
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
import { getIncidents, getApplicationHotspots, getInsights } from '../api'
import { useDashboard } from '../context/DashboardContext'

const PIE_COLORS = {
  Critical: '#f87171',
  High: '#fbbf24',
  Medium: '#38bdf8',
  Low: '#34d399',
  Planning: '#818cf8',
}
const PIE_FALLBACK = ['#f87171', '#fbbf24', '#38bdf8', '#34d399', '#818cf8', '#a78bfa']

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

// Function: IncidentKPIRow
function IncidentKPIRow({ loading, d, openDrawer }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      <KPICard
        title="Total Incidents"
        value={loading ? null : d.summary?.total_incidents?.toLocaleString() ?? '—'}
        subtitle="All incident records"
        icon={AlertTriangle}
        color="rose"
        loading={loading}
        onClick={() => openDrawer('incident-mttr', 'Total Incidents — L2 / L3')}
      />
      <KPICard
        title="Ageing > 30 days"
        value={loading ? null : ((d.ageing?.['30_90d'] ?? 0) + (d.ageing?.gt_90d ?? 0)).toLocaleString()}
        subtitle="Open > 30 days"
        icon={Inbox}
        color="amber"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('incident-mttr', 'Incident Ageing — L2 / L3')}
      />
      <KPICard
        title="Avg Cycle Time"
        value={loading ? null : d.cycle_time?.avg != null ? `${Number(d.cycle_time.avg).toFixed(1)}h` : '—'}
        subtitle="Mean time to resolve"
        icon={Clock}
        color="cyan"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('incident-mttr', 'Avg Cycle Time — L2 / L3')}
      />
      <KPICard
        title="P90 Resolution"
        value={loading ? null : d.cycle_time?.p90 != null ? `${Number(d.cycle_time.p90).toFixed(1)}h` : '—'}
        subtitle="90th percentile hours"
        icon={Timer}
        color="indigo"
        loading={loading}
        invertTrend
        onClick={() => openDrawer('incident-mttr', 'P90 Resolution — L2 / L3')}
      />
      <KPICard
        title="SLA Compliance"
        value={loading ? null : d.summary?.sla_compliance_pct != null ? `${Number(d.summary.sla_compliance_pct).toFixed(1)}%` : '—'}
        subtitle="Within SLA target"
        icon={CheckCircle}
        color="emerald"
        loading={loading}
        onClick={() => openDrawer('incident-mttr', 'SLA Compliance — L2 / L3')}
      />
    </div>
  )
}

// Function: PriorityDrilldownTable
function PriorityDrilldownTable({ priorityDrilldown, onClose }) {
  return (
    <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-accent-cyan">L2: {priorityDrilldown.title}</span>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-900 text-lg leading-none">×</button>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table text-xs w-full">
          <thead>
            <tr>
              {priorityDrilldown.columns.map((col, i) => (
                <th key={i} className="text-left px-2 py-1 text-slate-600 font-semibold">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {priorityDrilldown.rows.map((row, i) => (
              <tr key={i} className="border-t border-slate-200">
                <td className="px-2 py-1 text-slate-700">{row.month}</td>
                <td className="px-2 py-1 tabular-nums text-slate-900">{typeof row.count === 'number' ? row.count.toLocaleString() : row.count}</td>
                <td className="px-2 py-1 tabular-nums text-slate-600">{row.avg_mttr}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Function: PriorityDistributionPanel
function PriorityDistributionPanel({
  loading, priorityDist, mttrTrend, priorityDrilldown, setPriorityDrilldown, setHotspotDrilldown,
}) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }
  if (priorityDist.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-16">No data available</p>
  }

  // Function: handlePieClick
  function handlePieClick(data) {
    if (!data) return
    const priority = data.priority
    const monthRows = mttrTrend.map((m) => ({
      month: m.month,
      count: m.count ?? '—',
      avg_mttr: m.avg_mttr_hours != null ? `${Number(m.avg_mttr_hours).toFixed(1)}h` : '—',
    }))
    setPriorityDrilldown({
      title: `${priority} — Monthly Trend`,
      rows: monthRows,
      columns: ['Month', 'Incident Count', 'Avg MTTR'],
    })
    setHotspotDrilldown(null)
  }

  return (
    <>
      <div className="flex items-center gap-4">
        <ResponsiveContainer width="60%" height={380}>
          <PieChart>
            <Pie
              data={priorityDist}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={130}
              paddingAngle={2}
              dataKey="count"
              nameKey="priority"
              labelLine={false}
              label={<CustomPieLabel />}
              onClick={handlePieClick}
            >
              {priorityDist.map((entry, idx) => (
                <Cell
                  key={idx}
                  fill={PIE_COLORS[entry.priority] || PIE_FALLBACK[idx % PIE_FALLBACK.length]}
                  style={{ cursor: 'pointer' }}
                />
              ))}
            </Pie>
            <Tooltip
              content={<CustomTooltipDark />}
              formatter={(val, name) => [val.toLocaleString(), name]}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex-1 space-y-2">
          {priorityDist.map((entry, idx) => (
            <div key={idx} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: PIE_COLORS[entry.priority] || PIE_FALLBACK[idx % PIE_FALLBACK.length] }}
                />
                <span className="text-xs text-slate-600">{entry.priority}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-900 tabular-nums">
                  {entry.count?.toLocaleString()}
                </span>
                {entry.pct != null && (
                  <span className="text-xs text-slate-500">{Number(entry.pct).toFixed(1)}%</span>
                )}
              </div>
            </div>
          ))}
          <p className="text-xs text-slate-600 mt-3">Click a slice for monthly trend</p>
        </div>
      </div>
      {priorityDrilldown && (
        <PriorityDrilldownTable priorityDrilldown={priorityDrilldown} onClose={() => setPriorityDrilldown(null)} />
      )}
    </>
  )
}

// Function: HotspotDrilldownPanel
function HotspotDrilldownPanel({ hotspotDrilldown, onClose }) {
  return (
    <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-accent-cyan">L2: {hotspotDrilldown.title}</span>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-900 text-lg leading-none">×</button>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {hotspotDrilldown.rows.map((app, i) => (
          <React.Fragment key={i}>
            <div className="rounded-lg bg-white border border-slate-200 p-3">
              <p className="text-xs text-slate-500 mb-1">Incident Count</p>
              <p className="text-xl font-bold text-slate-900 tabular-nums">{app.count?.toLocaleString() ?? '—'}</p>
            </div>
            <div className="rounded-lg bg-white border border-slate-200 p-3">
              <p className="text-xs text-slate-500 mb-1">Avg MTTR</p>
              <p className="text-xl font-bold text-amber-300 tabular-nums">
                {app.avg_mttr_hours != null ? `${Number(app.avg_mttr_hours).toFixed(1)}h` : '—'}
              </p>
            </div>
            <div className="rounded-lg bg-white border border-slate-200 p-3">
              <p className="text-xs text-slate-500 mb-1">% of Total</p>
              <p className="text-xl font-bold text-cyan-300 tabular-nums">
                {app.pct_of_total != null ? `${Number(app.pct_of_total).toFixed(1)}%` : '—'}
              </p>
            </div>
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}

// Function: HotspotsPanel
function HotspotsPanel({ loading, hotspotData, hotspotDrilldown, setHotspotDrilldown, setPriorityDrilldown }) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="skeleton h-5 rounded w-full" />
        ))}
      </div>
    )
  }
  if (hotspotData.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-16">No hotspot data available</p>
  }

  // Function: handleBarClick
  function handleBarClick(data) {
    if (!data?.activePayload?.[0]) return
    const app = data.activePayload[0].payload
    setHotspotDrilldown({
      title: app.application || 'Application',
      rows: [app],
    })
    setPriorityDrilldown(null)
  }

  return (
    <>
      <ResponsiveContainer width="100%" height={380}>
        <BarChart
          data={hotspotData.slice(0, 10)}
          layout="vertical"
          margin={{ left: 4, right: 20, top: 4, bottom: 4 }}
          onClick={handleBarClick}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
          <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis
            dataKey="application"
            type="category"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={120}
          />
          <Tooltip content={<CustomTooltipDark />} />
          <Bar dataKey="count" name="Incidents" fill="#fbbf24" radius={[0, 4, 4, 0]} style={{ cursor: 'pointer' }} />
        </BarChart>
      </ResponsiveContainer>
      {hotspotDrilldown && (
        <HotspotDrilldownPanel hotspotDrilldown={hotspotDrilldown} onClose={() => setHotspotDrilldown(null)} />
      )}
    </>
  )
}

// Function: MttrTrendPanel
function MttrTrendPanel({ loading, mttrTrend }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-60">
        <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }
  if (mttrTrend.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-16">No trend data available</p>
  }
  return (
    <ResponsiveContainer width="100%" height={420}>
      <LineChart data={mttrTrend} margin={{ left: 0, right: 24, top: 4, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
        <YAxis yAxisId="left" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
        <YAxis
          yAxisId="right"
          orientation="right"
          tick={{ fill: '#94a3b8', fontSize: 12 }}
          axisLine={false}
          tickLine={false}
          label={{ value: 'MTTR (h)', angle: 90, position: 'insideRight', fill: '#64748b', fontSize: 11 }}
        />
        <Tooltip content={<CustomTooltipDark />} />
        <Legend wrapperStyle={{ paddingTop: '8px', fontSize: '12px', color: '#94a3b8' }} />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="count"
          name="Incidents"
          stroke="#38bdf8"
          strokeWidth={2}
          dot={{ r: 4, fill: '#38bdf8' }}
          activeDot={{ r: 6 }}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="avg_mttr_hours"
          name="Avg MTTR (h)"
          stroke="#f87171"
          strokeWidth={2}
          dot={{ r: 4, fill: '#f87171' }}
          activeDot={{ r: 6 }}
          strokeDasharray="4 2"
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="p90_hours"
          name="P90 MTTR (h)"
          stroke="#fbbf24"
          strokeWidth={1.5}
          dot={{ r: 3, fill: '#fbbf24' }}
          activeDot={{ r: 5 }}
          strokeDasharray="2 3"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

// Function: AgeingPanel
function AgeingPanel({ loading, ageingArr }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-60">
        <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }
  if (ageingArr.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-16">No ageing data available</p>
  }
  return (
    <ResponsiveContainer width="100%" height={300}>
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

// Function: IncidentCommand
export default function IncidentCommand() {
  const { dateRange } = useDashboard()
  const printRef = useRef(null)
  const [incData, setIncData] = useState(null)
  const [hotspots, setHotspots] = useState([])
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)
  const [insightsLoading, setInsightsLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)
  const [refreshing, setRefreshing] = useState(false)
  const [priorityDrilldown, setPriorityDrilldown] = useState(null)
  const [hotspotDrilldown, setHotspotDrilldown] = useState(null)
  const [drawer, setDrawer] = useState({ open: false, chartType: null, title: '' })
  // Function: openDrawer
  function openDrawer(chartType, title) { setDrawer({ open: true, chartType, title }) }
  // Function: closeDrawer
  function closeDrawer() { setDrawer((d) => ({ ...d, open: false })) }

  const fetchData = useCallback(async () => {
    try {
      const [incRes, hsRes] = await Promise.all([
        getIncidents(dateRange),
        getApplicationHotspots(10, dateRange),
      ])
      setIncData(incRes.data)
      setHotspots(Array.isArray(hsRes.data) ? hsRes.data : hsRes.data?.hotspots || [])
    } catch (e) {
      console.error('Failed to load incident data', e)
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
    setPriorityDrilldown(null)
    setHotspotDrilldown(null)
    setRefreshing(false)
  }

  const d = incData || {}
  // FIXED: use d.priority_dist instead of d.priority_distribution
  const priorityDist = Array.isArray(d.priority_dist) ? d.priority_dist : []
  // FIXED: use d.mttr_trend instead of d.monthly_trend
  const mttrTrend = Array.isArray(d.mttr_trend) ? d.mttr_trend : []
  const ageingArr = ageingDictToArray(d.ageing)

  // Hotspot data: prefer inline d.hotspots, fall back to separate API call
  const hotspotData = (Array.isArray(d.hotspots) && d.hotspots.length > 0) ? d.hotspots : hotspots

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-lg gradient-bg-primary shadow-glow-md">
              <AlertTriangle className="w-7 h-7 text-white" />
            </div>
            Incident Command Center
          </h1>
          <p className="text-slate-400 text-sm mt-3">MTTR analytics, priority distribution, hotspot identification, and resolution trends</p>
        </div>
        <div className="flex items-center gap-2">
          <ExportPDFButton printRef={printRef} title="Incident Command" />
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

      <IncidentKPIRow loading={loading} d={d} openDrawer={openDrawer} />

      {/* Row 2 — MTTR chart full width — BIGGER */}
      <div className="mb-6">
        <ChartImage
          endpoint="incident-mttr"
          title="Incident MTTR Analysis"
          height={600}
          refreshKey={refreshKey}
          onDrilldown={() => openDrawer('incident-mttr', 'Incident MTTR Analysis')}
        />
      </div>

      {/* Row 3 — Priority pie + Application hotspots bar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 className="w-4 h-4 text-accent-rose" />
            <span className="text-lg font-semibold text-slate-700 uppercase tracking-wider">Priority Distribution</span>
          </div>
          <PriorityDistributionPanel
            loading={loading}
            priorityDist={priorityDist}
            mttrTrend={mttrTrend}
            priorityDrilldown={priorityDrilldown}
            setPriorityDrilldown={setPriorityDrilldown}
            setHotspotDrilldown={setHotspotDrilldown}
          />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 className="w-4 h-4 text-accent-amber" />
            <span className="text-lg font-semibold text-slate-700 uppercase tracking-wider">Top Application Hotspots</span>
          </div>
          <HotspotsPanel
            loading={loading}
            hotspotData={hotspotData}
            hotspotDrilldown={hotspotDrilldown}
            setHotspotDrilldown={setHotspotDrilldown}
            setPriorityDrilldown={setPriorityDrilldown}
          />
        </div>
      </div>

      {/* Row 4 — Monthly MTTR trend line chart (dual axis) */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <BarChart2 className="w-4 h-4 text-accent-cyan" />
          <span className="text-lg font-semibold text-slate-700 uppercase tracking-wider">Monthly Incident Volume & MTTR Trend</span>
        </div>
        <MttrTrendPanel loading={loading} mttrTrend={mttrTrend} />
      </div>

      {/* Row 5 — Ageing analysis */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-4 h-4 text-accent-rose" />
          <span className="text-lg font-semibold text-slate-700 uppercase tracking-wider">Open Ticket Ageing Analysis</span>
        </div>
        <AgeingPanel loading={loading} ageingArr={ageingArr} />
      </div>

      {/* Row 6 — Leadership insights */}
      <InsightPanel
        title="Incident Command — Leadership Insights"
        insights={insights?.incidents || []}
        loading={insightsLoading}
      />

      {/* Drilldown drawer for Matplotlib charts */}
      <DrilldownDrawer
        open={drawer.open}
        onClose={closeDrawer}
        title={drawer.title}
        chartType={drawer.chartType}
        data={drawer.chartType === 'incident-mttr' ? incData : { hotspots }}
      />
    </div>
  )
}
