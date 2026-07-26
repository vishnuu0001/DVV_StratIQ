// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (PeopleCapacityDashboard.jsx)
// Date: 2025-09-14
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Users,
  TrendingUp,
  Briefcase,
  Gauge,
  AlertCircle,
  CheckCircle,
  GitBranch,
} from 'lucide-react'
import { getPeopleCapacity } from '../api'
import { useDashboard } from '../context/DashboardContext'
import DrilldownDrawer from '../components/DrilldownDrawer'
import ExportPDFButton from '../components/ExportPDFButton'

// Function: TeamCard
function TeamCard({ team, tickets, incidents, changes, serviceRequests }) {
  // Function: getLoad
  const getLoad = () => {
    if (tickets > 50) return { level: 'Overloaded', color: 'text-rose-400 bg-rose-500/20', bar: 'bg-rose-500' }
    if (tickets > 30) return { level: 'High', color: 'text-amber-400 bg-amber-500/20', bar: 'bg-amber-500' }
    if (tickets < 10) return { level: 'Low', color: 'text-sky-400 bg-sky-500/20', bar: 'bg-sky-500' }
    return { level: 'Optimal', color: 'text-emerald-400 bg-emerald-500/20', bar: 'bg-emerald-500' }
  }

  const load = getLoad()

  return (
    <div className="rounded-lg border border-slate-600/30 bg-slate-800/20 p-4 hover:border-slate-500/40 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-white truncate text-sm">{team}</h3>
        <div className={`px-2 py-1 rounded text-xs font-bold ${load.color}`}>{load.level}</div>
      </div>

      <div className="mb-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-400">Workload</span>
          <span className="font-semibold text-white">{tickets} tickets</span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-700 overflow-hidden">
          <div className={`h-full ${load.bar} transition-all`} style={{ width: `${Math.min(100, (tickets / 60) * 100)}%` }} />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-xs text-slate-300">
        <div className="p-2 rounded bg-slate-700/30 text-center">
          <p className="text-slate-400">Incidents</p>
          <p className="font-bold mt-1">{incidents}</p>
        </div>
        <div className="p-2 rounded bg-slate-700/30 text-center">
          <p className="text-slate-400">Changes</p>
          <p className="font-bold mt-1">{changes}</p>
        </div>
        <div className="p-2 rounded bg-slate-700/30 text-center">
          <p className="text-slate-400">SRs</p>
          <p className="font-bold mt-1">{serviceRequests}</p>
        </div>
      </div>
    </div>
  )
}

// Function: StatBox
function StatBox({ title, value, unit = '', icon: Icon, color = 'cyan', onClick }) {
  const colors = {
    cyan: 'text-accent-cyan bg-cyan-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
    indigo: 'text-indigo-400 bg-indigo-500/10',
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left p-4 rounded-lg border border-slate-600/30 ${colors[color]} hover:-translate-y-0.5 transition-all ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">{title}</p>
        {Icon && <Icon className="w-4 h-4" />}
      </div>
      <p className="text-3xl font-bold">
        {value}
        <span className="text-sm font-normal text-slate-400 ml-1">{unit}</span>
      </p>
    </button>
  )
}

// Function: KeyMetricsRow
function KeyMetricsRow({ loading, capacityData, openDrawer }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-slide-up">
      <StatBox
        title="Estimated Staff"
        value={loading ? '—' : capacityData.total_staff_estimated || 0}
        unit="people"
        icon={Users}
        color="cyan"
        onClick={() => openDrawer('people-capacity', 'Estimated Staff — L2 / L3')}
      />
      <StatBox
        title="Tickets/Person"
        value={loading ? '—' : capacityData.tickets_per_person?.toFixed(1) || 0}
        unit="avg"
        icon={Gauge}
        color="emerald"
        onClick={() => openDrawer('people-capacity', 'Tickets Per Person — L2 / L3')}
      />
      <StatBox
        title="Capacity Utilization"
        value={loading ? '—' : `${capacityData.capacity_utilization_pct || 0}%`}
        unit=""
        icon={TrendingUp}
        color={capacityData.capacity_utilization_pct > 80 ? 'amber' : 'indigo'}
        onClick={() => openDrawer('people-capacity', 'Capacity Utilization — L2 / L3')}
      />
      <StatBox
        title="Rebadged Resources"
        value={loading ? '—' : capacityData.rebadged_resources || 0}
        unit="active"
        icon={Briefcase}
        color="amber"
        onClick={() => openDrawer('people-capacity', 'Rebadged Resources — L2 / L3')}
      />
    </div>
  )
}

