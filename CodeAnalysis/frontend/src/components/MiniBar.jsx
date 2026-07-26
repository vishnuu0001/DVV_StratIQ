// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (MiniBar.jsx)
// Date: 2026-04-16
// ---------------------------------------------------------------------------
import { motion } from 'framer-motion'
import { scoreColor } from '../utils.js'

// Function: MiniBar
export default function MiniBar({ label, value, max = 100, className = '' }) {
  const pct   = Math.min(100, Math.max(0, (value / max) * 100))
  const color = scoreColor(pct)

  return (
    <div className={`space-y-1 ${className}`}>
      <div className="flex justify-between text-xs text-blue-400">
        <span>{label}</span>
        <span style={{ color }}>{Number(value).toFixed(1)}</span>
      </div>
      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          style={{ background: `linear-gradient(90deg, ${color}99, ${color})` }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.9, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}
