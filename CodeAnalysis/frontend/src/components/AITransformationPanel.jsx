// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * AITransformationPanel.jsx — Modernisation roadmap with charts
// Date: 2025-09-30
// ---------------------------------------------------------------------------
/**
 * AITransformationPanel.jsx — Modernisation roadmap with charts
 */
import { useState } from 'react'
import { Rocket, ArrowRight, Calendar, TrendingUp, AlertTriangle, Layers } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import AIDetailModal from './AIDetailModal.jsx'

const CAT_COLOR_HEX = {
  framework: '#3b82f6', language: '#8b5cf6', database: '#f97316',
  messaging:  '#14b8a6', cloud: '#0ea5e9', security: '#ef4444',
}
const CAT_COLOR = {
  framework:  'bg-blue-100 text-blue-700',
  language:   'bg-purple-100 text-purple-700',
  database:   'bg-orange-100 text-orange-700',
  messaging:  'bg-teal-100 text-teal-700',
  cloud:      'bg-sky-100 text-sky-700',
  security:   'bg-red-100 text-red-700',
}
const RISK_COLOR = { low: 'text-green-600', medium: 'text-yellow-600', high: 'text-red-600' }
const MATURITY_BADGE = {
  legacy:        'bg-red-100 text-red-700',
  dated:         'bg-orange-100 text-orange-700',
  modern:        'bg-blue-100 text-blue-700',
  'cloud-native':'bg-green-100 text-green-700',
}

// Function: TIP
const TIP = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow px-3 py-2 text-xs">
      <p className="font-semibold text-blue-700 mb-1 max-w-[180px] truncate">{label}</p>
      {payload.map((p, i) => <p key={i} style={{ color: p.fill || p.color }}>{p.name}: <strong>{p.value}</strong></p>)}
    </div>
  )
}

