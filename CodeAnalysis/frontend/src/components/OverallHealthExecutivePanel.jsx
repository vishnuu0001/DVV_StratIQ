// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (OverallHealthExecutivePanel.jsx)
// Date: 2026-06-22
// ---------------------------------------------------------------------------
import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  HeartPulse, AlertTriangle, Gauge, MessageSquareText,
} from 'lucide-react'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'

// Function: scoreColor
function scoreColor(v) {
  if (v >= 80) return 'text-emerald-400'
  if (v >= 65) return 'text-yellow-400'
  if (v >= 50) return 'text-orange-400'
  return 'text-red-400'
}

// Function: riskBand
function riskBand(v) {
  if (v >= 80) return { bar: 'bg-emerald-500', chip: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/35' }
  if (v >= 65) return { bar: 'bg-lime-500', chip: 'bg-lime-500/15 text-lime-300 border-lime-500/35' }
  if (v >= 50) return { bar: 'bg-amber-500', chip: 'bg-amber-500/15 text-amber-300 border-amber-500/35' }
  return { bar: 'bg-red-500', chip: 'bg-red-500/15 text-red-300 border-red-500/35' }
}

// Function: StatTile
function StatTile({ label, value, sub, color = 'text-blue-300' }) {
  return (
    <div className="glass p-4 rounded-xl">
      <div className="text-[11px] text-blue-500 uppercase tracking-wide">{label}</div>
      <div className={`text-3xl font-extrabold mt-1 ${color}`}>{value}</div>
      {sub && <div className="text-[10px] text-blue-600 mt-1">{sub}</div>}
    </div>
  )
}

// Function: DimCard
function DimCard({ label, value }) {
  const rb = riskBand(value ?? 0)
  return (
    <div className="rounded-xl border border-surface-border bg-surface px-3 py-3 overflow-hidden relative">
      <div className={`absolute left-0 top-0 h-1 w-full ${rb.bar}`} />
      <div className="text-[10px] text-blue-500 uppercase tracking-wide">{label}</div>
      <div className={`text-2xl font-bold mt-0.5 ${scoreColor(value ?? 0)}`}>
        {(value ?? 0).toFixed(1)}
      </div>
    </div>
  )
}

// Function: Tip
function Tip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface border border-surface-border rounded-lg px-3 py-2 text-xs">
      <div className="font-semibold text-blue-300 mb-1">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color || p.fill }} />
          <span className="text-blue-400">{p.name}</span>
          <span className="text-blue-300 font-mono">{p.value}</span>
        </div>
      ))}
    </div>
  )
}

