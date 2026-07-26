// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (CloudCard.jsx)
// Date: 2026-04-17
// ---------------------------------------------------------------------------
import { Cloud, AlertCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import ScoreRing from './ScoreRing.jsx'
import MiniBar   from './MiniBar.jsx'
import { riskColor } from '../utils.js'

const DIMS = [
  { key: 'stateless_design',        label: 'Stateless Design' },
  { key: 'containerization',        label: 'Containerization' },
  { key: 'api_surface',             label: 'API Surface' },
  { key: 'config_externalization',  label: 'Config Extern.' },
  { key: 'logging_observability',   label: 'Logging & Obs.' },
  { key: 'ci_cd_artifacts',         label: 'CI/CD Artifacts' },
]

// Function: CloudCard
export default function CloudCard({ cloud }) {
  if (!cloud) return null
  const rc = riskColor(cloud.risk_label)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.10 }}
      className="glass p-6 flex flex-col gap-5"
    >
      {/* Header */}
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-sky-500/10 flex items-center justify-center">
          <Cloud size={16} className="text-sky-400" />
        </div>
        <span className="font-semibold text-sm text-blue-300">Cloud Maturity</span>
        <span className={`pill ml-auto ${rc.bg} ${rc.text} border ${rc.border}`}>
          {cloud.risk_label}
        </span>
      </div>

      {/* Ring + dims */}
      <div className="flex items-center gap-6">
        <ScoreRing value={cloud.total} size={110} stroke={10} label="/100" />
        <div className="flex-1 space-y-2.5">
          {DIMS.map(({ key, label }) => (
            <MiniBar key={key} label={label} value={cloud[key]} />
          ))}
        </div>
      </div>

      {/* Findings */}
      {cloud.findings?.length > 0 && (
        <div className="space-y-1.5 border-t border-surface-border pt-4">
          <div className="text-xs text-blue-500 font-medium mb-1 flex items-center gap-1">
            <AlertCircle size={11} className="text-sky-400" /> Findings
          </div>
          {cloud.findings.map((f, i) => (
            <p key={i} className="text-xs text-blue-400 pl-3 border-l border-sky-500/30">{f}</p>
          ))}
        </div>
      )}
    </motion.div>
  )
}
