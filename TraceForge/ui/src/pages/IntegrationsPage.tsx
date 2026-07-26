// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (IntegrationsPage.tsx)
// Date: 2026-05-19
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import NoProjectSelected from '../components/NoProjectSelected'
import { useProjectStore } from '../stores/projectStore'

interface Integration { id: string; connector_type: string; config: Record<string, unknown> }

// Function: IntegrationsPage
export default function IntegrationsPage() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [connectorType, setConnectorType] = useState('JIRA')
  const [baseUrl, setBaseUrl] = useState('')
  const [projectKey, setProjectKey] = useState('')
  const { data: integrations = [] } = useQuery<Integration[]>({
    queryKey: ['integrations', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/integrations`)).data,
    enabled: !!projectId,
  })
  const save = useMutation({
    mutationFn: async () => (await api.put(`/projects/${projectId}/integrations/${connectorType}`, {
      connector_type: connectorType,
      config: { base_url: baseUrl, project_key: projectKey },
    })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['integrations', projectId] }),
    onError: (error: any) => window.alert(error.response?.data?.detail || 'Integration settings could not be saved.'),
  })
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-sm font-semibold text-white">Integrations</h1>
        <p className="mt-1 text-xs text-gray-500">Store non-secret endpoints and project mappings. Runtime credentials remain request-scoped.</p>
      </div>
      <div className="grid max-w-3xl grid-cols-4 gap-2 rounded-lg border border-white/10 bg-gray-900 p-3">
        <select value={connectorType} onChange={(event) => setConnectorType(event.target.value)}
          className="rounded border border-white/10 bg-gray-800 px-2 py-1.5 text-xs">
          <option>SERVICENOW</option><option>JIRA</option><option>GITHUB</option>
        </select>
        <input value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} placeholder="Base URL / repository"
          className="col-span-2 rounded border border-white/10 bg-gray-800 px-2 py-1.5 text-xs" />
        <input value={projectKey} onChange={(event) => setProjectKey(event.target.value)} placeholder="Project key"
          className="rounded border border-white/10 bg-gray-800 px-2 py-1.5 text-xs" />
        <button onClick={() => save.mutate()} disabled={!baseUrl.trim() || save.isPending}
          className="col-start-4 rounded bg-blue-600 px-3 py-1.5 text-xs disabled:opacity-50">Save mapping</button>
      </div>
      {integrations.map((integration) => (
        <div key={integration.id} className="max-w-3xl rounded-lg border border-white/10 bg-gray-900 p-3">
          <p className="text-xs text-white">{integration.connector_type}</p>
          <pre className="mt-2 text-[10px] text-gray-400">{JSON.stringify(integration.config, null, 2)}</pre>
        </div>
      ))}
    </div>
  )
}
