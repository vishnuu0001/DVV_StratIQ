// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (RCAPage.jsx)
// Date: 2026-05-17
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { Search, Plus, Trash2, Copy, Check } from 'lucide-react'
import api from '../services/api.js'
import TicketPicker from '../components/TicketPicker.jsx'
import { useTicket } from '../context/TicketContext.jsx'

const TABS = ['Generate RCA', 'Pattern Analysis']

// Function: RCAPage
export default function RCAPage() {
  const { activeTicket } = useTicket()
  const [tab, setTab] = useState('Generate RCA')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  // RCA
  const [incId, setIncId] = useState('')
  const [rcaTitle, setRcaTitle] = useState('')
  const [rcaDesc, setRcaDesc] = useState('')
  const [services, setServices] = useState('')
  const [changes, setChanges] = useState('')
  const [timeline, setTimeline] = useState([{ timestamp: '', source: '', event: '' }])

  // Patterns
  const [patJson, setPatJson] = useState('')

  // â”€â”€ Wire active ticket â†’ RCA form â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  useEffect(() => {
    if (!activeTicket) return
    setIncId(activeTicket.number || '')
    setRcaTitle(activeTicket.short_description || '')
    setRcaDesc(activeTicket.description || '')
    setServices(activeTicket.cmdb_ci || activeTicket.assignment_group || '')
    // Seed timeline with the open event + any work notes
    const entries = [
      { timestamp: activeTicket.opened_at || '', source: activeTicket.caller_name || 'User', event: activeTicket.short_description || '' },
    ]
    if (activeTicket.work_notes) {
      entries.push({ timestamp: '', source: activeTicket.assigned_to || 'Support', event: activeTicket.work_notes })
    }
    setTimeline(entries)
    // Seed pattern analysis with this incident
    setPatJson(JSON.stringify([{
      id: activeTicket.number,
      title: activeTicket.short_description,
      category: activeTicket.category,
      ci: activeTicket.cmdb_ci || '',
      date: (activeTicket.opened_at || '').slice(0, 10),
      resolution: activeTicket.resolution_notes || activeTicket.work_notes || '',
    }], null, 2))
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

  // Function: addTl
  const addTl = () => setTimeline(t => [...t, { timestamp: '', source: '', event: '' }])
  const removeTl = i => setTimeline(t => t.filter((_, idx) => idx !== i))
  // Function: updateTl
  const updateTl = (i, k, v) => setTimeline(t => t.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  // Function: copyMd
  const copyMd = () => {
    navigator.clipboard.writeText(result?.rca_markdown || '')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-4">
      <div className="flex items-center gap-3">
        <Search size={22} className="text-blue-400" />
        <div>
          <h1 className="text-sm font-semibold text-white">Root Cause Analysis</h1>
          <p className="text-xs text-gray-400">AI-generated RCA documents and incident pattern recognition</p>
        </div>
      </div>

      <TicketPicker />

      <div className="flex gap-1 bg-gray-900 rounded-lg p-1 w-fit">
        {TABS.map(t => (
          <button key={t} onClick={() => { setTab(t); setResult(null); setError('') }}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${tab === t ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'Generate RCA' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Incident ID</label><input className={inputCls} value={incId} onChange={e => setIncId(e.target.value)} placeholder="INC0012345" /></div>
            <div><label className={labelCls}>Title</label><input className={inputCls} value={rcaTitle} onChange={e => setRcaTitle(e.target.value)} placeholder="SAP ERP production outage" /></div>
          </div>
          <div><label className={labelCls}>Description</label><textarea className={inputCls} rows={3} value={rcaDesc} onChange={e => setRcaDesc(e.target.value)} placeholder="Describe the incident..." /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Affected Services / CIs (comma-separated)</label><input className={inputCls} value={services} onChange={e => setServices(e.target.value)} placeholder="SAP ERP, HR Portal" /></div>
            <div><label className={labelCls}>Related Changes (comma-separated)</label><input className={inputCls} value={changes} onChange={e => setChanges(e.target.value)} placeholder="CHG0004567" /></div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2"><label className={labelCls}>Timeline Events</label><button onClick={addTl} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {timeline.map((e, i) => (
              <div key={i} className="flex gap-2 mb-2 items-start">
                <input className={`${inputCls} w-40`} value={e.timestamp} onChange={ev => updateTl(i, 'timestamp', ev.target.value)} placeholder="Timestamp" />
                <input className={`${inputCls} w-28`} value={e.source} onChange={ev => updateTl(i, 'source', ev.target.value)} placeholder="Source" />
                <input className={`${inputCls} flex-1`} value={e.event} onChange={ev => updateTl(i, 'event', ev.target.value)} placeholder="Event description" />
                <button onClick={() => removeTl(i)} className="text-red-400 hover:text-red-300 mt-2"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <button onClick={() => call('/rca/generate', { incident_id: incId, title: rcaTitle, description: rcaDesc, timeline, affected_services: services.split(',').map(s => s.trim()).filter(Boolean), related_changes: changes.split(',').map(c => c.trim()).filter(Boolean) })}
            disabled={loading || !rcaTitle} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Generating RCA...' : 'Generate RCA'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold text-white">RCA: {rcaTitle}</h2>
                <button onClick={copyMd} className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs rounded-lg transition-colors">
                  {copied ? <><Check size={12} className="text-green-400" />Copied</> : <><Copy size={12} />Copy RCA Markdown</>}
                </button>
              </div>
              {result.executive_summary && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-1">Executive Summary</p><p className="text-sm text-gray-200">{result.executive_summary}</p></div>}
              {result.probable_cause && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3"><p className="text-xs text-red-400 mb-1">Probable Cause</p><p className="text-sm text-white font-medium">{result.probable_cause}</p></div>}
              {result.contributing_factors?.length > 0 && (
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-2">Contributing Factors</p>
                  <ul className="space-y-1">{result.contributing_factors.map((f, i) => <li key={i} className="text-sm text-gray-300 flex gap-2"><span className="text-orange-400"></span>{f}</li>)}</ul>
                </div>
              )}
              {result.timeline_analysis && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-1">Timeline Analysis</p><p className="text-sm text-gray-200">{result.timeline_analysis}</p></div>}
              {result.impact_assessment && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-1">Impact Assessment</p><p className="text-sm text-gray-200">{result.impact_assessment}</p></div>}
              {result.preventive_actions?.length > 0 && (
                <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                  <p className="text-xs text-green-400 mb-2">Preventive Actions</p>
                  <ul className="space-y-1">{result.preventive_actions.map((a, i) => <li key={i} className="text-sm text-gray-200 flex gap-2"><span className="text-green-400">âœ“</span>{a}</li>)}</ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {tab === 'Pattern Analysis' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Incidents JSON (array of {`{id, title, category, ci, date, resolution}`})</label>
            <textarea className={inputCls} rows={8} value={patJson} onChange={e => setPatJson(e.target.value)}
              placeholder='[{"id": "INC001", "title": "Network flap", "category": "Network", "ci": "ROUTER-01", "date": "2026-06-01", "resolution": "Restarted interface"}]' />
          </div>
          <button onClick={() => { try { call('/rca/find-patterns', { incidents: JSON.parse(patJson || '[]') }) } catch { setError('Invalid JSON') } }}
            disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Analysing...' : 'Find Patterns'}
          </button>
          {result && (
            <div className="space-y-4">
              <p className="text-xs text-gray-400">{result.total_incidents} incidents analysed Â· {result.clusters?.length} cluster(s) identified</p>
              {result.clusters?.map((c, i) => (
                <div key={i} className="bg-gray-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-white">{c.cluster_name}</h3>
                    <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-xs rounded-full">{c.frequency} incidents</span>
                  </div>
                  <p className="text-xs text-gray-300">{c.pattern_description}</p>
                  {c.systemic_issue && <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg px-3 py-2"><p className="text-xs text-orange-300"><span className="font-medium">Systemic Issue:</span> {c.systemic_issue}</p></div>}
                  {c.recommended_fix && <p className="text-xs text-green-300 flex gap-1.5"><span>â†’</span>{c.recommended_fix}</p>}
                  <div className="flex flex-wrap gap-1 mt-1">{c.incident_ids?.slice(0, 8).map(id => <span key={id} className="px-1.5 py-0.5 bg-gray-700 text-gray-400 text-xs rounded">{id}</span>)}{c.incident_ids?.length > 8 && <span className="text-xs text-gray-500">+{c.incident_ids.length - 8} more</span>}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">{error}</div>}
    </div>
  )
}
