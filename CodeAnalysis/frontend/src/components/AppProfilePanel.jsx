// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (AppProfilePanel.jsx)
// Date: 2025-10-21
// ---------------------------------------------------------------------------
import { motion } from 'framer-motion'
import {
  Tag, Server, GitBranch, Code2, Layers, CheckCircle2, XCircle,
  Cpu, Cloud, Package, Zap, FileCheck, Paintbrush2, BarChart3, Network,
} from 'lucide-react'

// ── Colour helpers ────────────────────────────────────────────────────────────
// Function: levelColor
function levelColor(level = '') {
  const l = level.toLowerCase()
  if (l.startsWith('high') || l.startsWith('poor') || l.startsWith('lift'))
    return { text: 'text-red-300', bg: 'bg-red-500/10', border: 'border-red-500/30', dot: 'bg-red-400' }
  if (l.startsWith('medium') || l.startsWith('fair') || l.startsWith('partial') || l.startsWith('moderate'))
    return { text: 'text-amber-300', bg: 'bg-amber-500/10', border: 'border-amber-500/30', dot: 'bg-amber-400' }
  return { text: 'text-emerald-300', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', dot: 'bg-emerald-400' }
}

// Function: Badge
function Badge({ value }) {
  const c = levelColor(value)
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${c.text} ${c.bg} ${c.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${c.dot}`} />
      {value}
    </span>
  )
}

// ── Field row inside a card ───────────────────────────────────────────────────
// Function: FieldRow
function FieldRow({ icon: Icon, label, value, badge = false }) {
  return (
    <div className="flex items-start justify-between gap-3 py-2.5 border-b border-slate-700/40 last:border-0">
      <div className="flex items-center gap-2 min-w-0">
        <Icon size={13} className="text-slate-500 shrink-0" />
        <span className="text-[11px] text-slate-400 uppercase tracking-wide font-medium shrink-0">
          {label}
        </span>
      </div>
      {badge
        ? <Badge value={String(value || '—')} />
        : <span className="text-xs text-slate-200 text-right font-mono break-all">{value || '—'}</span>
      }
    </div>
  )
}

// ── Section card ─────────────────────────────────────────────────────────────
// Function: ProfileCard
function ProfileCard({ title, accent = 'blue', children }) {
  const accents = {
    blue:    'from-blue-500/10 to-cyan-500/10 border-blue-500/25',
    purple:  'from-purple-500/10 to-indigo-500/10 border-purple-500/25',
    emerald: 'from-emerald-500/10 to-teal-500/10 border-emerald-500/25',
    amber:   'from-amber-500/10 to-orange-500/10 border-amber-500/25',
  }
  return (
    <div className={`rounded-2xl border bg-gradient-to-br p-5 ${accents[accent] || accents.blue}`}>
      <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">{title}</h3>
      <div>{children}</div>
    </div>
  )
}

// ── Score pill ────────────────────────────────────────────────────────────────
// Function: ScorePill
function ScorePill({ label, score, max = 100, color = '#38bdf8' }) {
  const pct = Math.min(100, Math.max(0, (score / max) * 100))
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <span className="text-[10px] text-slate-400 uppercase tracking-wide">{label}</span>
        <span className="text-xs font-bold text-slate-200">{score}</span>
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

// ── Derive rationalization profile from result fields (works for any cached job) ──
// Function: deriveAppId
function deriveAppId(r) {
  const base = (r.repo_name || 'APP').toUpperCase().replace(/[^A-Z0-9]/g, '')
  return (base.slice(0, 10) || 'APP') + '_001'
}

// Function: deriveServerName
function deriveServerName(r) {
  try {
    if (r.repo_url) {
      const u = new URL(r.repo_url)
      return u.hostname || 'localhost'
    }
  } catch { /* ignore */ }
  return 'localhost'
}

// Function: deriveAppArchitecture
function deriveAppArchitecture(arch) {
  if (!arch?.layer_counts) return 'Monolithic'
  const lc    = arch.layer_counts
  const total = Object.values(lc).reduce((a, b) => a + b, 0) || 1
  const svc   = lc.Services || 0
  const pres  = lc.Presentation || 0
  const pers  = lc.Persistence || 0
  const coord = lc.Coordination || 0
  if (svc / total > 0.50) return 'Service-Oriented (SOA)'
  if (pres > 0 && pers > 0 && svc > 0) return 'Layered / N-Tier (MVC)'
  if (pres > 0 && pers > 0) return 'Two-Tier / Client-Server'
  if (svc > 0 || coord > 0) return 'Layered'
  return 'Monolithic'
}

// Function: deriveComponentCoupling
function deriveComponentCoupling(totalDeps, depPerFile) {
  if (depPerFile >= 5 || totalDeps >= 100) return 'High'
  if (depPerFile >= 2 || totalDeps >= 30) return 'Medium'
  return 'Low'
}

// Function: deriveCloudSuitability
function deriveCloudSuitability(cloudScore) {
  if (cloudScore >= 70) return 'Cloud-Ready'
  if (cloudScore >= 45) return 'Partially Ready'
  return 'Lift-and-Shift Required'
}

// Function: deriveApiReadiness
function deriveApiReadiness(r, cloudScore) {
  if (r.cloud_recommendations?.by_category) {
    const cats = Object.keys(r.cloud_recommendations.by_category)
    if (cats.some(c => /api|gateway|service|message/i.test(c))) return 'API-Ready'
    if (cloudScore >= 50) return 'Partial API Integration'
    return 'Not Detected'
  }
  if (cloudScore >= 50) return 'Partial API Integration'
  return 'Not Detected'
}

// Function: deriveProtocolDegree
function deriveProtocolDegree(elegance, avgComment) {
  if (elegance >= 70 && avgComment >= 0.10) return 'High'
  if (elegance >= 45 || avgComment >= 0.05) return 'Moderate'
  return 'Low'
}

// Function: deriveTotalBad
function deriveTotalBad(langReports) {
  return langReports.reduce((sum, r) => {
    if (!r.bad_practices) return sum
    return sum + Object.values(r.bad_practices).reduce((a, b) => a + (b ?? 0), 0)
  }, 0)
}

// Function: deriveCodeDesign
function deriveCodeDesign(elegance, totalBad) {
  if (elegance >= 70 && totalBad < 10) return 'Good'
  if (elegance >= 45 || totalBad < 50) return 'Fair'
  return 'Poor'
}

// Function: deriveComplexityLevel
function deriveComplexityLevel(totalSloc, avgCC) {
  if (totalSloc >= 50000 || avgCC >= 10) return 'High'
  if (totalSloc >= 10000 || avgCC >= 5) return 'Medium'
  return 'Low'
}

// Function: deriveDistributedArchitecture
function deriveDistributedArchitecture(r, arch) {
  let isDist = false
  const distEvidence = []
  if (arch?.layer_counts && (arch.layer_counts.Services ?? 0) >= 3) {
    isDist = true; distEvidence.push('Multiple service layers detected')
  }
  if (r.cloud_recommendations?.by_category) {
    if (Object.keys(r.cloud_recommendations.by_category).some(c => /gateway|bus|messaging|event/i.test(c))) {
      isDist = true; distEvidence.push('API gateway / messaging patterns detected')
    }
  }
  return isDist ? 'Yes — ' + distEvidence.join('; ') : 'No — Centralized Architecture'
}

// Function: computeProfile
function computeProfile(result) {
  const r = result
  const langReports = r.language_reports || []
  const totalSloc   = r.total_sloc ?? r.sloc ?? 0
  const totalFiles  = r.total_files ?? r.file_count ?? 0
  const languages   = r.languages_detected ?? r.languages ?? []
  const health      = r.health || {}
  const cloud       = r.cloud  || {}
  const arch        = r.architecture

  // APP ID
  const appId = deriveAppId(r)

  // SERVER_NAME
  const serverName = deriveServerName(r)

  // Application Architecture
  const appArch = deriveAppArchitecture(arch)

  // Source Code Availability
  const srcAvail = totalFiles > 0 ? 'Available' : 'Not Available'

  // Programming Language
  const allLangs   = languages.join(', ') || 'N/A'
  const primaryLang = langReports.length
    ? langReports.reduce((a, b) => ((a.total_sloc ?? 0) >= (b.total_sloc ?? 0) ? a : b)).language
    : 'N/A'

  // Component Coupling
  const totalDeps  = langReports.reduce((sum, r) => sum + (r.dependencies?.length ?? 0), 0)
  const depPerFile = totalDeps / Math.max(totalFiles, 1)
  const coupling   = deriveComponentCoupling(totalDeps, depPerFile)

  // Cloud Suitability
  const cloudScore = cloud.total ?? 0
  const cloudSuit  = deriveCloudSuitability(cloudScore)

  // Volume of External Dependencies
  const depLbl = totalDeps >= 50 ? 'High' : totalDeps >= 15 ? 'Medium' : 'Low'

  // API Readiness
  const apiReady = deriveApiReadiness(r, cloudScore)

  // Code Protocol Degree
  const avgComment = langReports.length
    ? langReports.reduce((s, r) => s + (r.comment_ratio ?? 0), 0) / langReports.length : 0
  const elegance   = health.elegance ?? 0
  const protocolDeg = deriveProtocolDegree(elegance, avgComment)

  // Code Design
  const totalBad = deriveTotalBad(langReports)
  const codeDesign = deriveCodeDesign(elegance, totalBad)

  // Complexity / Volume
  const avgCC = langReports.length
    ? langReports.reduce((s, r) => s + (r.avg_complexity ?? 0), 0) / langReports.length : 0
  const complexLevel = deriveComplexityLevel(totalSloc, avgCC)

  // Distributed Architecture
  const distLabel = deriveDistributedArchitecture(r, arch)

  return {
    app_id:                       appId,
    app_name:                     r.repo_name,
    server_name:                  serverName,
    repo_name:                    r.repo_url || r.repo_name,
    application_architecture:     appArch,
    source_code_availability:     srcAvail,
    programming_language:         allLangs,
    primary_language:             primaryLang,
    component_coupling:           coupling,
    cloud_suitability:            cloudSuit,
    cloud_score:                  Math.round(cloudScore * 10) / 10,
    volume_external_dependencies: `${depLbl} (${totalDeps} deps)`,
    total_deps_count:             totalDeps,
    api_readiness:                apiReady,
    code_protocol_degree:         protocolDeg,
    code_design:                  codeDesign,
    elegance_score:               Math.round(elegance * 10) / 10,
    complexity_volume:            `${complexLevel} (${totalSloc.toLocaleString()} SLOC, avg CC=${avgCC.toFixed(1)})`,
    complexity_level:             complexLevel,
    avg_cyclomatic:               Math.round(avgCC * 10) / 10,
    distributed_architecture:     distLabel,
  }
}

// ── Main panel ────────────────────────────────────────────────────────────────
// Function: AppProfilePanel
export default function AppProfilePanel({ result }) {
  // Use backend-computed profile if present, otherwise derive from result fields
  const p = result?.rationalization_profile ?? (result ? computeProfile(result) : null)
  if (!p) {
    return (
      <div className="flex items-center justify-center py-24 text-slate-500">
        <p className="text-sm">Rationalization profile not available.</p>
      </div>
    )
  }

  const isDistributed = p.distributed_architecture?.startsWith('Yes')
  const srcAvailable  = p.source_code_availability === 'Available'

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* ── Header banner ── */}
      <div className="rounded-2xl border border-slate-700/50 bg-gradient-to-r from-slate-900 via-slate-800/60 to-slate-900 px-6 py-5 flex flex-wrap items-center gap-6">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/30 to-cyan-500/20 border border-blue-400/30 flex items-center justify-center shrink-0">
            <Tag size={22} className="text-blue-300" />
          </div>
          <div className="min-w-0">
            <p className="text-lg font-bold text-white truncate">{p.app_name}</p>
            <p className="text-xs text-slate-400 font-mono">{p.app_id}</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-3 ml-auto">
          <div className="flex items-center gap-1.5 text-xs text-slate-300 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg">
            <Server size={12} className="text-slate-500" />
            <span>{p.server_name}</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-300 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg">
            <GitBranch size={12} className="text-slate-500" />
            <span className="max-w-[200px] truncate">{p.repo_name}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">

        {/* ── Identity ── */}
        <ProfileCard title="Identification" accent="blue">
          <FieldRow icon={Tag}      label="App ID"    value={p.app_id} />
          <FieldRow icon={Tag}      label="App Name"  value={p.app_name} />
          <FieldRow icon={Server}   label="Server"    value={p.server_name} />
          <FieldRow icon={GitBranch} label="Repo"     value={p.repo_name} />
        </ProfileCard>

        {/* ── Architecture ── */}
        <ProfileCard title="Architecture" accent="purple">
          <FieldRow icon={Layers} label="App Architecture" value={p.application_architecture} />
          <div className="flex items-start justify-between gap-3 py-2.5 border-b border-slate-700/40">
            <div className="flex items-center gap-2">
              {srcAvailable
                ? <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                : <XCircle size={13} className="text-red-400 shrink-0" />
              }
              <span className="text-[11px] text-slate-400 uppercase tracking-wide font-medium">Source Code</span>
            </div>
            <Badge value={p.source_code_availability} />
          </div>
          <FieldRow icon={Code2}   label="Language"  value={p.programming_language} />
          <div className="flex items-start justify-between gap-3 py-2.5">
            <div className="flex items-center gap-2">
              <Network size={13} className="text-slate-500 shrink-0" />
              <span className="text-[11px] text-slate-400 uppercase tracking-wide font-medium">Distributed</span>
            </div>
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
              isDistributed
                ? 'text-purple-300 bg-purple-500/10 border-purple-500/30'
                : 'text-slate-300 bg-slate-700/40 border-slate-600/40'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${isDistributed ? 'bg-purple-400' : 'bg-slate-500'}`} />
              {isDistributed ? 'Distributed' : 'Centralized'}
            </span>
          </div>
        </ProfileCard>

        {/* ── Cloud & Dependencies ── */}
        <ProfileCard title="Cloud & Dependencies" accent="emerald">
          <div className="mb-3">
            <ScorePill label="Cloud Suitability Score" score={p.cloud_score} color="#34d399" />
          </div>
          <FieldRow icon={Cloud}   label="Cloud Suitability"   value={p.cloud_suitability}            badge />
          <FieldRow icon={Package} label="External Deps"        value={p.volume_external_dependencies} badge />
          <FieldRow icon={Zap}     label="API Readiness"        value={p.api_readiness}                badge />
        </ProfileCard>

        {/* ── Code Quality ── */}
        <ProfileCard title="Code Quality" accent="amber">
          <div className="mb-3">
            <ScorePill label="Elegance Score" score={p.elegance_score} color="#fb923c" />
          </div>
          <FieldRow icon={Cpu}          label="Component Coupling"  value={p.component_coupling}    badge />
          <FieldRow icon={FileCheck}    label="Code Protocols"      value={p.code_protocol_degree}  badge />
          <FieldRow icon={Paintbrush2}  label="Code Design"         value={p.code_design}           badge />
        </ProfileCard>

        {/* ── Complexity ── */}
        <ProfileCard title="Complexity & Volume" accent="purple">
          <div className="mb-3 space-y-2">
            <ScorePill label="Avg Cyclomatic Complexity" score={p.avg_cyclomatic} max={20} color="#a78bfa" />
          </div>
          <FieldRow icon={BarChart3} label="Complexity Level" value={p.complexity_level}  badge />
          <FieldRow icon={BarChart3} label="Volume"           value={p.complexity_volume} />
        </ProfileCard>

        {/* ── Distributed Design Detail ── */}
        <ProfileCard title="Distributed Design" accent={isDistributed ? 'purple' : 'blue'}>
          <div className={`rounded-xl p-4 text-center ${
            isDistributed
              ? 'bg-purple-500/10 border border-purple-500/25'
              : 'bg-slate-800/40 border border-slate-700/40'
          }`}>
            <div className={`text-2xl font-black mb-1 ${isDistributed ? 'text-purple-300' : 'text-slate-400'}`}>
              {isDistributed ? 'YES' : 'NO'}
            </div>
            <p className={`text-xs ${isDistributed ? 'text-purple-400' : 'text-slate-500'}`}>
              {isDistributed ? 'Distributed Architecture Detected' : 'Centralized Architecture'}
            </p>
          </div>
          <p className="text-[11px] text-slate-400 mt-3 leading-relaxed">
            {p.distributed_architecture}
          </p>
        </ProfileCard>

      </div>

      {/* ── Full field table ── */}
      <div className="rounded-2xl border border-slate-700/40 bg-slate-900/40 overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-700/40">
          <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">
            Complete Rationalization Scorecard
          </h3>
        </div>
        <div className="divide-y divide-slate-700/30">
          {[
            { label: 'APP ID',                               value: p.app_id },
            { label: 'APP NAME',                             value: p.app_name },
            { label: 'SERVER NAME',                          value: p.server_name },
            { label: 'REPO NAME',                            value: p.repo_name },
            { label: 'Application Architecture',             value: p.application_architecture },
            { label: 'Source Code Availability',             value: p.source_code_availability, badge: true },
            { label: 'Programming Language',                 value: p.programming_language },
            { label: 'Component Coupling',                   value: p.component_coupling, badge: true },
            { label: 'Cloud Suitability',                    value: p.cloud_suitability, badge: true },
            { label: 'Volume of External Dependencies',      value: p.volume_external_dependencies, badge: true },
            { label: 'App Service / API Readiness',          value: p.api_readiness, badge: true },
            { label: 'Degree of Code Protocols',             value: p.code_protocol_degree, badge: true },
            { label: 'Code Design',                          value: p.code_design, badge: true },
            { label: 'Application-Code Complexity / Volume', value: p.complexity_volume, badge: true },
            { label: 'Distributed Architecture Design',      value: p.distributed_architecture },
          ].map(({ label, value, badge }) => (
            <div key={label} className="flex items-center justify-between gap-4 px-5 py-3 hover:bg-slate-800/30 transition-colors">
              <span className="text-xs text-slate-400 font-medium min-w-0 flex-1">{label}</span>
              {badge
                ? <Badge value={String(value || '—')} />
                : <span className="text-xs text-slate-200 text-right font-mono">{value || '—'}</span>
              }
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
