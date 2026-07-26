// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/pages (ConnectorsPage.tsx)
// Date: 2025-11-25
// ---------------------------------------------------------------------------
import ConnectorForms from '../components/ConnectorForms'
import NoProjectSelected from '../components/NoProjectSelected'
import { useProjectStore } from '../stores/projectStore'

// Function: ConnectorsPage
export default function ConnectorsPage() {
  const { projectId } = useProjectStore()
  if (!projectId) return <NoProjectSelected />
  return (
    <div className="p-6">
      <h1 className="text-sm font-semibold text-white">Connectors</h1>
      <p className="mb-4 mt-1 text-xs text-gray-500">
        Run credential-isolated imports from enterprise systems. Credentials are never persisted.
      </p>
      <div className="max-w-3xl"><ConnectorForms /></div>
    </div>
  )
}
