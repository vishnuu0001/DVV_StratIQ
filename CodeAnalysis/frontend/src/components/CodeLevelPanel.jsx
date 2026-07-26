// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * CodeLevelPanel.jsx — L2/L3 Code-Level Deep Scan Panel
// Date: 2025-11-12
// ---------------------------------------------------------------------------
/**
 * CodeLevelPanel.jsx — L2/L3 Code-Level Deep Scan Panel
 *
 * Renders per-function issues, anti-pattern catalog, coupling analysis,
 * class analysis, refactoring plan and quality gates from the ai_code_level service.
 */
import { useState } from 'react'
import {
  Code2, AlertCircle, GitBranch, Layers, Activity,
  ShieldAlert, Wrench, ChevronDown, ChevronUp, CheckCircle, XCircle,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'

// ─── Helpers ──────────────────────────────────────────────────────────────────
// Function: asList
const asList = (v) => (Array.isArray(v) ? v : v ? [v] : [])
// Function: asStr
const asStr  = (v, fallback = '—') => (v && typeof v === 'string' && v.trim() ? v.trim() : fallback)

const PRI_CLS = {
  critical : 'bg-red-100 text-red-700 border border-red-200',
  high     : 'bg-orange-100 text-orange-700 border border-orange-200',
  medium   : 'bg-yellow-100 text-yellow-700 border border-yellow-200',
  low      : 'bg-green-100 text-green-700 border border-green-200',
}
const PRI_BAR = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#f59e0b',
  low: '#22c55e',
}

