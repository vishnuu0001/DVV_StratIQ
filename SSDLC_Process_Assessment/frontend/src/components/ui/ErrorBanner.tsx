// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/components/ui (ErrorBanner.tsx)
// Date: 2025-07-25
// ---------------------------------------------------------------------------
import { AlertTriangle } from 'lucide-react'

interface ErrorBannerProps {
  message: string
}

// Function: ErrorBanner
export default function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <div className="flex items-start gap-3 p-4 bg-accent-red/10 border border-accent-red/30 rounded-xl text-accent-red text-sm">
      <AlertTriangle size={16} className="shrink-0 mt-0.5" />
      <div>
        <div className="font-semibold mb-0.5">Error</div>
        <div className="text-slate-300">{message}</div>
      </div>
    </div>
  )
}
