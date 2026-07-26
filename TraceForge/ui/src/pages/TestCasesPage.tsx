// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (TestCasesPage.tsx)
// Date: 2025-07-13
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, ChevronRight, PlayCircle } from 'lucide-react'
import api from '../api/client'
import type { Gate, PipelineRun, Requirement, TestCase, TestPlan } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

const TYPE_BADGE: Record<string, string> = {
  POSITIVE: 'bg-emerald-500/20 text-emerald-300', NEGATIVE: 'bg-red-500/20 text-red-300',
  EDGE: 'bg-amber-500/20 text-amber-300', BOUNDARY: 'bg-purple-500/20 text-purple-300',
  NEGATIVE_SECURITY: 'bg-red-600/30 text-red-300', PERFORMANCE: 'bg-cyan-500/20 text-cyan-300',
}

// Function: CoverageBadge
function CoverageBadge({ testCases }: { testCases: TestCase[] }) {
  const positive = testCases.filter((tc) => tc.test_type === 'POSITIVE').length
  const negative = testCases.filter((tc) => tc.test_type === 'NEGATIVE').length
  if (negative === 0) return <span className="text-[10px] text-red-400">⚠ NO NEGATIVE</span>
  return <span className="text-[10px] text-emerald-400">✓ {positive}P {negative}N</span>
}

