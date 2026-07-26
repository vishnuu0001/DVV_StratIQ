// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (SLAKPIDashboard.jsx)
// Date: 2025-08-23
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  BarChart3,
  AlertCircle,
} from 'lucide-react'
import { getSLABreachRisk } from '../api'
import { useDashboard } from '../context/DashboardContext'
import DrilldownDrawer from '../components/DrilldownDrawer'
import ExportPDFButton from '../components/ExportPDFButton'

// Function: MetricCard
function MetricCard({ title, value, subtitle, icon: Icon, status = 'neutral', trend = null, onClick }) {
  const statusColors = {
    good: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    warning: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    critical: 'text-rose-300 bg-rose-500/10 border-rose-500/30',
    neutral: 'text-slate-300 bg-slate-500/10 border-slate-500/30',
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left card-modern p-6 border ${statusColors[status]} hover:-translate-y-0.5 transition-all ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-bold">{value}</p>
            {trend && (
              <div className={`flex items-center gap-1 text-sm ${trend > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {trend > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span>{Math.abs(trend)}%</span>
              </div>
            )}
          </div>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className="p-3 rounded-lg bg-slate-700/30">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </button>
  )
}

// Function: TrendLine
function TrendLine({ label, data, color = 'cyan' }) {
  const colorClass = {
    cyan: 'text-accent-cyan',
    emerald: 'text-emerald-400',
    amber: 'text-amber-400',
    rose: 'text-rose-400',
  }[color] || 'text-accent-cyan'

  return (
    <div className="flex items-center gap-2 text-xs text-slate-300 py-2 border-b border-slate-700/30 last:border-0">
      <div className={`w-3 h-3 rounded-full ${colorClass}`} />
      <span className="flex-1">{label}</span>
      <span className="font-semibold">{data}</span>
    </div>
  )
}

// Function: breachRiskStatus
function breachRiskStatus(pct) {
  if (pct > 20) return 'critical'
  if (pct > 10) return 'warning'
  return 'good'
}

// Function: trajectoryStatus
function trajectoryStatus(trajectory) {
  if (trajectory === 'deteriorating') return 'critical'
  if (trajectory === 'improving') return 'good'
  return 'neutral'
}

// Function: TopKPIsRow
function TopKPIsRow({ loading, data, openDrawer }) {
  const trajectoryLabel = (data.trajectory || 'stable').charAt(0).toUpperCase() + (data.trajectory || 'stable').slice(1)
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-slide-up">
      <MetricCard
        title="Current Breach Risk"
        value={loading ? '—' : `${data.current_breach_risk_pct || 0}%`}
        subtitle="Tickets at risk"
        icon={AlertTriangle}
        status={breachRiskStatus(data.current_breach_risk_pct)}
        onClick={() => openDrawer('sla-kpi', 'Current Breach Risk — L2 / L3')}
      />
      <MetricCard
        title="Breached Tickets"
        value={loading ? '—' : data.breached_tickets || 0}
        subtitle="SLA violations"
        icon={AlertCircle}
        status={data.breached_tickets > 0 ? 'critical' : 'good'}
        onClick={() => openDrawer('sla-kpi', 'Breached Tickets — L2 / L3')}
      />
      <MetricCard
        title="At-Risk Tickets"
        value={loading ? '—' : data.at_risk_tickets || 0}
        subtitle="Approaching SLA limit"
        icon={Clock}
        status={data.at_risk_tickets > 10 ? 'warning' : 'neutral'}
        onClick={() => openDrawer('sla-kpi', 'At-Risk Tickets — L2 / L3')}
      />
      <MetricCard
        title="Trajectory"
        value={loading ? '—' : trajectoryLabel}
        subtitle="Month-over-month trend"
        icon={TrendingUp}
        status={trajectoryStatus(data.trajectory)}
        onClick={() => openDrawer('sla-kpi', 'SLA Trajectory — L2 / L3')}
      />
    </div>
  )
}

// Function: BreachTrendPanel
function BreachTrendPanel({ loading, data }) {
  const trend = data.breach_trend || []
  return (
    <div className="card-modern p-6">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4 text-accent-cyan" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Breach Trend (Last 12 Months)</h2>
      </div>
      {loading ? (
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => <div key={i} className="h-4 w-full rounded skeleton" />)}
        </div>
      ) : trend.length > 0 ? (
        <div className="space-y-2">
          {trend.slice(-6).map((t, i) => (
            <TrendLine
              key={i}
              label={t.month}
              data={`${t.breach_pct}% (${t.count} tickets)`}
              color={t.breach_pct > 20 ? 'rose' : t.breach_pct > 10 ? 'amber' : 'emerald'}
            />
          ))}
        </div>
      ) : (
        <p className="text-xs text-slate-500 italic">No trend data available.</p>
      )}
    </div>
  )
}

// Function: breachCategoryLabel
function breachCategoryLabel(pct) {
  if (pct > 20) return '🔴 CRITICAL'
  if (pct > 10) return '🟠 WARNING'
  return '🟢 HEALTHY'
}

// Function: breachBarColor
function breachBarColor(pct) {
  if (pct > 20) return 'bg-rose-500'
  if (pct > 10) return 'bg-amber-500'
  return 'bg-emerald-500'
}

// Function: trajectoryDisplayLabel
function trajectoryDisplayLabel(trajectory) {
  if (trajectory === 'deteriorating') return '📉 Deteriorating'
  if (trajectory === 'improving') return '📈 Improving'
  return '➡️ Stable'
}

// Function: trajectoryDescription
function trajectoryDescription(trajectory) {
  if (trajectory === 'deteriorating') return 'Breach risk is increasing. Consider escalating support capacity.'
  if (trajectory === 'improving') return 'Breach risk is decreasing. Current improvements are working.'
  return 'Breach risk is stable. Monitor for changes.'
}

// Function: RiskSummaryPanel
function RiskSummaryPanel({ data }) {
  return (
    <div className="card-modern p-6">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-4 h-4 text-accent-rose" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Risk Summary</h2>
      </div>
      <div className="space-y-4">
        <div>
          <p className="text-xs text-slate-400 mb-2">Breach Risk Category</p>
          <div className="flex items-center justify-between">
            <span className="text-sm">{breachCategoryLabel(data.current_breach_risk_pct)}</span>
            <div className="w-32 h-2 rounded-full bg-slate-700 overflow-hidden">
              <div
                className={`h-full transition-all ${breachBarColor(data.current_breach_risk_pct)}`}
                style={{ width: `${Math.min(100, data.current_breach_risk_pct)}%` }}
              />
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-700/30 space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Trajectory Status:</span>
            <span className="font-semibold text-amber-300">{trajectoryDisplayLabel(data.trajectory)}</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            {trajectoryDescription(data.trajectory)}
          </p>
        </div>
      </div>
    </div>
  )
}

// Function: RecommendedActionsPanel
function RecommendedActionsPanel({ data }) {
  return (
    <div className="card-modern p-6 animate-slide-up">
      <div className="flex items-center gap-2 mb-4">
        <CheckCircle className="w-4 h-4 text-accent-emerald" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Recommended Actions</h2>
      </div>
      <ul className="space-y-3 text-xs text-slate-300">
        {data.breached_tickets > 0 && (
          <li className="flex items-start gap-2 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
            <span>
              <strong>{data.breached_tickets} tickets</strong> have breached SLA. Prepare customer communications and determine next steps.
            </span>
          </li>
        )}
        {data.at_risk_tickets > 5 && (
          <li className="flex items-start gap-2 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
            <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <span>
              <strong>{data.at_risk_tickets} tickets</strong> are approaching SLA limits. Prioritize assignments and escalate if needed.
            </span>
          </li>
        )}
        {data.trajectory === 'deteriorating' && (
          <li className="flex items-start gap-2 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <span>
              Breach risk is <strong>trending upward</strong>. Review assignment patterns, staffing, and workload distribution.
            </span>
          </li>
        )}
        {data.breached_tickets === 0 && data.at_risk_tickets <= 5 && data.trajectory !== 'deteriorating' && (
          <li className="flex items-start gap-2 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
            <span>SLA performance is healthy. Continue monitoring and maintain current practices.</span>
          </li>
        )}
      </ul>
    </div>
  )
}

// Function: SLAKPIDashboard
export default function SLAKPIDashboard() {
  const { synced, dateRange } = useDashboard()
  const printRef = useRef(null)
  const [slaData, setSLAData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [drawer, setDrawer] = useState({ open: false, chartType: null, title: '' })

  // Function: openDrawer
  function openDrawer(chartType, title) {
    setDrawer({ open: true, chartType, title })
  }

  // Function: closeDrawer
  function closeDrawer() {
    setDrawer((d) => ({ ...d, open: false }))
  }

  const fetchData = useCallback(async () => {
    try {
      const res = await getSLABreachRisk(12, dateRange)
      setSLAData(res.data)
    } catch (e) {
      console.error('Failed to load SLA/KPI data', e)
    } finally {
      setLoading(false)
    }
  }, [dateRange])

  useEffect(() => {
    if (synced) {
      fetchData()
    }
  }, [synced, fetchData, dateRange])

  const data = slaData || {}

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
      {/* Header */}
      <div className="mb-8 animate-fade-in flex items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-lg gradient-bg-primary shadow-glow-md">
              <Target className="w-7 h-7 text-white" />
            </div>
            SLA / KPI Dashboard — Live Performance Tracking
          </h1>
          <p className="text-sm text-slate-400 mt-3">
            Real-time SLA compliance, breach risk indicators, and trajectory analysis
          </p>
        </div>
        <ExportPDFButton printRef={printRef} title="SLA KPI Dashboard" />
      </div>

      <TopKPIsRow loading={loading} data={data} openDrawer={openDrawer} />

      {/* SLA Trend + Breach Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 animate-slide-up">
        <BreachTrendPanel loading={loading} data={data} />
        <RiskSummaryPanel data={data} />
      </div>

      <RecommendedActionsPanel data={data} />

      <DrilldownDrawer
        open={drawer.open}
        onClose={closeDrawer}
        title={drawer.title}
        chartType={drawer.chartType}
        data={data}
      />
    </div>
  )
}
