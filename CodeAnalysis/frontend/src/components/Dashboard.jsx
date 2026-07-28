// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis â€” frontend/src/components (Dashboard.jsx)
// Date: 2026-04-04
// ---------------------------------------------------------------------------
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  ArrowLeft, Download, ExternalLink, GitBranch, FileCode, Layers,
  Shield, RefreshCw, Leaf, Brain, Sparkles, Lock
} from 'lucide-react'
import HealthCard              from './HealthCard.jsx'
import DebtCard                from './DebtCard.jsx'
import CloudCard               from './CloudCard.jsx'
import OSSCard                 from './OSSCard.jsx'
import ImpactCard              from './ImpactCard.jsx'
import Co2Card                 from './Co2Card.jsx'
import ChartsSection           from './ChartsSection.jsx'
import LanguageTable           from './LanguageTable.jsx'
import BadPracticesPanel       from './BadPracticesPanel.jsx'
import PortfolioTable          from './PortfolioTable.jsx'
import PortfolioScatter        from './PortfolioScatter.jsx'
import SecurityVulnsPanel      from './SecurityVulnsPanel.jsx'
import CloudReadyPanel         from './CloudReadyPanel.jsx'
import TechMixPanel            from './TechMixPanel.jsx'
import GreenImpactPanel        from './GreenImpactPanel.jsx'
import ArchitectureLayerPanel  from './ArchitectureLayerPanel.jsx'
import HealthPerTechPanel      from './HealthPerTechPanel.jsx'
import CloudRecommendationsPanel from './CloudRecommendationsPanel.jsx'
import TechDebtDetailPanel     from './TechDebtDetailPanel.jsx'
import OllamaSetupPanel        from './OllamaSetupPanel.jsx'
import AIInsightsPanel         from './AIInsightsPanel.jsx'
import KnowledgeGraphPanel     from './KnowledgeGraphPanel.jsx'
import EnterprisePanel         from './EnterprisePanel.jsx'
import MLPredictionsPanel      from './MLPredictionsPanel.jsx'
import OverviewPanel           from './OverviewPanel.jsx'
import AppProfilePanel         from './AppProfilePanel.jsx'
import OverallHealthExecutivePanel from './OverallHealthExecutivePanel.jsx'
import StratAqorynthModulePanel          from './StratAqorynthModulePanel.jsx'
import { riskColor, fmtNumber, getLLMTabAssessment } from '../utils.js'

const AI_TAB_LABELS = {
  overview: 'Overview',
  security: 'Security',
  cloud: 'CloudReady',
  cloud_services: 'Cloud Services',
  co2: 'CO2 & Tech Mix',
  green: 'Green Impact',
  health_tech: 'Health by Tech',
  debt_detail: 'Debt Advisor',
  architecture: 'Architecture',
  languages: 'Languages',
  practices: 'Bad Practices',
  knowledge_graph: 'Knowledge Graph',
  legacy_tech: 'Enterprise & Legacy',
  ml_predictions: 'ML Predictions',
}

const PRIORITY_STYLES = {
  high: 'bg-red-500/15 text-red-300 border-red-500/40',
  medium: 'bg-amber-500/15 text-amber-300 border-amber-500/40',
  low: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40',
}

const GARBLED_REPLACEMENTS = [
  [/â€¢/g, '-'],
  [/â€”|â€“/g, '-'],
  [/â€¦/g, '...'],
  [/Â·/g, '-'],
  [/Ã—/g, 'x'],
  [/â‚‚/g, '2'],
]

// Function: cleanText
function cleanText(value) {
  if (value == null) return ''
  let text = String(value)
  for (const [pattern, replacement] of GARBLED_REPLACEMENTS) {
    text = text.replace(pattern, replacement)
  }
  return text
}

