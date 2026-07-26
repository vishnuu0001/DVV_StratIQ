// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/pages (HeatmapPage.tsx)
// Date: 2026-01-01
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { HeatmapResponse, HeatmapRow } from '../types'
import SectionHeader from '../components/ui/SectionHeader'
import ErrorBanner from '../components/ui/ErrorBanner'
import NoWorkbook from '../components/ui/NoWorkbook'
import { formatCurrencyCompact, formatPctDirect, toNum } from '../utils/format'
import { Grid, List, ArrowUpDown } from 'lucide-react'

const RAG_STYLES: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  Red: {
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    border: 'border-red-500/30',
    dot: 'bg-red-500',
  },
  Amber: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    dot: 'bg-amber-500',
  },
  Green: {
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    border: 'border-emerald-500/30',
    dot: 'bg-emerald-500',
  },
}

// Function: ScoreBar
function ScoreBar({ score }: { score: number }) {
  const max = 10
  const safeScore = toNum(score)
  const pct = Math.min((safeScore / max) * 100, 100)
  const color = safeScore >= 7 ? 'bg-red-500' : safeScore >= 5 ? 'bg-amber-500' : 'bg-emerald-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-navy-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-slate-300 w-8 text-right">{formatPctDirect(safeScore).replace('%', '')}</span>
    </div>
  )
}

// Function: recommendedMove
function recommendedMove(row: Record<string, unknown>, rag: HeatmapRow['rag']) {
  if (row.recommended_move) return String(row.recommended_move)
  if (rag === 'Red') return 'Prioritize for immediate consolidation review'
  if (rag === 'Amber') return 'Assess bundling and selective rationalization'
  return 'Monitor and retain unless commercial trigger emerges'
}

// Function: normalizeHeatmapRows
function normalizeHeatmapRows(data: HeatmapResponse | undefined): HeatmapRow[] {
  const source = data as unknown as { rows?: unknown[]; heatmap?: unknown[] } | undefined
  const raw = (source?.rows ?? source?.heatmap ?? []) as Record<string, unknown>[]

  return raw.map((row) => {
    const rawRag = String(row.rag ?? row.rag_status ?? 'Green')
    const rag: HeatmapRow['rag'] = rawRag === 'Red' || rawRag === 'Amber' ? rawRag : 'Green'
    return {
      tower: String(row.tower ?? ''),
      spend: toNum(row.spend ?? row.annual_spend ?? row.current_spend),
      vendor_count: toNum(row.vendor_count),
      strategic_importance: toNum(row.strategic_importance),
      complexity: toNum(row.complexity),
      consolidation_priority_score: toNum(row.consolidation_priority_score ?? row.score),
      rag,
      recommended_move: recommendedMove(row, rag),
    }
  })
}

