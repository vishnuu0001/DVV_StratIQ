// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/components (ProjectSwitcher.tsx)
// Date: 2025-09-02
// ---------------------------------------------------------------------------
import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import api from '../api/client'
import type { Project } from '../api/types'
import { useProjectStore } from '../stores/projectStore'

// Function: ProjectSwitcher
export default function ProjectSwitcher() {
  const { projectId, setProjectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [creating, setCreating] = useState(false)
  const [newKey, setNewKey] = useState('')
  const [newName, setNewName] = useState('')

  const { data: projects = [], isSuccess, isError } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => (await api.get('/projects')).data,
  })

  useEffect(() => {
    if (!isSuccess) return

    const selectionIsValid = projects.some((project) => project.id === projectId)
    if (selectionIsValid) return

    // Do not let pages call APIs with a project ID that the selector cannot display.
    setProjectId(projects.length === 1 ? projects[0].id : null)
  }, [isSuccess, projectId, projects, setProjectId])

  const createProject = useMutation({
    mutationFn: async () => (await api.post('/projects', { key: newKey, name: newName })).data as Project,
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setProjectId(project.id)
      setCreating(false)
      setNewKey('')
      setNewName('')
    },
  })

  return (
    <div className="p-3 border-b border-white/10 space-y-2">
      <select
        className="w-full bg-gray-900 border border-white/10 rounded px-2 py-1.5 text-xs text-white"
        value={projectId || ''}
        onChange={(e) => setProjectId(e.target.value || null)}
      >
        <option value="">Select a project…</option>
        {projects.map((p) => (
          <option key={p.id} value={p.id}>{p.key} — {p.name}</option>
        ))}
      </select>

      {isError && (
        <p className="text-[11px] text-red-400">Projects could not be loaded. Refresh the page or sign in again.</p>
      )}

      {creating ? (
        <div className="space-y-1">
          <input className="w-full bg-gray-900 border border-white/10 rounded px-2 py-1 text-xs" placeholder="KEY (e.g. ACME-OMS)" value={newKey} onChange={(e) => setNewKey(e.target.value)} />
          <input className="w-full bg-gray-900 border border-white/10 rounded px-2 py-1 text-xs" placeholder="Project name" value={newName} onChange={(e) => setNewName(e.target.value)} />
          <div className="flex gap-1">
            <button
              className="flex-1 bg-blue-600 hover:bg-blue-500 rounded text-xs py-1 disabled:opacity-50"
              disabled={!newKey || !newName || createProject.isPending}
              onClick={() => createProject.mutate()}
            >
              Create
            </button>
            <button className="flex-1 bg-gray-800 hover:bg-gray-700 rounded text-xs py-1" onClick={() => setCreating(false)}>Cancel</button>
          </div>
          {createProject.isError && (
            <p className="text-[11px] text-red-400">Project creation failed. Check the key and try again.</p>
          )}
        </div>
      ) : (
        <button className="w-full flex items-center justify-center gap-1 bg-gray-900 hover:bg-gray-800 border border-white/10 rounded text-xs py-1.5 text-gray-400" onClick={() => setCreating(true)}>
          <Plus size={12} /> New project
        </button>
      )}
    </div>
  )
}
