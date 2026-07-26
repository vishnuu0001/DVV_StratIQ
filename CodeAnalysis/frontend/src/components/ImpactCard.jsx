// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (ImpactCard.jsx)
// Date: 2025-07-18
// ---------------------------------------------------------------------------
import { TrendingUp } from 'lucide-react'
import { motion }     from 'framer-motion'
import ScoreRing from './ScoreRing.jsx'
import MiniBar   from './MiniBar.jsx'
import { riskColor } from '../utils.js'

const DIMS = [
  { key: 'user_volume_score',   label: 'User Volume'    },
  { key: 'release_freq_score',  label: 'Release Freq.'  },
  { key: 'revenue_score',       label: 'Revenue Impact' },
  { key: 'age_risk_score',      label: 'Age Risk'       },
  { key: 'operational_score',   label: 'Operational'    },
  { key: 'integration_score',   label: 'Integration'    },
]

// Function: ImpactCard
export default function ImpactCard({ impact }) {
  if (!impact) return null
  const rc = riskColor(impact.risk_label)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.20 }}
      className="glass p-6 flex flex-col gap-5"
    >
      {/* Header */}
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
          <TrendingUp size={16} className="text-brand-blue" />
        </div>
        <span className="font-semibold text-sm text-blue-300">Business Impact</span>
        <span className={`pill ml-auto ${rc.bg} ${rc.text} border ${rc.border}`}>
          {impact.risk_label}
        </span>
      </div>

      {/* Ring */}
      <div className="flex items-center gap-6">
        <ScoreRing value={impact.total} size={110} stroke={10} label="/100" />
        <div className="flex-1 space-y-2.5">
          {DIMS.slice(0, 4).map(({ key, label }) => (
            <MiniBar key={key} label={label} value={impact[key]} />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2.5">
        {DIMS.slice(4).map(({ key, label }) => (
          <MiniBar key={key} label={label} value={impact[key]} />
        ))}
      </div>
    </motion.div>
  )
}
