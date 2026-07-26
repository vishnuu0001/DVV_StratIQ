// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (NovastraItsmHomePage.jsx)
// Date: 2026-02-25
// ---------------------------------------------------------------------------
import { useNavigate } from 'react-router-dom'
import {
  FileSpreadsheet, BrainCircuit, Network, Tag, Bot, BookOpen, TrendingUp, Zap,
  Search, Heart, Database, BarChart3, ShieldCheck, GitBranch, Lock,
  Sparkles, ArrowRight, Activity, Shield, FlaskConical, Cpu, Brain,
  AlertTriangle, Target, Layers, Eye, RefreshCw, ChevronRight, MonitorDot,
} from 'lucide-react'

const NEW_FEATURES = [
  {
    icon: GitBranch,
    title: 'Event Correlation Engine',
    description: 'Temporal correlation, event storm detection, causal chain analysis, and blast radius mapping across your entire event stream.',
    route: '/event-correlation',
    color: 'from-purple-600 to-violet-700',
    badge: 'NEW',
  },
  {
    icon: Lock,
    title: 'Security & Governance',
    description: 'PII masking with 9 entity types, tamper-proof audit logging, AI bias detection, and end-to-end data lineage tracking.',
    route: '/governance',
    color: 'from-emerald-600 to-teal-700',
    badge: 'NEW',
  },
  {
    icon: MonitorDot,
    title: 'ITSM Operations Dashboard',
    description: 'Real-time MTTA, MTTR, SLA compliance, FCR, reopen rate, backlog aging, change success rate — with scenario simulation and LLM executive summary.',
    route: '/itsm-dashboard',
    color: 'from-blue-600 to-indigo-700',
    badge: 'NEW',
  },
  {
    icon: Layers,
    title: 'Omnichannel Ticket Intake',
    description: '7 intake channels: Web Portal, Email, Chat, Phone, Mobile App, Monitoring Tools, API — with one-click simulation and AI triage routing.',
    route: '/omnichannel',
    color: 'from-violet-600 to-purple-700',
    badge: 'NEW',
  },
  {
    icon: Brain,
    title: 'ML Anomaly + Predictive Maintenance',
    description: 'Isolation Forest (scikit-learn) anomaly detection and asset failure probability scoring with MTTR prediction from live telemetry.',
    route: '/predictive',
    color: 'from-orange-600 to-amber-700',
    badge: 'NEW',
  },
]

const ALL_CAPABILITIES = [
  { icon: FileSpreadsheet, label: 'Ticket Analysis',      route: '/ticket-analysis',     desc: 'Bulk AI classification and insights' },
  { icon: BrainCircuit,    label: 'AI Assessment',        route: '/ai-assessment',       desc: 'Readiness and maturity scoring' },
  { icon: Network,         label: 'Knowledge Graph',      route: '/knowledge-graph',     desc: 'Semantic relationship mapping' },
  { icon: Tag,             label: 'Ticket Intelligence',  route: '/ticket-intelligence', desc: 'Auto-classify, duplicate detect, summarize' },
  { icon: Bot,             label: 'Virtual Agent',        route: '/virtual-agent',       desc: 'Multi-turn AI assistant' },
  { icon: BookOpen,        label: 'Knowledge Mgmt',       route: '/knowledge-mgmt',      desc: 'Smart KB article generation' },
  { icon: TrendingUp,      label: 'Predictive AIOps',    route: '/predictive',          desc: 'ML prediction + Isolation Forest + Maintenance' },
  { icon: Zap,             label: 'Automation',           route: '/automation',          desc: 'Playbook mapping and workflow builder' },
  { icon: Search,          label: 'Root Cause Analysis',  route: '/rca',                 desc: 'RCA generation and pattern clustering' },
  { icon: Heart,           label: 'Sentiment Analysis',   route: '/sentiment',           desc: 'Ticket sentiment and burnout risk' },
  { icon: Database,        label: 'CMDB Intelligence',    route: '/cmdb',                desc: 'NL queries and impact analysis' },
  { icon: BarChart3,       label: 'Reports & Insights',   route: '/reports',             desc: 'MTTA/MTTR/FCR/SLA KPI dashboard' },
  { icon: ShieldCheck,     label: 'Compliance',           route: '/compliance',          desc: 'ISO/ITIL/SOC2 gap assessment' },
  { icon: GitBranch,       label: 'Event Correlation',    route: '/event-correlation',   desc: 'Temporal clustering & blast radius', isNew: true },
  { icon: Lock,            label: 'Governance',           route: '/governance',          desc: 'PII masking, audit log, bias detection', isNew: true },
  { icon: MonitorDot,      label: 'ITSM Dashboard',       route: '/itsm-dashboard',      desc: 'Real-time ops KPIs + scenario simulator', isNew: true },
  { icon: Layers,          label: 'Omnichannel Intake',   route: '/omnichannel',         desc: '7-channel ticket intake + AI triage', isNew: true },
]

const STATS = [
  { value: '38', label: 'New API Routes', icon: Layers,       color: 'text-purple-400' },
  { value: '17', label: 'AI Capabilities',icon: Sparkles,     color: 'text-cyan-400'   },
  { value: '7',  label: 'New Features',   icon: Zap,          color: 'text-emerald-400'},
  { value: '11', label: 'Anti-Hallucination Layers', icon: Shield, color: 'text-orange-400' },
]

