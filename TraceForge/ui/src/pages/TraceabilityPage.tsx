// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (TraceabilityPage.tsx)
// Date: 2025-10-04
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import type { Artifact, CoverageSummary } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

const STATUS_COLOR: Record<string, string> = {
  TEST_DESIGNED: 'bg-emerald-500/20 text-emerald-300', NO_TESTS: 'bg-red-500/20 text-red-300',
  POLICY_GAPS: 'bg-red-500/20 text-red-300', INFORMATION_GAP: 'bg-amber-500/20 text-amber-600',
  AUTOMATION_BLOCKED: 'bg-amber-500/20 text-amber-600', MANUAL_ONLY: 'bg-gray-500/20 text-gray-300',
  READY_FOR_SCRIPT: 'bg-cyan-500/20 text-cyan-300', PARTIALLY_SCRIPTED: 'bg-blue-500/20 text-blue-300',
  SCRIPTED: 'bg-emerald-500/20 text-emerald-300', NOT_APPLICABLE: 'bg-gray-500/15 text-gray-500',
}

// Function: TraceabilityPage
export default function TraceabilityPage() {
  const { projectId } = useProjectStore()
  const [filter, setFilter] = useState<'ALL' | 'EXECUTABLE' | 'INFORMATION_GAP' | 'POLICY_GAPS'>('ALL')
  const [search, setSearch] = useState('')

  const { data: coverage } = useQuery<CoverageSummary>({
    queryKey: ['coverage', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/coverage`)).data,
    enabled: !!projectId,
  })
  const { data: artifacts = [] } = useQuery<Artifact[]>({
    queryKey: ['artifacts', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/artifacts`)).data,
    enabled: !!projectId,
  })

  if (!projectId) return <NoProjectSelected />

  const rtmArtifact = artifacts.filter((a) => a.kind === 'RTM_XLSX').sort((a, b) => b.version - a.version)[0]
  const normalizedSearch = search.trim().toLowerCase()
  const rows = (coverage?.requirements || []).filter((row) => {
    if (filter === 'EXECUTABLE' && !row.testable) return false
    if (filter === 'INFORMATION_GAP' && row.testable) return false
    if (filter === 'POLICY_GAPS' && (row.policy_compliant || !row.testable)) return false
    return !normalizedSearch || [row.req_id, row.title, row.statement].join(' ').toLowerCase().includes(normalizedSearch)
  })

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
          <button type="button" onClick={() => download(rtmArtifact)} className="text-xs bg-gray-800 hover:bg-gray-700 rounded px-3 py-1.5">Download RTM.xlsx</button>
        )}
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search requirement, title, or statement"
          className="min-w-64 flex-1 rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white outline-none focus:border-blue-500" />
        <div className="flex rounded border border-white/10 bg-gray-900 p-0.5">
          {(['ALL', 'EXECUTABLE', 'INFORMATION_GAP', 'POLICY_GAPS'] as const).map((value) => (
            <button key={value} type="button" onClick={() => setFilter(value)}
              className={`px-3 py-1.5 text-[10px] ${filter === value ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}>
              {value.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto rounded border border-white/10">
      <table className="w-full min-w-[1050px] text-xs">
        <thead className="text-gray-500 text-left">
          <tr>
            <th className="px-3 py-2 font-normal">REQ-ID</th>
            <th className="px-3 py-2 font-normal">Statement</th>
            <th className="px-3 py-2 font-normal">Test design</th>
            <th className="px-3 py-2 font-normal">Review</th>
            <th className="px-3 py-2 font-normal">Automation</th>
            <th className="px-3 py-2 font-normal">Scripts</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
              <tr key={row.requirement_id} className="border-t border-white/5 align-top">
                <td className="px-3 py-2 text-blue-400">{row.req_id}</td>
                <td className="max-w-lg px-3 py-2 text-gray-300"><p>{row.statement}</p><p className="mt-1 text-[10px] text-gray-600">{row.level}</p></td>
                <td className="px-3 py-2">
                  <span className={`whitespace-nowrap rounded-full px-2 py-0.5 text-[10px] ${STATUS_COLOR[row.test_status]}`}>{row.test_status.replace(/_/g, ' ')}</span>
                  <p className="mt-1 text-[10px] text-gray-500">{row.test_count} cases</p>
                </td>
                <td className="px-3 py-2 text-gray-400">{row.reviewed_test_count} / {row.test_count}</td>
                <td className="px-3 py-2">
                  <span className={`whitespace-nowrap rounded-full px-2 py-0.5 text-[10px] ${STATUS_COLOR[row.automation_status]}`}>{row.automation_status.replace(/_/g, ' ')}</span>
                  {row.automation_blocked_count > 0 && <p className="mt-1 text-[10px] text-gray-500">{row.automation_blocked_count} blocked</p>}
                </td>
                <td className="px-3 py-2 text-gray-400">{row.script_count} / {row.automation_ready_count} eligible</td>
              </tr>
          ))}
          {rows.length === 0 && <tr><td colSpan={6} className="px-3 py-8 text-center text-gray-600">No requirements match this view.</td></tr>}
        </tbody>
      </table>
      </div>
    </div>
  )
}
