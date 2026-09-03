import {
  ArrowRight, Boxes, BrainCircuit, CheckCircle2, ChevronRight, CloudCog,
  FileCheck2, FolderKanban, FolderUp, GitBranch, Network, Play, ShieldCheck,
} from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout.jsx'

const STAGES = [
  { label: 'Upload assets', title: 'Capture legacy assets', icon: FolderUp, route: '/requirements/upload', description: 'Create an immutable source snapshot with client, ownership and application metadata.', outputs: ['Source inventory', 'Application context', 'Governed snapshot'] },
  { label: 'AI discovery', title: 'Discover the application', icon: BrainCircuit, route: '/requirements/knowledge-graph', description: 'Map business capabilities, dependencies, data relationships and integration boundaries.', outputs: ['Capability map', 'Dependency graph', 'Risk signals'] },
  { label: 'Document review', title: 'Review requirements', icon: FileCheck2, route: '/requirements/brd', description: 'Generate and review evidence-grounded BRD and FSD documents with source traceability.', outputs: ['BRD', 'FSD', 'Traceability'] },
  { label: 'Target architecture', title: 'Approve target architecture', icon: GitBranch, route: '/requirements/architecture-review', description: 'Review domains, services, interfaces, technology choices and deployment topology.', outputs: ['Domain design', 'Target stack', 'Architecture controls'] },
  { label: 'Forward engineering', title: 'Engineer and validate', icon: CloudCog, route: '/projects', description: 'Generate production code and run compiler, dependency and quality validation gates.', outputs: ['Generated code', 'Build results', 'Quality gates'] },
  { label: 'Generated assets', title: 'Review and release assets', icon: Boxes, route: '/requirements/generated-assets', description: 'Access generated source, documents, schemas, infrastructure and audit artifacts.', outputs: ['Source packages', 'Documentation', 'Audit history'] },
]

const QUICK_ACTIONS = [
  { label: 'Upload a project', detail: 'Capture source for requirements discovery', icon: FolderUp, route: '/requirements/upload' },
  { label: 'Open governed projects', detail: 'Plan and execute modernization work', icon: FolderKanban, route: '/projects' },
  { label: 'Explore knowledge graphs', detail: 'Inspect business and functional relationships', icon: Network, route: '/requirements/knowledge-graph' },
]