// Function: AITransformationPanel
export default function AITransformationPanel({ data }) {
  if (!data) return null
  if (data.error) return <div className="bg-white rounded-2xl shadow p-6 text-red-500 text-sm">{data.error}</div>

  const paths  = data.transformation_paths || []
  const phases = data.modernisation_phases || []

  const [modal, setModal] = useState(null)
  // Function: openPaths
  const openPaths = (filterFn, label) =>
    setModal({ type: 'transform', title: label, items: filterFn ? paths.filter(filterFn) : paths })
  // Function: openPhases
  const openPhases = () =>
    setModal({ type: 'phase', title: 'Modernisation Phases', items: phases.map(p => ({ ...p, _panelColor: 'sky' })) })

  // Value score bar chart for paths
  const valueData = paths
    .filter(p => p.value_score != null)
    .sort((a, b) => (b.value_score || 0) - (a.value_score || 0))
    .map(p => ({
      name: `${p.current || '?'} → ${p.recommended || '?'}`?.slice(0, 26),
      score: p.value_score || 0,
      fill: CAT_COLOR_HEX[p.category] || '#6366f1',      _original: p,    }))

  // Category pie
  const catCounts = paths.reduce((a, p) => { a[p.category || 'other'] = (a[p.category || 'other'] || 0) + 1; return a }, {})
  const catPie = Object.entries(catCounts).map(([name, value]) => ({
    name, value, color: CAT_COLOR_HEX[name] || '#94a3b8'
  }))

  // Phase effort
  const phaseBar = phases
    .filter(ph => ph.duration_months)
    .map(ph => ({ name: ph.title?.slice(0, 20) || `Phase ${ph.phase}`, months: ph.duration_months || 0, fill: '#0ea5e9' }))

  const totalMonths = phases.reduce((s, ph) => s + (ph.duration_months || 0), 0) || data.total_effort_months

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">

      {/* Header with stats */}
      <div className="bg-white rounded-2xl shadow p-6">
        <div className="flex items-center gap-2 mb-3">
          <Rocket size={18} className="text-sky-600" />
          <h3 className="font-semibold text-blue-800">Modernisation Roadmap</h3>
          {data.current_maturity && (
            <span className={`ml-auto text-xs font-bold px-2 py-0.5 rounded ${MATURITY_BADGE[data.current_maturity] || 'bg-gray-100 text-blue-600'}`}>
              {data.current_maturity.replace('-', ' ').toUpperCase()}
            </span>
          )}
        </div>
        <p className="text-sm text-blue-700 mb-4">{data.summary}</p>
        <div className="grid grid-cols-3 gap-3 mb-4">
          <button onClick={() => openPhases()} className="bg-sky-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-sky-300 transition-all">
            <div className="text-2xl font-bold text-sky-600">{totalMonths || '?'}</div>
            <div className="text-xs text-blue-500 mt-1">Months total</div>
          </button>
          <button onClick={() => openPaths(null, 'All Transformation Paths')} className="bg-indigo-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-indigo-300 transition-all">
            <div className="text-2xl font-bold text-indigo-600">{paths.length}</div>
            <div className="text-xs text-blue-500 mt-1">Transform paths</div>
          </button>
          <button onClick={openPhases} className="bg-violet-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-violet-300 transition-all">
            <div className="text-2xl font-bold text-violet-600">{phases.length}</div>
            <div className="text-xs text-blue-500 mt-1">Phases</div>
          </button>
        </div>
        {data.target_state && (
          <div className="p-3 bg-sky-50 rounded-xl text-sm text-sky-800">
            <Rocket size={13} className="inline mr-1" />
            <strong>Target:</strong> {data.target_state}
          </div>
        )}
        {data.roi_narrative && (
          <p className="mt-3 text-xs text-blue-500 italic">{data.roi_narrative}</p>
        )}
      </div>

      {/* Charts row */}
      {(valueData.length > 0 || catPie.length > 0 || phaseBar.length > 0) && (
        <div className="grid md:grid-cols-3 gap-5">
          {valueData.length > 0 && (
            <div className="md:col-span-2 bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <TrendingUp size={14} className="text-sky-500" /> Path Value Scores (/10)
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={valueData} layout="vertical" margin={{ left: 4, right: 28, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                  <XAxis type="number" domain={[0, 10]} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <Tooltip content={<TIP />} />
                  <Bar dataKey="score" name="Value" radius={[0, 4, 4, 0]} maxBarSize={18}
                    onClick={(d) => d._original && setModal({ type: 'transform', title: d.name, items: paths, initialItem: d._original })} style={{ cursor: 'pointer' }}>
                    {valueData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {phaseBar.length > 0 ? (
            <div className="bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <Calendar size={14} className="text-sky-500" /> Phase Duration (months)
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={phaseBar} margin={{ left: 0, right: 12, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <Tooltip content={<TIP />} />
                  <Bar dataKey="months" name="Months" radius={[4, 4, 0, 0]} fill="#0ea5e9" maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : catPie.length > 1 ? (
            <div className="bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <Layers size={14} className="text-sky-500" /> By Category
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={catPie} cx="50%" cy="44%" innerRadius={48} outerRadius={72} paddingAngle={3} dataKey="value">
                    {catPie.map((e, i) => <Cell key={i} fill={e.color} />)}
                  </Pie>
                  <Tooltip formatter={(v, n) => [v + ' paths', n]} />
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : null}
        </div>
      )}

      {/* Transformation paths */}
      {paths.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={15} className="text-sky-500" />
            <h3 className="font-semibold text-blue-800">Transformation Paths ({paths.length})</h3>
          </div>
          <div className="space-y-3">
            {paths.map((p, i) => (
              <button key={i} onClick={() => setModal({ type: 'transform', title: `${p.current || '?'} \u2192 ${p.recommended || '?'}`, items: paths, initialItem: p })}
                className="w-full text-left border border-gray-100 rounded-xl p-4 hover:bg-sky-50/60 hover:border-sky-200 hover:shadow-sm transition-all">
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  {p.category && (
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${CAT_COLOR[p.category] || 'bg-gray-100 text-blue-600'}`}>
                      {p.category}
                    </span>
                  )}
                  <span className="text-sm font-mono text-red-600">{p.current}</span>
                  <ArrowRight size={14} className="text-blue-400" />
                  <span className="text-sm font-mono text-green-700 font-semibold">{p.recommended}</span>
                  {p.value_score != null && (
                    <span className="ml-auto flex items-center gap-0.5 text-xs text-blue-400">
                      Value: <strong className="text-indigo-600">{p.value_score}/10</strong>
                    </span>
                  )}
                  {p.risk && (
                    <span className={`text-xs font-semibold ${RISK_COLOR[p.risk] || ''}`}>
                      {p.risk} risk
                    </span>
                  )}
                </div>
                <p className="text-xs text-blue-600 mb-2">{p.rationale}</p>
                {(p.steps || []).length > 0 && (
                  <ol className="space-y-0.5 pl-2">
                    {p.steps.slice(0, 4).map((s, j) => (
                      <li key={j} className="text-xs text-blue-500 flex gap-1.5">
                        <span className="text-sky-400 font-bold shrink-0">{j+1}.</span>{s}
                      </li>
                    ))}
                  </ol>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Phases */}
      {phases.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calendar size={15} className="text-sky-500" />
            <h3 className="font-semibold text-blue-800">Modernisation Phases</h3>
            <button onClick={openPhases} className="ml-auto text-xs text-sky-500 hover:text-sky-700 underline underline-offset-2">View all</button>
          </div>
          <div className="space-y-3">
            {phases.map((ph, i) => (
              <button key={i} onClick={() => setModal({ type: 'phase', title: ph.title || `Phase ${ph.phase}`, items: phases.map(p => ({ ...p, _panelColor: 'sky' })), initialItem: { ...ph, _panelColor: 'sky' } })}
                className="w-full text-left border border-sky-100 rounded-xl p-4 bg-sky-50/30 hover:bg-sky-100/60 hover:border-sky-300 transition-colors">
                <div className="flex items-center gap-3 mb-2">
                  <span className="w-7 h-7 rounded-full bg-sky-600 text-blue-300 text-xs font-bold flex items-center justify-center shrink-0">
                    {ph.phase}
                  </span>
                  <span className="font-semibold text-sm text-blue-800">{ph.title}</span>
                  {ph.duration_months && (
                    <span className="ml-auto text-xs text-blue-400">{ph.duration_months} months</span>
                  )}
                </div>
                {(ph.items || []).length > 0 && (
                  <ul className="space-y-0.5 pl-10">
                    {ph.items.map((it, j) => (
                      <li key={j} className="text-xs text-blue-600 flex gap-1.5">
                        <ArrowRight size={10} className="text-sky-400 mt-0.5 shrink-0"/>{it}
                      </li>
                    ))}
                  </ul>
                )}
                {ph.milestone && (
                  <p className="mt-2 pl-10 text-xs text-sky-700 italic">✓ {ph.milestone}</p>
                )}
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
