// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (CloudReadyPanel.jsx)
// Date: 2025-09-06
// ---------------------------------------------------------------------------
import { Cloud, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'
import ScoreRing from './ScoreRing.jsx'
import MiniBar from './MiniBar.jsx'

// Function: ListItem
function ListItem({ text, type }) {
  const icon = type === 'booster'
    ? <CheckCircle2 size={12} className="text-emerald-400 flex-shrink-0 mt-0.5" />
    : <XCircle size={12} className="text-red-400 flex-shrink-0 mt-0.5" />

  return (
    <motion.li
      initial={{ opacity: 0, x: -6 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-start gap-2 text-xs text-blue-300 leading-snug"
    >
      {icon}
      {text}
    </motion.li>
  )
}

// Function: CloudReadyPanel
export default function CloudReadyPanel({ cloud }) {
  if (!cloud) return null

  const totalItems = (cloud.boosters?.length || 0) + (cloud.blockers?.length || 0) || 1
  const boosterPct = Math.round(((cloud.boosters?.length || 0) / totalItems) * 100)

  return (
    <div className="glass overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-surface-border flex items-center gap-2">
        <Cloud size={15} className="text-brand-cyan" />
        <h3 className="text-sm font-semibold text-blue-300">CloudReady Code Scan</h3>
        <span className="ml-auto text-xs text-blue-500">
          {cloud.roadblocks_count ?? 0} roadblock{cloud.roadblocks_count !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Score summary row */}
      <div className="p-5 grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'CloudReady',      value: cloud.total,            color: '#22d3ee' },
          { label: 'Code Scan',       value: cloud.cloud_ready_scan, color: '#60a5fa' },
          { label: 'Boosters',        value: cloud.boosters_score,   color: '#4ade80' },
          { label: 'Blockers',        value: cloud.blockers_score,   color: '#f87171' },
        ].map((s) => (
          <div key={s.label} className="flex flex-col items-center py-4 rounded-xl bg-surface border border-surface-border">
            <span className="text-3xl font-extrabold" style={{ color: s.color }}>
              {(s.value ?? 0).toFixed(1)}
            </span>
            <span className="text-[11px] text-blue-500 mt-1">{s.label}</span>
          </div>
        ))}
      </div>

      {/* Cloud dimensions */}
      <div className="px-5 pb-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Dimension bars */}
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wide">Dimensions</h4>
          {[
            { label: 'Stateless Design',       value: cloud.stateless_design },
            { label: 'Containerization',       value: cloud.containerization },
            { label: 'API Surface',            value: cloud.api_surface },
            { label: 'Config Externalisation', value: cloud.config_externalization },
            { label: 'Logging & Observability',value: cloud.logging_observability },
            { label: 'CI / CD Artifacts',      value: cloud.ci_cd_artifacts },
          ].map((d) => (
            <div key={d.label}>
              <MiniBar label={d.label} value={d.value ?? 0} />
            </div>
          ))}
        </div>

        {/* Boosters / Blockers lists */}
        <div className="space-y-4">
          {cloud.boosters?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wide mb-2 flex items-center gap-1">
                <CheckCircle2 size={11} /> Boosters ({cloud.boosters.length})
              </h4>
              <ul className="space-y-1.5">
                {cloud.boosters.map((b, i) => (
                  <ListItem key={i} text={b} type="booster" />
                ))}
              </ul>
            </div>
          )}

          {cloud.blockers?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wide mb-2 flex items-center gap-1">
                <XCircle size={11} /> Blockers ({cloud.blockers.length})
              </h4>
              <ul className="space-y-1.5">
                {cloud.blockers.map((b, i) => (
                  <ListItem key={i} text={b} type="blocker" />
                ))}
              </ul>
            </div>
          )}

          {cloud.findings?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-warning uppercase tracking-wide mb-2 flex items-center gap-1">
                <AlertTriangle size={11} /> Findings
              </h4>
              <ul className="space-y-1.5">
                {cloud.findings.map((f, i) => (
                  <li key={i} className="text-xs text-blue-400 flex items-start gap-2">
                    <AlertTriangle size={11} className="text-warning flex-shrink-0 mt-0.5" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
