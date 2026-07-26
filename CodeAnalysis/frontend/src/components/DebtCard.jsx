// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (DebtCard.jsx)
// Date: 2025-10-13
// ---------------------------------------------------------------------------
import { DollarSign } from 'lucide-react'
import { motion } from 'framer-motion'
import { riskColor, fmtUSD, fmtNumber } from '../utils.js'
import MiniBar from './MiniBar.jsx'

// Function: StatRow
function StatRow({ label, value }) {
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-surface-border last:border-0">
      <span className="text-xs text-blue-500">{label}</span>
      <span className="text-xs font-mono font-medium text-blue-200">{value}</span>
    </div>
  )
}

// Function: DebtCard
export default function DebtCard({ debt }) {
  if (!debt) return null
  const rc = riskColor(debt.risk_label)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.05 }}
      className="glass p-6 flex flex-col gap-5"
    >
      {/* Header */}
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
          <DollarSign size={16} className="text-warning" />
        </div>
        <span className="font-semibold text-sm text-blue-300">Technical Debt</span>
        <span className={`pill ml-auto ${rc.bg} ${rc.text} border ${rc.border}`}>
          {debt.risk_label}
        </span>
      </div>

      {/* Hero number */}
      <div className="flex items-end gap-3">
        <span className="text-4xl font-extrabold text-blue-300">{debt.debt_months}</span>
        <span className="text-blue-400 pb-1 text-sm">person-months</span>
      </div>

      {/* Debt ratio bar */}
      <MiniBar label="Debt Ratio" value={debt.debt_ratio} max={100} />

      {/* Stats */}
      <div className="border border-surface-border rounded-xl p-3 space-y-0.5">
        <StatRow label="KSLOC"             value={fmtNumber(debt.total_ksloc)} />
        <StatRow label="Est. Total Effort" value={`${debt.estimated_effort} PM`} />
        <StatRow label="FTEs Required"     value={debt.debt_ftes} />
        <StatRow label="Estimated Cost"    value={fmtUSD(debt.debt_usd)} />
        <StatRow label="Density"           value={`${debt.density} PM/kLOC`} />
      </div>
    </motion.div>
  )
}
