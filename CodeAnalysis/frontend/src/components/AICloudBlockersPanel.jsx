// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * AICloudBlockersPanel.jsx — Cloud migration readiness with charts
// Date: 2026-03-17
// ---------------------------------------------------------------------------
/**
 * AICloudBlockersPanel.jsx — Cloud migration readiness with charts
 */
import { useState } from 'react'
import { Cloud, ShieldAlert, Layers, CheckCheck, Clock } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, RadarChart, PolarGrid, PolarAngleAxis, Radar,
} from 'recharts'
import AIDetailModal from './AIDetailModal.jsx'

const SEV_COLOR = { critical: '#ef4444', high: '#f97316', medium: '#f59e0b', low: '#22c55e' }
const SCls = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high:     'bg-orange-100 text-orange-700 border-orange-200',
  medium:   'bg-yellow-100 text-yellow-700 border-yellow-200',
  low:      'bg-green-100 text-green-700 border-green-200',
}
const READINESS_BADGE = {
  ready:          'bg-green-100 text-green-700',
  needs_work:     'bg-yellow-100 text-yellow-700',
  major_refactor: 'bg-orange-100 text-orange-700',
  not_ready:      'bg-red-100 text-red-700',
}
const READINESS_SCORE = { ready: 90, needs_work: 55, major_refactor: 30, not_ready: 10 }

// Function: TIP
const TIP = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg px-3 py-2 text-xs">
      <p className="font-semibold text-blue-700 mb-1 max-w-[180px] truncate">{label}</p>
      {payload.map((p, i) => <p key={i} style={{ color: p.fill || p.color }}>{p.name}: <strong>{p.value}</strong></p>)}
    </div>
  )
}

