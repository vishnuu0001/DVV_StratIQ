// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * DrillDownModal.jsx
// Date: 2026-04-23
// ---------------------------------------------------------------------------
/**
 * DrillDownModal.jsx
 * L2: Per-file metric table  →  L3: Full file metric card on row click
 */
import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X, ChevronDown, ChevronRight, Search,
  ArrowUp, ArrowDown, ArrowUpDown,
  AlertTriangle, GitBranch, Layers, FileCode2,
  MessageSquare, Hash, AlignLeft, Zap,
} from 'lucide-react'

// ── helpers ──────────────────────────────────────────────────────────────────

const METRIC_META = {
  sloc:          { label: 'SLOC',           icon: FileCode2,    unit: '',    higher: 'neutral', fmt: v => v.toLocaleString() },
  complexity:    { label: 'Complexity (CC)', icon: GitBranch,   unit: '',    higher: 'bad',     fmt: v => v },
  cognitive:     { label: 'Cognitive (MI)',  icon: Zap,         unit: '',    higher: 'bad',     fmt: v => v },
  functions:     { label: 'Functions',       icon: AlignLeft,   unit: '',    higher: 'neutral', fmt: v => v },
  classes:       { label: 'Classes',         icon: Layers,      unit: '',    higher: 'neutral', fmt: v => v },
  long_methods:  { label: 'Long Methods',    icon: AlignLeft,   unit: '',    higher: 'bad',     fmt: v => v },
  deep_nesting:  { label: 'Deep Nesting',    icon: GitBranch,   unit: ' lines', higher: 'bad', fmt: v => v },
  magic_numbers: { label: 'Magic Numbers',   icon: Hash,        unit: '',    higher: 'bad',     fmt: v => v },
  todo_comments: { label: 'TODO/FIXME',      icon: MessageSquare, unit: '', higher: 'bad',     fmt: v => v },
  comment_ratio: { label: 'Comment Ratio',   icon: MessageSquare, unit: '', higher: 'good',    fmt: v => v.toFixed(3) },
}

// Function: cellColor
function cellColor(meta, value, max) {
  if (!meta || meta.higher === 'neutral') return 'text-blue-300'
  if (max === 0) return 'text-blue-500'
  const ratio = value / max
  if (meta.higher === 'bad') {
    if (ratio > 0.7) return 'text-red-400'
    if (ratio > 0.35) return 'text-amber-400'
    return 'text-emerald-400'
  }
  // good → higher is better
  if (ratio < 0.3) return 'text-red-400'
  if (ratio < 0.6) return 'text-amber-400'
  return 'text-emerald-400'
}

// ── L3 FileDetailCard ─────────────────────────────────────────────────────────

// Function: MetricRow
function MetricRow({ label, value, color = 'text-blue-300' }) {
  return (
    <div className="flex justify-between items-center py-1 border-b border-surface-border last:border-0">
      <span className="text-xs text-blue-500">{label}</span>
      <span className={`text-xs font-mono font-semibold ${color}`}>{value}</span>
    </div>
  )
}

