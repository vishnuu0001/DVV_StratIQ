import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { VendorLandscapeResponse, VendorRecord } from '../types'
import SectionHeader from '../components/ui/SectionHeader'
import ErrorBanner from '../components/ui/ErrorBanner'
import NoWorkbook from '../components/ui/NoWorkbook'
import KpiCard from '../components/ui/KpiCard'
import SpendByCategoryChart from '../components/charts/SpendByCategoryChart'
import { formatCurrencyCompact, formatPct, toNum } from '../utils/format'
import { Search, Filter } from 'lucide-react'

const SIGNAL_STYLES: Record<string, string> = {
  High: 'bg-accent-red/10 text-accent-red border border-accent-red/30',
  Medium: 'bg-accent-amber/10 text-accent-amber border border-accent-amber/30',
  Low: 'bg-accent-green/10 text-accent-green border border-accent-green/30',
}

function SignalBadge({ signal }: { signal: VendorRecord['consolidation_signal'] }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${SIGNAL_STYLES[signal]}`}>
      {signal}
    </span>
  )
}

function TreatmentBadge({ treatment }: { treatment: string }) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-accent-blue/10 text-accent-blue border border-accent-blue/20">
      {treatment}
    </span>
  )
}

function normalizeSignal(value: unknown): VendorRecord['consolidation_signal'] {
  const signal = String(value ?? 'Medium')
  return signal === 'High' || signal === 'Low' ? signal : 'Medium'
}

function normalizeVendors(data: VendorLandscapeResponse | undefined): VendorRecord[] {
  return ((data?.vendors ?? []) as unknown as Record<string, unknown>[]).map((row, i) => ({
    vendor: String(row.vendor ?? ''),
    spend_category: String(row.spend_category ?? row.category ?? 'Other'),
    tower: String(row.tower ?? 'Unassigned'),
    annual_spend: toNum(row.annual_spend ?? row.spend ?? row.total_spend),
    share_of_third_party_spend: toNum(row.share_of_third_party_spend ?? row.pct_of_total ?? row.share),
    consolidation_signal: normalizeSignal(row.consolidation_signal),
    recommended_treatment: String(row.recommended_treatment ?? row.treatment ?? 'Rationalize / bundle'),
    rank: toNum(row.rank ?? i + 1),
  }))
}

function groupSpend(vendors: VendorRecord[], key: 'spend_category' | 'tower') {
  const groups = new Map<string, { category: string; spend: number; count: number }>()
  vendors.forEach((vendor) => {
    const category = vendor[key] || 'Unassigned'
    const current = groups.get(category) ?? { category, spend: 0, count: 0 }
    current.spend += vendor.annual_spend
    current.count += 1
    groups.set(category, current)
  })
  return Array.from(groups.values()).sort((a, b) => b.spend - a.spend)
}

export default function VendorLandscapePage() {
  const { workbookId } = useWorkbook()
  const [search, setSearch] = useState('')
  const [filterCategory, setFilterCategory] = useState('all')
  const [filterSignal, setFilterSignal] = useState('all')

  const { data, isLoading, error } = useQuery<VendorLandscapeResponse>({
    queryKey: ['vendor-landscape', workbookId],
    queryFn: () => apiGet<VendorLandscapeResponse>(`/workbooks/${workbookId}/calculations/vendor-landscape`),
    enabled: !!workbookId,
  })

  const vendors = useMemo(() => normalizeVendors(data), [data])
  const spendByCategory = useMemo(() => groupSpend(vendors, 'spend_category'), [vendors])
  const spendByTower = useMemo(() => groupSpend(vendors, 'tower'), [vendors])
  const totalSpend = vendors.reduce((sum, vendor) => sum + vendor.annual_spend, 0)
  const pctFor = (category: string) => {
    const spend = vendors
      .filter((vendor) => vendor.spend_category.trim().toLowerCase() === category)
      .reduce((sum, vendor) => sum + vendor.annual_spend, 0)
    return totalSpend > 0 ? spend / totalSpend : 0
  }
  const summary = {
    total_spend: toNum(data?.summary?.total_spend ?? totalSpend),
    talent_pct: toNum(data?.summary?.talent_pct ?? pctFor('talent')),
    software_pct: toNum(data?.summary?.software_pct ?? pctFor('software')),
    data_pct: toNum(data?.summary?.data_pct ?? pctFor('data')),
    top_vendor: String(data?.summary?.top_vendor ?? vendors[0]?.vendor ?? ''),
  }

  const categories = useMemo(() => {
    const cats = new Set(vendors.map((v) => v.spend_category))
    return ['all', ...Array.from(cats)]
  }, [vendors])

  const filtered = useMemo(() => {
    return vendors.filter((v) => {
      const matchSearch =
        !search ||
        v.vendor.toLowerCase().includes(search.toLowerCase()) ||
        v.tower.toLowerCase().includes(search.toLowerCase())
      const matchCat = filterCategory === 'all' || v.spend_category === filterCategory
      const matchSig = filterSignal === 'all' || v.consolidation_signal === filterSignal
      return matchSearch && matchCat && matchSig
    })
  }, [vendors, search, filterCategory, filterSignal])

  if (!workbookId) return <div className="p-8"><NoWorkbook /></div>
  if (error) return <div className="p-8"><ErrorBanner message={error instanceof Error ? error.message : 'Error'} /></div>

  return (
    <div className="p-8 space-y-6">
      <SectionHeader
        eyebrow="Vendor Analytics"
        title="Vendor Landscape"
        subtitle="Third-party vendor spend analysis and consolidation opportunity"
      />

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <KpiCard
          label="Total Vendor Spend"
          value={summary.total_spend}
          format="currency"
          accent="blue"
          loading={isLoading}
        />
        <KpiCard
          label="Talent %"
          value={summary.talent_pct}
          format="pct"
          accent="purple"
          loading={isLoading}
        />
        <KpiCard
          label="Software %"
          value={summary.software_pct}
          format="pct"
          accent="cyan"
          loading={isLoading}
        />
        <KpiCard
          label="Data %"
          value={summary.data_pct}
          format="pct"
          accent="amber"
          loading={isLoading}
        />
        <div className="bg-navy-800/60 border border-navy-700 rounded-xl p-5">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Top Vendor</div>
          <div className="text-sm font-bold text-slate-100 truncate">{summary.top_vendor || '—'}</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
          <div className="text-sm font-semibold text-slate-200 mb-4">Spend by Category</div>
          {isLoading ? (
            <div className="h-56 skeleton-shimmer rounded-lg" />
          ) : (
            <SpendByCategoryChart data={spendByCategory} />
          )}
        </div>
        <div className="bg-navy-800 border border-navy-700 rounded-xl p-6">
          <div className="text-sm font-semibold text-slate-200 mb-4">Spend by Tower</div>
          {isLoading ? (
            <div className="h-56 skeleton-shimmer rounded-lg" />
          ) : (
            <SpendByCategoryChart data={spendByTower} />
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search vendors or towers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-navy-800 border border-navy-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-accent-blue"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-slate-500" />
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="bg-navy-800 border border-navy-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-accent-blue"
          >
            {categories.map((c) => <option key={c} value={c}>{c === 'all' ? 'All Categories' : c}</option>)}
          </select>
          <select
            value={filterSignal}
            onChange={(e) => setFilterSignal(e.target.value)}
            className="bg-navy-800 border border-navy-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-accent-blue"
          >
            <option value="all">All Signals</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        <div className="flex items-center text-xs text-slate-500">
          {filtered.length} vendors
        </div>
      </div>

      {/* Vendor table */}
      <div className="bg-navy-800 border border-navy-700 rounded-xl overflow-hidden">
        {isLoading ? (
          <div className="p-8 space-y-3">
            {[...Array(8)].map((_, i) => <div key={i} className="h-10 skeleton-shimmer rounded" />)}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-navy-700">
                  {['#', 'Vendor', 'Category', 'Tower', 'Annual Spend', 'Share %', 'Signal', 'Treatment'].map((h) => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500 whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((vendor) => (
                  <tr key={`${vendor.vendor}-${vendor.rank}`} className="border-b border-navy-700/50 hover:bg-navy-700/30 transition-colors">
                    <td className="px-4 py-3 text-xs text-slate-500">{vendor.rank}</td>
                    <td className="px-4 py-3 text-sm font-medium text-slate-200 whitespace-nowrap">{vendor.vendor}</td>
                    <td className="px-4 py-3 text-xs text-slate-400">{vendor.spend_category}</td>
                    <td className="px-4 py-3 text-xs text-slate-400">{vendor.tower}</td>
                    <td className="px-4 py-3 text-sm font-mono text-slate-300 text-right">{formatCurrencyCompact(vendor.annual_spend)}</td>
                    <td className="px-4 py-3 text-sm text-slate-400 text-right">{formatPct(vendor.share_of_third_party_spend)}</td>
                    <td className="px-4 py-3"><SignalBadge signal={vendor.consolidation_signal} /></td>
                    <td className="px-4 py-3"><TreatmentBadge treatment={vendor.recommended_treatment} /></td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={8} className="px-4 py-12 text-center text-slate-500 text-sm">
                      No vendors match your filter criteria
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
