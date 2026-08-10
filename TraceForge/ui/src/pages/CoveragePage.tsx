// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (CoveragePage.tsx)
// Date: 2026-07-18
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import type { CoverageSummary } from '../api/types'
import { useProjectStore } from '../stores/projectStore'

interface CoverageGapsResponse {
  gaps: Array<{ req_id: string; title: string; category: string; reasons: string[] }>
  count: number
  information_gaps: Array<{ req_id: string; title: string; category: string }>
  information_gap_count: number
}

// Function: CoveragePage
export default function CoveragePage() {
  const { projectId } = useProjectStore()
  const { data } = useQuery<CoverageSummary>({
    queryKey: ['coverage', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/coverage`)).data,
    enabled: !!projectId,
  })
  const { data: gapData } = useQuery<CoverageGapsResponse>({
    queryKey: ['coverage-gaps', projectId],
    queryFn: async () => (await api.get<CoverageGapsResponse>(`/projects/${projectId}/gaps`)).data,
    enabled: !!projectId,
  })
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Verification Coverage</h1>
        <p className="mt-1 text-xs text-gray-500">Requirement-to-test and test-to-script coverage with actionable gaps.</p>
      </div>
      {data && (
        <div className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-lg border border-emerald-500/25 bg-emerald-500/5 p-4">
              <p className="text-[10px] uppercase text-gray-500">Test design coverage</p>
              <p className="mt-1 text-2xl font-semibold text-emerald-300">{data.test_design_coverage_pct}%</p>
              <p className="mt-1 text-[11px] text-gray-500">{data.covered_requirements} of {data.total_requirements} active requirements meet policy</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-gray-900 p-4">
              <p className="text-[10px] uppercase text-gray-500">Human review</p>
              <p className="mt-1 text-2xl font-semibold text-white">{data.test_review_pct}%</p>
              <p className="mt-1 text-[11px] text-gray-500">{data.reviewed_test_cases} of {data.total_test_cases} cases approved</p>
            </div>
            <div className="rounded-lg border border-amber-500/25 bg-amber-500/5 p-4">
              <p className="text-[10px] uppercase text-gray-500">Automation eligibility</p>
              <p className="mt-1 text-2xl font-semibold text-amber-600">{data.automation_eligibility_pct}%</p>
              <p className="mt-1 text-[11px] text-gray-500">{data.automation_ready_test_cases} ready · {data.automation_blocked_test_cases} blocked · {data.manual_test_cases} manual</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-gray-900 p-4">
              <p className="text-[10px] uppercase text-gray-500">Script coverage</p>
              <p className="mt-1 text-2xl font-semibold text-white">{data.script_coverage_status === 'NOT_APPLICABLE' ? 'N/A' : `${data.script_coverage_pct}%`}</p>
              <p className="mt-1 text-[11px] text-gray-500">{data.scripted_ready_test_cases} scripted of {data.automation_ready_test_cases} eligible · {data.stale_scripts} stale</p>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-lg border border-white/10 bg-gray-900 p-3">
              <p className="text-[10px] uppercase text-gray-500">Requirements baseline</p>
              <p className="mt-1 text-lg font-semibold text-white">{data.total_requirements}</p>
              <p className="text-[11px] text-gray-500">{data.executable_requirements} executable · {data.information_gap_requirements} unresolved blockers</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-gray-900 p-3">
              <p className="text-[10px] uppercase text-gray-500">Designed cases</p>
              <p className="mt-1 text-lg font-semibold text-white">{data.total_test_cases}</p>
              <p className="text-[11px] text-gray-500">Source-grounded scenarios in the review inventory</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-gray-900 p-3">
              <p className="text-[10px] uppercase text-gray-500">Generated scripts</p>
              <p className="mt-1 text-lg font-semibold text-white">{data.total_scripts}</p>
              <p className="text-[11px] text-gray-500">Generated only after a complete automation contract is verified</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 rounded-lg border border-blue-500/20 bg-blue-500/5 p-3">
            <p className="mr-auto text-xs text-gray-300">Workflow actions</p>
            {(gapData?.count || gapData?.information_gap_count) ? <Link to="/requirements/register" className="rounded border border-white/15 px-3 py-1.5 text-xs text-gray-200 hover:bg-white/5">Enrich Requirements</Link> : null}
            <Link to="/verification/test-cases" className="rounded border border-white/15 px-3 py-1.5 text-xs text-gray-200 hover:bg-white/5">Review Test Design</Link>
            <Link to="/verification/scripts" className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-500">Configure Automation &amp; Scripts</Link>
          </div>
        </div>
      )}
      <div className="rounded-lg border border-white/10 bg-gray-900 p-4">
        <h2 className="text-xs font-semibold text-white">Actionable test-design gaps</h2>
        <p className="mb-3 mt-1 text-[11px] text-gray-500">Only executable requirements that fail deterministic policy appear here.</p>
        {gapData?.gaps.map((gap) => (
          <div key={gap.req_id} className="mb-2 rounded border border-red-500/20 bg-red-500/5 p-3">
            <div className="flex items-center justify-between"><p className="text-xs text-red-300">{gap.req_id} · {gap.title}</p><Link to={`/requirements/register?req=${gap.req_id}`} className="rounded border border-red-500/30 px-2 py-1 text-[10px] text-red-300 hover:bg-red-500/10">Enrich requirement</Link></div>
            {gap.reasons.map((reason) => <p key={reason} className="mt-1 text-[11px] text-gray-400">{reason}</p>)}
          </div>
        ))}
        {gapData && gapData.count === 0 && <p className="text-xs text-emerald-300">All executable requirements satisfy the test-design coverage policy.</p>}
      </div>
      <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
        <h2 className="text-xs font-semibold text-white">Information gaps requiring business input</h2>
        <p className="mt-1 text-[11px] text-gray-500">These unresolved source-derived assumptions count against complete coverage. Add confirmed outcomes and acceptance criteria; they then enter Test Design automatically.</p>
        <details className="mt-3">
          <summary className="cursor-pointer text-xs text-amber-600">{gapData?.information_gap_count || 0} information gaps</summary>
          <div className="mt-2 grid gap-2 md:grid-cols-2">
            {gapData?.information_gaps.map((gap) => (
              <Link key={gap.req_id} to={`/requirements/register?req=${gap.req_id}`} className="rounded border border-white/10 bg-gray-900 p-2 text-[11px] text-gray-300 hover:border-amber-500/30 hover:bg-amber-500/5"><span className="text-amber-600">{gap.req_id}</span> · {gap.title}</Link>
            ))}
          </div>
        </details>
      </div>
    </div>
  )
}