// Function: HeatmapCard
function HeatmapCard({ row }: { row: HeatmapRow }) {
  const rag = RAG_STYLES[row.rag] ?? RAG_STYLES.Green
  return (
    <div
      className={`${rag.bg} border ${rag.border} rounded-xl p-5 relative overflow-hidden group transition-all hover:scale-[1.01]`}
      title={row.recommended_move}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="text-sm font-semibold text-slate-200 leading-tight">{row.tower}</div>
        <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${rag.bg} ${rag.text} border ${rag.border}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${rag.dot}`} />
          {row.rag}
        </div>
      </div>

      <div className="space-y-2 text-xs text-slate-400 mb-3">
        <div className="flex justify-between">
          <span>Spend</span>
          <span className="text-slate-300 font-medium">{formatCurrencyCompact(row.spend)}</span>
        </div>
        <div className="flex justify-between">
          <span>Vendors</span>
          <span className="text-slate-300 font-medium">{row.vendor_count}</span>
        </div>
        <div className="flex justify-between">
          <span>Strategic Importance</span>
          <span className="text-slate-300 font-medium">{formatPctDirect(row.strategic_importance).replace('%', '')}</span>
        </div>
        <div className="flex justify-between">
          <span>Complexity</span>
          <span className="text-slate-300 font-medium">{formatPctDirect(row.complexity).replace('%', '')}</span>
        </div>
      </div>

      <div className="space-y-1">
        <div className="flex justify-between text-xs text-slate-500">
          <span>Priority Score</span>
        </div>
        <ScoreBar score={row.consolidation_priority_score} />
      </div>

      <div className={`mt-3 pt-3 border-t ${rag.border} text-xs ${rag.text} opacity-0 group-hover:opacity-100 transition-opacity`}>
        {row.recommended_move}
      </div>
    </div>
  )
}

// Function: HeatmapPage
export default function HeatmapPage() {
  const { workbookId } = useWorkbook()
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid')
  const [sortDesc, setSortDesc] = useState(true)

  const { data, isLoading, error } = useQuery<HeatmapResponse>({
    queryKey: ['vendor-heatmap', workbookId],
    queryFn: () => apiGet<HeatmapResponse>(`/workbooks/${workbookId}/calculations/vendor-heatmap`),
    enabled: !!workbookId,
  })

  if (!workbookId) return <div className="p-8"><NoWorkbook /></div>
  if (error) return <div className="p-8"><ErrorBanner message={error instanceof Error ? error.message : 'Error'} /></div>

  const rows = normalizeHeatmapRows(data).sort((a, b) =>
    sortDesc
      ? b.consolidation_priority_score - a.consolidation_priority_score
      : a.consolidation_priority_score - b.consolidation_priority_score
  )

  const ragCounts = rows.reduce<Record<string, number>>((acc, r) => {
    acc[r.rag] = (acc[r.rag] ?? 0) + 1
    return acc
  }, {})

  return (
    <div className="p-8 space-y-6">
      <SectionHeader
        eyebrow="Consolidation Priority"
        title="Tower Heatmap"
        subtitle="RAG-scored consolidation priority by technology tower"
      />

      {/* Legend + controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          {(['Red', 'Amber', 'Green'] as const).map((rag) => {
            const s = RAG_STYLES[rag]
            return (
              <div key={rag} className="flex items-center gap-2 text-xs">
                <span className={`w-2.5 h-2.5 rounded-full ${s.dot}`} />
                <span className="text-slate-400">{rag}</span>
                <span className={`font-medium ${s.text}`}>{ragCounts[rag] ?? 0} towers</span>
              </div>
            )
          })}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSortDesc(!sortDesc)}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 px-3 py-1.5 bg-navy-800 border border-navy-700 rounded-lg"
          >
            <ArrowUpDown size={12} />
            {sortDesc ? 'Highest First' : 'Lowest First'}
          </button>
          <div className="flex bg-navy-800 border border-navy-700 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 transition-colors ${viewMode === 'grid' ? 'bg-accent-blue/20 text-accent-blue' : 'text-slate-500 hover:text-slate-300'}`}
            >
              <Grid size={14} />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`p-2 transition-colors ${viewMode === 'table' ? 'bg-accent-blue/20 text-accent-blue' : 'text-slate-500 hover:text-slate-300'}`}
            >
              <List size={14} />
            </button>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => <div key={i} className="h-48 skeleton-shimmer rounded-xl" />)}
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {rows.map((row) => <HeatmapCard key={row.tower} row={row} />)}
        </div>
      ) : (
        <div className="bg-navy-800 border border-navy-700 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-navy-700">
                  {['Tower', 'Spend', 'Vendors', 'Strategic', 'Complexity', 'Score', 'RAG', 'Recommended Move'].map((h) => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500 whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => {
                  const rag = RAG_STYLES[row.rag] ?? RAG_STYLES.Green
                  return (
                    <tr key={row.tower} className="border-b border-navy-700/50 hover:bg-navy-700/30 transition-colors">
                      <td className="px-4 py-3 text-sm text-slate-200 font-medium">{row.tower}</td>
                      <td className="px-4 py-3 text-sm font-mono text-slate-300">{formatCurrencyCompact(row.spend)}</td>
                      <td className="px-4 py-3 text-sm text-slate-400 text-center">{row.vendor_count}</td>
                      <td className="px-4 py-3 text-sm text-slate-400 text-center">{formatPctDirect(row.strategic_importance).replace('%', '')}</td>
                      <td className="px-4 py-3 text-sm text-slate-400 text-center">{formatPctDirect(row.complexity).replace('%', '')}</td>
                      <td className="px-4 py-3"><ScoreBar score={row.consolidation_priority_score} /></td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${rag.bg} ${rag.text} border ${rag.border}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${rag.dot}`} />
                          {row.rag}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-400 max-w-xs">{row.recommended_move}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
