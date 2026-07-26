// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/pages (TechMGrowthPage.tsx)
// Date: 2026-03-04
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { TechMGrowthResponse, TechMScenario, OpportunityArea } from '../types'
import SectionHeader from '../components/ui/SectionHeader'
import ErrorBanner from '../components/ui/ErrorBanner'
import NoWorkbook from '../components/ui/NoWorkbook'
import KpiCard from '../components/ui/KpiCard'
import { formatCurrencyCompact, formatPctDirect } from '../utils/format'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const SCENARIO_STYLES: Record<string, { bg: string; border: string; badge: string; accent: string }> = {
  'Current Baseline': {
    bg: 'bg-slate-800/50',
    border: 'border-slate-700',
    badge: 'bg-slate-700 text-slate-300',
    accent: 'text-slate-300',
  },
  Target: {
    bg: 'bg-accent-blue/5',
    border: 'border-accent-blue/30',
    badge: 'bg-accent-blue/20 text-accent-blue',
    accent: 'text-accent-blue',
  },
  Stretch: {
    bg: 'bg-accent-purple/5',
    border: 'border-accent-purple/30',
    badge: 'bg-accent-purple/20 text-accent-purple',
    accent: 'text-accent-purple',
  },
  Aggressive: {
    bg: 'bg-accent-red/5',
    border: 'border-accent-red/30',
    badge: 'bg-accent-red/20 text-accent-red',
    accent: 'text-accent-red',
  },
}

// Function: ScenarioCard
function ScenarioCard({ scenario }: { scenario: TechMScenario }) {
  const style = SCENARIO_STYLES[scenario.scenario] ?? SCENARIO_STYLES['Target']
  return (
    <div className={`${style.bg} border ${style.border} rounded-xl p-6 flex flex-col gap-4`}>
      <div className="flex items-center justify-between">
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${style.badge}`}>
          {scenario.scenario}
        </span>
        <span className="text-xs text-slate-500">{scenario.confidence} confidence</span>
      </div>

      <div>
        <div className="text-xs text-slate-500 mb-1">Year 1 Target</div>
        <div className={`text-2xl font-bold ${style.accent}`}>
          {formatCurrencyCompact(scenario.year_1_target)}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <div className="text-slate-500 mb-0.5">Incremental Growth</div>
          <div className="font-medium text-slate-200">{formatCurrencyCompact(scenario.incremental_growth)}</div>
        </div>
        <div>
          <div className="text-slate-500 mb-0.5">Growth %</div>
          <div className={`font-medium ${style.accent}`}>{formatPctDirect(scenario.growth_pct)}</div>
        </div>
        <div>
          <div className="text-slate-500 mb-0.5">Quarterly Run-Rate</div>
          <div className="font-medium text-slate-200">{formatCurrencyCompact(scenario.quarterly_run_rate)}</div>
        </div>
        <div>
          <div className="text-slate-500 mb-0.5">Positioning</div>
          <div className="font-medium text-slate-400 text-xs leading-tight">{scenario.positioning}</div>
        </div>
      </div>
    </div>
  )
}

interface TooltipPayload {
  name: string
  value: number
  color: string
}

// Function: CustomTooltip
function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: TooltipPayload[]; label?: string }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-navy-700 border border-navy-600 rounded-lg p-3 text-xs shadow-xl min-w-[200px]">
      <div className="font-semibold text-slate-200 mb-2">{label}</div>
      {payload.map((p) => (
        <div key={p.name} className="flex justify-between gap-4">
          <span style={{ color: p.color }}>{p.name}</span>
          <span className="text-slate-300 font-medium">{formatCurrencyCompact(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

// Function: TechMGrowthPage
export default function TechMGrowthPage() {
  const { workbookId } = useWorkbook()

  const { data, isLoading, error } = useQuery<TechMGrowthResponse>({
    queryKey: ['techm-growth', workbookId],
    queryFn: () => apiGet<TechMGrowthResponse>(`/workbooks/${workbookId}/calculations/techm-growth`),
    enabled: !!workbookId,
  })

  if (!workbookId) return <div className="p-8"><NoWorkbook /></div>
  if (error) return <div className="p-8"><ErrorBanner message={error instanceof Error ? error.message : 'Error'} /></div>

  const opportunityChartData = (data?.opportunity_areas ?? []).map((o: OpportunityArea) => ({
    area: o.area,
    'Low Case': o.low_case,
    'Expected Case': o.expected_case,
    'High Case': o.high_case,
  }))

  return (
    <div className="p-8 space-y-6">
      <SectionHeader
        eyebrow="Growth Strategy"
        title="Portfolio Growth Scenarios"
        subtitle="Revenue opportunity sizing from technology consolidation positioning"
      />

      {/* Baseline KPI */}
      <div className="max-w-xs">
        <KpiCard
          label="Current TechM Baseline"
          value={data?.current_baseline ?? 0}
          format="currency"
          accent="blue"
          loading={isLoading}
          subtitle="Current annual revenue from Mazda"
        />
      </div>

      {/* Scenario cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-56 skeleton-shimmer rounded-xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {(data?.scenarios ?? []).map((s: TechMScenario) => (
            <ScenarioCard key={s.scenario} scenario={s} />
          ))}
        </div>
      )}

      {/* Opportunity areas chart */}
      <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
        <div className="text-sm font-semibold text-slate-200 mb-1">Opportunity Sizing by Area</div>
        <div className="text-xs text-slate-500 mb-4">Low / Expected / High case scenarios per opportunity area</div>
        {isLoading ? (
          <div className="h-64 skeleton-shimmer rounded-lg" />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={opportunityChartData}
              layout="vertical"
              margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#162338" horizontal={false} />
              <XAxis
                type="number"
                tickFormatter={(v) => formatCurrencyCompact(v)}
                tick={{ fill: '#94a3b8', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="area"
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={130}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: '#162338' }} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              <Bar dataKey="Low Case" fill="#94a3b8" radius={[0, 3, 3, 0]} maxBarSize={14} />
              <Bar dataKey="Expected Case" fill="#3B82F6" radius={[0, 3, 3, 0]} maxBarSize={14} />
              <Bar dataKey="High Case" fill="#8B5CF6" radius={[0, 3, 3, 0]} maxBarSize={14} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
