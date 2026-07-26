// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/pages (TransformationCapacityPage.tsx)
// Date: 2026-04-06
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { TransformationCapacityResponse, CapacityScenario, ReinvestmentAllocation } from '../types'
import SectionHeader from '../components/ui/SectionHeader'
import ErrorBanner from '../components/ui/ErrorBanner'
import NoWorkbook from '../components/ui/NoWorkbook'
import { formatCurrencyCompact, formatPctDirect } from '../utils/format'
import { CheckCircle, Star } from 'lucide-react'
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const SCENARIO_STYLES: Record<string, { bg: string; border: string; accent: string; badge: string }> = {
  Conservative: {
    bg: 'bg-slate-800/50',
    border: 'border-slate-700',
    accent: 'text-slate-300',
    badge: 'bg-slate-700 text-slate-300',
  },
  Target: {
    bg: 'bg-accent-blue/5',
    border: 'border-accent-blue/40',
    accent: 'text-accent-blue',
    badge: 'bg-accent-blue/20 text-accent-blue',
  },
  Aggressive: {
    bg: 'bg-accent-purple/5',
    border: 'border-accent-purple/30',
    accent: 'text-accent-purple',
    badge: 'bg-accent-purple/20 text-accent-purple',
  },
}

const ALLOCATION_COLORS = ['#3B82F6', '#8B5CF6', '#22D3EE', '#34D399', '#FCD34D']

