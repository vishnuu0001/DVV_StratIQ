// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/components/charts (SpendByCategoryChart.tsx)
// Date: 2026-02-21
// ---------------------------------------------------------------------------
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { SpendBreakdown } from '../../types'
import { formatCurrencyCompact, toNum } from '../../utils/format'

interface Props {
  data: SpendBreakdown[]
}

const CATEGORY_COLORS: Record<string, string> = {
  Talent: '#3B82F6',
  Software: '#8B5CF6',
  Data: '#22D3EE',
  Hardware: '#F59E0B',
  Services: '#34D399',
  Other: '#F87171',
}

// Function: getColor
function getColor(category: string, index: number): string {
  const fallbacks = ['#3B82F6', '#8B5CF6', '#22D3EE', '#F59E0B', '#34D399', '#F87171', '#F9A8D4']
  return CATEGORY_COLORS[category] ?? fallbacks[index % fallbacks.length]
}

interface TooltipPayload {
  name: string
  value: number
  payload: SpendBreakdown
}

// Function: CustomTooltip
function CustomTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload?.length) return null
  const item = payload[0]
  return (
    <div className="bg-navy-700 border border-navy-600 rounded-lg p-3 text-xs shadow-xl">
      <div className="font-semibold text-slate-200 mb-1">{item.name}</div>
      <div className="text-slate-300">{formatCurrencyCompact(item.value)}</div>
      {item.payload.count !== undefined && (
        <div className="text-slate-500 mt-0.5">{item.payload.count} vendors</div>
      )}
    </div>
  )
}

// Function: CustomLegend
function CustomLegend({ payload }: { payload?: Array<{ value: string; color: string; payload: { value: number } }> }) {
  if (!payload) return null
  return (
    <ul className="flex flex-col gap-1.5 mt-2">
      {payload.map((entry) => (
        <li key={entry.value} className="flex items-center justify-between gap-4 text-xs">
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2.5 h-2.5 rounded-full shrink-0" style={{ background: entry.color }} />
            <span className="text-slate-400">{entry.value}</span>
          </span>
          <span className="text-slate-300 font-medium">{formatCurrencyCompact(entry.payload.value)}</span>
        </li>
      ))}
    </ul>
  )
}

// Function: SpendByCategoryChart
export default function SpendByCategoryChart({ data }: Props) {
  if (!data?.length) return <div className="flex items-center justify-center h-48 text-slate-500 text-sm">No data</div>

  // Coerce spend values from Decimal strings to numbers so Recharts doesn't crash on .toFixed()
  const coerced = data.map((d) => ({ ...d, spend: toNum((d as unknown as Record<string, unknown>).total_spend ?? d.spend) }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={coerced}
          cx="45%"
          cy="50%"
          innerRadius={65}
          outerRadius={100}
          dataKey="spend"
          nameKey="category"
          paddingAngle={2}
        >
          {coerced.map((entry, index) => (
            <Cell key={entry.category} fill={getColor(entry.category, index)} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          layout="vertical"
          align="right"
          verticalAlign="middle"
          content={<CustomLegend />}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
