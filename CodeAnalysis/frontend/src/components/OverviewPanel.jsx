// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * OverviewPanel.jsx
// Date: 2026-03-12
// ---------------------------------------------------------------------------
/**
 * OverviewPanel.jsx
 * ─────────────────
 * Enriched overview with three drill-down levels:
 *   L1 – KPI stripe + summary cards + charts
 *   L2 – bottom-sheet table  (DrillDownModal)
 *   L3 – full per-file detail (inside DrillDownModal row)
 *
 * Extra widgets:
 *   • Bad-Practices stacked bar  (per language)
 *   • Cross-language hotspot table  (top-N worst files)
 *   • Dependency vulnerability list  (from oss.details)
 */
import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as RTooltip, Legend, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  PieChart, Pie, Cell,
} from 'recharts'
import {
  HeartPulse, DollarSign, Cloud, Shield, TrendingUp, Leaf,
  AlertTriangle, ChevronDown, ChevronRight, ExternalLink,
  PackageOpen, Flame, GitBranch, FileCode2, Zap, Hash,
  AlignLeft, ArrowUpRight, Info,
} from 'lucide-react'
import ScoreRing     from './ScoreRing.jsx'
import MiniBar       from './MiniBar.jsx'
import DrillDownModal from './DrillDownModal.jsx'
import { riskColor, fmtNumber, fmtUSD } from '../utils.js'

// ─────────────────────────────────────────────────────────────────────────────
// Colour helpers
// ─────────────────────────────────────────────────────────────────────────────
const LANG_COLORS = ['#61dafb','#4ade80','#fb923c','#a78bfa','#f472b6','#38bdf8','#facc15','#34d399']

const RISK_DOT = { LOW: '#4ade80', MEDIUM: '#f59e0b', HIGH: '#f97316', CRITICAL: '#ef4444' }

// Function: scoreColor
const scoreColor = (v) =>
  v >= 80 ? '#4ade80' : v >= 60 ? '#facc15' : v >= 40 ? '#f97316' : '#ef4444'

// ─────────────────────────────────────────────────────────────────────────────
// Tiny reusable bits
// ─────────────────────────────────────────────────────────────────────────────
// Function: KpiTile
function KpiTile({ icon: Icon, label, value, sub, color = '#61dafb', onClick }) {
  return (
    <motion.button
      whileHover={onClick ? { scale: 1.03 } : {}}
      onClick={onClick}
      className={`glass px-4 py-3 flex items-center gap-3 text-left rounded-xl
                  ${onClick ? 'cursor-pointer hover:border-brand-cyan/40' : 'cursor-default'}`}
    >
      <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
           style={{ background: color + '18' }}>
        <Icon size={16} style={{ color }} />
      </div>
      <div className="min-w-0">
        <div className="text-[11px] text-blue-500">{label}</div>
        <div className="text-lg font-bold text-blue-300 leading-tight">{value}</div>
        {sub && <div className="text-[10px] text-blue-500 truncate">{sub}</div>}
      </div>
      {onClick && <ArrowUpRight size={12} className="ml-auto text-blue-600 flex-shrink-0" />}
    </motion.button>
  )
}

// Function: SectionHeader
function SectionHeader({ title, subtitle, badge }) {
  return (
    <div className="flex items-center gap-3 mb-3">
      <h3 className="text-sm font-semibold text-blue-200">{title}</h3>
      {badge && (
        <span className="text-[10px] bg-surface px-2 py-0.5 rounded-full border border-surface-border text-blue-500">
          {badge}
        </span>
      )}
      {subtitle && <span className="text-[11px] text-blue-500 ml-1">{subtitle}</span>}
    </div>
  )
}

// Function: RiskPill
function RiskPill({ label }) {
  const rc = riskColor(label)
  return (
    <span className={`pill text-[10px] ${rc.bg} ${rc.text} border ${rc.border}`}>{label}</span>
  )
}

/** Tooltip for recharts */
// Function: ChartTip
function ChartTip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass px-3 py-2 text-xs space-y-1 rounded-xl">
      <p className="font-semibold text-blue-300 mb-1">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: p.fill || p.color }} />
          <span className="text-blue-400">{p.name}:</span>
          <span className="text-blue-300 font-mono">{typeof p.value === 'number' ? p.value.toFixed(1) : p.value}</span>
        </div>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Summary cards (L1) — with click → opens L2 DrillDownModal
