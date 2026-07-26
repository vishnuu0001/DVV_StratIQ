// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/components (InsightPanel.jsx)
// Date: 2025-07-15
// ---------------------------------------------------------------------------
import React from 'react'
import { TrendingUp, AlertTriangle, XCircle, Info } from 'lucide-react'

const LEVEL_CONFIG = {
  good: {
    Icon: TrendingUp,
    bg:         'bg-emerald-50',
    border:     'border-l-4 border-emerald-500',
    text:       'text-emerald-800',
    iconColor:  'text-emerald-600',
  },
  warn: {
    Icon: AlertTriangle,
    bg:         'bg-amber-50',
    border:     'border-l-4 border-amber-500',
    text:       'text-amber-900',
    iconColor:  'text-amber-600',
  },
  critical: {
    Icon: XCircle,
    bg:         'bg-rose-50',
    border:     'border-l-4 border-rose-500',
    text:       'text-rose-800',
    iconColor:  'text-rose-600',
  },
  info: {
    Icon: Info,
    bg:         'bg-slate-50',
    border:     'border-l-4 border-slate-300',
    text:       'text-slate-700',
    iconColor:  'text-slate-400',
  },
}

// Function: InsightBullet
function InsightBullet({ item }) {
  const cfg = LEVEL_CONFIG[item.level] || LEVEL_CONFIG.info
  const { Icon } = cfg
  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded-r-lg ${cfg.bg} ${cfg.border}`}>
      <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${cfg.iconColor}`} />
      <p className={`text-sm leading-relaxed font-medium ${cfg.text}`}>{item.text}</p>
    </div>
  )
}

// Function: InsightPanel
export default function InsightPanel({ title = 'Leadership Insights', insights = [], loading = false }) {
  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-sky-600" />
          <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">{title}</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 bg-slate-100 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (!insights || insights.length === 0) return null

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-4 h-4 text-sky-600" />
        <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">{title}</h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
        {insights.map((item, i) => (
          <InsightBullet key={i} item={item} />
        ))}
      </div>
    </div>
  )
}
