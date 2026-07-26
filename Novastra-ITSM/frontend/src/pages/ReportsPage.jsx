// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (ReportsPage.jsx)
// Date: 2026-05-02
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { BarChart3, Plus, Trash2, Copy, Check, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import api from '../services/api.js'

const TABS = ['Generate Report', 'Trend Narration', 'ITSM Metrics (KPIs)']
const REPORT_TYPES = ['Weekly Summary', 'P1 Incident Report', 'MTTR Trend', 'SLA Compliance', 'Capacity Report']

// Function: ReportsPage
export default function ReportsPage() {
  const [tab, setTab] = useState('Generate Report')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [openSections, setOpenSections] = useState({})

  // Report
  const [repType, setRepType] = useState('Weekly Summary')
  const [dateRange, setDateRange] = useState('')
  const [metrics, setMetrics] = useState([{ key: '', value: '' }])

  // Trend
  const [trendName, setTrendName] = useState('')
  const [trendCur, setTrendCur] = useState('')
  const [trendPrev, setTrendPrev] = useState('')
  const [trendUnit, setTrendUnit] = useState('')
  const [trendCtx, setTrendCtx] = useState([{ key: '', value: '' }])

  const inputCls = 'w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'
  const labelCls = 'block text-xs font-medium text-gray-400 mb-1'

  // Function: call
  const call = async (endpoint, payload) => {
    setLoading(true); setError(''); setResult(null); setOpenSections({})
    try {
      const { data } = await api.post(endpoint, payload, { timeout: 0 })
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Request failed')
    } finally { setLoading(false) }
  }

  // Function: addMetric
  const addMetric = () => setMetrics(m => [...m, { key: '', value: '' }])
  const removeMetric = i => setMetrics(m => m.filter((_, idx) => idx !== i))
  // Function: updateMetric
  const updateMetric = (i, k, v) => setMetrics(m => m.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  // Function: addCtx
  const addCtx = () => setTrendCtx(c => [...c, { key: '', value: '' }])
  const removeCtx = i => setTrendCtx(c => c.filter((_, idx) => idx !== i))
  // Function: updateCtx
  const updateCtx = (i, k, v) => setTrendCtx(c => c.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  // Function: copyMd
  const copyMd = () => {
    navigator.clipboard.writeText(result?.report_markdown || '')
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }

  const toMetricsObj = rows => Object.fromEntries(rows.filter(r => r.key).map(r => [r.key, r.value]))

  // Function: DirIcon
  const DirIcon = ({ pct }) => {
    if (pct > 0) return <TrendingUp size={28} className="text-green-400" />
    if (pct < 0) return <TrendingDown size={28} className="text-red-400" />
    return <Minus size={28} className="text-gray-400" />
  }

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-6">
      <div className="flex items-center gap-3">
        <BarChart3 size={22} className="text-blue-400" />
        <div>
          <h1 className="text-sm font-semibold text-white">Reporting & Executive Insights</h1>
          <p className="text-xs text-gray-400">AI-generated narrative reports and trend analysis</p>
        </div>
      </div>

      <div className="flex gap-1 bg-gray-900 rounded-lg p-1 w-fit">
        {TABS.map(t => (
          <button key={t} onClick={() => { setTab(t); setResult(null); setError('') }}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${tab === t ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'Generate Report' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Report Type</label><select className={inputCls} value={repType} onChange={e => setRepType(e.target.value)}>{REPORT_TYPES.map(t => <option key={t}>{t}</option>)}</select></div>
            <div><label className={labelCls}>Date Range</label><input className={inputCls} value={dateRange} onChange={e => setDateRange(e.target.value)} placeholder="e.g. 2026-06-01 to 2026-06-15" /></div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2"><label className={labelCls}>Metrics</label><button onClick={addMetric} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {metrics.map((m, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <input className={`${inputCls} flex-1`} value={m.key} onChange={e => updateMetric(i, 'key', e.target.value)} placeholder="Metric name (e.g. Total P1 Incidents)" />
                <input className={`${inputCls} w-40`} value={m.value} onChange={e => updateMetric(i, 'value', e.target.value)} placeholder="Value" />
                <button onClick={() => removeMetric(i)} className="text-red-400 hover:text-red-300"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <button onClick={() => call('/reports/generate', { report_type: repType, date_range: dateRange, metrics: toMetricsObj(metrics) })}
            disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Generating...' : 'Generate Report'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <div><h2 className="text-sm font-semibold text-white">{result.report_title}</h2>{result.period && <p className="text-xs text-gray-400">Period: {result.period}</p>}</div>
                <button onClick={copyMd} className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs rounded-lg transition-colors">
                  {copied ? <><Check size={12} className="text-green-400" />Copied</> : <><Copy size={12} />Copy Markdown</>}
                </button>
              </div>
              {result.executive_summary && <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4"><p className="text-xs text-blue-400 mb-1">Executive Summary</p><p className="text-sm text-gray-200 leading-relaxed">{result.executive_summary}</p></div>}
              {result.sections?.map((s, i) => (
                <div key={i} className="border border-white/10 rounded-lg overflow-hidden">
                  <button onClick={() => setOpenSections(o => ({ ...o, [i]: !o[i] }))} className="w-full flex items-center justify-between px-4 py-3 bg-gray-800 text-left">
                    <span className="text-sm font-medium text-white">{s.heading}</span>
                    <span className="text-gray-500 text-xs">{openSections[i] ? 'â–²' : 'â–¼'}</span>
                  </button>
                  {openSections[i] && <div className="px-4 py-3 bg-gray-900"><p className="text-xs text-gray-300 leading-relaxed">{s.content}</p></div>}
                </div>
              ))}
              {result.key_findings?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Key Findings</p><ul className="space-y-1">{result.key_findings.map((f, i) => <li key={i} className="text-sm text-gray-200 flex gap-2"><span className="text-blue-400"></span>{f}</li>)}</ul></div>}
              {result.recommendations?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Recommendations</p><ul className="space-y-1">{result.recommendations.map((r, i) => <li key={i} className="text-sm text-blue-300 flex gap-2"><span>â†’</span>{r}</li>)}</ul></div>}
            </div>
          )}
        </div>
      )}

      {tab === 'Trend Narration' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Metric Name</label><input className={inputCls} value={trendName} onChange={e => setTrendName(e.target.value)} placeholder="e.g. Mean Time to Resolve (MTTR)" /></div>
            <div><label className={labelCls}>Unit</label><input className={inputCls} value={trendUnit} onChange={e => setTrendUnit(e.target.value)} placeholder="e.g. hours, %, tickets" /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Current Value</label><input className={inputCls} type="number" value={trendCur} onChange={e => setTrendCur(e.target.value)} placeholder="e.g. 4.2" /></div>
            <div><label className={labelCls}>Previous Value</label><input className={inputCls} type="number" value={trendPrev} onChange={e => setTrendPrev(e.target.value)} placeholder="e.g. 6.1" /></div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2"><label className={labelCls}>Context (optional)</label><button onClick={addCtx} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {trendCtx.map((c, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <input className={`${inputCls} flex-1`} value={c.key} onChange={e => updateCtx(i, 'key', e.target.value)} placeholder="Context key" />
                <input className={`${inputCls} flex-1`} value={c.value} onChange={e => updateCtx(i, 'value', e.target.value)} placeholder="Value" />
                <button onClick={() => removeCtx(i)} className="text-red-400 hover:text-red-300"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <button onClick={() => call('/reports/narrate-trend', { metric_name: trendName, current_value: Number(trendCur), previous_value: Number(trendPrev), unit: trendUnit, context: toMetricsObj(trendCtx) })}
            disabled={loading || !trendName} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Narrating...' : 'Narrate Trend'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center gap-5 bg-gray-800 rounded-xl p-5">
                <DirIcon pct={result.change_pct} />
                <div>
                  <p className="text-xs text-gray-400">{result.metric_name}</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-white">{result.current_value} <span className="text-sm text-gray-400">{trendUnit}</span></span>
                    <span className={`text-sm font-semibold ${result.change_pct > 0 ? 'text-green-400' : result.change_pct < 0 ? 'text-red-400' : 'text-gray-400'}`}>{result.change_pct > 0 ? '+' : ''}{result.change_pct}%</span>
                  </div>
                  <p className="text-xs text-gray-400">vs {result.previous_value} {trendUnit} previously</p>
                </div>
              </div>
              {result.narrative && <div className="bg-gray-800 rounded-lg p-4"><p className="text-sm text-gray-200 leading-relaxed">{result.narrative}</p></div>}
              {result.contributing_factors?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Contributing Factors</p><ul className="space-y-1">{result.contributing_factors.map((f, i) => <li key={i} className="text-sm text-gray-300 flex gap-2"><span className="text-blue-400"></span>{f}</li>)}</ul></div>}
              {result.recommended_actions?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Recommended Actions</p><ul className="space-y-1">{result.recommended_actions.map((a, i) => <li key={i} className="text-sm text-blue-300 flex gap-2"><span>â†’</span>{a}</li>)}</ul></div>}
            </div>
          )}
        </div>
      )}

      {tab === 'ITSM Metrics (KPIs)' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <p className="text-xs text-gray-400">Compute MTTA, MTTR, FCR rate, SLA compliance, and other KPIs from raw ticket data.</p>
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Period Label</label><input className={inputCls} id="kpi-period" defaultValue="June 2026" /></div>
          </div>
          <div><label className={labelCls}>Tickets JSON â€” each with: priority, category, time_to_acknowledge_hours, time_to_resolve_hours, first_contact_resolution (bool), sla_met (bool)</label>
            <textarea className={inputCls} rows={10} id="kpi-tickets" defaultValue={JSON.stringify([
              { id: 'INC001', priority: 'P1', category: 'Network', time_to_acknowledge_hours: 0.5, time_to_resolve_hours: 2.5, first_contact_resolution: false, sla_met: true },
              { id: 'INC002', priority: 'P2', category: 'Application', time_to_acknowledge_hours: 1.2, time_to_resolve_hours: 6.0, first_contact_resolution: true, sla_met: true },
              { id: 'INC003', priority: 'P3', category: 'Hardware', time_to_acknowledge_hours: 3.0, time_to_resolve_hours: 28.0, first_contact_resolution: false, sla_met: false },
              { id: 'INC004', priority: 'P2', category: 'Application', time_to_acknowledge_hours: 0.8, time_to_resolve_hours: 5.5, first_contact_resolution: true, sla_met: true },
              { id: 'INC005', priority: 'P4', category: 'Request', time_to_acknowledge_hours: 8.0, time_to_resolve_hours: 48.0, first_contact_resolution: true, sla_met: true },
            ], null, 2)} />
          </div>
          <button onClick={() => {
            try {
              const tickets = JSON.parse(document.getElementById('kpi-tickets').value || '[]')
              call('/reports/itsm-metrics', { tickets, period_label: document.getElementById('kpi-period').value })
            } catch { setError('Invalid JSON for tickets') }
          }} disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Computing...' : 'Compute ITSM KPIs'}
          </button>
          {result && (
            <div className="space-y-4 mt-2">
              <div className="grid grid-cols-4 gap-3">
                {[
                  ['Health Score', `${result.health_score}/100`, result.health_score > 80 ? 'text-green-400' : result.health_score > 60 ? 'text-yellow-400' : 'text-red-400'],
                  ['MTTA', result.mtta_hours != null ? `${result.mtta_hours}h` : 'N/A', 'text-blue-400'],
                  ['MTTR', result.mttr_hours != null ? `${result.mttr_hours}h` : 'N/A', 'text-purple-400'],
                  ['FCR Rate', `${result.fcr_rate_pct}%`, 'text-emerald-400'],
                  ['SLA Compliance', `${result.sla_compliance_pct}%`, result.sla_compliance_pct >= 95 ? 'text-green-400' : 'text-orange-400'],
                  ['Median TTR', result.median_ttr_hours != null ? `${result.median_ttr_hours}h` : 'N/A', 'text-gray-300'],
                  ['Total Tickets', result.total_tickets, 'text-gray-300'],
                  ['Resolved', result.tickets_resolved, 'text-gray-300'],
                ].map(([k, v, cls]) => (
                  <div key={k} className="bg-gray-800 rounded-xl p-3 text-center">
                    <p className={`text-xl font-bold ${cls}`}>{v}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{k}</p>
                  </div>
                ))}
              </div>
              {result.key_insights?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Key Insights</p><ul className="space-y-1">{result.key_insights.map((ins, i) => <li key={i} className="text-sm text-gray-200 flex gap-2"><span className="text-blue-400"></span>{ins}</li>)}</ul></div>}
              {result.improvement_areas?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Improvement Areas</p><ul className="space-y-1">{result.improvement_areas.map((a, i) => <li key={i} className="text-sm text-yellow-300 flex gap-2"><span>âš‘</span>{a}</li>)}</ul></div>}
              {result.sla_by_priority && (
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-2">SLA Compliance by Priority</p>
                  {Object.entries(result.sla_by_priority).map(([prio, data]) => (
                    <div key={prio} className="flex items-center gap-3 text-xs mb-1.5">
                      <span className="w-6 font-bold text-white">{prio}</span>
                      <div className="flex-1 bg-gray-700 rounded-full h-1.5">
                        <div className={`h-1.5 rounded-full ${data.sla_rate_pct >= 95 ? 'bg-green-500' : data.sla_rate_pct >= 80 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${data.sla_rate_pct}%` }} />
                      </div>
                      <span className="text-gray-300 w-20 text-right">{data.sla_met}/{data.count} ({data.sla_rate_pct}%)</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">{error}</div>}
    </div>
  )
}
