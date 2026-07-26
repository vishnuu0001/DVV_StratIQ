// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (SentimentPage.jsx)
// Date: 2025-08-16
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { Heart, Plus, Trash2, Copy, Check } from 'lucide-react'
import api from '../services/api.js'
import TicketPicker from '../components/TicketPicker.jsx'
import { useTicket } from '../context/TicketContext.jsx'

const TABS = ['Ticket Sentiment', 'Survey Analysis', 'Response Coach']

const SENT_STYLES = {
  positive: 'bg-green-500/20 text-green-300 border-green-500/30',
  neutral: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
  negative: 'bg-red-500/20 text-red-300 border-red-500/30',
  frustrated: 'bg-red-600/30 text-red-200 border-red-600/40',
}

// Function: ScoreGauge
function ScoreGauge({ label, value }) {
  const pct = (value / 10) * 100
  const color = pct >= 70 ? 'bg-green-500' : pct >= 40 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs"><span className="text-gray-400">{label}</span><span className="text-white font-medium">{value?.toFixed(1)}/10</span></div>
      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden"><div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} /></div>
    </div>
  )
}

// Function: SentimentPage
export default function SentimentPage() {
  const { activeTicket } = useTicket()
  const [tab, setTab] = useState('Ticket Sentiment')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  // Ticket sentiment
  const [tId, setTId] = useState('')
  const [tDesc, setTDesc] = useState('')
  const [updates, setUpdates] = useState([''])

  // Survey
  const [surveys, setSurveys] = useState([{ id: '1', rating: 4, free_text: '' }])

  // Coach
  const [cId, setCId] = useState('')
  const [cDraft, setCDraft] = useState('')
  const [cCustomer, setCCustomer] = useState('')

  // â”€â”€ Wire active ticket â†’ sentiment form â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  useEffect(() => {
    if (!activeTicket) return
    setTId(activeTicket.number || '')
    setTDesc(activeTicket.description || activeTicket.short_description || '')
    setCId(activeTicket.number || '')
    setCCustomer(activeTicket.description || '')
    const wn = activeTicket.work_notes
    if (wn) setUpdates([wn])
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

  // Function: addUpdate
  const addUpdate = () => setUpdates(u => [...u, ''])
  const removeUpdate = i => setUpdates(u => u.filter((_, idx) => idx !== i))
  // Function: updateUpd
  const updateUpd = (i, v) => setUpdates(u => u.map((row, idx) => idx === i ? v : row))

  // Function: addSurvey
  const addSurvey = () => setSurveys(s => [...s, { id: String(Date.now()), rating: 4, free_text: '' }])
  const removeSurvey = i => setSurveys(s => s.filter((_, idx) => idx !== i))
  // Function: updateSurvey
  const updateSurvey = (i, k, v) => setSurveys(s => s.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  // Function: copyDraft
  const copyDraft = () => {
    navigator.clipboard.writeText(result?.improved_draft || '')
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-4">
      <div className="flex items-center gap-3">
        <Heart size={22} className="text-blue-400" />
        <div>
          <h1 className="text-sm font-semibold text-white">Sentiment Analysis</h1>
          <p className="text-xs text-gray-400">Ticket sentiment scoring, survey analysis, and response coaching</p>
        </div>
      </div>

      <TicketPicker />

      <div className="flex flex-wrap gap-1 bg-gray-900 rounded-lg p-1 w-fit">
        {TABS.map(t => (
          <button key={t} onClick={() => { setTab(t); setResult(null); setError('') }}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${tab === t ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'Ticket Sentiment' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Ticket ID</label><input className={inputCls} value={tId} onChange={e => setTId(e.target.value)} placeholder="INC0012345" /></div>
          <div><label className={labelCls}>Description</label><textarea className={inputCls} rows={4} value={tDesc} onChange={e => setTDesc(e.target.value)} placeholder="Ticket description..." /></div>
          <div>
            <div className="flex items-center justify-between mb-2"><label className={labelCls}>Thread Updates</label><button onClick={addUpdate} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
            {updates.map((u, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <input className={`${inputCls} flex-1`} value={u} onChange={e => updateUpd(i, e.target.value)} placeholder={`Update ${i+1}`} />
                <button onClick={() => removeUpdate(i)} className="text-red-400 hover:text-red-300"><Trash2 size={14} /></button>
              </div>
            ))}
          </div>
          <button onClick={() => call('/sentiment/score-ticket', { ticket_id: tId, description: tDesc, updates: updates.filter(Boolean) })}
            disabled={loading || !tDesc} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Analysing...' : 'Analyse Sentiment'}
          </button>
          {result && (
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">Sentiment</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${SENT_STYLES[result.sentiment] || SENT_STYLES.neutral}`}>{result.sentiment}</span>
                </div>
                <div className="flex items-center justify-between"><span className="text-xs text-gray-400">Urgency Signal</span><span className={result.urgency_signal ? 'text-red-400 text-xs' : 'text-gray-500 text-xs'}>{result.urgency_signal ? 'âš  Yes' : 'No'}</span></div>
                <div className="flex items-center justify-between"><span className="text-xs text-gray-400">VIP Indicator</span><span className={result.vip_indicator ? 'text-yellow-400 text-xs' : 'text-gray-500 text-xs'}>{result.vip_indicator ? 'â˜… Yes' : 'No'}</span></div>
                <div className="flex items-center justify-between"><span className="text-xs text-gray-400">Priority Recommendation</span><span className="text-sm font-bold text-white">{result.priority_recommendation}</span></div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 space-y-3">
                <div>
                  <span className="text-xs text-gray-400">Escalation Risk</span>
                  <div className="mt-1 flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden"><div className={`h-full rounded-full ${result.escalation_risk > 0.7 ? 'bg-red-500' : result.escalation_risk > 0.4 ? 'bg-yellow-500' : 'bg-green-500'}`} style={{ width: `${(result.escalation_risk || 0) * 100}%` }} /></div>
                    <span className="text-xs text-gray-400">{Math.round((result.escalation_risk || 0) * 100)}%</span>
                  </div>
                </div>
                {result.emotion_tags?.length > 0 && <div><p className="text-xs text-gray-400 mb-1">Emotion Tags</p><div className="flex flex-wrap gap-1">{result.emotion_tags.map(t => <span key={t} className="px-2 py-0.5 bg-red-500/20 text-red-300 text-xs rounded-full">{t}</span>)}</div></div>}
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'Survey Analysis' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="flex items-center justify-between"><label className={labelCls}>Survey Responses</label><button onClick={addSurvey} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
          {surveys.map((s, i) => (
            <div key={i} className="flex gap-3 items-start">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">Rating</span>
                <select value={s.rating} onChange={e => updateSurvey(i, 'rating', Number(e.target.value))} className="bg-gray-800 border border-white/10 rounded px-2 py-1 text-sm text-white">
                  {[1,2,3,4,5].map(r => <option key={r}>{r}</option>)}
                </select>
              </div>
              <input className={`${inputCls} flex-1`} value={s.free_text} onChange={e => updateSurvey(i, 'free_text', e.target.value)} placeholder="Customer feedback..." />
              <button onClick={() => removeSurvey(i)} className="text-red-400 hover:text-red-300 mt-2"><Trash2 size={14} /></button>
            </div>
          ))}
          <button onClick={() => call('/sentiment/analyze-survey', { responses: surveys })}
            disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Analysing...' : 'Analyse Survey'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center gap-6">
                <div><p className="text-xs text-gray-400">CSAT Score</p><p className={`text-4xl font-bold ${result.csat_score >= 4 ? 'text-green-400' : result.csat_score >= 3 ? 'text-yellow-400' : 'text-red-400'}`}>{result.csat_score?.toFixed(1)}<span className="text-lg text-gray-500">/5</span></p></div>
                <div><p className="text-xs text-gray-400">Overall Sentiment</p><span className={`px-3 py-1 rounded-full text-sm font-medium border ${SENT_STYLES[result.overall_sentiment] || SENT_STYLES.neutral}`}>{result.overall_sentiment}</span></div>
              </div>
              {result.themes?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs text-gray-400 font-medium">Themes</p>
                  {result.themes.map((t, i) => (
                    <div key={i} className="bg-gray-800 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-white">{t.theme}</span>
                        <span className="text-xs text-gray-400">{t.frequency} mentions</span>
                      </div>
                      {t.sample_quotes?.slice(0, 2).map((q, j) => <p key={j} className="text-xs text-gray-400 italic">"{q}"</p>)}
                    </div>
                  ))}
                </div>
              )}
              {result.top_issues?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Top Issues</p><ul className="space-y-1">{result.top_issues.map((t, i) => <li key={i} className="text-sm text-red-300 flex gap-2"><span></span>{t}</li>)}</ul></div>}
              {result.recommendations?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Recommendations</p><ul className="space-y-1">{result.recommendations.map((r, i) => <li key={i} className="text-sm text-blue-300 flex gap-2"><span>â†’</span>{r}</li>)}</ul></div>}
            </div>
          )}
        </div>
      )}

      {tab === 'Response Coach' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Ticket ID</label><input className={inputCls} value={cId} onChange={e => setCId(e.target.value)} placeholder="INC0012345" /></div>
          <div><label className={labelCls}>Customer Message</label><textarea className={inputCls} rows={3} value={cCustomer} onChange={e => setCCustomer(e.target.value)} placeholder="What the customer wrote..." /></div>
          <div><label className={labelCls}>Agent Draft Response</label><textarea className={inputCls} rows={4} value={cDraft} onChange={e => setCDraft(e.target.value)} placeholder="Agent's draft reply..." /></div>
          <button onClick={() => call('/sentiment/coach-response', { ticket_id: cId, agent_draft: cDraft, customer_message: cCustomer })}
            disabled={loading || !cDraft} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Coaching...' : 'Review Response'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="bg-gray-800 rounded-lg p-4 space-y-3">
                <ScoreGauge label="Tone" value={result.tone_score} />
                <ScoreGauge label="Empathy" value={result.empathy_score} />
                <ScoreGauge label="Professionalism" value={result.professionalism_score} />
              </div>
              {result.issues?.length > 0 && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3"><p className="text-xs text-red-400 mb-2">Issues</p><ul className="space-y-1">{result.issues.map((t, i) => <li key={i} className="text-sm text-red-300"> {t}</li>)}</ul></div>}
              {result.suggestions?.length > 0 && <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3"><p className="text-xs text-blue-400 mb-2">Suggestions</p><ul className="space-y-1">{result.suggestions.map((s, i) => <li key={i} className="text-sm text-blue-300">â†’ {s}</li>)}</ul></div>}
              {result.improved_draft && (
                <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs text-green-400 font-medium">Improved Draft</p>
                    <button onClick={copyDraft} className="flex items-center gap-1 text-xs text-gray-400 hover:text-white">
                      {copied ? <><Check size={12} className="text-green-400" />Copied</> : <><Copy size={12} />Copy</>}
                    </button>
                  </div>
                  <p className="text-sm text-gray-200 leading-relaxed">{result.improved_draft}</p>
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
