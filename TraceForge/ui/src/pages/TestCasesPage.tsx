// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (TestCasesPage.tsx)
// Date: 2025-07-13
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, ChevronDown, ChevronRight, Download, FileArchive, FileSpreadsheet, Pencil, PlayCircle, ShieldAlert, X } from 'lucide-react'
import api from '../api/client'
import type { CoverageRequirement, CoverageSummary, Gate, PipelineRun, Requirement, TestCase, TestPlan } from '../api/types'
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
  systems_involved?: string[]
  required_roles?: string[]
  cleanup_instructions?: string[]
}

type ReviewDraft = {
  title: string
  test_type: TestCase['test_type']
  test_level: string
  priority: string
  systems: string
  roles: string
  cleanup: string
  resolution: string
  steps: TestCase['steps']
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
function CoverageBadge({ requirement, testCases, coverage }: Readonly<{ requirement: Requirement; testCases: TestCase[]; coverage?: CoverageRequirement }>) {
  const { positive, negative, edge } = coverageCounts(testCases)
  const covered = coverage?.policy_compliant ?? (positive >= 1 && negative >= 1 && edge >= 1)
  const gapTitle = coverage?.policy_gaps?.join('\n')
  return (
    <span title={gapTitle} className={`text-[10px] ${covered ? 'text-emerald-400' : 'text-red-400'}`}>
      {covered ? '✓' : '⚠'} {testCases.length} total · {positive}P {negative}N {edge}E
    </span>
  )
}

function groupCasesByRequirement(testCases: TestCase[]) {
  const grouped: Record<string, TestCase[]> = {}
  for (const testCase of testCases) {
    grouped[testCase.requirement_id] = grouped[testCase.requirement_id] || []
    grouped[testCase.requirement_id].push(testCase)
  }
  return grouped
}

function coveredRequirementCount(requirements: Requirement[], casesByRequirement: Record<string, TestCase[]>) {
  return requirements.filter((requirement) => {
    const counts = coverageCounts(casesByRequirement[requirement.id] || [])
    return counts.positive >= 1 && counts.negative >= 1 && counts.edge >= 1
  }).length
}

function testDesignButtonLabel(status: PipelineRun['status'] | undefined, completed: number, total: number, hasTestCases: boolean) {
  if (status === 'RUNNING') return `Designing ${completed}/${total}…`
  return hasTestCases ? 'Generate Missing Cases' : 'Run Test Design'
}

// Function: TestCasesPage
export default function TestCasesPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [reviewingCase, setReviewingCase] = useState<TestCase | null>(null)
  const [reviewDraft, setReviewDraft] = useState<ReviewDraft | null>(null)
  const [showBlockedApproval, setShowBlockedApproval] = useState(false)
  const [approvalRationale, setApprovalRationale] = useState('')
  const [approvalAcknowledged, setApprovalAcknowledged] = useState(false)

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
  const { data: coverage } = useQuery<CoverageSummary>({
    queryKey: ['coverage', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/coverage`)).data,
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
  const editTestCase = useMutation({
    mutationFn: async ({ testCase, payload }: { testCase: TestCase; payload: Record<string, unknown> }) => (
      await api.patch(`/testcases/${testCase.id}`, payload)
    ).data,
    onSuccess: () => {
      setReviewingCase(null)
      setReviewDraft(null)
      queryClient.invalidateQueries({ queryKey: ['testcases', projectId] })
    },
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not save the test-case review.'),
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
      if (decision !== 'REJECTED' && automationReadyCases > 0) {
        await api.post(`/projects/${projectId}/runs`, { stage: 'SCRIPT_GEN' })
      }
      return result
    },
    onSuccess: () => {
      setShowBlockedApproval(false)
      setApprovalRationale('')
      setApprovalAcknowledged(false)
      queryClient.invalidateQueries({ queryKey: ['runs', projectId] })
      queryClient.invalidateQueries({ queryKey: ['testcases', projectId] })
      queryClient.invalidateQueries({ queryKey: ['testplan', projectId] })
    },
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Review decision failed.'),
  })

  if (!projectId) return <NoProjectSelected />

  const tcByReq = groupCasesByRequirement(testCases)
  const approvedBaseline = requirements.filter((r) => r.status === 'APPROVED' || tcByReq[r.id]?.length)
  const approvedRequirements = approvedBaseline.filter((r) => (r.acceptance_criteria || []).length > 0)
  const coverageByRequirement = Object.fromEntries(
    (coverage?.requirements || []).map((row) => [row.requirement_id, row]),
  )
  const informationGaps = coverage?.information_gap_requirements ?? (approvedBaseline.length - approvedRequirements.length)
  const coveredRequirements = coverage?.covered_requirements ?? coveredRequirementCount(approvedRequirements, tcByReq)
  const coveragePercent = coverage?.test_design_coverage_pct ?? (approvedBaseline.length
    ? Math.round((coveredRequirements / approvedBaseline.length) * 100)
    : 0)
  const businessReviewCases = testCases.filter(requiresBusinessReview)
  const executionReadyCases = testCases.length - businessReviewCases.length
  const automationReadyCases = testCases.filter((testCase) => {
    const status = caseMetadata(testCase).automation_status || ''
    return status.startsWith('READY_FOR_') && !requiresBusinessReview(testCase)
  }).length
  const approvalReady = testCases.length > 0
    && coveragePercent === 100
    && businessReviewCases.length === 0
  const runButtonLabel = testDesignButtonLabel(run?.status, requirementsCompleted, requirementsTotal, testCases.length > 0)

  const openCaseReview = (testCase: TestCase) => {
    const metadata = caseMetadata(testCase)
    setReviewingCase(testCase)
    setReviewDraft({
      title: testCase.title,
      test_type: testCase.test_type,
      test_level: testCase.test_level,
      priority: testCase.priority,
      systems: (metadata.systems_involved || []).join(', '),
      roles: (metadata.required_roles || []).join(', '),
      cleanup: (metadata.cleanup_instructions || []).join('; '),
      resolution: '',
      steps: testCase.steps.map((step) => ({ ...step })),
    })
  }

  const saveCaseReview = () => {
    if (!reviewingCase || !reviewDraft) return
    editTestCase.mutate({
      testCase: reviewingCase,
      payload: {
        title: reviewDraft.title.trim(),
        test_type: reviewDraft.test_type,
        test_level: reviewDraft.test_level,
        priority: reviewDraft.priority,
        steps: reviewDraft.steps,
        review_metadata: {
          systems_involved: reviewDraft.systems.split(',').map((value) => value.trim()).filter(Boolean),
          required_roles: reviewDraft.roles.split(',').map((value) => value.trim()).filter(Boolean),
          cleanup_instructions: reviewDraft.cleanup.split(';').map((value) => value.trim()).filter(Boolean),
          resolution: reviewDraft.resolution.trim(),
        },
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
          <button type="button" onClick={() => downloadPlan.mutate()} disabled={!testPlan || downloadPlan.isPending}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded px-3 py-1.5">
            <Download size={13} /> {downloadPlan.isPending ? 'Downloading…' : 'Test Plan'}
          </button>
          <button type="button" onClick={() => downloadCases.mutate()} disabled={!testCases.length || downloadCases.isPending}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded px-3 py-1.5">
            <FileSpreadsheet size={13} /> {downloadCases.isPending ? 'Downloading…' : 'Test Cases'}
          </button>
          <button type="button" onClick={() => downloadScripts.mutate()} disabled={downloadScripts.isPending}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded px-3 py-1.5">
            <FileArchive size={13} /> {downloadScripts.isPending ? 'Packaging…' : 'Test Scripts'}
          </button>
          <button type="button" onClick={() => startRun.mutate()} disabled={startRun.isPending || run?.status === 'RUNNING' || run?.status === 'QUEUED'}
            title={testCases.length > 0 ? 'Generate cases only for executable requirements that do not yet have Test Design coverage.' : undefined}
            className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-3 py-1.5 shrink-0">
            <PlayCircle size={13} /> {runButtonLabel}
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
          <p className="text-[10px] text-gray-500">{coveredRequirements} of {approvedBaseline.length} active requirements meet source-driven coverage</p>
          {informationGaps > 0 && <p className="text-[10px] text-amber-500">{informationGaps} unresolved information gap(s) block complete coverage · enrich them in Requirements</p>}
        </div>
        <div className="bg-gray-900 border border-white/10 rounded-lg p-3">
          <p className="text-[10px] text-gray-500 uppercase">Detailed test cases</p>
          <p className="text-lg text-white">{testCases.length}</p>
          <p className="text-[10px] text-gray-500">{testCases.filter((testCase) => testCase.status === 'APPROVED').length} approved scenarios across the generated test levels</p>
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
              <button type="button" onClick={() => toggle(req.id)} className="w-full flex items-center justify-between px-3 py-2 hover:bg-white/5">
                <span className="flex items-center gap-2 text-xs text-gray-300">
                  {isOpen ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                  <span className="text-blue-400">{req.req_id}</span> {req.title}
                </span>
                <CoverageBadge requirement={req} testCases={tcs} coverage={coverageByRequirement[req.id]} />
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
                        <button type="button" onClick={() => openCaseReview(tc)} disabled={editTestCase.isPending}
                          className="flex items-center gap-1 text-[10px] rounded border border-white/15 px-2 py-0.5 text-gray-300 hover:bg-white/5 disabled:opacity-50">
                          <Pencil size={10} /> Review case
                        </button>
                      </div>
                      <p className="text-xs text-gray-300">{tc.title}</p>
                      <ol className="mt-1 list-inside list-decimal space-y-0.5">
                        {tc.steps.map((step) => (
                          <li key={step.step_no} className="text-[11px] text-gray-500">
                            {step.action} <span className="text-gray-600">→ {step.expected_result}</span>
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
            <button type="button" onClick={() => decideGate.mutate({ decision: 'APPROVED' })} disabled={decideGate.isPending || !approvalReady}
              title={!approvalReady ? 'Resolve all business-review and automation-readiness blockers before script generation.' : undefined}
              className="text-xs bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-1.5 disabled:opacity-50">
              Approve{automationReadyCases > 0 ? ' & Generate Scripts' : ' Test Design'}
            </button>
            {businessReviewCases.length > 0 && (
              <button type="button" onClick={() => setShowBlockedApproval(true)} disabled={decideGate.isPending}
                className="flex items-center gap-1 text-xs border border-amber-500/50 text-amber-700 hover:bg-amber-500/10 rounded px-3 py-1.5 disabled:opacity-50">
                <ShieldAlert size={13} /> Approve with blockers
              </button>
            )}
            <button
              type="button"
              onClick={() => { const r = window.prompt('Rationale for rejecting (mandatory):'); if (r) decideGate.mutate({ decision: 'REJECTED', rationale: r }) }}
              disabled={decideGate.isPending} className="text-xs bg-red-600/80 hover:bg-red-500 rounded px-3 py-1.5 disabled:opacity-50">Reject</button>
          </div>
        </div>
      )}

      {reviewingCase && reviewDraft && (
        <dialog open className="fixed inset-0 z-50 flex h-full max-h-none w-full max-w-none items-center justify-center bg-black/70 p-4 text-left" aria-label={`Review ${reviewingCase.tc_id}`}>
          <div className="max-h-[92vh] w-full max-w-5xl overflow-y-auto rounded-lg border border-white/15 bg-gray-950 shadow-2xl">
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-white/10 bg-gray-950 px-5 py-4">
              <div>
                <p className="text-xs font-semibold text-white">Review {reviewingCase.tc_id}</p>
                <p className="mt-1 text-[11px] text-gray-500">Resolve business decisions and replace blocked execution details only when they are known.</p>
              </div>
              <button type="button" onClick={() => { setReviewingCase(null); setReviewDraft(null) }} title="Close review editor" className="rounded p-1 text-gray-400 hover:bg-white/10 hover:text-white">
                <X size={16} />
              </button>
            </div>

            <div className="space-y-5 p-5">
              <div className="grid gap-3 md:grid-cols-4">
                <label className="md:col-span-4 text-[11px] text-gray-400"><span>Title</span>
                  <input value={reviewDraft.title} onChange={(event) => setReviewDraft({ ...reviewDraft, title: event.target.value })}
                    className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white outline-none focus:border-blue-500" />
                </label>
                <label className="text-[11px] text-gray-400"><span>Type</span>
                  <select value={reviewDraft.test_type} onChange={(event) => setReviewDraft({ ...reviewDraft, test_type: event.target.value as TestCase['test_type'] })}
                    className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white">
                    {Object.keys(TYPE_LABEL).map((value) => <option key={value}>{value}</option>)}
                  </select>
                </label>
                <label className="text-[11px] text-gray-400"><span>Level</span>
                  <select value={reviewDraft.test_level} onChange={(event) => setReviewDraft({ ...reviewDraft, test_level: event.target.value })}
                    className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white">
                    {['UNIT', 'API', 'UI_E2E', 'INTEGRATION', 'UAT'].map((value) => <option key={value}>{value}</option>)}
                  </select>
                </label>
                <label className="text-[11px] text-gray-400"><span>Priority</span>
                  <select value={reviewDraft.priority} onChange={(event) => setReviewDraft({ ...reviewDraft, priority: event.target.value })}
                    className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white">
                    {['P1', 'P2', 'P3'].map((value) => <option key={value}>{value}</option>)}
                  </select>
                </label>
                <div className="rounded border border-white/10 bg-gray-900 px-3 py-2">
                  <p className="text-[10px] uppercase text-gray-500">Automation</p>
                  <p className="mt-1 text-xs text-amber-600">{caseMetadata(reviewingCase).automation_status || 'Not classified'}</p>
                </div>
              </div>

              <div>
                <p className="mb-2 text-[10px] uppercase text-gray-500">Execution steps</p>
                <div className="space-y-3">
                  {reviewDraft.steps.map((step, index) => (
                    <div key={step.step_no} className="grid gap-2 border-l-2 border-white/10 pl-3 md:grid-cols-2">
                      <label className="text-[11px] text-gray-400"><span>Step {step.step_no} action</span>
                        <textarea rows={3} value={step.action} onChange={(event) => {
                          const steps = reviewDraft.steps.map((value, stepIndex) => stepIndex === index ? { ...value, action: event.target.value } : value)
                          setReviewDraft({ ...reviewDraft, steps })
                        }} className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-gray-200 outline-none focus:border-blue-500" />
                      </label>
                      <label className="text-[11px] text-gray-400"><span>Expected result</span>
                        <textarea rows={3} value={step.expected_result} onChange={(event) => {
                          const steps = reviewDraft.steps.map((value, stepIndex) => stepIndex === index ? { ...value, expected_result: event.target.value } : value)
                          setReviewDraft({ ...reviewDraft, steps })
                        }} className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-gray-200 outline-none focus:border-blue-500" />
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-3">
                <label className="text-[11px] text-gray-400"><span>Systems involved</span>
                  <input value={reviewDraft.systems} onChange={(event) => setReviewDraft({ ...reviewDraft, systems: event.target.value })} placeholder="Comma-separated systems"
                    className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white" />
                </label>
                <label className="text-[11px] text-gray-400"><span>Execution roles</span>
                  <input value={reviewDraft.roles} onChange={(event) => setReviewDraft({ ...reviewDraft, roles: event.target.value })} placeholder="Comma-separated roles"
                    className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white" />
                </label>
                <label className="text-[11px] text-gray-400"><span>Cleanup / reversal</span>
                  <input value={reviewDraft.cleanup} onChange={(event) => setReviewDraft({ ...reviewDraft, cleanup: event.target.value })} placeholder="Semicolon-separated steps"
                    className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white" />
                </label>
              </div>

              {(caseMetadata(reviewingCase).ambiguities?.length || caseMetadata(reviewingCase).assumptions?.length) ? (
                <div className="rounded border border-amber-500/25 bg-amber-500/5 p-3">
                  <p className="text-[10px] uppercase text-amber-600">Decisions required</p>
                  {[...(caseMetadata(reviewingCase).ambiguities || []), ...(caseMetadata(reviewingCase).assumptions || [])].map((item) => (
                    <p key={item} className="mt-1 text-[11px] text-gray-300">{item}</p>
                  ))}
                </div>
              ) : null}
              <label className="block text-[11px] text-gray-400"><span>Review resolution</span>
                <textarea rows={3} value={reviewDraft.resolution} onChange={(event) => setReviewDraft({ ...reviewDraft, resolution: event.target.value })}
                  placeholder="Record the business decision and evidence used to resolve the listed ambiguity or assumption."
                  className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white outline-none focus:border-blue-500" />
              </label>
            </div>

            <div className="sticky bottom-0 flex justify-end gap-2 border-t border-white/10 bg-gray-950 px-5 py-4">
              <button type="button" onClick={() => { setReviewingCase(null); setReviewDraft(null) }} className="rounded border border-white/15 px-3 py-2 text-xs text-gray-300 hover:bg-white/5">Cancel</button>
              <button type="button" onClick={saveCaseReview} disabled={editTestCase.isPending || !reviewDraft.title.trim() || !reviewDraft.systems.trim() || !reviewDraft.roles.trim() || !reviewDraft.cleanup.trim()}
                className="flex items-center gap-1 rounded bg-blue-600 px-3 py-2 text-xs text-white hover:bg-blue-500 disabled:opacity-40">
                <CheckCircle2 size={13} /> {editTestCase.isPending ? 'Saving…' : 'Save review'}
              </button>
            </div>
          </div>
        </dialog>
      )}

      {showBlockedApproval && (
        <dialog open className="fixed inset-0 z-50 flex h-full max-h-none w-full max-w-none items-center justify-center bg-black/70 p-4 text-left" aria-label="Approve Test Design with blockers">
          <div className="w-full max-w-xl rounded-lg border border-amber-500/30 bg-gray-950 shadow-2xl">
            <div className="flex items-start gap-3 border-b border-white/10 p-5">
              <ShieldAlert className="mt-0.5 shrink-0 text-amber-600" size={20} />
              <div>
                <h2 className="text-sm font-semibold text-white">Approve Test Design with blockers</h2>
                <p className="mt-1 text-xs leading-5 text-gray-400">
                  This accepts all {testCases.length} cases as reviewed test assets. {businessReviewCases.length} blocked or manual cases remain non-automatable and will not produce scripts.
                </p>
              </div>
            </div>
            <div className="space-y-4 p-5">
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="rounded border border-white/10 bg-gray-900 p-3"><p className="text-lg text-white">{testCases.length}</p><p className="text-[10px] text-gray-500">Reviewed cases</p></div>
                <div className="rounded border border-amber-500/20 bg-amber-500/5 p-3"><p className="text-lg text-amber-600">{businessReviewCases.length}</p><p className="text-[10px] text-gray-500">Remain blocked</p></div>
                <div className="rounded border border-emerald-500/20 bg-emerald-500/5 p-3"><p className="text-lg text-emerald-400">{automationReadyCases}</p><p className="text-[10px] text-gray-500">Scripts eligible</p></div>
              </div>
              <label className="block text-[11px] text-gray-400"><span>Approval rationale <span className="text-red-400">required</span></span>
                <textarea rows={4} value={approvalRationale} onChange={(event) => setApprovalRationale(event.target.value)}
                  placeholder="Explain why the Test Design is acceptable and how the outstanding execution bindings will be governed."
                  className="mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white outline-none focus:border-amber-500" />
              </label>
              <label className="flex items-start gap-2 text-[11px] leading-5 text-gray-300">
                <input type="checkbox" checked={approvalAcknowledged} onChange={(event) => setApprovalAcknowledged(event.target.checked)} className="mt-1" />
                <span>I acknowledge that blocked cases remain non-executable, their automation status is unchanged, and scripts are generated only for independently verified automation-ready cases.</span>
              </label>
            </div>
            <div className="flex justify-end gap-2 border-t border-white/10 px-5 py-4">
              <button type="button" onClick={() => setShowBlockedApproval(false)} className="rounded border border-white/15 px-3 py-2 text-xs text-gray-300 hover:bg-white/5">Cancel</button>
              <button type="button" onClick={() => decideGate.mutate({ decision: 'APPROVED_WITH_COMMENTS', rationale: approvalRationale.trim() })}
                disabled={decideGate.isPending || !approvalAcknowledged || !approvalRationale.trim()}
                className="rounded bg-amber-600 px-3 py-2 text-xs font-medium text-gray-950 hover:bg-amber-500 disabled:opacity-40">
                {decideGate.isPending ? 'Recording decision…' : 'Approve with blockers'}
              </button>
            </div>
          </div>
        </dialog>
      )}
    </div>
  )
}
