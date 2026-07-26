// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (GovernancePage.jsx)
// Date: 2025-11-04
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { ShieldCheck, Eye, EyeOff, FileText, AlertTriangle } from 'lucide-react'
import api from '../services/api.js'

const TABS = ['PII Masking', 'Audit Log', 'Bias Detection', 'Data Lineage']

const SAMPLE_PII_TEXT = `Dear John Smith,

Your ticket INC0001234 has been updated. Please contact us at john.smith@company.com
or call 555-867-5309. Your reference number is 4532 1234 5678 9012.
Account SSN on file: 123-45-6789. IP: 192.168.1.100`

const SAMPLE_DATASET = JSON.stringify([
  { gender: 'M', age_group: '25-34', region: 'North', outcome: 0.82 },
  { gender: 'F', age_group: '25-34', region: 'North', outcome: 0.64 },
  { gender: 'M', age_group: '35-44', region: 'South', outcome: 0.78 },
  { gender: 'F', age_group: '35-44', region: 'South', outcome: 0.71 },
  { gender: 'M', age_group: '45-54', region: 'East', outcome: 0.88 },
  { gender: 'F', age_group: '45-54', region: 'East', outcome: 0.60 },
], null, 2)

const sevColor = s => ({ HIGH: 'text-red-400', MEDIUM: 'text-yellow-400', LOW: 'text-green-400' }[s] || 'text-gray-400')

