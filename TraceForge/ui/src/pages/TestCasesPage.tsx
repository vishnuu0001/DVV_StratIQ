// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (TestCasesPage.tsx)
// Date: 2025-07-13
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, ChevronRight, Download, FileArchive, FileSpreadsheet, PlayCircle } from 'lucide-react'
import api from '../api/client'
import type { Gate, PipelineRun, Requirement, TestCase, TestPlan } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

const TYPE_BADGE: Record<string, string> = {
  POSITIVE: 'bg-emerald-500/20 text-emerald-300', NEGATIVE: 'bg-red-500/20 text-red-300',
  EDGE: 'bg-amber-500/20 text-amber-300', BOUNDARY: 'bg-purple-500/20 text-purple-300',
  NEGATIVE_SECURITY: 'bg-red-600/30 text-red-300', PERFORMANCE: 'bg-cyan-500/20 text-cyan-300',
}

const TYPE_LABEL: Record<string, string> = {
  POSITIVE: 'positive', NEGATIVE: 'negative', EDGE: 'edge', BOUNDARY: 'boundary',
  NEGATIVE_SECURITY: 'security', PERFORMANCE: 'performance',
}

const NEGATIVE_EVIDENCE = /\b(block(?:ed|s|ing)?|prevent(?:ed|s|ing)?|reject(?:ed|s|ing)?|cannot|must not|not allowed|den(?:y|ied)|invalid|imbalance|without|unless|failed?|unauthori[sz]ed|returned? in full)\b/i

function requiresNegativeScenario(requirement: Requirement) {
  return NEGATIVE_EVIDENCE.test([
    requirement.title,
    requirement.statement,
    ...(requirement.acceptance_criteria || []),
  ].join(' '))
}

function coverageCounts(testCases: TestCase[]) {
  const positive = testCases.filter((tc) => tc.test_type === 'POSITIVE').length
  const directNegative = testCases.filter((tc) => tc.test_type === 'NEGATIVE').length
  const security = testCases.filter((tc) => tc.test_type === 'NEGATIVE_SECURITY').length
  const edge = testCases.filter((tc) => tc.test_type === 'EDGE').length
  return { positive, directNegative, security, negative: directNegative + security, edge }
}

type CaseMetadata = {
  automation_status?: string
  automation_blockers?: string[]
  ambiguities?: string[]
  assumptions?: string[]
}

function caseMetadata(testCase: TestCase): CaseMetadata {
  const raw = testCase.gherkin?.trim()
  if (!raw?.startsWith('{')) return {}
  try {
    return JSON.parse(raw) as CaseMetadata
  } catch {
    return {}
  }
}

function requiresBusinessReview(testCase: TestCase) {
  const metadata = caseMetadata(testCase)
  const assumptions = (metadata.assumptions || []).join(' ').toLowerCase()
  return Boolean(
    metadata.automation_status === 'AUTOMATION_BLOCKED'
    || metadata.ambiguities?.length
    || assumptions.includes('pending')
    || assumptions.includes('review')
    || testCase.steps.some((step) => step.action.includes('[EXECUTION DETAIL BLOCKED'))
  )
}

function hasDecisionBlocker(testCase: TestCase) {
  const metadata = caseMetadata(testCase)
  const assumptions = (metadata.assumptions || []).join(' ').toLowerCase()
  return Boolean(
    metadata.ambiguities?.length
    || assumptions.includes('pending')
    || assumptions.includes('review')
  )
}

function saveDownload(data: BlobPart, disposition: string | undefined, fallback: string) {
  const match = disposition?.match(/filename="?([^";]+)"?/i)
  const url = URL.createObjectURL(new Blob([data]))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = match?.[1] || fallback
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

