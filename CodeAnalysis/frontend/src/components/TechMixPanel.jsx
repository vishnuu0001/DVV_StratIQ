// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (TechMixPanel.jsx)
// Date: 2026-07-10
// ---------------------------------------------------------------------------
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { Code2 } from 'lucide-react'

const LANG_COLORS = [
  '#22d3ee', '#818cf8', '#f97316', '#4ade80', '#fb923c',
  '#a78bfa', '#f472b6', '#34d399', '#60a5fa', '#fbbf24',
]

// Function: CustomTooltip
function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="glass px-3 py-2 text-xs border border-surface-border rounded-lg shadow-lg">
      <div className="font-semibold text-blue-300">{d.language}</div>
      <div className="text-blue-400">{d.sloc.toLocaleString()} SLOC</div>
      <div className="text-blue-400">{d.pct.toFixed(1)}%</div>
    </div>
  )
}

// Function: ccColor
const ccColor = (v) => v >= 10 ? '#ef4444' : v >= 5 ? '#f59e0b' : '#4ade80'
// Function: ratioColor
const ratioColor = (v) => v >= 0.15 ? '#4ade80' : v >= 0.05 ? '#f59e0b' : '#ef4444'

// Function: TechMixPanel
export default function TechMixPanel({ language_reports = [] }) {
  if (!language_reports.length) return null

  const total = language_reports.reduce((s, r) => s + r.total_sloc, 0) || 1
  const data = language_reports
    .map((r, i) => ({
      language: r.language,
      sloc:     r.total_sloc,
      pct:      (r.total_sloc / total) * 100,
      color:    LANG_COLORS[i % LANG_COLORS.length],
    }))
    .sort((a, b) => b.sloc - a.sloc)

  return (
    <div className="glass overflow-hidden">
      <div className="px-6 py-4 border-b border-surface-border flex items-center gap-2">
        <Code2 size={15} className="text-brand-cyan" />
        <h3 className="text-sm font-semibold text-blue-300">Technology Mix</h3>
        <span className="text-xs text-blue-500 ml-auto">{total.toLocaleString()} total SLOC</span>
      </div>

      <div className="p-5">
        {/* Legend pills */}
        <div className="flex flex-wrap gap-2 mb-4">
          {data.map((d) => (
            <div key={d.language} className="flex items-center gap-1.5 text-xs text-blue-300">
              <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: d.color }} />
              <span>{d.language}</span>
              <span className="text-blue-500">{d.pct.toFixed(0)}%</span>
            </div>
          ))}
        </div>

        {/* Horizontal bar chart */}
        <ResponsiveContainer width="100%" height={Math.max(80, data.length * 36)}>
          <BarChart
            layout="vertical"
            data={data}
            margin={{ left: 0, right: 40, top: 0, bottom: 0 }}
          >
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="language"
              width={80}
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              content={<CustomTooltip />}
              cursor={{ fill: 'rgba(255,255,255,0.03)' }}
            />
            <Bar dataKey="pct" radius={[0, 4, 4, 0]}>
              {data.map((d) => (
                <Cell key={d.language} fill={d.color} fillOpacity={0.85} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Detailed per-language stats table ───────────────────────────── */}
      <div className="border-t border-surface-border overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-surface-border bg-gray-900/40">
              <th className="px-4 py-2.5 text-left text-blue-500 font-medium">Language</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Files</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">SLOC</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">SLOC %</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Avg CC</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Max CC</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Functions</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Classes</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Dependencies</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Comment Ratio</th>
              <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Long Methods %</th>
            </tr>
          </thead>
          <tbody>
            {language_reports.slice().sort((a, b) => b.total_sloc - a.total_sloc).map((r, i) => {
              const color = LANG_COLORS[language_reports.indexOf(r) % LANG_COLORS.length]
              const pct   = total > 0 ? ((r.total_sloc / total) * 100).toFixed(1) : '0.0'
              const depsCount = r.dependencies?.length ?? 0
              return (
                <tr key={r.language} className="border-b border-surface-border/50 hover:bg-surface-hover">
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: color }} />
                      <span className="font-semibold text-blue-200">{r.language}</span>
                    </div>
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-blue-400">{r.file_count?.toLocaleString()}</td>
                  <td className="px-3 py-2.5 text-right font-mono text-blue-300 font-semibold">{r.total_sloc?.toLocaleString()}</td>
                  <td className="px-3 py-2.5 text-right font-mono">
                    <span style={{ color }} className="font-semibold">{pct}%</span>
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono font-semibold"
                      style={{ color: ccColor(r.avg_complexity ?? 0) }}>
                    {(r.avg_complexity ?? 0).toFixed(1)}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono font-semibold"
                      style={{ color: ccColor(r.max_complexity ?? 0) }}>
                    {r.max_complexity ?? '—'}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-blue-400">{r.total_functions?.toLocaleString()}</td>
                  <td className="px-3 py-2.5 text-right font-mono text-blue-400">{r.total_classes?.toLocaleString()}</td>
                  <td className="px-3 py-2.5 text-right font-mono">
                    <span className={depsCount >= 50 ? 'text-red-400 font-semibold' : depsCount >= 15 ? 'text-amber-400' : 'text-blue-400'}>
                      {depsCount.toLocaleString()}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono font-semibold"
                      style={{ color: ratioColor(r.comment_ratio ?? 0) }}>
                    {((r.comment_ratio ?? 0) * 100).toFixed(1)}%
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono">
                    <span className={(r.long_methods_pct ?? 0) > 15 ? 'text-red-400 font-semibold' : (r.long_methods_pct ?? 0) > 5 ? 'text-amber-400' : 'text-emerald-400'}>
                      {(r.long_methods_pct ?? 0).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        <div className="px-4 py-2 flex gap-4 text-[10px] text-blue-600">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-emerald-500/60" /> CC &lt; 5 = Low</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-amber-500/60" /> CC 5–9 = Medium</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-red-500/60" /> CC ≥ 10 = High</span>
        </div>
      </div>
    </div>
  )
}
