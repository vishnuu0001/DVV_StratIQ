// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * BusinessRulesPanel.jsx — Business rules with charts
// Date: 2026-04-05
// ---------------------------------------------------------------------------
/**
 * BusinessRulesPanel.jsx — Business rules with charts
 */
import { useState } from 'react'
import { BookOpen, Tag, GitBranch, Layers, PieChart as PiIcon } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import AIDetailModal from './AIDetailModal.jsx'

const TYPE_COLOR_HEX = {
  validation:       '#3b82f6',
  calculation:      '#8b5cf6',
  workflow:         '#22c55e',
  'access-control': '#ef4444',
  integration:      '#f97316',
  'data-transform': '#14b8a6',
}
const TYPE_COLOR = {
  validation:       'bg-blue-100 text-blue-700',
  calculation:      'bg-purple-100 text-purple-700',
  workflow:         'bg-green-100 text-green-700',
  'access-control': 'bg-red-100 text-red-700',
  integration:      'bg-orange-100 text-orange-700',
  'data-transform': 'bg-teal-100 text-teal-700',
}
const CONF_COLOR = { high: '#22c55e', medium: '#f59e0b', low: '#94a3b8' }
const CONF_CLS   = { high: 'text-green-600', medium: 'text-yellow-600', low: 'text-blue-400' }

// Function: TIP
const TIP = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow px-3 py-2 text-xs">
      <p className="font-semibold text-blue-700 mb-1">{label}</p>
      {payload.map((p, i) => <p key={i} style={{ color: p.fill || p.color }}>{p.name}: <strong>{p.value}</strong></p>)}
    </div>
  )
}

