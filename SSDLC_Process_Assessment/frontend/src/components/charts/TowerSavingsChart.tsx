// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/components/charts (TowerSavingsChart.tsx)
// Date: 2025-11-21
// ---------------------------------------------------------------------------
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { TowerSummaryRow } from '../../types'
import { formatCurrencyCompact } from '../../utils/format'

interface Props {
  data: TowerSummaryRow[]
}

// Function: abbreviate
function abbreviate(tower: string): string {
  const map: Record<string, string> = {
    'Infrastructure': 'Infra',
    'Application Development': 'App Dev',
    'End User Computing': 'EUC',
    'Cybersecurity': 'Cyber',
    'Data & Analytics': 'D&A',
    'Cloud Services': 'Cloud',
    'Network & Connectivity': 'Network',
    'IT Service Management': 'ITSM',
  }
  return map[tower] ?? tower.slice(0, 8)
}

interface TooltipPayload {
  name: string
  value: number
  color: string
}

// Function: CustomTooltip
function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: TooltipPayload[]; label?: string }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-navy-700 border border-navy-600 rounded-lg p-3 text-xs shadow-xl min-w-[180px]">
      <div className="font-semibold text-slate-200 mb-2">{label}</div>
      {payload.map((p) => (
        <div key={p.name} className="flex justify-between gap-4">
          <span style={{ color: p.color }}>{p.name}</span>
          <span className="text-slate-300 font-medium">{formatCurrencyCompact(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

// Function: TowerSavingsChart
export default function TowerSavingsChart({ data }: Props) {
  if (!data?.length) return <div className="flex items-center justify-center h-48 text-slate-500 text-sm">No data</div>

  const chartData = data.map((row) => ({
    tower: abbreviate(row.tower),
    'Current Spend': row.current_spend,
    'Addressable Spend': row.addressable_spend,
    'Net Y1 Savings': row.net_year_1_savings,
  }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#162338" vertical={false} />
        <XAxis dataKey="tower" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis
          tickFormatter={(v) => formatCurrencyCompact(v)}
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={55}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#162338' }} />
        <Legend
          wrapperStyle={{ fontSize: 11, color: '#94a3b8' }}
        />
        <Bar dataKey="Current Spend" fill="#3B82F6" radius={[3, 3, 0, 0]} maxBarSize={24} />
        <Bar dataKey="Addressable Spend" fill="#8B5CF6" radius={[3, 3, 0, 0]} maxBarSize={24} />
        <Bar dataKey="Net Y1 Savings" fill="#34D399" radius={[3, 3, 0, 0]} maxBarSize={24} />
      </BarChart>
    </ResponsiveContainer>
  )
}