// Function: OverallHealthExecutivePanel
export default function OverallHealthExecutivePanel({ result }) {
  const q = result?.quality_coverage
  const reports = result?.language_reports || []

  const totals = useMemo(() => {
    const code = reports.reduce((s, r) => s + (r.total_sloc || 0), 0)
    const comment = reports.reduce((s, r) => s + (r.total_comments || 0), 0)
    const commentedOut = reports.reduce((s, r) => s + (r.commented_out_lines || 0), 0)
    const pureComment = Math.max(0, comment - commentedOut)
    return { code, pureComment, commentedOut }
  }, [reports])

  const commentDonut = useMemo(() => ([
    { name: 'Code', value: totals.code, color: '#60a5fa' },
    { name: 'Comment Lines', value: totals.pureComment, color: '#22c55e' },
    { name: 'Commented-out Code', value: totals.commentedOut, color: '#f59e0b' },
  ].filter(x => x.value > 0)), [totals])

  const severityTrend = useMemo(() => {
    const matrix = q?.vulnerability_age_matrix || {}
    const order = ['>3y', '2-3y', '1-2y', '<1y']
    return order.map((age) => ({
      age,
      critical: matrix[age]?.critical || 0,
      high: matrix[age]?.high || 0,
      medium: matrix[age]?.medium || 0,
      low: matrix[age]?.low || 0,
    }))
  }, [q])

  if (!q) {
    return (
      <div className="glass p-8 text-center text-blue-500">
        Overall quality executive data is not available yet. Run analysis again to generate this view.
      </div>
    )
  }

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <div className="glass p-5 rounded-xl border border-surface-border">
        <div className="flex flex-wrap items-center gap-2">
          <HeartPulse size={16} className="text-emerald-400" />
          <h3 className="text-base font-semibold text-blue-200">Overall Health / Quality Executive</h3>
          <span className="ml-auto text-xs text-blue-500">Single-page executive risk view</span>
        </div>

        {/* CAST-style risk legend strip */}
        <div className="mt-4 rounded-lg border border-surface-border overflow-hidden">
          <div className="px-3 py-2 bg-surface text-[11px] text-blue-400 uppercase tracking-wide">
            Risk Legend (ISO 1-4 style)
          </div>
          <div className="grid grid-cols-4">
            {[
              { idx: '1', label: 'Very High Risk', cls: 'bg-red-500/15 text-red-300 border-red-500/30' },
              { idx: '2', label: 'High Risk', cls: 'bg-amber-500/15 text-amber-300 border-amber-500/30' },
              { idx: '3', label: 'Medium Risk', cls: 'bg-lime-500/15 text-lime-300 border-lime-500/30' },
              { idx: '4', label: 'Low Risk', cls: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' },
            ].map((r) => (
              <div key={r.idx} className={`px-3 py-2 border-r last:border-r-0 border-surface-border ${r.cls}`}>
                <div className="text-xs font-bold">{r.idx}</div>
                <div className="text-[11px] leading-tight">{r.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatTile label="TQI" value={`${(q.tqi_score_4 || 0).toFixed(2)}/4`} color="text-brand-cyan" />
        <StatTile label="Quality Score" value={(q.total || 0).toFixed(1)} sub={q.risk_label} color={scoreColor(q.total || 0)} />
        <StatTile label="Critical Violations" value={q.critical_violations || 0} color="text-red-400" />
        <StatTile label="Violation Density" value={(q.violation_density_per_kloc || 0).toFixed(2)} sub="per kLOC" color="text-orange-400" />
      </div>

      {/* CAST-style score band */}
      <div className="glass p-4 rounded-xl">
        <div className="text-xs text-blue-500 mb-2">Quality Score Band</div>
        <div className="h-3 rounded-full overflow-hidden flex border border-surface-border">
          <div className="w-1/4 bg-red-500/80" />
          <div className="w-1/4 bg-amber-500/80" />
          <div className="w-1/4 bg-lime-500/80" />
          <div className="w-1/4 bg-emerald-500/80" />
        </div>
        <div className="flex justify-between mt-1 text-[10px] text-blue-500">
          <span>0-49</span>
          <span>50-64</span>
          <span>65-79</span>
          <span>80-100</span>
        </div>
      </div>

      <div className="glass p-5 rounded-xl">
        <div className="flex items-center gap-2 mb-3">
          <Gauge size={14} className="text-blue-400" />
          <span className="text-sm font-semibold text-blue-300">Quality Drivers</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          <DimCard label="Robustness" value={q.robustness} />
          <DimCard label="Efficiency" value={q.efficiency} />
          <DimCard label="Security" value={q.security} />
          <DimCard label="Changeability" value={q.changeability} />
          <DimCard label="Transferability" value={q.transferability} />
          <DimCard label="Green" value={q.green} />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="glass p-5 rounded-xl">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquareText size={14} className="text-emerald-400" />
            <span className="text-sm font-semibold text-blue-300">Comments Composition</span>
          </div>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={commentDonut} dataKey="value" nameKey="name" innerRadius={68} outerRadius={98} paddingAngle={3}>
                  {commentDonut.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
                <Tooltip content={<Tip />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-xs text-blue-500 mt-2">
            Comment ratio: {(q.comment_ratio_pct || 0).toFixed(2)}% · Commented-out ratio: {(q.commented_out_ratio_pct || 0).toFixed(2)}%
          </div>
        </div>

        <div className="glass p-5 rounded-xl">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={14} className="text-warning" />
            <span className="text-sm font-semibold text-blue-300">Severity Trend by Dependency Age</span>
          </div>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={severityTrend} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="age" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<Tip />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line type="monotone" dataKey="critical" name="Critical" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="high" name="High" stroke="#f97316" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="medium" name="Medium" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="low" name="Low" stroke="#60a5fa" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="glass rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-surface-border text-sm font-semibold text-blue-300">
          Top Critical Rules
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-surface-border text-blue-500">
                <th className="px-3 py-2 text-left">Rule</th>
                <th className="px-3 py-2 text-left">Category</th>
                <th className="px-3 py-2 text-left">Severity</th>
                <th className="px-3 py-2 text-right">Count</th>
              </tr>
            </thead>
            <tbody>
              {(q.top_critical_rules || []).slice(0, 10).map((r, i) => (
                <tr key={i} className="border-b border-surface-border/60 hover:bg-surface-hover">
                  <td className="px-3 py-2 text-blue-300">{r.rule}</td>
                  <td className="px-3 py-2 text-blue-500 capitalize">{r.category}</td>
                  <td className="px-3 py-2 uppercase text-blue-500">{r.severity}</td>
                  <td className="px-3 py-2 text-right font-mono font-bold text-red-400">{r.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  )
}
