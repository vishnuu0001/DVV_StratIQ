// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (ScriptsPage.tsx)
// Date: 2026-05-24
// ---------------------------------------------------------------------------
import { useEffect, useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { CheckCircle2, Download, FileArchive, GitPullRequest, Pencil, PlayCircle, Save, Settings2, X, XCircle } from 'lucide-react'
import api from '../api/client'
import type { CoverageSummary, Gate, PipelineRun, TestCase, TestScript } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

// Function: saveDownload
function saveDownload(data: BlobPart, disposition: string | undefined, fallback: string) {
  const match = disposition?.match(/filename="?([^";]+)"?/i)
  const filename = match?.[1] || fallback
  const url = URL.createObjectURL(new Blob([data]))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

function compileStatusClass(compiles: boolean | null) {
  if (compiles === true) return 'bg-emerald-500/10 text-emerald-300'
  if (compiles === false) return 'bg-red-500/10 text-red-300'
  return 'bg-gray-800 text-gray-500'
}

function compileStatusText(script: TestScript) {
  if (script.compiles === true) return 'Compiles cleanly'
  if (script.compiles === false) return script.validation_output || 'Does not compile'
  return 'Not validated'
}

type AutomationDraft = {
  baseUrl: string
  authMethod: string
  locators: string
  assertions: string
  testDataFactory: string
  cleanup: string
  workerIsolation: boolean
}

const EMPTY_AUTOMATION_DRAFT: AutomationDraft = {
  baseUrl: '', authMethod: '', locators: '{}', assertions: '{}',
  testDataFactory: '', cleanup: '', workerIsolation: false,
}

function isBindableUiCase(testCase: TestCase) {
  if (testCase.status !== 'APPROVED' || testCase.test_level !== 'UI_E2E') return false
  if (testCase.steps.some((step) => (
    step.action.includes('[EXECUTION DETAIL BLOCKED')
    || step.expected_result.includes('[PENDING BUSINESS CONFIRMATION')
  ))) return false
  return true
}

function automationBindingTemplate(cases: TestCase[]) {
  const locators = Object.fromEntries(cases.flatMap((testCase) => testCase.steps.map((step) => [step.action, ''])))
  const assertions = Object.fromEntries(cases.flatMap((testCase) => testCase.steps.map((step) => [step.expected_result, ''])))
  return {
    locators: JSON.stringify(locators, null, 2),
    assertions: JSON.stringify(assertions, null, 2),
  }
}

function scriptGenerationTitle(testDesignApproved: boolean, candidateCount: number, automationReadyCount: number | undefined) {
  if (!testDesignApproved) return 'Approve Test Design before generating scripts.'
  if (candidateCount === 0) return 'No approved test cases are available.'
  if (automationReadyCount === 0) return 'Generate traceable scripts now; runtime UI bindings can be supplied later.'
  return 'Generate scripts for all approved cases.'
}

function AutomationSetupDialog({
  candidates, selectedCaseIds, draft, pending, result, onChange, onToggleCase, onApply, onReviewCases, onClose,
}: Readonly<{
  candidates: TestCase[]
  selectedCaseIds: string[]
  draft: AutomationDraft
  pending: boolean
  result: string | null
  onChange: (draft: AutomationDraft) => void
  onToggleCase: (testCaseId: string) => void
  onApply: () => void
  onReviewCases: () => void
  onClose: () => void
}>) {
  const inputClass = 'mt-1 w-full rounded border border-white/10 bg-gray-900 px-3 py-2 text-xs text-white outline-none focus:border-blue-500'
  const complete = draft.baseUrl.trim() && draft.authMethod.trim() && draft.testDataFactory.trim() && draft.cleanup.trim()
  const selectedLabel = `${selectedCaseIds.length} ${selectedCaseIds.length === 1 ? 'Case' : 'Cases'}`
  return (
    <dialog open className="fixed inset-0 z-50 flex h-full max-h-none w-full max-w-none items-center justify-center bg-black/70 p-4 text-left" aria-label="Configure UI automation">
      <div className="max-h-[92vh] w-full max-w-3xl overflow-y-auto rounded-lg border border-white/15 bg-gray-950 shadow-2xl">
        <div className="sticky top-0 flex items-center justify-between border-b border-white/10 bg-gray-950 px-5 py-4">
          <div>
            <p className="text-sm font-semibold text-white">Configure UI automation</p>
            <p className="mt-1 text-[11px] text-gray-500">Select reviewed UI cases, then supply their real non-secret Playwright bindings.</p>
          </div>
          <button type="button" onClick={onClose} title="Close automation setup" className="rounded p-1 text-gray-400 hover:bg-white/10 hover:text-white"><X size={16} /></button>
        </div>
        <div className="space-y-4 p-5">
          {candidates.length === 0 && (
            <div className="flex items-center justify-between gap-4 rounded border border-amber-500/25 bg-amber-500/5 p-3">
              <p className="text-xs text-amber-300">No bindable UI cases are available. Replace every blocked or pending execution step with reviewed application details first.</p>
              <button type="button" onClick={onReviewCases} className="shrink-0 rounded border border-amber-500/40 px-3 py-1.5 text-xs text-amber-300 hover:bg-amber-500/10">Review UI Cases</button>
            </div>
          )}
          {candidates.length > 0 && (
            <fieldset className="rounded border border-white/10 bg-gray-900/60 p-3">
              <legend className="px-1 text-[10px] uppercase text-gray-500">UI cases to automate</legend>
              <div className="max-h-40 space-y-2 overflow-y-auto">
                {candidates.map((testCase) => (
                  <label key={testCase.id} className="flex items-start gap-2 text-xs text-gray-300">
                    <input type="checkbox" checked={selectedCaseIds.includes(testCase.id)} onChange={() => onToggleCase(testCase.id)} className="mt-0.5" />
                    <span><span className="text-blue-300">{testCase.tc_id}</span> {testCase.title}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          )}
          <div className="grid gap-3 md:grid-cols-2">
            <label className="text-[11px] text-gray-400"><span>Test environment base URL</span>
              <input type="url" value={draft.baseUrl} onChange={(event) => onChange({ ...draft, baseUrl: event.target.value })} placeholder="https://test.example.com" className={inputClass} />
            </label>
            <label className="text-[11px] text-gray-400"><span>Authentication method</span>
              <input value={draft.authMethod} onChange={(event) => onChange({ ...draft, authMethod: event.target.value })} placeholder="Playwright storage state (no credentials)" className={inputClass} />
            </label>
            <label className="text-[11px] text-gray-400"><span>Test-data factory contract</span>
              <input value={draft.testDataFactory} onChange={(event) => onChange({ ...draft, testDataFactory: event.target.value })} placeholder="Worker-scoped API fixture" className={inputClass} />
            </label>
            <label className="text-[11px] text-gray-400"><span>Cleanup contract</span>
              <input value={draft.cleanup} onChange={(event) => onChange({ ...draft, cleanup: event.target.value })} placeholder="Delete fixture records through test API" className={inputClass} />
            </label>
          </div>
          <label className="block text-[11px] text-gray-400"><span>Stable locator map (JSON)</span>
            <textarea rows={6} value={draft.locators} onChange={(event) => onChange({ ...draft, locators: event.target.value })} placeholder={'{"Submit order":"[data-testid=submit-order]"}'} className={`${inputClass} font-mono`} />
          </label>
          <label className="block text-[11px] text-gray-400"><span>Assertion selector map (JSON)</span>
            <textarea rows={6} value={draft.assertions} onChange={(event) => onChange({ ...draft, assertions: event.target.value })} placeholder={'{"Order is accepted":"[data-testid=order-status]"}'} className={`${inputClass} font-mono`} />
          </label>
          <label className="flex items-center gap-2 text-xs text-gray-300">
            <input type="checkbox" checked={draft.workerIsolation} onChange={(event) => onChange({ ...draft, workerIsolation: event.target.checked })} />
            <span>Worker-isolated test data is provisioned for shared business state</span>
          </label>
          <p className="text-[11px] text-gray-500">Credentials and tokens are not accepted or stored. Configure secrets in the Playwright execution environment.</p>
          {result && <p className="rounded border border-white/10 bg-gray-900 p-3 text-xs text-gray-300">{result}</p>}
        </div>
        <div className="sticky bottom-0 flex justify-end gap-2 border-t border-white/10 bg-gray-950 px-5 py-4">
          <button type="button" onClick={onClose} className="rounded border border-white/15 px-3 py-2 text-xs text-gray-300 hover:bg-white/5">Cancel</button>
          <button type="button" onClick={onApply} disabled={!complete || selectedCaseIds.length === 0 || pending}
            className="rounded bg-blue-600 px-3 py-2 text-xs text-white hover:bg-blue-500 disabled:opacity-40">
            {pending ? 'Verifying…' : `Verify & Enable ${selectedLabel}`}
          </button>
        </div>
      </div>
    </dialog>
  )
}

function useScriptSelectionSync(
  scripts: TestScript[],
  selected: TestScript | null,
  editingScript: boolean,
  setSelected: Dispatch<SetStateAction<TestScript | null>>,
  setScriptDraft: Dispatch<SetStateAction<string>>,
) {
  useEffect(() => {
    if (!selected && scripts.length) {
      setSelected(scripts[0])
      setScriptDraft(scripts[0].code)
    }
    if (selected) {
      const refreshed = scripts.find((script) => script.id === selected.id)
      if (refreshed && refreshed !== selected && !editingScript) {
        setSelected(refreshed)
        setScriptDraft(refreshed.code)
      }
    }
  }, [editingScript, scripts, selected, setScriptDraft, setSelected])
}

// Function: ScriptsPage
export default function ScriptsPage() {
  const { projectId } = useProjectStore()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selected, setSelected] = useState<TestScript | null>(null)
  const [editingScript, setEditingScript] = useState(false)
  const [scriptDraft, setScriptDraft] = useState('')
  const [showPrForm, setShowPrForm] = useState(false)
  const [pr, setPr] = useState({ repo_full_name: '', token: '', base_branch: 'main' })
  const [prResult, setPrResult] = useState<string | null>(null)
  const [showAutomationSetup, setShowAutomationSetup] = useState(false)
  const [selectedAutomationCaseIds, setSelectedAutomationCaseIds] = useState<string[]>([])
  const [automationDraft, setAutomationDraft] = useState(EMPTY_AUTOMATION_DRAFT)
  const [automationResult, setAutomationResult] = useState<string | null>(null)

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
  const { data: coverage } = useQuery<CoverageSummary>({
    queryKey: ['coverage', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/coverage`)).data,
    enabled: !!projectId,
  })
  const { data: runs = [] } = useQuery<PipelineRun[]>({
    queryKey: ['runs', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/runs`)).data,
    enabled: !!projectId,
    refetchInterval: (query) => ((query.state.data as PipelineRun[] | undefined)?.some((item) => ['QUEUED', 'RUNNING'].includes(item.status)) ? 3000 : 30000),
  })
  const run = runs.filter((r) => r.stage === 'SCRIPT_GEN').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0]
  const testDesignRun = runs.filter((r) => r.stage === 'TEST_DESIGN').sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0]
  const testDesignApproved = testDesignRun?.status === 'APPROVED'
  const playwrightCandidates = testCases.filter((testCase) => testCase.status === 'APPROVED')
  const generateTitle = scriptGenerationTitle(testDesignApproved, playwrightCandidates.length, coverage?.automation_ready_test_cases)
  const { data: gate } = useQuery<Gate>({
    queryKey: ['gate', run?.id],
    queryFn: async () => (await api.get(`/runs/${run!.id}/gate`)).data,
    enabled: !!run && run.status === 'AWAITING_APPROVAL',
  })

  const startRun = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/runs`, { stage: 'SCRIPT_GEN' })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['runs', projectId] }),
    onError: (error: any) => setPrResult(error.response?.data?.detail || 'Script Generation could not start.'),
  })
  const bindableUiCases = testCases.filter(isBindableUiCase)
  const selectedAutomationCases = bindableUiCases.filter((testCase) => selectedAutomationCaseIds.includes(testCase.id))
  const toggleAutomationCase = (testCaseId: string) => {
    const nextIds = selectedAutomationCaseIds.includes(testCaseId)
      ? selectedAutomationCaseIds.filter((id) => id !== testCaseId)
      : [...selectedAutomationCaseIds, testCaseId]
    setSelectedAutomationCaseIds(nextIds)
    const template = automationBindingTemplate(bindableUiCases.filter((testCase) => nextIds.includes(testCase.id)))
    setAutomationDraft((current) => ({ ...current, ...template }))
  }
  const applyAutomationProfile = useMutation({
    mutationFn: async () => {
      let locators: Record<string, string>
      let assertions: Record<string, string>
      try {
        locators = JSON.parse(automationDraft.locators)
        assertions = JSON.parse(automationDraft.assertions)
      } catch {
        throw new Error('Locator and assertion maps must be valid JSON objects.')
      }
      if (!locators || Array.isArray(locators) || !Object.keys(locators).length || !assertions || Array.isArray(assertions) || !Object.keys(assertions).length) {
        throw new Error('Locator and assertion maps must each contain at least one binding.')
      }
      return (await api.post(`/projects/${projectId}/testcases/automation-profile`, {
        test_case_ids: selectedAutomationCases.map((testCase) => testCase.id),
        base_url: automationDraft.baseUrl,
        auth_method: automationDraft.authMethod,
        locators,
        assertions,
        test_data_factory: automationDraft.testDataFactory,
        cleanup: automationDraft.cleanup,
        worker_isolation: automationDraft.workerIsolation,
      })).data as { ready: string[]; blocked: Array<{ tc_id: string; reasons: string[] }> }
    },
    onSuccess: (data) => {
      const blockedMessage = data.blocked.length ? ` ${data.blocked.length} remain blocked.` : ''
      setAutomationResult(`${data.ready.length} case(s) are ready for Playwright generation.${blockedMessage}`)
      queryClient.invalidateQueries({ queryKey: ['testcases', projectId] })
      queryClient.invalidateQueries({ queryKey: ['coverage', projectId] })
    },
    onError: (error: any) => setAutomationResult(error.response?.data?.detail || error.message || 'Automation setup failed.'),
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
  const downloadAll = useMutation({
    mutationFn: async () => api.get(`/projects/${projectId}/scripts/download`, { responseType: 'blob' }),
    onSuccess: (response) => saveDownload(response.data, response.headers['content-disposition'], 'playwright-tests.zip'),
  })
  const downloadOne = useMutation({
    mutationFn: async (script: TestScript) => api.get(`/scripts/${script.id}/download`, { responseType: 'blob' }),
    onSuccess: (response, script) => saveDownload(
      response.data,
      response.headers['content-disposition'],
      script.file_path.split('/').pop() || `${script.ts_id}.spec.ts`,
    ),
  })
  const saveScript = useMutation({
    mutationFn: async () => (await api.patch(`/scripts/${selected!.id}`, { code: scriptDraft })).data as TestScript,
    onSuccess: (script) => {
      setSelected(script)
      setScriptDraft(script.code)
      setEditingScript(false)
      queryClient.invalidateQueries({ queryKey: ['scripts', projectId] })
      queryClient.invalidateQueries({ queryKey: ['coverage', projectId] })
    },
    onError: (error: any) => setPrResult(error.response?.data?.detail || 'Could not save and validate the script.'),
  })

  useScriptSelectionSync(scripts, selected, editingScript, setSelected, setScriptDraft)

  if (!projectId) return <NoProjectSelected />

  const tcById: Record<string, TestCase> = Object.fromEntries(testCases.map((tc) => [tc.id, tc]))

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div>
          <h1 className="text-sm font-semibold text-white">Scripts</h1>
          <p className="text-xs text-gray-500">Production-oriented Playwright TypeScript with traceability, validation, and downloadable suite packaging.</p>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={() => downloadAll.mutate()} disabled={!scripts.length || downloadAll.isPending}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded px-3 py-1.5">
            <FileArchive size={13} /> {downloadAll.isPending ? 'Packaging…' : 'Download Test Scripts'}
          </button>
          <button type="button" onClick={() => setShowPrForm((v) => !v)} className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 rounded px-3 py-1.5">
            <GitPullRequest size={13} /> Open GitHub PR
          </button>
          <button type="button" onClick={() => {
            const initialCases = bindableUiCases.slice(0, 1)
            setSelectedAutomationCaseIds(initialCases.map((testCase) => testCase.id))
            const template = automationBindingTemplate(initialCases)
            setAutomationDraft((current) => ({ ...current, ...template }))
            setShowAutomationSetup(true)
            setAutomationResult(null)
          }}
            className="flex items-center gap-1 rounded bg-gray-800 px-3 py-1.5 text-xs hover:bg-gray-700">
            <Settings2 size={13} /> Optional Runtime Config
          </button>
          <button type="button" onClick={() => startRun.mutate()}
            disabled={!coverage || !testDesignApproved || !playwrightCandidates.length || startRun.isPending || run?.status === 'RUNNING' || run?.status === 'QUEUED'}
            title={generateTitle}
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
          <button type="button" onClick={() => openPr.mutate()} disabled={!pr.repo_full_name || !pr.token || openPr.isPending} className="text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-3 py-1.5">Open PR</button>
        </div>
      )}
      {prResult && <p className="px-6 py-2 text-[11px] text-amber-300 border-b border-white/10">{prResult}</p>}
      {run?.status === 'FAILED' && <p className="px-6 py-2 text-xs text-red-300 border-b border-white/10">{run.error}</p>}
      {coverage?.script_coverage_status === 'NOT_APPLICABLE' && (
        <div className="flex items-center justify-between border-b border-amber-500/20 bg-amber-500/5 px-6 py-2">
          <p className="text-xs text-amber-300">Runtime UI bindings are not configured. Script generation remains available; configure these values only when executing against a real UI.</p>
          <button type="button" onClick={() => {
            const initialCases = bindableUiCases.slice(0, 1)
            setSelectedAutomationCaseIds(initialCases.map((testCase) => testCase.id))
            setAutomationDraft((current) => ({ ...current, ...automationBindingTemplate(initialCases) }))
            setShowAutomationSetup(true)
          }} className="rounded border border-amber-500/40 px-3 py-1 text-xs text-amber-300 hover:bg-amber-500/10">Configure now</button>
        </div>
      )}
      {!testDesignApproved && testDesignRun && (
        <div className="flex items-center justify-between border-b border-amber-500/20 bg-amber-500/5 px-6 py-2">
          <p className="text-xs text-amber-300">Test Design approval is required before Script Generation.</p>
          <button type="button" onClick={() => navigate('/verification/test-cases')} className="rounded border border-amber-500/40 px-3 py-1 text-xs text-amber-300 hover:bg-amber-500/10">Review Test Design</button>
        </div>
      )}

      {showAutomationSetup && (
        <AutomationSetupDialog
          candidates={bindableUiCases}
          selectedCaseIds={selectedAutomationCaseIds}
          draft={automationDraft}
          pending={applyAutomationProfile.isPending}
          result={automationResult}
          onChange={setAutomationDraft}
          onToggleCase={toggleAutomationCase}
          onApply={() => applyAutomationProfile.mutate()}
          onReviewCases={() => navigate('/verification/test-cases')}
          onClose={() => setShowAutomationSetup(false)}
        />
      )}

      <div className="flex flex-1 min-h-0">
        <div className="w-72 shrink-0 border-r border-white/10 overflow-y-auto">
          {scripts.map((script) => {
            const tc = tcById[script.test_case_id]
            return (
              <button type="button" key={script.id} onClick={() => setSelected(script)}
                className={`w-full text-left px-3 py-2 border-b border-white/5 hover:bg-white/5 ${selected?.id === script.id ? 'bg-blue-600/10' : ''}`}>
                <div className="flex items-center gap-1.5">
                  {script.compiles === true && <CheckCircle2 size={12} className="text-emerald-400 shrink-0" />}
                  {script.compiles === false && <XCircle size={12} className="text-red-400 shrink-0" />}
                  <span className="text-[10px] text-gray-500">{script.ts_id}</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 shrink-0">Playwright</span>
                </div>
                <p className="text-xs text-gray-300 truncate mt-0.5">{tc?.title || script.file_path}</p>
              </button>
            )
          })}
          {scripts.length === 0 && <p className="p-4 text-xs text-gray-600">{playwrightCandidates.length ? 'Generate traceable scripts for all approved test cases.' : 'No approved test cases are available.'}</p>}
        </div>

        <div className="flex-1 flex min-w-0">
          {selected ? (
            <>
              <div className="w-80 shrink-0 border-r border-white/10 p-4 overflow-y-auto">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <p className="text-[10px] text-gray-500 break-all">{selected.file_path}</p>
                  <button type="button" onClick={() => downloadOne.mutate(selected)} disabled={downloadOne.isPending}
                    title="Download this Playwright script"
                    className="shrink-0 flex items-center gap-1 text-[10px] bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded px-2 py-1">
                    <Download size={11} /> Download
                  </button>
                </div>
                <h3 className="text-xs font-semibold text-white mb-2">{tcById[selected.test_case_id]?.title}</h3>
                <ol className="space-y-1.5">
                  {(tcById[selected.test_case_id]?.steps || []).map((step) => (
                    <li key={step.step_no} className="text-[11px] text-gray-400">
                      <span className="text-gray-600">{step.step_no}.</span> {step.action}
                      <br /><span className="text-gray-600">Expected: {step.expected_result}</span>
                    </li>
                  ))}
                </ol>
                <div className={`mt-3 text-[11px] px-2 py-1.5 rounded ${compileStatusClass(selected.compiles)}`}>
                  {compileStatusText(selected)}
                </div>
              </div>
              <div className="flex min-w-0 flex-1 flex-col">
                <div className="flex h-10 items-center justify-end gap-2 border-b border-white/10 px-3">
                  {editingScript ? (
                    <>
                      <button type="button" onClick={() => { setEditingScript(false); setScriptDraft(selected.code) }} className="rounded border border-white/15 px-2 py-1 text-[10px] text-gray-300">Cancel</button>
                      <button type="button" onClick={() => saveScript.mutate()} disabled={saveScript.isPending || !scriptDraft.trim()} className="flex items-center gap-1 rounded bg-blue-600 px-2 py-1 text-[10px] text-white disabled:opacity-40"><Save size={11} /> {saveScript.isPending ? 'Validating…' : 'Save & Validate'}</button>
                    </>
                  ) : (
                    <button type="button" onClick={() => { setScriptDraft(selected.code); setEditingScript(true) }} className="flex items-center gap-1 rounded border border-white/15 px-2 py-1 text-[10px] text-gray-300 hover:bg-white/5"><Pencil size={11} /> Edit Script</button>
                  )}
                </div>
                <Editor
                  height="100%" language="typescript" theme="vs-dark" value={editingScript ? scriptDraft : selected.code}
                  onChange={(value) => { if (editingScript) setScriptDraft(value || '') }}
                  options={{ readOnly: !editingScript, minimap: { enabled: false }, fontSize: 12 }}
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
            <button type="button" onClick={() => decideGate.mutate({ decision: 'APPROVED' })} disabled={decideGate.isPending}
              className="text-xs bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-1.5 disabled:opacity-50">Approve &amp; Generate Final Artifacts</button>
            <button
              type="button"
              onClick={() => { const r = window.prompt('Rationale for rejecting (mandatory):'); if (r) decideGate.mutate({ decision: 'REJECTED', rationale: r }) }}
              disabled={decideGate.isPending} className="text-xs bg-red-600/80 hover:bg-red-500 rounded px-3 py-1.5 disabled:opacity-50">Reject</button>
          </div>
        </div>
      )}
    </div>
  )
}
