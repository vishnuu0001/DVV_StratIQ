// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (TicketIntelligencePage.jsx)
// Date: 2025-12-25
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { Tag, Copy, Plus, Trash2, Layers } from 'lucide-react'
import api from '../services/api.js'
import TicketPicker from '../components/TicketPicker.jsx'
import { useTicket } from '../context/TicketContext.jsx'

const TABS = ['Auto-Classify', 'Find Duplicates', 'Summarize Thread']

const PRIORITY_COLORS = { P1: 'bg-red-500/20 text-red-300 border-red-500/30', P2: 'bg-orange-500/20 text-orange-300 border-orange-500/30', P3: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30', P4: 'bg-gray-500/20 text-gray-300 border-gray-500/30' }
const RISK_COLORS = { duplicate: 'bg-red-500/20 text-red-300', related: 'bg-yellow-500/20 text-yellow-300', similar: 'bg-blue-500/20 text-blue-300' }

// Function: Badge
function Badge({ color = 'blue', children }) {
  const map = { blue: 'bg-blue-500/20 text-blue-300', green: 'bg-green-500/20 text-green-300', red: 'bg-red-500/20 text-red-300', yellow: 'bg-yellow-500/20 text-yellow-300', gray: 'bg-gray-500/20 text-gray-300' }
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border border-white/10 ${map[color] || map.blue}`}>{children}</span>
}

// Function: ScoreBar
function ScoreBar({ value, max = 1, color = 'blue' }) {
  const pct = Math.min(100, (value / max) * 100)
  const c = { blue: 'bg-blue-500', green: 'bg-green-500', red: 'bg-red-500', yellow: 'bg-yellow-500' }
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${c[color] || c.blue}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-400 w-8 text-right">{Math.round(pct)}%</span>
    </div>
  )
}

// Function: TicketIntelligencePage
export default function TicketIntelligencePage() {
  const { activeTicket, tickets } = useTicket()
  const [tab, setTab] = useState('Auto-Classify')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // Classify
  const [classTitle, setClassTitle] = useState('')
  const [classDesc, setClassDesc] = useState('')
  const [classGroup, setClassGroup] = useState('')

  // Duplicates
  const [dupTitle, setDupTitle] = useState('')
  const [dupDesc, setDupDesc] = useState('')
  const [existingTickets, setExistingTickets] = useState([{ id: '', title: '', description: '' }])

  // Summarize
  const [sumId, setSumId] = useState('')
  const [thread, setThread] = useState([{ author: '', timestamp: '', content: '' }])

  // â”€â”€ Wire active ticket â†’ form fields â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  useEffect(() => {
    setResult(null)
    setError('')
    if (!activeTicket) {
      setSumId('')
      setThread([{ author: '', timestamp: '', content: '' }])
      return
    }
    setClassTitle(activeTicket.short_description || '')
    setClassDesc(activeTicket.description || '')
    setClassGroup(activeTicket.assignment_group || '')
    setDupTitle(activeTicket.short_description || '')
    setDupDesc(activeTicket.description || '')
    // Candidate matches: real tickets in the same category, so "Find
    // Duplicates" has something to actually compare against instead of
    // blank rows the user has to hand-type from other ticket screens.
    const candidates = (tickets || [])
      .filter(t => t.number !== activeTicket.number && t.category === activeTicket.category)
      .slice(0, 5)
      .map(t => ({ id: t.number || '', title: t.short_description || '', description: t.description || '' }))
    setExistingTickets(candidates.length > 0 ? candidates : [{ id: '', title: '', description: '' }])
    setSumId(activeTicket.number || '')
    // Always seed the selected ticket as source material. A ticket without
    // work notes previously left an empty or stale thread in the form.
    const seededThread = [{
      author: activeTicket.opened_by || 'Requester',
      timestamp: activeTicket.opened_at || '',
      content: [
        activeTicket.short_description && `Issue: ${activeTicket.short_description}`,
        activeTicket.description && `Description: ${activeTicket.description}`,
      ].filter(Boolean).join('\n'),
    }]
    if (activeTicket.work_notes) seededThread.push({
      author: activeTicket.assigned_to || 'Support',
      timestamp: '',
      content: `Work notes: ${activeTicket.work_notes}`,
    })
    const resolution = activeTicket.resolution_notes || activeTicket.close_notes
    if (resolution) seededThread.push({
      author: activeTicket.assigned_to || 'Support',
      timestamp: activeTicket.closed_at || '',
      content: `Resolution notes: ${resolution}`,
    })
    setThread(seededThread)
  }, [activeTicket, tickets])

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

  // Function: addTicket
  const addTicket = () => setExistingTickets(t => [...t, { id: '', title: '', description: '' }])
  const removeTicket = i => setExistingTickets(t => t.filter((_, idx) => idx !== i))
  // Function: updateTicket
  const updateTicket = (i, k, v) => setExistingTickets(t => t.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  // Function: addMsg
  const addMsg = () => setThread(t => [...t, { author: '', timestamp: '', content: '' }])
  const removeMsg = i => setThread(t => t.filter((_, idx) => idx !== i))
  // Function: updateMsg
  const updateMsg = (i, k, v) => setThread(t => t.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  const inputCls = 'w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'
  const labelCls = 'block text-xs font-medium text-gray-400 mb-1'

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-4">
      <div className="flex items-center gap-3">
        <Tag size={22} className="text-blue-400" />
        <div>
          <h1 className="text-sm font-semibold text-white">Ticket Intelligence</h1>
          <p className="text-xs text-gray-400">AI-powered ticket classification, duplicate detection, and summarization</p>
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

      {tab === 'Auto-Classify' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div>
            <label className={labelCls}>Title</label>
            <input className={inputCls} value={classTitle} onChange={e => setClassTitle(e.target.value)} placeholder="e.g. Cannot access VPN from home office" />
          </div>
          <div>
            <label className={labelCls}>Description</label>
            <textarea className={inputCls} rows={4} value={classDesc} onChange={e => setClassDesc(e.target.value)} placeholder="Describe the issue in detail..." />
          </div>
          <div>
            <label className={labelCls}>Assignment Group (optional)</label>
            <input className={inputCls} value={classGroup} onChange={e => setClassGroup(e.target.value)} placeholder="e.g. Network Operations" />
          </div>
          <button onClick={() => call('/ticket-intelligence/classify', { title: classTitle, description: classDesc, assignment_group: classGroup })}
            disabled={loading || !classTitle}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Classifying...' : 'Classify Ticket'}
          </button>
          {result && (
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between"><span className="text-xs text-gray-400">Category</span><Badge color="blue">{result.category}</Badge></div>
                <div className="flex items-center justify-between"><span className="text-xs text-gray-400">Subcategory</span><span className="text-sm text-white">{result.subcategory}</span></div>
                <div className="flex items-center justify-between"><span className="text-xs text-gray-400">Priority</span><span className={`px-2 py-0.5 rounded text-xs font-bold border ${PRIORITY_COLORS[result.priority] || PRIORITY_COLORS.P4}`}>{result.priority}</span></div>
                <div className="flex items-center justify-between"><span className="text-xs text-gray-400">Urgency</span><Badge color={result.urgency === 'High' ? 'red' : result.urgency === 'Medium' ? 'yellow' : 'gray'}>{result.urgency}</Badge></div>
                <div className="flex items-center justify-between"><span className="text-xs text-gray-400">Assignment Group</span><span className="text-sm text-white">{result.assignment_group}</span></div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 space-y-3">
                <div><span className="text-xs text-gray-400">Confidence</span><ScoreBar value={result.confidence} color="green" /></div>
                <div><span className="text-xs text-gray-400">Reasoning</span><p className="mt-1 text-xs text-gray-300 leading-relaxed">{result.reasoning}</p></div>
                <Badge color="green">Ollama LLM · {result.model || 'configured model'}</Badge>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'Find Duplicates' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Query Title</label><input className={inputCls} value={dupTitle} onChange={e => setDupTitle(e.target.value)} placeholder="New ticket title" /></div>
          <div><label className={labelCls}>Query Description</label><textarea className={inputCls} rows={3} value={dupDesc} onChange={e => setDupDesc(e.target.value)} placeholder="New ticket description" /></div>
          <div className="space-y-2">
            <div className="flex items-center justify-between"><label className={labelCls}>Existing Tickets</label><button onClick={addTicket} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {existingTickets.map((t, i) => (
              <div key={i} className="flex gap-2 items-start">
                <input className={`${inputCls} w-20`} value={t.id} onChange={e => updateTicket(i, 'id', e.target.value)} placeholder="ID" />
                <input className={`${inputCls} flex-1`} value={t.title} onChange={e => updateTicket(i, 'title', e.target.value)} placeholder="Title" />
                <input className={`${inputCls} flex-1`} value={t.description} onChange={e => updateTicket(i, 'description', e.target.value)} placeholder="Description" />
                <button onClick={() => removeTicket(i)} className="text-red-400 hover:text-red-300 mt-2"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <button onClick={() => call('/ticket-intelligence/find-duplicates', { title: dupTitle, description: dupDesc, existing_tickets: existingTickets })}
            disabled={loading || !dupTitle}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Searching...' : 'Find Duplicates'}
          </button>
          {result && (
            <div className="space-y-2 mt-2">
              {result.duplicates?.length === 0 && <p className="text-sm text-gray-400">No duplicates found.</p>}
              {result.duplicates?.map((d, i) => (
                <div key={i} className="bg-gray-800 rounded-lg p-3 flex items-center justify-between gap-3">
                  <div><p className="text-sm text-white font-medium">{d.title || d.ticket_id}</p><p className="text-xs text-gray-400">ID: {d.ticket_id}</p></div>
                  <div className="flex items-center gap-2">
                    <ScoreBar value={d.similarity_score} />
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${RISK_COLORS[d.relationship] || ''}`}>{d.relationship}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'Summarize Thread' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Ticket ID</label><input className={inputCls} value={sumId} onChange={e => setSumId(e.target.value)} placeholder="INC0012345" /></div>
          <div className="space-y-2">
            <div className="flex items-center justify-between"><label className={labelCls}>Thread Messages</label><button onClick={addMsg} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {thread.map((m, i) => (
              <div key={i} className="flex gap-2 items-start">
                <input className={`${inputCls} w-28`} value={m.author} onChange={e => updateMsg(i, 'author', e.target.value)} placeholder="Author" />
                <input className={`${inputCls} w-36`} value={m.timestamp} onChange={e => updateMsg(i, 'timestamp', e.target.value)} placeholder="Timestamp" />
                <input className={`${inputCls} flex-1`} value={m.content} onChange={e => updateMsg(i, 'content', e.target.value)} placeholder="Message content" />
                <button onClick={() => removeMsg(i)} className="text-red-400 hover:text-red-300 mt-2"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <button onClick={() => call('/ticket-intelligence/summarize', { ticket_id: sumId, thread })}
            disabled={loading || !sumId.trim() || !thread.some(m => m.content.trim())}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Summarizing...' : 'Summarize Thread'}
          </button>
          {result && (
            <div className="mt-3 space-y-3">
              <div className="bg-gray-800 rounded-lg p-4"><p className="text-xs text-gray-400 mb-1">Summary</p><p className="text-sm text-white leading-relaxed">{result.summary}</p></div>
              <div className="bg-gray-800 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-2">Key Actions</p>
                {result.key_actions?.length > 0
                  ? <ul className="space-y-1">{result.key_actions.map((a, i) => <li key={i} className="text-sm text-gray-300 flex items-start gap-2"><span className="text-green-500 mt-0.5">✓</span>{a}</li>)}</ul>
                  : <p className="text-sm text-gray-400">No completed actions are recorded in this thread.</p>}
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-2">Next Steps</p>
                {result.next_steps?.length > 0
                  ? <ul className="space-y-1">{result.next_steps.map((s, i) => <li key={i} className="text-sm text-gray-300 flex items-start gap-2"><span className="text-blue-500 mt-0.5">→</span>{s}</li>)}</ul>
                  : <p className="text-sm text-gray-400">No pending next steps are recorded in this thread.</p>}
              </div>
              <Badge color="green">Ollama LLM · {result.model || 'configured model'}</Badge>
            </div>
          )}
        </div>
      )}

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">{error}</div>}
    </div>
  )
}
