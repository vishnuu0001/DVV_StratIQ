// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (ProgressOverlay.jsx)
// Date: 2025-11-03
// ---------------------------------------------------------------------------
import { motion } from 'framer-motion'
import { Code2 } from 'lucide-react'

// Function: ProgressOverlay
export default function ProgressOverlay({ job }) {
  const progress = job?.progress ?? 0
  const message  = job?.message  ?? 'Initialising…'

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      {/* Animated logo */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
        className="relative w-20 h-20 mb-8"
      >
        <div className="absolute inset-0 rounded-2xl bg-gradient-brand opacity-30 blur-xl" />
        <div className="relative w-20 h-20 rounded-2xl bg-gradient-brand flex items-center justify-center shadow-2xl shadow-indigo-500/50">
          <Code2 size={36} className="text-blue-300" />
        </div>
      </motion.div>

      <h2 className="text-2xl font-bold text-blue-300 mb-2">Analysing Repository</h2>
      <p className="text-blue-400 text-sm mb-10 text-center max-w-sm">{message}</p>

      {/* Progress bar */}
      <div className="w-full max-w-md">
        <div className="flex justify-between text-xs text-blue-500 mb-2">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="progress-bar">
          <motion.div
            className="progress-fill bg-gradient-cyan"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Step indicators */}
      <div className="mt-10 flex gap-6 text-xs text-blue-600">
        {['Clone', 'Parse', 'Metrics', 'Reports'].map((step, i) => {
          const stepPct = (i + 1) * 25
          const active  = progress >= stepPct - 10
          const done    = progress >= stepPct
          return (
            <div key={step} className="flex items-center gap-1.5">
              <motion.div
                animate={{ scale: active && !done ? [1, 1.2, 1] : 1 }}
                transition={{ repeat: active && !done ? Infinity : 0, duration: 1.2 }}
                className={`w-2 h-2 rounded-full transition-colors duration-500 ${
                  done   ? 'bg-success' :
                  active ? 'bg-brand-cyan' :
                           'bg-surface-border'
                }`}
              />
              <span className={done ? 'text-success' : active ? 'text-brand-cyan' : ''}>{step}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
