// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (Timeline.tsx)
// Date: 2026-03-12
// ---------------------------------------------------------------------------
import React from 'react'
import { CheckCircle, AlertCircle, Clock, User, Bot, XCircle, Play } from 'lucide-react'
import type { TimelineEvent } from '../api/agents'

const STATE_COLORS: Record<string, string> = {
  RESOLVED: 'text-green-400 border-green-500/30 bg-green-500/10',
  CLASSIFIED: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10',
  DISPATCHED: 'text-purple-400 border-purple-500/30 bg-purple-500/10',
  IN_PROGRESS: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
  AWAITING_APPROVAL: 'text-yellow-300 border-yellow-400/30 bg-yellow-400/10',
  ESCALATED: 'text-red-400 border-red-500/30 bg-red-500/10',
  REJECTED: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
  FAILED: 'text-red-500 border-red-600/30 bg-red-600/10',
  BLOCKED: 'text-orange-400 border-orange-500/30 bg-orange-500/10',
  NEW: 'text-text-2 border-border bg-surface-2',
}

// Function: getIcon
function getIcon(eventType: string) {
  if (eventType.includes('resolved')) return <CheckCircle size={14} className="text-green-400" />
  if (eventType.includes('reject')) return <XCircle size={14} className="text-rose-400" />
  if (eventType.includes('approved')) return <CheckCircle size={14} className="text-cyan-400" />
  if (eventType.includes('human')) return <User size={14} className="text-amber-400" />
  if (eventType.includes('agent') || eventType.includes('specialist')) return <Bot size={14} className="text-purple-400" />
  if (eventType.includes('start') || eventType.includes('trigger')) return <Play size={14} className="text-cyan-400" />
  if (eventType.includes('error') || eventType.includes('fail')) return <AlertCircle size={14} className="text-red-400" />
  return <Clock size={14} className="text-text-3" />
}

// Function: formatTs
function formatTs(ts: string): string {
  try {
    const d = new Date(ts)
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ts
  }
}

interface Props {
  events: TimelineEvent[]
}

// Function: Timeline
export function Timeline({ events }: Props) {
  if (events.length === 0) {
    return <div className="text-text-3 text-sm py-4 text-center">No timeline events</div>
  }

  return (
    <div className="space-y-0">
      {events.map((evt, i) => {
        const stateClass = STATE_COLORS[evt.event_type.toUpperCase()] ?? STATE_COLORS['NEW']
        return (
          <div key={evt.id} className="flex gap-3 group">
            {/* Line + dot */}
            <div className="flex flex-col items-center">
              <div className="w-7 h-7 rounded-full bg-surface-2 border border-border flex items-center justify-center shrink-0 mt-0.5">
                {getIcon(evt.event_type)}
              </div>
              {i < events.length - 1 && <div className="w-px flex-1 bg-border min-h-4 my-1" />}
            </div>
            {/* Content */}
            <div className="pb-4 flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`text-xs px-1.5 py-0.5 rounded border font-mono uppercase ${stateClass}`}>
                  {evt.event_type.replace(/_/g, ' ')}
                </span>
                <span className="text-xs text-text-3 font-mono">{formatTs(evt.created_at)}</span>
                {evt.actor && (
                  <span className="text-xs text-text-3">
                    by <span className="text-text-2">{evt.actor}</span>
                  </span>
                )}
              </div>
              {evt.message && (
                <p className="text-sm text-text-2 mt-1 leading-relaxed">{evt.message}</p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
