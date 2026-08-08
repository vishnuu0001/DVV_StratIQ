// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (OverviewPage.tsx)
// Date: 2025-08-12
// ---------------------------------------------------------------------------
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { PlayCircle, RefreshCw, RotateCcw, Square, Trash2 } from 'lucide-react'
import api from '../api/client'
import type { CoverageSummary, PipelineRun } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'
import PipelineDag from '../components/PipelineDag'

const STATUS_COLOR: Record<string, string> = {
  QUEUED: 'bg-gray-700 text-gray-300',
  RUNNING: 'bg-blue-500/20 text-blue-300 animate-pulse',
  AWAITING_APPROVAL: 'bg-amber-500/20 text-amber-300',
  APPROVED: 'bg-emerald-500/20 text-emerald-300',
  REJECTED: 'bg-red-500/20 text-red-300',
  FAILED: 'bg-red-500/20 text-red-300',
}

const GATE_PAGE_FOR_STAGE: Record<string, string> = {
  EXTRACT: '/requirements/register',
  BRD: '/specifications/brd',
  TEST_DESIGN: '/verification/test-cases',
  SCRIPT_GEN: '/verification/test-scripts',
}

// Function: statNumber
function statNumber(run: PipelineRun, key: string): number {
  const value = run.stats?.[key]
  return typeof value === 'number' ? value : 0
}

