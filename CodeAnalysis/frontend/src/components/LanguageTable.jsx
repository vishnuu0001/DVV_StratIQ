// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (LanguageTable.jsx)
// Date: 2025-09-30
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { ChevronDown, ChevronRight, Code2, AlertTriangle, Package, ExternalLink } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { fmtNumber } from '../utils.js'
import DrillDownModal from './DrillDownModal.jsx'

// ── helpers ────────────────────────────────────────────────────────────────────

// Function: ComplexityBadge
function ComplexityBadge({ value, onClick }) {
  const color = value > 10 ? '#f87171' : value > 5 ? '#fb923c' : '#4ade80'
  return (
    <span
      className="font-mono text-xs px-2 py-0.5 rounded-md cursor-pointer hover:opacity-70 transition-opacity"
      style={{ color, background: `${color}15` }}
      onClick={onClick}
      title="Click to drill down per file"
    >
      {value}
    </span>
  )
}

// Function: ClickableCell
function ClickableCell({ value, colorClass = 'text-blue-300', onClick, title }) {
  return (
    <span
      className={`font-mono text-xs cursor-pointer hover:underline decoration-dotted underline-offset-2 ${colorClass}`}
      onClick={onClick}
      title={title || 'Click to drill down per file'}
    >
      {value}
    </span>
  )
}

// ─ Bad practice → {metric, filterFn} ─────────────────────────────────────────

const BP_META = {
  'Deep nesting (>4 levels)': { metric: 'deep_nesting',  filter: f => f.deep_nesting  > 0 },
  'Long methods (>40 LOC)':   { metric: 'long_methods',  filter: f => f.long_methods  > 0 },
  'Magic numbers':            { metric: 'magic_numbers', filter: f => f.magic_numbers > 0 },
  'TODO/FIXME markers':       { metric: 'todo_comments', filter: f => f.todo_comments > 0 },
}

// Function: matchBpMeta
function matchBpMeta(practice) {
  for (const [key, val] of Object.entries(BP_META)) {
    if (practice.toLowerCase().includes(key.toLowerCase())) return val
  }
  return null
}

// ─ Dependency registry URL resolver ──────────────────────────────────────────

// Function: depUrl
function depUrl(language, name) {
  const lang = language.toLowerCase()
  if (lang === 'python')                              return `https://pypi.org/project/${name}`
  if (lang === 'java')                                return `https://mvnrepository.com/search?q=${name}`
  if (['c#', '.net', 'vb.net'].includes(lang))        return `https://www.nuget.org/packages/${name}`
  if (['javascript', 'typescript'].includes(lang))    return `https://www.npmjs.com/package/${name}`
  return null
}

// ─ Expanded row (L1 → L2 entry points for bad practices & deps) ───────────────

