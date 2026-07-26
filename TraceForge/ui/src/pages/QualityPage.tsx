// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (QualityPage.tsx)
// Date: 2025-12-17
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import { useProjectStore } from '../stores/projectStore'

interface Finding {
  code: string
  severity: string
  requirement_ids: string[]
  message: string
}
interface QualityResult {
  total_requirements: number
  finding_count: number
  blocker_count: number
  high_count: number
  quality_gate: string
  findings: Finding[]
}

const severityClass: Record<string, string> = {
  BLOCKER: 'bg-red-500/15 text-red-300',
  HIGH: 'bg-amber-500/15 text-amber-300',
  MEDIUM: 'bg-blue-500/15 text-blue-300',
}

// Function: QualityPage
export default function QualityPage() {
  const { projectId } = useProjectStore()
  const { data, isLoading, isError } = useQuery<QualityResult>({
    queryKey: ['quality', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/quality`)).data,
    enabled: !!projectId,
  })
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Requirement Quality &amp; Conflicts</h1>
        <p className="mt-1 text-xs text-gray-500">
          Deterministic checks for missing evidence, ambiguity, acceptance criteria, and exact duplicates.
        </p>
      </div>
      {isLoading && <p className="text-xs text-gray-500">Evaluating requirements…</p>}
      {isError && <p className="rounded border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-300">Quality analysis could not be loaded.</p>}
      {data && (
        <>
          <div className="grid grid-cols-4 gap-3">
            {[
              ['Quality gate', data.quality_gate],
              ['Requirements', data.total_requirements],
              ['Blockers', data.blocker_count],
              ['High findings', data.high_count],
            ].map(([label, value]) => (
              <div key={label} className="rounded-lg border border-white/10 bg-gray-900 p-3">
                <p className="text-[10px] uppercase text-gray-500">{label}</p>
                <p className="mt-1 text-lg font-semibold text-white">{value}</p>
              </div>
            ))}
          </div>
          <div className="overflow-hidden rounded-lg border border-white/10 bg-gray-900">
            {data.findings.map((finding, index) => (
              <div key={`${finding.code}-${index}`} className="flex items-start gap-3 border-b border-white/5 p-3 last:border-0">
                <span className={`rounded px-2 py-0.5 text-[10px] ${severityClass[finding.severity] || 'bg-gray-800 text-gray-300'}`}>
                  {finding.severity}
                </span>
                <div>
                  <p className="text-xs text-white">{finding.code.replace(/_/g, ' ')}</p>
                  <p className="mt-1 text-[11px] text-gray-400">{finding.message}</p>
                  <p className="mt-1 text-[10px] text-blue-400">{finding.requirement_ids.join(', ')}</p>
                </div>
              </div>
            ))}
            {!data.findings.length && <p className="p-8 text-center text-xs text-emerald-300">No deterministic quality findings.</p>}
          </div>
        </>
      )}
    </div>
  )
}
