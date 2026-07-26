// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (GreenImpactPanel.jsx)
// Date: 2026-06-01
// ---------------------------------------------------------------------------
import React, { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Leaf, ChevronDown, ChevronUp, TrendingDown } from 'lucide-react'

const CATEGORY_COLORS = {
  'Algorithmic Costs': 'bg-green-900/40 text-green-300 border-green-700/40',
  'Avoiding Failure':  'bg-red-900/40 text-red-300 border-red-700/40',
  'Resource Economy':  'bg-blue-900/40 text-blue-300 border-blue-700/40',
  'Maintainability':   'bg-amber-900/40 text-amber-300 border-amber-700/40',
  'Security':          'bg-purple-900/40 text-purple-300 border-purple-700/40',
}

const LANG_COLORS = {
  Java:       'bg-orange-900/50 text-orange-300',
  Python:     'bg-blue-900/50 text-blue-300',
  '.NET':     'bg-purple-900/50 text-purple-300',
  JavaScript: 'bg-yellow-900/50 text-yellow-300',
  TypeScript: 'bg-cyan-900/50 text-cyan-300',
  Mainframe:  'bg-gray-700/50 text-blue-300',
}

// Function: ScoreBadge
function ScoreBadge({ score, risk }) {
  const color =
    risk === 'LOW'      ? 'text-green-400 border-green-600' :
    risk === 'MEDIUM'   ? 'text-amber-400 border-amber-600' :
    risk === 'HIGH'     ? 'text-orange-400 border-orange-600' :
                          'text-red-400 border-red-600'
  return (
    <div className={`inline-flex flex-col items-center px-4 py-2 rounded-xl border ${color} bg-gray-900/60`}>
      <span className="text-2xl font-bold">{score}</span>
      <span className="text-xs opacity-70">Green Score</span>
    </div>
  )
}

