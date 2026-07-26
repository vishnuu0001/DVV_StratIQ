// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (DocumentsPage.tsx)
// Date: 2026-04-29
// ---------------------------------------------------------------------------
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, FileText, PlayCircle } from 'lucide-react'
import api from '../api/client'
import type { Artifact, Gate, PipelineRun } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

const DOC_KINDS = [
  { kind: 'BRD_DOCX', label: 'Business Requirements Document (BRD)' },
  { kind: 'FRD_DOCX', label: 'Software / Functional Requirements Specification (SRS / FRS)' },
  { kind: 'FSD_DOCX', label: 'Functional Design Specification' },
  { kind: 'SOLUTION_DOC_DOCX', label: 'Architecture & Solution Design' },
]

interface DocumentsPageProps {
  title?: string
  subtitle?: string
  kinds?: string[]
}

// Function: DocumentsPage
export default function DocumentsPage({
  title = 'Specifications',
  subtitle = 'BRD, SRS/FRS, functional design, and architecture generated from the same approved and cited requirement baseline.',
  kinds,
}: DocumentsPageProps) {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()

  const { data: artifacts = [] } = useQuery<Artifact[]>({
    queryKey: ['artifacts', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/artifacts`)).data,
    enabled: !!projectId,
    refetchInterval: 5000,
  })
  const { data: runs = [] } = useQuery<PipelineRun[]>({
    queryKey: ['runs', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/runs`)).data,
    enabled: !!projectId,
    refetchInterval: (query) => ((query.state.data as PipelineRun[] | undefined)?.some((run) => ['QUEUED', 'RUNNING'].includes(run.status)) ? 3000 : 30000),
  })
  const brdRun = runs.filter((r) => r.stage === 'BRD').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0]

  const { data: gate } = useQuery<Gate>({
    queryKey: ['gate', brdRun?.id],
    queryFn: async () => (await api.get(`/runs/${brdRun!.id}/gate`)).data,
    enabled: !!brdRun && brdRun.status === 'AWAITING_APPROVAL',
  })

  const startBrd = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/runs`, { stage: 'BRD' })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['runs', projectId] }),
  })

  const decideGate = useMutation({
    mutationFn: async ({ decision, rationale }: { decision: string; rationale?: string }) => {
      const result = (await api.post(`/runs/${brdRun!.id}/gate/decide`, { decision, rationale, item_decisions: {} })).data
      if (decision === 'APPROVED') await api.post(`/projects/${projectId}/runs`, { stage: 'TEST_DESIGN' })
      return result
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs', projectId] })
      queryClient.invalidateQueries({ queryKey: ['artifacts', projectId] })
    },
  })

  if (!projectId) return <NoProjectSelected />

  const visibleKinds = kinds ? DOC_KINDS.filter((item) => kinds.includes(item.kind)) : DOC_KINDS
  const latestByKind: Record<string, Artifact> = {}
  for (const a of artifacts) {
    if (visibleKinds.some((d) => d.kind === a.kind) && (!latestByKind[a.kind] || a.version > latestByKind[a.kind].version)) {
      latestByKind[a.kind] = a
    }
  }

  // Function: download
  const download = async (artifact: Artifact) => {
    const response = await api.get(`/artifacts/${artifact.id}/download`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = artifact.filename
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-sm font-semibold text-white">{title}</h1>
          <p className="text-xs text-gray-500">{subtitle}</p>
        </div>
        <button
          onClick={() => startBrd.mutate()}
          disabled={startBrd.isPending || brdRun?.status === 'RUNNING' || brdRun?.status === 'QUEUED'}
          className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-3 py-1.5 shrink-0"
        >
          <PlayCircle size={13} /> {brdRun?.status === 'RUNNING' ? 'Generating…' : 'Generate Documents'}
        </button>
      </div>

      {brdRun?.status === 'FAILED' && (
        <div className="bg-red-500/10 border border-red-500/30 rounded p-3 text-xs text-red-300 mb-4">{brdRun.error}</div>
      )}

      <div className="space-y-2 mb-4">
        {visibleKinds.map(({ kind, label }) => {
          const artifact = latestByKind[kind]
          return (
            <div key={kind} className="flex items-center justify-between bg-gray-900 border border-white/10 rounded-lg p-3">
              <div className="flex items-center gap-3 min-w-0">
                <FileText size={16} className="text-blue-400 shrink-0" />
                <div className="min-w-0">
                  <p className="text-xs text-white">{label}</p>
                  <p className="text-[10px] text-gray-500">{artifact ? `${artifact.filename} · v${artifact.version}` : 'Not generated yet'}</p>
                </div>
              </div>
              {artifact && (
                <button onClick={() => download(artifact)} className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 rounded px-3 py-1.5 shrink-0">
                  <Download size={12} /> Download
                </button>
              )}
            </div>
          )
        })}
      </div>

      {brdRun?.status === 'AWAITING_APPROVAL' && gate?.decision === 'PENDING' && (
        <div className="border border-amber-500/30 bg-amber-500/10 rounded-lg px-4 py-3 flex items-center justify-between">
          <p className="text-xs text-amber-300">⚠ Documents generated and awaiting Architect review before Test Design can start.</p>
          <div className="flex gap-2">
            <button onClick={() => decideGate.mutate({ decision: 'APPROVED' })} disabled={decideGate.isPending}
              className="text-xs bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-1.5 disabled:opacity-50">Approve &amp; Generate Test Plan</button>
            <button
              onClick={() => { const r = window.prompt('Rationale for rejecting (mandatory):'); if (r) decideGate.mutate({ decision: 'REJECTED', rationale: r }) }}
              disabled={decideGate.isPending} className="text-xs bg-red-600/80 hover:bg-red-500 rounded px-3 py-1.5 disabled:opacity-50">Reject</button>
          </div>
        </div>
      )}
    </div>
  )
}
