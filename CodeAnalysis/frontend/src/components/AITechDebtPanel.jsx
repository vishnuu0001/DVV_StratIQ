// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * AITechDebtPanel.jsx  — Tech Debt Intelligence with charts and detailed metrics
// Date: 2025-11-26
// ---------------------------------------------------------------------------
/**
 * AITechDebtPanel.jsx  — Tech Debt Intelligence with charts and detailed metrics
 */
import { useState } from 'react'
import { TrendingDown, AlertTriangle, Zap, Target, Shield, ChevronDown, ChevronUp } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import AIDetailModal from './AIDetailModal.jsx'

// Function: TIP
const TIP = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg px-3 py-2 text-xs">
      <p className="font-semibold text-blue-700 mb-1 max-w-[200px] truncate">{label}</p>
      {payload.map((p, i) => <p key={i} style={{ color: p.fill || p.color }}>{p.name}: <strong>{p.value}</strong></p>)}
    </div>
  )
}

const PCOL = { high: '#ef4444', medium: '#f59e0b', low: '#22c55e' }
const PCls = { high: 'bg-red-100 text-red-700', medium: 'bg-yellow-100 text-yellow-700', low: 'bg-green-100 text-green-700' }
const ImpactCls = { high: 'text-red-600', medium: 'text-yellow-600', low: 'text-green-600' }
const CAT_COLORS = {
  complexity: '#ef4444', long_methods: '#f97316', deep_nesting: '#f59e0b',
  test_coverage: '#8b5cf6', documentation: '#06b6d4', design: '#3b82f6',
}

