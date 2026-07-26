// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/components (SourceBadges.jsx)
// Date: 2025-11-21
// ---------------------------------------------------------------------------
import { FileText } from 'lucide-react'

// Function: SourceBadges
export default function SourceBadges({ sources = [] }) {
  return (
    <div className="flex flex-wrap gap-1">
      {sources.map((s) => (
        <span
          key={s.source}
          title={`Relevance: ${Math.round(s.relevance * 100)}%`}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-brand-50 text-brand-700 text-xs font-medium border border-brand-100"
        >
          <FileText size={11} />
          {s.source}
        </span>
      ))}
    </div>
  )
}