// Function: ScenarioCard
function ScenarioCard({ scenario, isRecommended }: { scenario: CapacityScenario; isRecommended: boolean }) {
  const style = SCENARIO_STYLES[scenario.name] ?? SCENARIO_STYLES.Target
  return (
    <div className={`relative ${style.bg} border ${style.border} rounded-xl p-6`}>
      {isRecommended && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <div className="flex items-center gap-1 px-3 py-1 bg-accent-blue text-white text-xs font-bold rounded-full shadow-lg">
            <Star size={10} />
            Recommended
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${style.badge}`}>
          {scenario.name}
        </span>
        <span className={`text-xs font-medium ${style.accent}`}>
          {formatPctDirect(scenario.optimization_rate * 100)} opt. rate
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="text-xs text-slate-500 mb-1">Capacity Created</div>
          <div className={`text-2xl font-bold ${style.accent}`}>
            {formatCurrencyCompact(scenario.capacity_created)}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500 mb-1">Reinvestment Pool</div>
          <div className="text-lg font-semibold text-slate-200">
            {formatCurrencyCompact(scenario.reinvestment_pool)}
          </div>
        </div>

        {/* Progress bar */}
        <div>
          <div className="h-1.5 bg-navy-700 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${isRecommended ? 'bg-accent-blue' : 'bg-slate-600'}`}
              style={{ width: `${Math.min(scenario.optimization_rate * 100 * 4, 100)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

interface TooltipPayload {
  name: string
  value: number
  payload: ReinvestmentAllocation
}

// Function: AllocationTooltip
function AllocationTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload?.length) return null
  const item = payload[0]
  return (
    <div className="bg-navy-700 border border-navy-600 rounded-lg p-3 text-xs shadow-xl">
      <div className="font-semibold text-slate-200 mb-1">{item.name}</div>
      <div className="text-slate-300">{formatCurrencyCompact(item.payload.funding)}</div>
      <div className="text-slate-500">{item.payload.allocation_pct.toFixed(1)}% of pool</div>
    </div>
  )
}

// Function: TransformationCapacityPage
export default function TransformationCapacityPage() {
  const { workbookId } = useWorkbook()

  const { data, isLoading, error } = useQuery<TransformationCapacityResponse>({
    queryKey: ['transformation-capacity', workbookId],
    queryFn: () => apiGet<TransformationCapacityResponse>(`/workbooks/${workbookId}/calculations/transformation-capacity`),
    enabled: !!workbookId,
  })

  if (!workbookId) return <div className="p-8"><NoWorkbook /></div>
  if (error) return <div className="p-8"><ErrorBanner message={error instanceof Error ? error.message : 'Error'} /></div>

  const allocations = data?.reinvestment_allocations ?? []
  const recommended = data?.recommended_scenario ?? 'Target'

  return (
    <div className="p-8 space-y-8">
      <SectionHeader
        eyebrow="Value Creation"
        title="Transformation Capacity"
        subtitle="Capacity creation and reinvestment allocation model"
      />

      {/* Narrative banner */}
      <div className="flex items-start gap-3 p-4 bg-accent-cyan/5 border border-accent-cyan/20 rounded-xl">
        <CheckCircle size={16} className="text-accent-cyan shrink-0 mt-0.5" />
        <div className="text-sm text-slate-300">
          <span className="font-semibold text-accent-cyan">Strategic Framing: </span>
          Position this as <span className="font-medium text-slate-200">transformation capacity creation</span>, not cost take-out.
          The savings fund a reinvestment pool that accelerates digital transformation initiatives.
        </div>
      </div>

      {/* Scenario cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          {[...Array(3)].map((_, i) => <div key={i} className="h-52 skeleton-shimmer rounded-xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mt-4">
          {(data?.scenarios ?? []).map((s: CapacityScenario) => (
            <ScenarioCard key={s.name} scenario={s} isRecommended={s.name === recommended} />
          ))}
        </div>
      )}

      {/* Reinvestment allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
          <div className="text-sm font-semibold text-slate-200 mb-1">Reinvestment Allocation</div>
          <div className="text-xs text-slate-500 mb-4">How the capacity pool is deployed</div>
          {isLoading ? (
            <div className="h-64 skeleton-shimmer rounded-lg" />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={allocations}
                  cx="45%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={95}
                  dataKey="funding"
                  nameKey="area"
                  paddingAngle={2}
                >
                  {allocations.map((_, index) => (
                    <Cell key={index} fill={ALLOCATION_COLORS[index % ALLOCATION_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<AllocationTooltip />} />
                <Legend
                  layout="vertical"
                  align="right"
                  verticalAlign="middle"
                  wrapperStyle={{ fontSize: 11, color: '#94a3b8' }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
          <div className="text-sm font-semibold text-slate-200 mb-4">Allocation Table</div>
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => <div key={i} className="h-8 skeleton-shimmer rounded" />)}
            </div>
          ) : (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-navy-700">
                  <th className="pb-2 text-left font-semibold text-slate-500 uppercase tracking-wider">Area</th>
                  <th className="pb-2 text-right font-semibold text-slate-500 uppercase tracking-wider">%</th>
                  <th className="pb-2 text-right font-semibold text-slate-500 uppercase tracking-wider">Funding</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-700/50">
                {allocations.map((item: ReinvestmentAllocation, i) => (
                  <tr key={item.area} className="hover:bg-navy-700/20">
                    <td className="py-2.5">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-2 h-2 rounded-full shrink-0"
                          style={{ background: ALLOCATION_COLORS[i % ALLOCATION_COLORS.length] }}
                        />
                        <span className="text-slate-300">{item.area}</span>
                      </div>
                    </td>
                    <td className="py-2.5 text-right text-slate-400">{item.allocation_pct.toFixed(1)}%</td>
                    <td className="py-2.5 text-right font-medium font-mono text-slate-200">
                      {formatCurrencyCompact(item.funding)}
                    </td>
                  </tr>
                ))}
              </tbody>
              {data?.total_capacity && (
                <tfoot>
                  <tr className="border-t border-navy-700">
                    <td className="pt-2.5 font-semibold text-slate-200">Total</td>
                    <td className="pt-2.5 text-right font-semibold text-slate-300">100%</td>
                    <td className="pt-2.5 text-right font-bold font-mono text-accent-blue">
                      {formatCurrencyCompact(data.total_capacity)}
                    </td>
                  </tr>
                </tfoot>
              )}
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
