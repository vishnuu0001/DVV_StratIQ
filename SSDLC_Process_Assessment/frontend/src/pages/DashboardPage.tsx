// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/pages (DashboardPage.tsx)
// Date: 2025-12-06
// ---------------------------------------------------------------------------
import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { DashboardResponse, TowerSummaryRow, SpendBreakdown, VendorRecord } from '../types'
import KpiCard from '../components/ui/KpiCard'
import SectionHeader from '../components/ui/SectionHeader'
import ErrorBanner from '../components/ui/ErrorBanner'
import NoWorkbook from '../components/ui/NoWorkbook'
import SpendByCategoryChart from '../components/charts/SpendByCategoryChart'
import TowerSavingsChart from '../components/charts/TowerSavingsChart'
import WaterfallChart from '../components/charts/WaterfallChart'
import TopVendorsChart from '../components/charts/TopVendorsChart'
import { CheckCircle, AlertTriangle } from 'lucide-react'
import { toNum } from '../utils/format'

// Function: mapTowerData
function mapTowerData(rows: DashboardResponse['tower_summary']): TowerSummaryRow[] {
  return ((rows ?? []) as unknown as Record<string, unknown>[]).map((row) => ({
    tower: String(row.tower ?? ''),
    current_spend: toNum(row.current_annual_spend ?? row.current_spend),
    addressable_spend: toNum(row.addressable_spend),
    gross_savings: toNum(row.gross_annual_savings ?? row.gross_savings),
    transition_cost: toNum(row.transition_cost),
    net_year_1_savings: toNum(row.net_year_1_savings),
    run_rate_savings: toNum(row.run_rate_annual_savings ?? row.run_rate_savings),
    vendor_count: toNum(row.vendor_count),
    consolidation_scope_pct: toNum(row.consolidation_scope_pct),
  }))
}

// Function: mapSpendData
function mapSpendData(rows: DashboardResponse['spend_by_category']): SpendBreakdown[] {
  return ((rows ?? []) as unknown as Record<string, unknown>[]).map((row) => ({
    category: String(row.category ?? ''),
    spend: toNum(row.total_spend ?? row.spend),
    count: toNum(row.vendor_count ?? row.count),
  }))
}

// Function: mapVendorData
function mapVendorData(rows: DashboardResponse['top_vendors']): VendorRecord[] {
  return ((rows ?? []) as unknown as Record<string, unknown>[]).map((row, i) => ({
    vendor: String(row.vendor ?? ''),
    spend_category: String(row.spend_category ?? row.category ?? ''),
    tower: String(row.tower ?? ''),
    annual_spend: toNum(row.annual_spend),
    share_of_third_party_spend: toNum(row.pct_of_total ?? row.share_of_third_party_spend),
    consolidation_signal: (String(row.consolidation_signal ?? 'Medium')) as VendorRecord['consolidation_signal'],
    recommended_treatment: String(row.recommended_treatment ?? ''),
    rank: toNum(row.rank ?? i + 1),
  }))
}

// Function: KpiGrid
function KpiGrid({
  kpis,
  isLoading,
}: Readonly<{ kpis: DashboardResponse['kpis'] | undefined; isLoading: boolean }>) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4">
      <KpiCard
        label="Third-Party Spend"
        value={toNum(kpis?.total_third_party_spend ?? 0)}
        format="currency"
        accent="blue"
        loading={isLoading}
        subtitle="External vendor spend"
      />
      <KpiCard
        label="External Talent Spend"
        value={toNum(kpis?.external_talent_spend ?? 0)}
        format="currency"
        accent="purple"
        loading={isLoading}
        subtitle="Contractor & staff aug"
      />
      <KpiCard
        label="Addressable Spend"
        value={toNum(kpis?.addressable_spend ?? 0)}
        format="currency"
        accent="cyan"
        loading={isLoading}
        subtitle="In-scope for consolidation"
      />
      <KpiCard
        label="Gross Capacity Created"
        value={toNum(kpis?.gross_annual_capacity ?? 0)}
        format="currency"
        accent="green"
        loading={isLoading}
        subtitle="Pre-transition gross savings"
      />
      <KpiCard
        label="Transition Cost"
        value={toNum(kpis?.transition_cost ?? 0)}
        format="currency"
        accent="amber"
        loading={isLoading}
        subtitle="One-time transition investment"
      />
      <KpiCard
        label="Net Year 1 Capacity"
        value={toNum(kpis?.net_year_1_savings ?? 0)}
        format="currency"
        accent="green"
        loading={isLoading}
        subtitle="Primary value creation KPI"
      />
      <KpiCard
        label="Run-Rate Annual"
        value={toNum(kpis?.run_rate_annual_savings ?? 0)}
        format="currency"
        accent="green"
        loading={isLoading}
        subtitle="Steady-state annual savings"
      />
      <KpiCard
        label="ROI"
        value={toNum(kpis?.roi_pct ?? 0)}
        format="pct"
        accent="blue"
        loading={isLoading}
        subtitle="Return on investment"
      />
    </div>
  )
}

