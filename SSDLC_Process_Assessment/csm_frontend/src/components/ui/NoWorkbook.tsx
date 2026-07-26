// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/components/ui (NoWorkbook.tsx)
// Date: 2026-06-21
// ---------------------------------------------------------------------------
import { Link } from 'react-router-dom'
import { Upload } from 'lucide-react'

// Function: NoWorkbook
export default function NoWorkbook() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 text-center">
      <div className="flex items-center justify-center w-16 h-16 bg-accent-blue/10 rounded-2xl">
        <Upload size={28} className="text-accent-blue" />
      </div>
      <div>
        <h3 className="text-xl font-semibold text-slate-200 mb-2">No Workbook Uploaded</h3>
        <p className="text-slate-400 text-sm max-w-sm">
          Please upload a Consolidation_Savings_Model.xlsx file to view this page.
        </p>
      </div>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-5 py-2.5 bg-accent-blue hover:bg-blue-500 text-white rounded-lg font-medium text-sm transition-colors"
      >
        <Upload size={16} />
        Go to Upload
      </Link>
    </div>
  )
}
