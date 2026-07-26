// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (Co2Card.jsx)
// Date: 2026-05-19
// ---------------------------------------------------------------------------
import { motion } from 'framer-motion'
import { Leaf, Zap, Server, TrendingDown } from 'lucide-react'
import ScoreRing from './ScoreRing.jsx'

// Function: StatBox
function StatBox({ icon: Icon, label, value, unit, color = '#4ade80' }) {
  return (
    <div className="flex flex-col gap-1 p-3 rounded-xl bg-surface border border-surface-border">
      <div className="flex items-center gap-1.5 text-xs text-blue-500">
        <Icon size={11} style={{ color }} /> {label}
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-xl font-bold text-blue-300">{value}</span>
        <span className="text-xs text-blue-500">{unit}</span>
      </div>
    </div>
  )
}

// Function: Co2Card
export default function Co2Card({ data }) {
  if (!data) return null

  // Map co2 reduction potential to a 0-100 "green score"
  // Higher potential = worse (means not yet cloud-migrated)
  // Show as "reduction potential" – more tons saved = greener opportunity
  const opportunityScore = Math.min(100, data.cloud_gap_pct ?? 0)

  return (
    <div className="glass flex flex-col gap-4 p-5">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Leaf size={14} className="text-emerald-400" />
        <span className="text-sm font-semibold text-blue-300">CO₂ Reduction Potential</span>
        <span className="ml-auto text-[10px] text-blue-500 bg-surface px-2 py-0.5 rounded-full border border-surface-border">
          /year
        </span>
      </div>

      {/* Main figure */}
      <div className="flex items-center gap-5">
        <div className="flex flex-col items-center min-w-[80px]">
          <ScoreRing score={opportunityScore} size={80} stroke={7} label="Gap">
            <span className="text-xs font-bold text-blue-300">{opportunityScore.toFixed(0)}%</span>
          </ScoreRing>
          <span className="text-[10px] text-blue-500 mt-1">cloud gap</span>
        </div>

        <div className="flex-1 space-y-1">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-baseline gap-1"
          >
            <span className="text-4xl font-extrabold text-emerald-400">
              {data.co2_tons_year?.toFixed(1)}
            </span>
            <span className="text-sm text-blue-400 font-medium">tons CO₂</span>
          </motion.div>
          <p className="text-xs text-blue-500 leading-relaxed">
            Estimated annual CO₂ savings by fully migrating on-prem workloads to cloud-native infrastructure.
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-2">
        <StatBox
          icon={Zap}
          label="Electricity saved"
          value={data.mwh_year?.toFixed(1)}
          unit="MWh/yr"
          color="#facc15"
        />
        <StatBox
          icon={Server}
          label="Est. servers"
          value={data.servers_estimated}
          unit="on-prem"
          color="#60a5fa"
        />
      </div>

      {/* MtM change placeholder */}
      <div className="flex items-center gap-1.5 text-xs text-blue-500 border-t border-surface-border pt-3">
        <TrendingDown size={11} className="text-emerald-400" />
        <span>Cloud migration reduces energy use ~40% (EPA/IEA 2023 model)</span>
      </div>
    </div>
  )
}
