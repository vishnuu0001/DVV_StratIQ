// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (ImpactAnalysisPage.tsx)
// Date: 2025-08-05
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import type { Requirement } from '../api/types'
import { useProjectStore } from '../stores/projectStore'

// Function: ImpactAnalysisPage
export default function ImpactAnalysisPage() {
  const { projectId } = useProjectStore()
  const [requirementId, setRequirementId] = useState('')
  const { data: requirements = [] } = useQuery<Requirement[]>({
    queryKey: ['requirements', projectId, 'impact'],
    queryFn: async () => (await api.get(`/projects/${projectId}/requirements`)).data,
    enabled: !!projectId,
  })
  const { data: impact, isFetching } = useQuery<any>({
    queryKey: ['impact', requirementId],
    queryFn: async () => (await api.get(`/requirements/${requirementId}/impact`)).data,
    enabled: !!requirementId,
  })
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Impact Analysis</h1>
        <p className="mt-1 text-xs text-gray-500">Preview downstream test, script, and document impact before changing a requirement.</p>
      </div>
      <select value={requirementId} onChange={(event) => setRequirementId(event.target.value)}
        className="w-full max-w-xl rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs">
        <option value="">Select a requirement…</option>
        {requirements.map((item) => <option key={item.id} value={item.id}>{item.req_id} — {item.title}</option>)}
      </select>
      {isFetching && <p className="text-xs text-gray-500">Calculating impact…</p>}
      {impact && <pre className="overflow-auto rounded-lg border border-white/10 bg-gray-900 p-4 text-xs text-gray-300">{JSON.stringify(impact, null, 2)}</pre>}
    </div>
  )
}
