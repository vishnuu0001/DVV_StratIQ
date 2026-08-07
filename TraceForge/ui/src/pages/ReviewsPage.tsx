// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (ReviewsPage.tsx)
// Date: 2025-09-16
// ---------------------------------------------------------------------------
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../api/client'
import type { TestCase } from '../api/types'
import NoProjectSelected from '../components/NoProjectSelected'
import { useProjectStore } from '../stores/projectStore'

interface Review {
  id: string
  run_id: string
  stage: string
  required_role: string
  decision: string
  decided_by: string | null
  decided_at: string | null
  rationale: string | null
  created_at: string
}

const NEXT_STAGE: Record<string, string> = {
  EXTRACT: 'BRD',
  BRD: 'TEST_DESIGN',
  TEST_DESIGN: 'SCRIPT_GEN',
  SCRIPT_GEN: 'RENDER',
}

function metadata(testCase: TestCase): Record<string, any> {
  const raw = testCase.gherkin?.trim()
  if (!raw?.startsWith('{')) return {}
  try { return JSON.parse(raw) } catch { return {} }
}

function hasUnresolvedDecision(testCase: TestCase) {
  const value = metadata(testCase)
  const assumptions = (value.assumptions || []).join(' ').toLowerCase()
  return Boolean(value.ambiguities?.length || assumptions.includes('pending') || assumptions.includes('review'))
}

// Function: ReviewsPage
export default function ReviewsPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const { data: reviews = [] } = useQuery<Review[]>({
    queryKey: ['reviews', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/reviews`)).data,
    enabled: !!projectId,
    refetchInterval: 10000,
  })
  const { data: testCases = [] } = useQuery<TestCase[]>({
    queryKey: ['testcases', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/testcases`)).data,
    enabled: !!projectId,
  })
  const unresolvedTestCases = testCases.filter(hasUnresolvedDecision)
  const automationReadyCount = testCases.filter((testCase) => (
    String(metadata(testCase).automation_status || '').startsWith('READY_FOR_')
  )).length
  const decide = useMutation({
    mutationFn: async ({ review, decision, rationale }: { review: Review; decision: string; rationale?: string }) => {
      const result = (await api.post(`/runs/${review.run_id}/gate/decide`, {
        decision, rationale: rationale || null, item_decisions: {},
      })).data
      const nextStage = NEXT_STAGE[review.stage]
      if (decision === 'APPROVED' && nextStage && !(review.stage === 'TEST_DESIGN' && automationReadyCount === 0)) {
        await api.post(`/projects/${projectId}/runs`, { stage: nextStage })
      }
      return result
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', projectId] })
      queryClient.invalidateQueries({ queryKey: ['runs', projectId] })
    },
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Review decision failed.'),
  })
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Reviews &amp; Approvals</h1>
        <p className="mt-1 text-xs text-gray-500">A consolidated queue for every governed pipeline decision.</p>
      </div>
      <div className="overflow-hidden rounded-lg border border-white/10 bg-gray-900">
        {reviews.map((review) => (
          <div key={review.id} className="flex items-center justify-between border-b border-white/5 p-3 last:border-0">
            <div>
              <p className="text-xs text-white">{review.stage.replace(/_/g, ' ')}</p>
              <p className="mt-1 text-[10px] text-gray-500">
                Required role: {review.required_role.replace(/_/g, ' ')} · opened {new Date(review.created_at).toLocaleString()}
              </p>
              {review.rationale && <p className="mt-1 text-[11px] text-gray-400">{review.rationale}</p>}
            </div>
            {review.decision === 'PENDING' ? (
              <div className="flex items-center gap-2">
                {review.stage === 'TEST_DESIGN' && unresolvedTestCases.length > 0 && (
                  <Link to="/verification/test-cases" className="text-[10px] text-amber-700 underline">
                    Resolve {unresolvedTestCases.map((testCase) => testCase.tc_id).join(', ')}
                  </Link>
                )}
                <button onClick={() => decide.mutate({ review, decision: 'APPROVED' })}
                  disabled={decide.isPending || (review.stage === 'TEST_DESIGN' && unresolvedTestCases.length > 0)}
                  title={review.stage === 'TEST_DESIGN' && unresolvedTestCases.length > 0 ? 'Resolve the linked test-case decisions first.' : undefined}
                  className="rounded bg-emerald-600 px-3 py-1.5 text-xs disabled:opacity-50">
                  {review.stage === 'TEST_DESIGN' && automationReadyCount === 0 ? 'Approve Test Design' : 'Approve'}
                </button>
                <button onClick={() => {
                  const rationale = window.prompt('Rejection rationale (required)')
                  if (rationale?.trim()) decide.mutate({ review, decision: 'REJECTED', rationale })
                }} className="rounded bg-red-600/80 px-3 py-1.5 text-xs">Reject</button>
              </div>
            ) : (
              <div className="text-right">
                <span className={`rounded px-2 py-0.5 text-[10px] ${review.decision.startsWith('APPROVED') ? 'bg-emerald-500/15 text-emerald-300' : 'bg-red-500/15 text-red-300'}`}>
                  {review.decision.replace(/_/g, ' ')}
                </span>
                <p className="mt-1 text-[10px] text-gray-500">{review.decided_by || 'system'}</p>
              </div>
            )}
          </div>
        ))}
        {!reviews.length && <p className="p-8 text-center text-xs text-gray-600">No reviews have been opened.</p>}
      </div>
    </div>
  )
}