// Function: AICloudBlockersPanel
export default function AICloudBlockersPanel({ data }) {
  if (!data) return null
  if (data.error) return <div className="bg-white rounded-2xl shadow p-6 text-red-500 text-sm">{data.error}</div>

  const blockers = data.blockers         || []
  const phases   = data.migration_phases || []

  const [modal, setModal] = useState(null)
  // Function: openBlockers
  const openBlockers = (filterFn, label) =>
    setModal({ type: 'blocker', title: label, items: filterFn ? blockers.filter(filterFn) : blockers })
  // Function: openPhases
  const openPhases = (label) =>
    setModal({ type: 'phase', title: label, items: phases.map(p => ({ ...p, _panelColor: 'indigo' })) })

  // Severity distribution
  const sevCounts = blockers.reduce((a, b) => { a[b.severity] = (a[b.severity] || 0) + 1; return a }, {})
  const pieData = Object.entries(sevCounts).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1), value, color: SEV_COLOR[name] || '#94a3b8'
  }))

  // Effort per blocker bar
  const barData = blockers
    .filter(b => b.effort_days > 0)
    .sort((a, b) => (b.effort_days || 0) - (a.effort_days || 0))
    .map(b => ({ name: b.title?.slice(0, 22) || '?', effort: b.effort_days || 0, fill: SEV_COLOR[b.severity] || '#94a3b8', _original: b }))

  const readinessScore = READINESS_SCORE[data.migration_readiness] || 0
  const totalEffort    = blockers.reduce((s, b) => s + (b.effort_days || 0), 0)

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">

      {/* Header with readiness meter */}
      <div className="bg-white rounded-2xl shadow p-6">
        <div className="flex items-center gap-2 mb-3">
          <Cloud size={18} className="text-blue-500" />
          <h3 className="font-semibold text-blue-800">Cloud Migration Intelligence</h3>
          <span className={`ml-auto text-xs font-bold px-2 py-0.5 rounded ${READINESS_BADGE[data.migration_readiness] || 'bg-gray-100 text-blue-600'}`}>
            {(data.migration_readiness || '').replace('_', ' ').toUpperCase()}
          </span>
        </div>
        <p className="text-sm text-blue-700 mb-4">{data.summary}</p>

        {/* Readiness gauge bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-blue-500 mb-1">
            <span>Migration Readiness</span><span>{readinessScore}%</span>
          </div>
          <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: readinessScore >= 70 ? '#22c55e' : readinessScore >= 40 ? '#f59e0b' : '#ef4444' }}
              initial={{ width: 0 }} animate={{ width: `${readinessScore}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <button onClick={() => openBlockers(b => b.severity === 'critical', 'Critical Blockers')} className="bg-red-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-red-300 transition-all">
            <div className="text-2xl font-bold text-red-600">{sevCounts.critical || 0}</div>
            <div className="text-xs text-blue-500 mt-1">Critical</div>
          </button>
          <button onClick={() => openBlockers(null, 'All Blockers')} className="bg-orange-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-orange-300 transition-all">
            <div className="text-2xl font-bold text-orange-600">{blockers.length}</div>
            <div className="text-xs text-blue-500 mt-1">Total blockers</div>
          </button>
          <button onClick={() => openBlockers(b => b.effort_days > 0, `Blockers (${totalEffort} days)`)} className="bg-blue-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-blue-300 transition-all">
            <div className="text-2xl font-bold text-blue-600">{totalEffort}</div>
            <div className="text-xs text-blue-500 mt-1">Days to fix</div>
          </button>
        </div>

        {data.target_architecture && (
          <div className="mt-4 p-3 bg-blue-50 rounded-xl text-sm text-blue-800">
            <strong>Target Architecture:</strong> {typeof data.target_architecture === 'object' ? (data.target_architecture.guidance || JSON.stringify(data.target_architecture)) : data.target_architecture}
          </div>
        )}
        {data.containerisation_strategy && (
          <div className="mt-2 p-3 bg-indigo-50 rounded-xl text-sm text-indigo-800">
            <strong>Containerisation:</strong> {typeof data.containerisation_strategy === 'object' ? (data.containerisation_strategy.guidance || data.containerisation_strategy.base_image || JSON.stringify(data.containerisation_strategy)) : data.containerisation_strategy}
          </div>
        )}
      </div>

      {/* Charts row */}
      {(barData.length > 0 || pieData.length > 0) && (
        <div className="grid md:grid-cols-3 gap-5">
          {barData.length > 0 && (
            <div className="md:col-span-2 bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <Clock size={14} className="text-blue-500" /> Effort to Resolve (days)
              </h3>
              <ResponsiveContainer width="100%" height={210}>
                <BarChart data={barData} layout="vertical" margin={{ left: 4, right: 28, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                  <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <Tooltip content={<TIP />} />
                  <Bar dataKey="effort" name="Days" radius={[0, 4, 4, 0]} maxBarSize={18}
                    onClick={(d) => d._original && setModal({ type: 'blocker', title: d.name, items: blockers, initialItem: d._original })} style={{ cursor: 'pointer' }}>
                    {barData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {pieData.length > 0 && (
            <div className="bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <ShieldAlert size={14} className="text-red-500" /> Severity Mix
              </h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="44%" innerRadius={50} outerRadius={74} paddingAngle={3} dataKey="value"
                    onClick={(d) => openBlockers(b => (b.severity || '').toLowerCase() === d.name.toLowerCase(), `${d.name} Blockers`)}
                    style={{ cursor: 'pointer' }}>
                    {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                  </Pie>
                  <Tooltip formatter={(v, n) => [v + ' blockers', n]} />
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Blockers */}
      {blockers.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <ShieldAlert size={16} className="text-red-500" />
            <h3 className="font-semibold text-blue-800">Blockers ({blockers.length})</h3>
          </div>
          <div className="space-y-3">
            {blockers.map((b, i) => {
              const sc = SCls[b.severity] || 'border-gray-200 bg-white text-blue-700'
              return (
                <button key={i} onClick={() => setModal({ type: 'blocker', title: b.title, items: blockers, initialItem: b })}
                  className={`w-full text-left border rounded-xl p-4 ${sc} hover:shadow-md hover:scale-[1.01] transition-all`}>
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="font-semibold text-sm">{b.title}</span>
                    <span className={`text-xs px-2 py-0.5 rounded font-bold ${sc}`}>{(b.severity || '').toUpperCase()}</span>
                    {b.effort_days && <span className="ml-auto text-xs opacity-70">~{b.effort_days}d</span>}
                  </div>
                  <p className="text-xs mb-1 opacity-80">{b.description}</p>
                  <p className="text-xs font-medium">Fix: {b.remediation}</p>
                  {(b.impacted_files_pattern || b.impacted_pattern) && (
                    <code className="text-xs opacity-70 block mt-1">{b.impacted_files_pattern || b.impacted_pattern}</code>
                  )}
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Migration phases */}
      {phases.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Layers size={16} className="text-indigo-500" />
            <h3 className="font-semibold text-blue-800">Migration Phases</h3>
            <button onClick={() => openPhases('Migration Phases')} className="ml-auto text-xs text-indigo-500 hover:text-indigo-700 underline underline-offset-2">View all</button>
          </div>
          <div className="space-y-3">
            {phases.map((ph, i) => (
              <button key={i} onClick={() => setModal({ type: 'phase', title: ph.title || `Phase ${ph.phase}`, items: phases.map(p => ({ ...p, _panelColor: 'indigo' })), initialItem: { ...ph, _panelColor: 'indigo' } })}
                className="w-full text-left border border-gray-100 rounded-xl p-4 hover:bg-indigo-50/50 hover:border-indigo-200 transition-colors">
                <div className="flex items-center gap-3 mb-2">
                  <span className="w-7 h-7 rounded-full bg-indigo-600 text-blue-300 text-xs font-bold flex items-center justify-center shrink-0">
                    {ph.phase}
                  </span>
                  <span className="font-semibold text-sm text-blue-800">{ph.title}</span>
                  {ph.duration_weeks && (
                    <span className="ml-auto text-xs text-blue-400">{ph.duration_weeks}w</span>
                  )}
                </div>
                <ul className="space-y-1 pl-10">
                  {(ph.tasks || []).map((t, j) => (
                    <li key={j} className="text-xs text-blue-600 flex gap-1.5">
                      <CheckCheck size={12} className="text-green-400 mt-0.5 shrink-0" />{t}
                    </li>
                  ))}
                </ul>
              </button>
            ))}
          </div>
        </div>
      )}
      <AnimatePresence>
        {modal && <AIDetailModal {...modal} onClose={() => setModal(null)} />}
      </AnimatePresence>
    </motion.div>
  )
}
