// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (TechDebtDetailPanel.jsx)
// Date: 2025-10-27
// ---------------------------------------------------------------------------
import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Clock, TrendingUp, DollarSign, Layers, FileCode, ChevronDown, ChevronUp } from 'lucide-react'
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts'

const RISK_COLORS = {
  CRITICAL: '#ef4444',
  HIGH:     '#f97316',
  MEDIUM:   '#f59e0b',
  LOW:      '#22c55e',
  FAIR:     '#84cc16',
}

// Function: DebtBar
function DebtBar({ value, max, color }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0
  return (
    <div className="h-1.5 w-24 rounded-full bg-gray-800 overflow-hidden">
      <motion.div
        className="h-full rounded-full"
        style={{ background: color || '#f59e0b' }}
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      />
    </div>
  )
}

// Function: fmtNum
function fmtNum(n) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}m`
  if (n >= 1_000)     return `${(n / 1_000).toFixed(1)}k`
  return String(Math.round(n))
}

// Function: fmtUSD
function fmtUSD(n) {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000)     return `$${(n / 1_000).toFixed(0)}k`
  return `$${Math.round(n)}`
}

// Custom content for Recharts Treemap cells
// Function: TreemapCell
function TreemapCell(props) {
  const { x, y, width, height, name, value, root, depth } = props
  if (depth > 1 || width < 20 || height < 20) return null
  const fill = RISK_COLORS[root?.risk_label] || '#f59e0b'
  return (
    <g>
      <rect x={x} y={y} width={width} height={height}
        fill={fill} fillOpacity={0.3}
        stroke="#1f2937" strokeWidth={1.5} rx={4}
      />
      {width > 60 && height > 25 && (
        <>
          <text x={x + width / 2} y={y + height / 2 - 5}
            textAnchor="middle" fill="#e5e7eb" fontSize={10} fontWeight="600">
            {name?.length > 14 ? name.slice(0, 13) + '…' : name}
          </text>
          {height > 40 && (
            <text x={x + width / 2} y={y + height / 2 + 9}
              textAnchor="middle" fill={fill} fontSize={9}>
              {fmtNum(value)} SLOC
            </text>
          )}
        </>
      )}
    </g>
  )
}

// Function: TechDebtDetailPanel
export default function TechDebtDetailPanel({ result, portfolio }) {
  // Build rows — either from portfolio results or single result
  const rows = useMemo(() => {
    if (portfolio?.results?.length > 0) {
      return [...portfolio.results]
        .sort((a, b) => b.debt_person_months - a.debt_person_months)
        .slice(0, 10)
    }
    if (result) {
      // Single repo — show language breakdown
      return (result.language_reports || []).map(lr => ({
        repo_name:           lr.language,
        sloc:                lr.total_sloc,
        file_count:          lr.file_count,
        impact_score:        0,
        debt_person_months:  result.debt?.debt_months * (lr.total_sloc / (result.total_sloc || 1)),
        risk_label:          result.health?.risk_label || 'MEDIUM',
        debt_density:        result.debt?.density || 0,
        rebuild_cost:        result.debt?.debt_usd * (lr.total_sloc / (result.total_sloc || 1)),
      })).sort((a, b) => b.debt_person_months - a.debt_person_months)
    }
    return []
  }, [result, portfolio])

  const maxDebt = Math.max(...rows.map(r => r.debt_person_months || 0), 1)

  // Treemap data from language_reports or portfolio
  const treemapData = useMemo(() => {
    if (result?.language_reports) {
      return result.language_reports.map(lr => ({
        name:       lr.language,
        value:      lr.total_sloc,
        risk_label: result.health?.risk_label || 'MEDIUM',
      }))
    }
    return (portfolio?.results || []).map(r => ({
      name:       r.repo_name?.split('/').pop() || r.repo_name,
      value:      r.sloc || 0,
      risk_label: r.risk_label || 'MEDIUM',
    }))
  }, [result, portfolio])

  if (rows.length === 0) {
    return (
      <div className="py-16 text-center text-blue-500">
        <Clock size={32} className="mx-auto mb-3 opacity-40" />
        <p>No technical debt data available. Run analysis to compute debt estimates.</p>
      </div>
    )
  }

  const debtInfo = result?.debt
  const summaryCards = debtInfo ? [
    { label: 'Total Tech Debt',    value: `${debtInfo.debt_months?.toFixed(1)} p-months`, icon: Clock,      color: 'text-amber-400' },
    { label: 'Debt / LOC',        value: `${debtInfo.density?.toFixed(2)} m/kSLOC`,       icon: TrendingUp,  color: 'text-orange-400' },
    { label: 'Remediation Cost',  value: fmtUSD(debtInfo.debt_usd || 0),                  icon: DollarSign,  color: 'text-red-400'   },
    { label: 'Debt Ratio',        value: `${debtInfo.debt_ratio?.toFixed(1)}%`,           icon: Layers,      color: 'text-yellow-400' },
  ] : []

  return (
    <div className="space-y-6">
      {/* KPI summary */}
      {summaryCards.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {summaryCards.map(c => {
            const Icon = c.icon
            return (
              <div key={c.label}
                className="rounded-xl border border-surface-border bg-gray-900/40 px-4 py-3 flex flex-col gap-1">
                <div className="flex items-center gap-1.5">
                  <Icon size={12} className={c.color} />
                  <span className="text-[10px] text-blue-500">{c.label}</span>
                </div>
                <span className={`text-lg font-bold ${c.color}`}>{c.value}</span>
              </div>
            )
          })}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Top-10 debt table */}
        <div className="rounded-xl border border-surface-border overflow-hidden">
          <div className="px-4 py-3 bg-gray-900/60 border-b border-surface-border text-sm font-semibold text-blue-200">
            Top Applications by Tech Debt
          </div>
          <table className="w-full text-xs">
            <thead className="bg-gray-900/40">
              <tr>
                <th className="px-3 py-2 text-left text-blue-500 font-medium">Name</th>
                <th className="px-3 py-2 text-right text-blue-500 font-medium">LOC</th>
                <th className="px-3 py-2 text-right text-blue-500 font-medium">Files</th>
                <th className="px-3 py-2 text-center text-blue-500 font-medium">BI</th>
                <th className="px-3 py-2 text-right text-blue-500 font-medium">Tech Debt</th>
                <th className="px-3 py-2 text-right text-blue-500 font-medium">Debt/LOC</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => {
                const debtMonths = row.debt_person_months || 0
                const density    = row.sloc > 0 ? (debtMonths / (row.sloc / 1000)) : 0
                const color = RISK_COLORS[row.risk_label] || '#f59e0b'
                return (
                  <motion.tr key={row.repo_name + i}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.03 }}
                    className="border-b border-surface-border/40 hover:bg-gray-800/20 transition-colors"
                  >
                    <td className="px-3 py-2.5 text-blue-200 font-medium truncate max-w-36"
                        title={row.repo_name}>
                      {row.repo_name?.split('/').pop() || row.repo_name}
                    </td>
                    <td className="px-3 py-2.5 text-right text-blue-400 font-mono">
                      {fmtNum(row.sloc || 0)} LOC
                    </td>
                    <td className="px-3 py-2.5 text-right text-blue-400 font-mono">
                      {fmtNum(row.file_count || 0)}
                    </td>
                    <td className="px-3 py-2.5 text-center">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold"
                        style={{ background: color + '30', color }}>
                        {Math.round(row.impact_score || 0)}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 text-right">
                      <div className="flex flex-col items-end gap-1">
                        <span className="font-semibold" style={{ color }}>
                          {debtMonths.toFixed(1)} p-month
                        </span>
                        <DebtBar value={debtMonths} max={maxDebt} color={color} />
                      </div>
                    </td>
                    <td className="px-3 py-2.5 text-right text-blue-400 font-mono">
                      {density.toFixed(2)} m/kLOC
                    </td>
                  </motion.tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Treemap */}
        <div className="rounded-xl border border-surface-border bg-gray-900/40 overflow-hidden">
          <div className="px-4 py-3 bg-gray-900/60 border-b border-surface-border text-sm font-semibold text-blue-200">
            Code Distribution by Technology
          </div>
          <div className="p-3" style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <Treemap
                data={treemapData}
                dataKey="value"
                aspectRatio={1.2}
                content={<TreemapCell />}
              >
                <Tooltip
                  contentStyle={{
                    background: '#111827', border: '1px solid #374151',
                    borderRadius: 8, fontSize: 11,
                  }}
                  formatter={(val, _name, props) => [
                    `${fmtNum(val)} SLOC`, props?.payload?.name
                  ]}
                />
              </Treemap>
            </ResponsiveContainer>
          </div>
          {/* Color legend */}
          <div className="px-4 pb-3 flex flex-wrap gap-2">
            {Object.entries(RISK_COLORS).map(([label, color]) => (
              <span key={label} className="flex items-center gap-1 text-[10px] text-blue-500">
                <span className="w-2.5 h-2.5 rounded-sm" style={{ background: color + '60', border: `1px solid ${color}` }} />
                {label}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Footnote */}
      <p className="text-xs text-blue-600 italic text-center">
        Technical Debt as an effort per application should be considered as a baseline.
        TD density is a great KPI to monitor team performance.
        Technical Debt is an indication of the opportunities to improve the application.
      </p>

      {/* ── Top file-level debt hotspots (single repo only) ──────────────── */}
      {result && <DebtHotspotFiles result={result} />}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Debt hotspot files — top files ranked by combined complexity + size score
// ─────────────────────────────────────────────────────────────────────────────
// Function: DebtHotspotFiles
function DebtHotspotFiles({ result }) {
  const [showAll, setShowAll] = useState(false)

  const hotspots = useMemo(() => {
    const out = []
    for (const lr of result?.language_reports ?? []) {
      const debtRatio = result?.debt?.density ?? 0 // person-months per kSLOC
      for (const f of (lr.files || [])) {
        const cc    = f.complexity   ?? 0
        const sloc  = f.sloc         ?? 0
        const lm    = f.long_methods ?? 0
        const dn    = f.deep_nesting ?? 0
        const score = cc * 3 + sloc / 150 + lm * 4 + dn * 2
        // Estimated fix effort: proportional to SLOC debt density
        const estMonths = sloc > 0 ? (sloc / 1000) * debtRatio : 0
        out.push({ ...f, language: lr.language, _score: score, estMonths })
      }
    }
    return out.sort((a, b) => b._score - a._score)
  }, [result])

  const visible = showAll ? hotspots : hotspots.slice(0, 12)
  if (!visible.length) return null

  // Function: ccColor
  const ccColor = (v) => v > 20 ? '#ef4444' : v > 10 ? '#f97316' : v > 5 ? '#f59e0b' : '#4ade80'
  // Function: sColor
  const sColor  = (s) => s > 100 ? '#ef4444' : s > 50 ? '#f97316' : '#f59e0b'
  const LANG_C  = { Python: '#3b82f6', Java: '#f97316', '.NET': '#818cf8', JavaScript: '#f59e0b', TypeScript: '#06b6d4' }
  // Function: lc
  const lc      = (lang) => { for (const [k, v] of Object.entries(LANG_C)) { if (lang.includes(k)) return v } return '#94a3b8' }

  return (
    <div className="rounded-xl border border-surface-border overflow-hidden">
      <div className="px-4 py-3 bg-gray-900/60 border-b border-surface-border flex items-center gap-2">
        <FileCode size={13} className="text-danger" />
        <span className="text-sm font-semibold text-blue-200">🔥 Top Files by Debt Score</span>
        <span className="text-xs text-blue-500 ml-auto">{hotspots.length} files ranked</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead className="bg-gray-900/40">
            <tr>
              <th className="px-3 py-2 text-left text-blue-500 font-medium">#</th>
              <th className="px-3 py-2 text-left text-blue-500 font-medium">File</th>
              <th className="px-3 py-2 text-left text-blue-500 font-medium">Lang</th>
              <th className="px-3 py-2 text-right text-blue-500 font-medium">SLOC</th>
              <th className="px-3 py-2 text-right text-blue-500 font-medium">CC</th>
              <th className="px-3 py-2 text-right text-blue-500 font-medium">Functions</th>
              <th className="px-3 py-2 text-right text-blue-500 font-medium">Classes</th>
              <th className="px-3 py-2 text-right text-blue-500 font-medium">Long Methods</th>
              <th className="px-3 py-2 text-right text-blue-500 font-medium">Deep Nesting</th>
              <th className="px-3 py-2 text-right text-blue-500 font-medium">Est. Effort</th>
              <th className="px-3 py-2 text-right text-blue-500 font-medium">Debt Score</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((f, i) => {
              const cc    = f.complexity ?? 0
              const score = Math.round(f._score)
              return (
                <motion.tr key={f.name + i}
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.01 }}
                  className="border-b border-surface-border/40 hover:bg-gray-800/20">
                  <td className="px-3 py-2 text-blue-600 font-mono">{i + 1}</td>
                  <td className="px-3 py-2 font-mono text-blue-300 max-w-[200px] truncate" title={f.name}>
                    {f.name.split('/').slice(-2).join('/')}
                  </td>
                  <td className="px-3 py-2">
                    <span className="text-[10px] px-1.5 py-0.5 rounded font-mono"
                      style={{ color: lc(f.language), background: lc(f.language) + '18' }}>
                      {f.language}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-blue-400">{(f.sloc ?? 0).toLocaleString()}</td>
                  <td className="px-3 py-2 text-right font-mono font-semibold" style={{ color: ccColor(cc) }}>{cc}</td>
                  <td className="px-3 py-2 text-right font-mono text-blue-400">{f.functions ?? '—'}</td>
                  <td className="px-3 py-2 text-right font-mono text-blue-400">{f.classes ?? '—'}</td>
                  <td className="px-3 py-2 text-right font-mono" style={{ color: (f.long_methods ?? 0) > 0 ? '#f97316' : '#374151' }}>
                    {(f.long_methods ?? 0) > 0 ? f.long_methods : '—'}
                  </td>
                  <td className="px-3 py-2 text-right font-mono" style={{ color: (f.deep_nesting ?? 0) > 0 ? '#ef4444' : '#374151' }}>
                    {(f.deep_nesting ?? 0) > 0 ? f.deep_nesting : '—'}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-amber-400">
                    {f.estMonths > 0.01 ? `${f.estMonths.toFixed(2)} p-mo` : '< 0.01'}
                  </td>
                  <td className="px-3 py-2 text-right font-bold" style={{ color: sColor(score) }}>{score}</td>
                </motion.tr>
              )
            })}
          </tbody>
        </table>
      </div>
      {hotspots.length > 12 && (
        <div className="px-4 py-3 border-t border-surface-border">
          <button onClick={() => setShowAll(v => !v)}
                  className="text-xs text-brand-cyan hover:text-white transition-colors flex items-center gap-1.5">
            {showAll ? <><ChevronUp size={12} /> Show less</> : <><ChevronDown size={12} /> Show all {hotspots.length} files</>}
          </button>
        </div>
      )}
    </div>
  )
}
