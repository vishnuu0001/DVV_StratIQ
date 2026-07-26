// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (SourcesPage.tsx)
// Date: 2025-10-07
// ---------------------------------------------------------------------------
import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { FileText, Trash2, Upload } from 'lucide-react'
import api from '../api/client'
import type { Chunk, SourceDocument } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

const STATUS_COLOR: Record<string, string> = {
  PENDING: 'bg-gray-700 text-gray-300',
  PARSING: 'bg-blue-500/20 text-blue-300 animate-pulse',
  INDEXED: 'bg-emerald-500/20 text-emerald-300',
  FAILED: 'bg-red-500/20 text-red-300',
}

const ACCEPTED_FILES = '.docx,.pdf,.xlsx,.md,.txt,.py,.js,.jsx,.ts,.tsx,.java,.cs,.go,.rb,.php,.cpp,.cc,.c,.h,.rs,.kt'
const ARTIFACT_ROLES = [
  ['FUNCTIONAL_DETAILS', 'Functional details / requirements'],
  ['SUPPORTING_ARTIFACT', 'Supporting artifact'],
  ['PROCESS_FLOW', 'Process flow / workflow'],
  ['BUSINESS_RULES', 'Business rules / policies'],
  ['TEST_EVIDENCE', 'Existing test evidence'],
  ['SOURCE_CODE', 'Source code'],
] as const

// Function: errorMessage
function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  return error instanceof Error ? error.message : 'Upload failed. Please try again.'
}

