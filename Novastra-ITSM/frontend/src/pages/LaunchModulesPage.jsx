// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (LaunchModulesPage.jsx)
// Date: 2025-11-26
// ---------------------------------------------------------------------------
import { Code, BrainCircuit, LayoutDashboard, ArrowRight, Server, Sparkles, ShieldCheck, Compass, Bot, FlaskConical, Image, Cpu } from 'lucide-react'
import { clsx } from 'clsx'
import { useAuth } from '../contexts/AuthContext.jsx'

const MODULES = [
  {
    id: 'infra-scan',
    number: '01',
    label: 'Infra Scan',
    tag: 'Infra Scanner',
    subtitle: 'Infrastructure & Analysis',
    description: 'Scan live infrastructure environments or upload reports to auto-classify every server with a cloud migration strategy.',
    icon: Server,
    launchUrl: 'http://localhost/infra/',
  },
  {
    id: 'code-analysis',
    number: '02',
    label: 'Code Analysis',
    tag: 'Code Intelligence',
    subtitle: 'Infrastructure & Analysis',
    description: 'Clone any GitHub repo to get software health, technical debt, cloud maturity, OSS CVE scan, and an interactive HTML report.',
    icon: Code,
    launchUrl: 'http://localhost/ca/',
  },
  {
    id: 'app-rationalization',
    number: '03',
    label: 'App Rationalization',
    tag: 'Portfolio Decisions',
    subtitle: 'Infrastructure & Analysis',
    description: 'Ingest your application inventory to score every app on business value, technical health, and cloud readiness.',
    icon: LayoutDashboard,
    launchUrl: 'http://localhost/app/',
  },
  {
    id: 'modernization',
    number: '04',
    label: 'Modernization Studio',
    tag: 'Code Modernizer',
    subtitle: 'AI & Intelligence',
    description: 'Upload a legacy codebase and describe the target architecture. AI-powered streams deliver a modernized code archive.',
    icon: Sparkles,
    launchUrl: 'http://localhost/modernization/',
  },
  {
    id: 'ai-playbook',
    number: '05',
    label: 'AI Playbook',
    tag: 'AI Playbooks',
    subtitle: 'AI & Intelligence',
    description: 'AI pair programming, AIOps intelligence, and automated test generation running on a local Ollama LLM.',
    icon: Bot,
    launchUrl: 'http://localhost/ai-playbook/',
  },
  {
    id: 'novastra-itsm',
    number: '06',
    label: 'STM-ITSM',
    tag: 'Knowledge Graph',
    subtitle: 'AI & Intelligence',
    description: 'Query operational knowledge using natural language. Surface incidents, monitoring events, and relationships from a unified graph.',
    icon: BrainCircuit,
    launchUrl: 'http://localhost/novastra-itsm/ticket-analysis',
  },
  {
    id: 'lab-robot',
    number: '07',
    label: 'Lab Robot',
    tag: 'Lab Automation',
    subtitle: 'Automation & Operations',
    description: 'Manage lab chemical inventory and robotic workflows with controlled access and audit-ready execution.',
    icon: FlaskConical,
    launchUrl: 'http://localhost/lab/',
  },
  {
    id: 'image-vision',
    number: '08',
    label: 'ImageVision',
    tag: 'Visual Intelligence',
    subtitle: 'Automation & Operations',
    description: 'Inspect image assets, classify visual signals, and connect computer vision workflows into operational decisions.',
    icon: Image,
    launchUrl: 'http://localhost/vision/',
  },
  {
    id: 'robot-automation',
    number: '09',
    label: 'Robot Automation',
    tag: 'Automation',
    subtitle: 'Automation & Operations',
    description: 'Coordinate robot actions, workflow status, and controlled automation routines from a single operator workspace.',
    icon: Cpu,
    launchUrl: 'http://localhost/robots/',
  },
  {
    id: 'tool-analysis-qualification',
    number: '10',
    label: 'Tool Analysis Qualification',
    tag: 'Governance',
    subtitle: 'Automation & Operations',
    description: 'Evaluate AI-assisted development tools with governance readiness, security guardrails, ROI metrics, and adoption recommendations.',
    icon: Compass,
    launchUrl: 'http://localhost/tools/',
  },
]

// Function: LaunchModulesPage
export default function LaunchModulesPage() {
  const { token, user } = useAuth()
  const allowedApps = new Set(user?.apps || [])
  const visibleModules = user?.role === 'admin'
    ? MODULES
    : MODULES.filter((module) => allowedApps.has(module.id.toUpperCase().replaceAll('-', '_')))

  // Function: withToken
  const withToken = (url) => {
    if (!token) return url
    const joiner = url.includes('#') ? '&' : '#'
    return `${url}${joiner}authToken=${encodeURIComponent(token)}`
  }

  // Function: launchModule
  const launchModule = (url) => {
    window.location.href = withToken(url)
  }

  return (
    <div className="min-h-full bg-[linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),radial-gradient(circle_at_48%_0%,rgba(79,70,229,0.2),transparent_36rem),radial-gradient(circle_at_86%_18%,rgba(6,182,212,0.16),transparent_36rem),#020617] bg-[length:64px_64px,64px_64px,auto,auto,auto] px-7 py-8">
      <div className="mx-auto max-w-7xl">
        <section className="mb-8 border-b border-slate-800 pb-6">
          <p className="mb-2 text-xs font-black uppercase tracking-[0.25em] text-cyan-300">Launch Modules</p>
          <h1 className="text-xs font-black text-white">Open the right workspace for the next decision</h1>
        </section>

        {['Infrastructure & Analysis', 'AI & Intelligence', 'Automation & Operations'].map((section) => (
          <section key={section} className="mb-10">
            <p className="mb-2 text-xs font-black uppercase tracking-[0.25em] text-cyan-300">{section}</p>
            <h2 className="mb-5 border-b border-slate-800 pb-5 text-xs font-black uppercase tracking-widest text-white">
              {section === 'Infrastructure & Analysis' ? 'Discover and rationalize your estate' : section === 'AI & Intelligence' ? 'Modernize, automate, and interact with AI' : 'Operate with controlled automation'}
            </h2>
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
              {visibleModules.filter((module) => module.subtitle === section).map((module) => {
            const Icon = module.icon
            return (
              <article
                key={module.id}
                className="group rounded-3xl border border-slate-700/80 bg-slate-950/65 p-5 transition hover:-translate-y-1 hover:border-cyan-300/40"
              >
                <div className="mb-4 flex h-36 items-center justify-center rounded-2xl border border-cyan-300/20 bg-[linear-gradient(90deg,rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(135deg,rgba(79,70,229,0.35),rgba(6,182,212,0.16))] bg-[length:28px_28px,28px_28px,auto]">
                  <Icon size={42} className="text-cyan-200" />
                </div>
                <div className="mb-3 flex items-center justify-between gap-3">
                  <p className="m-0 text-xs font-black uppercase tracking-[0.22em] text-cyan-300">Module {module.number}</p>
                  <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-bold text-slate-300">{module.tag}</span>
                </div>
                <h3 className="mb-4 text-xs font-black text-white">{module.label}</h3>
                <p className="min-h-24 text-xs leading-relaxed text-slate-300">{module.description}</p>
                <button
                  type="button"
                  onClick={() => launchModule(module.launchUrl)}
                  className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500 px-4 py-2.5 text-xs font-black text-white"
                >
                  {module.label} <ArrowRight size={16} />
                </button>
              </article>
            )
          })}
            </div>
          </section>
        ))}
                  </div>
    </div>
  )
}
