// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/components (KPICard.jsx)
// Date: 2026-01-04
// ---------------------------------------------------------------------------
import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const colorMap = {
  cyan: {
    bg:       'bg-sky-50',
    border:   'border-sky-300',
    value:    'text-sky-600',
    icon:     'bg-sky-100 text-sky-600',
    trend_up: 'text-emerald-600',
    trend_dn: 'text-rose-600',
  },
  indigo: {
    bg:       'bg-indigo-50',
    border:   'border-indigo-300',
    value:    'text-indigo-600',
    icon:     'bg-indigo-100 text-indigo-600',
    trend_up: 'text-emerald-600',
    trend_dn: 'text-rose-600',
  },
  emerald: {
    bg:       'bg-emerald-50',
    border:   'border-emerald-400',
    value:    'text-emerald-700',
    icon:     'bg-emerald-100 text-emerald-700',
    trend_up: 'text-emerald-600',
    trend_dn: 'text-rose-600',
  },
  amber: {
    bg:       'bg-amber-50',
    border:   'border-amber-400',
    value:    'text-amber-700',
    icon:     'bg-amber-100 text-amber-700',
    trend_up: 'text-emerald-600',
    trend_dn: 'text-rose-600',
  },
  rose: {
    bg:       'bg-rose-50',
    border:   'border-rose-300',
    value:    'text-rose-600',
    icon:     'bg-rose-100 text-rose-600',
    trend_up: 'text-rose-600',
    trend_dn: 'text-emerald-600',
  },
}

// Function: SkeletonCard
function SkeletonCard() {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="skeleton h-8 w-28 rounded mb-3" />
      <div className="skeleton h-6 w-20 rounded mb-2" />
      <div className="skeleton h-3 w-32 rounded" />
    </div>
  )
}

// Function: trendDisplay
function trendDisplay(trend, invertTrend, p) {
  const trendNum = typeof trend === 'number' ? trend : parseFloat(trend)
  if (isNaN(trendNum)) {
    return { hasTrend: false, trendNum, TrendIcon: Minus, trendClass: 'text-slate-400' }
  }
  if (trendNum > 0) {
    return { hasTrend: true, trendNum, TrendIcon: TrendingUp, trendClass: invertTrend ? p.trend_dn : p.trend_up }
  }
  if (trendNum < 0) {
    return { hasTrend: true, trendNum, TrendIcon: TrendingDown, trendClass: invertTrend ? p.trend_up : p.trend_dn }
  }
  return { hasTrend: true, trendNum, TrendIcon: Minus, trendClass: 'text-slate-400' }
}

// Function: KPICard
export default function KPICard({
  title,
  value,
  subtitle,
  trend,
  trendLabel,
  icon: Icon,
  color = 'cyan',
  loading = false,
  invertTrend = false,
  onClick,
}) {
  if (loading) return <SkeletonCard />

  const p = colorMap[color] || colorMap.cyan
  const { hasTrend, trendNum, TrendIcon, trendClass } = trendDisplay(trend, invertTrend, p)

  const Comp = onClick ? 'button' : 'div'

  return (
    <Comp
      type={onClick ? 'button' : undefined}
      onClick={onClick}
      className={`w-full text-left rounded-xl border ${p.border} ${p.bg} p-4 shadow-sm hover:shadow-md transition-shadow ${onClick ? 'cursor-pointer hover:-translate-y-0.5 transition-transform' : ''}`}
    >
      <div className="flex items-start justify-between mb-2">
        {Icon && (
          <div className={`p-2 rounded-lg ${p.icon}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
        {hasTrend && (
          <div className={`flex items-center gap-1 text-xs font-medium ${trendClass}`}>
            <TrendIcon className="w-3.5 h-3.5" />
            <span>{Math.abs(trendNum).toFixed(1)}%</span>
          </div>
        )}
      </div>

      <p className={`text-3xl font-bold mt-1 tabular-nums ${p.value}`}>
        {value !== null && value !== undefined ? value : '—'}
      </p>

      <p className="text-sm font-semibold text-slate-700 mt-1 truncate">{title}</p>

      {(subtitle || trendLabel) && (
        <p className="text-xs text-slate-400 mt-0.5 truncate">
          {trendLabel || subtitle}
        </p>
      )}
    </Comp>
  )
}
