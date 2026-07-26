// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/pages (NotFoundPage.tsx)
// Date: 2025-11-07
// ---------------------------------------------------------------------------
import { Link } from 'react-router-dom'
import { Upload, Home } from 'lucide-react'

// Function: NotFoundPage
export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-navy-900 flex flex-col items-center justify-center gap-6 text-center p-8">
      <div className="text-8xl font-black text-navy-700">404</div>
      <div>
        <h1 className="text-2xl font-bold text-slate-200 mb-2">Page Not Found</h1>
        <p className="text-slate-500 text-sm max-w-sm">
          The page you're looking for doesn't exist or has been moved.
        </p>
      </div>
      <div className="flex gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 bg-navy-800 hover:bg-navy-700 border border-navy-700 text-slate-300 rounded-lg text-sm transition-colors"
        >
          <Upload size={14} />
          Upload
        </Link>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-4 py-2 bg-accent-blue hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Home size={14} />
          Dashboard
        </Link>
      </div>
    </div>
  )
}
