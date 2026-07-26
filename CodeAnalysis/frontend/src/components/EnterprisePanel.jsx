// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * EnterprisePanel.jsx
// Date: 2026-01-05
// ---------------------------------------------------------------------------
/**
 * EnterprisePanel.jsx
 * -------------------
 * Displays detected enterprise & legacy technologies:
 *   • IBM Mainframe  – COBOL, JCL, CICS, VSAM, DB2 embedded SQL, CSP, PANVALET, ISPF, z/OS
 *   • Classic Java EE – Struts, EJB, SOAP, WAS/WebSphere, Servlets, JSP
 *   • Legacy Web      – jQuery, Bootstrap (old versions)
 *
 * Data source: result.language_reports[] from the analysis pipeline.
 */
import { useMemo } from 'react'

// ── Colour helpers ────────────────────────────────────────────────────────────
const RISK_COLORS = {
  critical: 'border-red-500/60   bg-red-500/10   text-red-300',
  high:     'border-amber-500/60 bg-amber-500/10 text-amber-300',
  medium:   'border-yellow-500/40 bg-yellow-500/8 text-yellow-300',
  low:      'border-emerald-500/40 bg-emerald-500/8 text-emerald-300',
  none:     'border-slate-600/40 bg-slate-800/30 text-slate-400',
}

const BADGE_COLORS = {
  critical: 'bg-red-500/20 text-red-300 border-red-400/40',
  high:     'bg-amber-500/20 text-amber-300 border-amber-400/40',
  medium:   'bg-yellow-500/15 text-yellow-300 border-yellow-400/30',
  low:      'bg-emerald-500/15 text-emerald-300 border-emerald-400/30',
  none:     'bg-slate-700/40 text-slate-400 border-slate-500/30',
}

// ── Technology catalogue ──────────────────────────────────────────────────────
const TECH_CATALOGUE = [
  // IBM Mainframe
  { id: 'cobol',     label: 'Enterprise COBOL', category: 'Mainframe',  risk: 'critical', langKey: 'COBOL'    },
  { id: 'jcl',       label: 'JCL',              category: 'Mainframe',  risk: 'critical', langKey: 'JCL'      },
  { id: 'cics',      label: 'CICS',             category: 'Mainframe',  risk: 'critical', langKey: 'COBOL',   depKey: 'CICS' },
  { id: 'vsam',      label: 'VSAM',             category: 'Mainframe',  risk: 'critical', langKey: 'COBOL',   depKey: 'VSAM' },
  { id: 'db2_emb',   label: 'DB2 Embedded SQL', category: 'Mainframe',  risk: 'high',     langKey: 'DB2'      },
  { id: 'db2_sql',   label: 'DB2/UDB SQL',      category: 'Mainframe',  risk: 'high',     langKey: 'DB2'      },
  { id: 'csp',       label: 'CSP',              category: 'Mainframe',  risk: 'critical', langKey: 'CSP'      },
  { id: 'panvalet',  label: 'PANVALET',         category: 'Mainframe',  risk: 'high',     langKey: 'PANVALET' },
  { id: 'ispf',      label: 'ISPF',             category: 'Mainframe',  risk: 'medium',   langKey: 'REXX',    depKey: 'ISPF' },
  { id: 'rexx',      label: 'REXX',             category: 'Mainframe',  risk: 'medium',   langKey: 'REXX'     },
  { id: 'zos',       label: 'z/OS',             category: 'Mainframe',  risk: 'medium',   langKey: 'COBOL',   depKey: 'Z/OS USS' },
  // Classic Java EE
  { id: 'struts',    label: 'Struts 1/2',       category: 'Java EE',    risk: 'critical', langKey: 'Java',    depKey: 'Struts' },
  { id: 'ejb',       label: 'EJB',              category: 'Java EE',    risk: 'high',     langKey: 'Java',    depKey: 'EJB' },
  { id: 'soap',      label: 'SOAP Web Services', category: 'Java EE',   risk: 'high',     langKey: 'Java',    depKey: 'SOAP' },
  { id: 'was',       label: 'IBM WAS',          category: 'Java EE',    risk: 'high',     langKey: 'WAS'      },
  { id: 'servlets',  label: 'Servlets',         category: 'Java EE',    risk: 'medium',   langKey: 'Java',    depKey: 'Servlets' },
  { id: 'jsp',       label: 'JSP (Scriptlets)', category: 'Java EE',    risk: 'medium',   langKey: 'JSP'      },
  { id: 'spring',    label: 'Spring MVC',       category: 'Java EE',    risk: 'low',      langKey: 'Java',    depKey: 'Spring MVC' },
  { id: 'rest',      label: 'REST API (JAX-RS)', category: 'Java EE',   risk: 'low',      langKey: 'Java',    depKey: 'REST (JAX-RS)' },
  // Legacy Web
  { id: 'jquery',    label: 'jQuery',           category: 'Legacy Web', risk: 'medium',   langKey: 'JavaScript', depKey: 'jQuery' },
  { id: 'bootstrap', label: 'Bootstrap',        category: 'Legacy Web', risk: 'low',      langKey: 'JavaScript', depKey: 'Bootstrap' },
]

const CATEGORIES = ['Mainframe', 'Java EE', 'Legacy Web']

