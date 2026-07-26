// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/pages (OperatingModelPage.tsx)
// Date: 2026-07-06
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { OperatingModelResponse, OperatingModelParticipant, OperatingModelRoadmapItem, RaciEntry } from '../types'
import SectionHeader from '../components/ui/SectionHeader'
import NoWorkbook from '../components/ui/NoWorkbook'
import { CheckCircle } from 'lucide-react'

// Static fallback data
const STATIC_DATA: OperatingModelResponse = {
  participants: [
    {
      name: 'Mazda',
      role: 'Business Sponsor & Decision Authority',
      responsibilities: ['Strategic direction', 'Executive sponsorship', 'Commercial sign-off', 'Requirements prioritization'],
      color: '#3B82F6',
    },
    {
      name: 'EY',
      role: 'Program Management & Advisory',
      responsibilities: ['Program governance', 'Consolidation roadmap', 'Vendor negotiation support', 'Change management'],
      color: '#22D3EE',
    },
    {
      name: 'Microsoft',
      role: 'Platform & Hyperscaler',
      responsibilities: ['Azure platform', 'M365 productivity suite', 'Security posture', 'AI/Copilot enablement'],
      color: '#34D399',
    },
    {
      name: 'Tech Mahindra',
      role: 'Managed Services Integrator',
      responsibilities: ['Delivery execution', 'Tower operations', 'Vendor management', 'Savings realization'],
      color: '#8B5CF6',
    },
  ],
  roadmap: [
    {
      phase: 'Phase 1: Foundation',
      months: 'Months 1-3',
      activities: ['Baseline current state', 'Vendor rationalization plan', 'Governance model', 'Quick wins identification'],
      milestone: 'Consolidation Blueprint Approved',
    },
    {
      phase: 'Phase 2: Consolidation',
      months: 'Months 4-9',
      activities: ['Vendor contract transitions', 'Service migration', 'Skills transfer', 'Process standardization'],
      milestone: 'First Wave Vendors Consolidated',
    },
    {
      phase: 'Phase 3: Optimization',
      months: 'Months 10-18',
      activities: ['Performance baselining', 'Continuous improvement', 'Savings realization tracking', 'Reinvestment deployment'],
      milestone: 'Run-Rate Savings Achieved',
    },
    {
      phase: 'Phase 4: Transformation',
      months: 'Months 19-24',
      activities: ['Digital acceleration programs', 'AI/automation initiatives', 'New capability build', 'Strategic partnership deepening'],
      milestone: 'Transformation Capacity Fully Deployed',
    },
  ],
  raci: [
    { activity: 'Vendor Selection', mazda: 'A', ey: 'R', microsoft: 'C', tech_mahindra: 'I' },
    { activity: 'Contract Negotiation', mazda: 'A', ey: 'R', microsoft: 'C', tech_mahindra: 'C' },
    { activity: 'Service Delivery', mazda: 'I', ey: 'C', microsoft: 'C', tech_mahindra: 'R' },
    { activity: 'Savings Tracking', mazda: 'A', ey: 'R', microsoft: 'I', tech_mahindra: 'C' },
    { activity: 'Risk Management', mazda: 'A', ey: 'R', microsoft: 'C', tech_mahindra: 'C' },
    { activity: 'Governance & Reporting', mazda: 'A', ey: 'R', microsoft: 'I', tech_mahindra: 'I' },
    { activity: 'Change Management', mazda: 'A', ey: 'R', microsoft: 'I', tech_mahindra: 'C' },
    { activity: 'Technology Roadmap', mazda: 'A', ey: 'C', microsoft: 'R', tech_mahindra: 'C' },
  ],
  priority_areas: [
    { area: 'External Talent Rationalization', description: 'Consolidate contractor and staff aug to TechM managed model', impact: 'High' },
    { area: 'Software License Optimization', description: 'Standardize on Microsoft + core platforms, eliminate duplicates', impact: 'High' },
    { area: 'Data Platform Consolidation', description: 'Migrate to Azure Synapse/Fabric, retire legacy data tools', impact: 'Medium' },
    { area: 'Infrastructure Rightsizing', description: 'Shift remaining on-prem workloads to Azure, optimize hyperscaler spend', impact: 'High' },
    { area: 'Service Management Tooling', description: 'Consolidate ITSM/monitoring to single platform', impact: 'Medium' },
  ],
}

const RACI_COLORS: Record<string, string> = {
  R: 'bg-accent-blue/20 text-accent-blue border-accent-blue/30',
  A: 'bg-accent-purple/20 text-accent-purple border-accent-purple/30',
  C: 'bg-accent-cyan/10 text-accent-cyan border-accent-cyan/20',
  I: 'bg-navy-700/50 text-slate-400 border-navy-600',
}

const IMPACT_STYLES: Record<string, string> = {
  High: 'bg-accent-red/10 text-accent-red border-accent-red/20',
  Medium: 'bg-accent-amber/10 text-accent-amber border-accent-amber/20',
  Low: 'bg-accent-green/10 text-accent-green border-accent-green/20',
}

// Function: RaciBadge
function RaciBadge({ code }: { code: string }) {
  return (
    <span className={`inline-flex items-center justify-center w-7 h-7 rounded-lg text-xs font-bold border ${RACI_COLORS[code] ?? RACI_COLORS.I}`}>
      {code}
    </span>
  )
}

