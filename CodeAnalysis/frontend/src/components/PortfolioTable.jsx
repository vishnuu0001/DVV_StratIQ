// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (PortfolioTable.jsx)
// Date: 2026-04-22
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { ChevronDown, ChevronUp, ExternalLink, BarChart3 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { riskColor, scoreColor, fmtNumber, fmtUSD } from '../utils.js'

const PORTFOLIO_PAGE_SIZES = [10, 25, 50, 100]

// Function: PaginationBar
function PaginationBar({ page, totalPages, pageSize, pageSizeOptions, onPage, onPageSize, total }) {
  const start = total === 0 ? 0 : (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)
  const range = []
  for (let p = Math.max(1, page - 2); p <= Math.min(totalPages, page + 2); p++) range.push(p)
  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-surface-border text-xs">
      <div className="flex items-center gap-2 text-blue-500">
        <span>{total > 0 ? `${start}–${end} of ${total} repos` : '0 repos'}</span>
        <span className="text-blue-700">·</span>
        <span>Rows per page:</span>
        <select
          value={pageSize}
          onChange={e => { onPageSize(Number(e.target.value)); onPage(1) }}
          className="bg-surface-hover border border-surface-border text-blue-300 rounded px-1.5 py-0.5 text-xs"
        >
          {pageSizeOptions.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div className="flex items-center gap-0.5">
        <button disabled={page === 1} onClick={() => onPage(1)} className="px-2 py-1 rounded hover:bg-surface-hover disabled:opacity-30 text-blue-400">«</button>
        <button disabled={page === 1} onClick={() => onPage(page - 1)} className="px-2 py-1 rounded hover:bg-surface-hover disabled:opacity-30 text-blue-400">‹</button>
        {range.map(p => (
          <button key={p} onClick={() => onPage(p)} className={`px-2 py-1 rounded ${p === page ? 'bg-brand-cyan text-white' : 'hover:bg-surface-hover text-blue-400'}`}>{p}</button>
        ))}
        <button disabled={page === totalPages} onClick={() => onPage(page + 1)} className="px-2 py-1 rounded hover:bg-surface-hover disabled:opacity-30 text-blue-400">›</button>
        <button disabled={page === totalPages} onClick={() => onPage(totalPages)} className="px-2 py-1 rounded hover:bg-surface-hover disabled:opacity-30 text-blue-400">»</button>
      </div>
    </div>
  )
}

// Function: ScorePill
function ScorePill({ value }) {
  const col = scoreColor(value)
  return (
    <span
      className="text-xs font-mono font-semibold px-2 py-0.5 rounded-md"
      style={{ color: col, background: `${col}18` }}
    >
      {value?.toFixed(0)}
    </span>
  )
}

// Function: RiskPill
function RiskPill({ label }) {
  const c = riskColor(label)
  return (
    <span
      className="text-[11px] font-semibold px-2 py-0.5 rounded-full border"
      style={{ color: c.text, background: c.bg, borderColor: c.border }}
    >
      {label}
    </span>
  )
}

// Function: PortfolioTable
export default function PortfolioTable({ portfolio = [] }) {
  const [sortKey, setSortKey] = useState('repo_name')
  const [sortDir, setSortDir] = useState('asc')
  const [expanded, setExpanded] = useState(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)

  if (!portfolio.length) return null

  const cols = [
    { key: 'repo_name', label: 'Repository' },
    { key: 'sloc', label: 'SLOC' },
    { key: 'health_score', label: 'Health' },
    { key: 'debt_person_months', label: 'Debt (PM)' },
    { key: 'cloud_score', label: 'Cloud' },
    { key: 'oss_score', label: 'OSS' },
    { key: 'impact_score', label: 'Impact' },
    { key: 'risk_label', label: 'Risk' },
  ]

  // Function: handleSort
  function handleSort(key) {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
    setPage(1)
  }

  const sorted = [...portfolio].sort((a, b) => {
    const av = a[sortKey]
    const bv = b[sortKey]
    if (av === undefined) return 1
    if (bv === undefined) return -1
    const cmp = typeof av === 'string' ? av.localeCompare(bv) : av - bv
    return sortDir === 'asc' ? cmp : -cmp
  })

  return (
    <div className="glass overflow-hidden">
      <div className="px-6 py-4 border-b border-surface-border flex items-center gap-2">
        <BarChart3 size={15} className="text-brand-cyan" />
        <h3 className="text-sm font-semibold text-blue-300">Portfolio Overview</h3>
        <span className="text-xs text-blue-500 ml-auto">{portfolio.length} repositories</span>
      </div>
      <div className="overflow-x-auto scrollbar-thin">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-border">
              {cols.map((c) => (
                <th
                  key={c.key}
                  onClick={() => handleSort(c.key)}
                  className="px-4 py-3 text-left text-xs font-medium text-blue-500 whitespace-nowrap cursor-pointer hover:text-gray-300 select-none"
                >
                  <span className="inline-flex items-center gap-1">
                    {c.label}
                    {sortKey === c.key && (
                      sortDir === 'asc' ? <ChevronUp size={11} /> : <ChevronDown size={11} />
                    )}
                  </span>
                </th>
              ))}
              <th />
            </tr>
          </thead>
          <tbody>
            {sorted.slice((page - 1) * pageSize, page * pageSize).map((r) => (
              <>
                <tr
                  key={r.repo_name}
                  onClick={() => setExpanded(expanded === r.repo_name ? null : r.repo_name)}
                  className="border-b border-surface-border hover:bg-surface-hover cursor-pointer transition-colors"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-blue-300">{r.repo_name}</span>
                      {r.repo_url && (
                        <a
                          href={r.repo_url}
                          target="_blank"
                          rel="noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="text-blue-600 hover:text-brand-cyan transition-colors"
                        >
                          <ExternalLink size={11} />
                        </a>
                      )}
                    </div>
                    {r.description && (
                      <p className="text-[11px] text-blue-500 mt-0.5 max-w-xs truncate">{r.description}</p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-blue-300 font-mono">{fmtNumber(r.sloc)}</td>
                  <td className="px-4 py-3"><ScorePill value={r.health_score} /></td>
                  <td className="px-4 py-3 text-blue-300 font-mono text-xs">{r.debt_person_months?.toFixed(1)}</td>
                  <td className="px-4 py-3"><ScorePill value={r.cloud_score} /></td>
                  <td className="px-4 py-3"><ScorePill value={r.oss_score} /></td>
                  <td className="px-4 py-3"><ScorePill value={r.impact_score} /></td>
                  <td className="px-4 py-3"><RiskPill label={r.risk_label} /></td>
                  <td className="px-3 py-3 text-blue-600">
                    {expanded === r.repo_name ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </td>
                </tr>

                <AnimatePresence>
                  {expanded === r.repo_name && (
                    <motion.tr
                      key={`${r.repo_name}-detail`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <td colSpan={9} className="bg-surface px-6 py-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                          <div>
                            <div className="text-blue-500 mb-1">Estimated Cost</div>
                            <div className="font-semibold text-blue-300">{fmtUSD(r.rebuild_cost)}</div>
                          </div>
                          <div>
                            <div className="text-blue-500 mb-1">Languages</div>
                            <div className="flex flex-wrap gap-1">
                              {(r.languages || []).map((l) => (
                                <span key={l} className="px-1.5 py-0.5 bg-surface-hover border border-surface-border rounded text-blue-400">
                                  {l}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div>
                            <div className="text-blue-500 mb-1">Files</div>
                            <div className="font-semibold text-blue-300">{fmtNumber(r.file_count)}</div>
                          </div>
                          <div>
                            <div className="text-blue-500 mb-1">Vulnerable Deps</div>
                            <div className="font-semibold" style={{ color: r.vulnerable_deps > 0 ? '#f87171' : '#4ade80' }}>
                              {r.vulnerable_deps ?? '—'}
                            </div>
                          </div>
                        </div>
                      </td>
                    </motion.tr>
                  )}
                </AnimatePresence>
              </>
            ))}
          </tbody>
        </table>
      </div>
      <PaginationBar
        page={page}
        totalPages={Math.max(1, Math.ceil(sorted.length / pageSize))}
        pageSize={pageSize}
        pageSizeOptions={PORTFOLIO_PAGE_SIZES}
        onPage={setPage}
        onPageSize={setPageSize}
        total={sorted.length}
      />
    </div>
  )
}