// Function: BusinessRulesPanel
export default function BusinessRulesPanel({ data }) {
  if (!data) return null
  if (data.error) return <div className="bg-white rounded-2xl shadow p-6 text-red-500 text-sm">{data.error}</div>

  const rules     = data.business_rules || []
  const workflows = data.workflows      || []
  const entities  = data.key_entities   || []

  const [modal, setModal] = useState(null)
  // Function: openRules
  const openRules = (filterFn, label) =>
    setModal({ type: 'rule', title: label, items: filterFn ? rules.filter(filterFn) : rules })

  // Type breakdown donut
  const typeCounts = rules.reduce((a, r) => { a[r.type || 'other'] = (a[r.type || 'other'] || 0) + 1; return a }, {})
  const typePie = Object.entries(typeCounts).map(([name, value]) => ({
    name: name.replace('-', ' '), value, color: TYPE_COLOR_HEX[name] || '#94a3b8'
  }))

  // Confidence breakdown bar
  const confCounts = rules.reduce((a, r) => { a[r.confidence || 'low'] = (a[r.confidence || 'low'] || 0) + 1; return a }, {})
  const confBar = ['high', 'medium', 'low']
    .filter(c => confCounts[c])
    .map(c => ({ name: c.charAt(0).toUpperCase() + c.slice(1), count: confCounts[c], fill: CONF_COLOR[c] }))

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">

      {/* Header */}
      <div className="bg-white rounded-2xl shadow p-6">
        <div className="flex items-center gap-2 mb-3">
          <BookOpen size={18} className="text-emerald-600" />
          <h3 className="font-semibold text-blue-800">Business Rules Extraction</h3>
          {data.domain && (
            <span className="ml-auto text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-semibold">
              {data.domain}
            </span>
          )}
        </div>
        <p className="text-sm text-blue-700">{data.summary}</p>
        {entities.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {entities.map((e, i) => (
              <span key={i} className="flex items-center gap-1 text-xs bg-gray-100 text-blue-700 px-2 py-0.5 rounded-full">
                <Tag size={10}/>{e}
              </span>
            ))}
          </div>
        )}
        <div className="mt-4 grid grid-cols-3 gap-3">
          <button onClick={() => openRules(null, 'All Business Rules')} className="bg-emerald-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-emerald-300 transition-all">
            <div className="text-2xl font-bold text-emerald-600">{rules.length}</div>
            <div className="text-xs text-blue-500 mt-1">Rules</div>
          </button>
          <div className="bg-green-50 rounded-xl p-3 text-center">
            <div className="text-2xl font-bold text-green-600">{workflows.length}</div>
            <div className="text-xs text-blue-500 mt-1">Workflows</div>
          </div>
          <div className="bg-teal-50 rounded-xl p-3 text-center">
            <div className="text-2xl font-bold text-teal-600">{entities.length}</div>
            <div className="text-xs text-blue-500 mt-1">Entities</div>
          </div>
        </div>
      </div>

      {/* Charts row */}
      {(typePie.length > 0 || confBar.length > 0) && (
        <div className="grid md:grid-cols-3 gap-5">
          {typePie.length > 0 && (
            <div className="md:col-span-1 bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <PiIcon size={14} className="text-emerald-500" /> By Rule Type
              </h3>
              <ResponsiveContainer width="100%" height={210}>
                <PieChart>
                  <Pie data={typePie} cx="50%" cy="44%" innerRadius={48} outerRadius={72} paddingAngle={3} dataKey="value"
                    onClick={(d) => openRules(r => (r.type || '').replace('-', ' ') === d.name, `${d.name} Rules`)}
                    style={{ cursor: 'pointer' }}>
                    {typePie.map((e, i) => <Cell key={i} fill={e.color} />)}
                  </Pie>
                  <Tooltip formatter={(v, n) => [v + ' rules', n]} />
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 10 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
          {confBar.length > 0 && (
            <div className="md:col-span-2 bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <Layers size={14} className="text-emerald-500" /> Confidence Distribution
              </h3>
              <ResponsiveContainer width="100%" height={210}>
                <BarChart data={confBar} margin={{ left: 4, right: 16, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
                  <Tooltip content={<TIP />} />
                  <Bar dataKey="count" name="Rules" radius={[6, 6, 0, 0]} maxBarSize={60}
                    onClick={(d) => openRules(r => (r.confidence || 'low').toLowerCase() === d.name.toLowerCase(), `${d.name} Confidence Rules`)}
                    style={{ cursor: 'pointer' }}>
                    {confBar.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Rules */}
      {rules.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Layers size={15} className="text-emerald-500" />
            <h3 className="font-semibold text-blue-800">Business Rules ({rules.length})</h3>
          </div>
          <div className="space-y-3">
            {rules.map((r, i) => (
              <button key={i} onClick={() => setModal({ type: 'rule', title: r.title || r.id, items: rules, initialItem: r })}
                className="w-full text-left border border-gray-100 rounded-xl p-4 hover:bg-emerald-50/60 hover:border-emerald-200 hover:shadow-sm transition-all">
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <span className="text-xs text-blue-400 font-mono">{r.id}</span>
                  <span className="font-semibold text-sm text-blue-800">{r.title}</span>
                  {r.type && (
                    <span className={`text-xs px-2 py-0.5 rounded font-semibold ${TYPE_COLOR[r.type] || 'bg-gray-100 text-blue-600'}`}>
                      {r.type}
                    </span>
                  )}
                  {r.confidence && (
                    <span className={`ml-auto text-xs font-semibold ${CONF_CLS[r.confidence] || ''}`}>
                      {r.confidence} confidence
                    </span>
                  )}
                </div>
                <p className="text-sm text-blue-600 mb-1">{r.description}</p>
                {r.source_evidence && (
                  <code className="text-xs text-blue-400 block">{r.source_evidence}</code>
                )}
                {(r.affected_entities || []).length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {r.affected_entities.map((e, j) => (
                      <span key={j} className="text-xs bg-gray-50 border text-blue-500 px-1.5 py-0.5 rounded">{e}</span>
                    ))}
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Workflows */}
      {workflows.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <GitBranch size={15} className="text-emerald-500" />
            <h3 className="font-semibold text-blue-800">Workflows</h3>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            {workflows.map((w, i) => (
              <div key={i} className="border border-emerald-100 rounded-xl p-4 bg-emerald-50/30">
                <h4 className="font-semibold text-sm text-blue-800 mb-2">{w.name}</h4>
                <ol className="space-y-1">
                  {(w.steps || []).map((s, j) => (
                    <li key={j} className="flex gap-2 text-xs text-blue-600">
                      <span className="text-emerald-500 font-bold shrink-0">{j + 1}.</span>{s}
                    </li>
                  ))}
                </ol>
              </div>
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
