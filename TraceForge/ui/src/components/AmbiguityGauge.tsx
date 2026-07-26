// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/components (AmbiguityGauge.tsx)
// Date: 2025-11-18
// ---------------------------------------------------------------------------
// Function: AmbiguityGauge
export default function AmbiguityGauge({ score }: { score: number }) {
  const color = score < 0.2 ? 'bg-emerald-500' : score < 0.4 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-1.5">
      <div className="w-12 h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${Math.round(score * 100)}%` }} />
      </div>
      <span className="text-[10px] text-gray-500 tabular-nums">{score.toFixed(2)}</span>
    </div>
  )
}