// Function: utilizationStrokeColor
function utilizationStrokeColor(pct) {
  if (pct > 80) return '#f97316'
  if (pct > 50) return '#fbbf24'
  return '#10b981'
}

// Function: utilizationMessage
function utilizationMessage(pct) {
  if (pct > 80) return '⚠️ Team is overloaded'
  if (pct > 50) return '✓ Optimal range'
  return '📈 Capacity available'
}

// Function: CapacityHealthPanel
function CapacityHealthPanel({ loading, capacityData }) {
  const pct = capacityData.capacity_utilization_pct || 0
  return (
    <div className="card-modern p-6">
      <div className="flex items-center gap-2 mb-4">
        <Gauge className="w-4 h-4 text-accent-indigo" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Capacity Health</h2>
      </div>

      <div className="space-y-6">
        <div className="text-center py-4">
          <div className="relative w-32 h-32 mx-auto mb-4">
            <svg className="w-full h-full" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="#334155" strokeWidth="8" />
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke={utilizationStrokeColor(pct)}
                strokeWidth="8"
                strokeDasharray={`${pct * 2.83} 283`}
                strokeDashoffset="0"
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <p className="text-3xl font-bold">{loading ? '—' : `${pct}%`}</p>
              <p className="text-xs text-slate-400 mt-1">Utilization</p>
            </div>
          </div>

          <p className="text-xs text-slate-400 mt-4">
            {loading ? '—' : utilizationMessage(pct)}
          </p>
        </div>

        <div className="pt-4 border-t border-slate-700/30">
          <p className="text-xs font-semibold text-slate-400 mb-2">Utilization Zones</p>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-sky-400" />
              &lt; 30% — Underutilized
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              30-70% — Optimal
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              70-85% — High Load
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-400" />
              &gt; 85% — Overloaded
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Function: TeamStructurePanel
function TeamStructurePanel({ loading, capacityData }) {
  return (
    <div className="card-modern p-6">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-4 h-4 text-accent-emerald" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Team Structure</h2>
      </div>

      <div className="space-y-4">
        <div>
          <p className="text-xs text-slate-400 mb-2">Estimated Team Size</p>
          <div className="text-4xl font-bold text-accent-emerald">{loading ? '—' : capacityData.total_staff_estimated || 0}</div>
          <p className="text-xs text-slate-500 mt-1">Assignment groups / teams</p>
        </div>

        <div className="pt-4 border-t border-slate-700/30">
          <p className="text-xs text-slate-400 mb-2">Average Team Size</p>
          <div className="text-2xl font-bold text-sky-400">{loading ? '—' : capacityData.avg_team_size || 0}</div>
          <p className="text-xs text-slate-500 mt-1">Per assignment group</p>
        </div>

        <div className="pt-4 border-t border-slate-700/30">
          <p className="text-xs text-slate-400 mb-2">Workload Per Person</p>
          <div className="text-2xl font-bold text-indigo-400">{loading ? '—' : capacityData.tickets_per_person?.toFixed(1) || 0}</div>
          <p className="text-xs text-slate-500 mt-1">Tickets per month per person</p>
        </div>
      </div>
    </div>
  )
}

// Function: ResourceStatusPanel
function ResourceStatusPanel({ loading, capacityData }) {
  return (
    <div className="card-modern p-6">
      <div className="flex items-center gap-2 mb-4">
        <Briefcase className="w-4 h-4 text-accent-amber" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Resource Status</h2>
      </div>

      <div className="space-y-4">
        <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20">
          <p className="text-xs text-slate-400 mb-1">Rebadged / Contract Resources</p>
          <div className="text-3xl font-bold text-amber-400">{loading ? '—' : capacityData.rebadged_resources || 0}</div>
          <p className="text-xs text-slate-500 mt-1">Currently active</p>
        </div>

        <div className="pt-4 border-t border-slate-700/30 space-y-2">
          <p className="text-xs font-semibold text-slate-400">Resource Mix</p>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Full-time</span>
            <span className="text-sky-400 font-bold">
              {loading ? '—' : (capacityData.total_staff_estimated || 0) - (capacityData.rebadged_resources || 0)}
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Contract/Rebadged</span>
            <span className="text-amber-400 font-bold">{loading ? '—' : capacityData.rebadged_resources || 0}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Function: TeamWorkloadPanel
function TeamWorkloadPanel({ loading, capacityData }) {
  const teams = capacityData.team_workload_distribution || []
  return (
    <div className="card-modern p-6 mb-8 animate-slide-up">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="w-4 h-4 text-accent-cyan" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Team Workload Distribution</h2>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => <div key={i} className="h-24 rounded skeleton" />)}
        </div>
      ) : teams.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto pr-2">
          {teams.map((team, i) => (
            <TeamCard
              key={i}
              team={team.team}
              tickets={team.total_tickets}
              incidents={team.incidents}
              changes={team.changes}
              serviceRequests={team.service_requests}
            />
          ))}
        </div>
      ) : (
        <p className="text-xs text-slate-500 italic">No team data available.</p>
      )}
    </div>
  )
}

