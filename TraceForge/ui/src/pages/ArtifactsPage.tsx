// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (ArtifactsPage.tsx)
// Date: 2025-12-29
// ---------------------------------------------------------------------------
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, Download, FileText, PlayCircle } from 'lucide-react'
import api from '../api/client'
import type { Artifact, PipelineRun } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

const KIND_LABEL: Record<string, string> = {
  BRD_DOCX: 'Business Requirements Document', FRD_DOCX: 'Software / Functional Requirements Specification',
  FSD_DOCX: 'Functional Design Specification',
  SOLUTION_DOC_DOCX: 'Solution Documentation', TEST_PLAN_DOCX: 'Test Plan',
  RTM_XLSX: 'Requirements Traceability Matrix', TEST_PACK_ZIP: 'Test Evidence Pack', SCRIPT_BUNDLE_ZIP: 'Script Bundle',
}

// Function: ArtifactsPage
export default function ArtifactsPage() {
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
    refetchInterval: 3000,
  })
  const renderRun = runs.filter((r) => r.stage === 'RENDER').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0]
  const scriptRun = runs.filter((r) => r.stage === 'SCRIPT_GEN').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0]
  const finalArtifactsCurrent = !!renderRun && !!scriptRun && renderRun.status === 'APPROVED' && renderRun.created_at > scriptRun.created_at
  const startRender = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/runs`, { stage: 'RENDER' })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['runs', projectId] }),
  })

  if (!projectId) return <NoProjectSelected />

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
          <h1 className="text-sm font-semibold text-white mb-1">Artifacts</h1>
          <p className="text-xs text-gray-500">Generated deliverables, versioned and downloadable.</p>
        </div>
        <button
          onClick={() => startRender.mutate()}
          disabled={startRender.isPending || renderRun?.status === 'QUEUED' || renderRun?.status === 'RUNNING' || scriptRun?.status !== 'APPROVED' || finalArtifactsCurrent}
          title={scriptRun?.status !== 'APPROVED' ? 'Approve generated scripts at Gate 4 first.' : 'Generate the RTM and evidence pack.'}
          className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-3 py-1.5"
        >
          <PlayCircle size={13} /> {renderRun?.status === 'RUNNING' ? 'Rendering…' : finalArtifactsCurrent ? 'Final Artifacts Ready' : 'Generate Final Artifacts'}
        </button>
      </div>
      {renderRun?.status === 'FAILED' && <p className="mb-4 text-xs text-red-300 bg-red-500/10 border border-red-500/30 rounded p-3">{renderRun.error}</p>}
      <div className="space-y-2">
        {artifacts.map((artifact) => (
          <div key={artifact.id} className={`flex items-center justify-between bg-gray-900 border rounded-lg p-3 ${artifact.stale ? 'border-amber-500/40' : 'border-white/10'}`}>
            <div className="flex items-center gap-3 min-w-0">
              <FileText size={16} className="text-blue-400 shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-white truncate">{KIND_LABEL[artifact.kind] || artifact.kind}</p>
                <p className="text-[10px] text-gray-500 truncate">{artifact.filename} · v{artifact.version}</p>
              </div>
              {artifact.stale && (
                <span className="flex items-center gap-1 text-[10px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full shrink-0" title="An upstream requirement changed since this was generated">
                  <AlertTriangle size={10} /> Stale
                </span>
              )}
            </div>
            <button onClick={() => download(artifact)} className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 rounded px-3 py-1.5 shrink-0">
              <Download size={12} /> Download
            </button>
          </div>
        ))}
        {artifacts.length === 0 && <p className="text-xs text-gray-600 py-8 text-center">No artifacts generated yet — approve Gate 2 (BRD/FSD/SolutionDoc) or later stages to produce them.</p>}
      </div>
    </div>
  )
}
