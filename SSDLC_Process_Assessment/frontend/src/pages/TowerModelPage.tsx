// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/pages (TowerModelPage.tsx)
// Date: 2026-06-19
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiGet, apiPost } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { TowerModelResponse, TowerModelRow, ScenarioRequest } from '../types'
import SectionHeader from '../components/ui/SectionHeader'
import ErrorBanner from '../components/ui/ErrorBanner'
import NoWorkbook from '../components/ui/NoWorkbook'
import { formatCurrencyCompact, formatPctDirect } from '../utils/format'
import { Play, X, ChevronDown, ChevronUp } from 'lucide-react'

// Function: SliderField
function SliderField({
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  onChange: (v: number) => void
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="text-accent-blue font-medium">{value.toFixed(1)}%</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-1.5 rounded-full appearance-none cursor-pointer bg-navy-600 accent-accent-blue"
      />
      <div className="flex justify-between text-xs text-slate-600">
        <span>{min}%</span>
        <span>{max}%</span>
      </div>
    </div>
  )
}

const COL_HEADERS = [
  'Tower', 'Current Spend', 'Scope %', 'Addressable',
  'Productivity', 'Rate Savings', 'VM Savings', 'Gross Savings',
  'Transition', 'Net Y1', 'Run-Rate',
]

// Function: TowerRow
function TowerRow({
  row,
  isTotal = false,
  onClick,
}: {
  row: TowerModelRow
  isTotal?: boolean
  onClick?: () => void
}) {
  const base = isTotal
    ? 'bg-navy-700/50 text-slate-200 font-semibold'
    : 'hover:bg-navy-700/30 cursor-pointer text-slate-300'

  return (
    <tr className={`border-b border-navy-700 transition-colors ${base}`} onClick={onClick}>
      <td className="px-4 py-3 text-sm whitespace-nowrap">{row.tower}</td>
      <td className="px-4 py-3 text-sm text-right font-mono">{formatCurrencyCompact(row.current_spend)}</td>
      <td className="px-4 py-3 text-sm text-right">{formatPctDirect(row.consolidation_scope_pct * 100)}</td>
      <td className="px-4 py-3 text-sm text-right font-mono">{formatCurrencyCompact(row.addressable_spend)}</td>
      <td className="px-4 py-3 text-sm text-right font-mono text-accent-green">{formatCurrencyCompact(row.productivity_savings)}</td>
      <td className="px-4 py-3 text-sm text-right font-mono text-accent-green">{formatCurrencyCompact(row.rate_savings)}</td>
      <td className="px-4 py-3 text-sm text-right font-mono text-accent-cyan">{formatCurrencyCompact(row.vm_savings)}</td>
      <td className="px-4 py-3 text-sm text-right font-mono text-accent-green font-semibold">{formatCurrencyCompact(row.gross_savings)}</td>
      <td className="px-4 py-3 text-sm text-right font-mono text-accent-amber">{formatCurrencyCompact(row.transition_cost)}</td>
      <td className="px-4 py-3 text-sm text-right font-mono text-accent-blue font-semibold">{formatCurrencyCompact(row.net_year_1_savings)}</td>
      <td className="px-4 py-3 text-sm text-right font-mono text-accent-purple">{formatCurrencyCompact(row.run_rate_savings)}</td>
    </tr>
  )
}

