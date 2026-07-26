// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/components/charts (WaterfallChart.tsx)
// Date: 2025-11-03
// ---------------------------------------------------------------------------
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from 'recharts'
import { formatCurrencyCompact } from '../../utils/format'

interface WaterfallProps {
  gross: number
  transitionCost: number
  net: number
}

interface TooltipPayload {
  value: number
  payload: { label: string; total: number; color: string }
}

// Function: CustomTooltip
function CustomTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload?.length) return null
  const p = payload[0]
  return (
    <div className="bg-navy-700 border border-navy-600 rounded-lg p-3 text-xs shadow-xl">
      <div className="font-semibold text-slate-200 mb-1">{p.payload.label}</div>
      <div className="text-slate-300">{formatCurrencyCompact(p.payload.total)}</div>
    </div>
  )
}

// Function: WaterfallChart
export default function WaterfallChart({ gross, transitionCost, net }: WaterfallProps) {
  // Waterfall simulation using invisible base + visible bar
  const data = [
    { label: 'Gross Capacity', base: 0, value: gross, total: gross, color: '#34D399' },
    { label: 'Transition Cost', base: net, value: transitionCost, total: -transitionCost, color: '#F87171' },
    { label: 'Net Year 1', base: 0, value: net, total: net, color: '#3B82F6' },
  ]

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#162338" vertical={false} />
        <XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
        <YAxis
          tickFormatter={(v) => formatCurrencyCompact(v)}
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={60}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#162338' }} />
        {/* Invisible base bar */}
        <Bar dataKey="base" stackId="stack" fill="transparent" />
        {/* Visible value bar */}
        <Bar dataKey="value" stackId="stack" radius={[4, 4, 0, 0]} maxBarSize={60}>
          {data.map((entry) => (
            <Cell key={entry.label} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