// ─────────────────────────────────────────────────────────────────────────────
// Function: SummaryCard
function SummaryCard({ icon: Icon, title, score, riskLabel, children, onDrillDown, accentColor = '#61dafb' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
      className="glass p-5 flex flex-col gap-4"
    >
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
             style={{ background: accentColor + '18' }}>
          <Icon size={15} style={{ color: accentColor }} />
        </div>
        <span className="text-sm font-semibold text-blue-300 flex-1">{title}</span>
        {riskLabel && <RiskPill label={riskLabel} />}
      </div>

      <div className="flex items-center gap-5">
        {score != null && (
          <ScoreRing value={score} size={100} stroke={9} label="/100" />
        )}
        <div className="flex-1 min-w-0">{children}</div>
      </div>

      {onDrillDown && (
        <button
          onClick={onDrillDown}
          className="mt-auto flex items-center gap-1.5 text-[11px] text-blue-500 hover:text-brand-cyan
                     transition-colors border-t border-surface-border pt-3 w-full"
        >
          <ArrowUpRight size={11} /> View per-file breakdown (L2 →)
        </button>
      )}
    </motion.div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Hotspot table — top files ranked by weighted score
// ─────────────────────────────────────────────────────────────────────────────
// Function: HotspotTable
// Function: tierColor
function tierColor(value, tiers, defaultColor) {
  for (const [threshold, color] of tiers) {
    if (value > threshold) return color
  }
  return defaultColor
}

// Function: HotspotFileName
function HotspotFileName({ name }) {
  const pts = name.split('/')
  return (
    <span title={name}>
      <span className="text-blue-500 text-[10px]">{pts.slice(0, -1).join('/') + (pts.length > 1 ? '/' : '')}</span>
      <span className="text-blue-300 font-semibold">{pts[pts.length - 1]}</span>
    </span>
  )
}

// Function: HotspotRow
function HotspotRow({ f, i, isExpanded, onToggle }) {
  const cc   = f.complexity ?? 0
  const ccColor = tierColor(cc, [[20, '#ef4444'], [10, '#f97316'], [5, '#f59e0b']], '#4ade80')
  const score = Math.round(f._score)
  const sColor = tierColor(score, [[100, '#ef4444'], [50, '#f97316']], '#f59e0b')
  const longMethodsColor = tierColor(f.long_methods, [[0, '#f59e0b']], '#4b5563')
  const deepNestingColor = tierColor(f.deep_nesting, [[10, '#ef4444'], [3, '#f59e0b']], '#4b5563')
  const magicNumbersColor = tierColor(f.magic_numbers, [[5, '#f59e0b']], '#4b5563')
  const todoColor = tierColor(f.todo_comments, [[0, '#60a5fa']], '#4b5563')
  return (
    <React.Fragment key={f.name + '-' + i}>
      <tr
        onClick={onToggle}
        className={`border-b border-surface-border cursor-pointer transition-colors group
                    ${isExpanded ? 'bg-surface' : 'hover:bg-surface-hover'}`}
      >
        <td className="px-3 py-2 text-blue-600 font-mono">{i + 1}</td>
        <td className="px-3 py-2 font-mono max-w-[200px]"><HotspotFileName name={f.name} /></td>
        <td className="px-3 py-2">
          <span className="text-[10px] bg-surface border border-surface-border rounded px-1.5 py-0.5 text-blue-400">
            {f.language}
          </span>
        </td>
        <td className="px-3 py-2 font-mono text-blue-400">{fmtNumber(f.sloc)}</td>
        <td className="px-3 py-2 font-mono font-semibold" style={{ color: ccColor }}>{cc}</td>
        <td className="px-3 py-2 font-mono" style={{ color: longMethodsColor }}>{f.long_methods}</td>
        <td className="px-3 py-2 font-mono" style={{ color: deepNestingColor }}>{f.deep_nesting}</td>
        <td className="px-3 py-2 font-mono" style={{ color: magicNumbersColor }}>{f.magic_numbers}</td>
        <td className="px-3 py-2 font-mono" style={{ color: todoColor }}>{f.todo_comments}</td>
        <td className="px-3 py-2 font-mono font-bold" style={{ color: sColor }}>{score}</td>
      </tr>

      {/* L3 inline file detail */}
      {isExpanded && (
        <tr>
          <td colSpan={10} className="bg-surface px-5 pb-4">
            <FileDetailInline file={f} onClose={onToggle} />
          </td>
        </tr>
      )}
    </React.Fragment>
  )
}

// Function: HotspotTable
function HotspotTable({ languageReports, onFileClick }) {
  const [expanded, setExpanded] = useState(null)

  const hotspots = useMemo(() => {
    const out = []
    for (const lr of languageReports ?? []) {
      for (const f of lr.files ?? []) {
        const cc   = f.complexity   ?? 0
        const sloc = f.sloc         ?? 0
        const lm   = f.long_methods ?? 0
        const dn   = f.deep_nesting ?? 0
        const score = cc * 3 + sloc / 200 + lm * 4 + dn * 0.5
        out.push({ ...f, language: lr.language, _score: score })
      }
    }
    return out.sort((a, b) => b._score - a._score).slice(0, 12)
  }, [languageReports])

  if (!hotspots.length) return null

  return (
    <div className="glass p-5">
      <SectionHeader
        title="🔥 Code Hotspots"
        subtitle="— top 12 most complex files ranked by cyclomatic × SLOC × bad-practices"
        badge={`${hotspots.length} files`}
      />
      <div className="overflow-x-auto">
        <table className="w-full text-xs min-w-[640px]">
          <thead>
            <tr className="border-b border-surface-border text-blue-500">
              {['#', 'File', 'Lang', 'SLOC', 'CC', 'Long', 'Nesting', 'Magic#', 'TODO', 'Debt Score'].map(h => (
                <th key={h} className="px-3 py-2 text-left font-medium whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {hotspots.map((f, i) => (
              <HotspotRow
                key={f.name + '-' + i}
                f={f} i={i}
                isExpanded={expanded === i}
                onToggle={() => setExpanded(expanded === i ? null : i)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

/** Inline L3 file card — replicates DrillDownModal's FileDetailCard */
// Function: FileDetailInline
function FileDetailInline({ file, onClose }) {
  const cc = file.complexity ?? 0
  const ccColor = cc > 20 ? 'text-red-400' : cc > 10 ? 'text-orange-400' : cc > 5 ? 'text-amber-400' : 'text-emerald-400'
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 6 }}
      className="mt-3 border border-surface-border rounded-xl p-4 relative bg-[#0d1117]"
    >
      <button onClick={onClose}
        className="absolute top-2 right-2 text-blue-500 hover:text-white text-xs px-2 py-0.5 rounded border border-surface-border">
        ✕ Close
      </button>
      <div className="text-[11px] font-mono text-brand-cyan mb-3 pr-14">{file.name}</div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-6 gap-y-0 text-xs">
        {[
          ['SLOC',          file.sloc?.toLocaleString()],
          ['Total Lines',   file.total_lines?.toLocaleString()],
          ['Comment Lines', file.comment_lines?.toLocaleString()],
          ['Blank Lines',   file.blank_lines?.toLocaleString()],
          ['Comment Ratio', file.comment_ratio?.toFixed(3)],
          ['Complexity CC', <span className={ccColor}>{cc}</span>],
          ['Functions',     file.functions],
          ['Classes',       file.classes],
          ['Long Methods',  <span className={file.long_methods > 0 ? 'text-amber-400' : ''}>{file.long_methods}</span>],
          ['Deep Nesting',  <span className={file.deep_nesting > 10 ? 'text-red-400' : file.deep_nesting > 3 ? 'text-amber-400' : ''}>{file.deep_nesting}</span>],
          ['Magic Numbers', <span className={file.magic_numbers > 5 ? 'text-amber-400' : ''}>{file.magic_numbers}</span>],
          ['TODO / FIXME',  <span className={file.todo_comments > 0 ? 'text-blue-400' : ''}>{file.todo_comments}</span>],
        ].map(([label, val], i) => (
          <div key={i} className="flex justify-between items-center py-1 border-b border-surface-border">
            <span className="text-blue-500">{label}</span>
            <span className="font-mono font-medium text-blue-200">{val}</span>
          </div>
        ))}
      </div>
      {file.error && <p className="mt-2 text-xs text-red-400">⚠ {file.error}</p>}
    </motion.div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Bad-Practices bar chart
// ─────────────────────────────────────────────────────────────────────────────
// Function: BadPracticesChart
function BadPracticesChart({ languageReports }) {
  const data = (languageReports ?? []).map(lr => ({
    lang:          lr.language,
    'Long Methods':  +(lr.long_methods_pct ?? 0).toFixed(1),
    'Deep Nesting':  +(lr.deep_nesting_pct ?? 0).toFixed(1),
    'Comment Gap':   +(Math.max(0, 30 - (lr.comment_ratio ?? 0) * 100)).toFixed(1),
  }))

  if (!data.length) return null
  return (
    <div className="glass p-5">
      <SectionHeader title="Bad-Practices Breakdown" subtitle="(% of files per language)" />
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 0, right: 10, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="lang" tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} unit="%" />
          <RTooltip content={<ChartTip />} />
          <Legend wrapperStyle={{ fontSize: 11, color: '#9ca3af' }} />
          <Bar dataKey="Long Methods" stackId="a" fill="#f97316" radius={[0,0,0,0]} />
          <Bar dataKey="Deep Nesting" stackId="a" fill="#ef4444" radius={[0,0,0,0]} />
          <Bar dataKey="Comment Gap"  stackId="a" fill="#6366f1" radius={[4,4,0,0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Language breakdown — collapsible per-language rows → L2 drill-down
// ─────────────────────────────────────────────────────────────────────────────
// Function: TopComplexFileRow
function TopComplexFileRow({ f, fi, lr, onDrillDown }) {
  const cc = f.complexity ?? 0
  const ccC = tierColor(cc, [[20, '#ef4444'], [10, '#f97316'], [5, '#f59e0b']], '#4ade80')
  const fname = f.name.split('/').pop()
  return (
    <div
      onClick={() => onDrillDown(lr, 'complexity')}
      className="flex items-center gap-3 text-xs px-3 py-1.5 rounded-lg
                 bg-surface-hover cursor-pointer hover:bg-surface border border-transparent
                 hover:border-surface-border transition-all group">
      <span className="text-blue-500 w-4 text-right">{fi + 1}</span>
      <span className="font-mono text-blue-300 flex-1 truncate">{fname}</span>
      <span className="font-mono text-blue-500">{fmtNumber(f.sloc)} SLOC</span>
      <span className="font-mono font-bold text-xs" style={{ color: ccC }}>CC {cc}</span>
      {f.long_methods > 0 && (
        <span className="text-[9px] text-amber-500 bg-amber-500/10 px-1 rounded">
          {f.long_methods} long
        </span>
      )}
    </div>
  )
}

// Function: LanguageRowDependencies
function LanguageRowDependencies({ lr }) {
  if ((lr.dependencies?.length ?? 0) === 0) return null
  return (
    <div>
      <div className="text-[10px] text-blue-500 uppercase tracking-wider mb-1.5">
        Dependencies ({lr.dependencies.length})
      </div>
      <div className="flex flex-wrap gap-1.5">
        {lr.dependencies.slice(0, 20).map(dep => (
          <span key={dep}
            className="text-[10px] bg-surface border border-surface-border rounded-full px-2 py-0.5 text-blue-400">
            {dep}
          </span>
        ))}
        {lr.dependencies.length > 20 && (
          <span className="text-[10px] text-blue-600">+{lr.dependencies.length - 20} more</span>
        )}
      </div>
    </div>
  )
}

// Function: LanguageRowExpanded
function LanguageRowExpanded({ lr, onDrillDown }) {
  return (
    <div className="border-t border-surface-border px-4 py-4 space-y-4">

      {/* Metric tiles */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {[
          { label: 'Total Functions',  v: lr.total_functions  ?? 0, color: '#61dafb' },
          { label: 'Total Classes',    v: lr.total_classes    ?? 0, color: '#a78bfa' },
          { label: 'Max Complexity',   v: lr.max_complexity   ?? 0, color: lr.max_complexity > 20 ? '#ef4444' : '#4ade80' },
          { label: 'Long Meth. %',     v: (lr.long_methods_pct ?? 0).toFixed(1) + '%', color: '#f97316' },
          { label: 'Deep Nest. %',     v: (lr.deep_nesting_pct ?? 0).toFixed(1) + '%', color: '#ef4444' },
          { label: 'Comment Ratio',    v: (lr.comment_ratio    ?? 0).toFixed(3), color: '#4ade80' },
          { label: 'Avg Complexity',   v: (lr.avg_complexity   ?? 0).toFixed(1), color: '#f59e0b' },
          { label: 'Dependencies',     v: lr.dependencies?.length ?? 0, color: '#38bdf8' },
        ].map(({ label, v, color }) => (
          <div key={label} className="bg-surface border border-surface-border rounded-lg px-3 py-2">
            <div className="text-[10px] text-blue-500 mb-0.5">{label}</div>
            <div className="text-base font-bold font-mono" style={{ color }}>{v}</div>
          </div>
        ))}
      </div>

      {/* Top 5 worst files */}
      <div>
        <div className="text-[10px] text-blue-500 uppercase tracking-wider mb-2 flex items-center justify-between">
          <span>Top 5 Complex Files</span>
          <button
            onClick={() => onDrillDown(lr, 'complexity')}
            className="text-brand-cyan hover:underline"
          >
            View all {lr.file_count} files →
          </button>
        </div>
        <div className="space-y-1">
          {[...(lr.files ?? [])]
            .sort((a, b) => (b.complexity ?? 0) - (a.complexity ?? 0))
            .slice(0, 5)
            .map((f, fi) => (
              <TopComplexFileRow key={fi} f={f} fi={fi} lr={lr} onDrillDown={onDrillDown} />
            ))}
        </div>
      </div>

      {/* Dependencies */}
      <LanguageRowDependencies lr={lr} />
    </div>
  )
}

// Function: LanguageRow
function LanguageRow({ lr, i, total, isOpen, onToggle, onDrillDown }) {
  const pct = total > 0 ? ((lr.total_sloc / total) * 100).toFixed(1) : '0'
  const col = LANG_COLORS[i % LANG_COLORS.length]
  const ccColor = tierColor(lr.avg_complexity, [[15, '#ef4444'], [8, '#f59e0b']], '#4ade80')
  return (
    <div className="border border-surface-border rounded-xl overflow-hidden">
      {/* Row header — changed outer to div to avoid button-in-button */}
      <div
        role="button"
        tabIndex={0}
        onClick={onToggle}
        onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && onToggle()}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-surface-hover transition-colors text-left cursor-pointer"
      >
        <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: col }} />
        <span className="text-sm font-semibold text-blue-300 flex-1">{lr.language}</span>

        <div className="flex items-center gap-4 text-xs text-blue-400 flex-wrap">
          <span>{fmtNumber(lr.total_sloc)} <span className="text-blue-600">SLOC</span></span>
          <span>{lr.file_count} <span className="text-blue-600">files</span></span>
          <span>{lr.total_functions ?? 0} <span className="text-blue-600">fns</span></span>
          <span className="font-mono" style={{ color: ccColor }}>
            CC&nbsp;{lr.avg_complexity?.toFixed(1)}
          </span>
          <span className="hidden sm:inline">{pct}%</span>
        </div>

        {/* SLOC bar */}
        <div className="hidden sm:block w-28 h-1.5 rounded-full bg-surface-border overflow-hidden flex-shrink-0 mx-2">
          <div className="h-full rounded-full" style={{ width: pct + '%', background: col }} />
        </div>

        {/* Drill-down button — kept as real button, click stops propagation */}
        <button
          onClick={e => { e.stopPropagation(); onDrillDown(lr, 'complexity') }}
          className="hidden sm:flex items-center gap-1 text-[10px] text-blue-500 hover:text-brand-cyan
                     border border-surface-border rounded px-2 py-1 transition-colors flex-shrink-0"
        >
          <FileCode2 size={10} /> L2
        </button>

        {isOpen ? <ChevronDown size={14} className="text-blue-500 flex-shrink-0" />
                : <ChevronRight size={14} className="text-blue-500 flex-shrink-0" />}
      </div>

      {/* Expanded: mini metric grid + top files */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <LanguageRowExpanded lr={lr} onDrillDown={onDrillDown} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Function: LanguageBreakdown
function LanguageBreakdown({ languageReports, onDrillDown }) {
  const [open, setOpen] = useState(new Set())
  const toggle = lang => setOpen(s => {
    const n = new Set(s)
    n.has(lang) ? n.delete(lang) : n.add(lang)
    return n
  })

  const total = (languageReports ?? []).reduce((s, r) => s + (r.total_sloc ?? 0), 0)

  return (
    <div className="glass p-5">
      <SectionHeader title="Language Breakdown" subtitle="click row to expand · L2 for per-file detail" />
      <div className="space-y-2">
        {(languageReports ?? []).map((lr, i) => (
          <LanguageRow
            key={lr.language}
            lr={lr} i={i} total={total}
            isOpen={open.has(lr.language)}
            onToggle={() => toggle(lr.language)}
            onDrillDown={onDrillDown}
          />
        ))}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// OSS Dependency vulnerability list  (L2 inline expansion)
// ─────────────────────────────────────────────────────────────────────────────
// Function: DepVulnList
function DepVulnList({ oss }) {
  const [showAll, setShowAll] = useState(false)
  const details = oss?.details ?? []
  if (!details.length) return null

  const sorted = [...details].sort((a, b) => {
    const rank = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 }
    const ra = rank[b.cve_severity] ?? 0
    const rb = rank[a.cve_severity] ?? 0
    return ra - rb || (b.vulnerable ? 1 : 0) - (a.vulnerable ? 1 : 0)
  })
  const visible = showAll ? sorted : sorted.slice(0, 8)

  const SEV = { CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#f59e0b', LOW: '#94a3b8' }

  return (
    <div className="glass p-5">
      <SectionHeader
        title="OSS Dependency Inventory"
        badge={`${details.length} packages`}
        subtitle={`— ${oss.vulnerable_count ?? 0} vulnerable, ${oss.license_issues ?? 0} license issues`}
      />
      <div className="overflow-x-auto">
        <table className="w-full text-xs min-w-[540px]">
          <thead>
            <tr className="border-b border-surface-border text-blue-500">
              {['Package', 'Ecosystem', 'License', 'License Risk', 'Age (yrs)', 'CVE Sev', 'CVEs', 'Status'].map(h => (
                <th key={h} className="px-3 py-2 text-left font-medium whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visible.map((dep, i) => (
              <tr key={dep.name + i}
                className="border-b border-surface-border hover:bg-surface-hover transition-colors">
                <td className="px-3 py-2 font-mono text-blue-300 font-semibold">{dep.name}</td>
                <td className="px-3 py-2 text-blue-400">{dep.ecosystem}</td>
                <td className="px-3 py-2 text-blue-400 font-mono text-[10px]">{dep.license || '—'}</td>
                <td className="px-3 py-2">
                  <span className="text-[10px] rounded px-1.5 py-0.5"
                    style={{
                      background: dep.license_risk === 'HIGH' ? '#450a0a' : dep.license_risk === 'MEDIUM' ? '#431407' : '#0f172a',
                      color:      dep.license_risk === 'HIGH' ? '#fca5a5' : dep.license_risk === 'MEDIUM' ? '#fcd34d' : '#94a3b8',
                    }}>
                    {dep.license_risk || 'LOW'}
                  </span>
                </td>
                <td className="px-3 py-2 font-mono text-blue-400">
                  {dep.age_years != null ? dep.age_years : '—'}
                  {dep.age_ok === false && <span className="ml-1 text-amber-500">⚠</span>}
                </td>
                <td className="px-3 py-2 font-mono font-bold"
                  style={{ color: SEV[dep.cve_severity] || '#4b5563' }}>
                  {dep.cve_severity || '—'}
                </td>
                <td className="px-3 py-2 font-mono">
                  <span className={dep.vuln_count > 0 ? 'text-red-400 font-bold' : 'text-blue-600'}>
                    {dep.vuln_count ?? 0}
                  </span>
                  {dep.cve_ids?.length > 0 && (
                    <span className="ml-1 text-[10px] text-blue-500" title={dep.cve_ids.join(', ')}>
                      [{dep.cve_ids.slice(0,2).join(', ')}{dep.cve_ids.length > 2 ? `…+${dep.cve_ids.length - 2}` : ''}]
                    </span>
                  )}
                </td>
                <td className="px-3 py-2">
                  {dep.vulnerable
                    ? <span className="text-[10px] bg-red-900/30 text-red-400 border border-red-700/40 rounded px-1.5 py-0.5">Vulnerable</span>
                    : <span className="text-[10px] text-emerald-500">✓ Safe</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {sorted.length > 8 && (
        <button
          onClick={() => setShowAll(s => !s)}
          className="mt-3 text-xs text-blue-500 hover:text-brand-cyan transition-colors">
          {showAll ? '▲ Show less' : `▼ Show all ${sorted.length} packages`}
        </button>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Complexity distribution bar
// ─────────────────────────────────────────────────────────────────────────────
// Function: ComplexityDistChart
function ComplexityDistChart({ languageReports }) {
  const buckets = useMemo(() => {
    const b = { '1-5': 0, '6-10': 0, '11-20': 0, '21-50': 0, '50+': 0 }
    for (const lr of languageReports ?? []) {
      for (const f of lr.files ?? []) {
        const cc = f.complexity ?? 0
        if (cc <= 5) b['1-5']++
        else if (cc <= 10) b['6-10']++
        else if (cc <= 20) b['11-20']++
        else if (cc <= 50) b['21-50']++
        else b['50+']++
      }
    }
    return Object.entries(b).map(([name, count]) => ({ name, count }))
  }, [languageReports])

  const BCOL = { '1-5': '#4ade80', '6-10': '#a3e635', '11-20': '#f59e0b', '21-50': '#f97316', '50+': '#ef4444' }

  return (
    <div className="glass p-5">
      <SectionHeader title="Complexity Distribution" subtitle="— files by cyclomatic complexity (CC) bucket" />
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={buckets} margin={{ top: 0, right: 10, bottom: 0, left: -10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} allowDecimals={false} />
          <RTooltip content={<ChartTip />} />
          <Bar dataKey="count" name="Files" radius={[4, 4, 0, 0]}
            label={false}
          >
            {buckets.map((b, i) => <Cell key={i} fill={BCOL[b.name]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Radar + Language pie (moved from ChartsSection)
// ─────────────────────────────────────────────────────────────────────────────
// Function: RadarAndPie
function RadarAndPie({ result }) {
  const { health, debt, cloud, oss, impact, language_reports = [] } = result

  const radarData = [
    { subject: 'Health',     score: health?.health    ?? 0 },
    { subject: 'Debt (inv)', score: 100 - (debt?.debt_ratio ?? 0) },
    { subject: 'Cloud',      score: cloud?.total      ?? 0 },
    { subject: 'OSS Safety', score: oss?.total        ?? 0 },
    { subject: 'Biz Impact', score: impact?.total     ?? 0 },
  ]

  const pieData = language_reports.map(r => ({ name: r.language, value: r.total_sloc }))

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <div className="glass p-5">
        <SectionHeader title="Portfolio Radar" />
        <ResponsiveContainer width="100%" height={240}>
          <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
            <PolarGrid gridType="polygon" stroke="#2a2d3e" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 12 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }} />
            <Radar name="Score" dataKey="score" stroke="#61dafb" fill="#61dafb" fillOpacity={0.15} strokeWidth={2} />
            <RTooltip content={<ChartTip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="glass p-5">
        <SectionHeader title="Language Breakdown (SLOC)" />
        {pieData.length === 0
          ? <div className="h-[240px] flex items-center justify-center text-blue-600 text-sm">No language data</div>
          : (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                  paddingAngle={3} dataKey="value">
                  {pieData.map((_, i) => <Cell key={i} fill={LANG_COLORS[i % LANG_COLORS.length]} />)}
                </Pie>
                <RTooltip content={<ChartTip />} />
                <Legend wrapperStyle={{ fontSize: 11, color: '#9ca3af' }} />
              </PieChart>
            </ResponsiveContainer>
          )}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Main export
// ─────────────────────────────────────────────────────────────────────────────
// Function: KpiStripe
function KpiStripe({ r, avgCC, maxCC, totalFunctions, totalClasses, totalDeps, lr, openDrill }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <KpiTile icon={FileCode2} label="Source Lines (SLOC)" value={fmtNumber(r.total_sloc ?? r.sloc)} color="#61dafb" />
      <KpiTile icon={AlignLeft}  label="Total Files"         value={fmtNumber(r.total_files ?? r.file_count)} color="#a78bfa" />
      <KpiTile icon={GitBranch}  label="Avg Complexity"       value={avgCC} sub={`max ${maxCC}`}
        color={avgCC > 15 ? '#ef4444' : avgCC > 8 ? '#f59e0b' : '#4ade80'}
        onClick={lr[0] ? () => openDrill(lr.reduce((b,l) => (l.avg_complexity??0) > (b.avg_complexity??0) ? l : b, lr[0]), 'complexity') : null}
      />
      <KpiTile icon={Zap}        label="Total Functions"      value={fmtNumber(totalFunctions)} color="#06b6d4"
        onClick={lr[0] ? () => openDrill(lr[0], 'functions') : null}
      />
      <KpiTile icon={Hash}       label="Total Classes"        value={fmtNumber(totalClasses)}   color="#f472b6" />
      <KpiTile icon={PackageOpen} label="Dependencies"        value={fmtNumber(totalDeps)} sub={`${r.oss?.vulnerable_count ?? 0} vuln`}
        color={r.oss?.vulnerable_count > 0 ? '#ef4444' : '#4ade80'}
        onClick={() => document.getElementById('dep-section')?.scrollIntoView({ behavior: 'smooth' })}
      />
    </div>
  )
}

// Function: HealthSummaryCard
function HealthSummaryCard({ r, lr, openDrill }) {
  return (
    <SummaryCard
      icon={HeartPulse} title="Software Health"
      score={r.health?.health} riskLabel={r.health?.risk_label}
      accentColor="#4ade80"
      onDrillDown={lr[0] ? () => openDrill(lr[0], 'complexity') : null}
    >
      <div className="space-y-2.5">
        <MiniBar label="Resiliency" value={r.health?.resiliency} />
        <MiniBar label="Agility"    value={r.health?.agility} />
        <MiniBar label="Elegance"   value={r.health?.elegance} />
      </div>
      {r.health?.summary?.slice(0, 3).map((s, i) => (
        <p key={i} className="text-[10px] text-blue-400 border-l border-amber-500/30 pl-2 mt-1">{s}</p>
      ))}
    </SummaryCard>
  )
}

// Function: DebtSummaryCard
function DebtSummaryCard({ r, lr, openDrill }) {
  return (
    <SummaryCard
      icon={DollarSign} title="Technical Debt"
      score={Math.max(0, 100 - (r.debt?.debt_ratio ?? 0))} riskLabel={r.debt?.risk_label}
      accentColor="#f97316"
      onDrillDown={lr[0] ? () => openDrill(lr[0], 'sloc') : null}
    >
      <div className="text-3xl font-extrabold text-blue-300 leading-tight mb-2">
        {r.debt?.debt_months} <span className="text-sm font-normal text-blue-400">person-months</span>
      </div>
      <div className="space-y-1.5 text-xs text-blue-400">
        {[
          ['Est. Cost',    fmtUSD(r.debt?.debt_usd)],
          ['FTEs',         r.debt?.debt_ftes],
          ['Density',      (r.debt?.density ?? 0) + ' PM/kLOC'],
          ['Debt Ratio',   (r.debt?.debt_ratio ?? 0) + '%'],
        ].map(([k, v]) => (
          <div key={k} className="flex justify-between border-b border-surface-border pb-1">
            <span className="text-blue-500">{k}</span>
            <span className="font-mono text-blue-200">{v}</span>
          </div>
        ))}
      </div>
    </SummaryCard>
  )
}

// Function: CloudSummaryCard
function CloudSummaryCard({ r, onTabChange }) {
  return (
    <SummaryCard
      icon={Cloud} title="Cloud Maturity"
      score={r.cloud?.total} riskLabel={r.cloud?.risk_label}
      accentColor="#38bdf8"
      onDrillDown={() => onTabChange?.('cloud')}
    >
      <div className="space-y-2">
        {[
          ['Stateless Design',    r.cloud?.stateless_design],
          ['Containerization',    r.cloud?.containerization],
          ['API Surface',         r.cloud?.api_surface],
          ['Config Extern.',      r.cloud?.config_externalization],
        ].map(([k, v]) => (
          <MiniBar key={k} label={k} value={v} />
        ))}
      </div>
    </SummaryCard>
  )
}

// Function: OSSCveBadges
function OSSCveBadges({ r }) {
  if (!(r.oss?.cve_critical > 0 || r.oss?.cve_high > 0)) return null
  return (
    <div className="mt-2 flex gap-2">
      {r.oss?.cve_critical > 0 && (
        <span className="text-[10px] bg-red-900/40 text-red-400 border border-red-700/40 rounded px-2 py-0.5">
          {r.oss.cve_critical} CRITICAL
        </span>
      )}
      {r.oss?.cve_high > 0 && (
        <span className="text-[10px] bg-orange-900/40 text-orange-400 border border-orange-700/40 rounded px-2 py-0.5">
          {r.oss.cve_high} HIGH
        </span>
      )}
    </div>
  )
}

// Function: OSSSummaryCard
function OSSSummaryCard({ r }) {
  return (
    <SummaryCard
      icon={Shield} title="OSS Safety"
      score={r.oss?.total} riskLabel={r.oss?.risk_label}
      accentColor="#a78bfa"
      onDrillDown={() => document.getElementById('dep-section')?.scrollIntoView({ behavior: 'smooth' })}
    >
      <div className="grid grid-cols-2 gap-2 text-center">
        {[
          { l: 'Total Deps',  v: r.oss?.dependency_count,  c: 'text-blue-300' },
          { l: 'Vulnerable',  v: r.oss?.vulnerable_count,  c: r.oss?.vulnerable_count > 0 ? 'text-red-400' : 'text-emerald-400' },
          { l: 'Lic. Issues', v: r.oss?.license_issues,    c: r.oss?.license_issues   > 0 ? 'text-amber-400' : 'text-blue-400' },
          { l: 'Stale',       v: r.oss?.stale_count,       c: 'text-blue-400' },
        ].map(({ l, v, c }) => (
          <div key={l} className="bg-surface rounded-lg p-2">
            <div className={`text-lg font-bold ${c}`}>{v ?? 0}</div>
            <div className="text-[10px] text-blue-500">{l}</div>
          </div>
        ))}
      </div>
      {/* CVE summary */}
      <OSSCveBadges r={r} />
    </SummaryCard>
  )
}

// Function: ImpactSummaryCard
function ImpactSummaryCard({ r }) {
  return (
    <SummaryCard
      icon={TrendingUp} title="Business Impact"
      score={r.impact?.total} riskLabel={r.impact?.risk_label}
      accentColor="#3b82f6"
      onDrillDown={null}
    >
      <div className="space-y-2">
        {[
          ['User Volume',   r.impact?.user_volume_score],
          ['Release Freq.', r.impact?.release_freq_score],
          ['Revenue',       r.impact?.revenue_score],
          ['Age Risk',      r.impact?.age_risk_score],
        ].map(([k, v]) => (
          <MiniBar key={k} label={k} value={v} />
        ))}
      </div>
    </SummaryCard>
  )
}

// Function: CO2SummaryCard
function CO2SummaryCard({ r, onTabChange }) {
  return (
    <SummaryCard
      icon={Leaf} title="CO₂ Reduction Potential"
      score={null} riskLabel={null}
      accentColor="#4ade80"
      onDrillDown={() => onTabChange?.('co2')}
    >
      <div className="flex flex-col gap-2">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-extrabold text-emerald-400">
            {r.co2?.co2_tons_year?.toFixed(2) ?? '—'}
          </span>
          <span className="text-sm text-blue-400">tons CO₂/year</span>
        </div>
        <div className="text-xs text-blue-400">
          Cloud gap: <span className="text-blue-300 font-mono">{r.co2?.cloud_gap_pct?.toFixed(0) ?? '—'}%</span>
        </div>
        <div className="text-xs text-blue-400">
          Electricity saved: <span className="text-blue-300 font-mono">{r.co2?.electricity_mwh?.toFixed(1) ?? '—'} MWh/yr</span>
        </div>
        <div className="text-xs text-blue-400">
          Est. servers: <span className="text-blue-300 font-mono">{r.co2?.estimated_servers ?? '—'} on-prem</span>
        </div>
      </div>
    </SummaryCard>
  )
}

// Function: OverviewPanel
export default function OverviewPanel({ result, onTabChange }) {
  const [drill, setDrill]     = useState(null) // { language, metric, files }
  const [expanded, setExpanded] = useState(null) // card key

  if (!result) return null
  const r = result
  const lr = r.language_reports ?? []

  // All files flat list for cross-language hotspot queries
  const allFiles = useMemo(() =>
    lr.flatMap(lrep => (lrep.files ?? []).map(f => ({ ...f, language: lrep.language }))),
  [lr])

  // KPI calculations
  const totalFunctions = lr.reduce((s, l) => s + (l.total_functions ?? 0), 0)
  const totalClasses   = lr.reduce((s, l) => s + (l.total_classes   ?? 0), 0)
  const avgCC = allFiles.length
    ? (allFiles.reduce((s, f) => s + (f.complexity ?? 0), 0) / allFiles.length).toFixed(1)
    : '—'
  const maxCC = allFiles.length
    ? Math.max(...allFiles.map(f => f.complexity ?? 0))
    : 0
  const totalDeps = lr.reduce((s, l) => s + (l.dependencies?.length ?? 0), 0)

  // Function: openDrill
  const openDrill = (langReport, metric) =>
    setDrill({ language: langReport.language, metric, files: langReport.files ?? [] })

  return (
    <div className="space-y-5">

      {/* ── L1: KPI Stripe ─────────────────────────────────────────────────── */}
      <KpiStripe r={r} avgCC={avgCC} maxCC={maxCC} totalFunctions={totalFunctions}
        totalClasses={totalClasses} totalDeps={totalDeps} lr={lr} openDrill={openDrill} />

      {/* ── L1: Summary Cards ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        <HealthSummaryCard r={r} lr={lr} openDrill={openDrill} />
        <DebtSummaryCard r={r} lr={lr} openDrill={openDrill} />
        <CloudSummaryCard r={r} onTabChange={onTabChange} />
        <OSSSummaryCard r={r} />
        <ImpactSummaryCard r={r} />
        <CO2SummaryCard r={r} onTabChange={onTabChange} />
      </div>

      {/* ── L1: Charts row ─────────────────────────────────────────────────── */}
      <RadarAndPie result={r} />

      {/* ── Complexity distribution ─────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <ComplexityDistChart languageReports={lr} />
        <BadPracticesChart   languageReports={lr} />
      </div>

      {/* ── Hotspots table (L1 → click row = L3) ── */}
      <HotspotTable languageReports={lr} />

      {/* ── Language breakdown (L1 → toggle = L2 expand → click = L2 modal) – */}
      <LanguageBreakdown languageReports={lr} onDrillDown={openDrill} />

      {/* ── OSS dep list (L2 inline) ──────────────────────────────────────── */}
      <div id="dep-section">
        <DepVulnList oss={r.oss} />
      </div>

      {/* ── L2 Drill-Down Modal ──────────────────────────────────────────── */}
      <AnimatePresence>
        {drill && (
          <DrillDownModal
            language={drill.language}
            metric={drill.metric}
            files={drill.files}
            onClose={() => setDrill(null)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
