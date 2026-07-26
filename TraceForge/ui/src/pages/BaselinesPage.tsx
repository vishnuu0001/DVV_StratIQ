// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (BaselinesPage.tsx)
// Date: 2026-02-27
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import { useProjectStore } from '../stores/projectStore'

interface Baseline {
  id: string
  name: string
  description: string | null
  sha256: string
  created_by: string
  created_at: string
  snapshot: { requirements?: unknown[]; test_cases?: unknown[]; test_scripts?: unknown[]; artifacts?: unknown[] }
}

// Function: BaselinesPage
export default function BaselinesPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const { data: baselines = [] } = useQuery<Baseline[]>({
    queryKey: ['baselines', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/baselines`)).data,
    enabled: !!projectId,
  })
  const create = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/baselines`, { name, description: description || null })).data,
    onSuccess: () => {
      setName(''); setDescription('')
      queryClient.invalidateQueries({ queryKey: ['baselines', projectId] })
    },
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Could not create baseline.'),
  })
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Baselines</h1>
        <p className="mt-1 text-xs text-gray-500">Immutable, content-addressed snapshots of requirements, tests, scripts, and deliverables.</p>
      </div>
      <div className="flex max-w-4xl gap-2 rounded-lg border border-white/10 bg-gray-900 p-3">
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Baseline name"
          className="min-w-48 rounded border border-white/10 bg-gray-800 px-2 py-1.5 text-xs" />
        <input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description"
          className="flex-1 rounded border border-white/10 bg-gray-800 px-2 py-1.5 text-xs" />
        <button onClick={() => create.mutate()} disabled={!name.trim() || create.isPending}
          className="rounded bg-blue-600 px-3 py-1.5 text-xs disabled:opacity-50">Create baseline</button>
      </div>
      <div className="space-y-2">
        {baselines.map((baseline) => (
          <div key={baseline.id} className="rounded-lg border border-white/10 bg-gray-900 p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-white">{baseline.name}</p>
                <p className="mt-1 text-[10px] text-gray-500">{baseline.created_by} · {new Date(baseline.created_at).toLocaleString()}</p>
              </div>
              <span className="font-mono text-[10px] text-blue-400">{baseline.sha256.slice(0, 12)}</span>
            </div>
            <p className="mt-2 text-[11px] text-gray-400">{baseline.description}</p>
            <p className="mt-2 text-[10px] text-gray-500">
              {baseline.snapshot.requirements?.length || 0} requirements · {baseline.snapshot.test_cases?.length || 0} tests · {baseline.snapshot.test_scripts?.length || 0} scripts · {baseline.snapshot.artifacts?.length || 0} artifacts
            </p>
          </div>
        ))}
        {!baselines.length && <p className="py-8 text-center text-xs text-gray-600">No baselines created.</p>}
      </div>
    </div>
  )
}
