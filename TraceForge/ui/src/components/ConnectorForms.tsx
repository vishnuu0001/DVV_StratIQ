// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/components (ConnectorForms.tsx)
// Date: 2026-07-07
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Database, GitBranch, Ticket } from 'lucide-react'
import api from '../api/client'
import { useProjectStore } from '../stores/projectStore'

const inputCls = 'w-full bg-gray-800 border border-white/10 rounded px-2 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'
const TABS = ['ServiceNow', 'JIRA', 'GitHub'] as const

// Function: ConnectorForms
export default function ConnectorForms() {
  const { projectId } = useProjectStore()
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<(typeof TABS)[number]>('ServiceNow')
  const [result, setResult] = useState<string | null>(null)

  const [snow, setSnow] = useState({ base_url: '', username: '', password: '', window_months: 12, verify_ssl: false })
  const [jira, setJira] = useState({ base_url: '', email: '', api_token: '', jql: 'project = PROJ ORDER BY created DESC' })
  const [github, setGithub] = useState({ repo_url: '', token: '' })

  // Function: invalidateSources
  const invalidateSources = () => queryClient.invalidateQueries({ queryKey: ['sources', projectId] })

  const snowMutation = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/sources/servicenow`, {
      base_url: snow.base_url, username: snow.username, password: snow.password,
      window_months: snow.window_months, verify_ssl: snow.verify_ssl,
    })).data,
    onSuccess: () => { setResult('ServiceNow ingestion queued — check back in a minute.'); invalidateSources() },
    onError: (e: any) => setResult(e.response?.data?.detail || 'ServiceNow ingestion failed to queue.'),
  })

  const jiraMutation = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/sources/jira`, jira)).data,
    onSuccess: () => { setResult('JIRA ingestion queued — check back in a minute.'); invalidateSources() },
    onError: (e: any) => setResult(e.response?.data?.detail || 'JIRA ingestion failed to queue.'),
  })

  const githubMutation = useMutation({
    mutationFn: async () => (await api.post(`/projects/${projectId}/sources/github`, github)).data,
    onSuccess: () => { setResult('GitHub ingestion queued — cloning can take a minute.'); invalidateSources() },
    onError: (e: any) => setResult(e.response?.data?.detail || 'GitHub ingestion failed to queue.'),
  })

  return (
    <div className="bg-gray-900 border border-white/10 rounded-lg p-3 mb-4">
      <div className="flex gap-1 mb-3">
        {TABS.map((t) => (
          <button key={t} onClick={() => { setTab(t); setResult(null) }}
            className={`text-xs px-2 py-1 rounded ${tab === t ? 'bg-blue-600/20 text-blue-300' : 'text-gray-500 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>
      <p className="text-[10px] text-gray-600 mb-2">Credentials are used for this request only and are not stored.</p>

      {tab === 'ServiceNow' && (
        <div className="space-y-1.5">
          <input className={inputCls} placeholder="https://instance.service-now.com" value={snow.base_url} onChange={(e) => setSnow((v) => ({ ...v, base_url: e.target.value }))} />
          <div className="grid grid-cols-2 gap-1.5">
            <input className={inputCls} placeholder="Username" value={snow.username} onChange={(e) => setSnow((v) => ({ ...v, username: e.target.value }))} />
            <input className={inputCls} type="password" placeholder="Password" value={snow.password} onChange={(e) => setSnow((v) => ({ ...v, password: e.target.value }))} />
          </div>
          <button onClick={() => snowMutation.mutate()} disabled={!snow.base_url || !snow.username || snowMutation.isPending}
            className="w-full flex items-center justify-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded py-1.5">
            <Database size={12} /> Sync incidents, requests, changes, KB, CMDB glossary
          </button>
        </div>
      )}

      {tab === 'JIRA' && (
        <div className="space-y-1.5">
          <input className={inputCls} placeholder="https://yourcompany.atlassian.net" value={jira.base_url} onChange={(e) => setJira((v) => ({ ...v, base_url: e.target.value }))} />
          <div className="grid grid-cols-2 gap-1.5">
            <input className={inputCls} placeholder="Email" value={jira.email} onChange={(e) => setJira((v) => ({ ...v, email: e.target.value }))} />
            <input className={inputCls} type="password" placeholder="API token" value={jira.api_token} onChange={(e) => setJira((v) => ({ ...v, api_token: e.target.value }))} />
          </div>
          <input className={inputCls} placeholder="JQL query" value={jira.jql} onChange={(e) => setJira((v) => ({ ...v, jql: e.target.value }))} />
          <button onClick={() => jiraMutation.mutate()} disabled={!jira.base_url || !jira.email || jiraMutation.isPending}
            className="w-full flex items-center justify-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded py-1.5">
            <Ticket size={12} /> Import issues
          </button>
        </div>
      )}

      {tab === 'GitHub' && (
        <div className="space-y-1.5">
          <input className={inputCls} placeholder="https://github.com/org/repo.git" value={github.repo_url} onChange={(e) => setGithub((v) => ({ ...v, repo_url: e.target.value }))} />
          <input className={inputCls} type="password" placeholder="Personal access token (optional for public repos)" value={github.token} onChange={(e) => setGithub((v) => ({ ...v, token: e.target.value }))} />
          <button onClick={() => githubMutation.mutate()} disabled={!github.repo_url || githubMutation.isPending}
            className="w-full flex items-center justify-center gap-1 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded py-1.5">
            <GitBranch size={12} /> Clone &amp; parse repository
          </button>
        </div>
      )}

      {result && <p className="text-[11px] text-amber-300 mt-2">{result}</p>}
    </div>
  )
}
