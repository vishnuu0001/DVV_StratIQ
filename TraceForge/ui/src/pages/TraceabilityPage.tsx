// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (TraceabilityPage.tsx)
// Date: 2025-10-04
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import type { Artifact, Requirement, TestCase, TestScript } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

const STATUS_COLOR: Record<string, string> = {
  COVERED: 'bg-emerald-500/20 text-emerald-300', 'NO TESTS': 'bg-red-500/20 text-red-300',
  'NO NEGATIVE': 'bg-amber-500/20 text-amber-300', 'NOT AUTOMATED': 'bg-blue-500/20 text-blue-300',
}

// Function: coverageStatus
function coverageStatus(tcs: TestCase[], scriptedTcIds: Set<string>): string {
  if (tcs.length === 0) return 'NO TESTS'
  if (!tcs.some((tc) => tc.test_type === 'NEGATIVE')) return 'NO NEGATIVE'
  if (!tcs.some((tc) => scriptedTcIds.has(tc.id))) return 'NOT AUTOMATED'
  return 'COVERED'
}

// Function: TraceabilityPage
export default function TraceabilityPage() {
  const { projectId } = useProjectStore()

  const { data: requirements = [] } = useQuery<Requirement[]>({
    queryKey: ['requirements', projectId, ''],
    queryFn: async () => (await api.get(`/projects/${projectId}/requirements`)).data,
    enabled: !!projectId,
  })
  const { data: testCases = [] } = useQuery<TestCase[]>({
    queryKey: ['testcases', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/testcases`)).data,
    enabled: !!projectId,
  })
  const { data: scripts = [] } = useQuery<TestScript[]>({
    queryKey: ['scripts', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/scripts`)).data,
    enabled: !!projectId,
  })
  const { data: artifacts = [] } = useQuery<Artifact[]>({
    queryKey: ['artifacts', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/artifacts`)).data,
    enabled: !!projectId,
  })

  if (!projectId) return <NoProjectSelected />

  const tcByReq: Record<string, TestCase[]> = {}
  for (const tc of testCases) { (tcByReq[tc.requirement_id] ||= []).push(tc) }
  const scriptedTcIds = new Set(scripts.map((s) => s.test_case_id))
  const rtmArtifact = artifacts.filter((a) => a.kind === 'RTM_XLSX').sort((a, b) => b.version - a.version)[0]

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
          <h1 className="text-sm font-semibold text-white">Traceability</h1>
          <p className="text-xs text-gray-500">Live view mirroring the RTM export — REQ → Test Cases → Scripts → Coverage.</p>
        </div>
        {rtmArtifact && (
          <button onClick={() => download(rtmArtifact)} className="text-xs bg-gray-800 hover:bg-gray-700 rounded px-3 py-1.5">Download RTM.xlsx</button>
        )}
      </div>

      <table className="w-full text-xs">
        <thead className="text-gray-500 text-left">
          <tr>
            <th className="px-3 py-2 font-normal">REQ-ID</th>
            <th className="px-3 py-2 font-normal">Statement</th>
            <th className="px-3 py-2 font-normal">Tests</th>
            <th className="px-3 py-2 font-normal">Scripts</th>
            <th className="px-3 py-2 font-normal">Coverage</th>
          </tr>
        </thead>
        <tbody>
          {requirements.map((req) => {
            const tcs = tcByReq[req.id] || []
            const scriptCount = tcs.filter((tc) => scriptedTcIds.has(tc.id)).length
            const status = coverageStatus(tcs, scriptedTcIds)
            return (
              <tr key={req.id} className="border-t border-white/5">
                <td className="px-3 py-2 text-blue-400">{req.req_id}</td>
                <td className="px-3 py-2 text-gray-300 max-w-lg truncate">{req.statement}</td>
                <td className="px-3 py-2 text-gray-400">{tcs.length}</td>
                <td className="px-3 py-2 text-gray-400">{scriptCount}</td>
                <td className="px-3 py-2"><span className={`text-[10px] px-2 py-0.5 rounded-full ${STATUS_COLOR[status]}`}>{status}</span></td>
              </tr>
            )
          })}
          {requirements.length === 0 && <tr><td colSpan={5} className="px-3 py-8 text-center text-gray-600">No requirements yet.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