// Function: ChartOrSkeleton
function ChartOrSkeleton({
  isLoading,
  skeletonClass,
  children,
}: Readonly<{ isLoading: boolean; skeletonClass: string; children: React.ReactNode }>) {
  if (isLoading) return <div className={skeletonClass} />
  return <>{children}</>
}

// Function: ExecutiveStorySection
function ExecutiveStorySection({
  storyData,
}: Readonly<{ storyData: Array<{ bullet: string; category: string }> }>) {
  if (storyData.length === 0) return null
  return (
    <div>
      <SectionHeader
        eyebrow="Narrative"
        title="Executive Story"
        subtitle="Key insights and value creation narrative"
      />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {storyData.map((bullet, i) => (
          <div
            key={bullet.category ?? i}
            className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4"
          >
            <div className="text-xs font-semibold uppercase tracking-wider text-accent-blue mb-1">
              {bullet.category}
            </div>
            <div className="text-sm text-slate-400">{bullet.bullet}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Function: ValidationFooter
function ValidationFooter({ data, isLoading }: Readonly<{ data: DashboardResponse | undefined; isLoading: boolean }>) {
  const warnings = data?.validation?.warnings
  if (warnings?.length) {
    return (
      <div className="flex items-start gap-3 p-4 bg-accent-amber/10 border border-accent-amber/20 rounded-xl">
        <AlertTriangle size={16} className="text-accent-amber shrink-0 mt-0.5" />
        <div>
          <div className="text-sm font-semibold text-accent-amber mb-2">Data Validation Warnings</div>
          <ul className="space-y-1">
            {warnings.map((w, i) => (
              <li key={i} className="text-xs text-slate-400">• {w}</li>
            ))}
          </ul>
        </div>
      </div>
    )
  }
  if (data && !isLoading) {
    return (
      <div className="flex items-center gap-2 text-xs text-accent-green">
        <CheckCircle size={14} />
        All calculations validated successfully
      </div>
    )
  }
  return null
}

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
  const towerData = mapTowerData(data?.tower_summary)
  const spendData = mapSpendData(data?.spend_by_category)
  const vendorData = mapVendorData(data?.top_vendors)
  const storyData = ((data?.executive_story ?? []) as unknown as Array<{ bullet: string; category: string }>)

  return (
    <div className="p-8 space-y-8">
      <SectionHeader
        eyebrow="Executive Summary"
        title="Consolidation Savings Dashboard"
        subtitle="Third-party spend analysis with consolidation opportunity sizing"
      />

      {/* KPI Grid — 7 KPIs matching backend ExecutiveDashboardKpis */}
      <KpiGrid kpis={kpis} isLoading={isLoading} />

      {/* Executive Story */}
      <ExecutiveStorySection storyData={storyData} />

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
          <div className="text-sm font-semibold text-slate-200 mb-4">Spend by Category</div>
          <ChartOrSkeleton isLoading={isLoading} skeletonClass="h-64 skeleton-shimmer rounded-lg">
            <SpendByCategoryChart data={spendData} />
          </ChartOrSkeleton>
        </div>
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
          <div className="text-sm font-semibold text-slate-200 mb-4">Savings by Tower</div>
          <ChartOrSkeleton isLoading={isLoading} skeletonClass="h-64 skeleton-shimmer rounded-lg">
            <TowerSavingsChart data={towerData} />
          </ChartOrSkeleton>
        </div>
      </div>

      {/* Waterfall */}
      <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
        <div className="text-sm font-semibold text-slate-200 mb-1">Capacity Waterfall</div>
        <div className="text-xs text-slate-500 mb-4">Gross savings → minus transition cost → net year 1</div>
        <ChartOrSkeleton isLoading={isLoading} skeletonClass="h-48 skeleton-shimmer rounded-lg">
          <WaterfallChart
            gross={toNum(kpis?.gross_annual_capacity ?? 0)}
            transitionCost={toNum(kpis?.transition_cost ?? 0)}
            net={toNum(kpis?.net_year_1_savings ?? 0)}
          />
        </ChartOrSkeleton>
      </div>

      {/* Top Vendors */}
      <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
        <div className="text-sm font-semibold text-slate-200 mb-1">Top Vendors by Spend</div>
        <div className="text-xs text-slate-500 mb-4">Color indicates consolidation signal: green=low, amber=medium, red=high</div>
        <ChartOrSkeleton isLoading={isLoading} skeletonClass="h-64 skeleton-shimmer rounded-lg">
          <TopVendorsChart data={vendorData} />
        </ChartOrSkeleton>
      </div>

      {/* Validation warnings */}
      <ValidationFooter data={data} isLoading={isLoading} />
    </div>
  )
}