const AI_TAB_UNLOCK_HINTS = {
  overview: [
    'AI-enriched summary across all quality dimensions',
    'ML-ranked risk highlights and hotspot detection',
    'Model-generated key findings and recommendations overview',
  ],
  security: [
    'AI-identified security blockers and high-severity CVE hotspots',
    'ML-ranked vulnerability severities with automated fix suggestions',
    'LLM-assessed dependency risk scoring across the entire codebase',
  ],
  cloud: [
    'ML-predicted cloud readiness blockers and step-by-step remediation',
    'AI-generated migration phases with sequenced action plans',
    'Model-assessed lift-and-shift vs refactor trade-off analysis',
  ],
  cloud_services: [
    'LLM-recommended cloud service mappings per detected technology',
    'AI-generated migration sequence across cloud adoption phases',
    'Model-prioritized cloud modernisation and integration roadmap',
  ],
  co2: [
    'AI-estimated CO\u2082 reduction from each modernisation transformation path',
    'ML-assessed energy efficiency improvements from cloud migration',
    'Model-driven technology sustainability and green score recommendations',
  ],
  green: [
    'AI-identified green code improvement opportunities by category',
    'ML-ranked algorithmic and resource efficiency enhancements',
    'LLM-recommended sustainability refactorings with impact estimates',
  ],
  health_tech: [
    'ML-assessed health risks segmented by technology stack',
    'AI-identified high-debt hotspot files and components per language',
    'Model-generated technology-specific remediation action plans',
  ],
  debt_detail: [
    'AI-ranked tech debt hotspots by business impact and severity',
    'ML-generated quick wins with time-to-fix estimations',
    'LLM-planned strategic refactoring roadmap with phased execution',
  ],
  architecture: [
    'ML-identified candidate microservices extracted from monolith structure',
    'AI-assessed architecture layer health, coupling risks, and patterns',
    'Model-recommended strangler fig decomposition strategy and sequence',
  ],
  languages: [
    'AI-ranked language-specific technical debt and obsolescence risk',
    'ML-identified migration complexity and effort per technology',
    'Model-recommended modernisation paths per language ecosystem',
  ],
  practices: [
    'LLM-classified bad practices by severity and downstream impact',
    'AI-generated fix priorities with code quality improvement plans',
    'ML-identified anti-pattern clusters and systemic root causes',
  ],
  knowledge_graph: [
    'AI-mapped service dependencies, coupling hotspots, and call chains',
    'ML-identified tightly-coupled components as microservice candidates',
    'Model-generated refactoring sequence for safe service extraction',
  ],
  legacy_tech: [
    'AI-detected enterprise & mainframe technologies (COBOL, CICS, VSAM, JCL, DB2, Struts, EJB, WAS)',
    'LLM-generated modernization roadmap with technology replacement recommendations',
    'ML-assessed migration complexity, effort estimates, and strangler-fig candidates',
  ],
  ml_predictions: [
    'ML-predicted defect probability per file using cyclomatic complexity and code metrics',
    'COCOMO II-inspired effort estimation for quick-wins, medium and complex files',
    'Technology fingerprinting, migration complexity scoring, and statistical anomaly detection',
  ],
}

