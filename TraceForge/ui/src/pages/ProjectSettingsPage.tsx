// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (ProjectSettingsPage.tsx)
// Date: 2026-04-30
// ---------------------------------------------------------------------------
import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import type { Project } from '../api/types'
import { useProjectStore } from '../stores/projectStore'

// Function: ProjectSettingsPage
export default function ProjectSettingsPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const { data: project } = useQuery<Project>({
    queryKey: ['project', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}`)).data,
    enabled: !!projectId,
  })
  const [ambiguityThreshold, setAmbiguityThreshold] = useState('0.4')
  const [coveragePolicy, setCoveragePolicy] = useState('DEFAULT')
  useEffect(() => {
    if (!project) return
    setAmbiguityThreshold(String(project.config.ambiguity_threshold ?? '0.4'))
    setCoveragePolicy(String(project.config.coverage_policy ?? 'DEFAULT'))
  }, [project])
  const save = useMutation({
    mutationFn: async () => (await api.patch(`/projects/${projectId}/config`, {
      config: {
        ambiguity_threshold: Number(ambiguityThreshold),
        coverage_policy: coveragePolicy,
      },
    })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['project', projectId] }),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Project settings could not be saved.'),
  })
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Project Settings</h1>
        <p className="mt-1 text-xs text-gray-500">Govern quality thresholds and verification policy for this project.</p>
      </div>
      <div className="max-w-xl space-y-4 rounded-lg border border-white/10 bg-gray-900 p-4">
        <label className="block text-xs text-gray-300">
          Ambiguity threshold
          <input type="number" min="0" max="1" step="0.05" value={ambiguityThreshold}
            onChange={(event) => setAmbiguityThreshold(event.target.value)}
            className="mt-1 w-full rounded border border-white/10 bg-gray-800 px-3 py-2 text-xs" />
        </label>
        <label className="block text-xs text-gray-300">
          Coverage policy
          <select value={coveragePolicy} onChange={(event) => setCoveragePolicy(event.target.value)}
            className="mt-1 w-full rounded border border-white/10 bg-gray-800 px-3 py-2 text-xs">
            <option value="DEFAULT">Default</option>
            <option value="STRICT">Strict</option>
            <option value="REGULATED">Regulated</option>
          </select>
        </label>
        <button onClick={() => save.mutate()} disabled={save.isPending}
          className="rounded bg-blue-600 px-3 py-1.5 text-xs disabled:opacity-50">Save settings</button>
      </div>
    </div>
  )
}
