// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/stores (projectStore.ts)
// Date: 2025-11-30
// ---------------------------------------------------------------------------
import { create } from 'zustand'

interface ProjectStore {
  projectId: string | null
  setProjectId: (id: string | null) => void
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projectId: localStorage.getItem('tf_current_project') || null,
  setProjectId: (id) => {
    if (id) localStorage.setItem('tf_current_project', id)
    else localStorage.removeItem('tf_current_project')
    set({ projectId: id })
  },
}))
