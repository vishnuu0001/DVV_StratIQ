// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (RequirementsPage.tsx)
// Date: 2026-05-31
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import type { Gate, PipelineRun, Requirement } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'
import AmbiguityGauge from '../components/AmbiguityGauge'
import CitationDrawer from '../components/CitationDrawer'

const EARS_COLOR: Record<string, string> = {
  UBIQUITOUS: 'text-gray-400',
  EVENT_DRIVEN: 'text-blue-400',
  STATE_DRIVEN: 'text-purple-400',
  OPTIONAL_FEATURE: 'text-cyan-400',
  UNWANTED_BEHAVIOUR: 'text-red-400',
  COMPLEX: 'text-amber-400',
  NON_CONFORMANT: 'text-red-500',
}

// Function: RequirementsPage
export default function RequirementsPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const { data: requirements = [] } = useQuery<Requirement[]>({
    queryKey: ['requirements', projectId, statusFilter],
    queryFn: async () => (await api.get(`/projects/${projectId}/requirements`, { params: statusFilter ? { status: statusFilter } : {} })).data,
    enabled: !!projectId,
  })

  const { data: runs = [] } = useQuery<PipelineRun[]>({
    queryKey: ['runs', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/runs`)).data,
    enabled: !!projectId,
    refetchInterval: (query) => ((query.state.data as PipelineRun[] | undefined)?.some((run) => ['QUEUED', 'RUNNING'].includes(run.status)) ? 3000 : 30000),
  })
  const extractRun = runs.filter((r) => r.stage === 'EXTRACT').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0]

  const { data: gate } = useQuery<Gate>({
    queryKey: ['gate', extractRun?.id],
    queryFn: async () => (await api.get(`/runs/${extractRun!.id}/gate`)).data,
    enabled: !!extractRun && extractRun.status === 'AWAITING_APPROVAL',
  })

  const decideGate = useMutation({
    mutationFn: async ({ decision, rationale }: { decision: string; rationale?: string }) => {
      const result = (await api.post(`/runs/${extractRun!.id}/gate/decide`, { decision, rationale, item_decisions: {} })).data
      if (decision === 'APPROVED') await api.post(`/projects/${projectId}/runs`, { stage: 'BRD' })
      return result
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs', projectId] })
      queryClient.invalidateQueries({ queryKey: ['gate', extractRun?.id] })
      queryClient.invalidateQueries({ queryKey: ['requirements', projectId] })
    },
  })

  // Function: handleReject
  const handleReject = () => {
    const rationale = window.prompt('Rationale for rejecting (mandatory):')
    if (rationale) decideGate.mutate({ decision: 'REJECTED', rationale })
  }

  if (!projectId) return <NoProjectSelected />

  const threshold = 0.4
  const blocked = requirements.filter((r) => r.ambiguity_score > threshold).length
  const approvable = requirements.length - blocked

  return (
    <div className="flex h-full">
      <div className="w-40 shrink-0 border-r border-white/10 p-3 space-y-3">
        <p className="text-[10px] text-gray-500 uppercase tracking-wide">Status</p>
        {['', 'DRAFT', 'APPROVED', 'REJECTED', 'SUSPECT'].map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`block w-full text-left text-xs px-2 py-1 rounded ${statusFilter === s ? 'bg-blue-600/20 text-blue-300' : 'text-gray-400 hover:bg-white/5'}`}
          >
            {s || 'All'}
          </button>
        ))}
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto">
          <table className="w-full text-xs">
            <thead className="text-gray-500 text-left sticky top-0 bg-gray-950">
              <tr>
                <th className="px-3 py-2 font-normal">REQ-ID</th>
                <th className="px-3 py-2 font-normal">Statement</th>
                <th className="px-3 py-2 font-normal">EARS</th>
                <th className="px-3 py-2 font-normal">Ambiguity</th>
                <th className="px-3 py-2 font-normal">Pri</th>
                <th className="px-3 py-2 font-normal">Status</th>
              </tr>
            </thead>
            <tbody>
              {requirements.map((req) => (
                <tr
                  key={req.id}
                  onClick={() => setSelectedId(req.id)}
                  className={`border-t border-white/5 cursor-pointer hover:bg-white/5 ${req.ambiguity_score > threshold ? 'border-l-2 border-l-red-500' : ''} ${selectedId === req.id ? 'bg-blue-600/10' : ''}`}
                >
                  <td className="px-3 py-2 text-gray-400 whitespace-nowrap">{req.req_id}</td>
                  <td className="px-3 py-2 text-gray-200 max-w-md truncate">{req.statement}</td>
                  <td className={`px-3 py-2 whitespace-nowrap ${EARS_COLOR[req.ears_pattern] || 'text-gray-400'}`}>{req.ears_pattern}</td>
                  <td className="px-3 py-2"><AmbiguityGauge score={req.ambiguity_score} /></td>
                  <td className="px-3 py-2 text-gray-400">{req.priority}</td>
                  <td className="px-3 py-2 text-gray-400">{req.status}</td>
                </tr>
              ))}
              {requirements.length === 0 && (
                <tr><td colSpan={6} className="px-3 py-8 text-center text-gray-600">No requirements yet — run Extract from the Overview tab.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {extractRun?.status === 'AWAITING_APPROVAL' && gate?.decision === 'PENDING' && (
          <div className="border-t border-amber-500/30 bg-amber-500/10 px-4 py-3 flex items-center justify-between">
            <p className="text-xs text-amber-300">
              ⚠ {requirements.length} requirements awaiting your approval. {blocked} are blocked (ambiguity &gt; {threshold.toFixed(2)}).
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => decideGate.mutate({ decision: 'APPROVED' })}
                disabled={decideGate.isPending}
                className="text-xs bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-1.5 disabled:opacity-50"
              >
                Approve {approvable} &amp; Generate Documents
              </button>
              <button
                onClick={handleReject}
                disabled={decideGate.isPending}
                className="text-xs bg-red-600/80 hover:bg-red-500 rounded px-3 py-1.5 disabled:opacity-50"
                title="Rejecting without per-item comments — full per-item reject UI is Phase 2"
              >
                Reject all
              </button>
            </div>
          </div>
        )}
      </div>

      {selectedId && <CitationDrawer requirementId={selectedId} onClose={() => setSelectedId(null)} />}
    </div>
  )
}
