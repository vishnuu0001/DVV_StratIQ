// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (TransformationAutomationDashboard.jsx)
// Date: 2025-11-23
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Zap,
  TrendingUp,
  Target,
  DollarSign,
  Gauge,
  ArrowUp,
  CheckCircle,
  Lightbulb,
} from 'lucide-react'
import { getTransformationKpis } from '../api'
import { useDashboard } from '../context/DashboardContext'
import ExportPDFButton from '../components/ExportPDFButton'
import DrilldownDrawer from '../components/DrilldownDrawer'

// Function: StatCard
function StatCard({ title, value, unit = '', icon: Icon, color = 'cyan', trend = null, onClick }) {
  const colorMap = {
    cyan: 'text-accent-cyan bg-cyan-500/10 border-cyan-500/20',
    emerald: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/20',
    amber: 'text-amber-300 bg-amber-500/10 border-amber-500/20',
    indigo: 'text-indigo-300 bg-indigo-500/10 border-indigo-500/20',
    rose: 'text-rose-300 bg-rose-500/10 border-rose-500/20',
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left card-modern p-5 border ${colorMap[color]} hover:-translate-y-0.5 transition-all ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-2">{title}</p>
          <p className="text-4xl font-bold">
            {value}
            <span className="text-sm font-normal text-slate-400 ml-1">{unit}</span>
          </p>
          {trend && <p className="text-xs text-slate-500 mt-2">{trend}</p>}
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

// Function: OpportunityCard
function OpportunityCard({ type, count, potential }) {
  return (
    <div className="p-4 rounded-lg bg-slate-700/20 border border-slate-600/30 hover:border-slate-500/40 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-white truncate">{type}</h3>
          <p className="text-xs text-slate-400 mt-1">{count} requests</p>
        </div>
        <div className={`px-2 py-1 rounded text-xs font-bold ${
          potential === 'High' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
        }`}>
          {potential}
        </div>
      </div>
      <div className="w-full h-1.5 rounded-full bg-slate-700 overflow-hidden">
        <div
          className={`h-full ${potential === 'High' ? 'bg-emerald-500' : 'bg-amber-500'}`}
          style={{ width: `${Math.min(100, (count / 50) * 100)}%` }}
        />
      </div>
    </div>
  )
}

// Function: PrimaryMetricsRow
function PrimaryMetricsRow({ loading, transformData, openDrawer }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-slide-up">
      <StatCard
        title="Automation %"
        value={loading ? '—' : transformData.automation_pct || 0}
        unit="%"
        icon={Zap}
        color="cyan"
        trend="of all tickets automated"
        onClick={() => openDrawer('transformation-kpis', 'Automation % — L2 / L3')}
      />
      <StatCard
        title="Effort Reduction"
        value={loading ? '—' : transformData.effort_reduction_pct || 0}
        unit="%"
        icon={TrendingUp}
        color="emerald"
        trend="vs. manual resolution"
        onClick={() => openDrawer('transformation-kpis', 'Effort Reduction — L2 / L3')}
      />
      <StatCard
        title="Incident Deflection"
        value={loading ? '—' : transformData.incident_deflection_pct || 0}
        unit="%"
        icon={Target}
        color="amber"
        trend="requests vs incidents"
        onClick={() => openDrawer('transformation-kpis', 'Incident Deflection — L2 / L3')}
      />
      <StatCard
        title="Cost Take-Out"
        value={loading ? '—' : `$${transformData.cost_takeout_estimate || 0}`}
        unit="k"
        icon={DollarSign}
        color="indigo"
        trend="estimated annual savings"
        onClick={() => openDrawer('transformation-kpis', 'Cost Take-Out — L2 / L3')}
      />
    </div>
  )
}

// Function: TransformationImpactRow
function TransformationImpactRow({ loading, transformData }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-slide-up">
      <div className="card-modern p-6">
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle className="w-4 h-4 text-accent-emerald" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Automation Impact</h2>
        </div>
        <div className="space-y-4">
          <div>
            <p className="text-xs text-slate-400 mb-2">Automation Adoption</p>
            <div className="text-3xl font-bold text-accent-cyan">{loading ? '—' : `${transformData.automation_pct || 0}%`}</div>
            <p className="text-xs text-slate-500 mt-1">Percentage of tickets handled by automation</p>
          </div>
          <div className="pt-4 border-t border-slate-700/30">
            <p className="text-xs text-slate-400 mb-2">Time Savings Per Ticket</p>
            <div className="text-2xl font-bold text-emerald-400">10h</div>
            <p className="text-xs text-slate-500 mt-1">Automated: 2h vs. Manual: 12h</p>
          </div>
        </div>
      </div>

      <div className="card-modern p-6">
        <div className="flex items-center gap-2 mb-4">
          <ArrowUp className="w-4 h-4 text-accent-amber" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Effort Reduction</h2>
        </div>
        <div className="space-y-4">
          <div>
            <p className="text-xs text-slate-400 mb-2">Manual Effort Eliminated</p>
            <div className="text-3xl font-bold text-amber-300">{loading ? '—' : `${transformData.effort_reduction_pct || 0}%`}</div>
            <p className="text-xs text-slate-500 mt-1">Across all ticket types</p>
          </div>
          <div className="pt-4 border-t border-slate-700/30">
            <p className="text-xs text-slate-400 mb-2">Estimated Staff Hours Freed</p>
            <div className="text-2xl font-bold text-amber-300">1,240h</div>
            <p className="text-xs text-slate-500 mt-1">Available for strategic work</p>
          </div>
        </div>
      </div>

      <div className="card-modern p-6">
        <div className="flex items-center gap-2 mb-4">
          <DollarSign className="w-4 h-4 text-accent-indigo" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Cost Impact</h2>
        </div>
        <div className="space-y-4">
          <div>
            <p className="text-xs text-slate-400 mb-2">Annual Cost Take-Out</p>
            <div className="text-3xl font-bold text-indigo-300">${loading ? '—' : transformData.cost_takeout_estimate || 0}k</div>
            <p className="text-xs text-slate-500 mt-1">Through automation and efficiency</p>
          </div>
          <div className="pt-4 border-t border-slate-700/30">
            <p className="text-xs text-slate-400 mb-2">Cost Per Ticket Saved</p>
            <div className="text-2xl font-bold text-indigo-300">$250</div>
            <p className="text-xs text-slate-500 mt-1">Reduced manual handling</p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Function: AutomationOpportunitiesPanel
function AutomationOpportunitiesPanel({ loading, transformData }) {
  const opportunities = transformData.automation_opportunities || []
  return (
    <div className="card-modern p-6">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-4 h-4 text-accent-amber" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Top Automation Opportunities</h2>
      </div>
      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => <div key={i} className="h-16 rounded skeleton" />)}
        </div>
      ) : opportunities.length > 0 ? (
        <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
          {opportunities.map((opp, i) => (
            <OpportunityCard key={i} type={opp.type} count={opp.count} potential={opp.automation_potential} />
          ))}
        </div>
      ) : (
        <p className="text-xs text-slate-500 italic">No automation opportunities identified yet.</p>
      )}
    </div>
  )
}

