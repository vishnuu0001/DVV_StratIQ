// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/pages (DashboardPage.tsx)
// Date: 2025-12-21
// ---------------------------------------------------------------------------
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { DashboardResponse } from '../types'
import KpiCard from '../components/ui/KpiCard'
import SectionHeader from '../components/ui/SectionHeader'
import ErrorBanner from '../components/ui/ErrorBanner'
import NoWorkbook from '../components/ui/NoWorkbook'
import SpendByCategoryChart from '../components/charts/SpendByCategoryChart'
import TowerSavingsChart from '../components/charts/TowerSavingsChart'
import WaterfallChart from '../components/charts/WaterfallChart'
import TopVendorsChart from '../components/charts/TopVendorsChart'
import { CheckCircle, AlertTriangle } from 'lucide-react'

// Function: DashboardPage
export default function DashboardPage() {
  const { workbookId } = useWorkbook()

  const { data, isLoading, error } = useQuery<DashboardResponse>({
    queryKey: ['dashboard', workbookId],
    queryFn: () => apiGet<DashboardResponse>(`/workbooks/${workbookId}/dashboard`),
    enabled: !!workbookId,
  })

  if (!workbookId) return <div className="p-8"><NoWorkbook /></div>

  if (error) return (
    <div className="p-8">
      <ErrorBanner message={error instanceof Error ? error.message : 'Failed to load dashboard'} />
    </div>
  )

  const kpis = data?.kpis

  return (
    <div className="p-8 space-y-8">
      <SectionHeader
        eyebrow="Executive Summary"
        title="Consolidation Savings Dashboard"
        subtitle="Total technology spend analysis with consolidation opportunity sizing"
      />

      {/* KPI Grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        <KpiCard
          label="Total Technology Spend"
          value={kpis?.total_technology_spend ?? 0}
          format="currency"
          accent="blue"
          loading={isLoading}
          subtitle="All-in technology cost base"
        />
        <KpiCard
          label="Direct Tech OpEx"
          value={kpis?.direct_tech_opex ?? 0}
          format="currency"
          accent="blue"
          loading={isLoading}
          subtitle="Operating expenditure"
        />
        <KpiCard
          label="Third-Party Spend"
          value={kpis?.total_third_party_spend ?? 0}
          format="currency"
          accent="purple"
          loading={isLoading}
          subtitle="External vendor spend"
        />
        <KpiCard
          label="External Talent Spend"
          value={kpis?.external_talent_spend ?? 0}
          format="currency"
          accent="purple"
          loading={isLoading}
          subtitle="Contractor & staff aug"
        />
        <KpiCard
          label="Addressable Spend"
          value={kpis?.addressable_spend ?? 0}
          format="currency"
          accent="cyan"
          loading={isLoading}
          subtitle="In-scope for consolidation"
        />
        <KpiCard
          label="Gross Capacity Created"
          value={kpis?.gross_annual_capacity_created ?? 0}
          format="currency"
          accent="green"
          loading={isLoading}
          subtitle="Pre-transition gross savings"
        />
        <KpiCard
          label="Transition Cost"
          value={kpis?.transition_cost ?? 0}
          format="currency"
          accent="amber"
          loading={isLoading}
          subtitle="One-time transition investment"
        />
        <KpiCard
          label="Net Year 1 Capacity"
          value={kpis?.net_year_1_capacity_created ?? 0}
          format="currency"
          accent="green"
          loading={isLoading}
          subtitle="Primary value creation KPI"
        />
        <KpiCard
          label="Run-Rate Annual"
          value={kpis?.run_rate_annual_capacity_created ?? 0}
          format="currency"
          accent="green"
          loading={isLoading}
          subtitle="Steady-state annual savings"
        />
      </div>

      {/* Executive Story */}
      {(data?.executive_story?.length ?? 0) > 0 && (
        <div>
          <SectionHeader
            eyebrow="Narrative"
            title="Executive Story"
            subtitle="Key insights and value creation narrative"
          />
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data!.executive_story.map((bullet) => (
              <div
                key={bullet.metric_key}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4"
              >
                <div className="text-xs font-semibold uppercase tracking-wider text-accent-blue mb-1">
                  {bullet.label}
                </div>
                {bullet.display_value && (
                  <div className="text-xl font-bold text-slate-100 mb-1">{bullet.display_value}</div>
                )}
                {bullet.text && <div className="text-sm text-slate-400">{bullet.text}</div>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
          <div className="text-sm font-semibold text-slate-200 mb-4">Spend by Category</div>
          {isLoading ? (
            <div className="h-64 skeleton-shimmer rounded-lg" />
          ) : (
            <SpendByCategoryChart data={data?.spend_by_category ?? []} />
          )}
        </div>
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
          <div className="text-sm font-semibold text-slate-200 mb-4">Savings by Tower</div>
          {isLoading ? (
            <div className="h-64 skeleton-shimmer rounded-lg" />
          ) : (
            <TowerSavingsChart data={data?.tower_summary ?? []} />
          )}
        </div>
      </div>

      {/* Waterfall */}
      <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
        <div className="text-sm font-semibold text-slate-200 mb-1">Capacity Waterfall</div>
        <div className="text-xs text-slate-500 mb-4">Gross savings → minus transition cost → net year 1</div>
        {isLoading ? (
          <div className="h-48 skeleton-shimmer rounded-lg" />
        ) : (
          <WaterfallChart
            gross={kpis?.gross_annual_capacity_created ?? 0}
            transitionCost={kpis?.transition_cost ?? 0}
            net={kpis?.net_year_1_capacity_created ?? 0}
          />
        )}
      </div>

      {/* Top Vendors */}
      <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
        <div className="text-sm font-semibold text-slate-200 mb-1">Top Vendors by Spend</div>
        <div className="text-xs text-slate-500 mb-4">Color indicates consolidation signal: green=low, amber=medium, red=high</div>
        {isLoading ? (
          <div className="h-64 skeleton-shimmer rounded-lg" />
        ) : (
          <TopVendorsChart data={data?.top_vendors ?? []} />
        )}
      </div>

      {/* Validation warnings */}
      {data?.validation?.warnings?.length ? (
        <div className="flex items-start gap-3 p-4 bg-accent-amber/10 border border-accent-amber/20 rounded-xl">
          <AlertTriangle size={16} className="text-accent-amber shrink-0 mt-0.5" />
          <div>
            <div className="text-sm font-semibold text-accent-amber mb-2">Data Validation Warnings</div>
            <ul className="space-y-1">
              {data.validation.warnings.map((w, i) => (
                <li key={i} className="text-xs text-slate-400">• {w}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : data && !isLoading ? (
        <div className="flex items-center gap-2 text-xs text-accent-green">
          <CheckCircle size={14} />
          All calculations validated successfully
        </div>
      ) : null}
    </div>
  )
}
