// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (StatCard.tsx)
// Date: 2026-04-20
// ---------------------------------------------------------------------------
import React from 'react'
import type { LucideIcon } from 'lucide-react'

interface Props {
  title: string
  value: string | number
  icon?: LucideIcon
  color?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  pulse?: boolean
  subtitle?: string
  onClick?: () => void
  active?: boolean
}

// Function: StatCard
export function StatCard({ title, value, icon: Icon, color = 'text-text', trend, trendValue, pulse, subtitle, onClick, active }: Props) {
  const className = `bg-surface border rounded-lg p-4 flex flex-col gap-2 relative overflow-hidden text-left ${
    active ? 'border-cyan-400/60 bg-cyan-500/5' : pulse ? 'border-pulse-red border' : 'border-border'
  } ${onClick ? 'hover:border-border-hi hover:bg-surface-2 transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-cyan-400/50' : ''}`

  const content = (
    <>
      <div className="flex items-center justify-between">
        <span className="text-xs text-text-2 uppercase tracking-wider font-medium">{title}</span>
        {Icon && <Icon size={16} className="text-text-3" />}
      </div>
      <div className={`text-2xl font-semibold font-mono ${color}`}>{value}</div>
      {subtitle && <div className="text-xs text-text-3">{subtitle}</div>}
      {trend && trendValue && (
        <div
          className={`text-xs font-mono ${
            trend === 'up' ? 'text-red-400' : trend === 'down' ? 'text-green-400' : 'text-text-3'
          }`}
        >
          {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
        </div>
      )}
      {pulse && (
        <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-red-500 dot-blink" />
      )}
    </>
  )

  if (onClick) {
    return (
      <button type="button" onClick={onClick} className={className} aria-pressed={active}>
        {content}
      </button>
    )
  }

  return (
    <div className={className}>
      {content}
    </div>
  )
}