// Function: DeflectionAndOpportunitiesRow
function DeflectionAndOpportunitiesRow({ loading, transformData }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 animate-slide-up">
      <div className="card-modern p-6">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-4 h-4 text-accent-rose" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Incident Deflection</h2>
        </div>
        <div className="space-y-4">
          <div className="text-center py-6">
            <div className="text-5xl font-bold gradient-text">{loading ? '—' : `${transformData.incident_deflection_pct || 0}%`}</div>
            <p className="text-xs text-slate-400 mt-2">Service Requests vs. Incidents Ratio</p>
          </div>
          <div className="pt-4 border-t border-slate-700/30">
            <p className="text-xs text-slate-400 mb-3">Deflection Strategy:</p>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Improved self-service capabilities
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Knowledge base optimization
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Automated ticket classification
              </li>
            </ul>
          </div>
        </div>
      </div>

      <AutomationOpportunitiesPanel loading={loading} transformData={transformData} />
    </div>
  )
}

// Function: EvidenceSection
function EvidenceSection() {
  return (
    <div className="card-modern p-6 animate-slide-up">
      <div className="flex items-center gap-2 mb-4">
        <Gauge className="w-4 h-4 text-accent-cyan" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Evidence & Linked Metrics</h2>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
        <div className="p-4 rounded-lg bg-slate-700/20 border border-slate-600/30">
          <p className="text-xs text-slate-400 mb-1">Scripts & Workflows</p>
          <p className="text-2xl font-bold text-accent-cyan">12</p>
          <p className="text-xs text-slate-500 mt-1">Active automation workflows</p>
        </div>
        <div className="p-4 rounded-lg bg-slate-700/20 border border-slate-600/30">
          <p className="text-xs text-slate-400 mb-1">Documented Procedures</p>
          <p className="text-2xl font-bold text-accent-emerald">25</p>
          <p className="text-xs text-slate-500 mt-1">Linked to automation projects</p>
        </div>
        <div className="p-4 rounded-lg bg-slate-700/20 border border-slate-600/30">
          <p className="text-xs text-slate-400 mb-1">ROI Tracking</p>
          <p className="text-2xl font-bold text-accent-amber">$450k</p>
          <p className="text-xs text-slate-500 mt-1">YTD value realization</p>
        </div>
      </div>
    </div>
  )
}

// Function: TransformationAutomationDashboard
export default function TransformationAutomationDashboard() {
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
      const res = await getTransformationKpis(dateRange)
      setData(res.data)
    } catch (e) {
      console.error('Failed to load transformation KPIs', e)
    } finally {
      setLoading(false)
    }
  }, [dateRange])

  useEffect(() => {
    if (synced) {
      fetchData()
    }
  }, [synced, fetchData, dateRange])

  const transformData = data || {}

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
      {/* Header */}
      <div className="mb-8 animate-fade-in flex items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-lg gradient-bg-primary shadow-glow-md">
              <Zap className="w-7 h-7 text-white" />
            </div>
            Transformation & Automation Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-3">
            Track automation adoption, effort reduction, incident deflection, and cost take-out metrics
          </p>
        </div>
        <ExportPDFButton printRef={printRef} title="Transformation Dashboard" />
      </div>

      <PrimaryMetricsRow loading={loading} transformData={transformData} openDrawer={openDrawer} />

      <TransformationImpactRow loading={loading} transformData={transformData} />

      <DeflectionAndOpportunitiesRow loading={loading} transformData={transformData} />

      <EvidenceSection />

      <DrilldownDrawer
        open={drawer.open}
        onClose={closeDrawer}
        title={drawer.title}
        chartType={drawer.chartType}
        data={transformData}
      />
    </div>
  )
}