// Function: FileDetailCard
function FileDetailCard({ file, onClose }) {
  const cc = file.complexity ?? 0
  const ccColor = cc > 10 ? 'text-red-400' : cc > 5 ? 'text-amber-400' : 'text-emerald-400'
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 8 }}
      className="mt-2 rounded-lg border border-surface-border bg-surface p-4 relative"
    >
      <button onClick={onClose}
        className="absolute top-2 right-2 text-blue-500 hover:text-white transition-colors">
        <X size={12} />
      </button>
      <div className="text-[11px] font-mono text-brand-cyan mb-3 truncate pr-4">{file.name}</div>
      <div className="grid grid-cols-2 gap-x-6">
        <div>
          <div className="text-[10px] font-semibold text-blue-500 uppercase tracking-wider mb-1">Size</div>
          <MetricRow label="SLOC"          value={file.sloc?.toLocaleString()} />
          <MetricRow label="Total lines"   value={file.total_lines?.toLocaleString()} />
          <MetricRow label="Comment lines" value={file.comment_lines?.toLocaleString()} />
          <MetricRow label="Blank lines"   value={file.blank_lines?.toLocaleString()} />
          <MetricRow label="Comment ratio" value={file.comment_ratio?.toFixed(3)} />
        </div>
        <div>
          <div className="text-[10px] font-semibold text-blue-500 uppercase tracking-wider mb-1">Complexity</div>
          <MetricRow label="Cyclomatic CC"  value={cc} color={ccColor} />
          <MetricRow label="Cognitive (MI derived)" value={file.cognitive} />
          <MetricRow label="Functions"      value={file.functions} />
          <MetricRow label="Classes"        value={file.classes} />
          <div className="mt-2">
            <div className="text-[10px] font-semibold text-blue-500 uppercase tracking-wider mb-1">Bad Practices</div>
            <MetricRow label="Long methods (>40 LOC)"  value={file.long_methods}
              color={file.long_methods > 0 ? 'text-amber-400' : 'text-blue-500'} />
            <MetricRow label="Deep nesting lines"      value={file.deep_nesting}
              color={file.deep_nesting > 0 ? 'text-amber-400' : 'text-blue-500'} />
            <MetricRow label="Magic numbers"           value={file.magic_numbers}
              color={file.magic_numbers > 5 ? 'text-amber-400' : 'text-blue-500'} />
            <MetricRow label="TODO / FIXME"            value={file.todo_comments}
              color={file.todo_comments > 0 ? 'text-blue-400' : 'text-blue-500'} />
          </div>
        </div>
      </div>
      {file.error && (
        <div className="mt-2 text-xs text-red-400 flex items-center gap-1">
          <AlertTriangle size={11} /> Parse error: {file.error}
        </div>
      )}
    </motion.div>
  )
}

// ── L2 Header summary pills ───────────────────────────────────────────────────

// Function: SummaryPill
function SummaryPill({ label, value, color }) {
  return (
    <div className="flex flex-col items-center px-4 py-2 rounded-lg bg-surface border border-surface-border min-w-[70px]">
      <span className={`text-sm font-semibold font-mono ${color}`}>{value}</span>
      <span className="text-[10px] text-blue-500 mt-0.5">{label}</span>
    </div>
  )
}

// ── Column sort header ────────────────────────────────────────────────────────

// Function: SortTh
function SortTh({ col, label, sortCol, sortDir, onSort }) {
  const active = sortCol === col
  return (
    <th
      className="px-3 py-2 text-left text-[10px] font-medium text-blue-500 whitespace-nowrap cursor-pointer hover:text-gray-200 transition-colors select-none"
      onClick={() => onSort(col)}
    >
      <span className="flex items-center gap-1">
        {label}
        {active
          ? (sortDir === 'desc' ? <ArrowDown size={10} className="text-brand-cyan" /> : <ArrowUp size={10} className="text-brand-cyan" />)
          : <ArrowUpDown size={10} className="opacity-30" />}
      </span>
    </th>
  )
}

// ── Main Modal ────────────────────────────────────────────────────────────────

