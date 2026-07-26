// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (HealthCard.jsx)
// Date: 2025-08-25
// ---------------------------------------------------------------------------
import { HeartPulse, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'
import ScoreRing from './ScoreRing.jsx'
import MiniBar   from './MiniBar.jsx'
import { riskColor } from '../utils.js'

// Function: HealthCard
export default function HealthCard({ health }) {
  if (!health) return null
  const rc = riskColor(health.risk_label)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass p-6 flex flex-col gap-5"
    >
      {/* Header */}
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
          <HeartPulse size={16} className="text-success" />
        </div>
        <span className="font-semibold text-sm text-blue-300">Software Health</span>
        <span className={`pill ml-auto ${rc.bg} ${rc.text} border ${rc.border}`}>
          {health.risk_label}
        </span>
      </div>

      {/* Ring + sub-scores */}
      <div className="flex items-center gap-6">
        <ScoreRing value={health.health} size={110} stroke={10} label="/100" />
        <div className="flex-1 space-y-3">
          <MiniBar label="Resiliency" value={health.resiliency} />
          <MiniBar label="Agility"    value={health.agility} />
          <MiniBar label="Elegance"   value={health.elegance} />
        </div>
      </div>

      {/* Findings */}
      {health.summary?.length > 0 && (
        <div className="space-y-1.5 border-t border-surface-border pt-4">
          <div className="text-xs text-blue-500 font-medium mb-1 flex items-center gap-1">
            <AlertTriangle size={11} className="text-warning" /> Findings
          </div>
          {health.summary.slice(0, 4).map((f, i) => (
            <p key={i} className="text-xs text-blue-400 pl-3 border-l border-warning/30">
              {f}
            </p>
          ))}
          {health.summary.length > 4 && (
            <p className="text-xs text-blue-600">+{health.summary.length - 4} more…</p>
          )}
        </div>
      )}
    </motion.div>
  )
}