// Function: TabLLMAssessmentBanner
function TabLLMAssessmentBanner({ tabKey, aiReport, onOpenAI }) {
  const assessment = getLLMTabAssessment(aiReport, tabKey)

  if (!assessment) {
    return (
      <div className="rounded-2xl border border-amber-300 bg-amber-50 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
          <div className="flex items-start gap-2 flex-1 min-w-0">
            <Brain size={16} className="text-amber-700 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-semibold text-amber-800">
                LLM inputs pending for {AI_TAB_LABELS[tabKey] || tabKey}
              </p>
              <p className="text-xs text-amber-700 mt-1">
                Run AI Analysis to drive this tab with model-based assessment and recommendations.
              </p>
            </div>
          </div>
          <button
            onClick={onOpenAI}
            className="text-xs font-semibold bg-amber-100 hover:bg-amber-200 text-amber-800 px-3 py-1.5 rounded-lg border border-amber-300 transition"
          >
            Open AI Analysis
          </button>
        </div>
      </div>
    )
  }

  const modelUsed = aiReport?.model_used || 'LLM'
  const drivers = (assessment.drivers || []).slice(0, 3)
  const actions = (assessment.recommended_actions || []).slice(0, 3)
  const priority = assessment.priority || 'medium'

  return (
    <div className="rounded-2xl border border-cyan-200 bg-gradient-to-r from-cyan-50 via-blue-50 to-emerald-50 p-4">
      <div className="flex flex-col md:flex-row md:items-start gap-3 md:gap-5">
        <div className="flex items-start gap-2 flex-1 min-w-0">
          <Sparkles size={16} className="text-cyan-700 mt-0.5 shrink-0" />
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-900 truncate">
              ML Assessment for {AI_TAB_LABELS[tabKey] || tabKey}
            </p>
            <p className="text-xs text-slate-700 mt-1">{cleanText(assessment.summary)}</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-[11px]">
          <span className={`px-2 py-1 rounded-full border ${PRIORITY_STYLES[priority] || PRIORITY_STYLES.medium}`}>
            {priority.toUpperCase()} PRIORITY
          </span>
          <span className="px-2 py-1 rounded-full border border-cyan-300 bg-cyan-100 text-cyan-800">
            Confidence {Math.round(assessment.confidence || 70)}%
          </span>
          <span className="px-2 py-1 rounded-full border border-slate-300 bg-slate-100 text-slate-700">
            Model {modelUsed}
          </span>
        </div>
      </div>

      {(drivers.length > 0 || actions.length > 0) && (
        <div className="mt-3 grid grid-cols-1 lg:grid-cols-2 gap-3 text-xs">
          {drivers.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white/80 p-3">
              <p className="font-semibold text-slate-900 mb-1">Signals</p>
              <ul className="space-y-1 text-slate-700">
                {drivers.map((item, idx) => (
                  <li key={`${tabKey}-signal-${idx}`}>- {cleanText(item)}</li>
                ))}
              </ul>
            </div>
          )}
          {actions.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white/80 p-3">
              <p className="font-semibold text-slate-900 mb-1">Recommended Actions</p>
              <ul className="space-y-1 text-slate-700">
                {actions.map((item, idx) => (
                  <li key={`${tabKey}-action-${idx}`}>- {cleanText(item)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// â”€â”€ ML Predictions List Helper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Function: MLItemList
function MLItemList({ title, items, color }) {
  if (!items?.length) return null
  const titleColors = {
    red: 'text-red-700', orange: 'text-orange-700', cyan: 'text-cyan-700',
    emerald: 'text-emerald-700', purple: 'text-purple-700', blue: 'text-blue-700',
  }
  return (
    <div>
      <p className={`text-[11px] font-semibold uppercase tracking-wide mb-2 ${titleColors[color] || 'text-cyan-700'}`}>
        {title}
      </p>
      <ul className="space-y-1">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-1.5 text-xs text-slate-800">
            <span className="text-slate-500 mt-0.5 shrink-0 text-[10px]">&#9658;</span>
            <span className="leading-snug">{cleanText(it).length > 110 ? cleanText(it).slice(0, 107) + '...' : cleanText(it)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

// â”€â”€ ML Predictions Card (per-tab AI sub-analysis display) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Function: strOfMlValue
function strOfMlValue(v) {
  if (typeof v === 'string') return v
  if (v == null) return ''
  // Use ?? so only null/undefined skips to next; then force to string to guard numbers/booleans
  const candidate = v?.action ?? v?.phase ?? v?.path ?? v?.risk ?? v?.description ??
                    v?.type ?? v?.name ?? v?.responsibility
  const s = candidate != null ? String(candidate) : String(JSON.stringify(v) ?? '')
  return cleanText(s).slice(0, 100)
}

// Function: SecurityBlockersCard
function SecurityBlockersCard({ tabKey, A, aiReport, strOf }) {
  if (!(tabKey === 'security' && A.cloud_blockers?.blockers?.length)) return null
  const items = A.cloud_blockers.blockers.slice(0, 5).map(
    b => cleanText(`[${b.severity || 'N/A'}] ${b.type || ''}: ${b.description || ''} - ${b.fix_suggestion || ''}`).slice(0, 110)
  )
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Brain size={13} className="text-red-700" />
        <span className="text-xs font-semibold text-red-800">ML-Identified Security Blockers</span>
        <span className="ml-auto text-[10px] text-slate-600">{aiReport.model_used || 'AI'}</span>
      </div>
      <MLItemList title="Security Blockers Detected" items={items} color="red" />
      {A.cloud_blockers.quick_wins?.length > 0 && (
        <div className="mt-3">
          <MLItemList title="Recommended Quick Fixes" items={A.cloud_blockers.quick_wins.slice(0, 3).map(strOf)} color="emerald" />
        </div>
      )}
    </div>
  )
}

// Function: CloudMigrationCard
function CloudMigrationCard({ tabKey, A, aiReport, strOf }) {
  if (!((tabKey === 'cloud' || tabKey === 'cloud_services') && A.cloud_blockers)) return null
  const phases = (A.cloud_blockers.migration_phases || []).slice(0, 4).map(strOf)
  const wins   = (A.cloud_blockers.quick_wins || []).slice(0, 4).map(strOf)
  if (!phases.length && !wins.length) return null
  return (
    <div className="rounded-2xl border border-cyan-200 bg-cyan-50 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Brain size={13} className="text-cyan-700" />
        <span className="text-xs font-semibold text-cyan-800">ML Cloud Migration Analysis</span>
        <span className="ml-auto text-[10px] text-slate-600">{aiReport.model_used || 'AI'}</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MLItemList title="Migration Phases" items={phases} color="cyan" />
        <MLItemList title="Quick Wins" items={wins} color="emerald" />
      </div>
    </div>
  )
}

// Function: SustainabilityCard
function SustainabilityCard({ tabKey, A, aiReport, strOf }) {
  if (!((tabKey === 'co2' || tabKey === 'green') && A.transformation)) return null
  const paths  = (A.transformation.transformation_paths || []).slice(0, 4).map(strOf)
  const phases = (A.transformation.modernisation_phases || []).slice(0, 4).map(strOf)
  if (!paths.length && !phases.length) return null
  return (
    <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Brain size={13} className="text-emerald-700" />
        <span className="text-xs font-semibold text-emerald-800">ML Transformation &amp; Sustainability Analysis</span>
        <span className="ml-auto text-[10px] text-slate-600">{aiReport.model_used || 'AI'}</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MLItemList title="Transformation Paths" items={paths} color="emerald" />
        <MLItemList title="Modernisation Phases" items={phases} color="cyan" />
      </div>
    </div>
  )
}

// Function: TechDebtCard
function TechDebtCard({ tabKey, A, aiReport, strOf }) {
  if (!(['health_tech', 'debt_detail', 'languages', 'practices'].includes(tabKey) && A.tech_debt)) return null
  const hotspots = (A.tech_debt.hotspots || []).slice(0, 4).map(h =>
    typeof h === 'string' ? cleanText(h)
      : cleanText(`${h.file || h.component || 'Component'} - ${h.risk_label || ''}, ~${h.estimated_hours ?? '?'}h`)
  )
  const wins    = (A.tech_debt.quick_wins || []).slice(0, 4).map(strOf)
  const actions = (A.tech_debt.strategic_actions || []).slice(0, 3).map(strOf)
  if (!hotspots.length && !wins.length) return null
  return (
    <div className="rounded-2xl border border-orange-200 bg-orange-50 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Brain size={13} className="text-orange-700" />
        <span className="text-xs font-semibold text-orange-800">ML Tech Debt Intelligence</span>
        <span className="ml-auto text-[10px] text-slate-600">{aiReport.model_used || 'AI'}</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MLItemList title="Debt Hotspots" items={hotspots} color="orange" />
        <MLItemList title="Quick Wins" items={wins} color="emerald" />
        <MLItemList title="Strategic Actions" items={actions} color="cyan" />
      </div>
    </div>
  )
}

// Function: ArchitectureCard
function ArchitectureCard({ tabKey, A, aiReport, strOf }) {
  if (!((tabKey === 'architecture' || tabKey === 'knowledge_graph') && A.microservices)) return null
  const svcs  = (A.microservices.microservices || []).slice(0, 4).map(s =>
    typeof s === 'string' ? s
      : `${s.name || 'Service'}: ${s.responsibility || s.description || ''}`.slice(0, 90)
  )
  const risks = (A.microservices.risks || []).slice(0, 4).map(strOf)
  if (!svcs.length && !risks.length) return null
  return (
    <div className="rounded-2xl border border-purple-200 bg-purple-50 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Brain size={13} className="text-purple-700" />
        <span className="text-xs font-semibold text-purple-800">ML Architecture &amp; Microservices Analysis</span>
        <span className="ml-auto text-[10px] text-slate-600">{aiReport.model_used || 'AI'}</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MLItemList title="Identified Microservices" items={svcs} color="purple" />
        <MLItemList title="Architecture Risks" items={risks} color="orange" />
      </div>
    </div>
  )
}

// Function: MLPredictionsCard
function MLPredictionsCard({ tabKey, aiReport }) {
  if (!aiReport?.analyses) return null
  const A = aiReport.analyses
  const strOf = strOfMlValue
  const ctx = { tabKey, A, aiReport, strOf }

  return (
    SecurityBlockersCard(ctx) ??
    CloudMigrationCard(ctx) ??
    SustainabilityCard(ctx) ??
    TechDebtCard(ctx) ??
    ArchitectureCard(ctx) ??
    null
  )
}

// â”€â”€ AI Tab Gate â€“ blocks tab content until AI Analysis is complete â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Function: AITabGate
function AITabGate({ tabKey, aiReport, onOpenAI, children }) {
  if (!aiReport) {
    const tabLabel = AI_TAB_LABELS[tabKey] || tabKey
    const hints    = AI_TAB_UNLOCK_HINTS[tabKey] || ['AI-powered predictions and analysis for this view']
    return (
      <div className="flex flex-col items-center justify-center min-h-[460px] py-16 px-6">
        <div className="flex flex-col items-center gap-5 max-w-lg w-full text-center">
          <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/30 flex items-center justify-center">
            <Lock size={32} className="text-amber-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-blue-300 mb-2">AI Analysis Required</h2>
            <p className="text-sm text-blue-400 leading-relaxed">
              The <span className="text-amber-300 font-semibold">{tabLabel}</span> tab is powered by
              machine learning models. Complete AI Analysis to unlock ML predictions, risk assessments,
              and intelligence-driven insights for this view.
            </p>
          </div>
          <button
            onClick={onOpenAI}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-400/40 text-cyan-200 font-semibold text-sm hover:from-cyan-500/30 hover:to-blue-500/30 transition-all"
          >
            <Brain size={14} />
            Run AI Analysis
            <Sparkles size={12} className="text-cyan-400" />
          </button>
          <div className="w-full rounded-2xl border border-slate-700/40 bg-slate-900/30 p-4 text-left">
            <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-3">
              What ML Analysis Provides for {tabLabel}
            </p>
            <ul className="space-y-2">
              {hints.map((hint, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-slate-400">
                  <Sparkles size={10} className="text-cyan-500/70 mt-0.5 shrink-0" />
                  {hint}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <TabLLMAssessmentBanner tabKey={tabKey} aiReport={aiReport} onOpenAI={onOpenAI} />
      <MLPredictionsCard tabKey={tabKey} aiReport={aiReport} />
      {children}
    </div>
  )
}

// Function: StatPill
function StatPill({ icon: Icon, label, value, color }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-surface-card border border-surface-border">
      <Icon size={13} className={color || 'text-blue-500'} />
      <span className="text-xs text-blue-500">{label}</span>
      <span className="text-xs font-semibold text-blue-300 ml-1">{value}</span>
    </div>
  )
}

// Function: Dashboard
export default function Dashboard({ result, portfolio, jobId, onBack }) {
  const [activeTab, setActiveTab] = useState(portfolio ? 'portfolio' : 'app_profile')
  const [bestModel, setBestModel] = useState(null)
  const [aiReport, setAiReport] = useState(null)

  const r = result
  const isPortfolio = !!portfolio

  const riskLabel = r?.risk_label ?? (portfolio ? 'Mixed' : 'Unknown')
  const rc = riskColor(riskLabel)

  useEffect(() => {
    if (!jobId) {
      setAiReport(null)
      return
    }
    const key = `ai_insights_${jobId}`
    try {
      const saved = localStorage.getItem(key)
      if (!saved) {
        setAiReport(null)
        return
      }
      const parsed = JSON.parse(saved)
      setAiReport(parsed?.status === 'done' ? (parsed.result || null) : null)
    } catch {
      setAiReport(null)
    }
  }, [jobId])

  // Function: handleExportJSON
  function handleExportJSON() {
    const data = isPortfolio ? portfolio : r
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `codeanalysis-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const singleTabs = [
    { key: 'app_profile',    label: 'App Profile'       },
    { key: 'ai_setup',       label: 'AI Setup'          },
    { key: 'ai_insights',    label: 'AI Analysis'       },
    { key: 'overview',       label: 'Overview'            },
    { key: 'quality_exec',   label: 'Overall Health / Quality Executive' },
    { key: 'security',       label: 'Security'            },
    { key: 'cloud',          label: 'CloudReady'          },
    { key: 'cloud_services', label: 'Cloud Services'      },
    { key: 'co2',            label: 'CO2 & Tech Mix'    },
    { key: 'green',          label: 'Green Impact'        },
    { key: 'health_tech',    label: 'Health by Tech'      },
    { key: 'debt_detail',    label: 'Debt Advisor'        },
    { key: 'architecture',   label: 'Architecture'        },
    { key: 'languages',      label: 'Languages'           },
    { key: 'practices',      label: 'Bad Practices'       },
    { key: 'knowledge_graph',   label: 'Knowledge Graph'   },
    { key: 'legacy_tech',       label: 'Enterprise & Legacy' },
    { key: 'ml_predictions',    label: 'ML Predictions'    },
    { key: 'aqorynth_modules',  label: 'Strat-Aqorynth Module Analysis' },
  ]
  const portfolioTabs = [
    { key: 'portfolio', label: 'Portfolio Map'   },
    { key: 'repos',     label: 'Repository List' },
    ...(r ? singleTabs : []),
  ]
  const tabs = isPortfolio ? portfolioTabs : singleTabs

  return (
    <div className="min-h-screen bg-gray-950 text-blue-300">
      {/* Navbar */}
      <nav className="sticky top-0 z-40 border-b border-surface-border bg-surface/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-3">
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-sm text-blue-400 hover:text-white transition-colors"
          >
            <ArrowLeft size={15} /> Back
          </button>

          <div className="h-4 w-px bg-surface-border" />

          <div className="flex items-center gap-2 flex-1 min-w-0">
            <GitBranch size={13} className="text-brand-cyan flex-shrink-0" />
            <span className="text-sm font-semibold text-blue-300 truncate">
              {isPortfolio ? 'Portfolio Analysis' : (r?.repo_name ?? 'Analysis Results')}
            </span>
            {r?.repo_url && (
              <a
                href={r.repo_url}
                target="_blank"
                rel="noreferrer"
                className="flex-shrink-0 text-blue-500 hover:text-brand-cyan transition-colors"
              >
                <ExternalLink size={12} />
              </a>
            )}
          </div>

          {!isPortfolio && r?.risk_label && (
            <span
              className="hidden sm:inline text-[11px] font-semibold px-2.5 py-1 rounded-full border"
              style={{ color: rc.text, background: rc.bg, borderColor: rc.border }}
            >
              {riskLabel} Risk
            </span>
          )}

          <button
            onClick={handleExportJSON}
            className="btn-secondary flex items-center gap-1.5 text-xs py-1.5 px-3"
          >
            <Download size={12} /> Export JSON
          </button>
        </div>
      </nav>

      {/* Stats bar */}
      {r && (
        <div className="border-b border-surface-border bg-surface/40">
          <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap gap-2">
            <StatPill icon={FileCode}  label="SLOC"         value={fmtNumber(r.sloc ?? r.total_sloc)} />
            <StatPill icon={Layers}    label="Files"        value={fmtNumber(r.file_count ?? r.total_files)} />
            <StatPill icon={GitBranch} label="Languages"    value={(r.languages ?? r.languages_detected ?? []).length} />
            {r.vulnerable_deps != null && (
              <StatPill icon={Shield} label="Vuln Deps"     value={r.vulnerable_deps}
                color={r.vulnerable_deps > 0 ? 'text-danger' : 'text-emerald-400'} />
            )}
            {r.co2?.co2_tons_year != null && (
              <StatPill icon={Leaf} label="CO2 Reduction"
                value={`${r.co2.co2_tons_year.toFixed(1)} t/yr`}
                color="text-emerald-400" />
            )}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-surface-border bg-surface/20 overflow-x-auto scrollbar-thin">
        <div className="max-w-7xl mx-auto px-4 flex gap-1 pt-2 min-w-max">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`tab-btn ${activeTab === t.key ? 'active' : ''}`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">

        {/* â”€â”€ Portfolio Map tab â”€â”€ */}
        {activeTab === 'portfolio' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <PortfolioScatter portfolio={portfolio} />
          </motion.div>
        )}

        {/* â”€â”€ Repository List tab â”€â”€ */}
        {activeTab === 'repos' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <PortfolioTable portfolio={portfolio} />
          </motion.div>
        )}

        {/* â”€â”€ App Profile tab (always visible â€” no AI required) â”€â”€ */}
        {activeTab === 'app_profile' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AppProfilePanel result={r} />
          </motion.div>
        )}

        {/* â”€â”€ Overview tab â”€â”€ */}
        {activeTab === 'overview' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="overview" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <OverviewPanel result={r} onTabChange={setActiveTab} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ Overall Health / Quality Executive tab â”€â”€ */}
        {activeTab === 'quality_exec' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <OverallHealthExecutivePanel result={r} />
          </motion.div>
        )}

        {/* No result fallback */}
        {activeTab === 'overview' && !r && (
          <div className="flex flex-col items-center justify-center py-24 text-blue-500 gap-3">
            <RefreshCw size={28} className="opacity-40" />
            <p className="text-sm">No single-repo data available.</p>
          </div>
        )}

        {/* â”€â”€ Security tab â”€â”€ */}
        {activeTab === 'security' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="security" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <SecurityVulnsPanel oss={r.oss} quality={r.quality_coverage} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ CloudReady tab â”€â”€ */}
        {activeTab === 'cloud' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="cloud" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <CloudReadyPanel cloud={r.cloud} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ COâ‚‚ & Tech Mix tab â”€â”€ */}
        {activeTab === 'co2' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="co2" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Co2Card data={r.co2} />
                <TechMixPanel language_reports={r.language_reports} />
              </div>
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ Languages tab â”€â”€ */}
        {activeTab === 'languages' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="languages" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <LanguageTable language_reports={r.language_reports} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ Bad Practices tab â”€â”€ */}
        {activeTab === 'practices' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="practices" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <BadPracticesPanel language_reports={r.language_reports} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ Green Impact tab â”€â”€ */}
        {activeTab === 'green' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="green" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <GreenImpactPanel green={r.green_impact} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ Health by Technology tab â”€â”€ */}
        {activeTab === 'health_tech' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="health_tech" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <HealthPerTechPanel healthPerLang={r.health_per_language} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ Architecture Layers tab â”€â”€ */}
        {activeTab === 'architecture' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="architecture" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <ArchitectureLayerPanel architecture={r.architecture} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ Cloud Service Recommendations tab â”€â”€ */}
        {activeTab === 'cloud_services' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="cloud_services" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <CloudRecommendationsPanel cloudRecs={r.cloud_recommendations} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ Debt Advisor tab â”€â”€ */}
        {activeTab === 'debt_detail' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="debt_detail" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <TechDebtDetailPanel result={r} portfolio={portfolio} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ AI Setup tab â”€â”€ */}
        {activeTab === 'ai_setup' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <OllamaSetupPanel onModelReady={(m) => setBestModel(m)} />
          </motion.div>
        )}

        {/* â”€â”€ AI Analysis tab â”€â”€ */}
        {activeTab === 'ai_insights' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <AIInsightsPanel jobId={jobId} scanJobId={jobId} bestModel={bestModel} onReportChange={setAiReport} />
          </motion.div>
        )}

        {/* â”€â”€ Knowledge Graph tab â”€â”€ */}
        {activeTab === 'knowledge_graph' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <KnowledgeGraphPanel jobId={jobId} />
          </motion.div>
        )}

        {/* â”€â”€ Enterprise & Legacy Tech tab â”€â”€ */}
        {activeTab === 'legacy_tech' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <AITabGate tabKey="legacy_tech" aiReport={aiReport} onOpenAI={() => setActiveTab('ai_insights')}>
              <EnterprisePanel result={r} />
            </AITabGate>
          </motion.div>
        )}

        {/* â”€â”€ ML Predictions tab â”€â”€ */}
        {activeTab === 'ml_predictions' && r && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <MLPredictionsPanel result={r} />
          </motion.div>
        )}

        {/* â”€â”€ Strat-Aqorynth Module Analysis tab â”€â”€ */}
        {activeTab === 'aqorynth_modules' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <StratAqorynthModulePanel jobId={jobId} />
          </motion.div>
        )}
      </main>
    </div>
  )
}


