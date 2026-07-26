// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/components/charts (TopVendorsChart.tsx)
// Date: 2025-12-19
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
import type { VendorRecord } from '../../types'
import { formatCurrencyCompact } from '../../utils/format'

interface Props {
  data: VendorRecord[]
}

const SIGNAL_COLORS: Record<string, string> = {
  High: '#F87171',
  Medium: '#FCD34D',
  Low: '#34D399',
}

interface TooltipPayload {
  value: number
  payload: VendorRecord
}

// Function: CustomTooltip
function CustomTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload?.length) return null
  const v = payload[0].payload
  return (
    <div className="bg-navy-700 border border-navy-600 rounded-lg p-3 text-xs shadow-xl min-w-[200px]">
      <div className="font-semibold text-slate-200 mb-1">{v.vendor}</div>
      <div className="text-slate-300 mb-1">{formatCurrencyCompact(v.annual_spend)}</div>
      <div className="text-slate-400">{v.spend_category} · {v.tower}</div>
      <div className={`mt-1 font-medium`} style={{ color: SIGNAL_COLORS[v.consolidation_signal] ?? '#94a3b8' }}>
        {v.consolidation_signal} consolidation signal
      </div>
    </div>
  )
}

// Function: TopVendorsChart
export default function TopVendorsChart({ data }: Props) {
  if (!data?.length) return <div className="flex items-center justify-center h-48 text-slate-500 text-sm">No data</div>

  const top10 = [...data]
    .map((v) => ({ ...v, annual_spend: typeof v.annual_spend === 'string' ? parseFloat(v.annual_spend) || 0 : v.annual_spend }))
    .sort((a, b) => b.annual_spend - a.annual_spend)
    .slice(0, 10)

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart
        data={top10}
        layout="vertical"
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#162338" horizontal={false} />
        <XAxis
          type="number"
          tickFormatter={(v) => formatCurrencyCompact(v)}
          tick={{ fill: '#94a3b8', fontSize: 10 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="vendor"
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={120}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#162338' }} />
        <Bar dataKey="annual_spend" radius={[0, 4, 4, 0]} maxBarSize={18}>
          {top10.map((entry) => (
            <Cell key={entry.vendor} fill={SIGNAL_COLORS[entry.consolidation_signal] ?? '#3B82F6'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
