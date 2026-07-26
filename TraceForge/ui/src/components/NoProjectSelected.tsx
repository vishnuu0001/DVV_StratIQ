// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/components (NoProjectSelected.tsx)
// Date: 2025-10-20
// ---------------------------------------------------------------------------
// Function: NoProjectSelected
export default function NoProjectSelected() {
  return (
    <div className="flex items-center justify-center h-full text-center">
      <div>
        <p className="text-sm text-gray-400">No project selected.</p>
        <p className="text-xs text-gray-600 mt-1">Pick or create a project in the sidebar to get started.</p>
      </div>
    </div>
  )
}
