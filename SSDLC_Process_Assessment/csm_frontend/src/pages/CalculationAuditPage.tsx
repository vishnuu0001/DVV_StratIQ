// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/pages (CalculationAuditPage.tsx)
// Date: 2025-09-12
// ---------------------------------------------------------------------------
import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { CalculationAuditEntry } from '../types'
import SectionHeader from '../components/ui/SectionHeader'
import ErrorBanner from '../components/ui/ErrorBanner'
import NoWorkbook from '../components/ui/NoWorkbook'
import { formatCurrencyCompact } from '../utils/format'
import { Search, Download, ChevronDown, ChevronRight } from 'lucide-react'

interface AuditResponse {
  entries: CalculationAuditEntry[]
  generated_at?: string
}

// Function: AuditEntryRow
function AuditEntryRow({ entry }: { entry: CalculationAuditEntry }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="border border-navy-700 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-navy-700/30 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? (
          <ChevronDown size={14} className="text-slate-500 shrink-0" />
        ) : (
          <ChevronRight size={14} className="text-slate-500 shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-slate-200 truncate">{entry.metric}</div>
          <div className="text-xs text-slate-500 font-mono truncate mt-0.5">{entry.formula}</div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-sm font-bold text-accent-blue font-mono">{formatCurrencyCompact(entry.result)}</div>
          {entry.source_refs?.length > 0 && (
            <div className="text-xs text-slate-600 mt-0.5">{entry.source_refs[0]}</div>
          )}
        </div>
      </button>

      {expanded && (
        <div className="px-5 pb-4 border-t border-navy-700 bg-navy-800/50">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
            {/* Formula */}
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Formula</div>
              <div className="bg-navy-900 border border-navy-700 rounded-lg px-4 py-3 font-mono text-xs text-accent-cyan break-all">
                {entry.formula}
              </div>
            </div>

            {/* Source refs */}
            {entry.source_refs?.length > 0 && (
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Source References</div>
                <div className="flex flex-wrap gap-2">
                  {entry.source_refs.map((ref) => (
                    <span key={ref} className="inline-flex items-center px-2 py-0.5 bg-navy-700/50 border border-navy-600 rounded text-xs font-mono text-slate-300">
                      {ref}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Inputs */}
            {entry.inputs && Object.keys(entry.inputs).length > 0 && (
              <div className="lg:col-span-2">
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Inputs</div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                  {Object.entries(entry.inputs).map(([key, value]) => (
                    <div key={key} className="bg-navy-900 border border-navy-700 rounded-lg px-3 py-2">
                      <div className="text-xs text-slate-500 truncate mb-0.5">{key}</div>
                      <div className="text-xs font-mono font-medium text-slate-200">
                        {typeof value === 'number' ? formatCurrencyCompact(value) : String(value)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Function: CalculationAuditPage
export default function CalculationAuditPage() {
  const { workbookId } = useWorkbook()
  const [search, setSearch] = useState('')

  const { data, isLoading, error } = useQuery<AuditResponse>({
    queryKey: ['calculations-audit', workbookId],
    queryFn: () => apiGet<AuditResponse>(`/workbooks/${workbookId}/calculations`),
    enabled: !!workbookId,
  })

  const entries = data?.entries ?? []

  const filtered = useMemo(() => {
    if (!search) return entries
    const q = search.toLowerCase()
    return entries.filter(
      (e) =>
        e.metric.toLowerCase().includes(q) ||
        e.formula.toLowerCase().includes(q) ||
        e.source_refs?.some((r) => r.toLowerCase().includes(q))
    )
  }, [entries, search])

  // Group by first source ref prefix as "service"
  const grouped = useMemo(() => {
    const groups: Record<string, CalculationAuditEntry[]> = {}
    filtered.forEach((e) => {
      const group = e.source_refs?.[0]?.split('!')?.[0] ?? 'General'
      if (!groups[group]) groups[group] = []
      groups[group].push(e)
    })
    return groups
  }, [filtered])

  // Function: exportJson
  const exportJson = () => {
    const blob = new Blob([JSON.stringify(entries, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `csm_calculations_${workbookId ?? 'export'}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!workbookId) return <div className="p-8"><NoWorkbook /></div>
  if (error) return <div className="p-8"><ErrorBanner message={error instanceof Error ? error.message : 'Error'} /></div>

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-start justify-between gap-4">
        <SectionHeader
          eyebrow="Transparency"
          title="Calculation Audit"
          subtitle="Full formula catalog with source references and input values"
        />
        <button
          onClick={exportJson}
          disabled={entries.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-navy-800 hover:bg-navy-700 border border-navy-600 text-slate-300 rounded-lg text-sm transition-colors disabled:opacity-50 shrink-0"
        >
          <Download size={14} />
          Export JSON
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-lg">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          placeholder="Search metrics, formulas, refs..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-navy-800 border border-navy-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-accent-blue"
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-600">
          {filtered.length} results
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 sm:grid-cols-4 gap-4">
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-accent-blue">{entries.length}</div>
          <div className="text-xs text-slate-500">Total Formulas</div>
        </div>
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-accent-purple">{Object.keys(grouped).length}</div>
          <div className="text-xs text-slate-500">Sheets / Groups</div>
        </div>
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-accent-green">{entries.filter((e) => e.result > 0).length}</div>
          <div className="text-xs text-slate-500">Positive Results</div>
        </div>
        {data?.generated_at && (
          <div className="bg-navy-800 border border-navy-700 rounded-xl p-4 text-center">
            <div className="text-sm font-bold text-slate-300">{new Date(data.generated_at).toLocaleDateString()}</div>
            <div className="text-xs text-slate-500">Generated</div>
          </div>
        )}
      </div>

      {/* Formula catalog */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(8)].map((_, i) => <div key={i} className="h-16 skeleton-shimmer rounded-xl" />)}
        </div>
      ) : Object.keys(grouped).length === 0 ? (
        <div className="text-center py-12 text-slate-500 text-sm">No formulas found</div>
      ) : (
        Object.entries(grouped).map(([group, groupEntries]) => (
          <div key={group} className="space-y-2">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 px-1 mb-2">
              {group} <span className="text-slate-600 font-normal">({groupEntries.length})</span>
            </div>
            {groupEntries.map((entry) => (
              <AuditEntryRow key={entry.metric} entry={entry} />
            ))}
          </div>
        ))
      )}
    </div>
  )
}