// ─── Metric chip ──────────────────────────────────────────────────────────────
// Function: MetricChip
function MetricChip({ label, value, warn }) {
  if (value == null || value === 0) return null
  const cls = warn && value > 0 ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-gray-100 text-blue-700'
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded ${cls}`}>
      <span className="font-semibold">{label}</span>
      <span>{value}</span>
    </span>
  )
}

// ─── Expandable hotspot card ──────────────────────────────────────────────────
// Function: HotspotCard
function HotspotCard({ h, index, onClick }) {
  const [expanded, setExpanded] = useState(false)
  const m = h.metrics || {}
  return (
    <div className="border border-gray-100 rounded-xl overflow-hidden hover:border-orange-200 transition-colors">
      <button
        className="w-full text-left p-4 hover:bg-orange-50/40 transition-colors"
        onClick={() => { setExpanded(e => !e); onClick && onClick() }}
      >
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <span className={`text-xs font-bold px-2 py-0.5 rounded ${PCls[h.priority] || 'bg-gray-100 text-blue-600'}`}>
            {(h.priority || '').toUpperCase()}
          </span>
          {h.debt_category && (
            <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-blue-50 text-blue-600 border border-blue-100">
              {h.debt_category}
            </span>
          )}
          <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded text-blue-700 max-w-xs truncate flex-1" title={h.file}>
            {h.file}
          </code>
          {h.effort_days > 0 && (
            <span className="text-xs font-semibold text-blue-500 bg-gray-100 px-2 py-0.5 rounded whitespace-nowrap">~{h.effort_days}d</span>
          )}
          {expanded ? <ChevronUp size={13} className="text-blue-400 shrink-0" /> : <ChevronDown size={13} className="text-blue-400 shrink-0" />}
        </div>

        {/* Metric chips row */}
        {(m.cyclomatic_complexity > 0 || m.sloc > 0 || m.long_methods > 0 || m.deep_nesting > 0) && (
          <div className="flex flex-wrap gap-1.5 mb-2">
            <MetricChip label="CC"      value={m.cyclomatic_complexity} warn={m.cyclomatic_complexity > 10} />
            <MetricChip label="SLOC"    value={m.sloc} />
            <MetricChip label="fns"     value={m.functions} />
            <MetricChip label="classes" value={m.classes} />
            <MetricChip label="long-methods" value={m.long_methods} warn={m.long_methods > 0} />
            <MetricChip label="nesting" value={m.deep_nesting}  warn={m.deep_nesting > 0} />
          </div>
        )}

        <p className="text-sm text-blue-600 mb-1"><strong>Issue:</strong> {h.issue}</p>
        <p className="text-sm text-indigo-700"><strong>Fix:</strong> {h.recommendation}</p>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-2 border-t border-gray-100 pt-3 bg-gray-50/50">
              {h.root_cause && (
                <div className="bg-orange-50 rounded-lg p-3">
                  <p className="text-[10px] font-semibold text-orange-600 uppercase tracking-wide mb-1">Root Cause</p>
                  <p className="text-xs text-orange-800">{h.root_cause}</p>
                </div>
              )}
              {Array.isArray(h.per_function_breakdown) && h.per_function_breakdown.length > 0 && (
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-[10px] font-semibold text-blue-600 uppercase tracking-wide mb-2">
                    L3 Function Breakdown
                  </p>
                  <div className="space-y-1.5">
                    {h.per_function_breakdown.slice(0, 5).map((fn, idx) => (
                      <div key={idx} className="text-xs rounded border border-blue-100 bg-white px-2 py-1.5">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono font-semibold text-blue-700">{fn.function || 'unknown_function'}</span>
                          {fn.cyclomatic_complexity != null && (
                            <span className="text-[10px] bg-red-50 text-red-700 px-1.5 py-0.5 rounded">
                              CC {fn.cyclomatic_complexity}
                            </span>
                          )}
                          {fn.sloc != null && (
                            <span className="text-[10px] bg-gray-100 text-blue-700 px-1.5 py-0.5 rounded">
                              LOC {fn.sloc}
                            </span>
                          )}
                        </div>
                        {fn.issue && <p className="text-[11px] text-blue-700 mt-1">Issue: {fn.issue}</p>}
                        {fn.refactoring && <p className="text-[11px] text-green-700 mt-0.5">Fix: {fn.refactoring}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {h.impact && (
                <div className="bg-red-50 rounded-lg p-3">
                  <p className="text-[10px] font-semibold text-red-600 uppercase tracking-wide mb-1">Business Impact if Ignored</p>
                  <p className="text-xs text-red-800">{h.impact}</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Function: AITechDebtPanel
export default function AITechDebtPanel({ data }) {
  if (!data) return null
  if (data.error) return <div className="bg-white rounded-2xl shadow p-6 text-red-500 text-sm">{data.error}</div>

  const hotspots  = data.hotspots            || []
  const quickWins = data.quick_wins           || []
  const strategic = data.strategic_actions    || []

  const [modal,        setModal]        = useState(null)
  const [showAllHS,    setShowAllHS]    = useState(false)
  const visibleHS = showAllHS ? hotspots : hotspots.slice(0, 8)

  // Function: openHotspots
  const openHotspots = (filterFn, label) =>
    setModal({ type: 'hotspot', title: label, items: filterFn ? hotspots.filter(filterFn) : hotspots })

  const priorityCounts = hotspots.reduce((a, h) => { const p = h.priority || 'low'; a[p] = (a[p] || 0) + 1; return a }, {})
  const pieData = Object.entries(priorityCounts).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1), value, color: PCOL[name] || '#94a3b8'
  }))
  const barData = [...hotspots]
    .filter(h => h.effort_days > 0)
    .sort((a, b) => (b.effort_days || 0) - (a.effort_days || 0))
    .slice(0, 10)
    .map(h => ({ name: (h.file || '').split('/').pop() || h.file || '?', effort: h.effort_days || 0, fill: PCOL[h.priority] || '#94a3b8', _original: h }))
  const totalEffort = hotspots.reduce((s, h) => s + (h.effort_days || 0), 0)

  // Debt by category chart
  const debtCatData = data.debt_by_category
    ? Object.entries(data.debt_by_category)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => ({ name: k.replace(/_/g, ' '), value: v, color: CAT_COLORS[k] || '#94a3b8' }))
    : []

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">

      {/* Summary + stat cards */}
      <div className="bg-white rounded-2xl shadow p-6">
        <div className="flex items-center gap-2 mb-3">
          <TrendingDown size={18} className="text-orange-500" />
          <h3 className="font-semibold text-blue-800">Tech Debt Intelligence</h3>
          {data._model_used && <span className="ml-auto text-xs text-blue-400">{data._model_used}</span>}
        </div>
        <p className="text-sm text-blue-700 leading-relaxed">{data.summary}</p>
        <div className="mt-4 grid grid-cols-3 gap-3">
          <button onClick={() => openHotspots(h => h.effort_days > 0, `All Hotspots (${data.estimated_total_effort_days ?? totalEffort} days)`)} className="bg-orange-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-orange-300 transition-all">
            <div className="text-2xl font-bold text-orange-600">{data.estimated_total_effort_days ?? totalEffort}</div>
            <div className="text-xs text-blue-500 mt-1">Total days</div>
          </button>
          <button onClick={() => openHotspots(h => h.priority === 'high', 'High Priority Hotspots')} className="bg-red-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-red-300 transition-all">
            <div className="text-2xl font-bold text-red-600">{priorityCounts.high || 0}</div>
            <div className="text-xs text-blue-500 mt-1">High priority</div>
          </button>
          <button onClick={() => openHotspots(null, 'All Hotspots')} className="bg-blue-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-blue-300 transition-all">
            <div className="text-2xl font-bold text-blue-600">{hotspots.length}</div>
            <div className="text-xs text-blue-500 mt-1">Hotspots</div>
          </button>
        </div>
        {/* Risk if ignored */}
        {data.risk_if_ignored && (
          <div className="mt-4 bg-red-50 border border-red-100 rounded-xl p-3">
            <p className="text-[10px] font-semibold text-red-600 uppercase tracking-wide mb-1">Risk if Not Addressed</p>
            <p className="text-xs text-red-700">{data.risk_if_ignored}</p>
          </div>
        )}
      </div>

      {/* Charts row */}
      {(barData.length > 0 || pieData.length > 0 || debtCatData.length > 0) && (
        <div className="grid md:grid-cols-3 gap-5">
          {barData.length > 0 && (
            <div className="md:col-span-2 bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <Target size={14} className="text-orange-500" /> Effort by File (top {barData.length}) — days
              </h3>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={barData} layout="vertical" margin={{ left: 4, right: 28, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                  <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <Tooltip content={<TIP />} />
                  <Bar dataKey="effort" name="Days" radius={[0, 4, 4, 0]} maxBarSize={18}
                    onClick={(d) => d._original && setModal({ type: 'hotspot', title: d.name, items: hotspots, initialItem: d._original })} style={{ cursor: 'pointer' }}>
                    {barData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          <div className="space-y-5">
            {pieData.length > 0 && (
              <div className="bg-white rounded-2xl shadow p-5">
                <h3 className="font-semibold text-blue-800 text-sm mb-3 flex items-center gap-2">
                  <AlertTriangle size={14} className="text-yellow-500" /> By Priority
                </h3>
                <ResponsiveContainer width="100%" height={160}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="44%" innerRadius={40} outerRadius={62} paddingAngle={3} dataKey="value"
                      onClick={(d) => openHotspots(h => (h.priority || 'low').toLowerCase() === d.name.toLowerCase(), `${d.name} Priority Hotspots`)}
                      style={{ cursor: 'pointer' }}>
                      {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                    </Pie>
                    <Tooltip formatter={(v, n) => [v + ' items', n]} />
                    <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 10 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
            {debtCatData.length > 0 && (
              <div className="bg-white rounded-2xl shadow p-5">
                <h3 className="font-semibold text-blue-800 text-sm mb-3 flex items-center gap-2">
                  <Shield size={14} className="text-blue-500" /> Debt by Category (%)
                </h3>
                <div className="space-y-2">
                  {debtCatData.sort((a, b) => b.value - a.value).map(cat => (
                    <div key={cat.name} className="flex items-center gap-2">
                      <span className="text-[10px] text-blue-500 w-28 shrink-0 capitalize">{cat.name}</span>
                      <div className="flex-1 h-2 rounded-full bg-gray-100 overflow-hidden">
                        <div className="h-full rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, cat.value)}%`, background: cat.color }} />
                      </div>
                      <span className="text-[10px] font-mono text-blue-600 w-8 text-right">{cat.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* By-language breakdown */}
      {(data.by_language || []).length > 0 && (
        <div className="bg-white rounded-2xl shadow p-5">
          <h3 className="font-semibold text-blue-800 text-sm mb-3 flex items-center gap-2">
            <TrendingDown size={14} className="text-orange-500" /> Debt Level by Language
          </h3>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
            {data.by_language.map((bl, i) => (
              <div key={i} className={`rounded-xl p-3 border ${
                bl.debt_level === 'high'   ? 'bg-red-50 border-red-100' :
                bl.debt_level === 'medium' ? 'bg-yellow-50 border-yellow-100' :
                                             'bg-green-50 border-green-100'
              }`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-blue-800 text-xs">{bl.language}</span>
                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ml-auto ${
                    bl.debt_level === 'high'   ? 'bg-red-100 text-red-700' :
                    bl.debt_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                                 'bg-green-100 text-green-700'
                  }`}>{bl.debt_level}</span>
                </div>
                <p className="text-[11px] text-blue-600">{bl.primary_issue}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hotspots */}
      {hotspots.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={16} className="text-red-500" />
            <h3 className="font-semibold text-blue-800">Debt Hotspots ({hotspots.length})</h3>
            <span className="ml-auto text-xs text-blue-400">
              Click a card to expand root cause &amp; impact details
            </span>
          </div>
          <div className="space-y-3">
            {visibleHS.map((h, i) => (
              <HotspotCard key={i} h={h} index={i} />
            ))}
          </div>
          {hotspots.length > 8 && (
            <button
              onClick={() => setShowAllHS(s => !s)}
              className="mt-3 w-full text-xs text-blue-500 hover:text-blue-700 py-2 rounded-lg border border-dashed border-blue-200 hover:border-blue-400 transition-colors"
            >
              {showAllHS ? `Show less` : `Show all ${hotspots.length} hotspots`}
            </button>
          )}
        </div>
      )}

      {/* Quick Wins + Strategic Actions */}
      {(quickWins.length > 0 || strategic.length > 0) && (
        <div className="grid md:grid-cols-2 gap-4">
          {quickWins.length > 0 && (
            <div className="bg-white rounded-2xl shadow p-5">
              <div className="flex items-center gap-2 mb-4">
                <Zap size={15} className="text-yellow-500" />
                <h3 className="font-semibold text-blue-700 text-sm">Quick Wins ({quickWins.length})</h3>
              </div>
              <div className="space-y-3">
                {quickWins.map((w, i) => {
                  const isObj = typeof w === 'object' && w !== null
                  const action  = isObj ? w.action  || w.description || JSON.stringify(w) : w
                  const benefit = isObj ? w.benefit  : null
                  const effort  = isObj ? w.effort_hours : null
                  const file    = isObj ? w.file     : null
                  return (
                    <div key={i} className="rounded-xl border border-yellow-100 bg-yellow-50/50 p-3">
                      <div className="flex items-start gap-2">
                        <span className="mt-0.5 w-5 h-5 rounded-full bg-yellow-100 text-yellow-700 text-[10px] font-bold flex items-center justify-center shrink-0">{i+1}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-blue-700 font-medium">{action}</p>
                          {file && file !== 'multiple' && (
                            <code className="text-[10px] text-blue-500 bg-blue-50 px-1.5 py-0.5 rounded mt-1 inline-block truncate max-w-full">{file}</code>
                          )}
                          {benefit && <p className="text-xs text-green-700 mt-1">✓ {benefit}</p>}
                          {effort != null && <span className="text-[10px] text-blue-400 mt-1 block">~{effort}h effort</span>}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
          {strategic.length > 0 && (
            <div className="bg-white rounded-2xl shadow p-5">
              <div className="flex items-center gap-2 mb-4">
                <Target size={15} className="text-blue-500" />
                <h3 className="font-semibold text-blue-700 text-sm">Strategic Actions ({strategic.length})</h3>
              </div>
              <div className="space-y-3">
                {strategic.map((s, i) => {
                  const isObj = typeof s === 'object' && s !== null
                  const action    = isObj ? s.action    || s.description || JSON.stringify(s) : s
                  const rationale = isObj ? s.rationale : null
                  const effort    = isObj ? s.effort_weeks : null
                  const impact    = isObj ? s.impact    : null
                  return (
                    <div key={i} className="rounded-xl border border-blue-100 bg-blue-50/50 p-3">
                      <div className="flex items-start gap-2">
                        <span className="mt-0.5 w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold flex items-center justify-center shrink-0">{i+1}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start gap-2 flex-wrap">
                            <p className="text-sm text-blue-700 font-medium flex-1">{action}</p>
                            {impact && (
                              <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded whitespace-nowrap ${ImpactCls[impact] || 'text-blue-500'}`}>
                                {impact} impact
                              </span>
                            )}
                          </div>
                          {rationale && <p className="text-xs text-blue-600 mt-1 leading-relaxed">{rationale}</p>}
                          {effort != null && <span className="text-[10px] text-blue-400 mt-1 block">~{effort} week{effort !== 1 ? 's' : ''} effort</span>}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      <AnimatePresence>
        {modal && <AIDetailModal {...modal} onClose={() => setModal(null)} />}
      </AnimatePresence>
    </motion.div>
  )
}