export default function ModernizationHomePage() {
  const [activeIndex, setActiveIndex] = useState(0)
  const active = STAGES[activeIndex]
  const ActiveIcon = active.icon

  return (
    <Layout>
      <main className="min-h-full bg-[#f5f5f5]">
        <div className="mx-auto max-w-[1480px] px-5 py-6 lg:px-8">
          <div className="mb-3 flex items-center gap-1.5 text-xs text-slate-500">
            <span>Modernization</span><ChevronRight className="h-3 w-3" /><span className="text-slate-800">Overview</span>
          </div>

          <header className="mb-5 flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-[28px] font-semibold tracking-tight text-slate-900">Modernization overview</h1>
              <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-600">Move from governed source evidence to reviewed requirements, target architecture and production-ready assets.</p>
            </div>
            <div className="flex items-center gap-2">
              <Link to="/requirements/upload" className="inline-flex h-9 items-center gap-2 rounded-sm bg-[#0078d4] px-4 text-xs font-semibold text-white shadow-sm hover:bg-[#106ebe]"><FolderUp className="h-4 w-4" />Upload assets</Link>
              <Link to="/projects" className="inline-flex h-9 items-center gap-2 rounded-sm border border-slate-300 bg-white px-4 text-xs font-semibold text-slate-700 hover:border-slate-400 hover:bg-slate-50"><Play className="h-4 w-4" />Governed projects</Link>
            </div>
          </header>

          <section className="mb-5 flex items-start gap-3 border border-[#b3d6f2] bg-[#eff6fc] px-4 py-3" aria-label="Modernization journey status">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[#107c10]" />
            <div className="min-w-0"><p className="text-xs font-semibold text-slate-900">Unified modernization journey is ready</p><p className="mt-0.5 text-xs leading-5 text-slate-600">OpenSourceLLM discovery, governed reviews and engineering validation are connected through one auditable workflow.</p></div>
          </section>

          <section className="mb-5 grid border border-slate-200 bg-white shadow-sm sm:grid-cols-2 xl:grid-cols-4">
            {[
              ['6', 'Governed stages', 'From evidence to release'],
              ['2', 'Requirements artifacts', 'Business and functional'],
              ['1', 'Architecture approval', 'Before engineering starts'],
              ['100%', 'Traceable outputs', 'Linked to source evidence'],
            ].map(([value, label, detail], index) => (
              <div key={label} className={`px-5 py-4 ${index ? 'border-t border-slate-200 sm:border-l sm:border-t-0' : ''} ${index === 2 ? 'sm:border-l-0 xl:border-l' : ''}`}>
                <p className="text-2xl font-semibold text-[#0078d4]">{value}</p><p className="mt-1 text-xs font-semibold text-slate-900">{label}</p><p className="mt-0.5 text-[11px] text-slate-500">{detail}</p>
              </div>
            ))}
          </section>

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
            <section className="border border-slate-200 bg-white shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
                <div><h2 className="text-sm font-semibold text-slate-900">Modernization workflow</h2><p className="mt-0.5 text-xs text-slate-500">Select a stage to review its scope and outputs.</p></div>
                <span className="border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-semibold text-slate-600">Stage {activeIndex + 1} of 6</span>
              </div>

              <div className="grid border-b border-slate-200 md:grid-cols-3 2xl:grid-cols-6">
                {STAGES.map((stage, index) => {
                  const Icon = stage.icon
                  const selected = activeIndex === index
                  return (
                    <button key={stage.label} type="button" data-read-only-allow onClick={() => setActiveIndex(index)} aria-pressed={selected} className={`relative flex min-h-[78px] items-center gap-3 border-b border-r border-slate-200 px-4 py-3 text-left transition last:border-r-0 md:border-b-0 ${selected ? 'bg-[#f3f8fc]' : 'bg-white hover:bg-slate-50'}`}>
                      {selected && <span className="absolute inset-x-0 bottom-0 h-0.5 bg-[#0078d4]" />}
                      <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-sm ${selected ? 'bg-[#0078d4] text-white' : 'bg-slate-100 text-slate-600'}`}><Icon className="h-4 w-4" /></span>
                      <span className="min-w-0"><span className="block text-[10px] font-semibold uppercase tracking-wide text-slate-400">Step {index + 1}</span><span className={`mt-0.5 block text-xs leading-4 ${selected ? 'font-semibold text-[#0078d4]' : 'font-medium text-slate-700'}`}>{stage.label}</span></span>
                    </button>
                  )
                })}
              </div>

              <div className="grid gap-6 p-5 lg:grid-cols-[minmax(0,1fr)_280px] lg:p-6">
                <div className="flex gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-sm bg-[#e5f1fb] text-[#0078d4]"><ActiveIcon className="h-5 w-5" /></div>
                  <div className="min-w-0">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#0078d4]">Current stage</p><h3 className="mt-1 text-xl font-semibold text-slate-900">{active.title}</h3><p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{active.description}</p>
                    <div className="mt-5 flex flex-wrap gap-2"><Link to={active.route} className="inline-flex h-9 items-center gap-2 rounded-sm bg-[#0078d4] px-4 text-xs font-semibold text-white hover:bg-[#106ebe]">Open stage<ArrowRight className="h-3.5 w-3.5" /></Link><Link to="/projects" className="inline-flex h-9 items-center rounded-sm border border-slate-300 bg-white px-4 text-xs font-semibold text-slate-700 hover:bg-slate-50">View workflow details</Link></div>
                  </div>
                </div>
                <div className="border-l-0 border-slate-200 lg:border-l lg:pl-6">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Stage outputs</p>
                  <ul className="mt-3 space-y-2.5">{active.outputs.map(output => <li key={output} className="flex items-center gap-2 text-xs text-slate-700"><CheckCircle2 className="h-3.5 w-3.5 text-[#107c10]" />{output}</li>)}</ul>
                </div>
              </div>
            </section>

            <aside className="border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 px-5 py-4"><h2 className="text-sm font-semibold text-slate-900">Quick actions</h2><p className="mt-0.5 text-xs text-slate-500">Continue in the modernization workspace.</p></div>
              <div className="divide-y divide-slate-200">
                {QUICK_ACTIONS.map(({ label, detail, icon: Icon, route }) => (
                  <Link key={label} to={route} className="group flex items-start gap-3 px-5 py-4 hover:bg-[#f3f8fc]">
                    <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-sm bg-slate-100 text-slate-600 group-hover:bg-[#e5f1fb] group-hover:text-[#0078d4]"><Icon className="h-4 w-4" /></span>
                    <span className="min-w-0 flex-1"><span className="block text-xs font-semibold text-slate-900 group-hover:text-[#0078d4]">{label}</span><span className="mt-1 block text-[11px] leading-4 text-slate-500">{detail}</span></span><ChevronRight className="mt-2 h-3.5 w-3.5 text-slate-400 group-hover:text-[#0078d4]" />
                  </Link>
                ))}
              </div>
              <div className="border-t border-slate-200 bg-slate-50 px-5 py-4"><div className="flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-[#107c10]" /><p className="text-xs font-semibold text-slate-800">Governance enabled</p></div><p className="mt-1.5 text-[11px] leading-5 text-slate-500">Snapshots, approvals, generated assets and validation results retain a complete audit history.</p></div>
            </aside>
          </div>
        </div>
      </main>
    </Layout>
  )
}
