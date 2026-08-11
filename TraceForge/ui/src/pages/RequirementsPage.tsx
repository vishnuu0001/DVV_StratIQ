// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (RequirementsPage.tsx)
// Date: 2026-05-31
// ---------------------------------------------------------------------------
import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { AlertTriangle, Pencil, X } from 'lucide-react'
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

type RequirementDraft = {
  title: string
  statement: string
  level: string
  priority: string
  acceptanceCriteria: string
  status: string
}

// Function: RequirementsPage
export default function RequirementsPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [editing, setEditing] = useState<Requirement | null>(null)
  const [draft, setDraft] = useState<RequirementDraft | null>(null)

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

  const enrichRequirement = useMutation({
    mutationFn: async ({ requirement, values }: { requirement: Requirement; values: RequirementDraft }) => (
      await api.patch(`/requirements/${requirement.id}`, {
        title: values.title.trim(),
        statement: values.statement.trim(),
        level: values.level,
        priority: values.priority,
        acceptance_criteria: values.acceptanceCriteria.split('\n').map((value) => value.trim()).filter(Boolean),
        status: values.status,
      })
    ).data,
    onSuccess: () => {
      setEditing(null)
      setDraft(null)
      queryClient.invalidateQueries({ queryKey: ['requirements', projectId] })
      queryClient.invalidateQueries({ queryKey: ['coverage', projectId] })
      queryClient.invalidateQueries({ queryKey: ['coverage-gaps', projectId] })
      queryClient.invalidateQueries({ queryKey: ['testcases', projectId] })
    },
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not save requirement enrichment.'),
  })

  const openEditor = (requirement: Requirement) => {
    setEditing(requirement)
    setDraft({
      title: requirement.title,
      statement: requirement.statement,
      level: requirement.level,
      priority: requirement.priority,
      acceptanceCriteria: requirement.acceptance_criteria.join('\n'),
      status: requirement.status,
    })
  }

  useEffect(() => {
    const requested = searchParams.get('req')
    if (!requested || editing) return
    const requirement = requirements.find((item) => item.req_id === requested)
    if (requirement) openEditor(requirement)
  }, [editing, requirements, searchParams])

  // Function: handleReject
  const handleReject = () => {
    const rationale = window.prompt('Rationale for rejecting (mandatory):')
    if (rationale) decideGate.mutate({ decision: 'REJECTED', rationale })
  }

  if (!projectId) return <NoProjectSelected />

  const threshold = 0.4
  const ambiguityWarnings = requirements.filter((r) => r.ambiguity_score > threshold).length

  return (
    <div className="flex h-full">
      <div className="w-40 shrink-0 border-r border-white/10 p-3 space-y-3">
        <p className="text-[10px] text-gray-500 uppercase tracking-wide">Status</p>
        {['', 'DRAFT', 'APPROVED', 'REJECTED', 'SUSPECT'].map((s) => (
          <button
            type="button"
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
                <th className="px-3 py-2 font-normal">Action</th>
              </tr>
            </thead>
            <tbody>
              {requirements.map((req) => (
                <tr
                  key={req.id}
                  onClick={() => setSelectedId(req.id)}
                  className={`border-t border-white/5 cursor-pointer hover:bg-white/5 ${req.ambiguity_score > threshold ? 'border-l-2 border-l-amber-500' : ''} ${selectedId === req.id ? 'bg-blue-600/10' : ''}`}
                >
                  <td className="px-3 py-2 text-gray-400 whitespace-nowrap">{req.req_id}</td>
                  <td className="px-3 py-2 text-gray-200 max-w-md truncate">{req.statement}</td>
                  <td className={`px-3 py-2 whitespace-nowrap ${EARS_COLOR[req.ears_pattern] || 'text-gray-400'}`}>{req.ears_pattern}</td>
                  <td className="px-3 py-2"><AmbiguityGauge score={req.ambiguity_score} /></td>
                  <td className="px-3 py-2 text-gray-400">{req.priority}</td>
                  <td className="px-3 py-2 text-gray-400">{req.status}</td>
                  <td className="px-3 py-2">
                    <button type="button" onClick={(event) => { event.stopPropagation(); openEditor(req) }} title={`Enrich ${req.req_id}`} className="rounded p-1 text-gray-400 hover:bg-white/10 hover:text-white"><Pencil size={13} /></button>
                  </td>
                </tr>
              ))}
              {requirements.length === 0 && (
                <tr><td colSpan={7} className="px-3 py-8 text-center text-gray-600">No requirements yet — run Extract from the Overview tab.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {extractRun?.status === 'AWAITING_APPROVAL' && gate?.decision === 'PENDING' && (
          <div className="border-t border-amber-500/30 bg-amber-500/10 px-4 py-3 flex items-center justify-between">
            <p className="flex items-center gap-2 text-xs text-amber-300">
              <AlertTriangle size={14} className="shrink-0" />
              {requirements.length} requirements awaiting approval. {ambiguityWarnings} need ambiguity review (score &gt; {threshold.toFixed(2)}); warnings do not block approval.
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => decideGate.mutate({ decision: 'APPROVED' })}
                disabled={decideGate.isPending}
                className="text-xs bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-1.5 disabled:opacity-50"
              >
                Approve All {requirements.length} &amp; Generate Documents
              </button>
              <button
                type="button"
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
      {editing && draft && (
        <dialog open className="fixed inset-0 z-50 flex h-full max-h-none w-full max-w-none items-center justify-center bg-black/70 p-4" aria-label={`Enrich ${editing.req_id}`}>
          <div className="max-h-[92vh] w-full max-w-3xl overflow-y-auto rounded-lg border border-white/15 bg-gray-950 shadow-2xl">
            <div className="sticky top-0 flex items-center justify-between border-b border-white/10 bg-gray-950 px-5 py-4">
              <div><p className="text-sm font-semibold text-white">Enrich {editing.req_id}</p><p className="mt-1 text-[11px] text-gray-500">Use source-confirmed outcomes only. Approved edits mark downstream artifacts suspect for regeneration.</p></div>
              <button type="button" onClick={() => { setEditing(null); setDraft(null) }} title="Close requirement editor" className="rounded p-1 text-gray-400 hover:bg-white/10 hover:text-white"><X size={16} /></button>
            </div>
            <div className="space-y-4 p-5">
              <label className="block text-[11px] text-gray-400">Title<input value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white" /></label>
              <label className="block text-[11px] text-gray-400">Requirement statement<textarea rows={4} value={draft.statement} onChange={(event) => setDraft({ ...draft, statement: event.target.value })} className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white" /></label>
              <div className="grid gap-3 md:grid-cols-3">
                <label className="text-[11px] text-gray-400">Level<select value={draft.level} onChange={(event) => setDraft({ ...draft, level: event.target.value })} className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white">{['BUSINESS', 'FUNCTIONAL', 'NON_FUNCTIONAL', 'CONSTRAINT', 'ASSUMPTION'].map((value) => <option key={value}>{value}</option>)}</select></label>
                <label className="text-[11px] text-gray-400">Priority<select value={draft.priority} onChange={(event) => setDraft({ ...draft, priority: event.target.value })} className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white">{['MUST', 'SHOULD', 'COULD', 'WONT'].map((value) => <option key={value}>{value}</option>)}</select></label>
                <label className="text-[11px] text-gray-400">Status<select value={draft.status} onChange={(event) => setDraft({ ...draft, status: event.target.value })} className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white">{['DRAFT', 'IN_REVIEW', 'APPROVED', 'REJECTED'].map((value) => <option key={value}>{value}</option>)}</select></label>
              </div>
              <label className="block text-[11px] text-gray-400">Acceptance criteria, one per line<textarea rows={6} value={draft.acceptanceCriteria} onChange={(event) => setDraft({ ...draft, acceptanceCriteria: event.target.value })} placeholder="Enter source-grounded observable outcomes" className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white" /></label>
            </div>
            <div className="sticky bottom-0 flex justify-end gap-2 border-t border-white/10 bg-gray-950 px-5 py-4">
              <button type="button" onClick={() => { setEditing(null); setDraft(null) }} className="rounded border border-white/15 px-3 py-2 text-xs text-gray-300">Cancel</button>
              <button type="button" onClick={() => enrichRequirement.mutate({ requirement: editing, values: draft })} disabled={enrichRequirement.isPending || !draft.title.trim() || !draft.statement.trim() || (draft.level !== 'ASSUMPTION' && !draft.acceptanceCriteria.trim())} className="rounded bg-blue-600 px-3 py-2 text-xs text-white disabled:opacity-40">Save Enrichment</button>
            </div>
          </div>
        </dialog>
      )}
    </div>
  )
}