// Function: OverviewPage
export default function OverviewPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const { data: runs = [], refetch } = useQuery<PipelineRun[]>({
    queryKey: ['runs', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/runs`)).data,
    enabled: !!projectId,
    refetchInterval: (query) => ((query.state.data as PipelineRun[] | undefined)?.some((run) => ['QUEUED', 'RUNNING'].includes(run.status)) ? 3000 : 30000),
  })
  const { data: coverage } = useQuery<CoverageSummary>({
    queryKey: ['coverage', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/coverage`)).data,
    enabled: !!projectId,
    refetchInterval: () => (runs.some((run) => ['QUEUED', 'RUNNING'].includes(run.status)) ? 5000 : 30000),
  })

  const latestByStage: Record<string, PipelineRun> = {}
  for (const run of runs) {
    if (!latestByStage[run.stage] || run.created_at > latestByStage[run.stage].created_at) {
      latestByStage[run.stage] = run
    }
  }

  const startExtract = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/runs`, { stage: 'EXTRACT' })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['runs', projectId] }),
  })

  const resetPipeline = useMutation({

      const resetRequirements = useMutation({
        mutationFn: async () => (await api.post(`/projects/${projectId}/reset-requirements`)).data,
        onSuccess: () => queryClient.invalidateQueries(),
        onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not reset requirements.'),
      })
    mutationFn: async () => (await api.post(`/projects/${projectId}/reset-pipeline`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['runs', projectId] })
      queryClient.invalidateQueries({ queryKey: ['coverage', projectId] })
    },
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not reset the workflow.'),
  })

  const startFresh = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/start-fresh`, { confirmation: 'START OVER' })).data,
    onSuccess: () => queryClient.invalidateQueries(),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not start the project from scratch.'),
  })

  const stopRun = useMutation({
    mutationFn: async (runId: string) => (await api.post(`/runs/${runId}/cancel`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['runs', projectId] }),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not stop the active run.'),
  })

  // Function: handleReset
  function handleReset() {
    if (!window.confirm(
      'Reset this project\'s pipeline? Every stage will go back to idle and the run history will be cleared.\n\n' +
      'Requirements, Documents, Test Cases, Scripts, and Artifacts already generated are NOT deleted — only the run/gate history is.'
    )) return
    resetPipeline.mutate()
  }

  function handleResetRequirements() {
    if (!window.confirm(
      'Regenerate requirements from all indexed sources? Existing requirements and run history will be removed. Uploaded sources and indexed chunks are preserved.'
    )) return
    resetRequirements.mutate()
  }

  // Function: handleStartFresh
  function handleStartFresh() {
    const confirmation = window.prompt(
      'Permanently remove ALL sources, requirements, documents, test plans/cases, scripts, artifacts, and run history for this project.\n\n' +
      'The project itself and its audit trail will be retained. Type START OVER to continue.'
    )
    if (confirmation !== 'START OVER') return
    startFresh.mutate()
  }

  if (!projectId) return <NoProjectSelected />

  const blockingStage = Object.entries(latestByStage).find(([, run]) => run.status === 'AWAITING_APPROVAL')?.[0]
  const extractIsActive = runs.some((run) => run.stage === 'EXTRACT' && ['QUEUED', 'RUNNING'].includes(run.status))
  const pipelineIsActive = runs.some((run) => ['QUEUED', 'RUNNING'].includes(run.status))
  const activeRun = runs.find((run) => ['QUEUED', 'RUNNING'].includes(run.status))

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-sm font-semibold text-white">Pipeline Overview</h1>
          <p className="text-xs text-gray-500">Source Corpus → RAG Index → Requirements → BRD/FSD/SolutionDoc → Test Plan/Cases → Scripts → RTM</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 rounded px-3 py-1.5">
            <RefreshCw size={13} /> Refresh
          </button>
          <button
            onClick={handleReset}
            disabled={resetPipeline.isPending || runs.length === 0 || pipelineIsActive}
            title={pipelineIsActive ? 'Wait for the active stage to finish before resetting the workflow.' : 'Clear run/gate history so every stage shows idle again. Does not delete Requirements/Documents/Test Cases/Scripts/Artifacts.'}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 rounded px-3 py-1.5 disabled:opacity-50"
          >
            <RotateCcw size={13} /> Reset Workflow
          </button>
          <button
            onClick={handleResetRequirements}
            disabled={resetRequirements.isPending || pipelineIsActive}
            title={pipelineIsActive ? 'Wait for the active stage to finish.' : 'Clear requirements and run history while preserving indexed sources.'}
            className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 rounded px-3 py-1.5 disabled:opacity-50"
          >
            <RefreshCw size={13} /> Regenerate Requirements
          </button>
          <button
            onClick={handleStartFresh}
            disabled={startFresh.isPending || pipelineIsActive}
            title={pipelineIsActive ? 'Wait for the active stage to finish before clearing the project.' : 'Permanently clear sources and all generated outputs while retaining the project.'}
            className="flex items-center gap-1 text-xs bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-300 rounded px-3 py-1.5 disabled:opacity-50"
          >
            <Trash2 size={13} /> Start from Scratch
          </button>
          <button
            onClick={() => startExtract.mutate()}
            disabled={startExtract.isPending || extractIsActive}
            className="flex items-center gap-1 text-xs text-white rounded-sm px-3 py-1.5 disabled:opacity-50"
            style={{ background: '#0078d4' }}
          >
            <PlayCircle size={13} /> Run Extract
          </button>
          {activeRun && (
            <button
              onClick={() => window.confirm(`Stop the active ${activeRun.stage.replace('_', ' ')} run? Completed batches will remain available.`) && stopRun.mutate(activeRun.id)}
              disabled={stopRun.isPending}
              className="flex items-center gap-1 text-xs bg-red-600/80 hover:bg-red-500 rounded px-3 py-1.5 disabled:opacity-50"
            >
              <Square size={12} /> Stop Run
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-sm border border-white/10 bg-gray-900 px-4 py-3">
          <p className="text-xs font-medium text-gray-200">Reset Workflow</p>
          <p className="mt-1 text-[11px] text-gray-500">Clears stage and gate history only. Sources and every generated deliverable remain available.</p>
        </div>
        <div className="rounded-sm border border-red-500/20 bg-red-500/5 px-4 py-3">
          <p className="text-xs font-medium text-red-300">Start from Scratch</p>
          <p className="mt-1 text-[11px] text-gray-500">Permanently clears sources and all generated outputs. Requires typing START OVER; the project and audit trail are retained.</p>
        </div>
      </div>

      {blockingStage && (
        <button onClick={() => navigate(GATE_PAGE_FOR_STAGE[blockingStage] || '/')} className="w-full text-left bg-amber-500/10 border border-amber-500/30 rounded-sm p-4 hover:bg-amber-500/15">
          <p className="text-sm text-amber-300 font-medium">A gate is blocking the pipeline — click to review.</p>
          <p className="text-xs text-amber-400/80 mt-1">{blockingStage.replace('_', ' ')} is awaiting approval before the next stage can run.</p>
        </button>
      )}

      <PipelineDag runs={runs} onGateClick={(stage) => navigate(GATE_PAGE_FOR_STAGE[stage] || '/')} />

      {coverage && (
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-gray-900 border border-white/10 rounded-sm p-3">
            <p className="text-[10px] text-gray-500 uppercase">Coverage</p>
            <p className="text-lg font-semibold text-white">{coverage.coverage_pct}%</p>
          </div>
          <div className="bg-gray-900 border border-white/10 rounded-sm p-3">
            <p className="text-[10px] text-gray-500 uppercase">Requirements</p>
            <p className="text-lg font-semibold text-white">{coverage.total_requirements}</p>
          </div>
          <div className="bg-gray-900 border border-white/10 rounded-sm p-3">
            <p className="text-[10px] text-gray-500 uppercase">Test Cases</p>
            <p className="text-lg font-semibold text-white">{coverage.total_test_cases}</p>
          </div>
          <div className="bg-gray-900 border border-white/10 rounded-sm p-3">
            <p className="text-[10px] text-gray-500 uppercase">Scripts</p>
            <p className="text-lg font-semibold text-white">{coverage.total_scripts}</p>
          </div>
        </div>
      )}

      <div className="bg-gray-900 border border-white/10 rounded-sm">
        <div className="px-4 py-3 border-b border-white/10">
          <h2 className="text-xs font-semibold text-white">Recent Runs</h2>
        </div>
        <table className="w-full text-xs">
          <thead className="text-gray-500 text-left">
            <tr>
              <th className="px-4 py-2 font-normal">Stage</th>
              <th className="px-4 py-2 font-normal">Status</th>
              <th className="px-4 py-2 font-normal">Started</th>
              <th className="px-4 py-2 font-normal">Error</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id} className="border-t border-white/5">
                <td className="px-4 py-2 text-gray-300">{run.stage}</td>
                <td className="px-4 py-2">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full ${STATUS_COLOR[run.status] || ''}`}>{run.status}</span>
                  {run.status === 'RUNNING' && statNumber(run, 'batch_total') > 0 && (
                    <span className="ml-2 text-[10px] text-gray-400">
                      batch {statNumber(run, 'batch_current')}/{statNumber(run, 'batch_total')} · {statNumber(run, 'items_generated')} generated
                      {statNumber(run, 'response_chunks') > 0 && ` · ${statNumber(run, 'response_chunks')} response chunks received`}
                    </span>
                  )}
                  {run.status === 'RUNNING' && statNumber(run, 'batch_total') === 0 && Boolean(run.stats?.phase) && (
                    <span className="ml-2 text-[10px] text-gray-400">
                      {String(run.stats.phase).replace(/_/g, ' ')}
                      {statNumber(run, 'requirements_total') > 0 && ` · ${statNumber(run, 'requirements_completed')}/${statNumber(run, 'requirements_total')} requirements`}
                      {statNumber(run, 'test_cases_total') > 0 && ` · ${statNumber(run, 'test_cases_completed')}/${statNumber(run, 'test_cases_total')} test cases`}
                      {statNumber(run, 'document_total') > 0 && ` · ${statNumber(run, 'document_current')}/${statNumber(run, 'document_total')} documents`}
                    </span>
                  )}
                </td>
                <td className="px-4 py-2 text-gray-500">{run.started_at ? new Date(run.started_at).toLocaleString() : '—'}</td>
                <td className="px-4 py-2 text-red-400">{run.error || ''}</td>
              </tr>
            ))}
            {runs.length === 0 && (
              <tr><td colSpan={4} className="px-4 py-6 text-center text-gray-600">No runs yet — upload a source document, then click "Run Extract".</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