// Function: UtilizationRecommendation
function UtilizationRecommendation({ pct }) {
  if (pct > 80) {
    return (
      <li className="flex items-start gap-3 p-3 bg-amber-500/10 border border-amber-500/20 rounded">
        <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <span>
          <strong>Team is overloaded.</strong> Consider hiring additional staff or implementing automation to reduce manual workload.
        </span>
      </li>
    )
  }
  if (pct < 30) {
    return (
      <li className="flex items-start gap-3 p-3 bg-sky-500/10 border border-sky-500/20 rounded">
        <AlertCircle className="w-5 h-5 text-sky-400 flex-shrink-0 mt-0.5" />
        <span>
          <strong>Spare capacity available.</strong> Use this opportunity for strategic projects, training, or technical debt reduction.
        </span>
      </li>
    )
  }
  return (
    <li className="flex items-start gap-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded">
      <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
      <span>
        <strong>Capacity is well-balanced.</strong> Team utilization is in the optimal range. Continue monitoring for changes.
      </span>
    </li>
  )
}

// Function: RecommendationsPanel
function RecommendationsPanel({ capacityData }) {
  return (
    <div className="card-modern p-6 animate-slide-up">
      <div className="flex items-center gap-2 mb-4">
        <CheckCircle className="w-4 h-4 text-accent-emerald" />
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Recommendations</h2>
      </div>

      <ul className="space-y-3 text-sm text-slate-300">
        <UtilizationRecommendation pct={capacityData.capacity_utilization_pct} />

        {(capacityData.rebadged_resources || 0) > 3 && (
          <li className="flex items-start gap-3 p-3 bg-amber-500/10 border border-amber-500/20 rounded">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <span>
              <strong>{capacityData.rebadged_resources} contract resources active.</strong> Plan transition strategy and knowledge transfer before contracts end.
            </span>
          </li>
        )}

        <li className="flex items-start gap-3 p-3 bg-indigo-500/10 border border-indigo-500/20 rounded">
          <GitBranch className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Review workload distribution:</strong> Ensure balanced assignments across teams. Consider cross-training for critical skills.
          </span>
        </li>
      </ul>
    </div>
  )
}

// Function: PeopleCapacityDashboard
export default function PeopleCapacityDashboard() {
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
      const res = await getPeopleCapacity(dateRange)
      setData(res.data)
    } catch (e) {
      console.error('Failed to load people & capacity data', e)
    } finally {
      setLoading(false)
    }
  }, [dateRange])

  useEffect(() => {
    if (synced) {
      fetchData()
    }
  }, [synced, fetchData, dateRange])

  const capacityData = data || {}

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
      {/* Header */}
      <div className="mb-8 animate-fade-in flex items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-lg gradient-bg-primary shadow-glow-md">
              <Users className="w-7 h-7 text-white" />
            </div>
            People & Capacity Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-3">
            Track team workload, resource utilization, capacity health, and rebadged resource allocation
          </p>
        </div>
        <ExportPDFButton printRef={printRef} title="People & Capacity" />
      </div>

      <KeyMetricsRow loading={loading} capacityData={capacityData} openDrawer={openDrawer} />

      {/* Capacity Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-slide-up">
        <CapacityHealthPanel loading={loading} capacityData={capacityData} />
        <TeamStructurePanel loading={loading} capacityData={capacityData} />
        <ResourceStatusPanel loading={loading} capacityData={capacityData} />
      </div>

      <TeamWorkloadPanel loading={loading} capacityData={capacityData} />

      <RecommendationsPanel capacityData={capacityData} />

      <DrilldownDrawer
        open={drawer.open}
        onClose={closeDrawer}
        title={drawer.title}
        chartType={drawer.chartType}
        data={capacityData}
      />
    </div>
  )
}
