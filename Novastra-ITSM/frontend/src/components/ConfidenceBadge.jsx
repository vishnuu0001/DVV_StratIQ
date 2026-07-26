// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/components (ConfidenceBadge.jsx)
// Date: 2025-11-26
// ---------------------------------------------------------------------------
import { clsx } from 'clsx'

// Function: ConfidenceBadge
export default function ConfidenceBadge({ value, contextUsed }) {
  if (!contextUsed) {
    return (
      <span className="badge bg-gray-100 text-gray-500">
        ⚠ Limited knowledge base evidence
      </span>
    )
  }

  const pct = Math.round(value * 100)
  const color =
    pct >= 70 ? 'bg-green-100 text-green-700' :
    pct >= 45 ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-600'

  return (
    <span className={clsx('badge', color)}>
      Confidence: {pct}%
    </span>
  )
}