// Function: GovernancePage
export default function GovernancePage() {
  const [tab, setTab] = useState('PII Masking')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // PII Masking
  const [piiText, setPiiText] = useState(SAMPLE_PII_TEXT)
  const [showMasked, setShowMasked] = useState(false)
  const [piiTypes, setPiiTypes] = useState([])

  // Audit Log
  const [auditLogs, setAuditLogs] = useState([])
  const [auditLoading, setAuditLoading] = useState(false)
  const [auditAction, setAuditAction] = useState('')
  const [auditResourceType, setAuditResourceType] = useState('')

  // Bias
  const [biasDataset, setBiasDataset] = useState(SAMPLE_DATASET)
  const [sensitiveAttrs, setSensitiveAttrs] = useState('gender,age_group,region')
  const [outcomeField, setOutcomeField] = useState('outcome')

  // Lineage
  const [lineageData, setLineageData] = useState([])
  const [lineageLoading, setLineageLoading] = useState(false)

  const inputCls = 'w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'
  const labelCls = 'block text-xs font-medium text-gray-400 mb-1'

  // Function: call
  const call = async (endpoint, payload) => {
    setLoading(true); setError(''); setResult(null)
    try {
      const { data } = await api.post(endpoint, payload, { timeout: 0 })
      setResult(data)
      setShowMasked(true)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Request failed')
    } finally { setLoading(false) }
  }

  // Function: loadAuditLogs
  const loadAuditLogs = async () => {
    setAuditLoading(true)
    try {
      const params = {}
      if (auditAction) params.action = auditAction
      if (auditResourceType) params.resource_type = auditResourceType
      const { data } = await api.get('/governance/audit/logs', { params })
      setAuditLogs(data.logs || [])
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Failed to load audit logs')
    } finally { setAuditLoading(false) }
  }

  // Function: loadLineage
  const loadLineage = async () => {
    setLineageLoading(true)
    try {
      const { data } = await api.get('/governance/data-lineage')
      setLineageData(data.lineage || [])
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Failed to load lineage')
    } finally { setLineageLoading(false) }
  }

  useEffect(() => {
    if (tab === 'Audit Log') loadAuditLogs()
    if (tab === 'Data Lineage') loadLineage()
  }, [tab])

  const piiTypeOptions = ['email', 'phone_us', 'phone_intl', 'ssn', 'credit_card', 'ip_address', 'date_of_birth', 'aadhaar', 'passport']

  // Function: togglePiiType
  const togglePiiType = (t) => setPiiTypes(prev => prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t])

  return (
    <div className="flex flex-col h-full bg-gray-950 text-white overflow-hidden">
      <div className="px-6 pt-5 pb-4 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-3 mb-1">
          <ShieldCheck size={20} className="text-emerald-400" />
          <h1 className="text-sm font-semibold">Security & Governance</h1>
        </div>
        <p className="text-xs text-gray-400">PII masking, audit logging, bias detection, and data lineage tracking</p>
        <div className="flex gap-1 mt-4">
          {TABS.map(t => (
            <button key={t} onClick={() => { setTab(t); setResult(null); setError('') }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${tab === t ? 'bg-emerald-600 text-white' : 'text-gray-400 hover:text-white hover:bg-white/10'}`}>
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5">
        {error && <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">{error}</div>}

        {tab === 'PII Masking' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className={labelCls}>Text to Analyze</label>
                <textarea value={piiText} onChange={e => setPiiText(e.target.value)} rows={10} className={`${inputCls} font-mono text-xs`} />
              </div>
              <div>
                <label className={labelCls}>PII Types to Mask (none = all types)</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {piiTypeOptions.map(t => (
                    <button key={t} onClick={() => togglePiiType(t)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors ${piiTypes.includes(t) ? 'bg-emerald-600/30 border-emerald-500/50 text-emerald-300' : 'border-white/10 text-gray-400 hover:text-white'}`}>
                      {t}
                    </button>
                  ))}
                </div>
              </div>
              <button onClick={() => call('/governance/pii-mask', { text: piiText, pii_types: piiTypes.length > 0 ? piiTypes : null })}
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-sm font-semibold transition-colors flex items-center justify-center gap-2">
                {loading ? 'Analyzing...' : <><EyeOff size={15} /> Detect & Mask PII</>}
              </button>
            </div>

            <div>
              {result && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    <div className={`rounded-xl p-3 text-center ${result.is_clean ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
                      <p className={`text-2xl font-bold ${result.is_clean ? 'text-green-400' : 'text-red-400'}`}>{result.total_pii_instances_masked}</p>
                      <p className="text-xs text-gray-400">PII Instances Found</p>
                    </div>
                    <div className="bg-gray-800 rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold text-emerald-400">{Object.keys(result.pii_types_found || {}).length}</p>
                      <p className="text-xs text-gray-400">PII Types Detected</p>
                    </div>
                  </div>

                  {Object.entries(result.pii_types_found || {}).length > 0 && (
                    <div className="bg-gray-800 rounded-xl p-3">
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Detected PII Types</p>
                      {Object.entries(result.pii_types_found).map(([type, count]) => (
                        <div key={type} className="flex justify-between text-xs py-0.5">
                          <span className="text-gray-300 capitalize">{type.replace('_', ' ')}</span>
                          <span className="text-red-400 font-medium">{count} instance{count > 1 ? 's' : ''}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="bg-gray-800 rounded-xl p-3">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Masked Output</p>
                      <button onClick={() => setShowMasked(p => !p)} className="text-gray-400 hover:text-white">
                        {showMasked ? <EyeOff size={14} /> : <Eye size={14} />}
                      </button>
                    </div>
                    {showMasked && (
                      <pre className="text-xs text-gray-200 font-mono whitespace-pre-wrap break-words bg-gray-900 rounded-lg p-2">
                        {result.masked_text}
                      </pre>
                    )}
                  </div>
                </div>
              )}
              {!result && !loading && <div className="flex items-center justify-center h-40 text-gray-500 text-sm">Paste text and click Detect & Mask PII</div>}
            </div>
          </div>
        )}

        {tab === 'Audit Log' && (
          <div className="space-y-4">
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <label className={labelCls}>Filter by Action</label>
                <input value={auditAction} onChange={e => setAuditAction(e.target.value)} placeholder="e.g. pii-mask" className={inputCls} />
              </div>
              <div className="flex-1">
                <label className={labelCls}>Filter by Resource Type</label>
                <input value={auditResourceType} onChange={e => setAuditResourceType(e.target.value)} placeholder="e.g. ticket" className={inputCls} />
              </div>
              <button onClick={loadAuditLogs} disabled={auditLoading}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-sm font-semibold transition-colors whitespace-nowrap">
                {auditLoading ? 'Loading...' : 'Refresh'}
              </button>
            </div>

            {auditLogs.length === 0 && !auditLoading && (
              <div className="flex items-center justify-center h-40 text-gray-500 text-sm">No audit events found. Events are logged automatically when you use API features.</div>
            )}
            <div className="space-y-1.5">
              {auditLogs.map((log, i) => (
                <div key={i} className="bg-gray-800 rounded-xl px-4 py-3 flex items-start gap-3">
                  <FileText size={14} className="text-emerald-400 mt-0.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 text-xs">
                      <span className="font-mono text-gray-400">{log.timestamp}</span>
                      <span className="font-medium text-white">{log.actor}</span>
                      <span className="text-emerald-400 font-mono">{log.action}</span>
                      {log.resource_type && <span className="text-gray-400">{log.resource_type}:{log.resource_id}</span>}
                      <span className={`ml-auto font-medium ${log.outcome === 'success' ? 'text-green-400' : 'text-red-400'}`}>{log.outcome}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'Bias Detection' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className={labelCls}>Dataset JSON (array of records)</label>
                <textarea value={biasDataset} onChange={e => setBiasDataset(e.target.value)} rows={10} className={`${inputCls} font-mono text-xs`} />
              </div>
              <div>
                <label className={labelCls}>Sensitive Attributes (comma-separated)</label>
                <input value={sensitiveAttrs} onChange={e => setSensitiveAttrs(e.target.value)} placeholder="gender,age_group,region" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Outcome Field</label>
                <input value={outcomeField} onChange={e => setOutcomeField(e.target.value)} placeholder="outcome" className={inputCls} />
              </div>
              <button
                onClick={() => {
                  let dataset
                  try { dataset = JSON.parse(biasDataset) } catch { setError('Invalid JSON'); return }
                  call('/governance/bias-check', {
                    dataset,
                    sensitive_attributes: sensitiveAttrs.split(',').map(s => s.trim()).filter(Boolean),
                    outcome_field: outcomeField,
                  })
                }}
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-sm font-semibold transition-colors">
                {loading ? 'Analyzing...' : 'Check for Bias'}
              </button>
            </div>

            <div>
              {result && (
                <div className="space-y-4">
                  <div className={`rounded-2xl border p-4 ${result.bias_detected ? 'bg-red-500/10 border-red-500/30' : 'bg-green-500/10 border-green-500/30'}`}>
                    <div className="flex items-center gap-2 mb-1">
                      {result.bias_detected ? <AlertTriangle size={16} className="text-red-400" /> : <ShieldCheck size={16} className="text-green-400" />}
                      <span className={`font-semibold ${result.bias_detected ? 'text-red-400' : 'text-green-400'}`}>
                        {result.bias_detected ? 'Bias Detected' : 'No Significant Bias'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-300">{result.recommendation}</p>
                  </div>

                  {result.results?.map((r, i) => (
                    <div key={i} className="bg-gray-800 rounded-xl p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-white capitalize">{r.attribute}</span>
                        <span className={`text-xs font-medium ${sevColor(r.severity)}`}>{r.severity}</span>
                      </div>
                      <p className="text-xs text-gray-400 mb-2">{r.recommendation}</p>
                      <div className="space-y-1">
                        {Object.entries(r.group_stats || {}).map(([group, stats]) => (
                          <div key={group} className="flex items-center gap-2 text-xs">
                            <span className="text-gray-400 w-20 truncate">{group}</span>
                            <div className="flex-1 bg-gray-700 rounded-full h-1.5">
                              <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${(stats.mean * 100).toFixed(0)}%` }} />
                            </div>
                            <span className="text-gray-300 w-12 text-right">{(stats.mean * 100).toFixed(1)}%</span>
                          </div>
                        ))}
                      </div>
                      {r.max_disparity !== undefined && (
                        <p className="text-xs text-gray-500 mt-2">Max disparity: {(r.max_disparity * 100).toFixed(1)}%</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {!result && !loading && <div className="flex items-center justify-center h-40 text-gray-500 text-sm">Run bias check to see results</div>}
            </div>
          </div>
        )}

        {tab === 'Data Lineage' && (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-400">{lineageData.length} lineage records</p>
              <button onClick={loadLineage} disabled={lineageLoading}
                className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-xs font-semibold transition-colors">
                {lineageLoading ? 'Loading...' : 'Refresh'}
              </button>
            </div>

            {lineageData.length === 0 && !lineageLoading && (
              <div className="flex items-center justify-center h-40 text-gray-500 text-sm">
                No lineage records yet. Records are created via the governance API when data flows are tracked.
              </div>
            )}

            {lineageData.map((entry, i) => (
              <div key={i} className="bg-gray-800 rounded-xl p-4 flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-1">
                    <span className="font-mono">{entry.timestamp}</span>
                    <span className="text-gray-600">|</span>
                    <span className="text-emerald-400">{entry.recorded_by}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-mono text-blue-300">{entry.source_system}</span>
                    <span className="text-gray-500">-&gt;</span>
                    <span className="font-mono text-purple-300">{entry.destination}</span>
                  </div>
                  {entry.transformation && <p className="text-xs text-gray-400 mt-0.5">Transform: {entry.transformation}</p>}
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                    {entry.data_type && <span>Type: {entry.data_type}</span>}
                    {entry.record_count > 0 && <span>{entry.record_count.toLocaleString()} records</span>}
                    {entry.tags?.map((tag, ti) => (
                      <span key={ti} className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-300">{tag}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
