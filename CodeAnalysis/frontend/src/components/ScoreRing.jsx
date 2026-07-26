// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (ScoreRing.jsx)
// Date: 2025-09-09
// ---------------------------------------------------------------------------
import { useEffect, useRef } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'
import { scoreColor } from '../utils.js'

/**
 * Animated SVG ring that draws from 0 to `value` on mount.
 */
// Function: ScoreRing
export default function ScoreRing({ value = 0, size = 120, stroke = 10, label, children }) {
  const r   = (size - stroke) / 2
  const circ = 2 * Math.PI * r
  
  const count = useMotionValue(0)
  const dashOffset = useTransform(count, (v) => circ - (v / 100) * circ)
  const displayVal = useTransform(count, Math.round)

  useEffect(() => {
    const controls = animate(count, value, { duration: 1.2, ease: 'easeOut' })
    return controls.stop
  }, [value])

  const color = scoreColor(value)

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Track */}
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none"
          stroke="#2a2d3e"
          strokeWidth={stroke}
        />
        {/* Progress */}
        <motion.circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeDasharray={circ}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${color}60)` }}
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {children || (
          <>
            <motion.span className="text-2xl font-bold text-blue-300" style={{ color }}>
              {displayVal}
            </motion.span>
            {label && <span className="text-[10px] text-blue-500 mt-0.5">{label}</span>}
          </>
        )}
      </div>
    </div>
  )
}
