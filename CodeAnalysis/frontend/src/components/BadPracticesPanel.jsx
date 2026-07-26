// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (BadPracticesPanel.jsx)
// Date: 2025-12-02
// ---------------------------------------------------------------------------
import React, { useState, useMemo } from 'react'
import { AlertTriangle, ShieldAlert, Code2, FileCode, ChevronDown, ChevronUp } from 'lucide-react'
import { motion } from 'framer-motion'

const LANG_COLORS = {
  Python: '#3b82f6', Java: '#f97316', '.NET': '#818cf8',
  'C#': '#818cf8', Mainframe: '#22d3ee', JavaScript: '#f59e0b', TypeScript: '#06b6d4',
}
// Function: langColor
function langColor(lang) {
  for (const [k, v] of Object.entries(LANG_COLORS)) { if (lang.includes(k)) return v }
  return '#94a3b8'
}

const PRACTICE_META = {
  'Deep nesting (>4 levels)': { key: 'deep_nesting',  icon: '🔀', impact: 'High',   color: '#ef4444', desc: 'Functions with > 4 nesting levels — poor readability and hard to test.' },
  'Long methods (>40 LOC)':   { key: 'long_methods',  icon: '📏', impact: 'High',   color: '#f97316', desc: 'Methods exceeding 40 lines typically violate Single Responsibility.' },
  'Magic numbers':            { key: 'magic_numbers', icon: '🔢', impact: 'Medium', color: '#f59e0b', desc: 'Unnamed numeric literals make code harder to understand and maintain.' },
  'TODO/FIXME markers':       { key: 'todo_comments', icon: '📌', impact: 'Low',    color: '#22d3ee', desc: 'Unresolved technical debt markers indicating incomplete work.' },
}

// Function: parsePractice
function parsePractice(str) {
  const m = str.match(/^(.+?):\s*(\d+)$/)
  return m ? { name: m[1].trim(), count: parseInt(m[2], 10) } : { name: str, count: 1 }
}

