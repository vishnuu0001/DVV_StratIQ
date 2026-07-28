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
    <div className="az-project-switcher">
      <select
        value={projectId || ''}
        onChange={(e) => setProjectId(e.target.value || null)}
      >
        <option value="">Select a project…</option>
        {projects.map((p) => (
          <option key={p.id} value={p.id}>{p.key} — {p.name}</option>
        ))}
      </select>

      {isError && (
        <p className="text-[11px] mt-1" style={{ color: '#a4262c' }}>Projects could not be loaded. Refresh the page or sign in again.</p>
      )}

      {creating ? (
        <div>
          <input placeholder="KEY (e.g. ACME-OMS)" value={newKey} onChange={(e) => setNewKey(e.target.value)} />
          <input placeholder="Project name" value={newName} onChange={(e) => setNewName(e.target.value)} />
          <div className="flex gap-1 mt-1.5">
            <button
              className="az-project-switcher-btn"
              style={{ background: '#0078d4', color: '#fff', borderColor: '#0078d4' }}
              disabled={!newKey || !newName || createProject.isPending}
              onClick={() => createProject.mutate()}
            >
              Create
            </button>
            <button className="az-project-switcher-btn" onClick={() => setCreating(false)}>Cancel</button>
          </div>
          {createProject.isError && (
            <p className="text-[11px] mt-1" style={{ color: '#a4262c' }}>Project creation failed. Check the key and try again.</p>
          )}
        </div>
      ) : (
        <button className="az-project-switcher-btn" onClick={() => setCreating(true)}>
          <Plus size={12} /> New project
        </button>
      )}
    </div>
  )
}