// Function: OperatingModelPage
export default function OperatingModelPage() {
  const { workbookId } = useWorkbook()

  const { data: apiData } = useQuery<OperatingModelResponse>({
    queryKey: ['operating-model', workbookId],
    queryFn: () => apiGet<OperatingModelResponse>(`/workbooks/${workbookId}/calculations/operating-model`),
    enabled: !!workbookId,
  })

  if (!workbookId) return <div className="p-8"><NoWorkbook /></div>

  const data = apiData ?? STATIC_DATA

  return (
    <div className="p-8 space-y-8">
      <SectionHeader
        eyebrow="Governance"
        title="Operating Model"
        subtitle="Participant roles, RACI matrix, and 24-month transformation roadmap"
      />

      {/* Participant cards */}
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">Participants</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {data.participants.map((p: OperatingModelParticipant) => (
            <div
              key={p.name}
              className="bg-navy-800 border border-navy-700 rounded-xl p-5"
              style={{ borderLeftColor: p.color, borderLeftWidth: 3 }}
            >
              <div className="text-lg font-bold mb-1" style={{ color: p.color }}>{p.name}</div>
              <div className="text-xs font-medium text-slate-300 mb-3">{p.role}</div>
              <ul className="space-y-1">
                {p.responsibilities.map((r) => (
                  <li key={r} className="flex items-start gap-1.5 text-xs text-slate-400">
                    <CheckCircle size={10} className="mt-0.5 shrink-0" style={{ color: p.color }} />
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Priority Areas */}
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">Priority Acceleration Areas</div>
        <div className="bg-navy-800 border border-navy-700 rounded-xl overflow-hidden">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-navy-700">
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Area</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Description</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Impact</th>
              </tr>
            </thead>
            <tbody>
              {data.priority_areas.map((area) => (
                <tr key={area.area} className="border-b border-navy-700/50 hover:bg-navy-700/20 transition-colors">
                  <td className="px-4 py-3 text-sm font-medium text-slate-200">{area.area}</td>
                  <td className="px-4 py-3 text-xs text-slate-400 max-w-sm">{area.description}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${IMPACT_STYLES[area.impact] ?? ''}`}>
                      {area.impact}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* RACI matrix */}
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">RACI Matrix</div>
        <div className="mb-3 flex flex-wrap gap-4">
          {[{ code: 'R', label: 'Responsible' }, { code: 'A', label: 'Accountable' }, { code: 'C', label: 'Consulted' }, { code: 'I', label: 'Informed' }].map((item) => (
            <div key={item.code} className="flex items-center gap-2 text-xs">
              <RaciBadge code={item.code} />
              <span className="text-slate-400">{item.label}</span>
            </div>
          ))}
        </div>
        <div className="bg-navy-800 border border-navy-700 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-navy-700">
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500 min-w-[200px]">Activity</th>
                  {['Mazda', 'EY', 'Microsoft', 'Tech Mahindra'].map((p) => (
                    <th key={p} className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500 text-center">{p}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.raci.map((row: RaciEntry) => (
                  <tr key={row.activity} className="border-b border-navy-700/50 hover:bg-navy-700/20 transition-colors">
                    <td className="px-4 py-3 text-sm text-slate-300">{row.activity}</td>
                    <td className="px-4 py-3 text-center"><RaciBadge code={row.mazda} /></td>
                    <td className="px-4 py-3 text-center"><RaciBadge code={row.ey} /></td>
                    <td className="px-4 py-3 text-center"><RaciBadge code={row.microsoft} /></td>
                    <td className="px-4 py-3 text-center"><RaciBadge code={row.tech_mahindra} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Roadmap timeline */}
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">12-24 Month Transformation Roadmap</div>
        <div className="relative">
          {/* Connecting line */}
          <div className="absolute top-6 left-6 right-6 h-0.5 bg-navy-700 hidden lg:block" />
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {data.roadmap.map((phase: OperatingModelRoadmapItem, index) => (
              <div key={phase.phase} className="relative">
                {/* Phase dot */}
                <div className="hidden lg:flex items-center justify-center w-12 h-12 rounded-full bg-navy-800 border-2 border-accent-blue/50 mx-auto mb-4 relative z-10">
                  <span className="text-accent-blue font-bold text-sm">{index + 1}</span>
                </div>
                <div className="bg-navy-800 border border-navy-700 rounded-xl p-4">
                  <div className="text-xs font-bold text-accent-blue mb-0.5">{phase.months}</div>
                  <div className="text-sm font-semibold text-slate-200 mb-2">{phase.phase}</div>
                  <ul className="space-y-1 mb-3">
                    {phase.activities.map((a) => (
                      <li key={a} className="flex items-start gap-1.5 text-xs text-slate-400">
                        <span className="w-1 h-1 rounded-full bg-accent-blue/60 mt-1.5 shrink-0" />
                        {a}
                      </li>
                    ))}
                  </ul>
                  <div className="pt-2 border-t border-navy-700">
                    <div className="flex items-start gap-1.5 text-xs text-accent-green">
                      <CheckCircle size={10} className="shrink-0 mt-0.5" />
                      {phase.milestone}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