// Function: CategorySummaryBar
function CategorySummaryBar({ catTotals }) {
  const categories = Object.keys(CATEGORY_COLORS)
  const total = Object.values(catTotals).reduce((a, b) => a + b, 0) || 1
  return (
    <div className="flex gap-3 flex-wrap mb-5">
      {categories.filter(c => catTotals[c]).map(cat => (
        <div key={cat}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium ${CATEGORY_COLORS[cat]}`}>
          <span>{cat}</span>
          <span className="font-bold">{catTotals[cat]}</span>
          <span className="opacity-50">({Math.round(catTotals[cat] / total * 100)}%)</span>
        </div>
      ))}
    </div>
  )
}

// Function: GreenImpactPanel
export default function GreenImpactPanel({ green }) {
  const [sortCol, setSortCol]       = useState('occurrences')
  const [sortDir, setSortDir]       = useState('desc')
  const [filterCat, setFilterCat]   = useState('All')
  const [filterLang, setFilterLang] = useState('All')
  const [showAll, setShowAll]       = useState(false)

  if (!green) {
    return (
      <div className="py-16 text-center text-blue-500">
        No green impact data available. Re-run analysis to generate green deficiency report.
      </div>
    )
  }

  const { deficiencies = [], green_score, risk_label,
          total_occurrences, total_effort_days, category_totals = {} } = green

  const categories = ['All', ...new Set(deficiencies.map(d => d.category))]
  const languages  = ['All', ...new Set(deficiencies.map(d => d.language))]

  const filtered = useMemo(() => {
    let rows = deficiencies
    if (filterCat  !== 'All') rows = rows.filter(d => d.category === filterCat)
    if (filterLang !== 'All') rows = rows.filter(d => d.language === filterLang)
    return [...rows].sort((a, b) => {
      const va = a[sortCol] ?? 0, vb = b[sortCol] ?? 0
      return sortDir === 'desc' ? (vb > va ? 1 : -1) : (va > vb ? 1 : -1)
    })
  }, [deficiencies, filterCat, filterLang, sortCol, sortDir])

  const shown = showAll ? filtered : filtered.slice(0, 15)

  // Function: toggleSort
  function toggleSort(col) {
    if (sortCol === col) setSortDir(d => d === 'desc' ? 'asc' : 'desc')
    else { setSortCol(col); setSortDir('desc') }
  }

  // Function: Th
  const Th = ({ col, children }) => (
    <th
      className="px-3 py-2.5 text-left text-xs font-semibold text-blue-400 cursor-pointer hover:text-white select-none whitespace-nowrap"
      onClick={() => toggleSort(col)}
    >
      <span className="flex items-center gap-1">
        {children}
        {sortCol === col
          ? (sortDir === 'desc' ? <ChevronDown size={12} /> : <ChevronUp size={12} />)
          : <span className="w-3" />}
      </span>
    </th>
  )

  return (
    <div className="space-y-5">
      {/* Header KPIs */}
      <div className="flex flex-wrap items-start gap-4">
        <ScoreBadge score={green_score} risk={risk_label} />
        <div className="flex gap-3 flex-wrap">
          <Kpi label="Total Occurrences" value={total_occurrences.toLocaleString()} icon={TrendingDown} color="text-red-400" />
          <Kpi label="Remediation Effort" value={`${total_effort_days.toFixed(1)} p-days`} icon={Leaf} color="text-green-400" />
          <Kpi label="Risk Level" value={risk_label} color={
            risk_label === 'LOW' ? 'text-green-400' :
            risk_label === 'MEDIUM' ? 'text-amber-400' :
            risk_label === 'HIGH' ? 'text-orange-400' : 'text-red-400'
          } />
        </div>
      </div>

      {/* Category totals */}
      {Object.keys(category_totals).length > 0 && (
        <CategorySummaryBar catTotals={category_totals} />
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <FilterSelect label="Category" value={filterCat} options={categories} onChange={setFilterCat} />
        <FilterSelect label="Language" value={filterLang} options={languages}  onChange={setFilterLang} />
        <span className="text-xs text-blue-500 ml-auto">{filtered.length} deficiencies</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-surface-border">
        <table className="w-full text-sm">
          <thead className="bg-gray-900/60 border-b border-surface-border">
            <tr>
              <th className="px-3 py-2.5 text-left text-xs font-semibold text-blue-400 w-8">#</th>
              <th className="px-3 py-2.5 text-left text-xs font-semibold text-blue-400">Green Deficiency</th>
              <th className="px-3 py-2.5 text-left text-xs font-semibold text-blue-400">Category</th>
              <Th col="language">Technology</Th>
              <Th col="occurrences">Occurrences</Th>
              <Th col="effort_days">Green Impact Effort (?)</Th>
              <Th col="affected_files">Affected Files</Th>
            </tr>
          </thead>
          <tbody>
            {shown.map((d, i) => (
              <motion.tr
                key={`${d.rule_key}-${d.language}`}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.02 }}
                className="border-b border-surface-border/50 hover:bg-gray-800/30 transition-colors"
              >
                <td className="px-3 py-2.5 text-blue-600 text-xs">{i + 1}</td>
                <td className="px-3 py-2.5 text-blue-200 font-medium">{d.label}</td>
                <td className="px-3 py-2.5">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${CATEGORY_COLORS[d.category] || 'bg-gray-800 text-blue-300 border-gray-700'}`}>
                    {d.category}
                  </span>
                </td>
                <td className="px-3 py-2.5">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${LANG_COLORS[d.language] || 'bg-gray-700 text-blue-300'}`}>
                    {d.language}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-right font-mono">
                  <span className={`font-bold ${
                    d.occurrences > 1000 ? 'text-red-400' :
                    d.occurrences > 200  ? 'text-amber-400' :
                    d.occurrences > 50   ? 'text-yellow-400' : 'text-blue-300'
                  }`}>{d.occurrences.toLocaleString()}</span>
                </td>
                <td className="px-3 py-2.5 text-right font-mono text-green-300 font-semibold">
                  {d.effort_days.toFixed(2)} person-day
                </td>
                <td className="px-3 py-2.5 text-right text-blue-400">
                  {d.affected_files}
                </td>
              </motion.tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-blue-500 text-sm">
                  No deficiencies found for the selected filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {filtered.length > 15 && (
        <button
          onClick={() => setShowAll(v => !v)}
          className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
        >
          {showAll ? 'Show less' : `Show all ${filtered.length} deficiencies`}
        </button>
      )}

      <p className="text-xs text-blue-600 italic">
        Efforts are indicative. Educate the team with these deficiencies as good practices in terms
        of green software development, yielding better usage of resources and performance.
      </p>
    </div>
  )
}

// Function: Kpi
function Kpi({ label, value, icon: Icon, color }) {
  return (
    <div className="flex flex-col px-4 py-2 rounded-xl bg-gray-900/60 border border-surface-border min-w-28">
      <div className="flex items-center gap-1.5 mb-0.5">
        {Icon && <Icon size={12} className={color || 'text-blue-400'} />}
        <span className="text-[10px] text-blue-500">{label}</span>
      </div>
      <span className={`text-base font-bold ${color || 'text-blue-300'}`}>{value}</span>
    </div>
  )
}

// Function: FilterSelect
function FilterSelect({ label, value, options, onChange }) {
  return (
    <label className="flex items-center gap-2 text-xs text-blue-400">
      {label}:
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="bg-gray-900 border border-surface-border rounded px-2 py-1 text-xs text-blue-300 focus:outline-none"
      >
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  )
}
