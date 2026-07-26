// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (AutomationPage.jsx)
// Date: 2026-04-18
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { Zap, CheckCircle2, AlertCircle, Plus, Trash2 } from 'lucide-react'
import api from '../services/api.js'
import TicketPicker from '../components/TicketPicker.jsx'
import { useTicket } from '../context/TicketContext.jsx'

const TABS = ['Playbook Mapper', 'Workflow Builder']
const CATEGORIES = ['Hardware', 'Software', 'Network', 'Security', 'Access', 'Performance', 'Database', 'Other']

// Map ServiceNow category names to the page's category list
// Function: mapCategory
function mapCategory(snCat) {
  if (!snCat) return 'Other'
  const found = CATEGORIES.find(c => c.toLowerCase() === snCat.toLowerCase())
  return found || 'Other'
}

// Function: AutomationPage
export default function AutomationPage() {
  const { activeTicket } = useTicket()
  const [tab, setTab] = useState('Playbook Mapper')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // Playbook
  const [pbTitle, setPbTitle] = useState('')
  const [pbCat, setPbCat] = useState('Software')
  const [pbDesc, setPbDesc] = useState('')
  const [pbCI, setPbCI] = useState('')

  // Workflow
  const [wfDesc, setWfDesc] = useState('')
  const [wfTrigger, setWfTrigger] = useState('')
  const [wfActions, setWfActions] = useState([''])

  // â”€â”€ Wire active ticket â†’ playbook fields â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  useEffect(() => {
    if (!activeTicket) return
    setPbTitle(activeTicket.short_description || '')
    setPbCat(mapCategory(activeTicket.category))
    setPbDesc(activeTicket.description || '')
    setPbCI(activeTicket.cmdb_ci || '')
    // Seed workflow trigger from ticket priority / category
    const pLabel = (activeTicket.priority || '').split(' - ')[0] === '1' ? 'P1' :
                   (activeTicket.priority || '').split(' - ')[0] === '2' ? 'P2' : 'P3'
    setWfTrigger(`${pLabel} incident created â€” ${activeTicket.category || 'IT'} category`)
    setWfDesc(`When a ${pLabel} incident is raised for ${activeTicket.cmdb_ci || activeTicket.category || 'this CI'}, notify the ${activeTicket.assignment_group || 'support'} team and escalate if unacknowledged after 15 minutes.`)
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

  // Function: addAction
  const addAction = () => setWfActions(a => [...a, ''])
  const removeAction = i => setWfActions(a => a.filter((_, idx) => idx !== i))
  // Function: updateAction
  const updateAction = (i, v) => setWfActions(a => a.map((row, idx) => idx === i ? v : row))

  const confColor = c => c > 0.75 ? 'text-green-400' : c > 0.5 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-4">
      <div className="flex items-center gap-3">
        <Zap size={22} className="text-blue-400" />
        <div>
          <h1 className="text-sm font-semibold text-white">Intelligent Automation</h1>
          <p className="text-xs text-gray-400">Playbook mapping and natural language workflow builder</p>
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

      {tab === 'Playbook Mapper' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Incident Title</label><input className={inputCls} value={pbTitle} onChange={e => setPbTitle(e.target.value)} placeholder="e.g. SAP application unresponsive" /></div>
            <div><label className={labelCls}>Category</label><select className={inputCls} value={pbCat} onChange={e => setPbCat(e.target.value)}>{CATEGORIES.map(c => <option key={c}>{c}</option>)}</select></div>
          </div>
          <div><label className={labelCls}>Description</label><textarea className={inputCls} rows={3} value={pbDesc} onChange={e => setPbDesc(e.target.value)} placeholder="Describe the incident..." /></div>
          <div><label className={labelCls}>CI (optional)</label><input className={inputCls} value={pbCI} onChange={e => setPbCI(e.target.value)} placeholder="e.g. SAP-PROD-01" /></div>
          <button onClick={() => call('/automation/map-playbook', { incident_title: pbTitle, category: pbCat, description: pbDesc, ci: pbCI })}
            disabled={loading || !pbTitle} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Mapping...' : 'Map Playbook'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-white">{result.playbook_name}</h2>
                <div className="flex items-center gap-3">
                  <span className={`text-sm font-bold ${confColor(result.confidence)}`}>{Math.round((result.confidence || 0) * 100)}% confidence</span>
                  <span className="text-xs text-gray-400">~{result.estimated_resolution_mins} min</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-xs font-medium text-green-400 mb-3 flex items-center gap-1.5"><CheckCircle2 size={12} />Automated Steps</p>
                  <ul className="space-y-2">
                    {result.automated_steps?.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-200">
                        <CheckCircle2 size={14} className="text-green-400 shrink-0 mt-0.5" />{s}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-xs font-medium text-orange-400 mb-3 flex items-center gap-1.5"><AlertCircle size={12} />Manual Steps</p>
                  <ul className="space-y-2">
                    {result.manual_steps?.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-200">
                        <AlertCircle size={14} className="text-orange-400 shrink-0 mt-0.5" />{s}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'Workflow Builder' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div>
            <label className={labelCls}>Describe your workflow in plain English</label>
            <textarea className={inputCls} rows={4} value={wfDesc} onChange={e => setWfDesc(e.target.value)}
              placeholder="e.g. When a P1 incident is raised for SAP, notify the SAP team on Microsoft Teams and create a bridge call in Cisco Webex" />
          </div>
          <div><label className={labelCls}>Trigger Event</label><input className={inputCls} value={wfTrigger} onChange={e => setWfTrigger(e.target.value)} placeholder="e.g. P1 incident created" /></div>
          <div>
            <div className="flex items-center justify-between mb-2"><label className={labelCls}>Actions</label><button onClick={addAction} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {wfActions.map((a, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <input className={`${inputCls} flex-1`} value={a} onChange={e => updateAction(i, e.target.value)} placeholder={`Action ${i+1}`} />
                <button onClick={() => removeAction(i)} className="text-red-400 hover:text-red-300"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <button onClick={() => call('/automation/build-workflow', { description: wfDesc, trigger_event: wfTrigger, actions: wfActions.filter(Boolean) })}
            disabled={loading || !wfDesc} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Building...' : 'Build Workflow'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-white">{result.workflow_name}</h2>
                <span className="text-xs text-gray-400">~{result.estimated_execution_secs}s execution</span>
              </div>
              {result.trigger && (
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                  <p className="text-xs font-medium text-blue-400 mb-1">Trigger</p>
                  <p className="text-sm text-white">{result.trigger.event}</p>
                  {result.trigger.conditions?.map((c, i) => <p key={i} className="text-xs text-gray-400 mt-0.5"> {c}</p>)}
                </div>
              )}
              {result.steps?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-400">Steps</p>
                  {result.steps.map((s, i) => (
                    <div key={i} className="bg-gray-800 rounded-lg p-3 flex items-start gap-3">
                      <span className="w-6 h-6 rounded-full bg-blue-600/30 text-blue-300 text-xs font-bold flex items-center justify-center shrink-0">{s.step_num}</span>
                      <div>
                        <p className="text-sm text-white">{s.action}</p>
                        <p className="text-xs text-gray-400">Target: {s.target}{s.on_failure ? ` Â· On failure: ${s.on_failure}` : ''}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {result.notifications?.length > 0 && (
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-xs font-medium text-gray-400 mb-2">Notifications</p>
                  {result.notifications.map((n, i) => <p key={i} className="text-xs text-gray-300"> {n.channel}: {n.recipient} ({n.condition})</p>)}
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
