// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (SecurityVulnsPanel.jsx)
// Date: 2026-04-04
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { ShieldAlert, Search, ExternalLink } from 'lucide-react'
import { motion } from 'framer-motion'

const SEV_CONFIG = {
  CRITICAL: { label: 'Critical Severity', bg: '#18181b', border: '#71717a', text: '#ffffff' },
  HIGH:     { label: 'High Severity',     bg: '#7f1d1d', border: '#ef4444', text: '#fca5a5' },
  MEDIUM:   { label: 'Medium Severity',   bg: '#78350f', border: '#f59e0b', text: '#fcd34d' },
  LOW:      { label: 'Low Severity',      bg: '#1e293b', border: '#475569', text: '#94a3b8' },
}

// Function: SeverityBox
function SeverityBox({ sev, count }) {
  const cfg = SEV_CONFIG[sev]
  return (
    <div
      className="flex flex-col items-center justify-center py-5 rounded-xl border"
      style={{ background: cfg.bg, borderColor: cfg.border }}
    >
      <span className="text-4xl font-extrabold" style={{ color: cfg.text }}>{count}</span>
      <span className="text-[11px] font-semibold mt-1 uppercase tracking-wide" style={{ color: cfg.text }}>
        {cfg.label}
      </span>
    </div>
  )
}

const LIC_RISK_COLOR = {
  HIGH:    { bg: '#7f1d1d', text: '#fca5a5', border: '#ef4444' },
  MEDIUM:  { bg: '#78350f', text: '#fcd34d', border: '#f59e0b' },
  LOW:     { bg: '#14532d', text: '#86efac', border: '#22c55e' },
}

// Function: LicRiskBadge
function LicRiskBadge({ risk }) {
  const c = LIC_RISK_COLOR[risk] || LIC_RISK_COLOR.LOW
  return (
    <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded border"
      style={{ background: c.bg, color: c.text, borderColor: c.border }}>
      {risk}
    </span>
  )
}

