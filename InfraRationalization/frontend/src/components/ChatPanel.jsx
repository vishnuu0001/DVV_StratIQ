// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/components (ChatPanel.jsx)
// Date: 2025-09-17
// ---------------------------------------------------------------------------
import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import { sendChatMessage } from '../api/client.js'

const SUGGESTED_PROMPTS = [
  'Summarize the biggest migration risks in this scan',
  'Which servers are the best right-sizing candidates?',
  'What EOS (end-of-support) exposure does this report show?',
]

// Function: ChatPanel
export default function ChatPanel({ scanId }) {
  const [messages, setMessages] = useState([])   // [{role, content}]
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  // Function: send
  const send = async (text) => {
    const message = (text ?? input).trim()
    if (!message || sending) return

    const history = messages
    setMessages(prev => [...prev, { role: 'user', content: message }])
    setInput('')
    setSending(true)
    setError(null)

    try {
      const result = await sendChatMessage(scanId, message, history)
      setMessages(prev => [...prev, { role: 'assistant', content: result.reply, unavailable: !result.available }])
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Failed to reach the AI assistant.')
      setMessages(prev => prev.slice(0, -1))   // don't leave an unanswered user message stuck in history
    } finally {
      setSending(false)
    }
  }

  // Function: onKeyDown
  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="flex flex-col h-[520px] rounded-xl border border-slate-700/50 bg-slate-950/40">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center gap-4 py-8">
            <div className="w-12 h-12 rounded-xl bg-brand-green/10 flex items-center justify-center">
              <Bot size={22} className="text-brand-green" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-200">Ask about this scan report</p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm">
                Answers are grounded in this specific report's data — servers, utilization,
                EOS advisories, and cloud-readiness classifications.
              </p>
            </div>
            <div className="flex flex-col gap-2 w-full max-w-md">
              {SUGGESTED_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p)}
                  className="text-left text-xs px-3 py-2 rounded-lg border border-slate-700/50 text-slate-400 hover:text-slate-200 hover:border-brand-green/40 transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-brand-green/10 flex items-center justify-center shrink-0 mt-0.5">
                <Bot size={14} className="text-brand-green" />
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                m.role === 'user'
                  ? 'bg-brand-green/15 text-slate-100 border border-brand-green/25'
                  : m.unavailable
                    ? 'bg-amber-950/30 text-amber-200 border border-amber-700/30'
                    : 'bg-slate-800/60 text-slate-200 border border-slate-700/40'
              }`}
            >
              {m.content}
            </div>
            {m.role === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-slate-700/50 flex items-center justify-center shrink-0 mt-0.5">
                <User size={14} className="text-slate-300" />
              </div>
            )}
          </div>
        ))}

        {sending && (
          <div className="flex gap-2.5 justify-start">
            <div className="w-7 h-7 rounded-lg bg-brand-green/10 flex items-center justify-center shrink-0">
              <Bot size={14} className="text-brand-green" />
            </div>
            <div className="rounded-xl px-3.5 py-2.5 bg-slate-800/60 border border-slate-700/40 flex items-center gap-2">
              <Loader2 size={13} className="animate-spin text-slate-400" />
              <span className="text-xs text-slate-500">Thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="px-4 py-2 text-xs text-red-300 bg-red-950/30 border-t border-red-700/30">
          {error}
        </div>
      )}

      <div className="p-3 border-t border-slate-700/40 flex items-end gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask a question about this scan…"
          rows={1}
          disabled={sending}
          className="flex-1 resize-none rounded-lg bg-slate-900/60 border border-slate-700/50 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-green/50 disabled:opacity-50"
        />
        <button
          onClick={() => send()}
          disabled={sending || !input.trim()}
          className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-green/15 border border-brand-green/30 text-brand-green hover:bg-brand-green/25 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shrink-0"
          title="Send"
        >
          <Send size={15} />
        </button>
      </div>
    </div>
  )
}
