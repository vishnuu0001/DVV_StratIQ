// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (CoveragePage.tsx)
// Date: 2026-07-18
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import type { CoverageSummary } from '../api/types'
import { useProjectStore } from '../stores/projectStore'

interface CoverageGapsResponse {
  gaps: unknown[]
  count: number
}

// Function: CoveragePage
export default function CoveragePage() {
  const { projectId } = useProjectStore()
  const { data } = useQuery<CoverageSummary>({
    queryKey: ['coverage', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/coverage`)).data,
    enabled: !!projectId,
  })
  const { data: gaps = [] } = useQuery<unknown[]>({
    queryKey: ['coverage-gaps', projectId],
    queryFn: async () => {
      const response = await api.get<CoverageGapsResponse>(`/projects/${projectId}/gaps`)
      return Array.isArray(response.data.gaps) ? response.data.gaps : []
    },
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
        <div className="grid grid-cols-4 gap-3">
          {[
            ['Coverage', `${data.coverage_pct}%`],
            ['Requirements', data.total_requirements],
            ['Test cases', data.total_test_cases],
            ['Scripts', data.total_scripts],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-white/10 bg-gray-900 p-3">
              <p className="text-[10px] uppercase text-gray-500">{label}</p>
              <p className="mt-1 text-lg font-semibold text-white">{value}</p>
            </div>
          ))}
        </div>
      )}
      <div className="rounded-lg border border-white/10 bg-gray-900 p-4">
        <h2 className="mb-3 text-xs font-semibold text-white">Coverage gaps</h2>
        {gaps.map((gap, index) => <pre key={index} className="mb-2 whitespace-pre-wrap rounded bg-gray-950 p-2 text-[11px] text-amber-300">{JSON.stringify(gap, null, 2)}</pre>)}
        {!gaps.length && <p className="text-xs text-emerald-300">No coverage gaps reported.</p>}
      </div>
    </div>
  )
}