// Function: SourcesPage
export default function SourcesPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const fileInput = useRef<HTMLInputElement>(null)
  const [selected, setSelected] = useState<SourceDocument | null>(null)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [artifactRole, setArtifactRole] = useState('FUNCTIONAL_DETAILS')

  const { data: sources = [], isError: sourcesFailed } = useQuery<SourceDocument[]>({
    queryKey: ['sources', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/sources`)).data,
    enabled: !!projectId,
    refetchInterval: (query) => ((query.state.data as SourceDocument[] | undefined)?.some((source) => ['PENDING', 'PARSING'].includes(source.status)) ? 3000 : 30000),
  })

  const { data: chunks = [] } = useQuery<Chunk[]>({
    queryKey: ['chunks', selected?.id],
    queryFn: async () => (await api.get(`/sources/${selected!.id}/chunks`)).data,
    enabled: !!selected,
  })

  const upload = useMutation({
    mutationFn: async (files: File[]) => {
      if (!projectId) throw new Error('Select a project before uploading files.')
      const form = new FormData()
      files.forEach((file) => form.append('files', file))
      form.append('artifact_role', artifactRole)
      return (await api.post<SourceDocument[]>(`/projects/${projectId}/sources/upload`, form)).data
    },
    onMutate: (files) => setUploadMessage(`Uploading ${files.length} file${files.length === 1 ? '' : 's'}…`),
    onSuccess: (created) => {
      queryClient.setQueryData<SourceDocument[]>(['sources', projectId], (current = []) => [
        ...created,
        ...current.filter((source) => !created.some((item) => item.id === source.id)),
      ])
      setSelected(created[0] ?? null)
      setUploadMessage(`${created.length} file${created.length === 1 ? '' : 's'} uploaded. Indexing has started.`)
      queryClient.invalidateQueries({ queryKey: ['sources', projectId] })
    },
    onError: (error) => setUploadMessage(errorMessage(error)),
    onSettled: () => {
      if (fileInput.current) fileInput.current.value = ''
    },
  })

  const deleteSource = useMutation({
    mutationFn: async (sourceId: string) => api.delete(`/sources/${sourceId}`),
    onSuccess: (_data, sourceId) => {
      queryClient.invalidateQueries({ queryKey: ['sources', projectId] })
      setSelected((current) => (current?.id === sourceId ? null : current))
    },
  })

  // Function: handleDelete
  function handleDelete(source: SourceDocument) {
    if (!window.confirm(
      `Delete "${source.filename}"?\n\n` +
      'This removes it from the source list and RAG index. Requirements already extracted ' +
      'from it are NOT deleted or re-validated — re-run Extract afterward if you want the corpus back in sync.'
    )) return
    deleteSource.mutate(source.id)
  }

  if (!projectId) return <NoProjectSelected />

  return (
    <div className="p-6 grid grid-cols-2 gap-6">
      <div>
        <div className="flex items-center justify-between gap-3 mb-3">
          <h1 className="text-sm font-semibold text-white">Sources</h1>
          <select
            value={artifactRole}
            onChange={(event) => setArtifactRole(event.target.value)}
            disabled={upload.isPending}
            className="ml-auto max-w-64 bg-gray-900 border border-white/10 rounded px-2 py-1.5 text-xs text-gray-200"
            aria-label="Uploaded artifact role"
          >
            {ARTIFACT_ROLES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
          <button
            onClick={() => fileInput.current?.click()}
            disabled={upload.isPending}
            className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 rounded px-3 py-1.5 disabled:opacity-50"
          >
            <Upload size={13} /> {upload.isPending ? 'Uploading…' : 'Upload'}
          </button>
          <input
            ref={fileInput} type="file" multiple accept={ACCEPTED_FILES} className="hidden"
            onChange={(event) => {
              const files = Array.from(event.target.files ?? [])
              if (files.length) upload.mutate(files)
            }}
          />
        </div>
        <p className="text-[11px] text-gray-600 mb-2">Upload accepts Word, PDF, Excel, Markdown, text, and common source-code files.</p>
        {uploadMessage && (
          <div className={`mb-3 rounded border px-3 py-2 text-xs ${upload.isError ? 'border-red-500/30 bg-red-500/10 text-red-300' : 'border-blue-500/30 bg-blue-500/10 text-blue-200'}`}>
            {uploadMessage}
          </div>
        )}
        {sourcesFailed && (
          <div className="mb-3 rounded border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-300">
            Uploaded sources could not be loaded. Refresh the page or reselect the project.
          </div>
        )}

        <div className="space-y-1">
          {sources.map((source) => (
            <div
              key={source.id}
              onClick={() => setSelected(source)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setSelected(source)}
              className={`w-full flex items-center justify-between text-left px-3 py-2 rounded-lg border text-xs cursor-pointer ${selected?.id === source.id ? 'bg-blue-600/10 border-blue-500/40' : 'bg-gray-900 border-white/10 hover:border-white/20'}`}
            >
              <span className="flex items-center gap-2 text-gray-300 truncate min-w-0">
                <FileText size={13} className="shrink-0" />
                <span className="truncate">
                  {source.filename}
                  <span className="block text-[10px] text-gray-600">{String(source.connector_ref?.artifact_role || source.doc_class).replace(/_/g, ' ')}</span>
                </span>
              </span>
              <span className="flex items-center gap-2 shrink-0 ml-2">
                <span className={`px-2 py-0.5 rounded-full ${STATUS_COLOR[source.status]}`}>{source.status}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); handleDelete(source) }}
                  disabled={deleteSource.isPending}
                  title={`Delete ${source.filename}`}
                  className="p-1 rounded text-gray-500 hover:text-red-400 hover:bg-red-500/10 disabled:opacity-40"
                >
                  <Trash2 size={13} />
                </button>
              </span>
            </div>
          ))}
          {sources.length === 0 && <p className="text-xs text-gray-600 py-6 text-center">No sources uploaded yet.</p>}
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-white mb-3">Chunk Explorer</h2>
        {selected?.parse_error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded p-3 text-xs text-red-300 mb-3">{selected.parse_error}</div>
        )}
        {!selected ? (
          <p className="text-xs text-gray-600">Select a source to inspect its chunks and locators.</p>
        ) : (
          <div className="space-y-2 max-h-[70vh] overflow-y-auto">
            {chunks.map((chunk) => (
              <div key={chunk.id} className="bg-gray-900 border border-white/10 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-gray-500">#{chunk.ordinal} · {chunk.token_count} tokens</span>
                  <span className="text-[10px] text-gray-600">{String((chunk.locator as any)?.section || '')}</span>
                </div>
                <p className="text-xs text-gray-300 whitespace-pre-wrap">{chunk.text}</p>
              </div>
            ))}
            {chunks.length === 0 && <p className="text-xs text-gray-600">No chunks yet — still parsing, or parsing failed.</p>}
          </div>
        )}
      </div>
    </div>
  )
}