// ── Component ─────────────────────────────────────────────────────────────────
// Function: EnterprisePanel
export default function EnterprisePanel({ result }) {
  const langReports = result?.language_reports ?? []

  // Build a lookup: langKey → LanguageReport
  const reportByLang = useMemo(() => {
    const m = {}
    for (const r of langReports) {
      m[r.language] = r
    }
    return m
  }, [langReports])

  // For each tech in catalogue, compute detected + metrics
  const techData = useMemo(() => {
    return TECH_CATALOGUE.map((tech) => {
      const report = reportByLang[tech.langKey]
      const depPresent = tech.depKey
        ? langReports.some((r) => (r.dependencies ?? []).some((d) => d.includes(tech.depKey)))
        : false

      const detected = !!(report || depPresent)
      const fileCount = report?.file_count ?? 0
      const sloc = report?.total_sloc ?? 0
      const avgCC = report?.avg_complexity ?? 0
      const badPractices = report?.bad_practices ?? []

      // Filter bad practices relevant to this tech
      const relevantBad = badPractices.filter((bp) => {
        if (!tech.depKey) return false
        const low = bp.toLowerCase()
        return low.includes(tech.depKey.toLowerCase()) ||
               low.includes(tech.id) ||
               low.includes(tech.label.toLowerCase())
      })

      return { ...tech, detected, fileCount, sloc, avgCC, badPractices: relevantBad }
    })
  }, [langReports, reportByLang])

  const detected = techData.filter((t) => t.detected)
  const criticalCount = detected.filter((t) => t.risk === 'critical').length
  const highCount     = detected.filter((t) => t.risk === 'high').length

  return (
    <div className="space-y-6">
      {/* Summary row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <SummaryPill label="Technologies Detected" value={detected.length} color="text-cyan-300" />
        <SummaryPill label="Critical Legacy"       value={criticalCount}   color="text-red-300"  />
        <SummaryPill label="High Risk"             value={highCount}       color="text-amber-300" />
        <SummaryPill label="Languages Scanned"     value={langReports.length} color="text-blue-300" />
      </div>

      {/* Per-category grids */}
      {CATEGORIES.map((cat) => {
        const items = techData.filter((t) => t.category === cat)
        const detectedItems = items.filter((t) => t.detected)
        if (detectedItems.length === 0 && items.every((t) => !t.detected)) {
          return (
            <section key={cat}>
              <h2 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-widest">{cat}</h2>
              <p className="text-xs text-slate-500 italic">No {cat} technologies detected in this codebase.</p>
            </section>
          )
        }
        return (
          <section key={cat}>
            <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-widest">{cat}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {items.map((tech) => (
                <TechCard key={tech.id} tech={tech} />
              ))}
            </div>
          </section>
        )
      })}

      {/* Full bad practices list from all reports */}
      <AllBadPractices langReports={langReports} />
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────
// Function: SummaryPill
function SummaryPill({ label, value, color }) {
  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-800/40 p-3 text-center">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-[11px] text-slate-400 mt-0.5">{label}</p>
    </div>
  )
}

// Function: TechCard
function TechCard({ tech }) {
  const colorClass = RISK_COLORS[tech.detected ? tech.risk : 'none']
  const badgeClass = BADGE_COLORS[tech.detected ? tech.risk : 'none']

  return (
    <div className={`rounded-xl border p-3 space-y-2 ${colorClass}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-semibold truncate">{tech.label}</span>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeClass}`}>
          {tech.detected ? tech.risk.toUpperCase() : 'NOT DETECTED'}
        </span>
      </div>

      {tech.detected && (
        <div className="text-[11px] space-y-0.5 text-current opacity-80">
          {tech.fileCount > 0 && <p>Files: <strong>{tech.fileCount}</strong></p>}
          {tech.sloc > 0     && <p>SLOC: <strong>{tech.sloc.toLocaleString()}</strong></p>}
          {tech.avgCC > 0    && <p>Avg CC: <strong>{tech.avgCC.toFixed(1)}</strong></p>}
        </div>
      )}

      {tech.badPractices.length > 0 && (
        <ul className="text-[10px] space-y-0.5 opacity-75">
          {tech.badPractices.slice(0, 3).map((bp, i) => (
            <li key={i} className="truncate">⚠ {bp}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

// Function: AllBadPractices
function AllBadPractices({ langReports }) {
  const allBad = useMemo(() => {
    const out = []
    for (const r of langReports) {
      for (const bp of (r.bad_practices ?? [])) {
        out.push({ lang: r.language, text: bp })
      }
    }
    return out
  }, [langReports])

  if (allBad.length === 0) return null

  return (
    <section>
      <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-widest">
        All Bad Practices ({allBad.length})
      </h2>
      <div className="rounded-xl border border-slate-700/40 bg-slate-900/30 divide-y divide-slate-700/30 max-h-80 overflow-y-auto">
        {allBad.map((item, i) => (
          <div key={i} className="flex items-start gap-3 px-3 py-2 text-xs">
            <span className="shrink-0 font-mono text-[10px] text-slate-500 mt-0.5 w-20 truncate">{item.lang}</span>
            <span className="text-slate-300">{item.text}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