// Function: CoverageBadge
function CoverageBadge({ requirement, testCases }: { requirement: Requirement; testCases: TestCase[] }) {
  const { positive, negative, edge } = coverageCounts(testCases)
  const covered = positive >= 1 && (!requiresNegativeScenario(requirement) || negative >= 1)
  return (
    <span className={`text-[10px] ${covered ? 'text-emerald-400' : 'text-red-400'}`}>
      {covered ? '✓' : '⚠'} {testCases.length} total · {positive}P {negative}N {edge}E
    </span>
  )
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
  const testDesignRuns = runs.filter((r) => r.stage === 'TEST_DESIGN').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))
  const run = testDesignRuns.find((item) => ['QUEUED', 'RUNNING', 'AWAITING_APPROVAL'].includes(item.status)) || testDesignRuns[0]
  const requirementsCompleted = Number(run?.stats?.requirements_completed || 0)
  const requirementsTotal = Number(run?.stats?.requirements_total || requirements.length)
  const { data: gate } = useQuery<Gate>({
    queryKey: ['gate', run?.id],
    queryFn: async () => (await api.get(`/runs/${run!.id}/gate`)).data,
    enabled: !!run && run.status === 'AWAITING_APPROVAL',
  })

  const startRun = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/runs`, { stage: 'TEST_DESIGN' })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['runs', projectId] }),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not start Test Design.'),
  })
  const resetTestDesign = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/reset-test-design`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['testcases', projectId] })
      queryClient.invalidateQueries({ queryKey: ['testplan', projectId] })
      queryClient.invalidateQueries({ queryKey: ['runs', projectId] })
    },
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not reset Test Design.'),
  })
  const resolveReviewMetadata = useMutation({
    mutationFn: async ({ testCase, reviewMetadata }: { testCase: TestCase; reviewMetadata: Record<string, unknown> }) => (
      await api.patch(`/testcases/${testCase.id}`, { review_metadata: reviewMetadata })
    ).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['testcases', projectId] }),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not save review metadata.'),
  })
  const downloadPlan = useMutation({
    mutationFn: async () => api.get(`/projects/${projectId}/test-plan/download`, { responseType: 'blob' }),
    onSuccess: (response) => saveDownload(
      response.data, response.headers['content-disposition'], 'test-plan.md',
    ),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not download the Test Plan.'),
  })
  const downloadCases = useMutation({
    mutationFn: async () => api.get(`/projects/${projectId}/testcases/download`, { responseType: 'blob' }),
    onSuccess: (response) => saveDownload(
      response.data, response.headers['content-disposition'], 'test-cases.xlsx',
    ),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not download Test Cases.'),
  })
  const downloadScripts = useMutation({
    mutationFn: async () => api.get(`/projects/${projectId}/scripts/download`, { responseType: 'blob' }),
    onSuccess: (response) => saveDownload(
      response.data, response.headers['content-disposition'], 'playwright-test-scripts.zip',
    ),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not download Test Scripts.'),
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
  const approvedBaseline = requirements.filter((r) => r.status === 'APPROVED' || tcByReq[r.id]?.length)
  const approvedRequirements = approvedBaseline.filter((r) => r.level !== 'ASSUMPTION' && (r.acceptance_criteria || []).length > 0)
  const informationGaps = approvedBaseline.length - approvedRequirements.length
  const coveredRequirements = approvedRequirements.filter((req) => {
    const cases = tcByReq[req.id] || []
    const counts = coverageCounts(cases)
    return counts.positive >= 1
      && (!requiresNegativeScenario(req) || counts.negative >= 1)
  }).length
  const coveragePercent = approvedRequirements.length
    ? Math.round((coveredRequirements / approvedRequirements.length) * 100)
    : 0
  const businessReviewCases = testCases.filter(requiresBusinessReview)
  const executionReadyCases = testCases.length - businessReviewCases.length
  const automationReadyCases = testCases.filter((testCase) => {
    const status = caseMetadata(testCase).automation_status || ''
    return status.startsWith('READY_FOR_') && !requiresBusinessReview(testCase)
  }).length
  const approvalReady = testCases.length > 0
    && coveragePercent === 100
    && businessReviewCases.length === 0

  const resolveCaseReview = (testCase: TestCase) => {
    const metadata = caseMetadata(testCase)
    const systems = window.prompt(
      'Confirmed systems involved (comma-separated)',
      ((metadata as any).systems_involved || []).join(', '),
    )
    if (!systems?.trim()) return
    const roles = window.prompt(
      'Confirmed execution roles (comma-separated)',
      ((metadata as any).required_roles || []).join(', '),
    )
    if (!roles?.trim()) return
    const cleanup = window.prompt(
      'Confirmed cleanup/reversal sequence (one or more steps)',
      ((metadata as any).cleanup_instructions || []).join('; '),
    )
    if (!cleanup?.trim()) return
    const resolution = window.prompt(
      'Document the business decision resolving every listed ambiguity/assumption',
      '',
    )
    if (!resolution?.trim()) return
    resolveReviewMetadata.mutate({
      testCase,
      reviewMetadata: {
        systems_involved: systems.split(',').map((value) => value.trim()).filter(Boolean),
        required_roles: roles.split(',').map((value) => value.trim()).filter(Boolean),
        cleanup_instructions: cleanup.split(';').map((value) => value.trim()).filter(Boolean),
        resolution: resolution.trim(),
      },
    })
  }

  // Function: toggle
  const toggle = (id: string) => setExpanded((prev) => { const next = new Set(prev); next.has(id) ? next.delete(id) : next.add(id); return next })

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-sm font-semibold text-white">Test Plan &amp; Test Cases</h1>
          <p className="text-xs text-gray-500">Grouped by requirement, with a live coverage badge per group.</p>
        </div>
        <div className="flex flex-wrap justify-end gap-2">
          <button onClick={() => downloadPlan.mutate()} disabled={!testPlan || downloadPlan.isPending}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded px-3 py-1.5">
            <Download size={13} /> {downloadPlan.isPending ? 'Downloading…' : 'Test Plan'}
          </button>
          <button onClick={() => downloadCases.mutate()} disabled={!testCases.length || downloadCases.isPending}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded px-3 py-1.5">
            <FileSpreadsheet size={13} /> {downloadCases.isPending ? 'Downloading…' : 'Test Cases'}
          </button>
          <button onClick={() => downloadScripts.mutate()} disabled={downloadScripts.isPending}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded px-3 py-1.5">
            <FileArchive size={13} /> {downloadScripts.isPending ? 'Packaging…' : 'Test Scripts'}
          </button>
          <button onClick={() => startRun.mutate()} disabled={startRun.isPending || testCases.length > 0 || run?.status === 'RUNNING' || run?.status === 'QUEUED'}
            title={testCases.length > 0 ? 'Test Design is replacement-based. Archive/reset the existing inventory before redesigning.' : undefined}
            className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-3 py-1.5 shrink-0">
            <PlayCircle size={13} /> {run?.status === 'RUNNING'
              ? `Designing ${requirementsCompleted}/${requirementsTotal}…`
              : 'Run Test Design'}
          </button>
          {testCases.length > 0 && (
            <button type="button" disabled={resetTestDesign.isPending || run?.status === 'RUNNING' || run?.status === 'QUEUED'}
              onClick={() => {
                const confirmation = window.prompt('Type RESET TEST DESIGN to remove only Test Plans, Test Cases, and Test Scripts. Sources and requirements are retained.')
                if (confirmation === 'RESET TEST DESIGN') resetTestDesign.mutate()
              }}
              className="text-xs border border-amber-500/40 text-amber-600 hover:bg-amber-500/10 disabled:opacity-50 rounded px-3 py-1.5">
              {resetTestDesign.isPending ? 'Resetting…' : 'Reset Test Design'}
            </button>
          )}
        </div>
      </div>

      {run?.status === 'RUNNING' && (
        <div className="bg-blue-500/10 border border-blue-500/30 rounded p-3 text-xs text-blue-200 mb-4">
          Ollama is generating evidence-backed requirement matrices in bounded per-requirement batches.
          Completed {requirementsCompleted} of {requirementsTotal}; {Number(run.stats?.test_cases_created || 0)} test cases committed.
        </div>
      )}

      {run?.status === 'FAILED' && testCases.length === 0 && !startRun.isPending && (
        <div className="bg-red-500/10 border border-red-500/30 rounded p-3 text-xs text-red-300 mb-4">{run.error}</div>
      )}

      {testPlan && (
        <div className="bg-gray-900 border border-white/10 rounded-lg p-4 mb-4">
          <h2 className="text-xs font-semibold text-white mb-2">{testPlan.title}</h2>
          <p className="text-xs text-gray-400 mb-1"><span className="text-gray-500">Scope:</span> {testPlan.scope}</p>
          <p className="text-xs text-gray-400 mb-1"><span className="text-gray-500">Strategy:</span> {testPlan.strategy}</p>
          <p className="text-xs text-gray-400"><span className="text-gray-500">Environments:</span> {testPlan.environments.join(', ')}</p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-3 border-t border-white/10 pt-3">
            {[
              ['Objectives', testPlan.schedule.objectives],
              ['Process coverage', testPlan.schedule.process_stages],
              ['Test levels', testPlan.schedule.test_levels],
              ['Test types', testPlan.schedule.test_types],
              ['Data strategy', testPlan.schedule.test_data_strategy],
              ['Automation strategy', testPlan.schedule.automation_strategy],
              ['Risks', testPlan.schedule.risks],
              ['Deliverables', testPlan.schedule.deliverables],
            ].map(([label, raw]) => {
              const values = Array.isArray(raw) ? raw.map(String) : []
              return values.length ? (
                <div key={String(label)}>
                  <p className="text-[10px] uppercase text-gray-500 mb-1">{String(label)}</p>
                  <ul className="space-y-1">{values.map((value) => <li key={value} className="text-[10px] text-gray-400">• {value}</li>)}</ul>
                </div>
              ) : null
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="bg-gray-900 border border-white/10 rounded-lg p-3">
          <p className="text-[10px] text-gray-500 uppercase">Scenario traceability</p>
          <p className="text-lg text-white">{coveragePercent}%</p>
          <p className="text-[10px] text-gray-500">{coveredRequirements} of {approvedRequirements.length} testable requirements meet source-driven coverage</p>
          {informationGaps > 0 && <p className="text-[10px] text-amber-500">{informationGaps} information-gap assumption(s) excluded from executable coverage</p>}
        </div>
        <div className="bg-gray-900 border border-white/10 rounded-lg p-3">
          <p className="text-[10px] text-gray-500 uppercase">Detailed test cases</p>
          <p className="text-lg text-white">{testCases.length}</p>
          <p className="text-[10px] text-gray-500">Draft scenarios across the generated test levels</p>
        </div>
        <div className="bg-gray-900 border border-white/10 rounded-lg p-3">
          <p className="text-[10px] text-gray-500 uppercase">Execution / automation ready</p>
          <p className="text-lg text-white">{executionReadyCases} / {automationReadyCases}</p>
          <p className="text-[10px] text-gray-500">of {testCases.length} cases; blocked drafts never count as ready</p>
        </div>
        <div className="bg-gray-900 border border-white/10 rounded-lg p-3">
          <p className="text-[10px] text-gray-500 uppercase">Scenario breadth</p>
          <p className="text-lg text-white">{new Set(testCases.map((tc) => tc.test_type)).size} types</p>
          <p className="text-[10px] text-gray-500">
            {Array.from(new Set(testCases.map((tc) => TYPE_LABEL[tc.test_type] || tc.test_type.toLowerCase()))).join(', ') || 'No scenarios generated'}
          </p>
        </div>
      </div>

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
                <CoverageBadge requirement={req} testCases={tcs} />
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
                        {hasDecisionBlocker(tc) && (
                          <button type="button" onClick={() => resolveCaseReview(tc)} disabled={resolveReviewMetadata.isPending}
                            className="text-[10px] rounded border border-amber-500/40 px-2 py-0.5 text-amber-700 hover:bg-amber-500/10 disabled:opacity-50">
                            Resolve review metadata
                          </button>
                        )}
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
        <div className="mt-4 border border-amber-500/30 bg-amber-500/10 rounded-lg px-4 py-3 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs text-amber-300">⚠ {testCases.length} test cases awaiting Test Lead review.</p>
            {businessReviewCases.length > 0 && (
              <p className="mt-1 text-[11px] text-amber-700">
                {businessReviewCases.length} case(s) remain DRAFT/Pending Business Review because application actions,
                roles, selectors, interfaces, test-data isolation, cleanup, or source ambiguities are unresolved.
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <button onClick={() => decideGate.mutate({ decision: 'APPROVED' })} disabled={decideGate.isPending || !approvalReady}
              title={!approvalReady ? 'Resolve all business-review and automation-readiness blockers before script generation.' : undefined}
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
