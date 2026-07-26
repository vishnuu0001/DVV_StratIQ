// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (KnowledgeMgmtPage.jsx)
// Date: 2026-07-01
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { BookOpen, Plus, Trash2, Copy, Check } from 'lucide-react'
import api from '../services/api.js'
import TicketPicker from '../components/TicketPicker.jsx'
import { useTicket } from '../context/TicketContext.jsx'

const TABS = ['Generate KB Article', 'KB Gap Analysis']

const RESOLVED_STATES = new Set(['resolved', 'closed'])

// Function: KnowledgeMgmtPage
export default function KnowledgeMgmtPage() {
  const { activeTicket, tickets } = useTicket()
  const [tab, setTab] = useState('Generate KB Article')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  // Article
  const [ticketId, setTicketId] = useState('')
  const [artTitle, setArtTitle] = useState('')
  const [category, setCategory] = useState('')
  const [steps, setSteps] = useState([''])
  const [tags, setTags] = useState('')

  // Gap
  const [gapJson, setGapJson] = useState('')
  const [gapTickets, setGapTickets] = useState([{ title: '', category: '', description: '' }])
  const [gapMode, setGapMode] = useState('manual')

  // â”€â”€ Wire active ticket â†’ form fields â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  useEffect(() => {
    if (!activeTicket) return
    setTicketId(activeTicket.number || '')
    setCategory(activeTicket.category || '')
    setArtTitle(activeTicket.short_description || '')
    setTags([activeTicket.category, activeTicket.subcategory].filter(Boolean).join(', ').toLowerCase())
    // Populate steps from work_notes / resolution_notes if available
    const notes = (activeTicket.work_notes || activeTicket.resolution_notes || '').trim()
    if (notes) {
      const lines = notes.split('\n').map(l => l.trim()).filter(Boolean)
      setSteps(lines.length > 0 ? lines : [''])
    }
    // Seed gap analysis with real unresolved tickets — coverage/frequency
    // stats need volume; a single ticket can't show a meaningful gap.
    const unresolved = (tickets || [])
      .filter(t => !RESOLVED_STATES.has((t.state || '').toLowerCase()))
      .slice(0, 20)
      .map(t => ({
        title: t.short_description || '',
        category: t.category || '',
        description: (t.description || '').slice(0, 250),
      }))
    setGapTickets(unresolved.length > 0 ? unresolved : [{
      title: activeTicket.short_description || '',
      category: activeTicket.category || '',
      description: (activeTicket.description || '').slice(0, 250),
    }])
  }, [activeTicket, tickets])

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

  // Function: copyMd
  const copyMd = () => {
    if (result?.draft_markdown || result?.report_markdown) {
      navigator.clipboard.writeText(result.draft_markdown || '')
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // Function: addStep
  const addStep = () => setSteps(s => [...s, ''])
  const removeStep = i => setSteps(s => s.filter((_, idx) => idx !== i))
  // Function: updateStep
  const updateStep = (i, v) => setSteps(s => s.map((row, idx) => idx === i ? v : row))

  // Function: addGapRow
  const addGapRow = () => setGapTickets(t => [...t, { title: '', category: '', description: '' }])
  const removeGapRow = i => setGapTickets(t => t.filter((_, idx) => idx !== i))
  // Function: updateGapRow
  const updateGapRow = (i, k, v) => setGapTickets(t => t.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  const coverageColor = score => score >= 70 ? 'text-green-400' : score >= 40 ? 'text-yellow-400' : 'text-red-400'
  const priBadge = { HIGH: 'bg-red-500/20 text-red-300', MEDIUM: 'bg-yellow-500/20 text-yellow-300', LOW: 'bg-blue-500/20 text-blue-300' }

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-4">
      <div className="flex items-center gap-3">
        <BookOpen size={22} className="text-blue-400" />
        <div>
          <h1 className="text-sm font-semibold text-white">Knowledge Management</h1>
          <p className="text-xs text-gray-400">AI-assisted KB article generation and gap analysis</p>
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

      {tab === 'Generate KB Article' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Ticket ID</label><input className={inputCls} value={ticketId} onChange={e => setTicketId(e.target.value)} placeholder="INC0012345" /></div>
            <div><label className={labelCls}>Category</label><input className={inputCls} value={category} onChange={e => setCategory(e.target.value)} placeholder="e.g. Network" /></div>
          </div>
          <div><label className={labelCls}>Article Title</label><input className={inputCls} value={artTitle} onChange={e => setArtTitle(e.target.value)} placeholder="e.g. How to reconnect VPN after password change" /></div>
          <div>
            <div className="flex items-center justify-between mb-2"><label className={labelCls}>Resolution Steps</label><button onClick={addStep} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {steps.map((s, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <span className="text-xs text-gray-500 mt-2.5 w-5 text-right">{i+1}.</span>
                <input className={`${inputCls} flex-1`} value={s} onChange={e => updateStep(i, e.target.value)} placeholder={`Step ${i+1}`} />
                <button onClick={() => removeStep(i)} className="text-red-400 hover:text-red-300 mt-2"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <div><label className={labelCls}>Tags (comma-separated)</label><input className={inputCls} value={tags} onChange={e => setTags(e.target.value)} placeholder="vpn, network, connectivity" /></div>
          <button onClick={() => call('/knowledge-mgmt/generate-article', { ticket_id: ticketId, title: artTitle, resolution_steps: steps.filter(Boolean), category, tags: tags.split(',').map(t => t.trim()).filter(Boolean) })}
            disabled={loading || !artTitle}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Generating...' : 'Generate Article'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold text-white">{result.article_title}</h2>
                <button onClick={copyMd} className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs rounded-lg transition-colors">
                  {copied ? <><Check size={12} className="text-green-400" />Copied</> : <><Copy size={12} />Copy Markdown</>}
                </button>
              </div>
              {result.summary && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-1">Summary</p><p className="text-sm text-gray-200">{result.summary}</p></div>}
              {result.symptoms?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Symptoms</p><ul className="space-y-1">{result.symptoms.map((s, i) => <li key={i} className="text-sm text-gray-300 flex items-start gap-2"><span className="text-yellow-400"></span>{s}</li>)}</ul></div>}
              {result.resolution_steps?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Resolution Steps</p><ol className="space-y-1 list-none">{result.resolution_steps.map((s, i) => <li key={i} className="text-sm text-gray-300 flex items-start gap-2"><span className="text-blue-400 font-mono text-xs mt-0.5">{i+1}.</span>{s}</li>)}</ol></div>}
              {result.tags?.length > 0 && <div className="flex flex-wrap gap-1">{result.tags.map(t => <span key={t} className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-xs rounded-full border border-blue-500/30">{t}</span>)}</div>}
            </div>
          )}
        </div>
      )}

      {tab === 'KB Gap Analysis' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="flex gap-2 mb-2">
            {['manual', 'json'].map(m => (
              <button key={m} onClick={() => setGapMode(m)} className={`px-3 py-1 rounded text-xs font-medium transition-colors ${gapMode === m ? 'bg-gray-700 text-white' : 'text-gray-500 hover:text-gray-300'}`}>{m === 'manual' ? 'Manual Entry' : 'Paste JSON'}</button>
            ))}
          </div>
          {gapMode === 'json' ? (
            <div><label className={labelCls}>Unresolved Tickets JSON (array of {`{title, category, description}`})</label><textarea className={inputCls} rows={8} value={gapJson} onChange={e => setGapJson(e.target.value)} placeholder='[{"title": "VPN issue", "category": "Network", "description": "..."}]' /></div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center justify-between"><label className={labelCls}>Unresolved Tickets</label><button onClick={addGapRow} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
              {gapTickets.map((t, i) => (
                <div key={i} className="flex gap-2 items-start">
                  <input className={`${inputCls} flex-1`} value={t.title} onChange={e => updateGapRow(i, 'title', e.target.value)} placeholder="Title" />
                  <input className={`${inputCls} w-32`} value={t.category} onChange={e => updateGapRow(i, 'category', e.target.value)} placeholder="Category" />
                  <input className={`${inputCls} flex-1`} value={t.description} onChange={e => updateGapRow(i, 'description', e.target.value)} placeholder="Description" />
                  <button onClick={() => removeGapRow(i)} className="text-red-400 hover:text-red-300 mt-2"><Trash2 size={14} /></button>
                </div>
              ))}
            </div>
          )}
          <button onClick={() => {
            let tickets = gapTickets
            if (gapMode === 'json') { try { tickets = JSON.parse(gapJson) } catch { setError('Invalid JSON'); return } }
            call('/knowledge-mgmt/gap-analysis', { unresolved_tickets: tickets })
          }} disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Analysing...' : 'Run Gap Analysis'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center gap-6">
                <div><p className="text-xs text-gray-400">Coverage Score</p><p className={`text-3xl font-bold ${coverageColor(result.coverage_score)}`}>{result.coverage_score}%</p></div>
                <div><p className="text-xs text-gray-400">Unresolved Tickets</p><p className="text-2xl font-bold text-white">{result.total_unresolved}</p></div>
              </div>
              <div className="space-y-2">
                {result.gaps?.map((g, i) => (
                  <div key={i} className="bg-gray-800 rounded-lg p-3 flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm text-white font-medium">{g.suggested_article_title}</p>
                      <p className="text-xs text-gray-400">{g.topic} Â· {g.frequency} occurrences Â· {g.coverage_status}</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${priBadge[g.priority] || 'bg-gray-500/20 text-gray-300'}`}>{g.priority}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">{error}</div>}
    </div>
  )
}