// Function: BadPracticesPanel
export default function BadPracticesPanel({ language_reports = [] }) {
  const [showAllFiles, setShowAllFiles] = useState(false)

  // ── Aggregate by practice type across all languages ──────────────────────
  const practiceAgg = useMemo(() => {
    const agg = {}
    for (const r of language_reports) {
      for (const p of (r.bad_practices || [])) {
        const { name, count } = parsePractice(p)
        if (!agg[name]) agg[name] = { total: 0, langs: {}, affectedFiles: 0 }
        agg[name].total += count
        agg[name].langs[r.language] = (agg[name].langs[r.language] || 0) + count
      }
    }
    // count affected files from per-file data
    for (const r of language_reports) {
      for (const f of (r.files || [])) {
        for (const [pName, meta] of Object.entries(PRACTICE_META)) {
          if ((f[meta.key] ?? 0) > 0 && agg[pName])
            agg[pName].affectedFiles = (agg[pName].affectedFiles || 0) + 1
        }
      }
    }
    return agg
  }, [language_reports])

  // ── Top offender files ────────────────────────────────────────────────────
  const allFilesWithBP = useMemo(() => {
    const files = []
    for (const r of language_reports) {
      for (const f of (r.files || [])) {
        const total = (f.deep_nesting ?? 0) + (f.long_methods ?? 0) + (f.magic_numbers ?? 0) + (f.todo_comments ?? 0)
        if (total > 0) files.push({ ...f, language: r.language, bpTotal: total })
      }
    }
    return files.sort((a, b) => b.bpTotal - a.bpTotal)
  }, [language_reports])

  const topFiles   = showAllFiles ? allFilesWithBP : allFilesWithBP.slice(0, 12)
  const totalCount = Object.values(practiceAgg).reduce((s, v) => s + v.total, 0)
  const practiceTypes = Object.keys(practiceAgg)

  if (!practiceTypes.length) return null

  return (
    <div className="space-y-5">

      {/* ── Summary Tiles ──────────────────────────────────────────────────── */}
      <div className="glass p-5">
        <div className="flex items-center gap-2 mb-4">
          <ShieldAlert size={15} className="text-warning" />
          <h3 className="text-sm font-semibold text-blue-300">Bad Practices Summary</h3>
          <span className="text-xs bg-warning/15 text-warning border border-warning/25 px-2 py-0.5 rounded-full ml-1">
            {totalCount.toLocaleString()} total occurrences
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(PRACTICE_META).map(([name, meta]) => {
            const agg = practiceAgg[name]
            if (!agg) return (
              <div key={name} className="rounded-xl border border-surface-border/30 p-3 opacity-40">
                <div className="text-xs text-blue-600 mb-1">{meta.icon} {name.split('(')[0].trim()}</div>
                <div className="text-2xl font-bold text-blue-700">0</div>
                <div className="text-[10px] text-blue-700 mt-0.5">{meta.impact} Impact</div>
              </div>
            )
            return (
              <div key={name} className="rounded-xl border p-3"
                   style={{ borderColor: meta.color + '40', background: meta.color + '0d' }}>
                <div className="text-xs text-blue-400 mb-1">{meta.icon} {name.split('(')[0].trim()}</div>
                <div className="text-2xl font-bold" style={{ color: meta.color }}>{agg.total.toLocaleString()}</div>
                {agg.affectedFiles > 0 && (
                  <div className="text-[10px] text-blue-500 mt-0.5">{agg.affectedFiles} files affected</div>
                )}
                <div className="text-[10px] font-semibold mt-1" style={{ color: meta.color }}>
                  {meta.impact} Impact
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Per-Language Breakdown Table ───────────────────────────────────── */}
      {language_reports.some(r => r.bad_practices?.length) && (
        <div className="glass overflow-hidden">
          <div className="px-5 py-3 border-b border-surface-border flex items-center gap-2">
            <Code2 size={13} className="text-brand-cyan" />
            <span className="text-sm font-semibold text-blue-300">Breakdown by Language</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="px-4 py-2.5 text-left text-blue-500 font-medium">Language</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium whitespace-nowrap">Files</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium whitespace-nowrap">SLOC</th>
                  {Object.entries(PRACTICE_META).map(([n, m]) => (
                    <th key={n} className="px-3 py-2.5 text-right text-blue-500 font-medium whitespace-nowrap">
                      {m.icon} {n.split('(')[0].trim()}
                    </th>
                  ))}
                  <th className="px-4 py-2.5 text-right text-blue-500 font-medium">Total</th>
                </tr>
              </thead>
              <tbody>
                {language_reports.map(r => {
                  const byName = {}
                  for (const p of (r.bad_practices || [])) {
                    const { name, count } = parsePractice(p)
                    byName[name] = count
                  }
                  const rowTotal = Object.values(byName).reduce((s, v) => s + v, 0)
                  return (
                    <motion.tr key={r.language} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                      className="border-b border-surface-border/50 hover:bg-surface-hover">
                      <td className="px-4 py-2.5">
                        <span className="font-semibold text-xs px-2 py-0.5 rounded"
                          style={{ color: langColor(r.language), background: langColor(r.language) + '18' }}>
                          {r.language}
                        </span>
                      </td>
                      <td className="px-3 py-2.5 text-right font-mono text-blue-400">{r.file_count?.toLocaleString()}</td>
                      <td className="px-3 py-2.5 text-right font-mono text-blue-400">{r.total_sloc?.toLocaleString()}</td>
                      {Object.entries(PRACTICE_META).map(([pName, meta]) => {
                        const val = byName[pName] ?? 0
                        return (
                          <td key={pName} className="px-3 py-2.5 text-right font-mono">
                            <span style={{ color: val > 0 ? meta.color : '#374151' }} className="font-semibold">
                              {val > 0 ? val.toLocaleString() : '—'}
                            </span>
                          </td>
                        )
                      })}
                      <td className="px-4 py-2.5 text-right font-bold text-blue-300">{rowTotal.toLocaleString()}</td>
                    </motion.tr>
                  )
                })}
                {/* Totals row */}
                <tr className="border-t border-surface-border bg-gray-900/40">
                  <td className="px-4 py-2.5 text-xs font-semibold text-blue-400" colSpan={3}>Grand Total</td>
                  {Object.keys(PRACTICE_META).map(pName => {
                    const val = practiceAgg[pName]?.total ?? 0
                    const meta = PRACTICE_META[pName]
                    return (
                      <td key={pName} className="px-3 py-2.5 text-right font-bold font-mono" style={{ color: val > 0 ? meta.color : '#374151' }}>
                        {val > 0 ? val.toLocaleString() : '—'}
                      </td>
                    )
                  })}
                  <td className="px-4 py-2.5 text-right font-bold text-blue-200">{totalCount.toLocaleString()}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Practice Descriptions ─────────────────────────────────────────── */}
      <div className="glass p-5">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle size={13} className="text-warning" />
          <span className="text-sm font-semibold text-blue-300">Practice Definitions &amp; Remediation Guidance</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(PRACTICE_META).map(([name, meta]) => {
            const agg = practiceAgg[name]
            return (
              <div key={name} className="p-3 rounded-xl border"
                   style={agg ? { borderColor: meta.color + '30', background: meta.color + '08' } : { borderColor: '#1f2937', opacity: 0.5 }}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-blue-200">{meta.icon} {name}</span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                        style={{ color: meta.color, background: meta.color + '20' }}>
                    {meta.impact} Impact
                  </span>
                </div>
                <p className="text-[11px] text-blue-500 leading-snug">{meta.desc}</p>
                {agg && (
                  <div className="flex gap-3 mt-1.5 text-[11px]">
                    <span className="font-bold" style={{ color: meta.color }}>{agg.total.toLocaleString()} occurrences</span>
                    {agg.affectedFiles > 0 && <span className="text-blue-500">{agg.affectedFiles} files affected</span>}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Top Offender Files ────────────────────────────────────────────── */}
      {topFiles.length > 0 && (
        <div className="glass overflow-hidden">
          <div className="px-5 py-3 border-b border-surface-border flex items-center gap-2">
            <FileCode size={13} className="text-danger" />
            <span className="text-sm font-semibold text-blue-300">🔥 Top Files by Bad Practice Count</span>
            <span className="text-xs text-blue-500 ml-auto">{allFilesWithBP.length} total files with issues</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="px-3 py-2.5 text-left text-blue-500 font-medium">#</th>
                  <th className="px-3 py-2.5 text-left text-blue-500 font-medium">File</th>
                  <th className="px-3 py-2.5 text-left text-blue-500 font-medium">Lang</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">SLOC</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">🔀 Deep Nest</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">📏 Long Methods</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">🔢 Magic #</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">📌 TODO</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Total</th>
                </tr>
              </thead>
              <tbody>
                {topFiles.map((f, i) => (
                  <motion.tr key={f.name + i} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                             transition={{ delay: i * 0.01 }}
                             className="border-b border-surface-border/40 hover:bg-surface-hover">
                    <td className="px-3 py-2 text-blue-600 font-mono">{i + 1}</td>
                    <td className="px-3 py-2 font-mono text-blue-300 max-w-[220px] truncate" title={f.name}>
                      {f.name.split('/').slice(-2).join('/')}
                    </td>
                    <td className="px-3 py-2">
                      <span className="text-[10px] px-1.5 py-0.5 rounded font-mono"
                        style={{ color: langColor(f.language), background: langColor(f.language) + '18' }}>
                        {f.language}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-right font-mono text-blue-400">{(f.sloc ?? 0).toLocaleString()}</td>
                    <td className="px-3 py-2 text-right font-mono" style={{ color: (f.deep_nesting ?? 0) > 0 ? '#ef4444' : '#374151' }}>
                      {(f.deep_nesting ?? 0) > 0 ? f.deep_nesting : '—'}
                    </td>
                    <td className="px-3 py-2 text-right font-mono" style={{ color: (f.long_methods ?? 0) > 0 ? '#f97316' : '#374151' }}>
                      {(f.long_methods ?? 0) > 0 ? f.long_methods : '—'}
                    </td>
                    <td className="px-3 py-2 text-right font-mono" style={{ color: (f.magic_numbers ?? 0) > 0 ? '#f59e0b' : '#374151' }}>
                      {(f.magic_numbers ?? 0) > 0 ? f.magic_numbers : '—'}
                    </td>
                    <td className="px-3 py-2 text-right font-mono" style={{ color: (f.todo_comments ?? 0) > 0 ? '#22d3ee' : '#374151' }}>
                      {(f.todo_comments ?? 0) > 0 ? f.todo_comments : '—'}
                    </td>
                    <td className="px-3 py-2 text-right font-bold text-blue-300">{f.bpTotal}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          {allFilesWithBP.length > 12 && (
            <div className="px-5 py-3 border-t border-surface-border">
              <button onClick={() => setShowAllFiles(v => !v)}
                      className="text-xs text-brand-cyan hover:text-white transition-colors flex items-center gap-1.5">
                {showAllFiles ? <><ChevronUp size={12} /> Show less</> : <><ChevronDown size={12} /> Show all {allFilesWithBP.length} files</>}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