// Function: PriBadge
function PriBadge({ v }) {
  const k = String(v || '').toLowerCase()
  return (
    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${PRI_CLS[k] || 'bg-gray-100 text-gray-600'}`}>
      {k.toUpperCase() || '—'}
    </span>
  )
}

// Function: SectionHeader
function SectionHeader({ icon: Icon, title, count, color = 'text-blue-700' }) {
  return (
    <div className={`flex items-center gap-2 mb-3 ${color}`}>
      <Icon size={16} />
      <span className="font-semibold text-sm">{title}</span>
      {count != null && (
        <span className="ml-1 text-xs bg-gray-100 text-gray-600 rounded-full px-2 py-0.5">{count}</span>
      )}
    </div>
  )
}

// Function: ScoreGauge
function ScoreGauge({ label, value, max = 100, good = 'high' }) {
  const pct   = Math.min(100, Math.max(0, (value / max) * 100))
  const isGood = good === 'high' ? pct >= 65 : pct <= 35
  const color  = isGood ? '#22c55e' : pct > 40 ? '#f59e0b' : '#ef4444'
  return (
    <div className="bg-gray-50 rounded-xl p-3 flex flex-col items-center gap-1">
      <div className="text-2xl font-bold" style={{ color }}>{value ?? '—'}</div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-2 rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <div className="text-xs text-gray-500 text-center">{label}</div>
    </div>
  )
}

// ─── Per-Function Issues Table ────────────────────────────────────────────────
// Function: FunctionIssuesTable
function FunctionIssuesTable({ items }) {
  const [showAll, setShowAll]       = useState(false)
  const [expanded, setExpanded]     = useState(null)
  const list = asList(items).filter((fn) => {
    const name = String(fn?.function || '').trim()
    return Boolean(name) && !['-', '--', '---', '—', '_', '?', 'unknown', 'n/a'].includes(name.toLowerCase())
  })
  const visible = showAll ? list : list.slice(0, 10)

  if (!list.length) return (
    <div className="text-xs text-gray-400 italic py-2">No per-function issues detected.</div>
  )

  return (
    <div>
      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="w-full text-xs">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              <th className="px-3 py-2 text-left">Function</th>
              <th className="px-3 py-2 text-left">File</th>
              <th className="px-2 py-2 text-center">CC</th>
              <th className="px-2 py-2 text-center">LOC</th>
              <th className="px-3 py-2 text-left">Issues</th>
              <th className="px-3 py-2 text-center">Priority</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {visible.map((fn, i) => (
              <>
                <tr
                  key={i}
                  className="hover:bg-blue-50/40 cursor-pointer transition-colors"
                  onClick={() => setExpanded(expanded === i ? null : i)}
                >
                  <td className="px-3 py-2 font-mono font-semibold text-blue-700 max-w-[160px] truncate">
                    {asStr(fn.function)}
                  </td>
                  <td className="px-3 py-2 text-gray-500 max-w-[160px] truncate">
                    {asStr(fn.file)}
                  </td>
                  <td className="px-2 py-2 text-center font-mono">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      (fn.cc || 0) > 15 ? 'bg-red-100 text-red-700' :
                      (fn.cc || 0) > 8  ? 'bg-orange-100 text-orange-700' :
                      'bg-green-100 text-green-700'
                    }`}>{fn.cc ?? '—'}</span>
                  </td>
                  <td className="px-2 py-2 text-center text-gray-500">{fn.sloc ?? '—'}</td>
                  <td className="px-3 py-2 text-gray-600 max-w-[200px]">
                    {asList(fn.issues).slice(0, 2).join('; ') || asStr(fn.issue)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    <PriBadge v={fn.priority} />
                  </td>
                </tr>
                {expanded === i && (
                  <tr key={`exp-${i}`} className="bg-blue-50/50">
                    <td colSpan={6} className="px-4 py-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        {fn.refactoring_action && (
                          <div>
                            <span className="font-semibold text-blue-700">Refactoring:</span>
                            <p className="mt-1 text-gray-600">{fn.refactoring_action}</p>
                          </div>
                        )}
                        {asList(fn.issues).length > 2 && (
                          <div>
                            <span className="font-semibold text-orange-700">All issues:</span>
                            <ul className="mt-1 list-disc list-inside text-gray-600">
                              {asList(fn.issues).map((iss, j) => <li key={j}>{iss}</li>)}
                            </ul>
                          </div>
                        )}
                        {fn.test_suggestion && (
                          <div>
                            <span className="font-semibold text-purple-700">Test suggestion:</span>
                            <p className="mt-1 text-gray-600">{fn.test_suggestion}</p>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>
      {list.length > 10 && (
        <button
          onClick={() => setShowAll(s => !s)}
          className="mt-2 text-xs text-blue-600 hover:underline flex items-center gap-1"
        >
          {showAll ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          {showAll ? 'Show less' : `Show all ${list.length} functions`}
        </button>
      )}
    </div>
  )
}

// ─── Anti-Pattern Catalog ─────────────────────────────────────────────────────
// Function: AntiPatternCatalog
function AntiPatternCatalog({ items }) {
  const list = asList(items)
  if (!list.length) return (
    <div className="text-xs text-gray-400 italic py-2">No anti-patterns detected.</div>
  )
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
      {list.map((p, i) => (
        <div
          key={i}
          className="border border-gray-200 rounded-xl p-3 bg-white hover:border-orange-300 transition-colors"
        >
          <div className="flex items-start justify-between gap-2 mb-1">
            <span className="font-semibold text-xs text-gray-800">{asStr(p.pattern || p.name)}</span>
            <PriBadge v={p.severity || p.priority} />
          </div>
          {p.occurrences != null && (
            <div className="text-[10px] text-orange-600 font-mono mb-1">×{p.occurrences} occurrences</div>
          )}
          {p.description && (
            <p className="text-[11px] text-gray-500 mb-1 leading-relaxed">{p.description}</p>
          )}
          {asList(p.examples || p.example_locations).length > 0 && (
            <div className="text-[10px] text-gray-400 font-mono truncate">
              {asList(p.examples || p.example_locations).slice(0, 2).join(', ')}
            </div>
          )}
          {p.remediation && (
            <div className="mt-2 text-[11px] text-green-700 border-t border-green-100 pt-1">
              ✓ {p.remediation}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

// ─── Class Analysis ───────────────────────────────────────────────────────────
// Function: ClassAnalysis
function ClassAnalysis({ items }) {
  const [open, setOpen] = useState(null)
  const list = asList(items)
  if (!list.length) return (
    <div className="text-xs text-gray-400 italic py-2">No class-level issues detected.</div>
  )
  return (
    <div className="space-y-2">
      {list.map((cls, i) => (
        <div key={i} className="border border-gray-200 rounded-xl overflow-hidden">
          <button
            onClick={() => setOpen(open === i ? null : i)}
            className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <Code2 size={14} className="text-purple-600" />
              <span className="font-semibold text-sm text-gray-800">{asStr(cls.class_name || cls.class)}</span>
              {cls.file && <span className="text-xs text-gray-400 font-mono">{cls.file}</span>}
              {cls.method_count != null && (
                <span className="text-[10px] bg-purple-50 text-purple-700 px-1.5 rounded">
                  {cls.method_count} methods
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <PriBadge v={cls.severity || cls.priority} />
              {open === i ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </div>
          </button>
          <AnimatePresence>
            {open === i && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-4 pb-4 pt-1 bg-purple-50/20 text-xs">
                  {asList(cls.detected_patterns || cls.patterns).length > 0 && (
                    <div className="mb-2">
                      <span className="font-semibold text-purple-700">Detected patterns: </span>
                      {asList(cls.detected_patterns || cls.patterns).join(', ')}
                    </div>
                  )}
                  {asList(cls.responsibilities || cls.issues).length > 0 && (
                    <div className="mb-2">
                      <span className="font-semibold text-orange-700">Responsibilities/Issues:</span>
                      <ul className="mt-1 list-disc list-inside text-gray-600">
                        {asList(cls.responsibilities || cls.issues).map((r, j) => <li key={j}>{r}</li>)}
                      </ul>
                    </div>
                  )}
                  {cls.recommendation && (
                    <div className="mt-2 p-2 bg-green-50 rounded border border-green-200 text-green-700">
                      <span className="font-semibold">Recommendation: </span>{cls.recommendation}
                    </div>
                  )}
                  {asList(cls.proposed_split_services || cls.proposed_services).length > 0 && (
                    <div className="mt-2">
                      <span className="font-semibold text-blue-700">Proposed split: </span>
                      {asList(cls.proposed_split_services || cls.proposed_services).join(' | ')}
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  )
}

// ─── Coupling Analysis ────────────────────────────────────────────────────────
// Function: CouplingAnalysis
function CouplingAnalysis({ data }) {
  if (!data || typeof data !== 'object') return (
    <div className="text-xs text-gray-400 italic">No coupling data available.</div>
  )
  const fanout = asList(data.fanout_hotspots || data.high_fanout_files)
  const tightly = asList(data.tightly_coupled_pairs || data.coupled_pairs)

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {fanout.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-orange-700 mb-2">High Fan-Out Files</div>
          <div className="space-y-1">
            {fanout.slice(0, 8).map((f, i) => (
              <div key={i} className="flex items-center justify-between bg-orange-50 rounded px-3 py-1.5 text-xs">
                <span className="font-mono text-gray-700 truncate max-w-[200px]">
                  {asStr(f.file || f)}
                </span>
                {(f.imports != null || f.import_count != null) && (
                  <span className="font-bold text-orange-700 ml-2 shrink-0">{f.imports ?? f.import_count} imports</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      {tightly.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-red-700 mb-2">Tightly Coupled Pairs</div>
          <div className="space-y-1">
            {tightly.slice(0, 6).map((p, i) => (
              <div key={i} className="bg-red-50 rounded px-3 py-1.5 text-xs">
                <span className="font-mono text-gray-700">
                  {asStr(p.from || p.module_a || p)} ↔ {asStr(p.to || p.module_b || '')}
                </span>
                {p.reason && <p className="text-gray-500 mt-0.5 text-[10px]">{p.reason}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
      {data.coupling_summary && (
        <div className="md:col-span-2 text-xs text-gray-600 bg-gray-50 p-3 rounded-xl">
          {data.coupling_summary}
        </div>
      )}
    </div>
  )
}

// ─── L3 Refactoring Plan ──────────────────────────────────────────────────────
// Function: RefactoringPlan
function RefactoringPlan({ items }) {
  const [open, setOpen] = useState(null)
  const list = asList(items)
  if (!list.length) return (
    <div className="text-xs text-gray-400 italic">No refactoring plan generated.</div>
  )
  return (
    <div className="space-y-3">
      {list.map((item, i) => (
        <div key={i} className="border border-gray-200 rounded-xl overflow-hidden">
          <button
            onClick={() => setOpen(open === i ? null : i)}
            className="w-full text-left px-4 py-3 hover:bg-blue-50/50 flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center shrink-0">
                {i + 1}
              </div>
              <div>
                <div className="font-semibold text-sm text-gray-800">{asStr(item.title || item.action)}</div>
                {item.target_function && (
                  <div className="text-[10px] font-mono text-blue-600">fn: {item.target_function}</div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              {item.effort_hours && (
                <span className="text-[10px] text-gray-500">{item.effort_hours}h</span>
              )}
              <PriBadge v={item.priority} />
              {open === i ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </div>
          </button>
          <AnimatePresence>
            {open === i && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-4 pb-4 pt-1 bg-blue-50/10 space-y-2 text-xs">
                  {item.description && <p className="text-gray-600">{item.description}</p>}
                  {(item.before_code || item.before_snippet) && (
                    <div>
                      <div className="text-[10px] font-bold text-red-700 mb-1">BEFORE</div>
                      <pre className="bg-red-50 border border-red-200 rounded p-2 text-[10px] font-mono overflow-x-auto whitespace-pre-wrap">
                        {item.before_code || item.before_snippet}
                      </pre>
                    </div>
                  )}
                  {(item.after_code || item.after_snippet) && (
                    <div>
                      <div className="text-[10px] font-bold text-green-700 mb-1">AFTER</div>
                      <pre className="bg-green-50 border border-green-200 rounded p-2 text-[10px] font-mono overflow-x-auto whitespace-pre-wrap">
                        {item.after_code || item.after_snippet}
                      </pre>
                    </div>
                  )}
                  {item.pattern_eliminated && (
                    <div className="text-gray-500">Pattern removed: <em>{item.pattern_eliminated}</em></div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  )
}

// ─── Quality Gates ────────────────────────────────────────────────────────────
// Function: QualityGates
function QualityGates({ items }) {
  const list = asList(items)
  if (!list.length) return (
    <div className="text-xs text-gray-400 italic">No quality gates recommended.</div>
  )
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead className="bg-gray-50 text-gray-600">
          <tr>
            <th className="px-3 py-2 text-left">Gate</th>
            <th className="px-3 py-2 text-left">Threshold</th>
            <th className="px-3 py-2 text-left">Rationale</th>
            <th className="px-3 py-2 text-center">Priority</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {list.map((g, i) => (
            <tr key={i} className="hover:bg-gray-50">
              <td className="px-3 py-2 font-semibold text-gray-800">{asStr(g.gate || g.name)}</td>
              <td className="px-3 py-2 font-mono text-blue-700">{asStr(g.threshold || g.value)}</td>
              <td className="px-3 py-2 text-gray-500 max-w-[300px]">{asStr(g.rationale || g.reason)}</td>
              <td className="px-3 py-2 text-center"><PriBadge v={g.priority} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Naming Violations ────────────────────────────────────────────────────────
// Function: NamingViolations
function NamingViolations({ items }) {
  const list = asList(items).slice(0, 12)
  if (!list.length) return null
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2">
      {list.map((v, i) => (
        <div key={i} className="bg-yellow-50 border border-yellow-200 rounded-xl px-3 py-2 text-xs">
          <div className="font-mono font-bold text-yellow-800">{asStr(v.name || v.identifier)}</div>
          <div className="text-gray-500">{asStr(v.violation || v.reason)}</div>
          {(v.suggestion || v.suggested_name) && <div className="text-green-700 mt-0.5">→ {v.suggestion || v.suggested_name}</div>}
        </div>
      ))}
    </div>
  )
}

// ─── CC Bar Chart ─────────────────────────────────────────────────────────────
// Function: CCChart
function CCChart({ items }) {
  const list = asList(items)
    .filter(f => typeof f === 'object' && f.cc != null)
    .sort((a, b) => (b.cc || 0) - (a.cc || 0))
    .slice(0, 12)
  if (!list.length) return null
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={list} margin={{ top: 4, right: 8, left: 0, bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="function"
          tick={{ fontSize: 9 }}
          angle={-35}
          textAnchor="end"
          interval={0}
        />
        <YAxis tick={{ fontSize: 10 }} />
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null
            const d = payload[0]?.payload || {}
            return (
              <div className="bg-white border border-gray-200 rounded shadow px-2 py-1 text-xs">
                <p className="font-mono font-semibold">{d.function}</p>
                <p className="text-gray-500">{d.file}</p>
                <p>CC: <strong className="text-red-600">{d.cc}</strong></p>
                <p>LOC: {d.sloc ?? '—'}</p>
              </div>
            )
          }}
        />
        <Bar dataKey="cc" radius={[4, 4, 0, 0]} name="Cyclomatic Complexity">
          {list.map((f, i) => (
            <Cell key={i} fill={(f.cc || 0) > 15 ? '#ef4444' : (f.cc || 0) > 8 ? '#f97316' : '#22c55e'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────
// Function: CodeLevelPanel
export default function CodeLevelPanel({ data }) {
  const [activeSection, setActiveSection] = useState('functions')

  if (!data) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
        No code-level analysis data available.
      </div>
    )
  }

  if (data.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
        <AlertCircle size={16} className="inline mr-2" />
        {data.error}
      </div>
    )
  }

  const perFn   = asList(data.per_function_issues)
  const catalog = asList(data.anti_pattern_catalog)
  const classes = asList(data.class_analysis)
  const plan    = asList(data.l3_refactoring_plan)
  const gates   = asList(data.quality_gates_recommended)
  const naming  = asList(data.naming_violations)

  const SECTIONS = [
    { id: 'functions',    label: 'Functions',       count: perFn.length,   icon: Code2 },
    { id: 'antipatterns', label: 'Anti-Patterns',   count: catalog.length, icon: ShieldAlert },
    { id: 'classes',      label: 'Classes',         count: classes.length, icon: Layers },
    { id: 'coupling',     label: 'Coupling',        count: null,           icon: GitBranch },
    { id: 'refactoring',  label: 'Refactoring Plan',count: plan.length,    icon: Wrench },
    { id: 'gates',        label: 'Quality Gates',   count: gates.length,   icon: CheckCircle },
  ]

  return (
    <div className="space-y-6">
      {/* Score gauges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <ScoreGauge label="Code Smell Score" value={data.code_smell_score} max={100} good="high" />
        <ScoreGauge label="Maintainability" value={data.maintainability_index} max={100} good="high" />
        <ScoreGauge label="Functions Analysed" value={perFn.length} max={Math.max(50, perFn.length)} good="low" />
        <ScoreGauge label="Anti-Patterns Found" value={catalog.length} max={Math.max(10, catalog.length)} good="low" />
      </div>

      {/* Summary */}
      {data.summary && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-gray-700">
          {data.summary}
        </div>
      )}

      {/* CC Chart */}
      {perFn.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <SectionHeader icon={Activity} title="Cyclomatic Complexity — Top Functions" color="text-red-600" />
          <CCChart items={perFn} />
        </div>
      )}

      {/* Tabbed sections */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="flex overflow-x-auto border-b border-gray-200 bg-gray-50">
          {SECTIONS.map(s => (
            <button
              key={s.id}
              onClick={() => setActiveSection(s.id)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium whitespace-nowrap transition-colors border-b-2 ${
                activeSection === s.id
                  ? 'border-blue-600 text-blue-700 bg-white'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <s.icon size={12} />
              {s.label}
              {s.count != null && s.count > 0 && (
                <span className="bg-gray-200 text-gray-600 rounded-full px-1.5 py-0.5 text-[9px] font-bold">
                  {s.count}
                </span>
              )}
            </button>
          ))}
        </div>

        <div className="p-4">
          {activeSection === 'functions'    && <FunctionIssuesTable items={perFn} />}
          {activeSection === 'antipatterns' && <AntiPatternCatalog items={catalog} />}
          {activeSection === 'classes'      && <ClassAnalysis items={classes} />}
          {activeSection === 'coupling'     && <CouplingAnalysis data={data.coupling_analysis} />}
          {activeSection === 'refactoring'  && <RefactoringPlan items={plan} />}
          {activeSection === 'gates'        && (
            <div className="space-y-4">
              <QualityGates items={gates} />
              {naming.length > 0 && (
                <div className="mt-4">
                  <SectionHeader icon={AlertCircle} title="Naming Violations" count={naming.length} color="text-yellow-700" />
                  <NamingViolations items={naming} />
                </div>
              )}
              {asList(data.dead_code_indicators).length > 0 && (
                <div className="mt-4">
                  <SectionHeader icon={XCircle} title="Dead Code Indicators" count={asList(data.dead_code_indicators).length} color="text-gray-600" />
                  <div className="space-y-1">
                    {asList(data.dead_code_indicators).slice(0, 8).map((d, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs bg-gray-50 rounded px-3 py-1.5">
                        <XCircle size={10} className="text-gray-400 shrink-0" />
                        <span className="font-mono text-gray-600">{asStr(d.function || d)}</span>
                        {d.file && <span className="text-gray-400">({d.file})</span>}
                        {d.reason && <span className="text-gray-400 ml-auto">{d.reason}</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
