// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (ScriptsPage.tsx)
// Date: 2026-05-24
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import Editor from '@monaco-editor/react'
import { CheckCircle2, GitPullRequest, PlayCircle, XCircle } from 'lucide-react'
import api from '../api/client'
import type { Gate, PipelineRun, TestCase, TestScript } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

// Function: ScriptsPage
export default function ScriptsPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [selected, setSelected] = useState<TestScript | null>(null)
  const [showPrForm, setShowPrForm] = useState(false)
  const [pr, setPr] = useState({ repo_full_name: '', token: '', base_branch: 'main' })
  const [prResult, setPrResult] = useState<string | null>(null)

  const { data: scripts = [] } = useQuery<TestScript[]>({
    queryKey: ['scripts', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/scripts`)).data,
    enabled: !!projectId,
    refetchInterval: 5000,
  })
  const { data: testCases = [] } = useQuery<TestCase[]>({
    queryKey: ['testcases', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/testcases`)).data,
    enabled: !!projectId,
  })
  const { data: runs = [] } = useQuery<PipelineRun[]>({
    queryKey: ['runs', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/runs`)).data,
    enabled: !!projectId,
    refetchInterval: (query) => ((query.state.data as PipelineRun[] | undefined)?.some((item) => ['QUEUED', 'RUNNING'].includes(item.status)) ? 3000 : 30000),
  })
  const run = runs.filter((r) => r.stage === 'SCRIPT_GEN').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0]
  const { data: gate } = useQuery<Gate>({
    queryKey: ['gate', run?.id],
    queryFn: async () => (await api.get(`/runs/${run!.id}/gate`)).data,
    enabled: !!run && run.status === 'AWAITING_APPROVAL',
  })

  const startRun = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/runs`, { stage: 'SCRIPT_GEN' })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['runs', projectId] }),
  })
  const decideGate = useMutation({
    mutationFn: async ({ decision, rationale }: { decision: string; rationale?: string }) => {
      const result = (await api.post(`/runs/${run!.id}/gate/decide`, { decision, rationale, item_decisions: {} })).data
      if (decision === 'APPROVED') await api.post(`/projects/${projectId}/runs`, { stage: 'RENDER' })
      return result
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs', projectId] })
      queryClient.invalidateQueries({ queryKey: ['scripts', projectId] })
      queryClient.invalidateQueries({ queryKey: ['artifacts', projectId] })
    },
  })
  const openPr = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/scripts/github-pr`, pr)).data,
    onSuccess: (data) => setPrResult(`PR opened: ${data.pr_url}`),
    onError: (e: any) => setPrResult(e.response?.data?.detail || 'Failed to open PR.'),
  })

  if (!projectId) return <NoProjectSelected />

  const tcById: Record<string, TestCase> = Object.fromEntries(testCases.map((tc) => [tc.id, tc]))

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div>
          <h1 className="text-sm font-semibold text-white">Scripts</h1>
          <p className="text-xs text-gray-500">TypeScript, one emitter per automation tool — Playwright and Selenium, generated from the same test cases.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowPrForm((v) => !v)} className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 rounded px-3 py-1.5">
            <GitPullRequest size={13} /> Open GitHub PR
          </button>
          <button onClick={() => startRun.mutate()} disabled={startRun.isPending || run?.status === 'RUNNING' || run?.status === 'QUEUED'}
            className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-3 py-1.5">
            <PlayCircle size={13} /> {run?.status === 'RUNNING' ? 'Generating…' : 'Generate Scripts'}
          </button>
        </div>
      </div>

      {showPrForm && (
        <div className="px-6 py-3 border-b border-white/10 bg-gray-900 flex items-center gap-2">
          <input className="flex-1 bg-gray-800 border border-white/10 rounded px-2 py-1 text-xs" placeholder="org/repo" value={pr.repo_full_name} onChange={(e) => setPr((v) => ({ ...v, repo_full_name: e.target.value }))} />
          <input className="flex-1 bg-gray-800 border border-white/10 rounded px-2 py-1 text-xs" type="password" placeholder="GitHub PAT" value={pr.token} onChange={(e) => setPr((v) => ({ ...v, token: e.target.value }))} />
          <input className="w-32 bg-gray-800 border border-white/10 rounded px-2 py-1 text-xs" placeholder="base branch" value={pr.base_branch} onChange={(e) => setPr((v) => ({ ...v, base_branch: e.target.value }))} />
          <button onClick={() => openPr.mutate()} disabled={!pr.repo_full_name || !pr.token || openPr.isPending} className="text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-3 py-1.5">Open PR</button>
        </div>
      )}
      {prResult && <p className="px-6 py-2 text-[11px] text-amber-300 border-b border-white/10">{prResult}</p>}
      {run?.status === 'FAILED' && <p className="px-6 py-2 text-xs text-red-300 border-b border-white/10">{run.error}</p>}

      <div className="flex flex-1 min-h-0">
        <div className="w-72 shrink-0 border-r border-white/10 overflow-y-auto">
          {scripts.map((script) => {
            const tc = tcById[script.test_case_id]
            return (
              <button key={script.id} onClick={() => setSelected(script)}
                className={`w-full text-left px-3 py-2 border-b border-white/5 hover:bg-white/5 ${selected?.id === script.id ? 'bg-blue-600/10' : ''}`}>
                <div className="flex items-center gap-1.5">
                  {script.compiles === true && <CheckCircle2 size={12} className="text-emerald-400 shrink-0" />}
                  {script.compiles === false && <XCircle size={12} className="text-red-400 shrink-0" />}
                  <span className="text-[10px] text-gray-500">{script.ts_id}</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 shrink-0">{script.target === 'PLAYWRIGHT_TS' ? 'Playwright' : 'Selenium'}</span>
                </div>
                <p className="text-xs text-gray-300 truncate mt-0.5">{tc?.title || script.file_path}</p>
              </button>
            )
          })}
          {scripts.length === 0 && <p className="p-4 text-xs text-gray-600">No scripts yet.</p>}
        </div>

        <div className="flex-1 flex min-w-0">
          {selected ? (
            <>
              <div className="w-80 shrink-0 border-r border-white/10 p-4 overflow-y-auto">
                <p className="text-[10px] text-gray-500 mb-2">{selected.file_path}</p>
                <h3 className="text-xs font-semibold text-white mb-2">{tcById[selected.test_case_id]?.title}</h3>
                <ol className="space-y-1.5">
                  {(tcById[selected.test_case_id]?.steps || []).map((step) => (
                    <li key={step.step_no} className="text-[11px] text-gray-400">
                      <span className="text-gray-600">{step.step_no}.</span> {step.action}
                      <br /><span className="text-gray-600">Expected: {step.expected_result}</span>
                    </li>
                  ))}
                </ol>
                <div className={`mt-3 text-[11px] px-2 py-1.5 rounded ${selected.compiles ? 'bg-emerald-500/10 text-emerald-300' : selected.compiles === false ? 'bg-red-500/10 text-red-300' : 'bg-gray-800 text-gray-500'}`}>
                  {selected.compiles ? 'Compiles cleanly' : selected.compiles === false ? (selected.validation_output || 'Does not compile') : 'Not validated'}
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <Editor
                  height="100%" language="typescript" theme="vs-dark" value={selected.code}
                  options={{ readOnly: true, minimap: { enabled: false }, fontSize: 12 }}
                />
              </div>
            </>
          ) : (
            <p className="p-6 text-xs text-gray-600">Select a script to view it side-by-side with its test case.</p>
          )}
        </div>
      </div>

      {run?.status === 'AWAITING_APPROVAL' && gate?.decision === 'PENDING' && (
        <div className="border-t border-amber-500/30 bg-amber-500/10 px-6 py-3 flex items-center justify-between">
          <p className="text-xs text-amber-300">⚠ {scripts.length} scripts awaiting reviewer approval.</p>
          <div className="flex gap-2">
            <button onClick={() => decideGate.mutate({ decision: 'APPROVED' })} disabled={decideGate.isPending}
              className="text-xs bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-1.5 disabled:opacity-50">Approve &amp; Generate Final Artifacts</button>
            <button
              onClick={() => { const r = window.prompt('Rationale for rejecting (mandatory):'); if (r) decideGate.mutate({ decision: 'REJECTED', rationale: r }) }}
              disabled={decideGate.isPending} className="text-xs bg-red-600/80 hover:bg-red-500 rounded px-3 py-1.5 disabled:opacity-50">Reject</button>
          </div>
        </div>
      )}
    </div>
  )
}
