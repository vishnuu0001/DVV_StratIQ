// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * DrilldownDrawer — sliding right-panel for L2/L3 chart exploration.
// Date: 2025-12-26
// ---------------------------------------------------------------------------
/**
 * DrilldownDrawer — sliding right-panel for L2/L3 chart exploration.
 *
 * Props:
 *   open        boolean        — whether panel is visible
 *   onClose     () => void
 *   title       string         — chart display name
 *   chartType   string         — one of the keys in VIEWS below
 *   data        object         — pre-fetched data from the page
 */
import React, { useState, useEffect, useRef } from 'react'
import { X, BarChart2, TrendingUp, TrendingDown, Table2, ChevronRight, ChevronDown, Target, AlertCircle, CheckCircle2, Gauge } from 'lucide-react'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell, PieChart, Pie,
} from 'recharts'

const C = ['#3b82f6', '#22c55e', '#ef4444', '#f97316', '#8b5cf6', '#06b6d4', '#eab308', '#ec4899']

/* ─── shared helpers ───────────────────────────────────────────────────── */

// Function: SectionTitle
function SectionTitle({ children }) {
  return (
    <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 mt-5 first:mt-0">
      {children}
    </h3>
  )
}

// Function: DataTable
function DataTable({ columns, rows, onRowClick, selectedKey, rowKey }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="w-full text-xs">
        <thead>
          <tr className="bg-slate-50 border-b border-slate-200">
            {columns.map((col) => (
              <th key={col.key} className="px-3 py-2 text-left font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">
                {col.label}
              </th>
            ))}
            {onRowClick && <th className="px-3 py-2 w-6" />}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => {
            const key = rowKey ? row[rowKey] : i
            const isSelected = selectedKey === key
            return (
              <tr
                key={i}
                onClick={onRowClick ? () => onRowClick(key, row) : undefined}
                className={`border-b border-slate-100 last:border-0 transition-colors ${onRowClick ? 'cursor-pointer hover:bg-sky-50' : ''} ${isSelected ? 'bg-sky-50' : ''}`}
              >
                {columns.map((col) => (
                  <td key={col.key} className={`px-3 py-2 ${col.bold ? 'font-semibold text-slate-800' : 'text-slate-600'} whitespace-nowrap`}>
                    {col.render ? col.render(row[col.key], row) : (row[col.key] ?? '—')}
                  </td>
                ))}
                {onRowClick && (
                  <td className="px-3 py-2">
                    {isSelected
                      ? <ChevronDown className="w-3 h-3 text-sky-500" />
                      : <ChevronRight className="w-3 h-3 text-slate-300" />}
                  </td>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

// Function: Tooltip2
function Tooltip2({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 shadow-lg rounded-lg px-3 py-2 text-xs">
      <p className="font-semibold text-slate-700 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: <span className="font-bold text-slate-900">{typeof p.value === 'number' ? p.value.toLocaleString() : p.value}</span>
        </p>
      ))}
    </div>
  )
}

/* ─── L2 view: Monthly Volume ──────────────────────────────────────────── */
// Function: MonthlyVolumeView
function MonthlyVolumeView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const rows = data || []
  const detail = selected ? rows.find((r) => r.month === selected) : null

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  return (
    <>
      <SectionTitle>Monthly Breakdown — Grouped Bar</SectionTitle>
      <div style={{ height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} margin={{ bottom: 24, left: 0, right: 8 }} barCategoryGap="30%">
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="month" tick={{ fontSize: 9 }} angle={-30} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 9 }} />
            <Tooltip content={<Tooltip2 />} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            <Bar dataKey="incidents" name="Incidents" fill={C[0]} radius={[2, 2, 0, 0]}>
              {rows.map((_, i) => <Cell key={i} fill={selected === rows[i]?.month ? '#1d4ed8' : C[0]} />)}
            </Bar>
            <Bar dataKey="changes" name="Changes" fill={C[1]} radius={[2, 2, 0, 0]} />
            <Bar dataKey="service_requests" name="Service Requests" fill={C[2]} radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <SectionTitle>L2 — Month Detail Table (click a row for L3)</SectionTitle>
      <DataTable
        rowKey="month"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'month', label: 'Month', bold: true },
          { key: 'incidents', label: 'Incidents', render: (v) => (v || 0).toLocaleString() },
          { key: 'changes', label: 'Changes', render: (v) => (v || 0).toLocaleString() },
          { key: 'service_requests', label: 'SRs', render: (v) => (v || 0).toLocaleString() },
          { key: 'total', label: 'Total', bold: true, render: (v) => (v || 0).toLocaleString() },
        ]}
        rows={rows}
      />

      {/* L3 — selected month detail */}
      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-3">L3 Detail — {detail.month}</p>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Incidents', value: detail.incidents, color: C[0] },
              { label: 'Changes', value: detail.changes, color: C[1] },
              { label: 'Service Requests', value: detail.service_requests, color: C[2] },
              { label: 'Total', value: detail.total, color: '#0f172a' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-white rounded-lg p-3 border border-sky-100 text-center">
                <p className="text-[10px] text-slate-500 mb-1">{label}</p>
                <p className="text-xl font-bold" style={{ color }}>{(value || 0).toLocaleString()}</p>
              </div>
            ))}
          </div>
          <div style={{ height: 120, marginTop: 12 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={[
                  { name: 'Incidents', value: detail.incidents },
                  { name: 'Changes', value: detail.changes },
                  { name: 'SRs', value: detail.service_requests },
                ]}
              >
                <XAxis dataKey="name" tick={{ fontSize: 9 }} />
                <YAxis tick={{ fontSize: 9 }} />
                <Tooltip content={<Tooltip2 />} />
                <Bar dataKey="value" name="Count" radius={[3, 3, 0, 0]}>
                  {[C[0], C[1], C[2]].map((color, i) => <Cell key={i} fill={color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: Application Hotspots ────────────────────────────────────── */
// Function: HotspotsView
function HotspotsView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const rows = (data || []).slice(0, 15)
  const detail = selected ? rows.find((r) => r.application === selected) : null

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  return (
    <>
      <SectionTitle>Top Application Hotspots — Bar Chart</SectionTitle>
      <div style={{ height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={[...rows].reverse()} layout="vertical" margin={{ left: 100, right: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
            <XAxis type="number" tick={{ fontSize: 9 }} />
            <YAxis dataKey="application" type="category" tick={{ fontSize: 8 }} width={100}
              tickFormatter={(v) => v.length > 18 ? v.slice(0, 17) + '…' : v} />
            <Tooltip content={<Tooltip2 />} />
            <Bar dataKey="count" name="Incidents" radius={[0, 3, 3, 0]}>
              {rows.map((_, i) => <Cell key={i} fill={C[i % C.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <SectionTitle>L2 — Hotspot Detail Table (click a row for L3)</SectionTitle>
      <DataTable
        rowKey="application"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'application', label: 'Application', bold: true, render: (v) => v?.length > 28 ? v.slice(0, 27) + '…' : v },
          { key: 'count', label: 'Incidents', render: (v) => (v || 0).toLocaleString() },
          { key: 'pct_of_total', label: '% of Total', render: (v) => `${(v || 0).toFixed(1)}%` },
          { key: 'avg_mttr_hours', label: 'Avg MTTR', render: (v) => v ? `${v.toFixed(1)}h` : '—' },
        ]}
        rows={rows}
      />

      {/* L3 detail */}
      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-1">L3 — {detail.application}</p>
          <div className="grid grid-cols-3 gap-2 mt-2">
            {[
              { label: 'Incidents', value: detail.count?.toLocaleString() },
              { label: '% of Total', value: `${(detail.pct_of_total || 0).toFixed(1)}%` },
              { label: 'Avg MTTR', value: detail.avg_mttr_hours ? `${detail.avg_mttr_hours.toFixed(1)}h` : '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-white rounded-lg p-2 border border-sky-100 text-center">
                <p className="text-[10px] text-slate-500">{label}</p>
                <p className="text-base font-bold text-sky-700">{value}</p>
              </div>
            ))}
          </div>
          {detail.avg_mttr_hours > 0 && (
            <p className={`mt-3 text-xs font-medium ${detail.avg_mttr_hours < 24 ? 'text-emerald-700' : detail.avg_mttr_hours < 72 ? 'text-amber-700' : 'text-rose-700'}`}>
              {detail.avg_mttr_hours < 24 ? '✓ MTTR within 24h target'
                : detail.avg_mttr_hours < 72 ? '⚠ MTTR elevated — review resolution workflows'
                : '✕ MTTR critical — escalate immediately'}
            </p>
          )}
        </div>
      )}
    </>
  )
}

/* ─── L2 view: Incident MTTR ────────────────────────────────────────────── */
// Function: MTTRView
function MTTRView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const trend = data?.mttr_trend || []
  const priDist = data?.priority_dist || []

  useEffect(() => {
    if (selected && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [selected])
  const detail = selected ? trend.find((r) => r.month === selected) : null

  return (
    <>
      <SectionTitle>MTTR Trend — Avg &amp; P90</SectionTitle>
      <div style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trend} margin={{ bottom: 20, right: 12 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="month" tick={{ fontSize: 9 }} angle={-30} textAnchor="end" />
            <YAxis tick={{ fontSize: 9 }} unit="h" />
            <Tooltip content={<Tooltip2 />} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            <Line dataKey="avg_mttr_hours" name="Avg MTTR (h)" stroke={C[3]} strokeWidth={2} dot={{ r: 3 }} />
            <Line dataKey="p90_hours" name="P90 MTTR (h)" stroke={C[4]} strokeWidth={1.5} strokeDasharray="4 2" dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <SectionTitle>Priority Distribution</SectionTitle>
      <div className="flex items-center gap-4">
        <div style={{ width: 140, height: 140, flexShrink: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={priDist} dataKey="count" nameKey="priority" cx="50%" cy="50%" outerRadius={60} label={({ priority, pct }) => `${pct?.toFixed(0)}%`} labelLine={false}>
                {priDist.map((_, i) => <Cell key={i} fill={C[i % C.length]} />)}
              </Pie>
              <Tooltip content={<Tooltip2 />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <DataTable
          columns={[
            { key: 'priority', label: 'Priority', bold: true },
            { key: 'count', label: 'Count', render: (v) => (v || 0).toLocaleString() },
            { key: 'pct', label: '%', render: (v) => `${(v || 0).toFixed(1)}%` },
          ]}
          rows={priDist}
        />
      </div>

      <SectionTitle>L2 — Monthly MTTR Table (click a row for L3)</SectionTitle>
      <DataTable
        rowKey="month"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'month', label: 'Month', bold: true },
          { key: 'count', label: 'Count', render: (v) => (v || 0).toLocaleString() },
          { key: 'avg_mttr_hours', label: 'Avg MTTR', render: (v) => v ? `${v.toFixed(1)}h` : '—' },
          { key: 'p50_hours', label: 'P50', render: (v) => v ? `${v.toFixed(1)}h` : '—' },
          { key: 'p90_hours', label: 'P90', render: (v) => v ? `${v.toFixed(1)}h` : '—' },
        ]}
        rows={trend}
      />

      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail — {detail.month}</p>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: 'Incident Count', value: detail.count?.toLocaleString() },
              { label: 'Avg MTTR', value: detail.avg_mttr_hours ? `${detail.avg_mttr_hours.toFixed(1)}h` : '—' },
              { label: 'Median (P50)', value: detail.p50_hours ? `${detail.p50_hours.toFixed(1)}h` : '—' },
              { label: 'P90 MTTR', value: detail.p90_hours ? `${detail.p90_hours.toFixed(1)}h` : '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-white rounded-lg p-2 border border-sky-100 text-center">
                <p className="text-[10px] text-slate-500">{label}</p>
                <p className="text-base font-bold text-sky-700">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: Change Risk ──────────────────────────────────────────────── */
// Function: ChangeRiskView
function ChangeRiskView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const trend = data?.volume_trend || []
  const risk = data?.risk || {}

  useEffect(() => {
    if (selected && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [selected])
  const byType = risk.by_type || {}
  const typeRows = Object.entries(byType).map(([type, count]) => ({ type, count }))
  const total = typeRows.reduce((s, r) => s + r.count, 0)
  const detail = selected ? trend.find((r) => r.month === selected) : null

  return (
    <>
      <SectionTitle>Change Type Distribution</SectionTitle>
      <div className="flex items-center gap-4">
        <div style={{ width: 140, height: 140, flexShrink: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={typeRows} dataKey="count" nameKey="type" cx="50%" cy="50%"
                outerRadius={60} innerRadius={30}
                label={({ type, count }) => total > 0 ? `${(count / total * 100).toFixed(0)}%` : ''}
                labelLine={false}>
                {typeRows.map((_, i) => <Cell key={i} fill={[C[0], C[2], C[4]][i % 3]} />)}
              </Pie>
              <Tooltip content={<Tooltip2 />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <DataTable
          columns={[
            { key: 'type', label: 'Type', bold: true },
            { key: 'count', label: 'Count', render: (v) => (v || 0).toLocaleString() },
            { key: 'count', label: '%', render: (v) => total > 0 ? `${(v / total * 100).toFixed(1)}%` : '—' },
          ]}
          rows={typeRows}
        />
      </div>

      <SectionTitle>Key Risk Metrics</SectionTitle>
      <div className="grid grid-cols-2 gap-2 mb-2">
        {[
          { label: 'Emergency Change %', value: `${(risk.emergency_pct || 0).toFixed(1)}%`, warn: risk.emergency_pct > 15, good: risk.emergency_pct < 5 },
          { label: 'Success Rate', value: `${(risk.implementation_success_pct || 0).toFixed(1)}%`, good: risk.implementation_success_pct >= 90 },
          { label: 'Expedited %', value: `${(risk.expedited_pct || 0).toFixed(1)}%` },
          { label: 'Avg Impl. Time', value: `${(risk.avg_impl_hours || 0).toFixed(1)}h` },
        ].map(({ label, value, warn, good }) => (
          <div key={label} className={`rounded-lg p-2.5 border text-center ${warn ? 'bg-rose-50 border-rose-200' : good ? 'bg-emerald-50 border-emerald-200' : 'bg-slate-50 border-slate-200'}`}>
            <p className="text-[10px] text-slate-500">{label}</p>
            <p className={`text-base font-bold ${warn ? 'text-rose-700' : good ? 'text-emerald-700' : 'text-slate-800'}`}>{value}</p>
          </div>
        ))}
      </div>

      <SectionTitle>L2 — Monthly Change Volume (click a row for L3)</SectionTitle>
      <DataTable
        rowKey="month"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'month', label: 'Month', bold: true },
          { key: 'normal', label: 'Normal', render: (v) => (v || 0).toLocaleString() },
          { key: 'standard', label: 'Standard', render: (v) => (v || 0).toLocaleString() },
          { key: 'emergency', label: 'Emergency', render: (v, row) => (
            <span className={row.emergency > 0 ? 'text-rose-600 font-semibold' : ''}>{(v || 0).toLocaleString()}</span>
          )},
          { key: 'total', label: 'Total', bold: true, render: (v) => (v || 0).toLocaleString() },
        ]}
        rows={trend}
      />

      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail — {detail.month}</p>
          <div style={{ height: 120 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[
                { name: 'Normal', value: detail.normal },
                { name: 'Standard', value: detail.standard },
                { name: 'Emergency', value: detail.emergency },
              ]}>
                <XAxis dataKey="name" tick={{ fontSize: 9 }} />
                <YAxis tick={{ fontSize: 9 }} />
                <Tooltip content={<Tooltip2 />} />
                <Bar dataKey="value" name="Count" radius={[3, 3, 0, 0]}>
                  {[C[0], C[2], C[4]].map((color, i) => <Cell key={i} fill={color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          {detail.emergency > 0 && detail.total > 0 && (
            <p className="mt-2 text-xs text-rose-700 font-medium">
              ⚠ Emergency changes this month: {((detail.emergency / detail.total) * 100).toFixed(1)}% of volume
            </p>
          )}
        </div>
      )}
    </>
  )
}

/* ─── L2 view: SR Productivity ──────────────────────────────────────────── */
// Function: SRProductivityView
function SRProductivityView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const summary = data?.summary || {}
  const ageing = data?.ageing || {}
  const topCats = summary.top_categories || []
  const detail = selected ? topCats.find((r) => r.category === selected) : null
  const total = summary.total || 1

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  const ageData = [
    { name: '< 7d', value: ageing.lt_7d || 0 },
    { name: '7–30d', value: ageing['7_30d'] || 0 },
    { name: '30–90d', value: ageing['30_90d'] || 0 },
    { name: '> 90d', value: ageing.gt_90d || 0 },
  ]

  return (
    <>
      <SectionTitle>SR Summary KPIs</SectionTitle>
      <div className="grid grid-cols-2 gap-2 mb-2">
        {[
          { label: 'Total SRs', value: (summary.total || 0).toLocaleString() },
          { label: 'Backlog (Open)', value: (summary.backlog_count || 0).toLocaleString(), warn: (summary.backlog_count / total) > 0.3 },
          { label: 'Avg Closure', value: `${(summary.avg_closure_hours || 0).toFixed(1)}h` },
          { label: 'Median Closure', value: `${(summary.median_closure_hours || 0).toFixed(1)}h` },
        ].map(({ label, value, warn }) => (
          <div key={label} className={`rounded-lg p-2.5 border text-center ${warn ? 'bg-amber-50 border-amber-200' : 'bg-slate-50 border-slate-200'}`}>
            <p className="text-[10px] text-slate-500">{label}</p>
            <p className={`text-base font-bold ${warn ? 'text-amber-700' : 'text-slate-800'}`}>{value}</p>
          </div>
        ))}
      </div>

      <SectionTitle>Open SR Ageing</SectionTitle>
      <div style={{ height: 140 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={ageData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="name" tick={{ fontSize: 9 }} />
            <YAxis tick={{ fontSize: 9 }} />
            <Tooltip content={<Tooltip2 />} />
            <Bar dataKey="value" name="Open SRs" radius={[3, 3, 0, 0]}>
              {[C[2], C[3], C[4], C[4]].map((color, i) => <Cell key={i} fill={color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <SectionTitle>L2 — Top SR Categories (click a row for L3)</SectionTitle>
      <DataTable
        rowKey="category"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'category', label: 'Category', bold: true, render: (v) => v?.length > 28 ? v.slice(0, 27) + '…' : v },
          { key: 'count', label: 'Count', render: (v) => (v || 0).toLocaleString() },
          { key: 'count', label: '% of Total', render: (v) => `${((v / total) * 100).toFixed(1)}%` },
        ]}
        rows={topCats}
      />

      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail — {detail.category}</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">SR Count</p>
              <p className="text-xl font-bold text-sky-700">{(detail.count || 0).toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">% of Total SRs</p>
              <p className="text-xl font-bold text-sky-700">{((detail.count / total) * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: Tickets-by-Type tab (used inside ExecutiveOverviewView) ─── */
// Function: TicketsByTypeTab
function TicketsByTypeTab({ types, volume }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const totalForType = types.reduce((s, t) => s + t.count, 0) || 1
  const selType = selected ? types.find((t) => t.label === selected) : null
  const monthlyForType = selType
    ? volume.map((m) => ({ month: m.month, count: m[selType.key] || 0 }))
    : []

  useEffect(() => {
    if (selType && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [selType])

  return (
    <>
      <SectionTitle>Tickets by Type — Distribution</SectionTitle>
      <div style={{ height: 170 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={types}
              dataKey="count"
              nameKey="label"
              cx="50%"
              cy="50%"
              innerRadius={42}
              outerRadius={72}
              paddingAngle={2}
              onClick={(d) => { if (d?.label) setSelected(selected === d.label ? null : d.label) }}
            >
              {types.map((t, i) => (
                <Cell key={i} fill={t.color} style={{ cursor: 'pointer' }} />
              ))}
            </Pie>
            <Tooltip content={<Tooltip2 />} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <SectionTitle>L2 — Type Summary (click a row for L3 monthly trend)</SectionTitle>
      <DataTable
        rowKey="label"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'label', label: 'Type', bold: true },
          { key: 'count', label: 'Count', render: (v) => (v || 0).toLocaleString() },
          { key: 'count', label: '% of Total', render: (v) => `${((v / totalForType) * 100).toFixed(1)}%` },
        ]}
        rows={types}
      />

      {selType && monthlyForType.length > 0 && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-3">L3 Monthly Trend — {selected}</p>
          <div style={{ height: 160 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyForType} margin={{ bottom: 24, left: 0, right: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 8 }} angle={-30} textAnchor="end" />
                <YAxis tick={{ fontSize: 9 }} />
                <Tooltip content={<Tooltip2 />} />
                <Bar dataKey="count" name={selected} fill={selType.color} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: Executive Overview (tabbed) ──────────────────────────────── */
// Function: ExecutiveOverviewView
function ExecutiveOverviewView({ data }) {
  const kpis = data?.kpis || {}
  const volume = data?.volume || []
  const hotspots = data?.hotspots || []
  const [tab, setTab] = useState('kpi')

  const tabs = [
    { id: 'kpi',      label: 'KPI Summary' },
    { id: 'type',     label: 'Tickets by Type' },
    { id: 'volume',   label: 'Monthly Volume' },
    { id: 'hotspots', label: 'App Hotspots' },
  ]

  const ticketTypes = [
    { label: 'Incidents',        key: 'incidents',        count: kpis.total_incidents || 0,  color: C[2] },
    { label: 'Changes',          key: 'changes',          count: kpis.total_changes   || 0,  color: C[0] },
    { label: 'Service Requests', key: 'service_requests', count: kpis.total_sr        || 0,  color: C[4] },
  ]

  return (
    <>
      {/* Tab navigation */}
      <div className="flex gap-1 mb-4 flex-wrap border-b border-slate-200 pb-3">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors ${
              tab === t.id
                ? 'bg-sky-100 text-sky-700 border border-sky-200'
                : 'text-slate-500 hover:bg-slate-100 border border-transparent'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* KPI Summary tab */}
      {tab === 'kpi' && (
        <>
          <SectionTitle>Executive KPI Summary</SectionTitle>
          <div className="grid grid-cols-2 gap-2 mb-2">
            {[
              { label: 'Total Tickets',     value: (kpis.total_tickets || 0).toLocaleString() },
              { label: 'SLA Compliance',    value: kpis.sla_compliance_pct != null ? `${kpis.sla_compliance_pct.toFixed(1)}%` : '—', good: kpis.sla_compliance_pct >= 95, warn: kpis.sla_compliance_pct < 85 },
              { label: 'Avg MTTR',          value: kpis.avg_mttr_hours != null ? `${kpis.avg_mttr_hours.toFixed(1)}h` : '—', warn: kpis.avg_mttr_hours > 72 },
              { label: 'Emergency Changes', value: kpis.emergency_change_pct != null ? `${kpis.emergency_change_pct.toFixed(1)}%` : '—', warn: kpis.emergency_change_pct > 15 },
              { label: 'Incidents',         value: (kpis.total_incidents || 0).toLocaleString() },
              { label: 'Changes',           value: (kpis.total_changes   || 0).toLocaleString() },
              { label: 'Service Requests',  value: (kpis.total_sr        || 0).toLocaleString() },
              { label: 'Avg Cycle Time',    value: kpis.avg_cycle_time_hours != null ? `${kpis.avg_cycle_time_hours.toFixed(1)}h` : '—' },
            ].map(({ label, value, good, warn }) => (
              <div key={label} className={`rounded-lg p-2.5 border text-center ${warn ? 'bg-rose-50 border-rose-200' : good ? 'bg-emerald-50 border-emerald-200' : 'bg-slate-50 border-slate-200'}`}>
                <p className="text-[10px] text-slate-500">{label}</p>
                <p className={`text-base font-bold ${warn ? 'text-rose-700' : good ? 'text-emerald-700' : 'text-slate-800'}`}>{value}</p>
              </div>
            ))}
          </div>
          {volume.length > 0 && (
            <>
              <SectionTitle>12-Month Volume Trend</SectionTitle>
              <div style={{ height: 180 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={volume} margin={{ bottom: 20, right: 12 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="month" tick={{ fontSize: 8 }} angle={-30} textAnchor="end" />
                    <YAxis tick={{ fontSize: 9 }} />
                    <Tooltip content={<Tooltip2 />} />
                    <Legend wrapperStyle={{ fontSize: 10 }} />
                    <Line dataKey="total" name="Total" stroke={C[0]} strokeWidth={2} dot={{ r: 2 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </>
      )}

      {/* Tickets by Type tab */}
      {tab === 'type' && <TicketsByTypeTab types={ticketTypes} volume={volume} />}

      {/* Monthly Volume tab — reuse full MonthlyVolumeView */}
      {tab === 'volume' && <MonthlyVolumeView data={volume} />}

      {/* App Hotspots tab — reuse full HotspotsView */}
      {tab === 'hotspots' && <HotspotsView data={hotspots} />}
    </>
  )
}

/* ─── L2 view: Automation Opportunities ─────────────────────────────────── */
// Function: AutomationView
function AutomationView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const candidates = Array.isArray(data) ? data : data?.candidates || []

  // Aggregate by category
  const catMap = {}
  candidates.forEach((c) => {
    const cat = c.category || 'Other'
    if (!catMap[cat]) catMap[cat] = { category: cat, count: 0, volume: 0, hours_saved: 0 }
    catMap[cat].count += 1
    catMap[cat].volume += Number(c.volume) || 0
    catMap[cat].hours_saved += Number(c.est_hours_saved) || 0
  })
  const cats = Object.values(catMap).sort((a, b) => b.volume - a.volume).slice(0, 15)
  const selCat = selected ? cats.find((c) => c.category === selected) : null
  const workTypes = selCat
    ? candidates
        .filter((c) => c.category === selCat.category)
        .sort((a, b) => (Number(b.volume) || 0) - (Number(a.volume) || 0))
    : []

  useEffect(() => {
    if (selCat && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [selCat])

  // Priority distribution
  const priMap = {}
  candidates.forEach((c) => { const p = c.priority || 'Monitor'; priMap[p] = (priMap[p] || 0) + 1 })
  const PRI_ORDER = ['High', 'Medium', 'Low', 'Monitor']
  const PRI_COLORS = { High: '#ef4444', Medium: '#f97316', Low: '#22c55e', Monitor: '#94a3b8' }
  const priData = PRI_ORDER
    .filter((p) => priMap[p])
    .map((p) => ({ priority: p, count: priMap[p] }))

  return (
    <>
      <SectionTitle>Priority Distribution</SectionTitle>
      <div style={{ height: 140 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={priData} margin={{ left: 0, right: 20, top: 4, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="priority" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 9 }} axisLine={false} tickLine={false} />
            <Tooltip content={<Tooltip2 />} />
            <Bar dataKey="count" name="Candidates" radius={[4, 4, 0, 0]}>
              {priData.map((d, i) => <Cell key={i} fill={PRI_COLORS[d.priority] || C[i % C.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <SectionTitle>L2 — Top Categories by Volume (click a row for L3 work types)</SectionTitle>
      <DataTable
        rowKey="category"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'category', label: 'Category', bold: true, render: (v) => v?.length > 24 ? v.slice(0, 23) + '…' : v },
          { key: 'volume',   label: 'Volume',   render: (v) => (v || 0).toLocaleString() },
          { key: 'hours_saved', label: 'Est. Hrs', render: (v) => v > 0 ? `${Math.round(v)}h` : '—' },
          { key: 'count',    label: 'Candidates', render: (v) => (v || 0).toLocaleString() },
        ]}
        rows={cats}
      />

      {selCat && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-3">L3 Work Types — {selCat.category}</p>
          <div className="grid grid-cols-2 gap-2 mb-3">
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Total Volume</p>
              <p className="text-lg font-bold text-sky-700">{selCat.volume.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Est. Hours Saved</p>
              <p className="text-lg font-bold text-emerald-600">{Math.round(selCat.hours_saved)}h</p>
            </div>
          </div>
          <div className="overflow-auto max-h-48 rounded-lg border border-sky-200">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-sky-100 border-b border-sky-200">
                  <th className="px-2 py-1.5 text-left text-sky-700 font-semibold">Work Type</th>
                  <th className="px-2 py-1.5 text-right text-sky-700 font-semibold">Volume</th>
                  <th className="px-2 py-1.5 text-right text-sky-700 font-semibold">Est. Hrs Saved</th>
                  <th className="px-2 py-1.5 text-right text-sky-700 font-semibold">LLM Score</th>
                  <th className="px-2 py-1.5 text-left text-sky-700 font-semibold">Automation Type</th>
                  <th className="px-2 py-1.5 text-left text-sky-700 font-semibold">Priority</th>
                </tr>
              </thead>
              <tbody>
                {workTypes.map((wt, i) => (
                  <tr key={i} className="border-b border-sky-100 hover:bg-sky-50/50">
                    <td className="px-2 py-1.5 text-slate-700">{wt.work_type || '—'}</td>
                    <td className="px-2 py-1.5 text-right tabular-nums font-medium">{(Number(wt.volume) || 0).toLocaleString()}</td>
                    <td className="px-2 py-1.5 text-right tabular-nums text-emerald-600 font-medium">{Number(wt.est_hours_saved) > 0 ? `${Math.round(wt.est_hours_saved)}h` : '—'}</td>
                    <td className="px-2 py-1.5 text-right tabular-nums text-cyan-700 font-medium">
                      {wt.llm_opportunity_score != null ? Number(wt.llm_opportunity_score).toFixed(1) : '—'}
                    </td>
                    <td className="px-2 py-1.5 text-slate-600">{wt.llm_automation_type || '—'}</td>
                    <td className="px-2 py-1.5 text-slate-600">{wt.priority || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: Repeat Incidents ─────────────────────────────────────────── */
// Function: RepeatIncidentsView
function RepeatIncidentsView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const rows = data?.top_repeats || []
  const detail = selected != null
    ? rows.find((row) => (row.description || '') === selected)
    : null

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  return (
    <>
      <SectionTitle>Repeat Incident Summary</SectionTitle>
      <div className="grid grid-cols-3 gap-2 mb-2">
        <div className="rounded-lg p-2.5 border text-center bg-slate-50 border-slate-200">
          <p className="text-[10px] text-slate-500">Total Incidents</p>
          <p className="text-base font-bold text-slate-800">{(data?.total_incidents || 0).toLocaleString()}</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-amber-50 border-amber-200">
          <p className="text-[10px] text-slate-500">Repeat Count</p>
          <p className="text-base font-bold text-amber-700">{(data?.repeat_incidents || 0).toLocaleString()}</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-sky-50 border-sky-200">
          <p className="text-[10px] text-slate-500">Repeat %</p>
          <p className="text-base font-bold text-sky-700">{(data?.repeat_pct || 0).toFixed(1)}%</p>
        </div>
      </div>

      <SectionTitle>L2 — Top Repeating Patterns (click a row for L3)</SectionTitle>
      <DataTable
        rowKey="description"
        selectedKey={selected}
        onRowClick={(key, _row) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'description', label: 'Pattern', bold: true, render: (v) => v?.length > 44 ? v.slice(0, 43) + '…' : v },
          { key: 'occurrences', label: 'Occurrences', render: (v) => (v || 0).toLocaleString() },
          { key: 'avg_mttr_hours', label: 'Avg MTTR', render: (v) => v ? `${v.toFixed(1)}h` : '—' },
        ]}
        rows={rows.map((row, i) => ({ ...row, description: row.description || `Pattern ${i + 1}` }))}
      />

      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail — Repeat Pattern</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Occurrences</p>
              <p className="text-xl font-bold text-sky-700">{(detail.occurrences || 0).toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Avg MTTR</p>
              <p className="text-xl font-bold text-amber-700">{detail.avg_mttr_hours ? `${detail.avg_mttr_hours.toFixed(1)}h` : '—'}</p>
            </div>
          </div>
          <p className="text-xs text-slate-600 mt-3 break-words">{detail.description}</p>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: RCA and Ownership ───────────────────────────────────────── */
// Function: RCAOwnershipView
function RCAOwnershipView({ data }) {
  const [causeSelected, setCauseSelected] = useState(null)
  const [ownerSelected, setOwnerSelected] = useState(null)
  const detailRef = useRef(null)

  const causes = data?.top_root_causes || []
  const owners = data?.ownership_distribution || []
  const causeDetail = causeSelected != null
    ? causes.find((cause) => (cause.cause || '') === causeSelected)
    : null
  const ownerDetail = ownerSelected != null
    ? owners.find((owner) => (owner.assigned_to || '') === ownerSelected)
    : null

  useEffect(() => {
    if ((causeDetail || ownerDetail) && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [causeDetail, ownerDetail])

  return (
    <>
      <SectionTitle>RCA Coverage & Ownership</SectionTitle>
      <div className="grid grid-cols-3 gap-2 mb-2">
        <div className="rounded-lg p-2.5 border text-center bg-emerald-50 border-emerald-200">
          <p className="text-[10px] text-slate-500">RCA Identified</p>
          <p className="text-base font-bold text-emerald-700">{(data?.rca_identified_pct || 0).toFixed(1)}%</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-slate-50 border-slate-200">
          <p className="text-[10px] text-slate-500">RCA Count</p>
          <p className="text-base font-bold text-slate-800">{(data?.rca_identified_count || 0).toLocaleString()}</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-sky-50 border-sky-200">
          <p className="text-[10px] text-slate-500">Avg Closure (RCA)</p>
          <p className="text-base font-bold text-sky-700">{data?.rca_closure_time_avg ? `${data.rca_closure_time_avg.toFixed(1)}h` : '—'}</p>
        </div>
      </div>

      <SectionTitle>L2 — Top Root Causes (click row for L3)</SectionTitle>
      <DataTable
        rowKey="cause"
        selectedKey={causeSelected}
        onRowClick={(key, _row) => setCauseSelected(causeSelected === key ? null : key)}
        columns={[
          { key: 'cause', label: 'Root Cause', bold: true, render: (v) => v?.length > 42 ? v.slice(0, 41) + '…' : v },
          { key: 'count', label: 'Count', render: (v) => (v || 0).toLocaleString() },
          { key: 'pct', label: '%', render: (v) => `${(v || 0).toFixed(1)}%` },
        ]}
        rows={causes}
      />

      <SectionTitle>L2 — Ownership Distribution (click row for L3)</SectionTitle>
      <DataTable
        rowKey="assigned_to"
        selectedKey={ownerSelected}
        onRowClick={(key, _row) => setOwnerSelected(ownerSelected === key ? null : key)}
        columns={[
          { key: 'assigned_to', label: 'Owner', bold: true, render: (v) => v?.length > 34 ? v.slice(0, 33) + '…' : v },
          { key: 'count', label: 'Tickets', render: (v) => (v || 0).toLocaleString() },
          { key: 'pct', label: '%', render: (v) => `${(v || 0).toFixed(1)}%` },
        ]}
        rows={owners}
      />

      {(causeDetail || ownerDetail) && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail</p>
          {causeDetail && (
            <div className="mb-3">
              <p className="text-[10px] text-slate-500">Selected Root Cause</p>
              <p className="text-sm font-semibold text-slate-800">{causeDetail.cause}</p>
              <p className="text-xs text-slate-600 mt-1">
                {causeDetail.count?.toLocaleString()} tickets, {(causeDetail.pct || 0).toFixed(1)}% contribution
              </p>
            </div>
          )}
          {ownerDetail && (
            <div>
              <p className="text-[10px] text-slate-500">Selected Owner</p>
              <p className="text-sm font-semibold text-slate-800">{ownerDetail.assigned_to}</p>
              <p className="text-xs text-slate-600 mt-1">
                {ownerDetail.count?.toLocaleString()} tickets, {(ownerDetail.pct || 0).toFixed(1)}% ownership share
              </p>
            </div>
          )}
        </div>
      )}
    </>
  )
}

/* ─── L2 view: SLA / KPI ──────────────────────────────────────────────── */
// Function: SLAKPIView
function SLAKPIView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const trend = data?.breach_trend || []
  const detail = selected ? trend.find((t) => t.month === selected) : null

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  return (
    <>
      <SectionTitle>SLA Risk KPIs</SectionTitle>
      <div className="grid grid-cols-2 gap-2 mb-2">
        <div className="rounded-lg p-2.5 border text-center bg-rose-50 border-rose-200">
          <p className="text-[10px] text-slate-500">Current Breach Risk</p>
          <p className="text-base font-bold text-rose-700">{(data?.current_breach_risk_pct || 0).toFixed(2)}%</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-amber-50 border-amber-200">
          <p className="text-[10px] text-slate-500">At-Risk Tickets</p>
          <p className="text-base font-bold text-amber-700">{(data?.at_risk_tickets || 0).toLocaleString()}</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-slate-50 border-slate-200">
          <p className="text-[10px] text-slate-500">Breached Tickets</p>
          <p className="text-base font-bold text-slate-800">{(data?.breached_tickets || 0).toLocaleString()}</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-emerald-50 border-emerald-200">
          <p className="text-[10px] text-slate-500">Trajectory</p>
          <p className="text-base font-bold text-emerald-700">{String(data?.trajectory || 'stable')}</p>
        </div>
      </div>

      <SectionTitle>L2 — Breach Trend (click a month for L3)</SectionTitle>
      <DataTable
        rowKey="month"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'month', label: 'Month', bold: true },
          { key: 'breach_pct', label: 'Breach %', render: (v) => `${(v || 0).toFixed(2)}%` },
          { key: 'count', label: 'Ticket Count', render: (v) => (v || 0).toLocaleString() },
        ]}
        rows={trend}
      />

      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail — {detail.month}</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Breach %</p>
              <p className="text-xl font-bold text-rose-700">{(detail.breach_pct || 0).toFixed(2)}%</p>
            </div>
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Tickets</p>
              <p className="text-xl font-bold text-sky-700">{(detail.count || 0).toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: Transformation KPI ─────────────────────────────────────── */
// Function: TransformationKPIView
function TransformationKPIView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const opportunities = data?.automation_opportunities || []
  const detail = selected ? opportunities.find((o) => o.type === selected) : null

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  return (
    <>
      <SectionTitle>Transformation KPIs</SectionTitle>
      <div className="grid grid-cols-2 gap-2 mb-2">
        <div className="rounded-lg p-2.5 border text-center bg-cyan-50 border-cyan-200">
          <p className="text-[10px] text-slate-500">Automation %</p>
          <p className="text-base font-bold text-cyan-700">{(data?.automation_pct || 0).toFixed(2)}%</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-emerald-50 border-emerald-200">
          <p className="text-[10px] text-slate-500">Effort Reduction</p>
          <p className="text-base font-bold text-emerald-700">{(data?.effort_reduction_pct || 0).toFixed(2)}%</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-amber-50 border-amber-200">
          <p className="text-[10px] text-slate-500">Incident Deflection</p>
          <p className="text-base font-bold text-amber-700">{(data?.incident_deflection_pct || 0).toFixed(2)}%</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-indigo-50 border-indigo-200">
          <p className="text-[10px] text-slate-500">Cost Take-out</p>
          <p className="text-base font-bold text-indigo-700">${(data?.cost_takeout_estimate || 0).toLocaleString()}k</p>
        </div>
      </div>

      <SectionTitle>L2 — Automation Opportunities (click a row for L3)</SectionTitle>
      <DataTable
        rowKey="type"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'type', label: 'Opportunity', bold: true, render: (v) => v?.length > 40 ? v.slice(0, 39) + '…' : v },
          { key: 'count', label: 'Volume', render: (v) => (v || 0).toLocaleString() },
          { key: 'automation_potential', label: 'Potential' },
        ]}
        rows={opportunities}
      />

      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail — {detail.type}</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Ticket Volume</p>
              <p className="text-xl font-bold text-sky-700">{(detail.count || 0).toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Potential</p>
              <p className="text-xl font-bold text-emerald-700">{detail.automation_potential || '—'}</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: Adhoc vs BAU ───────────────────────────────────────────── */
// Function: AdhocVsBauView
function AdhocVsBauView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)

  const rows = [
    { type: 'BAU Work', count: data?.bau_count || 0, pct: data?.bau_pct || 0 },
    { type: 'Ad-hoc Work', count: data?.adhoc_count || 0, pct: data?.adhoc_pct || 0 },
    { type: 'Enhancements', count: data?.enhancement_count || 0, pct: data?.enhancement_pct || 0 },
  ]
  const detail = selected ? rows.find((r) => r.type === selected) : null

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  return (
    <>
      <SectionTitle>Work Mix Overview</SectionTitle>
      <div className="rounded-lg p-2.5 border bg-slate-50 border-slate-200 mb-2 text-center">
        <p className="text-[10px] text-slate-500">Total Tickets</p>
        <p className="text-lg font-bold text-slate-800">{(data?.total_tickets || 0).toLocaleString()}</p>
      </div>

      <SectionTitle>L2 — BAU vs Ad-hoc vs Enhancements (click row for L3)</SectionTitle>
      <DataTable
        rowKey="type"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'type', label: 'Type', bold: true },
          { key: 'count', label: 'Count', render: (v) => (v || 0).toLocaleString() },
          { key: 'pct', label: '%', render: (v) => `${(v || 0).toFixed(2)}%` },
        ]}
        rows={rows}
      />

      <SectionTitle>Aging Alerts</SectionTitle>
      <DataTable
        columns={[
          { key: 'severity', label: 'Severity', bold: true },
          { key: 'message', label: 'Message' },
        ]}
        rows={(data?.aging_alerts || []).map((a) => ({ severity: a.severity, message: a.message }))}
      />

      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail — {detail.type}</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Ticket Count</p>
              <p className="text-xl font-bold text-sky-700">{(detail.count || 0).toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Share</p>
              <p className="text-xl font-bold text-amber-700">{(detail.pct || 0).toFixed(2)}%</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2 view: People and Capacity ─────────────────────────────────────── */
// Function: PeopleCapacityView
function PeopleCapacityView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  const teams = data?.team_workload_distribution || []
  const detail = selected ? teams.find((t) => t.team === selected) : null

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  return (
    <>
      <SectionTitle>Capacity KPIs</SectionTitle>
      <div className="grid grid-cols-2 gap-2 mb-2">
        <div className="rounded-lg p-2.5 border text-center bg-cyan-50 border-cyan-200">
          <p className="text-[10px] text-slate-500">Estimated Staff</p>
          <p className="text-base font-bold text-cyan-700">{(data?.total_staff_estimated || 0).toLocaleString()}</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-emerald-50 border-emerald-200">
          <p className="text-[10px] text-slate-500">Tickets / Person</p>
          <p className="text-base font-bold text-emerald-700">{(data?.tickets_per_person || 0).toFixed(2)}</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-indigo-50 border-indigo-200">
          <p className="text-[10px] text-slate-500">Capacity Utilization</p>
          <p className="text-base font-bold text-indigo-700">{(data?.capacity_utilization_pct || 0).toFixed(2)}%</p>
        </div>
        <div className="rounded-lg p-2.5 border text-center bg-amber-50 border-amber-200">
          <p className="text-[10px] text-slate-500">Rebadged Resources</p>
          <p className="text-base font-bold text-amber-700">{(data?.rebadged_resources || 0).toLocaleString()}</p>
        </div>
      </div>

      <SectionTitle>L2 — Team Workload Distribution (click row for L3)</SectionTitle>
      <DataTable
        rowKey="team"
        selectedKey={selected}
        onRowClick={(key) => setSelected(selected === key ? null : key)}
        columns={[
          { key: 'team', label: 'Team', bold: true, render: (v) => v?.length > 30 ? v.slice(0, 29) + '…' : v },
          { key: 'total_tickets', label: 'Total', render: (v) => (v || 0).toLocaleString() },
          { key: 'incidents', label: 'Inc', render: (v) => (v || 0).toLocaleString() },
          { key: 'changes', label: 'Chg', render: (v) => (v || 0).toLocaleString() },
          { key: 'service_requests', label: 'SR', render: (v) => (v || 0).toLocaleString() },
        ]}
        rows={teams}
      />

      {detail && (
        <div ref={detailRef} className="mt-3 rounded-xl border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-bold text-sky-700 mb-2">L3 Detail — {detail.team}</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Total Tickets</p>
              <p className="text-xl font-bold text-sky-700">{(detail.total_tickets || 0).toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg p-2 border border-sky-100 text-center">
              <p className="text-[10px] text-slate-500">Incident / Change / SR</p>
              <p className="text-sm font-bold text-indigo-700">{detail.incidents || 0} / {detail.changes || 0} / {detail.service_requests || 0}</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

/* ─── L2/L3 view: FRM End State Targets ────────────────────────────────── */
// Function: FRMEndStateView
function FRMEndStateView({ data }) {
  const [selected, setSelected] = useState(null)
  const detailRef = useRef(null)
  // data is the FRM_METRICS array passed from ExecutiveCockpit
  const metrics = Array.isArray(data) ? data : []
  const detail = selected ? metrics.find((m) => m.id === selected) : null

  useEffect(() => {
    if (detail && detailRef.current) {
      detailRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [detail])

  // Function: effortColor
  const effortColor = (effort = '') => {
    if (effort.toLowerCase().startsWith('high')) return { bg: 'bg-rose-50', border: 'border-rose-200', text: 'text-rose-700', badge: 'bg-rose-100 text-rose-700' }
    if (effort.toLowerCase().startsWith('medium')) return { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-700' }
    return { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-700' }
  }

  return (
    <>
      {/* Header summary */}
      <SectionTitle>FRM End State — 5 KPI Transformation Commitments</SectionTitle>
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="rounded-xl p-3 border text-center bg-indigo-50 border-indigo-200">
          <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wide">KPIs Tracked</p>
          <p className="text-2xl font-extrabold text-indigo-700 leading-tight">5</p>
        </div>
        <div className="rounded-xl p-3 border text-center bg-emerald-50 border-emerald-200">
          <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wide">Owner</p>
          <p className="text-sm font-bold text-emerald-700 leading-tight mt-1">Novastra</p>
        </div>
        <div className="rounded-xl p-3 border text-center bg-amber-50 border-amber-200">
          <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wide">Reference</p>
          <p className="text-sm font-bold text-amber-700 leading-tight mt-1">June 2026</p>
        </div>
      </div>

      {/* Visual roadmap strip */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 mb-4">
        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-3">Roadmap Overview</p>
        <div className="space-y-2">
          {metrics.map((m) => {
            const isUp = m.direction === 'up'
            return (
              <div key={m.id} className="flex items-center gap-3">
                <div className="text-[10px] font-semibold text-slate-600 w-28 flex-shrink-0 truncate">{m.label}</div>
                <div className="flex items-center gap-1 flex-1 min-w-0">
                  <span className="text-[10px] text-slate-400 flex-shrink-0">{m.baseline}</span>
                  <div className="flex-1 flex items-center gap-0.5 mx-1">
                    <div className="flex-1 h-1.5 rounded-full bg-slate-200" />
                    <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: m.accentColor }} />
                    <div className="flex-1 h-1.5 rounded-full" style={{ background: `${m.accentColor}60` }} />
                    <div className="w-2 h-2 rounded-full flex-shrink-0 ring-1 ring-offset-0.5" style={{ background: m.accentColor, ringColor: m.accentColor }} />
                  </div>
                  <span className="text-[10px] font-bold flex-shrink-0" style={{ color: m.accentColor }}>{m.year3}</span>
                </div>
                <div className="flex-shrink-0">
                  {isUp
                    ? <TrendingUp className="w-3 h-3 text-emerald-500" />
                    : <TrendingDown className="w-3 h-3 text-rose-500" />}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* L2 table */}
      <SectionTitle>L2 — KPI Targets (click a row for L3 detail)</SectionTitle>
      <div className="overflow-x-auto rounded-xl border border-slate-200 mb-2">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="px-3 py-2.5 text-left font-semibold text-slate-500 uppercase tracking-wide">Parameter</th>
              <th className="px-3 py-2.5 text-center font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">Baseline</th>
              <th className="px-3 py-2.5 text-center font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">Year 1</th>
              <th className="px-3 py-2.5 text-center font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">Year 3</th>
              <th className="px-3 py-2.5 text-center font-semibold text-slate-500 uppercase tracking-wide">Goal</th>
              <th className="px-3 py-2.5 w-6" />
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => {
              const isSelected = selected === m.id
              const isUp = m.direction === 'up'
              return (
                <tr
                  key={m.id}
                  onClick={() => setSelected(isSelected ? null : m.id)}
                  className={`border-b border-slate-100 last:border-0 cursor-pointer transition-colors ${isSelected ? 'bg-sky-50' : 'hover:bg-slate-50'}`}
                >
                  <td className="px-3 py-2.5 font-semibold text-slate-800 whitespace-nowrap">{m.fullName}</td>
                  <td className="px-3 py-2.5 text-center text-slate-500">{m.baseline}</td>
                  <td className="px-3 py-2.5 text-center font-semibold" style={{ color: m.accentColor }}>{m.year1}</td>
                  <td className="px-3 py-2.5 text-center">
                    <span className="font-extrabold" style={{ color: m.accentColor }}>{m.year3}</span>
                  </td>
                  <td className="px-3 py-2.5 text-center">
                    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-semibold
                      ${isUp ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                      {isUp ? <TrendingUp className="w-2.5 h-2.5" /> : <TrendingDown className="w-2.5 h-2.5" />}
                      {isUp ? 'Increase' : 'Reduce'}
                    </span>
                  </td>
                  <td className="px-3 py-2.5">
                    {isSelected
                      ? <ChevronDown className="w-3 h-3 text-sky-500" />
                      : <ChevronRight className="w-3 h-3 text-slate-300" />}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* L3 detail panel */}
      {detail && (() => {
        const effort = detail.effort || ''
        const ec = effortColor(effort)
        return (
          <div ref={detailRef} className="mt-3 rounded-2xl border border-sky-200 bg-gradient-to-br from-sky-50 to-white p-5">
            <div className="flex items-start justify-between gap-3 mb-4">
              <div>
                <p className="text-xs font-extrabold text-sky-700 uppercase tracking-wider">L3 Detail</p>
                <p className="text-base font-bold text-slate-800 mt-0.5">{detail.fullName}</p>
              </div>
              <div className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold"
                   style={{ background: `${detail.accentColor}15`, border: `1px solid ${detail.accentColor}40`, color: detail.accentColor }}>
                {detail.direction === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {detail.direction === 'up' ? 'Target: Increase' : 'Target: Reduce'}
              </div>
            </div>

            {/* 3 value cards */}
            <div className="grid grid-cols-3 gap-2 mb-4">
              {[
                { label: 'Baseline', value: detail.baseline, color: '#64748b', bg: 'bg-slate-100', border: 'border-slate-200' },
                { label: 'Year 1 Target', value: detail.year1, color: detail.accentColor, bg: 'bg-white', border: 'border-sky-200' },
                { label: 'Year 3 Target', value: detail.year3, color: detail.accentColor, bg: 'bg-white', border: 'border-sky-200' },
              ].map(({ label, value, color, bg, border }) => (
                <div key={label} className={`${bg} rounded-xl p-3 border ${border} text-center`}>
                  <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wide">{label}</p>
                  <p className="text-lg font-extrabold leading-tight mt-1" style={{ color }}>{value}</p>
                </div>
              ))}
            </div>

            {/* Detail sections */}
            <div className="space-y-2.5">
              <div className="bg-white rounded-xl p-3.5 border border-sky-100">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <Gauge className="w-3.5 h-3.5 text-sky-500 flex-shrink-0" />
                  <p className="text-[10px] font-bold text-sky-600 uppercase tracking-wider">Measurement Method</p>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">{detail.measurement}</p>
              </div>

              <div className="bg-white rounded-xl p-3.5 border border-indigo-100">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-indigo-500 flex-shrink-0" />
                  <p className="text-[10px] font-bold text-indigo-600 uppercase tracking-wider">Owner</p>
                </div>
                <p className="text-sm font-bold text-slate-800">{detail.owner}</p>
              </div>

              <div className={`rounded-xl p-3.5 border ${ec.bg} ${ec.border}`}>
                <div className="flex items-center justify-between mb-1.5">
                  <p className={`text-[10px] font-bold uppercase tracking-wider ${ec.text}`}>Nissan Effort Required</p>
                  <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${ec.badge}`}>
                    {effort.split(' ')[0]} {effort.split(' ')[1] || ''}
                  </span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">{effort}</p>
              </div>

              <div className="bg-rose-50 rounded-xl p-3.5 border border-rose-100">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <AlertCircle className="w-3.5 h-3.5 text-rose-500 flex-shrink-0" />
                  <p className="text-[10px] font-bold text-rose-600 uppercase tracking-wider">Risk</p>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">{detail.risk}</p>
              </div>
            </div>
          </div>
        )
      })()}
    </>
  )
}

/* ─── Chart type → view component map ─────────────────────────────────── */
const VIEWS = {
  'monthly-volume':               MonthlyVolumeView,
  'application-hotspots':         HotspotsView,
  'incident-mttr':                MTTRView,
  'change-risk':                  ChangeRiskView,
  'service-request-productivity': SRProductivityView,
  'executive-overview':           ExecutiveOverviewView,
  'automation-opportunities':     AutomationView,
  'repeat-incidents':             RepeatIncidentsView,
  'rca-ownership':                RCAOwnershipView,
  'sla-kpi':                      SLAKPIView,
  'transformation-kpis':          TransformationKPIView,
  'adhoc-vs-bau':                 AdhocVsBauView,
  'people-capacity':              PeopleCapacityView,
  'frm-end-state':                FRMEndStateView,
}

/* ─── Drawer shell ─────────────────────────────────────────────────────── */
// Function: DrilldownDrawer
export default function DrilldownDrawer({ open, onClose, title, chartType, data }) {
  const View = VIEWS[chartType]

  return (
    <>
      {/* Azure-style non-modal blade. Keep the dashboard canvas visible. */}
      <div
        className={`dashboard-drilldown-blade fixed top-0 right-0 h-full z-50 flex flex-col
          transform transition-all duration-350 ease-[cubic-bezier(0.23,1,0.32,1)]
          w-full sm:w-[600px]
          ${open ? 'translate-x-0 shadow-[−20px_0_60px_rgba(0,0,0,0.4)]' : 'translate-x-full'}`}
        aria-hidden={!open}
        style={{ background: '#ffffff', borderLeft: '1px solid rgba(226,232,240,0.8)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 shrink-0"
             style={{
               background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
               borderBottom: '1px solid #e2e8f0',
             }}>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl shadow-sm"
                 style={{ background: 'linear-gradient(135deg, #0ea5e9, #6366f1)' }}>
              <BarChart2 className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-800 leading-tight">{title}</p>
              <p className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold mt-0.5">L2 / L3 Drilldown</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-700 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-5 py-5 bg-white">
          {View && data
            ? <View data={data} />
            : (
              <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-300">
                <div className="p-5 rounded-2xl bg-slate-50 border border-slate-100">
                  <TrendingUp className="w-10 h-10 opacity-30" />
                </div>
                <p className="text-sm text-slate-400">No drilldown data available</p>
              </div>
            )
          }
        </div>
      </div>
    </>
  )
}
