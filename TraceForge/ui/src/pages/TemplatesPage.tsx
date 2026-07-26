// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (TemplatesPage.tsx)
// Date: 2025-07-29
// ---------------------------------------------------------------------------
import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import { useProjectStore } from '../stores/projectStore'

interface Template {
  id: string
  kind: string
  filename: string
  project_id: string | null
  section_map: Record<string, unknown>
}
const KINDS = ['BRD', 'FRD', 'FSD', 'SOLUTION_DOC', 'RTM', 'TEST_PLAN', 'TEST_CASE']

// Function: TemplatesPage
export default function TemplatesPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const fileInput = useRef<HTMLInputElement>(null)
  const [kind, setKind] = useState('BRD')
  const { data: templates = [] } = useQuery<Template[]>({
    queryKey: ['templates', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/templates`)).data,
    enabled: !!projectId,
  })
  const upload = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('kind', kind)
      form.append('section_map', '{}')
      form.append('file', file)
      return (await api.post(`/projects/${projectId}/templates`, form)).data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['templates', projectId] }),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Template upload failed.'),
  })
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Templates</h1>
        <p className="mt-1 text-xs text-gray-500">Controlled project templates for generated specifications, test plans, and matrices.</p>
      </div>
      <div className="flex max-w-xl gap-2 rounded-lg border border-white/10 bg-gray-900 p-3">
        <select value={kind} onChange={(event) => setKind(event.target.value)}
          className="rounded border border-white/10 bg-gray-800 px-2 py-1.5 text-xs">
          {KINDS.map((item) => <option key={item}>{item}</option>)}
        </select>
        <button onClick={() => fileInput.current?.click()} disabled={upload.isPending}
          className="rounded bg-blue-600 px-3 py-1.5 text-xs disabled:opacity-50">
          {upload.isPending ? 'Uploading…' : 'Upload DOCX/DOTX/XLSX'}
        </button>
        <input ref={fileInput} type="file" accept=".docx,.dotx,.xlsx" className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (file) upload.mutate(file)
            event.target.value = ''
          }} />
      </div>
      <div className="space-y-2">
        {templates.map((template) => (
          <div key={template.id} className="flex items-center justify-between rounded-lg border border-white/10 bg-gray-900 p-3">
            <div>
              <p className="text-xs text-white">{template.filename}</p>
              <p className="mt-1 text-[10px] text-gray-500">{template.kind} · {template.project_id ? 'Project' : 'Global'}</p>
            </div>
            <span className="rounded bg-blue-500/10 px-2 py-0.5 text-[10px] text-blue-300">Available</span>
          </div>
        ))}
        {!templates.length && <p className="py-8 text-center text-xs text-gray-600">No templates configured.</p>}
      </div>
    </div>
  )
}