// Function: TowerModelPage
export default function TowerModelPage() {
  const { workbookId } = useWorkbook()
  const [rateCompression, setRateCompression] = useState(5)
  const [productivity, setProductivity] = useState(10)
  const [transitionCost, setTransitionCost] = useState(8)
  const [selectedRow, setSelectedRow] = useState<TowerModelRow | null>(null)
  const [scenarioResult, setScenarioResult] = useState<TowerModelResponse | null>(null)

  const { data: baseData, isLoading, error } = useQuery<TowerModelResponse>({
    queryKey: ['tower-model', workbookId],
    queryFn: () => apiGet<TowerModelResponse>(`/workbooks/${workbookId}/calculations/tower-model`),
    enabled: !!workbookId,
  })

  const mutation = useMutation<TowerModelResponse, Error, ScenarioRequest>({
    mutationFn: (req) => apiPost<TowerModelResponse>(`/workbooks/${workbookId}/scenarios/run`, req),
    onSuccess: (data) => setScenarioResult(data),
  })

  // Function: runScenario
  const runScenario = () => {
    mutation.mutate({
      scenario_name: 'Custom Scenario',
      rate_compression_pct: rateCompression,
      productivity_improvement_pct: productivity,
      transition_cost_pct: transitionCost,
      tower_scope_overrides: {},
    })
  }

  if (!workbookId) return <div className="p-8"><NoWorkbook /></div>
  if (error) return <div className="p-8"><ErrorBanner message={error.message} /></div>

  const displayData = scenarioResult ?? baseData
  const rows = displayData?.rows ?? []
  const totals = displayData?.totals

  return (
    <div className="p-8 space-y-6">
      <SectionHeader
        eyebrow="Financial Model"
        title="Tower Savings Model"
        subtitle="Interactive scenario modeling across technology towers"
      />

      {/* Scenario Controls */}
      <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm font-semibold text-slate-200">Scenario Controls</div>
          {scenarioResult && (
            <button
              onClick={() => setScenarioResult(null)}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200"
            >
              <X size={12} />
              Reset to Base
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <SliderField
            label="Rate Compression"
            value={rateCompression}
            min={0}
            max={25}
            step={0.5}
            onChange={setRateCompression}
          />
          <SliderField
            label="Productivity Improvement"
            value={productivity}
            min={0}
            max={20}
            step={0.5}
            onChange={setProductivity}
          />
          <SliderField
            label="Transition Cost"
            value={transitionCost}
            min={0}
            max={15}
            step={0.5}
            onChange={setTransitionCost}
          />
        </div>
        <div className="mt-4 flex justify-end">
          <button
            onClick={runScenario}
            disabled={mutation.isPending}
            className="flex items-center gap-2 px-5 py-2 bg-accent-blue hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-sm font-semibold transition-colors"
          >
            {mutation.isPending ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Play size={14} />
            )}
            Run Scenario
          </button>
        </div>
        {mutation.error && (
          <div className="mt-3">
            <ErrorBanner message={mutation.error.message} />
          </div>
        )}
      </div>

      {/* Table */}
      <div className="bg-navy-800 border border-navy-700 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-navy-700">
          <div className="text-sm font-semibold text-slate-200">
            {scenarioResult ? `Scenario: ${scenarioResult.scenario_name}` : 'Base Case'}
          </div>
          <div className="text-xs text-slate-500">Click a row for formula detail</div>
        </div>
        {isLoading ? (
          <div className="p-8 space-y-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-10 skeleton-shimmer rounded" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-navy-700">
                  {COL_HEADERS.map((h) => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500 whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <TowerRow
                    key={row.tower}
                    row={row}
                    onClick={() => setSelectedRow(selectedRow?.tower === row.tower ? null : row)}
                  />
                ))}
                {totals && (
                  <TowerRow row={{ ...totals, tower: 'TOTAL' }} isTotal />
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Row detail drawer */}
      {selectedRow && (
        <div className="bg-navy-800 border border-accent-blue/30 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm font-semibold text-slate-200">{selectedRow.tower} · Formula Breakdown</div>
            <button onClick={() => setSelectedRow(null)} className="text-slate-500 hover:text-slate-300">
              <X size={16} />
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            {[
              { label: 'Current Spend', value: formatCurrencyCompact(selectedRow.current_spend), color: 'text-slate-300' },
              { label: 'Scope %', value: formatPctDirect(selectedRow.consolidation_scope_pct * 100), color: 'text-accent-cyan' },
              { label: 'Addressable', value: formatCurrencyCompact(selectedRow.addressable_spend), color: 'text-accent-cyan' },
              { label: 'Gross Savings', value: formatCurrencyCompact(selectedRow.gross_savings), color: 'text-accent-green' },
              { label: 'Transition Cost', value: formatCurrencyCompact(selectedRow.transition_cost), color: 'text-accent-amber' },
              { label: 'Net Year 1', value: formatCurrencyCompact(selectedRow.net_year_1_savings), color: 'text-accent-blue' },
              { label: 'Run-Rate', value: formatCurrencyCompact(selectedRow.run_rate_savings), color: 'text-accent-purple' },
              { label: 'Vendors', value: String(selectedRow.vendor_count ?? '-'), color: 'text-slate-300' },
            ].map((item) => (
              <div key={item.label} className="bg-navy-700/40 rounded-lg p-3">
                <div className="text-slate-500 mb-1">{item.label}</div>
                <div className={`font-semibold ${item.color}`}>{item.value}</div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 bg-navy-700/30 rounded-lg text-xs text-slate-500 font-mono">
            Addressable = Current Spend × Scope% &nbsp;|&nbsp;
            Gross = Addressable × (Rate% + Productivity% + VM%) &nbsp;|&nbsp;
            Net Y1 = Gross − Transition Cost
          </div>
        </div>
      )}
    </div>
  )
}