// Function: DrillDownModal
export default function DrillDownModal({ language, metric, files = [], filterFn, onClose }) {
  const meta = METRIC_META[metric] || METRIC_META.sloc
  const Icon = meta.icon

  const [q, setQ] = useState('')
  const [sortCol, setSortCol] = useState(metric)
  const [sortDir, setSortDir] = useState('desc')
  const [expandedFile, setExpandedFile] = useState(null)

  // Function: handleSort
  const handleSort = (col) => {
    if (sortCol === col) setSortDir(d => d === 'desc' ? 'asc' : 'desc')
    else { setSortCol(col); setSortDir('desc') }
  }

  // Apply optional pre-filter (e.g. only files with deep_nesting > 0)
  const baseFiles = useMemo(() =>
    filterFn ? files.filter(filterFn) : files,
    [files, filterFn])

  const filtered = useMemo(() => {
    let list = baseFiles
    if (q.trim()) list = list.filter(f => f.name.toLowerCase().includes(q.toLowerCase()))
    list = [...list].sort((a, b) => {
      const av = a[sortCol] ?? 0
      const bv = b[sortCol] ?? 0
      return sortDir === 'desc' ? bv - av : av - bv
    })
    return list
  }, [baseFiles, q, sortCol, sortDir])

  const maxVal = useMemo(() =>
    Math.max(...baseFiles.map(f => f[metric] ?? 0)),
    [baseFiles, metric])

  const avgVal = baseFiles.length
    ? baseFiles.reduce((s, f) => s + (f[metric] ?? 0), 0) / baseFiles.length
    : 0

  const minVal = baseFiles.length
    ? Math.min(...baseFiles.map(f => f[metric] ?? 0))
    : 0

  const COLS = [
    { col: 'name',          label: 'File'          },
    { col: 'sloc',          label: 'SLOC'          },
    { col: 'complexity',    label: 'CC'            },
    { col: 'functions',     label: 'Fns'           },
    { col: 'classes',       label: 'Cls'           },
    { col: 'long_methods',  label: 'Long'          },
    { col: 'deep_nesting',  label: 'Nesting'       },
    { col: 'magic_numbers', label: 'Magic#'        },
    { col: 'todo_comments', label: 'TODO'          },
    { col: 'comment_ratio', label: 'Cmt Ratio'     },
  ]

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center"
      style={{ background: 'rgba(0,0,0,0.65)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <motion.div
        initial={{ y: '100%', opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: '100%', opacity: 0 }}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
        className="w-full max-w-6xl max-h-[85vh] flex flex-col rounded-t-2xl border border-surface-border bg-[#0d1117] shadow-2xl"
      >
        {/* ── Header ── */}
        <div className="flex items-center gap-3 px-6 py-4 border-b border-surface-border flex-shrink-0">
          <div className="flex items-center gap-2">
            <Icon size={16} className="text-brand-cyan" />
            <span className="text-sm font-semibold text-blue-300">{language}</span>
            <span className="text-blue-500 text-sm">—</span>
            <span className="text-sm text-brand-cyan">{meta.label} drill-down</span>
          </div>
          <span className="text-xs text-blue-500 ml-1">{filtered.length} / {baseFiles.length} files</span>

          {/* Summary pills */}
          <div className="flex gap-2 ml-auto mr-4">
            <SummaryPill label="Min"  value={meta.fmt(minVal)}                     color="text-emerald-400" />
            <SummaryPill label="Avg"  value={meta.fmt(Math.round(avgVal * 100) / 100)} color="text-amber-400"   />
            <SummaryPill label="Max"  value={meta.fmt(maxVal)}                     color="text-red-400"    />
          </div>

          {/* Search */}
          <div className="relative">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-blue-500" />
            <input
              value={q}
              onChange={e => setQ(e.target.value)}
              placeholder="Filter files…"
              className="pl-7 pr-3 py-1.5 text-xs bg-surface border border-surface-border rounded-md text-blue-300 placeholder-gray-600 focus:outline-none focus:border-brand-cyan w-44"
            />
          </div>

          <button onClick={onClose} className="text-blue-500 hover:text-white transition-colors ml-2">
            <X size={18} />
          </button>
        </div>

        {/* ── Table body ── */}
        <div className="overflow-y-auto flex-1 scrollbar-thin">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-[#0d1117] z-10">
              <tr className="border-b border-surface-border">
                <th className="w-8 px-2" />
                {COLS.map(c => (
                  <SortTh key={c.col} col={c.col} label={c.label}
                    sortCol={sortCol} sortDir={sortDir} onSort={handleSort} />
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((file, idx) => (
                <React.Fragment key={file.name + idx}>
                  <tr
                    onClick={() => setExpandedFile(expandedFile === file.name ? null : file.name)}
                    className={`border-b border-surface-border cursor-pointer transition-colors group
                      ${expandedFile === file.name ? 'bg-surface' : 'hover:bg-surface-hover'}`}
                  >
                    <td className="px-2 py-2 text-blue-600 group-hover:text-gray-400 text-center">
                      {expandedFile === file.name
                        ? <ChevronDown size={11} />
                        : <ChevronRight size={11} />}
                    </td>

                    {/* File name */}
                    <td className="px-3 py-2 font-mono text-blue-300 max-w-xs truncate" title={file.name}>
                      {/* Highlight the last path segment */}
                      {(() => {
                        const parts = file.name.split('/')
                        const dir = parts.slice(0, -1).join('/') + (parts.length > 1 ? '/' : '')
                        const fname = parts[parts.length - 1]
                        return (
                          <span>
                            <span className="text-blue-500 text-[10px]">{dir}</span>
                            <span className="text-blue-300 font-semibold">{fname}</span>
                          </span>
                        )
                      })()}
                    </td>

                    {/* SLOC */}
                    <td className="px-3 py-2 font-mono text-blue-400">{file.sloc?.toLocaleString()}</td>

                    {/* CC */}
                    <td className="px-3 py-2 font-mono">
                      <span className={cellColor(METRIC_META.complexity, file.complexity, Math.max(...baseFiles.map(f => f.complexity ?? 0)))}>
                        {file.complexity}
                      </span>
                    </td>

                    {/* Functions */}
                    <td className="px-3 py-2 font-mono text-blue-400">{file.functions}</td>

                    {/* Classes */}
                    <td className="px-3 py-2 font-mono text-blue-400">{file.classes}</td>

                    {/* Long methods */}
                    <td className="px-3 py-2 font-mono">
                      <span className={file.long_methods > 0 ? 'text-amber-400' : 'text-blue-600'}>
                        {file.long_methods}
                      </span>
                    </td>

                    {/* Deep nesting */}
                    <td className="px-3 py-2 font-mono">
                      <span className={file.deep_nesting > 20 ? 'text-red-400' : file.deep_nesting > 5 ? 'text-amber-400' : 'text-blue-600'}>
                        {file.deep_nesting}
                      </span>
                    </td>

                    {/* Magic numbers */}
                    <td className="px-3 py-2 font-mono">
                      <span className={file.magic_numbers > 10 ? 'text-amber-400' : 'text-blue-600'}>
                        {file.magic_numbers}
                      </span>
                    </td>

                    {/* TODO */}
                    <td className="px-3 py-2 font-mono">
                      <span className={file.todo_comments > 0 ? 'text-blue-400' : 'text-blue-600'}>
                        {file.todo_comments}
                      </span>
                    </td>

                    {/* Comment ratio */}
                    <td className="px-3 py-2 font-mono">
                      <span className={file.comment_ratio < 0.05 ? 'text-amber-400' : 'text-blue-400'}>
                        {file.comment_ratio?.toFixed(3)}
                      </span>
                    </td>
                  </tr>

                  {/* L3 file detail card */}
                  <AnimatePresence>
                    {expandedFile === file.name && (
                      <tr key={`${file.name}-detail`}>
                        <td colSpan={11} className="px-6 pb-4 bg-surface">
                          <FileDetailCard file={file} onClose={() => setExpandedFile(null)} />
                        </td>
                      </tr>
                    )}
                  </AnimatePresence>
                </React.Fragment>
              ))}

              {filtered.length === 0 && (
                <tr>
                  <td colSpan={11} className="px-6 py-8 text-center text-blue-500 text-xs">
                    No files match the filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* ── Footer ── */}
        <div className="flex items-center gap-3 px-6 py-3 border-t border-surface-border flex-shrink-0">
          <span className="text-[10px] text-blue-600">
            Click any row to view full file metrics (L3). Column headers sort the table.
          </span>
          <button onClick={onClose}
            className="ml-auto text-xs px-4 py-1.5 rounded-md border border-surface-border text-blue-400 hover:text-white hover:border-gray-400 transition-colors">
            Close
          </button>
        </div>
      </motion.div>
    </div>
  )
}
