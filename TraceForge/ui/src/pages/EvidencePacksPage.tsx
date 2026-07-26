// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (EvidencePacksPage.tsx)
// Date: 2026-01-11
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import { Download } from 'lucide-react'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import type { Artifact } from '../api/types'
import { useProjectStore } from '../stores/projectStore'

// Function: EvidencePacksPage
export default function EvidencePacksPage() {
  const { projectId } = useProjectStore()
  const { data: artifacts = [] } = useQuery<Artifact[]>({
    queryKey: ['artifacts', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/artifacts`)).data,
    enabled: !!projectId,
  })
  if (!projectId) return <NoProjectSelected />
  const packs = artifacts.filter((item) => item.kind === 'TEST_PACK_ZIP' || item.kind === 'RTM_XLSX')
  // Function: download
  const download = async (artifact: Artifact) => {
    const response = await api.get(`/artifacts/${artifact.id}/download`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url; link.download = artifact.filename; link.click()
    URL.revokeObjectURL(url)
  }
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Evidence Packs</h1>
        <p className="mt-1 text-xs text-gray-500">Audit-ready matrices and evidence archives with checksums and source provenance.</p>
      </div>
      {packs.map((artifact) => (
        <div key={artifact.id} className="flex items-center justify-between rounded-lg border border-white/10 bg-gray-900 p-3">
          <div><p className="text-xs text-white">{artifact.filename}</p><p className="mt-1 text-[10px] text-gray-500">{artifact.kind} · v{artifact.version}</p></div>
          <button onClick={() => download(artifact)} className="flex items-center gap-1 rounded bg-gray-800 px-3 py-1.5 text-xs"><Download size={12} /> Download</button>
        </div>
      ))}
      {!packs.length && <p className="py-8 text-center text-xs text-gray-600">No evidence packs generated.</p>}
    </div>
  )
}
