// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (OSSCard.jsx)
// Date: 2026-06-21
// ---------------------------------------------------------------------------
import { Shield, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'
import ScoreRing from './ScoreRing.jsx'
import MiniBar   from './MiniBar.jsx'
import { riskColor } from '../utils.js'

const SEV_STYLE = {
  CRITICAL: { bg: '#18181b', border: '#71717a', text: '#ffffff' },
  HIGH:     { bg: '#450a0a', border: '#ef4444', text: '#fca5a5' },
  MEDIUM:   { bg: '#431407', border: '#f59e0b', text: '#fcd34d' },
  LOW:      { bg: '#0f172a', border: '#334155', text: '#94a3b8' },
}

// Function: CveSevBox
function CveSevBox({ sev, count }) {
  const s = SEV_STYLE[sev]
  return (
    <div className="flex flex-col items-center py-2 rounded-lg border text-center"
      style={{ background: s.bg, borderColor: s.border }}>
      <span className="text-xl font-extrabold" style={{ color: s.text }}>{count}</span>
      <span className="text-[9px] uppercase tracking-wide mt-0.5" style={{ color: s.text }}>
        {sev}
      </span>
    </div>
  )
}

// Function: OSSCard
export default function OSSCard({ oss }) {
  if (!oss) return null
  const rc = riskColor(oss.risk_label)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="glass p-6 flex flex-col gap-5"
    >
      {/* Header */}
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center">
          <Shield size={16} className="text-brand-purple" />
        </div>
        <span className="font-semibold text-sm text-blue-300">OSS Safety</span>
        <span className={`pill ml-auto ${rc.bg} ${rc.text} border ${rc.border}`}>
          {oss.risk_label}
        </span>
      </div>

      {/* Ring + counters */}
      <div className="flex items-center gap-6">
        <ScoreRing value={oss.total} size={110} stroke={10} label="/100" />
        <div className="flex-1 space-y-3">
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: 'Total Deps',  value: oss.dependency_count, color: 'text-blue-300' },
              { label: 'Vulnerable',  value: oss.vulnerable_count, color: 'text-danger' },
              { label: 'Lic. Issues', value: oss.license_issues,   color: 'text-warning' },
              { label: 'Stale',       value: oss.stale_count,      color: 'text-blue-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-surface rounded-lg p-2.5 text-center">
                <div className={`text-lg font-bold ${color}`}>{value}</div>
                <div className="text-[10px] text-blue-500 mt-0.5">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CVE severity breakdown */}
      {(oss.cve_critical > 0 || oss.cve_high > 0 || oss.cve_medium > 0 || oss.cve_low > 0) && (
        <div>
          <div className="text-[10px] text-blue-500 uppercase tracking-wide mb-2">CVE Severity</div>
          <div className="grid grid-cols-4 gap-1.5">
            <CveSevBox sev="CRITICAL" count={oss.cve_critical ?? 0} />
            <CveSevBox sev="HIGH"     count={oss.cve_high     ?? 0} />
            <CveSevBox sev="MEDIUM"   count={oss.cve_medium   ?? 0} />
            <CveSevBox sev="LOW"      count={oss.cve_low      ?? 0} />
          </div>
        </div>
      )}

      {/* License risk breakdown */}
      {(oss.license_high_risk > 0 || oss.license_medium_risk > 0) && (
        <div>
          <div className="text-[10px] text-blue-500 uppercase tracking-wide mb-2">License Risk</div>
          <div className="grid grid-cols-3 gap-1.5">
            {[
              { l: 'High',   v: oss.license_high_risk   ?? 0, col: '#fca5a5' },
              { l: 'Medium', v: oss.license_medium_risk ?? 0, col: '#fcd34d' },
              { l: 'Low',    v: oss.license_low_risk    ?? 0, col: '#86efac' },
            ].map((b) => (
              <div key={b.l} className="flex flex-col items-center py-1.5 rounded-lg bg-surface border border-surface-border text-center">
                <span className="text-base font-bold" style={{ color: b.col }}>{b.v}</span>
                <span className="text-[9px] text-blue-500">{b.l}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sub-scores */}
      <div className="space-y-2.5">
        <MiniBar label="Security"  value={oss.security_score}  />
        <MiniBar label="Licensing" value={oss.license_score}   />
        <MiniBar label="Freshness" value={oss.freshness_score} />
      </div>

      {/* Findings */}
      {oss.findings?.length > 0 && (
        <div className="space-y-1.5 border-t border-surface-border pt-4">
          {oss.findings.map((f, i) => (
            <p key={i} className="text-xs text-blue-400 flex items-start gap-1.5">
              <AlertTriangle size={10} className="text-warning mt-0.5 shrink-0" />
              {f}
            </p>
          ))}
        </div>
      )}
    </motion.div>
  )
}
