// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * NetworkIntelligencePage.jsx
// Date: 2025-08-21
// ---------------------------------------------------------------------------
/**
 * NetworkIntelligencePage.jsx
 *
 * Three-panel intelligence view for an infrastructure scan:
 *   - Tab 1: Visual network topology (SVG, pan/zoom)
 *   - Tab 2: Virtual locations map (clustered by cloud provider / region)
 *   - Panel: Failure predictions, root causes, preventive measures
 *
 * Backend:
 *   GET  /api/intelligence/status              → model info
 *   GET  /api/intelligence/analyze/:scanId     → cached analysis
 *   POST /api/intelligence/analyze/:scanId     → run (or re-run) analysis
 */
import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Brain, AlertTriangle, ShieldCheck, Zap, Activity, Server,
  Network, MapPin, RefreshCw, ChevronDown, ChevronUp,
  TrendingUp, Cpu, HardDrive, Wifi, WifiOff, ArrowLeft,
} from 'lucide-react'
import toast from 'react-hot-toast'
import {
  getScan, getScanReport,
  getIntelligenceStatus, runIntelligenceAnalysis, getIntelligenceAnalysis,
} from '../api/client.js'
import AppHeader from '../components/AppHeader.jsx'
import NetworkTopologyGraph from '../components/NetworkTopologyGraph.jsx'

// ─── Colour maps ──────────────────────────────────────────────────────────────
const RISK_COLOR = {
  Critical: 'text-red-400 border-red-700/40 bg-red-950/30',
  High:     'text-orange-400 border-orange-700/40 bg-orange-950/30',
  Medium:   'text-amber-400 border-amber-700/40 bg-amber-950/30',
  Low:      'text-emerald-400 border-emerald-700/40 bg-emerald-950/30',
}
const PROB_COLOR = {
  critical: 'bg-red-500',
  high:     'bg-orange-500',
  medium:   'bg-amber-500',
  low:      'bg-emerald-500',
}
const PROB_TEXT = {
  critical: 'text-red-400',
  high:     'text-orange-400',
  medium:   'text-amber-400',
  low:      'text-emerald-400',
}
const PRIORITY_COLOR = {
  P1_critical: 'text-red-400',
  P2_high:     'text-orange-400',
  P3_medium:   'text-amber-400',
  P4_low:      'text-emerald-400',
}
const PRIORITY_BADGE = {
  P1_critical: 'bg-red-950/50 border-red-700/40 text-red-300',
  P2_high:     'bg-orange-950/50 border-orange-700/40 text-orange-300',
  P3_medium:   'bg-amber-950/50 border-amber-700/40 text-amber-300',
  P4_low:      'bg-emerald-950/50 border-emerald-700/40 text-emerald-300',
}
const EFFORT_BADGE = {
  high:   'bg-red-950/40 text-red-300',
  medium: 'bg-amber-950/40 text-amber-300',
  low:    'bg-emerald-950/40 text-emerald-300',
}
const RC_CATEGORY_COLOR = {
  eos_os:                  'text-red-400',
  eos_software:            'text-orange-400',
  single_point_of_failure: 'text-yellow-400',
  capacity_exhaustion:     'text-amber-400',
  security_gap:            'text-rose-400',
  missing_redundancy:      'text-orange-300',
  network_segmentation:    'text-blue-400',
  config_drift:            'text-purple-400',
}
const CLOUD_COLORS = {
  'AWS':     'border-orange-700/40 bg-orange-950/20',
  'Azure':   'border-blue-700/40 bg-blue-950/20',
  'GCP':     'border-green-700/40 bg-green-950/20',
  'OnPrem':  'border-slate-600/40 bg-slate-800/40',
  'Unknown': 'border-slate-700/40 bg-slate-900/30',
}