// Function: ExpandedDetails
function ExpandedDetails({ report, onBpDrillDown }) {
  return (
    <motion.tr
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <td colSpan={10} className="bg-surface px-6 py-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Bad practices — each item is a drill-down link if per-file data exists */}
          {report.bad_practices?.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-warning mb-2 flex items-center gap-1">
                <AlertTriangle size={11} /> Bad Practices
              </div>
              <ul className="space-y-1">
                {report.bad_practices.map((p, i) => {
                  const bpMeta = matchBpMeta(p)
                  const canDrill = bpMeta && (report.files?.length > 0)
                  return (
                    <li key={i} className="text-xs text-blue-400 flex gap-1.5 items-start">
                      <span className="text-warning mt-0.5">·</span>
                      {canDrill ? (
                        <button
                          onClick={() => onBpDrillDown(bpMeta.metric, bpMeta.filter)}
                          className="text-left hover:text-amber-300 hover:underline decoration-dotted underline-offset-2 transition-colors"
                          title={`Drill down: files with this issue`}
                        >
                          {p} <ExternalLink size={9} className="inline ml-0.5 opacity-50" />
                        </button>
                      ) : (
                        <span>{p}</span>
                      )}
                    </li>
                  )
                })}
              </ul>
            </div>
          )}

          {/* Dependencies — pills are links to the package registry */}
          {report.dependencies?.length > 0 && (
            <div className="md:col-span-2">
              <div className="text-xs font-semibold text-brand-cyan mb-2 flex items-center gap-1">
                <Package size={11} /> Dependencies ({report.dependencies.length})
              </div>
              <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto scrollbar-thin">
                {report.dependencies.map((d, i) => {
                  const url = depUrl(report.language, d)
                  return url ? (
                    <a key={i} href={url} target="_blank" rel="noopener noreferrer"
                      title={`Open ${d} on registry`}
                      className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-hover border border-surface-border
                                 text-blue-400 hover:text-brand-cyan hover:border-brand-cyan transition-colors inline-flex items-center gap-1">
                      {d} <ExternalLink size={8} className="opacity-40" />
                    </a>
                  ) : (
                    <span key={i} className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-hover border border-surface-border text-blue-400">
                      {d}
                    </span>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </td>
    </motion.tr>
  )
}

// small superscript arrow that hints "click me" --------------------------------
// Function: DrillHint
function DrillHint() {
  return <span className="ml-0.5 text-[9px] text-blue-600 align-super leading-none select-none">↗</span>
}

// ─ Main table ─────────────────────────────────────────────────────────────────

// Function: LanguageTable
export default function LanguageTable({ language_reports = [] }) {
  const [expanded, setExpanded]   = useState(null)
  const [drillDown, setDrillDown] = useState(null) // { language, metric, files, filterFn }

  if (!language_reports.length) return (
    <div className="flex flex-col items-center justify-center py-24 text-blue-500">
      <svg width="48" height="48" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" className="mb-4 opacity-40">
        <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25M14.25 3l-4.5 18" />
      </svg>
      <p className="text-sm font-medium">No source files detected</p>
      <p className="text-xs mt-1 text-blue-600">The repository may be empty or contain only unsupported file types.</p>
    </div>
  )

  // Function: toggle
  const toggle = (lang) => setExpanded(expanded === lang ? null : lang)

  // Function: openDrill
  const openDrill = (r, metric, filterFn = null) => {
    setDrillDown({ language: r.language, metric, files: r.files || [], filterFn })
  }

  return (
    <>
      <div className="glass overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-border flex items-center gap-2">
          <Code2 size={15} className="text-brand-cyan" />
          <h3 className="text-sm font-semibold text-blue-300">Language Analysis</h3>
          <span className="text-[10px] text-blue-600 ml-2 hidden sm:inline">
            — click any metric value for per-file breakdown
          </span>
          <span className="text-xs text-blue-500 ml-auto">
            {language_reports.reduce((s, r) => s + r.total_sloc, 0).toLocaleString()} total SLOC
          </span>
        </div>

        <div className="overflow-x-auto scrollbar-thin">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                {['', 'Language', 'Files', 'SLOC', 'Avg CC', 'Max CC', 'Functions', 'Classes', 'Long %', 'Nesting %', 'Comment Ratio', 'Dependencies'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-blue-500 whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {language_reports.map((r) => (
                <React.Fragment key={r.language}>
                  <tr
                    onClick={() => toggle(r.language)}
                    className="border-b border-surface-border hover:bg-surface-hover cursor-pointer transition-colors group"
                  >
                    {/* expand chevron */}
                    <td className="px-3 py-3 text-blue-600 group-hover:text-gray-400">
                      {expanded === r.language ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    </td>

                    {/* Language name */}
                    <td className="px-4 py-3 font-semibold text-blue-300 whitespace-nowrap">{r.language}</td>

                    {/* Files → drill to SLOC view */}
                    <td className="px-4 py-3" onClick={e => { e.stopPropagation(); openDrill(r, 'sloc') }}>
                      <ClickableCell value={fmtNumber(r.file_count)} title="View files sorted by SLOC" />
                      <DrillHint />
                    </td>

                    {/* SLOC */}
                    <td className="px-4 py-3" onClick={e => { e.stopPropagation(); openDrill(r, 'sloc') }}>
                      <ClickableCell value={fmtNumber(r.total_sloc)} title="View files sorted by SLOC" />
                      <DrillHint />
                    </td>

                    {/* Avg CC */}
                    <td className="px-4 py-3" onClick={e => e.stopPropagation()}>
                      <ComplexityBadge value={r.avg_complexity} onClick={() => openDrill(r, 'complexity')} />
                      <DrillHint />
                    </td>

                    {/* Max CC */}
                    <td className="px-4 py-3" onClick={e => e.stopPropagation()}>
                      <ComplexityBadge value={r.max_complexity} onClick={() => openDrill(r, 'complexity')} />
                      <DrillHint />
                    </td>

                    {/* Functions */}
                    <td className="px-4 py-3" onClick={e => { e.stopPropagation(); openDrill(r, 'functions') }}>
                      <ClickableCell value={fmtNumber(r.total_functions)} title="View files sorted by function count" />
                      <DrillHint />
                    </td>

                    {/* Classes */}
                    <td className="px-4 py-3" onClick={e => { e.stopPropagation(); openDrill(r, 'classes') }}>
                      <ClickableCell value={fmtNumber(r.total_classes)} title="View files sorted by class count" />
                      <DrillHint />
                    </td>

                    {/* Long % */}
                    <td className="px-4 py-3" onClick={e => { e.stopPropagation(); openDrill(r, 'long_methods', f => f.long_methods > 0) }}>
                      <ClickableCell
                        value={`${r.long_methods_pct?.toFixed(1)}%`}
                        colorClass={r.long_methods_pct > 15 ? 'text-red-400' : r.long_methods_pct > 5 ? 'text-amber-400' : 'text-emerald-400'}
                        title="View files with long methods"
                      />
                      <DrillHint />
                    </td>

                    {/* Nesting % */}
                    <td className="px-4 py-3" onClick={e => { e.stopPropagation(); openDrill(r, 'deep_nesting', f => f.deep_nesting > 0) }}>
                      <ClickableCell
                        value={`${r.deep_nesting_pct?.toFixed(1)}%`}
                        colorClass={r.deep_nesting_pct > 5 ? 'text-red-400' : r.deep_nesting_pct > 1 ? 'text-amber-400' : 'text-emerald-400'}
                        title="View files with deep nesting"
                      />
                      <DrillHint />
                    </td>

                    {/* Comment Ratio */}
                    <td className="px-4 py-3" onClick={e => { e.stopPropagation(); openDrill(r, 'comment_ratio') }}>
                      <ClickableCell value={r.comment_ratio?.toFixed(3)} colorClass="text-blue-400" title="View files sorted by comment ratio" />
                      <DrillHint />
                    </td>

                    {/* Dependencies count */}
                    <td className="px-4 py-3 text-right">
                      <span className={`font-mono text-xs font-semibold ${
                        (r.dependencies?.length ?? 0) >= 50 ? 'text-red-400' :
                        (r.dependencies?.length ?? 0) >= 15 ? 'text-amber-400' : 'text-blue-400'
                      }`}>
                        {(r.dependencies?.length ?? 0).toLocaleString()}
                      </span>
                    </td>
                  </tr>

                  <AnimatePresence>
                    {expanded === r.language && (
                      <ExpandedDetails
                        key={`${r.language}-exp`}
                        report={r}
                        onBpDrillDown={(metric, filterFn) => openDrill(r, metric, filterFn)}
                      />
                    )}
                  </AnimatePresence>
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* L2 / L3 slide-up modal */}
      <AnimatePresence>
        {drillDown && (
          <DrillDownModal
            language={drillDown.language}
            metric={drillDown.metric}
            files={drillDown.files}
            filterFn={drillDown.filterFn}
            onClose={() => setDrillDown(null)}
          />
        )}
      </AnimatePresence>
    </>
  )
}