// Function: NovastraItsmHomePage
export default function NovastraItsmHomePage() {
  const navigate = useNavigate()

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 text-white">

      {/* Hero */}
      <div className="relative overflow-hidden bg-[linear-gradient(135deg,rgba(79,70,229,0.18),rgba(6,182,212,0.10),rgba(16,185,129,0.08))] border-b border-white/5 px-8 py-10">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_30%_0%,rgba(139,92,246,0.12),transparent_60%)]" />
        <div className="relative max-w-5xl">
          <div className="flex items-center gap-2 mb-3">
            <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              v2.0 · 7 NEW FEATURES ADDED
            </span>
          </div>
          <h1 className="text-3xl font-black text-white mb-2 leading-tight">
            STM-ITSM AI Platform
            <span className="ml-3 text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-cyan-400 to-emerald-400">
              · STM-ITSM
            </span>
          </h1>
          <p className="text-gray-400 text-sm leading-relaxed max-w-2xl">
            Enterprise AIOps and ITSM intelligence platform. 15 AI capabilities — from predictive maintenance and event correlation to governance and MLOps — all powered by local Ollama GPU inference with zero data leakage.
          </p>
        </div>

        {/* Stats bar */}
        <div className="relative grid grid-cols-4 gap-3 mt-8 max-w-3xl">
          {STATS.map(({ value, label, icon: Icon, color }) => (
            <div key={label} className="bg-white/5 border border-white/10 rounded-2xl px-4 py-3 flex items-center gap-3">
              <Icon size={18} className={color} />
              <div>
                <p className={`text-xl font-black ${color}`}>{value}</p>
                <p className="text-[10px] text-gray-500 leading-tight">{label}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="px-8 py-8 max-w-6xl mx-auto space-y-10">

        {/* What's New */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <div className="flex items-center gap-2">
              <span className="w-1 h-5 bg-gradient-to-b from-violet-500 to-cyan-500 rounded-full block" />
              <h2 className="text-base font-black text-white uppercase tracking-widest">What's New in v2.0</h2>
            </div>
            <span className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {NEW_FEATURES.map((f) => {
              const Icon = f.icon
              return (
                <button
                  key={f.route + f.title}
                  onClick={() => navigate(f.route)}
                  className="group relative text-left rounded-2xl border border-white/10 bg-white/[0.03] p-5 hover:border-white/20 hover:bg-white/[0.06] transition-all duration-200"
                >
                  <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-3 shadow-lg`}>
                    <Icon size={17} className="text-white" />
                  </div>
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <p className="text-sm font-bold text-white leading-tight">{f.title}</p>
                    <span className="shrink-0 text-[9px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {f.badge}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed">{f.description}</p>
                  <div className="flex items-center gap-1 mt-3 text-[10px] font-semibold text-gray-500 group-hover:text-white transition-colors">
                    Open feature <ChevronRight size={11} className="group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </button>
              )
            })}
          </div>
        </section>

        {/* All Capabilities */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <div className="flex items-center gap-2">
              <span className="w-1 h-5 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full block" />
              <h2 className="text-base font-black text-white uppercase tracking-widest">All AI Capabilities</h2>
            </div>
            <span className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
          </div>
          <div className="grid grid-cols-3 gap-2.5 sm:grid-cols-4 lg:grid-cols-5">
            {ALL_CAPABILITIES.map((cap) => {
              const Icon = cap.icon
              return (
                <button
                  key={cap.route + cap.label}
                  onClick={() => navigate(cap.route)}
                  className="group relative text-left rounded-xl border border-white/8 bg-white/[0.03] p-3 hover:border-white/15 hover:bg-white/[0.06] transition-all"
                >
                  {cap.isNew && (
                    <span className="absolute top-2 right-2 text-[8px] font-black uppercase px-1.5 py-0.5 rounded bg-emerald-500/25 text-emerald-300 border border-emerald-500/30">
                      NEW
                    </span>
                  )}
                  <Icon size={16} className={`mb-2 ${cap.isNew ? 'text-emerald-400' : 'text-blue-400'}`} />
                  <p className="text-xs font-semibold text-white leading-tight mb-0.5">{cap.label}</p>
                  <p className="text-[10px] text-gray-500 leading-tight">{cap.desc}</p>
                </button>
              )
            })}
          </div>
        </section>

        {/* Architecture callout */}
        <section className="bg-white/[0.03] border border-white/8 rounded-2xl p-6 grid grid-cols-3 gap-6">
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-cyan-400 mb-2">LLM Infrastructure</p>
            <p className="text-sm font-semibold text-white mb-1">Ollama · Qwen 2.5 Coder 14B</p>
            <p className="text-xs text-gray-400">Local GPU inference · zero cloud dependency · CUDA-accelerated embeddings via nomic-embed-text</p>
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-purple-400 mb-2">Vector Store</p>
            <p className="text-sm font-semibold text-white mb-1">LanceDB · GPU-accelerated</p>
            <p className="text-xs text-gray-400">Columnar vector store with ANN search · 11-layer RAG anti-hallucination pipeline · FlashrankRerank</p>
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-emerald-400 mb-2">ML Runtime</p>
            <p className="text-sm font-semibold text-white mb-1">scikit-learn · 1.9.0</p>
            <p className="text-xs text-gray-400">Isolation Forest anomaly detection · statistical drift detection · bias analysis · all running on-device</p>
          </div>
        </section>

      </div>
    </div>
  )
}
