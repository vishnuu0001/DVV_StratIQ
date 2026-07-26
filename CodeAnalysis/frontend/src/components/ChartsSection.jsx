// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (ChartsSection.jsx)
// Date: 2026-03-11
// ---------------------------------------------------------------------------
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { scoreColor } from '../utils.js'

const PALETTE = ['#61dafb', '#4ade80', '#fb923c', '#a78bfa', '#f472b6', '#38bdf8']

// Function: CustomTooltip
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass px-3 py-2 text-xs">
      <span className="text-blue-400">{payload[0].name}: </span>
      <span className="text-blue-300 font-semibold">{Number(payload[0].value).toFixed(1)}</span>
    </div>
  )
}

// Function: ChartsSection
export default function ChartsSection({ result }) {
  if (!result) return null
  const { health, debt, cloud, oss, impact, language_reports = [] } = result

  const radarData = [
    { subject: 'Health',      score: health?.health    ?? 0 },
    { subject: 'Debt (inv)',  score: 100 - (debt?.debt_ratio ?? 0) },
    { subject: 'Cloud',       score: cloud?.total      ?? 0 },
    { subject: 'OSS Safety',  score: oss?.total        ?? 0 },
    { subject: 'Biz Impact',  score: impact?.total     ?? 0 },
  ]

  const pieData = language_reports.map((r) => ({
    name:  r.language,
    value: r.total_sloc,
  }))

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      {/* Radar */}
      <div className="glass p-6">
        <h3 className="text-sm font-semibold text-blue-300 mb-4">Portfolio Radar</h3>
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
            <PolarGrid gridType="polygon" stroke="#2a2d3e" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 12 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }} />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#61dafb"
              fill="#61dafb"
              fillOpacity={0.15}
              strokeWidth={2}
            />
            <Tooltip content={<CustomTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Pie / Doughnut */}
      <div className="glass p-6">
        <h3 className="text-sm font-semibold text-blue-300 mb-4">Language Breakdown (SLOC)</h3>
        {pieData.length === 0 ? (
          <div className="h-[280px] flex items-center justify-center text-blue-600 text-sm">
            No language data
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(val) => <span className="text-xs text-blue-400">{val}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
