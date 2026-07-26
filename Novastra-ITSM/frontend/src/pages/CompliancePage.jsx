// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (CompliancePage.jsx)
// Date: 2026-02-13
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { ShieldCheck, Plus, Trash2 } from 'lucide-react'
import api from '../services/api.js'
import TicketPicker from '../components/TicketPicker.jsx'
import { useTicket } from '../context/TicketContext.jsx'

const TABS = ['PII Detection', 'Audit Log Summary', 'Policy Check']
const REQUEST_TYPES = ['Change Request', 'Access Request', 'Deployment Request', 'Data Access']

const RISK_COLORS = { CRITICAL: 'text-red-400 bg-red-500/10 border-red-500/30', HIGH: 'text-orange-400 bg-orange-500/10 border-orange-500/30', MEDIUM: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30', LOW: 'text-green-400 bg-green-500/10 border-green-500/30', NONE: 'text-gray-400 bg-gray-500/10 border-gray-500/30' }
const SEV_COLORS = { CRITICAL: 'text-red-400', HIGH: 'text-orange-400', MEDIUM: 'text-yellow-400', LOW: 'text-blue-400' }

// Function: CompliancePage
export default function CompliancePage() {
  const { activeTicket } = useTicket()
  const [tab, setTab] = useState('PII Detection')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // PII
  const [piiId, setPiiId] = useState('')
  const [piiText, setPiiText] = useState('')

  // Audit
  const [auditJson, setAuditJson] = useState('')
  const [auditPeriod, setAuditPeriod] = useState('')

  // Policy
  const [polType, setPolType] = useState('Change Request')
  const [polDetails, setPolDetails] = useState([{ key: '', value: '' }])
  const [polRules, setPolRules] = useState([''])

  // â”€â”€ Wire active ticket â†’ PII scan â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  useEffect(() => {
    if (!activeTicket) return
    setPiiId(activeTicket.number || '')
    // Aggregate all text fields that might contain PII
    const textParts = [
      activeTicket.short_description,
      activeTicket.description,
      activeTicket.caller_id,
      activeTicket.caller_name,
      activeTicket.work_notes,
    ].filter(Boolean)
    setPiiText(textParts.join('\n\n'))
  }, [activeTicket])

  const inputCls = 'w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'
  const labelCls = 'block text-xs font-medium text-gray-400 mb-1'

  // Function: call
  const call = async (endpoint, payload) => {
    setLoading(true); setError(''); setResult(null)
    try {
      const { data } = await api.post(endpoint, payload, { timeout: 0 })
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Request failed')
    } finally { setLoading(false) }
  }

  // Function: addDetail
  const addDetail = () => setPolDetails(d => [...d, { key: '', value: '' }])
  const removeDetail = i => setPolDetails(d => d.filter((_, idx) => idx !== i))
  // Function: updateDetail
  const updateDetail = (i, k, v) => setPolDetails(d => d.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  // Function: addRule
  const addRule = () => setPolRules(r => [...r, ''])
  const removeRule = i => setPolRules(r => r.filter((_, idx) => idx !== i))
  // Function: updateRule
  const updateRule = (i, v) => setPolRules(r => r.map((row, idx) => idx === i ? v : row))

  const toObj = rows => Object.fromEntries(rows.filter(r => r.key).map(r => [r.key, r.value]))

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-4">
      <div className="flex items-center gap-3">
        <ShieldCheck size={22} className="text-blue-400" />
        <div>
          <h1 className="text-sm font-semibold text-white">Security & Compliance</h1>
          <p className="text-xs text-gray-400">PII detection, audit log summarization, and policy compliance checks</p>
        </div>
      </div>

      <TicketPicker />

      <div className="flex flex-wrap gap-1 bg-gray-900 rounded-lg p-1 w-fit">
        {TABS.map(t => (
          <button key={t} onClick={() => { setTab(t); setResult(null); setError('') }}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${tab === t ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'PII Detection' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Ticket ID</label><input className={inputCls} value={piiId} onChange={e => setPiiId(e.target.value)} placeholder="INC0012345" /></div>
          <div><label className={labelCls}>Text to Scan for PII</label><textarea className={inputCls} rows={6} value={piiText} onChange={e => setPiiText(e.target.value)} placeholder="Paste ticket content, email, or any text to scan for personally identifiable information..." /></div>
          <button onClick={() => call('/compliance/detect-pii', { ticket_id: piiId, text: piiText })}
            disabled={loading || !piiText} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Scanning...' : 'Detect PII'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className={`flex items-center justify-between rounded-xl px-4 py-3 border ${RISK_COLORS[result.risk_level] || RISK_COLORS.NONE}`}>
                <span className="text-sm font-bold">Risk Level: {result.risk_level}</span>
                <span className="text-xs">{result.pii_found ? `${result.findings?.length} PII finding(s)` : 'No PII detected'}</span>
              </div>
              {result.findings?.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead><tr className="text-xs text-gray-500 border-b border-white/10">{['Type', 'Value (Redacted)', 'Position', 'Severity'].map(h => <th key={h} className="text-left pb-2 pr-4 font-medium">{h}</th>)}</tr></thead>
                    <tbody>
                      {result.findings.map((f, i) => (
                        <tr key={i} className="border-b border-white/5">
                          <td className="py-2 pr-4 text-white">{f.type}</td>
                          <td className="py-2 pr-4 font-mono text-gray-400 text-xs">{f.value_redacted}</td>
                          <td className="py-2 pr-4 text-gray-500">{f.position}</td>
                          <td className={`py-2 pr-4 font-medium ${SEV_COLORS[f.severity] || 'text-gray-400'}`}>{f.severity}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {result.redacted_text && (
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-2">Redacted Text</p>
                  <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">{result.redacted_text}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {tab === 'Audit Log Summary' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Period</label><input className={inputCls} value={auditPeriod} onChange={e => setAuditPeriod(e.target.value)} placeholder="e.g. 2026-06-01 to 2026-06-18" /></div>
          </div>
          <div><label className={labelCls}>Audit Logs JSON (array of {`{timestamp, user, action, resource, outcome}`})</label>
            <textarea className={inputCls} rows={7} value={auditJson} onChange={e => setAuditJson(e.target.value)}
              placeholder='[{"timestamp": "2026-06-18T09:00:00Z", "user": "jsmith", "action": "DELETE", "resource": "/api/users/42", "outcome": "success"}]' />
          </div>
          <button onClick={() => { try { call('/compliance/summarize-audit', { audit_logs: JSON.parse(auditJson || '[]'), period: auditPeriod }) } catch { setError('Invalid JSON') } }}
            disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Summarizing...' : 'Summarize Audit Log'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center gap-6">
                <div><p className="text-xs text-gray-400">Total Events</p><p className="text-2xl font-bold text-white">{result.total_events}</p></div>
                <div><p className="text-xs text-gray-400">Risk Level</p><span className={`px-3 py-1 rounded-full text-sm font-bold border ${RISK_COLORS[result.risk_level] || RISK_COLORS.NONE}`}>{result.risk_level}</span></div>
              </div>
              {result.summary && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-1">Summary</p><p className="text-sm text-gray-200">{result.summary}</p></div>}
              {result.key_activities?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Key Activities</p><ul className="space-y-1">{result.key_activities.map((a, i) => <li key={i} className="text-sm text-gray-300 flex gap-2"><span className="text-blue-400"></span>{a}</li>)}</ul></div>}
              {result.anomalies?.length > 0 && <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3"><p className="text-xs text-orange-400 mb-2">Anomalies</p><ul className="space-y-1">{result.anomalies.map((a, i) => <li key={i} className="text-sm text-orange-300 flex gap-2"><span>âš </span>{a}</li>)}</ul></div>}
              {result.compliance_concerns?.length > 0 && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3"><p className="text-xs text-red-400 mb-2">Compliance Concerns</p><ul className="space-y-1">{result.compliance_concerns.map((c, i) => <li key={i} className="text-sm text-red-300 flex gap-2"><span>âœ•</span>{c}</li>)}</ul></div>}
            </div>
          )}
        </div>
      )}

      {tab === 'Policy Check' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Request Type</label><select className={inputCls} value={polType} onChange={e => setPolType(e.target.value)}>{REQUEST_TYPES.map(t => <option key={t}>{t}</option>)}</select></div>
          <div>
            <div className="flex items-center justify-between mb-2"><label className={labelCls}>Request Details</label><button onClick={addDetail} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {polDetails.map((d, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <input className={`${inputCls} flex-1`} value={d.key} onChange={e => updateDetail(i, 'key', e.target.value)} placeholder="Field (e.g. environment)" />
                <input className={`${inputCls} flex-1`} value={d.value} onChange={e => updateDetail(i, 'value', e.target.value)} placeholder="Value (e.g. Production)" />
                <button onClick={() => removeDetail(i)} className="text-red-400 hover:text-red-300"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <div>
            <div className="flex items-center justify-between mb-2"><label className={labelCls}>Policy Rules</label><button onClick={addRule} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {polRules.map((r, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <input className={`${inputCls} flex-1`} value={r} onChange={e => updateRule(i, e.target.value)} placeholder="e.g. No production changes without CAB approval" />
                <button onClick={() => removeRule(i)} className="text-red-400 hover:text-red-300"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <button onClick={() => call('/compliance/check-policy', { request_type: polType, request_details: toObj(polDetails), policy_rules: polRules.filter(Boolean) })}
            disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Checking...' : 'Check Policy'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className={`flex items-center justify-between rounded-xl px-4 py-3 border ${result.compliant ? 'bg-green-500/10 border-green-500/30 text-green-300' : 'bg-red-500/10 border-red-500/30 text-red-300'}`}>
                <span className="text-sm font-bold">{result.compliant ? 'âœ“ Compliant' : 'âœ• Non-Compliant'}</span>
                <span className="text-xs font-semibold">{result.approval_recommendation}</span>
              </div>
              {result.violations?.length > 0 && (
                <div className="overflow-x-auto">
                  <p className="text-xs text-red-400 mb-2">Violations</p>
                  <table className="w-full text-sm">
                    <thead><tr className="text-xs text-gray-500 border-b border-white/10">{['Rule', 'Description', 'Severity'].map(h => <th key={h} className="text-left pb-2 pr-4">{h}</th>)}</tr></thead>
                    <tbody>{result.violations.map((v, i) => <tr key={i} className="border-b border-white/5"><td className="py-2 pr-4 text-gray-300">{v.rule}</td><td className="py-2 pr-4 text-gray-400 text-xs">{v.description}</td><td className={`py-2 pr-4 font-medium ${SEV_COLORS[v.severity] || ''}`}>{v.severity}</td></tr>)}</tbody>
                  </table>
                </div>
              )}
              {result.warnings?.length > 0 && <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3"><p className="text-xs text-orange-400 mb-1">Warnings</p><ul className="space-y-1">{result.warnings.map((w, i) => <li key={i} className="text-sm text-orange-300">âš  {w}</li>)}</ul></div>}
              {result.reasoning && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-1">Reasoning</p><p className="text-sm text-gray-200">{result.reasoning}</p></div>}
            </div>
          )}
        </div>
      )}

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">{error}</div>}
    </div>
  )
}
