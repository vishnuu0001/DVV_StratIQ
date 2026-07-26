// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (Strat-AqorynthModulePanel.jsx)
// Date: 2026-06-07
// ---------------------------------------------------------------------------
import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Layers, GitBranch, RefreshCw, Shield, Database, BarChart2,
  Trash2, Network, Zap, Clock, CheckSquare, Square, Play,
  ChevronDown, ChevronRight, AlertTriangle, CheckCircle2,
  XCircle, Info, Code2, Cpu, FileCode, TrendingUp
} from 'lucide-react'
import { listStrat-AqorynthModules, startStrat-AqorynthAnalysis, streamStrat-AqorynthJob } from '../api/client.js'

// ── Feature Cards (the 9 analysis capabilities) ───────────────────────────────

const FEATURES = [
  {
    icon: Cpu,
    title: 'Technology Stack Detection',
    desc: 'ASP.NET, Java EE, Spring, PHP, Oracle-heavy apps, and 20+ framework signatures.',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/25',
  },
  {
    icon: Layers,
    title: 'Architecture Pattern Recognition',
    desc: 'WebForms, MVC, n-tier, SOA, batch-oriented services, and monolithic seams.',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/25',
  },
  {
    icon: RefreshCw,
    title: 'Circular Dependency Detection',
    desc: 'Import graph analysis to find cycles that block independent service extraction.',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10 border-orange-500/25',
  },
  {
    icon: Trash2,
    title: 'Dead Code Identification',
    desc: 'Classes never referenced from other files — reduce cognitive load and exposure.',
    color: 'text-red-400',
    bg: 'bg-red-500/10 border-red-500/25',
  },
  {
    icon: Network,
    title: 'Domain Dependency Graph',
    desc: 'Interactive node/edge graph showing which domains reference which — the first step toward extraction.',
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/25',
  },
  {
    icon: Database,
    title: 'Database Layer Analysis',
    desc: 'Connection strings, raw ADO.NET, Oracle SQL patterns, schema touchpoints, and dependencies.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/25',
  },
  {
    icon: BarChart2,
    title: 'Code Metrics',
    desc: 'LOC, class volume, hotspot files, god class detection, and maintainability signals.',
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10 border-indigo-500/25',
  },
  {
    icon: Shield,
    title: 'Anti-Pattern Detection',
    desc: 'Hardcoded credentials, SQL concatenation, god classes, tight coupling, and risk markers.',
    color: 'text-rose-400',
    bg: 'bg-rose-500/10 border-rose-500/25',
  },
  {
    icon: Zap,
    title: 'Effort Estimation',
    desc: 'Time-to-modernize estimates anchored to real case study data (12x acceleration benchmarks).',
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10 border-yellow-500/25',
  },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

const RISK_STYLES = {
  CRITICAL: 'bg-red-500/15 text-red-300 border-red-500/40',
  HIGH:     'bg-orange-500/15 text-orange-300 border-orange-500/40',
  MEDIUM:   'bg-amber-500/15 text-amber-300 border-amber-500/40',
  LOW:      'bg-emerald-500/15 text-emerald-300 border-emerald-500/40',
}

// Function: RiskBadge
function RiskBadge({ label }) {
  return (
    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${RISK_STYLES[label] || RISK_STYLES.LOW}`}>
      {label}
    </span>
  )
}

// Function: MetricPill
function MetricPill({ icon: Icon, label, value, color }) {
  return (
    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/60 border border-slate-700/40">
      <Icon size={11} className={color || 'text-blue-400'} />
      <span className="text-[10px] text-slate-400">{label}</span>
      <span className="text-[10px] font-semibold text-slate-200 ml-1">{value}</span>
    </div>
  )
}

// Function: SectionHeader
function SectionHeader({ icon: Icon, title, color, badge }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <Icon size={14} className={color || 'text-blue-400'} />
      <span className="text-xs font-semibold text-slate-200">{title}</span>
      {badge && <RiskBadge label={badge} />}
    </div>
  )
}

// ── Domain Graph (simple SVG) ─────────────────────────────────────────────────

// Function: DomainGraph
function DomainGraph({ nodes = [], edges = [] }) {
  if (!nodes.length) return <p className="text-xs text-slate-500">No domain graph data.</p>

  const W = 560, H = 260
  const cx = W / 2, cy = H / 2
  const r = Math.min(cx, cy) - 40
  const angleStep = (2 * Math.PI) / nodes.length

  const positions = nodes.slice(0, 12).map((n, i) => ({
    ...n,
    x: cx + r * Math.cos(i * angleStep - Math.PI / 2),
    y: cy + r * Math.sin(i * angleStep - Math.PI / 2),
  }))

  const posMap = Object.fromEntries(positions.map(p => [p.id, p]))

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-h-56 rounded-xl bg-slate-900/40 border border-slate-700/30">
      <defs>
        <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
        </marker>
      </defs>
      {edges.slice(0, 30).map((e, i) => {
        const s = posMap[e.source], t = posMap[e.target]
        if (!s || !t) return null
        return (
          <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y}
            stroke="#475569" strokeWidth="1" strokeOpacity="0.5"
            markerEnd="url(#arrow)" />
        )
      })}
      {positions.map((n, i) => (
        <g key={n.id}>
          <circle cx={n.x} cy={n.y} r={14} fill="#1e3a5f" stroke="#3b82f6" strokeWidth="1.5" strokeOpacity="0.6" />
          <text x={n.x} y={n.y + 4} textAnchor="middle" fontSize="8" fill="#93c5fd"
            className="font-mono">{n.label?.slice(0, 6)}</text>
          <text x={n.x} y={n.y + 26} textAnchor="middle" fontSize="7" fill="#64748b">{n.file_count}f</text>
        </g>
      ))}
    </svg>
  )
}

// ── Module Result Card ────────────────────────────────────────────────────────

// Function: ModuleResultCard
function ModuleResultCard({ result }) {
  const [expanded, setExpanded] = useState(false)

  if (result.error) {
    return (
      <div className="rounded-2xl border border-red-500/30 bg-red-500/5 p-4">
        <div className="flex items-center gap-2">
          <XCircle size={14} className="text-red-400" />
          <span className="text-sm font-semibold text-red-300">{result.module_name}</span>
          <span className="text-xs text-red-400 ml-auto">Error: {result.error}</span>
        </div>
      </div>
    )
  }

  const { tech_stack, architecture, circular_deps, dead_code,
          domain_graph, db_analysis, code_metrics, anti_patterns, effort } = result

  return (
    <div className="rounded-2xl border border-slate-700/50 bg-slate-900/40 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-5 py-4 hover:bg-slate-800/30 transition-colors text-left"
      >
        <FileCode size={16} className="text-blue-400 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-blue-200">{result.module_name}</span>
            <RiskBadge label={effort?.risk_label || 'LOW'} />
            <span className="text-[10px] text-slate-400">{result.file_count} files</span>
          </div>
          <div className="flex flex-wrap gap-2 mt-1">
            <MetricPill icon={Code2}      label="SLOC"        value={(code_metrics?.total_sloc || 0).toLocaleString()} color="text-blue-400" />
            <MetricPill icon={TrendingUp} label="Effort"      value={`${effort?.estimated_effort_months || 0}mo`}      color="text-amber-400" />
            <MetricPill icon={RefreshCw}  label="Cycles"      value={circular_deps?.cycle_count || 0}                  color={circular_deps?.cycle_count > 0 ? 'text-orange-400' : 'text-emerald-400'} />
            <MetricPill icon={Shield}     label="Anti-patterns" value={anti_patterns?.total_patterns || 0}             color="text-rose-400" />
          </div>
        </div>
        <div className="flex-shrink-0">
          {expanded ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
        </div>
      </button>

      {/* Expanded Detail */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 space-y-5 border-t border-slate-700/40 pt-4">

              {/* Row 1: Tech Stack + Architecture */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                {/* Tech Stack */}
                <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
                  <SectionHeader icon={Cpu} title="Technology Stack" color="text-blue-400" />
                  <div className="space-y-2">
                    {tech_stack?.languages?.length > 0 && (
                      <div>
                        <p className="text-[10px] font-semibold text-slate-400 uppercase mb-1">Languages</p>
                        <div className="flex flex-wrap gap-1">
                          {tech_stack.languages.map(l => (
                            <span key={l} className="text-[10px] px-2 py-0.5 rounded-full bg-blue-800/40 text-blue-200 border border-blue-600/30">{l}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {Object.entries(tech_stack?.frameworks || {}).map(([cat, items]) => items.length > 0 && (
                      <div key={cat}>
                        <p className="text-[10px] font-semibold text-slate-400 uppercase mb-1">{cat}</p>
                        <div className="flex flex-wrap gap-1">
                          {items.map(f => (
                            <span key={f} className="text-[10px] px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-200 border border-slate-600/30">{f}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                    {!tech_stack?.languages?.length && !tech_stack?.total_frameworks && (
                      <p className="text-xs text-slate-500">No framework signatures detected.</p>
                    )}
                  </div>
                </div>

                {/* Architecture */}
                <div className="rounded-xl border border-purple-500/20 bg-purple-500/5 p-4">
                  <SectionHeader icon={Layers} title="Architecture Patterns" color="text-purple-400" />
                  {architecture?.detected_patterns?.length > 0 ? (
                    <div className="space-y-1.5">
                      {architecture.detected_patterns.map(p => (
                        <div key={p.key} className="flex items-center gap-2">
                          <CheckCircle2 size={11} className="text-purple-400 flex-shrink-0" />
                          <span className="text-xs text-slate-200">{p.label}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">No distinct patterns detected.</p>
                  )}
                  {architecture?.layers?.length > 0 && (
                    <div className="mt-3">
                      <p className="text-[10px] font-semibold text-slate-400 uppercase mb-1.5">Detected Layers</p>
                      <div className="space-y-1">
                        {architecture.layers.map(l => (
                          <div key={l.layer} className="flex items-center gap-2">
                            <div className="flex-1 bg-slate-700/40 rounded-full h-1.5">
                              <div
                                className="bg-purple-400/60 rounded-full h-1.5"
                                style={{ width: `${Math.min(100, l.file_count * 2)}%` }}
                              />
                            </div>
                            <span className="text-[10px] text-slate-300 w-24 flex-shrink-0">{l.layer} ({l.file_count})</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Row 2: Circular Deps + Dead Code */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                {/* Circular Dependencies */}
                <div className="rounded-xl border border-orange-500/20 bg-orange-500/5 p-4">
                  <SectionHeader icon={RefreshCw} title="Circular Dependencies" color="text-orange-400" badge={circular_deps?.risk_label} />
                  {circular_deps?.cycle_count > 0 ? (
                    <div className="space-y-2">
                      <p className="text-xs text-slate-300">{circular_deps.cycle_count} cycle{circular_deps.cycle_count !== 1 ? 's' : ''} detected</p>
                      {circular_deps.cycles?.slice(0, 4).map((cycle, i) => (
                        <div key={i} className="text-[10px] text-orange-200 bg-orange-900/20 rounded-lg px-2 py-1 font-mono">
                          {Array.isArray(cycle) ? cycle.slice(0, 4).join(' → ') : String(cycle)}
                          {Array.isArray(cycle) && cycle.length > 4 && ' …'}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <CheckCircle2 size={13} className="text-emerald-400" />
                      <span className="text-xs text-emerald-300">No circular dependencies detected</span>
                    </div>
                  )}
                </div>

                {/* Dead Code */}
                <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4">
                  <SectionHeader icon={Trash2} title="Dead Code" color="text-red-400" badge={dead_code?.risk_label} />
                  {dead_code?.count > 0 ? (
                    <div className="space-y-1.5">
                      <p className="text-xs text-slate-300">{dead_code.count} unreferenced symbol{dead_code.count !== 1 ? 's' : ''}</p>
                      {dead_code.unreferenced_symbols?.slice(0, 5).map((s, i) => (
                        <div key={i} className="flex items-center gap-2 text-[10px] text-red-200">
                          <span className="text-red-500">•</span>
                          <span className="font-mono">{s.symbol}</span>
                          <span className="text-slate-500">in {s.file}</span>
                        </div>
                      ))}
                      {dead_code.count > 5 && (
                        <p className="text-[10px] text-slate-500">…and {dead_code.count - 5} more</p>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <CheckCircle2 size={13} className="text-emerald-400" />
                      <span className="text-xs text-emerald-300">No unreferenced symbols found</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Row 3: Code Metrics + Anti-Patterns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                {/* Code Metrics */}
                <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-4">
                  <SectionHeader icon={BarChart2} title="Code Metrics" color="text-indigo-400" />
                  <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                    {[
                      ['SLOC',        (code_metrics?.total_sloc || 0).toLocaleString()],
                      ['Files',       code_metrics?.total_files || 0],
                      ['Functions',   code_metrics?.total_functions || 0],
                      ['Classes',     code_metrics?.total_classes || 0],
                      ['Avg CC',      code_metrics?.avg_complexity || 0],
                      ['Maint. Index', code_metrics?.maintainability_index || 0],
                    ].map(([label, val]) => (
                      <div key={label} className="flex justify-between px-2 py-1 rounded-lg bg-slate-800/40">
                        <span className="text-slate-400">{label}</span>
                        <span className="text-slate-200 font-semibold">{val}</span>
                      </div>
                    ))}
                  </div>
                  {code_metrics?.hotspot_files?.length > 0 && (
                    <>
                      <p className="text-[10px] font-semibold text-slate-400 uppercase mb-1.5">Hotspot Files</p>
                      {code_metrics.hotspot_files.slice(0, 4).map((f, i) => (
                        <div key={i} className="flex items-center gap-2 text-[10px] mb-1">
                          <span className="text-indigo-400 font-mono truncate flex-1">{f.name}</span>
                          <span className="text-slate-400 flex-shrink-0">CC={f.complexity}</span>
                        </div>
                      ))}
                    </>
                  )}
                  {code_metrics?.god_classes?.length > 0 && (
                    <div className="mt-2">
                      <p className="text-[10px] font-semibold text-amber-400 uppercase mb-1">God Classes ({code_metrics.god_classes.length})</p>
                      {code_metrics.god_classes.slice(0, 3).map((g, i) => (
                        <p key={i} className="text-[10px] text-amber-200 font-mono">{g}</p>
                      ))}
                    </div>
                  )}
                </div>

                {/* Anti-Patterns */}
                <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-4">
                  <SectionHeader icon={Shield} title="Anti-Patterns" color="text-rose-400" badge={anti_patterns?.risk_label} />
                  {anti_patterns?.patterns?.length > 0 ? (
                    <div className="space-y-1.5">
                      {anti_patterns.patterns.slice(0, 6).map((p, i) => (
                        <div key={i} className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold w-14 flex-shrink-0 ${
                            p.severity === 'CRITICAL' ? 'text-red-400' :
                            p.severity === 'HIGH'     ? 'text-orange-400' :
                            p.severity === 'MEDIUM'   ? 'text-amber-400' : 'text-slate-400'
                          }`}>{p.severity}</span>
                          <span className="text-[10px] text-slate-200 flex-1">{p.pattern}</span>
                          <span className="text-[10px] text-slate-400 flex-shrink-0">{p.affected_files}f · {p.total_count}x</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <CheckCircle2 size={13} className="text-emerald-400" />
                      <span className="text-xs text-emerald-300">No anti-patterns detected</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Row 4: DB Layer + Domain Graph */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                {/* Database Layer */}
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                  <SectionHeader icon={Database} title="Database Layer" color="text-emerald-400" badge={db_analysis?.risk_label} />
                  <div className="space-y-1.5 text-xs">
                    {[
                      ['DB Files',        db_analysis?.db_file_count || 0],
                      ['Raw SQL Files',   db_analysis?.raw_sql_file_count || 0],
                      ['Conn. Strings',   db_analysis?.connection_strings_found || 0],
                      ['SQL Concat.',     db_analysis?.sql_concatenation_count || 0],
                    ].map(([label, val]) => (
                      <div key={label} className="flex justify-between">
                        <span className="text-slate-400">{label}</span>
                        <span className={`font-semibold ${val > 0 ? 'text-amber-300' : 'text-emerald-300'}`}>{val}</span>
                      </div>
                    ))}
                    {db_analysis?.db_technologies?.length > 0 && (
                      <div className="mt-2">
                        <p className="text-[10px] font-semibold text-slate-400 uppercase mb-1">Technologies</p>
                        <div className="flex flex-wrap gap-1">
                          {db_analysis.db_technologies.map(t => (
                            <span key={t} className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-800/40 text-emerald-200 border border-emerald-600/30">{t}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {db_analysis?.orms_detected?.length > 0 && (
                      <div>
                        <p className="text-[10px] font-semibold text-slate-400 uppercase mb-1">ORMs</p>
                        <div className="flex flex-wrap gap-1">
                          {db_analysis.orms_detected.map(o => (
                            <span key={o} className="text-[10px] px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-200 border border-slate-600/30">{o}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Domain Graph */}
                <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
                  <SectionHeader icon={Network} title="Domain Dependency Graph" color="text-cyan-400" />
                  <DomainGraph nodes={domain_graph?.nodes} edges={domain_graph?.edges} />
                  <p className="text-[10px] text-slate-400 mt-2 text-center">
                    {domain_graph?.nodes?.length || 0} domains · {domain_graph?.edges?.length || 0} dependencies
                  </p>
                </div>
              </div>

              {/* Effort Estimation */}
              <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4">
                <SectionHeader icon={Zap} title="Effort Estimation" color="text-yellow-400" badge={effort?.risk_label} />
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                  {[
                    { label: 'Remediation Effort', value: `${effort?.estimated_effort_months || 0} months`, color: 'text-amber-300' },
                    { label: 'With AI (12× Accel.)', value: `${effort?.modernization_effort_months || 0} months`, color: 'text-emerald-300' },
                    { label: 'Rebuild Cost', value: `$${((effort?.debt_usd || 0) / 1000).toFixed(0)}k`, color: 'text-rose-300' },
                    { label: 'Quick Wins', value: `${effort?.quick_wins_files || 0} files`, color: 'text-blue-300' },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="rounded-xl bg-slate-800/40 border border-slate-700/30 py-3 px-2">
                      <p className={`text-sm font-bold ${color}`}>{value}</p>
                      <p className="text-[10px] text-slate-400 mt-1">{label}</p>
                    </div>
                  ))}
                </div>
                {effort?.benchmark_note && (
                  <p className="text-[10px] text-slate-400 mt-3 text-center">{effort.benchmark_note}</p>
                )}
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ── Progress Bar ──────────────────────────────────────────────────────────────

// Function: AnalysisProgress
function AnalysisProgress({ progress, message, currentModule, completedCount, totalCount }) {
  return (
    <div className="rounded-2xl border border-blue-500/30 bg-blue-500/5 p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-4 h-4 rounded-full border-2 border-blue-400 border-t-transparent animate-spin flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm font-semibold text-blue-200">Running Strat-Aqorynth Module Analysis</p>
          {currentModule && (
            <p className="text-xs text-blue-400 mt-0.5">
              Analysing: {currentModule}
              {totalCount > 0 && (
                <span className="ml-2 text-slate-400">· {completedCount}/{totalCount} done</span>
              )}
            </p>
          )}
        </div>
        <span className="text-xs font-semibold text-blue-300">{progress}%</span>
      </div>
      <div className="w-full bg-slate-700/50 rounded-full h-2">
        <motion.div
          className="bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full h-2"
          style={{ width: `${progress}%` }}
          transition={{ duration: 0.4 }}
        />
      </div>
      {message && <p className="text-xs text-slate-400 mt-2">{message}</p>}
    </div>
  )
}

// ── Main Component ────────────────────────────────────────────────────────────

// Function: Strat-AqorynthModulePanel
export default function Strat-AqorynthModulePanel({ jobId }) {
  const [modules, setModules] = useState([])
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [loadingModules, setLoadingModules] = useState(true)
  const [running, setRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressMsg, setProgressMsg] = useState('')
  const [currentModule, setCurrentModule] = useState(null)
  const [results, setResults] = useState([])
  const [error, setError] = useState(null)
  const [showOnlyProjects, setShowOnlyProjects] = useState(false)
  const pollRef = useRef(null)

  // Load modules when jobId changes (or on mount)
  useEffect(() => {
    setLoadingModules(true)
    setResults([])
    setSelectedIds(new Set())
    listStrat-AqorynthModules(jobId || undefined)
      .then(data => {
        setModules(data.modules || [])
      })
      .catch(() => setModules([]))
      .finally(() => setLoadingModules(false))
  }, [jobId])

  useEffect(() => {
    return () => pollRef.current?.cancel()
  }, [])

  const visibleModules = showOnlyProjects
    ? modules.filter(m => m.is_project)
    : modules

  const allSelected = visibleModules.length > 0 && visibleModules.every(m => selectedIds.has(m.path))

  // Function: toggleModule
  function toggleModule(path) {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(path)) next.delete(path); else next.add(path)
      return next
    })
  }

  // Function: selectAll
  function selectAll() {
    setSelectedIds(new Set(visibleModules.map(m => m.path)))
  }

  // Function: clearAll
  function clearAll() {
    setSelectedIds(new Set())
  }

  // Function: handleRunAnalysis
  async function handleRunAnalysis() {
    const selected = modules.filter(m => selectedIds.has(m.path))
    if (!selected.length) return

    setRunning(true)
    setError(null)
    setResults([])
    setProgress(0)
    setProgressMsg('Starting…')

    try {
      const { job_id } = await startStrat-AqorynthAnalysis(selected.map(m => ({ name: m.name, path: m.path })))
      const { promise, cancel } = streamStrat-AqorynthJob(job_id, (job) => {
        setProgress(job.progress || 0)
        setProgressMsg(job.message || '')
        setCurrentModule(job.current_module || null)
        // Show partial results as each module completes — don't wait for all done.
        if (job.results?.length > 0) {
          setResults(job.results)
        }
      })
      pollRef.current = { cancel }
      const finalJob = await promise
      setResults(finalJob.results || [])
    } catch (err) {
      setError(err.message || 'Analysis failed')
    } finally {
      setRunning(false)
      setCurrentModule(null)
    }
  }

  const selectedCount = modules.filter(m => selectedIds.has(m.path)).length

  return (
    <div className="space-y-6">

      {/* ── Feature Cards ── */}
      <div>
        <h3 className="text-sm font-semibold text-slate-300 mb-3">Analysis Capabilities</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {FEATURES.map(f => (
            <div key={f.title} className={`rounded-xl border p-3.5 ${f.bg}`}>
              <div className="flex items-start gap-2.5">
                <f.icon size={16} className={`${f.color} flex-shrink-0 mt-0.5`} />
                <div>
                  <p className="text-xs font-semibold text-slate-200">{f.title}</p>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{f.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Module Selector ── */}
      <div className="rounded-2xl border border-blue-500/30 bg-gradient-to-br from-blue-500/5 to-indigo-500/5 overflow-hidden">
        {/* Header */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-blue-500/20">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-600/20 border border-blue-500/30">
              <GitBranch size={14} className="text-blue-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-blue-200">Strat-Aqorynth Module Analysis</p>
              <p className="text-[11px] text-slate-400">
                Analyse each module independently
                {modules.length > 0 && ` — ${modules.length} modules · Full codebase coverage`}
              </p>
            </div>
          </div>
        </div>

        <div className="p-5 space-y-4">
          {/* Controls row */}
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs text-slate-400">Select modules to analyse:</span>
            <label className="flex items-center gap-1.5 cursor-pointer text-xs text-slate-400 hover:text-slate-200 transition-colors ml-auto">
              <input
                type="checkbox"
                checked={showOnlyProjects}
                onChange={e => setShowOnlyProjects(e.target.checked)}
                className="rounded accent-blue-500"
              />
              Projects only
            </label>
            <button
              onClick={allSelected ? clearAll : selectAll}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-600/50 bg-slate-800/50 text-slate-300 hover:bg-slate-700/50 transition-colors"
            >
              {allSelected ? 'Clear' : 'Select All'}
            </button>
            <button
              onClick={clearAll}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-600/50 bg-slate-800/50 text-slate-300 hover:bg-slate-700/50 transition-colors"
            >
              Clear
            </button>
          </div>

          {/* Module Grid */}
          {loadingModules ? (
            <div className="flex items-center justify-center py-8 gap-2 text-slate-400">
              <div className="w-4 h-4 rounded-full border-2 border-blue-400 border-t-transparent animate-spin" />
              <span className="text-sm">Discovering modules…</span>
            </div>
          ) : visibleModules.length === 0 ? (
            <p className="text-sm text-slate-500 py-4 text-center">No modules found.</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
              {visibleModules.map(m => {
                const isSelected = selectedIds.has(m.path)
                const isDone = running && results.some(r => r.module_path === m.path)
                const isScanning = running && isSelected && !isDone
                return (
                  <button
                    key={m.path}
                    onClick={() => !running && toggleModule(m.path)}
                    disabled={running}
                    className={`flex items-start gap-2 p-3 rounded-xl border text-left transition-all ${
                      isDone
                        ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-200'
                        : isScanning
                        ? 'border-blue-400/50 bg-blue-500/10 text-blue-200 animate-pulse'
                        : isSelected
                        ? 'border-blue-500/60 bg-blue-500/10 text-blue-200'
                        : 'border-slate-700/50 bg-slate-800/30 text-slate-300 hover:border-slate-500/50 hover:bg-slate-700/30'
                    }`}
                  >
                    <div className="mt-0.5 flex-shrink-0">
                      {isDone
                        ? <CheckCircle2 size={13} className="text-emerald-400" />
                        : isScanning
                        ? <div className="w-3 h-3 rounded-full border-2 border-blue-400 border-t-transparent animate-spin" />
                        : isSelected
                        ? <CheckSquare size={13} className="text-blue-400" />
                        : <Square size={13} className="text-slate-500" />
                      }
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold truncate">{m.name}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">{m.file_count} files</p>
                      {m.is_project && (
                        <span className="text-[9px] font-semibold text-emerald-400">PROJECT</span>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          )}

          {/* Footer: status + run button */}
          <div className="flex items-center justify-between pt-1">
            <p className="text-xs text-slate-400">
              {selectedCount > 0
                ? `${selectedCount} module${selectedCount !== 1 ? 's' : ''} selected`
                : 'Select one or more modules above to run ML analysis'}
            </p>
            <button
              onClick={handleRunAnalysis}
              disabled={selectedCount === 0 || running}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                selectedCount > 0 && !running
                  ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-900/40'
                  : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
              }`}
            >
              {running ? (
                <>
                  <div className="w-3.5 h-3.5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                  Analysing…
                </>
              ) : (
                <>
                  <Play size={13} />
                  Run Analysis
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* ── Progress ── */}
      {running && (
        <AnalysisProgress
          progress={progress}
          message={progressMsg}
          currentModule={currentModule}
          completedCount={results.length}
          totalCount={selectedCount}
        />
      )}

      {/* ── Error ── */}
      {error && (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/5 p-4 flex items-center gap-3">
          <XCircle size={16} className="text-red-400 flex-shrink-0" />
          <div>
            <p className="text-sm font-semibold text-red-300">Analysis failed</p>
            <p className="text-xs text-red-400 mt-0.5">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="ml-auto text-xs text-slate-500 hover:text-slate-300">Dismiss</button>
        </div>
      )}

      {/* ── Results (shown progressively as modules complete) ── */}
      {results.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            {running
              ? <div className="w-3.5 h-3.5 rounded-full border-2 border-blue-400 border-t-transparent animate-spin" />
              : <CheckCircle2 size={15} className="text-emerald-400" />
            }
            <h3 className="text-sm font-semibold text-slate-200">
              {running
                ? `${results.length} of ${selectedCount} module${selectedCount !== 1 ? 's' : ''} complete — more incoming…`
                : `Analysis Complete — ${results.length} module${results.length !== 1 ? 's' : ''}`
              }
            </h3>
          </div>
          <AnimatePresence initial={false}>
            {results.map((r, i) => (
              <motion.div
                key={r.module_name || i}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <ModuleResultCard result={r} />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  )
}
