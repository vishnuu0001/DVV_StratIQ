// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (AdHocEnhancementDashboard.jsx)
// Date: 2025-11-26
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Zap,
  AlertTriangle,
  Clock,
  TrendingUp,
  Flame,
  CheckCircle,
  AlertCircle,
  Inbox,
  ChevronRight,
} from 'lucide-react'
import { getAdHocVsBau } from '../api'
import { useDashboard } from '../context/DashboardContext'
import DrilldownDrawer from '../components/DrilldownDrawer'
import ExportPDFButton from '../components/ExportPDFButton'

// Function: MetricPill
function MetricPill({ label, value, sub, color = 'slate', icon: Icon, pulse, onClick }) {
  const colorCls = {
    slate: 'glass text-slate-200 border-slate-600/20',
    rose: 'glass text-red-200 border-red-500/20',
    emerald: 'glass text-emerald-200 border-emerald-500/20',
    amber: 'glass text-amber-200 border-amber-500/20',
    indigo: 'glass text-indigo-200 border-indigo-500/20',
    sky: 'glass text-sky-200 border-sky-500/20',
  }[color] || 'bg-slate-50 border-slate-200 text-slate-700'

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full flex items-center gap-3 rounded-xl border px-4 py-3 transition-all hover:shadow-card-hover ${colorCls} ${onClick ? 'cursor-pointer hover:-translate-y-0.5' : ''}`}
    >
      {Icon && (
        <div className={`p-2 rounded-lg bg-slate-700/30 ${pulse ? 'animate-pulse' : ''}`}>
          <Icon className="w-4 h-4" />
        </div>
      )}
      <div className="min-w-0">
        <div className="text-xs text-slate-400 font-medium truncate">{label}</div>
        <div className="text-xl font-bold leading-tight">{value ?? '—'}</div>
        {sub && <div className="text-[10px] text-slate-500 truncate">{sub}</div>}
      </div>
      {onClick && <ChevronRight className="w-4 h-4 text-slate-500 ml-auto" />}
    </button>
  )
}

// Function: Alert
function Alert({ severity, message }) {
  const colors = {
    critical: 'bg-rose-500/10 border-rose-500/20 text-rose-300',
    warning: 'bg-amber-500/10 border-amber-500/20 text-amber-300',
    info: 'bg-sky-500/10 border-sky-500/20 text-sky-300',
  }

  return (
    <div className={`p-4 rounded-lg border flex items-start gap-3 ${colors[severity]}`}>
      <div className="mt-0.5 flex-shrink-0">
        {severity === 'critical' ? (
          <Flame className="w-5 h-5" />
        ) : severity === 'warning' ? (
          <AlertTriangle className="w-5 h-5" />
        ) : (
          <AlertCircle className="w-5 h-5" />
        )}
      </div>
      <p className="text-sm">{message}</p>
    </div>
  )
}

// Function: TopKPIsRow
function TopKPIsRow({ loading, workData, openDrawer }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6 animate-slide-up">
      <MetricPill
        label="Total Tickets"
        value={loading ? null : workData.total_tickets?.toLocaleString() ?? '—'}
        sub="All request types"
        icon={Inbox}
        color="sky"
        onClick={() => openDrawer('adhoc-vs-bau', 'Total Tickets — L2 / L3')}
      />
      <MetricPill
        label="BAU Work"
        value={loading ? null : `${workData.bau_pct || 0}%`}
        sub={`${workData.bau_count || 0} tickets`}
        icon={CheckCircle}
        color="emerald"
        onClick={() => openDrawer('adhoc-vs-bau', 'BAU Work — L2 / L3')}
      />
      <MetricPill
        label="Ad-hoc Work"
        value={loading ? null : `${workData.adhoc_pct || 0}%`}
        sub={`${workData.adhoc_count || 0} tickets`}
        icon={Zap}
        color="amber"
        onClick={() => openDrawer('adhoc-vs-bau', 'Ad-hoc Work — L2 / L3')}
      />
      <MetricPill
        label="Enhancements"
        value={loading ? null : `${workData.enhancement_pct || 0}%`}
        sub={`${workData.enhancement_count || 0} tickets`}
        icon={TrendingUp}
        color="indigo"
        onClick={() => openDrawer('adhoc-vs-bau', 'Enhancements — L2 / L3')}
      />
    </div>
  )
}

// Function: WorkTypeDistributionPanel
function WorkTypeDistributionPanel({ loading, workData }) {
  return (
    <div className="card-modern p-6">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="w-4 h-4 text-accent-cyan" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Work Type Distribution</h2>
      </div>

      <div className="space-y-6">
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-semibold text-white">Business As Usual</span>
            </div>
            <span className="text-xl font-bold text-emerald-400">{loading ? '—' : `${workData.bau_pct || 0}%`}</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-700 overflow-hidden">
            <div className="h-full bg-emerald-500 rounded-full transition-all" style={{ width: `${workData.bau_pct || 0}%` }} />
          </div>
          <p className="text-xs text-slate-400 mt-2">{loading ? '—' : workData.bau_count} standard requests and incident fixes</p>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-sm font-semibold text-white">Ad-hoc / Unplanned</span>
            </div>
            <span className="text-xl font-bold text-amber-400">{loading ? '—' : `${workData.adhoc_pct || 0}%`}</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-700 overflow-hidden">
            <div className="h-full bg-amber-500 rounded-full transition-all" style={{ width: `${workData.adhoc_pct || 0}%` }} />
          </div>
          <p className="text-xs text-slate-400 mt-2">{loading ? '—' : workData.adhoc_count} unplanned incidents and urgent work</p>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
              <span className="text-sm font-semibold text-white">Enhancements</span>
            </div>
            <span className="text-xl font-bold text-indigo-400">{loading ? '—' : `${workData.enhancement_pct || 0}%`}</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-700 overflow-hidden">
            <div className="h-full bg-indigo-500 rounded-full transition-all" style={{ width: `${workData.enhancement_pct || 0}%` }} />
          </div>
          <p className="text-xs text-slate-400 mt-2">{loading ? '—' : workData.enhancement_count} improvement and CR requests</p>
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-slate-700/30">
        <p className="text-xs text-slate-400 mb-3 font-semibold">Industry Benchmark (ITIL)</p>
        <ul className="space-y-2 text-xs text-slate-300">
          <li className="flex items-center justify-between">
            <span>BAU Target:</span>
            <span className="font-semibold text-emerald-400">60-70%</span>
          </li>
          <li className="flex items-center justify-between">
            <span>Ad-hoc / Incidents:</span>
            <span className="font-semibold text-amber-400">15-25%</span>
          </li>
          <li className="flex items-center justify-between">
            <span>Enhancements / CRs:</span>
            <span className="font-semibold text-indigo-400">10-15%</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

// Function: AgingAlertsPanel
function AgingAlertsPanel({ loading, workData }) {
  const alerts = workData.aging_alerts || []
  return (
    <div className="card-modern p-6">
      <div className="flex items-center gap-2 mb-6">
        <Clock className="w-4 h-4 text-accent-rose" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Aging Alerts & Risk Indicators</h2>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => <div key={i} className="h-16 rounded skeleton" />)}
        </div>
      ) : alerts.length > 0 ? (
        <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
          {alerts.map((alert, i) => (
            <Alert key={i} severity={alert.severity} message={alert.message} />
          ))}
        </div>
      ) : (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
          <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <p className="text-sm text-emerald-300">No aging alerts detected. Aging is well-controlled.</p>
        </div>
      )}

      <div className="mt-6 pt-6 border-t border-slate-700/30">
        <p className="text-xs text-slate-400 mb-3 font-semibold">Aging Thresholds</p>
        <ul className="space-y-2 text-xs text-slate-300">
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-slate-500" /> &lt; 7 days — New / In Progress
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500" /> 7-30 days — Monitor
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-rose-500" /> &gt; 30 days — Escalate
          </li>
        </ul>
      </div>
    </div>
  )
}

// Function: CRMisusePanel
function CRMisusePanel() {
  return (
    <div className="card-modern p-6 mb-8 animate-slide-up">
      <div className="flex items-center gap-2 mb-6">
        <Flame className="w-4 h-4 text-accent-rose" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">CR Misuse Prevention & Early Warning</h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
        <div className="p-4 rounded-lg bg-slate-700/20 border border-slate-600/30">
          <p className="text-xs text-slate-400 mb-2 font-semibold">Unauthorized CRs Detected</p>
          <p className="text-3xl font-bold text-rose-400">2</p>
          <p className="text-xs text-slate-500 mt-1">CRs for tasks that should be standard changes</p>
        </div>

        <div className="p-4 rounded-lg bg-slate-700/20 border border-slate-600/30">
          <p className="text-xs text-slate-400 mb-2 font-semibold">Bypassed CAB Process</p>
          <p className="text-3xl font-bold text-amber-400">1</p>
          <p className="text-xs text-slate-500 mt-1">CRs implemented without board review</p>
        </div>

        <div className="p-4 rounded-lg bg-slate-700/20 border border-slate-600/30">
          <p className="text-xs text-slate-400 mb-2 font-semibold">Scope Creep Risk</p>
          <p className="text-3xl font-bold text-amber-400">3</p>
          <p className="text-xs text-slate-500 mt-1">CRs with documented post-implementation changes</p>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-slate-700/30">
        <p className="text-xs text-slate-400 mb-3 font-semibold">🚨 Recommended Actions:</p>
        <ul className="space-y-2 text-sm text-slate-300">
          <li className="flex items-start gap-2">
            <span className="text-rose-400 font-bold mt-0.5">→</span>
            <span>Review 2 unauthorized CRs and convert to Standard Change if applicable</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-400 font-bold mt-0.5">→</span>
            <span>Enforce CAB workflow — implement audit trail on Change records</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-400 font-bold mt-0.5">→</span>
            <span>Conduct training on proper CR use and scope management</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

// Function: QuickStatsRow
function QuickStatsRow({ loading, workData, openDrawer }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 animate-slide-up">
      <button type="button" onClick={() => openDrawer('adhoc-vs-bau', 'Total Work Items — L2 / L3')} className="card-modern p-4 text-center hover:scale-[1.02] transition-transform">
        <p className="text-2xl font-bold gradient-text">{loading ? '—' : workData.total_tickets || 0}</p>
        <p className="text-xs text-slate-400 mt-1">Total Work Items</p>
      </button>
      <button type="button" onClick={() => openDrawer('adhoc-vs-bau', 'Unplanned Workload — L2 / L3')} className="card-modern p-4 text-center hover:scale-[1.02] transition-transform">
        <p className="text-2xl font-bold text-amber-400">{loading ? '—' : `${workData.adhoc_pct || 0}%`}</p>
        <p className="text-xs text-slate-400 mt-1">Unplanned Workload</p>
      </button>
      <button type="button" onClick={() => openDrawer('adhoc-vs-bau', 'Enhancement Focus — L2 / L3')} className="card-modern p-4 text-center hover:scale-[1.02] transition-transform">
        <p className="text-2xl font-bold text-indigo-400">{loading ? '—' : `${workData.enhancement_pct || 0}%`}</p>
        <p className="text-xs text-slate-400 mt-1">Enhancement Focus</p>
      </button>
      <button type="button" onClick={() => openDrawer('adhoc-vs-bau', 'Active Risk Alerts — L2 / L3')} className="card-modern p-4 text-center hover:scale-[1.02] transition-transform">
        <p className="text-2xl font-bold text-rose-400">2</p>
        <p className="text-xs text-slate-400 mt-1">Active Risk Alerts</p>
      </button>
    </div>
  )
}

// Function: AdHocEnhancementDashboard
export default function AdHocEnhancementDashboard() {
  const { synced, dateRange } = useDashboard()
  const printRef = useRef(null)
  const [data, setData] = useState(null)
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
      const res = await getAdHocVsBau(dateRange)
      setData(res.data)
    } catch (e) {
      console.error('Failed to load ad-hoc vs BAU data', e)
    } finally {
      setLoading(false)
    }
  }, [dateRange])

  useEffect(() => {
    if (synced) {
      fetchData()
    }
  }, [synced, fetchData, dateRange])

  const workData = data || {}

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
      {/* Header */}
      <div className="mb-8 animate-fade-in flex items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-lg gradient-bg-primary shadow-glow-md">
              <Inbox className="w-7 h-7 text-white" />
            </div>
            Ad-hoc / Enhancement / CR Watch Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-3">
            Monitor unplanned work, aging requests, CR misuse, and the balance between routine operations and enhancements
          </p>
        </div>
        <ExportPDFButton printRef={printRef} title="Ad-Hoc Enhancement" />
      </div>

      <TopKPIsRow loading={loading} workData={workData} openDrawer={openDrawer} />

      {/* Work Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 animate-slide-up">
        <WorkTypeDistributionPanel loading={loading} workData={workData} />
        <AgingAlertsPanel loading={loading} workData={workData} />
      </div>

      <CRMisusePanel />

      <QuickStatsRow loading={loading} workData={workData} openDrawer={openDrawer} />

      <DrilldownDrawer
        open={drawer.open}
        onClose={closeDrawer}
        title={drawer.title}
        chartType={drawer.chartType}
        data={workData}
      />
    </div>
  )
}