// Function: TestCasesPage
export default function TestCasesPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const { data: requirements = [] } = useQuery<Requirement[]>({
    queryKey: ['requirements', projectId, ''],
    queryFn: async () => (await api.get(`/projects/${projectId}/requirements`)).data,
    enabled: !!projectId,
  })
  const { data: testCases = [] } = useQuery<TestCase[]>({
    queryKey: ['testcases', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/testcases`)).data,
    enabled: !!projectId,
    refetchInterval: 5000,
  })
  const { data: testPlan } = useQuery<TestPlan | null>({
    queryKey: ['testplan', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/test-plan`)).data,
    enabled: !!projectId,
    retry: false,
  })
  const { data: runs = [] } = useQuery<PipelineRun[]>({
    queryKey: ['runs', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/runs`)).data,
    enabled: !!projectId,
    refetchInterval: (query) => ((query.state.data as PipelineRun[] | undefined)?.some((item) => ['QUEUED', 'RUNNING'].includes(item.status)) ? 3000 : 30000),
  })
  const run = runs.filter((r) => r.stage === 'TEST_DESIGN').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0]
  const { data: gate } = useQuery<Gate>({
    queryKey: ['gate', run?.id],
    queryFn: async () => (await api.get(`/runs/${run!.id}/gate`)).data,
    enabled: !!run && run.status === 'AWAITING_APPROVAL',
  })

  const startRun = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/runs`, { stage: 'TEST_DESIGN' })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['runs', projectId] }),
  })
  const decideGate = useMutation({
    mutationFn: async ({ decision, rationale }: { decision: string; rationale?: string }) => {
      const result = (await api.post(`/runs/${run!.id}/gate/decide`, { decision, rationale, item_decisions: {} })).data
      if (decision === 'APPROVED') await api.post(`/projects/${projectId}/runs`, { stage: 'SCRIPT_GEN' })
      return result
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs', projectId] })
      queryClient.invalidateQueries({ queryKey: ['testcases', projectId] })
      queryClient.invalidateQueries({ queryKey: ['testplan', projectId] })
    },
  })

  if (!projectId) return <NoProjectSelected />

  const tcByReq: Record<string, TestCase[]> = {}
  for (const tc of testCases) {
    tcByReq[tc.requirement_id] = tcByReq[tc.requirement_id] || []
    tcByReq[tc.requirement_id].push(tc)
  }
  const approvedRequirements = requirements.filter((r) => r.status === 'APPROVED' || tcByReq[r.id]?.length)

  // Function: toggle
  const toggle = (id: string) => setExpanded((prev) => { const next = new Set(prev); next.has(id) ? next.delete(id) : next.add(id); return next })

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-sm font-semibold text-white">Test Plan &amp; Test Cases</h1>
          <p className="text-xs text-gray-500">Grouped by requirement, with a live coverage badge per group.</p>
        </div>
        <button onClick={() => startRun.mutate()} disabled={startRun.isPending || run?.status === 'RUNNING' || run?.status === 'QUEUED'}
          className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-3 py-1.5 shrink-0">
          <PlayCircle size={13} /> {run?.status === 'RUNNING' ? 'Designing…' : 'Run Test Design'}
        </button>
      </div>

      {run?.status === 'FAILED' && <div className="bg-red-500/10 border border-red-500/30 rounded p-3 text-xs text-red-300 mb-4">{run.error}</div>}

      {testPlan && (
        <div className="bg-gray-900 border border-white/10 rounded-lg p-4 mb-4">
          <h2 className="text-xs font-semibold text-white mb-2">{testPlan.title}</h2>
          <p className="text-xs text-gray-400 mb-1"><span className="text-gray-500">Scope:</span> {testPlan.scope}</p>
          <p className="text-xs text-gray-400 mb-1"><span className="text-gray-500">Strategy:</span> {testPlan.strategy}</p>
          <p className="text-xs text-gray-400"><span className="text-gray-500">Environments:</span> {testPlan.environments.join(', ')}</p>
        </div>
      )}

      <div className="space-y-2">
        {approvedRequirements.map((req) => {
          const tcs = tcByReq[req.id] || []
          const isOpen = expanded.has(req.id)
          return (
            <div key={req.id} className="bg-gray-900 border border-white/10 rounded-lg overflow-hidden">
              <button onClick={() => toggle(req.id)} className="w-full flex items-center justify-between px-3 py-2 hover:bg-white/5">
                <span className="flex items-center gap-2 text-xs text-gray-300">
                  {isOpen ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                  <span className="text-blue-400">{req.req_id}</span> {req.title}
                </span>
                <CoverageBadge testCases={tcs} />
              </button>
              {isOpen && (
                <div className="border-t border-white/10 divide-y divide-white/5">
                  {tcs.map((tc) => (
                    <div key={tc.id} className="px-4 py-2">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] text-gray-500">{tc.tc_id}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${TYPE_BADGE[tc.test_type] || ''}`}>{tc.test_type}</span>
                        <span className="text-[10px] text-gray-500">{tc.test_level} · {tc.priority}</span>
                        <span className="text-[10px] text-gray-600 ml-auto">{tc.status}</span>
                      </div>
                      <p className="text-xs text-gray-300">{tc.title}</p>
                      <ol className="mt-1 space-y-0.5">
                        {tc.steps.map((step) => (
                          <li key={step.step_no} className="text-[11px] text-gray-500">
                            {step.step_no}. {step.action} <span className="text-gray-600">→ {step.expected_result}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                  ))}
                  {tcs.length === 0 && <p className="px-4 py-2 text-[11px] text-gray-600">No test cases yet.</p>}
                </div>
              )}
            </div>
          )
        })}
        {approvedRequirements.length === 0 && <p className="text-xs text-gray-600 py-8 text-center">No approved requirements yet.</p>}
      </div>

      {run?.status === 'AWAITING_APPROVAL' && gate?.decision === 'PENDING' && (
        <div className="mt-4 border border-amber-500/30 bg-amber-500/10 rounded-lg px-4 py-3 flex items-center justify-between">
          <p className="text-xs text-amber-300">⚠ {testCases.length} test cases awaiting Test Lead review.</p>
          <div className="flex gap-2">
            <button onClick={() => decideGate.mutate({ decision: 'APPROVED' })} disabled={decideGate.isPending}
              className="text-xs bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-1.5 disabled:opacity-50">Approve &amp; Generate Scripts</button>
            <button
              onClick={() => { const r = window.prompt('Rationale for rejecting (mandatory):'); if (r) decideGate.mutate({ decision: 'REJECTED', rationale: r }) }}
              disabled={decideGate.isPending} className="text-xs bg-red-600/80 hover:bg-red-500 rounded px-3 py-1.5 disabled:opacity-50">Reject</button>
          </div>
        </div>
      )}
    </div>
  )
}