// ─── Risk Score Gauge ─────────────────────────────────────────────────────────
// Function: RiskGauge
function RiskGauge({ score, level }) {
  const SIZE = 120
  const R    = 44
  const cx   = SIZE / 2
  const cy   = SIZE / 2
  const circ = 2 * Math.PI * R
  // Only top-half arc (π radians)
  const arcLen = Math.PI * R
  const offset = arcLen - (score / 100) * arcLen

  const scoreColor = score >= 75 ? '#ef4444' : score >= 50 ? '#f97316' : score >= 25 ? '#f59e0b' : '#22c55e'

  return (
    <div className="flex flex-col items-center">
      <svg width={SIZE} height={SIZE * 0.68} viewBox={`0 0 ${SIZE} ${SIZE}`} overflow="visible">
        {/* Background half-arc */}
        <path
          d={`M ${cx - R}, ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none" stroke="#2a2d3e" strokeWidth={10} strokeLinecap="round"
        />
        {/* Scored arc */}
        <path
          d={`M ${cx - R}, ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none" stroke={scoreColor} strokeWidth={10} strokeLinecap="round"
          strokeDasharray={`${(score / 100) * arcLen} ${arcLen}`}
        />
        {/* Score text */}
        <text x={cx} y={cy - 4} textAnchor="middle" fontSize={26}
              fontWeight="bold" fill={scoreColor} fontFamily="monospace">{score}</text>
        <text x={cx} y={cy + 16} textAnchor="middle" fontSize={10} fill="#64748b">/ 100</text>
      </svg>
      <span className={`text-sm font-semibold ${scoreColor === '#ef4444' ? 'text-red-400'
                         : scoreColor === '#f97316' ? 'text-orange-400'
                         : scoreColor === '#f59e0b' ? 'text-amber-400' : 'text-emerald-400'}`}>
        {level} Risk
      </span>
    </div>
  )
}

// ─── Failure card ─────────────────────────────────────────────────────────────
// Function: FailureCard
function FailureCard({ failure }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="rounded-xl border border-surface-border bg-surface-card p-3 text-xs space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className={`w-2 h-2 rounded-full shrink-0 ${PROB_COLOR[failure.probability] || 'bg-slate-500'}`} />
          <span className="text-white font-medium font-mono truncate">{failure.component}</span>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className={`text-xs font-semibold capitalize ${PROB_TEXT[failure.probability]}`}>
            {failure.probability}
          </span>
          <button onClick={() => setExpanded(e => !e)}
                  className="text-slate-500 hover:text-white ml-1">
            {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <span className="px-1.5 py-0.5 rounded bg-surface text-slate-400 capitalize">
          {failure.component_type}
        </span>
        <span className="px-1.5 py-0.5 rounded bg-surface text-slate-400">
          {failure.failure_type?.replace(/_/g, ' ')}
        </span>
        <span className="px-1.5 py-0.5 rounded bg-surface text-slate-400">
          {failure.timeframe?.replace(/_/g, ' ')}
        </span>
        <span className={`px-1.5 py-0.5 rounded capitalize ${
          failure.blast_radius === 'critical' ? 'bg-red-950/50 text-red-300' :
          failure.blast_radius === 'major'    ? 'bg-orange-950/50 text-orange-300' :
          failure.blast_radius === 'moderate' ? 'bg-amber-950/50 text-amber-300' :
                                                'bg-slate-800 text-slate-300'}`}>
          blast: {failure.blast_radius}
        </span>
      </div>

      <p className="text-slate-400 leading-relaxed">{failure.description}</p>

      {expanded && (
        <>
          {failure.impact_chain?.length > 0 && (
            <div>
              <p className="text-slate-500 mb-1">Impact chain:</p>
              <div className="flex flex-wrap gap-1">
                {failure.impact_chain.map((c, i) => (
                  <span key={i} className="px-1.5 py-0.5 rounded bg-surface text-slate-300 font-mono">{c}</span>
                ))}
              </div>
            </div>
          )}
          {failure.affected_services?.length > 0 && (
            <div>
              <p className="text-slate-500 mb-1">Affected services:</p>
              <div className="flex flex-wrap gap-1">
                {failure.affected_services.map((s, i) => (
                  <span key={i} className="px-1.5 py-0.5 rounded bg-emerald-950/40 text-emerald-300">{s}</span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── Root cause card ──────────────────────────────────────────────────────────
// Function: RootCauseCard
function RootCauseCard({ rc }) {
  const catColor = RC_CATEGORY_COLOR[rc.category] || 'text-slate-400'
  return (
    <div className="rounded-xl border border-surface-border bg-surface-card p-3 text-xs space-y-2">
      <div className="flex items-center gap-2">
        <span className={`font-semibold capitalize ${catColor}`}>
          {rc.category?.replace(/_/g, ' ')}
        </span>
        <span className="text-slate-600 font-mono text-[10px]">{rc.id}</span>
      </div>
      <p className="text-slate-300">{rc.description}</p>
      {rc.contributing_factors?.length > 0 && (
        <ul className="space-y-0.5 pl-3">
          {rc.contributing_factors.map((f, i) => (
            <li key={i} className="text-slate-500 list-disc list-inside">{f}</li>
          ))}
        </ul>
      )}
      {rc.linked_failures?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {rc.linked_failures.map((id, i) => (
            <span key={i} className="px-1.5 py-0.5 rounded bg-surface font-mono text-slate-400">{id}</span>
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Preventive measure card ──────────────────────────────────────────────────
// Function: MeasureCard
function MeasureCard({ measure }) {
  return (
    <div className="rounded-xl border border-surface-border bg-surface-card p-3 text-xs space-y-2">
      <div className="flex items-start justify-between gap-2">
        <span className={`font-mono font-semibold shrink-0 ${PRIORITY_COLOR[measure.priority] || 'text-slate-400'}`}>
          {measure.priority?.replace('_', ' ')}
        </span>
        <div className="flex gap-1.5">
          <span className={`px-1.5 py-0.5 rounded text-[10px] capitalize ${EFFORT_BADGE[measure.effort] || 'bg-surface text-slate-400'}`}>
            effort: {measure.effort}
          </span>
          {measure.deadline_days && (
            <span className="px-1.5 py-0.5 rounded bg-surface text-slate-400 text-[10px]">
              ≤ {measure.deadline_days}d
            </span>
          )}
        </div>
      </div>
      <p className="text-white font-medium">{measure.action}</p>
      <p className="text-slate-500 italic">{measure.rationale}</p>
      {measure.linked_root_causes?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {measure.linked_root_causes.map((id, i) => (
            <span key={i} className="px-1.5 py-0.5 rounded bg-surface font-mono text-slate-400">{id}</span>
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Locations Map ────────────────────────────────────────────────────────────
// Function: LocationsMap
function LocationsMap({ servers, intelligenceData }) {
  const riskByServer = {}
  if (intelligenceData?.predicted_failures) {
    for (const f of intelligenceData.predicted_failures) {
      const comp = (f.component || '').split('/')[0]
      const cur  = riskByServer[comp]
      const pri  = { critical: 4, high: 3, medium: 2, low: 1 }
      if (!cur || (pri[f.probability] || 0) > (pri[cur.probability] || 0)) {
        riskByServer[comp] = f
      }
    }
  }

  // Group by cloud_provider then by region/subnet
  const grouped = {}
  for (const s of servers || []) {
    const cloud  = s.cloud_provider || 'OnPrem'
    const region = s.region || s.datacenter || (s.ip_address || s.ip || '').split('.').slice(0, 3).join('.') + '.0/24'
    if (!grouped[cloud]) grouped[cloud] = {}
    if (!grouped[cloud][region]) grouped[cloud][region] = []
    grouped[cloud][region].push(s)
  }

  if (!Object.keys(grouped).length) {
    return (
      <div className="flex items-center justify-center h-40 text-slate-600 text-sm">
        No server data available for location mapping.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([cloud, regions]) => (
        <div key={cloud} className={`rounded-2xl border p-4 ${CLOUD_COLORS[cloud] || CLOUD_COLORS.Unknown}`}>
          <div className="flex items-center gap-2 mb-4">
            <MapPin size={14} className="text-slate-400" />
            <h3 className="font-semibold text-white text-sm">{cloud}</h3>
            <span className="ml-auto text-xs text-slate-500">{Object.keys(regions).length} region(s)</span>
          </div>

          <div className="space-y-4">
            {Object.entries(regions).map(([region, srvs]) => (
              <div key={region}>
                <p className="text-xs text-slate-500 font-mono mb-2">📡 {region}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                  {srvs.map(s => {
                    const name  = s.server_name || s.name || s.ip_address || 'unknown'
                    const risk  = riskByServer[name]
                    const cpu   = s.cpu_util_pct ?? -1
                    const ram   = s.ram_util_pct ?? -1
                    return (
                      <div key={name}
                           className={`rounded-xl border p-3 bg-surface text-xs space-y-2 
                             ${risk?.probability === 'critical' ? 'border-red-700/50' :
                               risk?.probability === 'high'     ? 'border-orange-700/40' :
                               risk?.probability === 'medium'   ? 'border-amber-700/40' :
                                                                  'border-surface-border'}`}>
                        {/* Header */}
                        <div className="flex items-center justify-between gap-1">
                          <div className="flex items-center gap-1.5 min-w-0">
                            <Server size={11} className="text-slate-500 shrink-0" />
                            <span className="font-mono text-white truncate font-medium">{name}</span>
                          </div>
                          {risk && (
                            <span className={`shrink-0 w-2 h-2 rounded-full ${
                              risk.probability === 'critical' ? 'bg-red-500' :
                              risk.probability === 'high'     ? 'bg-orange-500' :
                              risk.probability === 'medium'   ? 'bg-amber-500' : 'bg-emerald-500'
                            }`} />
                          )}
                        </div>

                        {/* OS + IP */}
                        <div className="text-slate-500 space-y-0.5">
                          {s.ip_address && <div className="font-mono">{s.ip_address}</div>}
                          {(s.os_name || s.os) && <div className="truncate">{s.os_name || s.os}</div>}
                        </div>

                        {/* CPU bar */}
                        {cpu >= 0 && (
                          <div>
                            <div className="flex justify-between text-slate-500 mb-0.5">
                              <span>CPU</span><span>{cpu.toFixed(0)}%</span>
                            </div>
                            <div className="h-1.5 bg-surface-hover rounded-full overflow-hidden">
                              <div className={`h-full rounded-full transition-all ${
                                cpu >= 85 ? 'bg-red-500' : cpu >= 60 ? 'bg-amber-500' : 'bg-emerald-500'
                              }`} style={{ width: `${Math.min(100, cpu)}%` }} />
                            </div>
                          </div>
                        )}

                        {/* RAM bar */}
                        {ram >= 0 && (
                          <div>
                            <div className="flex justify-between text-slate-500 mb-0.5">
                              <span>RAM</span><span>{ram.toFixed(0)}%</span>
                            </div>
                            <div className="h-1.5 bg-surface-hover rounded-full overflow-hidden">
                              <div className={`h-full rounded-full transition-all ${
                                ram >= 85 ? 'bg-red-500' : ram >= 60 ? 'bg-amber-500' : 'bg-emerald-500'
                              }`} style={{ width: `${Math.min(100, ram)}%` }} />
                            </div>
                          </div>
                        )}

                        {/* Workloads */}
                        {s.workloads?.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {s.workloads.map((w, i) => (
                              <span key={i}
                                    className="px-1.5 py-0.5 rounded bg-emerald-950/40 text-emerald-300 text-[10px]">
                                {typeof w === 'string' ? w : w.name || ''}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Risk label */}
                        {risk && (
                          <div className={`text-[10px] rounded px-1.5 py-0.5 ${
                            risk.probability === 'critical' ? 'bg-red-950/50 text-red-300' :
                            risk.probability === 'high'     ? 'bg-orange-950/50 text-orange-300' :
                            risk.probability === 'medium'   ? 'bg-amber-950/50 text-amber-300' :
                                                              'bg-emerald-950/50 text-emerald-300'
                          }`}>
                            ⚠ {risk.failure_type?.replace(/_/g, ' ')}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

// ─── Topology Risks Summary ───────────────────────────────────────────────────
// Function: TopologyRisks
function TopologyRisks({ risks }) {
  if (!risks) return null
  const sections = [
    { label: 'Single Points of Failure', icon: <WifiOff size={13} className="text-red-400" />,
      items: risks.single_points_of_failure || [], color: 'text-red-300' },
    { label: 'Overloaded Servers',        icon: <Cpu size={13} className="text-orange-400" />,
      items: risks.overloaded_servers || [], color: 'text-orange-300' },
    { label: 'Missing HA/DR',             icon: <Activity size={13} className="text-amber-400" />,
      items: risks.missing_ha || [], color: 'text-amber-300' },
    { label: 'Unpatched Services',        icon: <ShieldCheck size={13} className="text-rose-400" />,
      items: risks.unpatched_services || [], color: 'text-rose-300' },
    { label: 'Isolated Segments',         icon: <Network size={13} className="text-blue-400" />,
      items: risks.isolated_segments || [], color: 'text-blue-300' },
  ].filter(s => s.items.length > 0)

  if (!sections.length) return null

  return (
    <div className="rounded-2xl border border-surface-border bg-surface-card p-4">
      <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
        <Zap size={14} className="text-amber-400" /> Topology Risk Summary
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {sections.map(s => (
          <div key={s.label} className="rounded-xl bg-surface border border-surface-border p-3">
            <div className="flex items-center gap-1.5 mb-2">{s.icon}
              <span className="text-xs text-slate-400">{s.label}</span>
              <span className="ml-auto text-xs font-mono text-slate-500">{s.items.length}</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {s.items.map((item, i) => (
                <span key={i} className={`px-1.5 py-0.5 rounded text-[10px] font-mono bg-surface-hover ${s.color}`}>
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────
// Function: NetworkIntelligencePage
export default function NetworkIntelligencePage() {
  const { scanId } = useParams()
  const navigate   = useNavigate()

  const [scan,      setScan]      = useState(null)
  const [report,    setReport]    = useState(null)
  const [modelInfo, setModelInfo] = useState(null)
  const [analysis,  setAnalysis]  = useState(null)
  const [loading,   setLoading]   = useState(false)
  const [analysing, setAnalysing] = useState(false)
  const [activeTab, setActiveTab] = useState('topology')

  // ── Load scan + cached analysis on mount ─────────────────────────────────
  useEffect(() => {
    if (!scanId) return
    setLoading(true)
    Promise.all([
      getScan(scanId).catch(() => null),
      getScanReport(scanId).catch(() => null),
      getIntelligenceStatus().catch(() => null),
      getIntelligenceAnalysis(scanId).catch(() => null),
    ]).then(([sc, rpt, model, cached]) => {
      setScan(sc)
      setReport(rpt)
      setModelInfo(model)
      if (cached) setAnalysis(cached)
    }).finally(() => setLoading(false))
  }, [scanId])

  // ── Run / re-run analysis ─────────────────────────────────────────────────
  const handleAnalyze = useCallback(async () => {
    setAnalysing(true)
    try {
      const result = await runIntelligenceAnalysis(scanId)
      setAnalysis(result)
      toast.success(`Analysis complete · Model: ${result.model_used || 'heuristic'}`)
    } catch (err) {
      toast.error('Analysis failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setAnalysing(false)
    }
  }, [scanId])

  const servers    = report?.servers || []
  const netTopo    = report?.network_topology || {}

  const criticalCount = analysis?.predicted_failures?.filter(f => f.probability === 'critical').length || 0
  const highCount     = analysis?.predicted_failures?.filter(f => f.probability === 'high').length || 0

  if (loading) {
    return (
      <div className="min-h-screen bg-surface text-white flex flex-col">
        <AppHeader />
        <div className="flex-1 flex items-center justify-center gap-3">
          <RefreshCw size={18} className="animate-spin text-brand-indigo" />
          <span className="text-slate-400">Loading intelligence view…</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface text-white flex flex-col">
      <AppHeader />

      <main className="flex-1 max-w-[1400px] mx-auto w-full px-4 sm:px-6 py-6 space-y-6">

        {/* Header row */}
        <div className="flex flex-wrap items-center gap-3">
          <button onClick={() => navigate(`/scans/${scanId}`)}
                  className="flex items-center gap-1.5 text-slate-400 hover:text-white text-sm
                             px-3 py-1.5 rounded-lg border border-transparent hover:border-surface-border
                             hover:bg-surface-hover transition-colors">
            <ArrowLeft size={14} /> Back to Scan
          </button>

          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Brain size={20} className="text-brand-indigo" /> Network Intelligence
          </h1>

          {scan?.scan_name && (
            <span className="text-slate-400 text-sm">— {scan.scan_name}</span>
          )}

          <div className="ml-auto flex items-center gap-3">
            {/* Model badge */}
            {modelInfo && (
              <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs
                              ${modelInfo.available
                                ? 'border-emerald-700/40 bg-emerald-950/30 text-emerald-300'
                                : 'border-slate-600/40 bg-slate-800/40 text-slate-400'}`}>
                <Cpu size={11} />
                {modelInfo.available ? (
                  <span>GPU · {modelInfo.model}</span>
                ) : (
                  <span>Rule-based analysis</span>
                )}
              </div>
            )}

            {/* Analyze button */}
            <button onClick={handleAnalyze} disabled={analysing}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-indigo/90 hover:bg-brand-indigo
                               text-white text-sm font-medium transition-colors disabled:opacity-60">
              {analysing ? <RefreshCw size={13} className="animate-spin" /> : <Brain size={13} />}
              {analysing ? 'Analysing…' : analysis ? 'Re-analyse' : 'Predict Failures'}
            </button>
          </div>
        </div>

        {/* Intelligence overview cards (shown once analysis exists) */}
        {analysis && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Risk gauge */}
            <div className="glass p-5 flex flex-col items-center justify-center">
              <RiskGauge score={analysis.risk_score ?? 0} level={analysis.risk_level ?? 'Unknown'} />
            </div>

            {/* Executive summary */}
            <div className="glass p-5 lg:col-span-3">
              <p className="text-xs text-slate-500 mb-1.5 uppercase tracking-wide font-medium">
                Executive Summary
              </p>
              <p className="text-sm text-slate-200 leading-relaxed">{analysis.executive_summary}</p>
              <div className="flex flex-wrap gap-2 mt-3">
                {criticalCount > 0 && (
                  <span className="px-2 py-1 rounded-lg bg-red-950/50 border border-red-700/40
                                   text-red-300 text-xs font-medium">
                    {criticalCount} Critical
                  </span>
                )}
                {highCount > 0 && (
                  <span className="px-2 py-1 rounded-lg bg-orange-950/50 border border-orange-700/40
                                   text-orange-300 text-xs font-medium">
                    {highCount} High
                  </span>
                )}
                <span className="px-2 py-1 rounded-lg bg-surface border border-surface-border
                                 text-slate-400 text-xs">
                  {analysis.predicted_failures?.length || 0} failure{' '}
                  {analysis.predicted_failures?.length !== 1 ? 'predictions' : 'prediction'}
                </span>
                <span className="px-2 py-1 rounded-lg bg-surface border border-surface-border
                                 text-slate-400 text-xs">
                  {analysis.preventive_measures?.length || 0} preventive measures
                </span>
                {analysis.model_used && (
                  <span className="px-2 py-1 rounded-lg bg-indigo-950/40 border border-indigo-700/30
                                   text-indigo-300 text-xs font-mono ml-auto">
                    {analysis.model_used}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Topology Risks */}
        {analysis?.topology_risks && <TopologyRisks risks={analysis.topology_risks} />}

        {/* Tab selector */}
        <div className="flex gap-1 bg-surface-card border border-surface-border rounded-xl p-1 w-fit">
          {[
            { id: 'topology',  label: 'Network Topology',   icon: <Network size={13} /> },
            { id: 'locations', label: 'Locations Map',       icon: <MapPin size={13} /> },
          ].map(tab => (
            <button key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm transition-colors
                               ${activeTab === tab.id
                                 ? 'bg-surface text-white font-medium'
                                 : 'text-slate-400 hover:text-white'}`}>
              {tab.icon}{tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="glass p-5">
          {activeTab === 'topology' && (
            <NetworkTopologyGraph
              networkTopology={netTopo}
              servers={servers}
              intelligenceData={analysis}
            />
          )}
          {activeTab === 'locations' && (
            <LocationsMap servers={servers} intelligenceData={analysis} />
          )}
        </div>

        {/* Predictions panel — 3 columns */}
        {analysis && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Predicted failures */}
            <div className="space-y-3">
              <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
                <AlertTriangle size={14} className="text-red-400" />
                Predicted Failures
                <span className="ml-auto text-xs text-slate-500 font-normal">
                  {analysis.predicted_failures?.length || 0}
                </span>
              </h2>
              {(!analysis.predicted_failures?.length) && (
                <p className="text-slate-500 text-sm">No failures predicted.</p>
              )}
              {[...( analysis.predicted_failures || [])].sort((a, b) => {
                const pri = { critical: 4, high: 3, medium: 2, low: 1 }
                return (pri[b.probability] || 0) - (pri[a.probability] || 0)
              }).map(f => <FailureCard key={f.id} failure={f} />)}
            </div>

            {/* Root causes */}
            <div className="space-y-3">
              <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
                <TrendingUp size={14} className="text-orange-400" />
                Root Causes
                <span className="ml-auto text-xs text-slate-500 font-normal">
                  {analysis.root_causes?.length || 0}
                </span>
              </h2>
              {(!analysis.root_causes?.length) && (
                <p className="text-slate-500 text-sm">No root causes identified.</p>
              )}
              {(analysis.root_causes || []).map(rc => <RootCauseCard key={rc.id} rc={rc} />)}
            </div>

            {/* Preventive measures */}
            <div className="space-y-3">
              <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
                <ShieldCheck size={14} className="text-emerald-400" />
                Preventive Measures
                <span className="ml-auto text-xs text-slate-500 font-normal">
                  {analysis.preventive_measures?.length || 0}
                </span>
              </h2>
              {(!analysis.preventive_measures?.length) && (
                <p className="text-slate-500 text-sm">No measures generated.</p>
              )}
              {[...(analysis.preventive_measures || [])].sort((a, b) => {
                const pri = { P1_critical: 4, P2_high: 3, P3_medium: 2, P4_low: 1 }
                return (pri[b.priority] || 0) - (pri[a.priority] || 0)
              }).map(m => <MeasureCard key={m.id} measure={m} />)}
            </div>
          </div>
        )}

        {/* Empty state */}
        {!analysis && !analysing && (
          <div className="glass p-12 flex flex-col items-center gap-4 text-center">
            <Brain size={48} className="text-slate-600" />
            <h3 className="text-lg font-semibold text-slate-300">No Analysis Yet</h3>
            <p className="text-slate-500 max-w-md text-sm">
              Click <strong className="text-white">Predict Failures</strong> to run
              {modelInfo?.available
                ? ` GPU-accelerated inference via ${modelInfo.model}`
                : ' rule-based failure prediction'}.
              The analysis covers EOS risks, capacity exhaustion, network single points of failure,
              missing HA/DR, and provides root causes with prioritised preventive actions.
            </p>
            <button onClick={handleAnalyze} disabled={analysing}
                    className="flex items-center gap-2 px-6 py-3 rounded-xl bg-brand-indigo/90
                               hover:bg-brand-indigo text-white font-medium transition-colors mt-2">
              <Brain size={16} /> Predict Failures
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
