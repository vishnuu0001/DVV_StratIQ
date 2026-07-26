// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (AuditPage.tsx)
// Date: 2026-06-08
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import type { AuditEventOut } from '../api/types'
import { useProjectStore } from '../stores/projectStore'
import NoProjectSelected from '../components/NoProjectSelected'

// Function: AuditPage
export default function AuditPage() {
  const { projectId } = useProjectStore()

  const { data: events = [] } = useQuery<AuditEventOut[]>({
    queryKey: ['audit', projectId],
    queryFn: async () => (await api.get(`/projects/${projectId}/audit`)).data,
    enabled: !!projectId,
  })

  if (!projectId) return <NoProjectSelected />

  return (
    <div className="p-6">
      <h1 className="text-sm font-semibold text-white mb-1">Audit Trail</h1>
      <p className="text-xs text-gray-500 mb-4">Append-only (spec P7) — every approval, edit, and state transition.</p>
      <div className="space-y-1">
        {events.map((event) => (
          <div key={event.id} className="flex items-center gap-3 bg-gray-900 border border-white/10 rounded px-3 py-2 text-xs">
            <span className="text-gray-600 w-40 shrink-0">{new Date(event.at).toLocaleString()}</span>
            <span className="text-blue-300 w-36 shrink-0 truncate">{event.actor}</span>
            <span className="text-gray-300 w-48 shrink-0">{event.action}</span>
            <span className="text-gray-500 truncate">{event.entity_type} {event.entity_id.slice(0, 8)}</span>
          </div>
        ))}
        {events.length === 0 && <p className="text-xs text-gray-600 py-6 text-center">No audit events yet.</p>}
      </div>
    </div>
  )
}
