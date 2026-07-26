// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (PortfolioScatter.jsx)
// Date: 2025-11-26
// ---------------------------------------------------------------------------
import { useState } from 'react'
import {
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, ReferenceLine, Label
} from 'recharts'
import { GitBranch } from 'lucide-react'

// Quadrant colours matching CAST Highlight style
const QUADRANT_LABELS = [
  { x: 75, y: 75, text: 'Most Ready\nfor Cloud',  color: '#4ade80' },
  { x: 75, y: 25, text: 'Green\nQuick Wins',      color: '#22d3ee' },
  { x: 25, y: 75, text: 'Financial\nBurdens',      color: '#f87171' },
  { x: 25, y: 25, text: 'Licensing\nExposures',    color: '#fb923c' },
]

// Function: pickColor
function pickColor(health, cloud) {
  const high = health >= 50 && cloud >= 50
  const quickWin = health >= 50 && cloud < 50
  const burden   = health < 50 && cloud >= 50
  if (high)     return '#4ade80'
  if (quickWin) return '#22d3ee'
  if (burden)   return '#f87171'
  return '#fb923c'
}

// Function: CustomTooltip
function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="glass px-3 py-2.5 text-xs border border-surface-border rounded-xl shadow-xl max-w-[200px]">
      <div className="font-semibold text-blue-300 truncate mb-1">{d.repo_name}</div>
      <div className="text-blue-400">Health: <span className="text-blue-300 font-mono">{d.health_score?.toFixed(0)}</span></div>
      <div className="text-blue-400">Cloud:  <span className="text-blue-300 font-mono">{d.cloud_score?.toFixed(0)}</span></div>
      <div className="text-blue-400">SLOC:   <span className="text-blue-300 font-mono">{d.sloc?.toLocaleString()}</span></div>
      {d.risk_label && (
        <div className="text-blue-400">Risk:   <span className="text-blue-300">{d.risk_label}</span></div>
      )}
    </div>
  )
}

// Custom dot that renders the repo name inside the bubble
// Function: CustomDot
function CustomDot(props) {
  const { cx, cy, payload, r } = props
  const color = pickColor(payload.health_score, payload.cloud_score)
  const radius = Math.max(16, r || 16)
  const name = (payload.repo_name || '').split('/').pop()
  const shortName = name.length > 8 ? name.slice(0, 7) + '…' : name

  return (
    <g>
      <circle cx={cx} cy={cy} r={radius} fill={color} fillOpacity={0.25} stroke={color} strokeWidth={1.5} />
      <text x={cx} y={cy + 1} textAnchor="middle" dominantBaseline="middle"
        fill={color} fontSize={Math.max(7, radius * 0.5)} fontWeight={600}>
        {shortName}
      </text>
    </g>
  )
}

// Function: PortfolioScatter
export default function PortfolioScatter({ portfolio = [] }) {
  const [hovered, setHovered] = useState(null)

  if (!portfolio.length) return null

  // Normalise SLOC to bubble size 300–3000
  const maxSloc = Math.max(...portfolio.map((p) => p.sloc || 1), 1)
  const data = portfolio.map((p) => ({
    ...p,
    x: p.health_score ?? 50,
    y: p.cloud_score  ?? 50,
    z: Math.max(300, ((p.sloc || 1) / maxSloc) * 3000),
  }))

  return (
    <div className="glass overflow-hidden">
      <div className="px-6 py-4 border-b border-surface-border flex items-center gap-2">
        <GitBranch size={15} className="text-brand-cyan" />
        <h3 className="text-sm font-semibold text-blue-300">Portfolio Map – Software Health vs Cloud Maturity</h3>
        <span className="text-xs text-blue-500 ml-auto">{portfolio.length} repos</span>
      </div>

      {/* Quadrant legend */}
      <div className="px-5 pt-3 flex flex-wrap gap-2">
        {[
          { label: 'Most Ready for Cloud', color: '#4ade80' },
          { label: 'Green Quick Wins',      color: '#22d3ee' },
          { label: 'Financial Burdens',      color: '#f87171' },
          { label: 'Licensing Exposures',    color: '#fb923c' },
        ].map((q) => (
          <span key={q.label} className="flex items-center gap-1.5 text-[11px] text-blue-400">
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: q.color, opacity: 0.7 }} />
            {q.label}
          </span>
        ))}
      </div>

      <div className="p-5">
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 10, right: 30, bottom: 30, left: 20 }}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="4 4" />

            <XAxis
              type="number" dataKey="x" name="Software Health"
              domain={[0, 100]} ticks={[0, 25, 50, 75, 100]}
              tick={{ fill: '#64748b', fontSize: 11 }}
              axisLine={{ stroke: '#1e293b' }} tickLine={false}
            >
              <Label value="Software Health" position="insideBottom" offset={-15}
                style={{ fill: '#64748b', fontSize: 11 }} />
            </XAxis>

            <YAxis
              type="number" dataKey="y" name="Cloud Maturity"
              domain={[0, 100]} ticks={[0, 25, 50, 75, 100]}
              tick={{ fill: '#64748b', fontSize: 11 }}
              axisLine={{ stroke: '#1e293b' }} tickLine={false}
            >
              <Label value="Cloud Maturity" angle={-90} position="insideLeft" offset={15}
                style={{ fill: '#64748b', fontSize: 11 }} />
            </YAxis>

            <ZAxis type="number" dataKey="z" range={[200, 3000]} />

            {/* Quadrant lines */}
            <ReferenceLine x={50} stroke="#334155" strokeDasharray="6 3" />
            <ReferenceLine y={50} stroke="#334155" strokeDasharray="6 3" />

            <Tooltip content={<CustomTooltip />} cursor={false} />

            <Scatter
              data={data}
              shape={<CustomDot />}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
