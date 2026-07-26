// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/components/ui (KpiCard.tsx)
// Date: 2025-10-21
// ---------------------------------------------------------------------------
import { formatCurrencyCompact, formatPct, formatNumber } from '../../utils/format'

interface KpiCardProps {
  label: string
  value: number
  format?: 'currency' | 'pct' | 'count'
  subtitle?: string
  trend?: number
  accent?: 'blue' | 'green' | 'amber' | 'red' | 'purple' | 'cyan'
  loading?: boolean
}

const accentClasses: Record<string, string> = {
  blue: 'text-accent-blue',
  green: 'text-accent-green',
  amber: 'text-accent-amber',
  red: 'text-accent-red',
  purple: 'text-accent-purple',
  cyan: 'text-accent-cyan',
}

const borderClasses: Record<string, string> = {
  blue: 'border-accent-blue/20',
  green: 'border-accent-green/20',
  amber: 'border-accent-amber/20',
  red: 'border-accent-red/20',
  purple: 'border-accent-purple/20',
  cyan: 'border-accent-cyan/20',
}

const glowClasses: Record<string, string> = {
  blue: 'bg-accent-blue/5',
  green: 'bg-accent-green/5',
  amber: 'bg-accent-amber/5',
  red: 'bg-accent-red/5',
  purple: 'bg-accent-purple/5',
  cyan: 'bg-accent-cyan/5',
}

// Function: formatValue
function formatValue(value: number, format: 'currency' | 'pct' | 'count' = 'currency'): string {
  switch (format) {
    case 'currency':
      return formatCurrencyCompact(value)
    case 'pct':
      return formatPct(value)
    case 'count':
      return formatNumber(value)
  }
}

// Function: KpiCard
export default function KpiCard({
  label,
  value,
  format = 'currency',
  subtitle,
  trend,
  accent = 'blue',
  loading = false,
}: KpiCardProps) {
  const colorClass = accentClasses[accent] ?? accentClasses.blue
  const borderClass = borderClasses[accent] ?? borderClasses.blue
  const glowClass = glowClasses[accent] ?? glowClasses.blue

  if (loading) {
    return (
      <div className="bg-navy-800 border border-navy-700 rounded-xl p-5 space-y-3">
        <div className="h-3 w-24 rounded skeleton-shimmer" />
        <div className="h-8 w-32 rounded skeleton-shimmer" />
        <div className="h-2.5 w-20 rounded skeleton-shimmer" />
      </div>
    )
  }

  return (
    <div
      className={`${glowClass} border ${borderClass} rounded-xl p-5 flex flex-col gap-2 group hover:border-opacity-40 transition-all duration-200`}
      title={format === 'currency' ? `$${Math.round(value).toLocaleString()}` : undefined}
    >
      <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</div>
      <div className={`text-2xl font-bold ${colorClass} leading-none`}>
        {formatValue(value, format)}
      </div>
      {subtitle && <div className="text-xs text-slate-500">{subtitle}</div>}
      {trend !== undefined && (
        <div className={`text-xs font-medium ${trend >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
          {trend >= 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}%
        </div>
      )}
    </div>
  )
}