// Function: SevBadge
function SevBadge({ sev }) {
  if (!sev) return <span className="text-blue-600 text-xs">—</span>
  const colors = {
    CRITICAL: 'text-blue-300 bg-zinc-900 border-zinc-600',
    HIGH:     'text-red-300 bg-red-950 border-red-700',
    MEDIUM:   'text-amber-300 bg-amber-950 border-amber-700',
    LOW:      'text-slate-400 bg-slate-900 border-slate-600',
  }
  return (
    <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${colors[sev] || colors.LOW}`}>
      {sev}
    </span>
  )
}

// Function: scoreColor
function scoreColor(v) {
  if (v >= 80) return 'text-emerald-400'
  if (v >= 65) return 'text-yellow-400'
  if (v >= 50) return 'text-orange-400'
  return 'text-red-400'
}

// Function: DimCard
function DimCard({ label, value }) {
  return (
    <div className="rounded-xl border border-surface-border bg-surface p-3">
      <div className="text-[10px] text-blue-500 uppercase tracking-wide">{label}</div>
      <div className={`text-2xl font-bold mt-0.5 ${scoreColor(value ?? 0)}`}>
        {(value ?? 0).toFixed(1)}
      </div>
    </div>
  )
}

// Function: SecurityVulnsPanel
export default function SecurityVulnsPanel({ oss, quality }) {
  const [search, setSearch] = useState('')
  const [tab, setTab] = useState('all') // all | vuln | license | stale

  if (!oss) return null

  const details = oss.details || []
  const filtered = details.filter((d) => {
    if (search && !d.name.toLowerCase().includes(search.toLowerCase())) return false
    if (tab === 'vuln')    return d.vulnerable
    if (tab === 'license') return d.license_risk === 'HIGH' || d.license_risk === 'MEDIUM'
    if (tab === 'stale')   return !d.age_ok
    return true
  })

  return (
    <div className="glass overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-surface-border flex items-center gap-2">
        <ShieldAlert size={15} className="text-danger" />
        <h3 className="text-sm font-semibold text-blue-300">Security Vulnerabilities & License Compliance</h3>
      </div>

      {/* CVE severity boxes */}
      <div className="p-5 grid grid-cols-2 md:grid-cols-4 gap-3">
        {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
          <SeverityBox key={s} sev={s} count={oss[`cve_${s.toLowerCase()}`] ?? 0} />
        ))}
      </div>

      {/* License risk row */}
      <div className="px-5 pb-4 grid grid-cols-3 gap-3">
        {[
          { label: 'High Risk',   count: oss.license_high_risk   ?? 0, risk: 'HIGH' },
          { label: 'Medium Risk', count: oss.license_medium_risk ?? 0, risk: 'MEDIUM' },
          { label: 'Low Risk',    count: oss.license_low_risk    ?? 0, risk: 'LOW' },
        ].map((b) => (
          <div key={b.risk}
            className="flex flex-col items-center py-4 rounded-xl border"
            style={{
              background: LIC_RISK_COLOR[b.risk].bg,
              borderColor: LIC_RISK_COLOR[b.risk].border,
            }}>
            <span className="text-3xl font-extrabold" style={{ color: LIC_RISK_COLOR[b.risk].text }}>
              {b.count}
            </span>
            <span className="text-[11px] font-semibold mt-1 uppercase tracking-wide"
              style={{ color: LIC_RISK_COLOR[b.risk].text }}>
              {b.label}
            </span>
          </div>
        ))}
      </div>

      {/* CAST-like quality dimensions */}
      {quality && (
        <div className="px-5 pb-5 border-t border-surface-border pt-4 space-y-4">
          <div className="flex items-center justify-between gap-3">
            <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wide">
              Quality Drivers (CAST-style)
            </h4>
            <div className="text-xs text-blue-500">
              TQI <span className="font-bold text-blue-300">{quality.tqi_score_4?.toFixed(2)}/4</span>
              {' '}· Risk <span className="font-semibold text-blue-300">{quality.risk_label}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
            <DimCard label="Robustness" value={quality.robustness} />
            <DimCard label="Efficiency" value={quality.efficiency} />
            <DimCard label="Security" value={quality.security} />
            <DimCard label="Changeability" value={quality.changeability} />
            <DimCard label="Transferability" value={quality.transferability} />
            <DimCard label="Green" value={quality.green} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            <div className="rounded-xl border border-surface-border bg-surface p-3">
              <div className="text-[10px] text-blue-500 uppercase tracking-wide">Critical Violations</div>
              <div className="text-2xl font-extrabold text-red-400 mt-0.5">
                {quality.critical_violations ?? 0}
              </div>
            </div>
            <div className="rounded-xl border border-surface-border bg-surface p-3">
              <div className="text-[10px] text-blue-500 uppercase tracking-wide">Violation Density</div>
              <div className="text-2xl font-extrabold text-orange-400 mt-0.5">
                {(quality.violation_density_per_kloc ?? 0).toFixed(2)}
              </div>
              <div className="text-[10px] text-blue-600">per kLOC</div>
            </div>
            <div className="rounded-xl border border-surface-border bg-surface p-3">
              <div className="text-[10px] text-blue-500 uppercase tracking-wide">Comment Health</div>
              <div className="text-xs text-blue-300 mt-1.5">
                comments: {(quality.comment_ratio_pct ?? 0).toFixed(2)}%
              </div>
              <div className="text-xs text-blue-300 mt-0.5">
                commented-out: {(quality.commented_out_ratio_pct ?? 0).toFixed(2)}%
              </div>
            </div>
          </div>

          {quality.top_critical_rules?.length > 0 && (
            <div className="rounded-xl border border-surface-border overflow-hidden">
              <div className="px-3 py-2 border-b border-surface-border text-[11px] font-semibold text-blue-400 uppercase tracking-wide">
                Top Critical Rules
              </div>
              <div className="divide-y divide-surface-border">
                {quality.top_critical_rules.slice(0, 6).map((r, i) => (
                  <div key={i} className="px-3 py-2 flex items-center gap-2 text-xs">
                    <span className="text-blue-300 flex-1">{r.rule}</span>
                    <span className="text-blue-500 uppercase">{r.severity}</span>
                    <span className="font-mono font-bold text-red-400">{r.count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {quality.vulnerability_age_matrix && (
            <div className="rounded-xl border border-surface-border overflow-hidden">
              <div className="px-3 py-2 border-b border-surface-border text-[11px] font-semibold text-blue-400 uppercase tracking-wide">
                Vulnerability Age Matrix
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-surface-border text-blue-500">
                      <th className="px-3 py-2 text-left">Age</th>
                      <th className="px-3 py-2 text-right">Critical</th>
                      <th className="px-3 py-2 text-right">High</th>
                      <th className="px-3 py-2 text-right">Medium</th>
                      <th className="px-3 py-2 text-right">Low</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(quality.vulnerability_age_matrix).map(([age, row]) => (
                      <tr key={age} className="border-b border-surface-border/60">
                        <td className="px-3 py-2 text-blue-300">{age}</td>
                        <td className="px-3 py-2 text-right font-mono text-red-400">{row.critical ?? 0}</td>
                        <td className="px-3 py-2 text-right font-mono text-orange-400">{row.high ?? 0}</td>
                        <td className="px-3 py-2 text-right font-mono text-yellow-400">{row.medium ?? 0}</td>
                        <td className="px-3 py-2 text-right font-mono text-blue-400">{row.low ?? 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Dependency table */}
      <div className="border-t border-surface-border">
        {/* Tabs + search */}
        <div className="px-5 pt-3 pb-0 flex flex-wrap items-center gap-3">
          <div className="flex gap-1">
            {[
              { k: 'all',     l: 'All' },
              { k: 'vuln',    l: 'Vulnerable' },
              { k: 'license', l: 'License Issues' },
              { k: 'stale',   l: 'Stale' },
            ].map((t) => (
              <button key={t.k} onClick={() => setTab(t.k)}
                className={`tab-btn ${tab === t.k ? 'active' : ''}`}>
                {t.l}
              </button>
            ))}
          </div>
          <div className="ml-auto relative">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-blue-500" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search component…"
              className="input-field pl-7 py-1 text-xs w-44"
            />
          </div>
        </div>

        <div className="overflow-x-auto scrollbar-thin max-h-72">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border">
                {['Component', 'Ecosystem', 'Version', 'License', 'Lic. Risk', 'CVE Severity', 'CVEs'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-blue-500 whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-sm text-blue-600">
                    No matching components
                  </td>
                </tr>
              )}
              {filtered.map((d, i) => (
                <motion.tr
                  key={`${d.name}-${i}`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.01 }}
                  className="border-b border-surface-border hover:bg-surface-hover transition-colors"
                >
                  <td className="px-4 py-2.5 font-medium text-blue-300 text-xs whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      {d.name}
                      {d.cve_ids?.length > 0 && (
                        <a href={`https://nvd.nist.gov/vuln/search/results?query=${d.cve_ids[0]}`}
                          target="_blank" rel="noreferrer"
                          className="text-blue-600 hover:text-brand-cyan">
                          <ExternalLink size={10} />
                        </a>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-2.5 text-xs text-blue-400 capitalize">{d.ecosystem}</td>
                  <td className="px-4 py-2.5 text-xs font-mono text-blue-400">
                    {d.latest_version !== 'unknown' ? d.latest_version : '—'}
                  </td>
                  <td className="px-4 py-2.5 text-xs text-blue-400 max-w-[140px] truncate">
                    {d.license || '—'}
                  </td>
                  <td className="px-4 py-2.5"><LicRiskBadge risk={d.license_risk || 'LOW'} /></td>
                  <td className="px-4 py-2.5"><SevBadge sev={d.cve_severity} /></td>
                  <td className="px-4 py-2.5 text-xs font-mono text-blue-400">
                    {d.cve_ids?.slice(0, 2).join(', ') || '—'}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
