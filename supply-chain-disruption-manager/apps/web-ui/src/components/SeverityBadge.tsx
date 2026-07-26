// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (SeverityBadge.tsx)
// Date: 2026-06-23
// ---------------------------------------------------------------------------
import React from 'react'

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400 border border-red-500/30',
  high: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
  med: 'bg-yellow-400/20 text-yellow-300 border border-yellow-400/30',
  low: 'bg-cyan-400/20 text-cyan-400 border border-cyan-400/30',
  info: 'bg-slate-600/20 text-slate-400 border border-slate-600/30',
}

interface Props {
  severity: string
}

// Function: SeverityBadge
export function SeverityBadge({ severity }: Props) {
  const style = SEVERITY_STYLES[severity.toLowerCase()] ?? SEVERITY_STYLES['info']
  return (
    <span className={`text-xs px-2 py-0.5 rounded font-mono uppercase tracking-wide ${style}`}>
      {severity}
    </span>
  )
}
