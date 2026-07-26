// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (VirtualAgentPage.jsx)
// Date: 2025-09-14
// ---------------------------------------------------------------------------
import React, { useState, useRef, useEffect } from 'react'
import { Bot, Send, AlertTriangle, Globe, Languages, Clock } from 'lucide-react'
import api from '../services/api.js'

const LANGUAGES = ['en', 'es', 'fr', 'de', 'ja', 'ar', 'pt', 'zh']
const LANG_LABELS = { en: 'English', es: 'Spanish', fr: 'French', de: 'German', ja: 'Japanese', ar: 'Arabic', pt: 'Portuguese', zh: 'Chinese' }

// Function: genId
function genId() { return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 7)}` }

// Function: MessageContent
function MessageContent({ content }) {
  return <span style={{ whiteSpace: 'pre-line' }}>{content}</span>
}

// Function: VirtualAgentPage
export default function VirtualAgentPage() {
  const [tab, setTab] = useState('chat')
  const [sessionId] = useState(genId)
  const [messages, setMessages] = useState([
    { role: 'agent', content: 'Hello! I am your L0/L1 IT Support Virtual Agent. I can help you with password resets, VPN issues, software requests, and general IT queries. How can I assist you today?', intent: 'greeting', escalate: false }
  ])
  const [input, setInput] = useState('')
  const [language, setLanguage] = useState('en')
  const [chatLoading, setChatLoading] = useState(false)
  const [waitingLong, setWaitingLong] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const slowTimerRef = useRef(null)

  const [xlText, setXlText] = useState('')
  const [xlTarget, setXlTarget] = useState('es')
  const [xlResult, setXlResult] = useState(null)
  const [xlLoading, setXlLoading] = useState(false)
  const [xlError, setXlError] = useState('')

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  // Function: sendMessage
  const sendMessage = async () => {
    if (!input.trim() || chatLoading) return
    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    const history = messages.map(m => ({ role: m.role === 'agent' ? 'assistant' : 'user', content: m.content }))
    setInput('')
    setChatLoading(true)
    setWaitingLong(false)
    setError('')
    slowTimerRef.current = setTimeout(() => setWaitingLong(true), 8000)
    try {
      const { data } = await api.post('/virtual-agent/chat', { message: userMsg.content, session_id: sessionId, history, language }, { timeout: 0 })
      setMessages(prev => [...prev, { role: 'agent', content: data.response, intent: data.intent, escalate: data.escalate, confidence: data.confidence }])
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Request failed')
    } finally {
      clearTimeout(slowTimerRef.current)
      setChatLoading(false)
      setWaitingLong(false)
    }
  }

  // Function: translate
  const translate = async () => {
    if (!xlText.trim()) return
    setXlLoading(true); setXlError(''); setXlResult(null)
    try {
      const { data } = await api.post('/virtual-agent/translate', { text: xlText, target_language: LANG_LABELS[xlTarget] }, { timeout: 0 })
      setXlResult(data)
    } catch (e) {
      setXlError(e.response?.data?.detail || e.message || 'Translation failed')
    } finally { setXlLoading(false) }
  }

  const fieldCls = 'w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 px-5 py-4 space-y-3">

      {/* Page header */}
      <div className="flex items-center gap-2 border-b border-white/8 pb-3">
        <Bot size={14} className="text-blue-400 shrink-0" />
        <div>
          <h1 className="text-xs font-black uppercase tracking-widest text-gray-400 leading-none">Virtual Agent</h1>
          <p className="text-[10px] text-gray-600 mt-0.5">L0/L1 AI Service Desk — multilingual support</p>
        </div>
      </div>

      {/* Tabs + language */}
      <div className="flex gap-1 bg-gray-900 rounded-lg p-1 w-fit">
        {['chat', 'translate'].map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-3 py-1 rounded-md text-xs font-semibold capitalize transition-colors ${tab === t ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}>
            {t === 'chat' ? 'Live Chat' : 'Translate'}
          </button>
        ))}
        <select value={language} onChange={e => setLanguage(e.target.value)}
          className="ml-2 bg-gray-800 border border-white/10 rounded-md px-2 py-1 text-[10px] text-gray-300">
          {LANGUAGES.map(l => <option key={l} value={l}>{LANG_LABELS[l]}</option>)}
        </select>
      </div>

      {/* ── Live Chat ── */}
      {tab === 'chat' && (
        <div className="flex flex-col h-[calc(100vh-210px)] min-h-72 bg-gray-900 rounded-xl border border-white/10 overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] space-y-1 ${m.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                  {m.role === 'agent' && (
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <Bot size={11} className="text-blue-400" />
                      <span className="text-[10px] text-gray-500">Virtual Agent</span>
                      {m.intent && m.intent !== 'greeting' && (
                        <span className="px-1.5 py-0.5 bg-blue-500/20 text-blue-300 text-[9px] font-semibold rounded uppercase tracking-wide">
                          {m.intent}
                        </span>
                      )}
                    </div>
                  )}
                  <div className={`rounded-2xl px-3 py-2 text-xs leading-relaxed ${m.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-gray-800 text-gray-200 rounded-tl-sm'}`}>
                    <MessageContent content={m.content} />
                  </div>
                  {m.escalate && (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 bg-red-500/10 border border-red-500/30 rounded-lg text-[10px] text-red-300">
                      <AlertTriangle size={10} /><span>Escalation Recommended</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-3 py-2 flex items-center gap-2">
                  <div className="flex gap-1">
                    {[0,1,2].map(i => (
                      <span key={i} className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                    ))}
                  </div>
                  {waitingLong && (
                    <span className="flex items-center gap-1 text-[10px] text-gray-400 ml-1">
                      <Clock size={9} className="text-yellow-400 animate-pulse" />
                      Still thinking, please wait…
                    </span>
                  )}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          {error && (
            <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/30 text-red-300 text-[10px]">{error}</div>
          )}
          <div className="border-t border-white/10 p-2.5 flex gap-2">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              className="flex-1 bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              placeholder="Type your IT support request…"
            />
            <button
              onClick={sendMessage}
              disabled={chatLoading || !input.trim()}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg transition-colors"
            >
              <Send size={13} />
            </button>
          </div>
        </div>
      )}

      {/* ── Translate ── */}
      {tab === 'translate' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Languages size={13} className="text-blue-400" />
            <span className="text-xs font-semibold text-white">Multilingual Translation</span>
          </div>
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-1">Text to Translate</label>
            <textarea className={fieldCls} rows={5} value={xlText} onChange={e => setXlText(e.target.value)} placeholder="Enter text in any language…" />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-[10px] text-gray-400 shrink-0">Target Language</label>
            <select value={xlTarget} onChange={e => setXlTarget(e.target.value)}
              className="bg-gray-800 border border-white/10 rounded-lg px-2 py-1.5 text-xs text-white">
              {LANGUAGES.map(l => <option key={l} value={l}>{LANG_LABELS[l]}</option>)}
            </select>
            <button
              onClick={translate}
              disabled={xlLoading || !xlText.trim()}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-colors"
            >
              {xlLoading ? 'Translating…' : 'Translate'}
            </button>
          </div>
          {xlError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-300 text-xs">{xlError}</div>
          )}
          {xlResult && (
            <div className="bg-gray-800 rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2 text-[10px] text-gray-400">
                <Globe size={10} />
                <span>Detected: {xlResult.source_language_detected}</span>
                <span>→</span>
                <span>{xlResult.target_language}</span>
              </div>
              <p className="text-white text-xs leading-relaxed">{xlResult.translated}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
