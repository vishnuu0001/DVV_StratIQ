// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (ChatPage.jsx)
// Date: 2026-03-22
// ---------------------------------------------------------------------------
import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import toast from 'react-hot-toast'
import {
  Send, RotateCcw, BookOpen, ThumbsUp, ThumbsDown,
  Paperclip, X, FileText, Ticket, CheckCircle, Loader2,
} from 'lucide-react'
import { clsx } from 'clsx'
import { queryAgentAsync, queryAgentWithFile, submitFeedback, snUpdateTicket } from '../services/api.js'
import SourceBadges from '../components/SourceBadges.jsx'
import ConfidenceBadge from '../components/ConfidenceBadge.jsx'
import { useChatContext } from '../contexts/ChatContext.jsx'

// Function: ChatPage
export default function ChatPage() {
  const {
    sessions, activeSessionId, selectedModel,
    createSession, updateSessionMessages,
  } = useChatContext()

  // ── Messages are always plain local state ──────────────────
  // We load from context when the user picks a different session,
  // and we explicitly persist back to context after each exchange.
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [ragSessionId, setRagSessionId] = useState(null)       // backend RAG session id
  const [attachment, setAttachment] = useState(null)
  const [ticketId, setTicketId] = useState('')
  const [updatingTicket, setUpdatingTicket] = useState(null)
  const [updatedTickets, setUpdatedTickets] = useState({})
  const fileInputRef = useRef(null)
  const bottomRef = useRef(null)
  // Use a ref for the current chat session ID so async handlers always see the latest value
  const chatIdRef = useRef(null)
  const prevActiveSessionRef = useRef(activeSessionId)

  // Load messages when the user selects a different session from sidebar
  useEffect(() => {
    if (activeSessionId !== prevActiveSessionRef.current) {
      prevActiveSessionRef.current = activeSessionId
      chatIdRef.current = activeSessionId
      setUpdatedTickets({})
      if (activeSessionId) {
        const session = sessions.find((s) => s.id === activeSessionId)
        setMessages(session?.messages || [])
      } else {
        setMessages([])
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSessionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Function: buildHistory
  const buildHistory = (currentMessages) =>
    (currentMessages || messages).map((m) => ({ role: m.role, content: m.content }))

  // ── Attachment helpers ──────────────────────────────────────
  // Function: handleAttachClick
  const handleAttachClick = () => fileInputRef.current?.click()

  // Function: handleFileChange
  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const isImage = file.type.startsWith('image/')
    const preview = isImage ? URL.createObjectURL(file) : null
    setAttachment({ file, preview, type: isImage ? 'image' : 'log' })
    e.target.value = ''
  }

  // Function: clearAttachment
  const clearAttachment = () => {
    if (attachment?.preview) URL.revokeObjectURL(attachment.preview)
    setAttachment(null)
  }

  // ── Send message (with optional attachment) ─────────────────
  // Function: handleSend
  const handleSend = async () => {
    const q = input.trim()
    if (!q || loading) return

    // Create a new context session on first message (no active session)
    let chatId = chatIdRef.current
    if (!chatId) {
      chatId = await createSession(q, selectedModel, 'general')
      chatIdRef.current = chatId
      prevActiveSessionRef.current = chatId  // prevent the useEffect from reloading
    }

    const userContent = attachment
      ? `${q}\n\n📎 Attachment: ${attachment.file.name}`
      : q

    const userMsg = {
      id: Date.now(),
      role: 'human',
      content: userContent,
      attachmentPreview: attachment?.preview,
      attachmentName: attachment?.file?.name,
    }

    // Build the exact list we'll send as history (before adding userMsg)
    const historySnapshot = buildHistory(messages)

    const withUser = [...messages, userMsg]
    setMessages(withUser)
    setInput('')
    setLoading(true)

    const currentAttachment = attachment
    clearAttachment()

    try {
      let data

      if (currentAttachment) {
        const fd = new FormData()
        fd.append('question', q)
        fd.append('llm_provider', selectedModel)
        fd.append('chat_history', JSON.stringify(historySnapshot))
        fd.append('attachment', currentAttachment.file)
        const res = await queryAgentWithFile(fd)
        data = res.data
      } else {
        const res = await queryAgentAsync({
          question: q,
          chat_history: historySnapshot,
          llm_provider: selectedModel,
        })
        data = res.data
      }

      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        confidence: data.confidence,
        context_used: data.context_used,
        session_id: data.session_id,
        question: q,
      }
      setRagSessionId(data.session_id)
      const finalMessages = [...withUser, assistantMsg]
      setMessages(finalMessages)
      // Persist the full conversation to context (sidebar history)
      await updateSessionMessages(chatId, finalMessages, q)
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Unknown error'
      toast.error(`Error: ${detail}`)
      // Also show error inline so it's not missed
      const errMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `**Could not get a response.**\n\nError: ${detail}\n\n*Please retry or check that Ollama is running.*`,
        sources: [],
        confidence: undefined,
        isError: true,
      }
      const withError = [...withUser, errMsg]
      setMessages(withError)
      if (chatIdRef.current) await updateSessionMessages(chatIdRef.current, withError, q)
    } finally {
      setLoading(false)
    }
  }

  // ── Feedback ────────────────────────────────────────────────
  // Function: handleFeedback
  const handleFeedback = async (msg, rating) => {
    try {
      await submitFeedback({
        session_id: msg.session_id || ragSessionId || 'unknown',
        question: msg.question,
        answer: msg.content,
        rating,
        sources: (msg.sources || []).map((s) => s.source),
      })
      toast.success('Feedback recorded — thank you!')
    } catch {
      toast.error('Could not save feedback.')
    }
  }

  // ── Update ServiceNow ticket with resolution ────────────────
  // Function: handleUpdateTicket
  const handleUpdateTicket = async (msg) => {
    const incNum = ticketId.trim()
    if (!incNum) return toast.error('Enter a ticket number first.')
    setUpdatingTicket(msg.id)
    try {
      await snUpdateTicket({
        ticket_number: incNum,
        resolution_notes: msg.content,
        state: 'resolved',
      })
      setUpdatedTickets((prev) => ({ ...prev, [msg.id]: incNum }))
      toast.success(`Ticket ${incNum} updated successfully.`)
    } catch (err) {
      const detail = err.response?.data?.detail || err.message
      toast.error(`Update failed: ${detail}`)
    } finally {
      setUpdatingTicket(null)
    }
  }

  // Function: clearChat
  const clearChat = () => {
    setMessages([])
    setRagSessionId(null)
    chatIdRef.current = null
    prevActiveSessionRef.current = null
    clearAttachment()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b bg-white">
        <div>
          <h1 className="font-semibold text-gray-900">Support Chat</h1>
          <p className="text-xs text-gray-500">
            RAG-grounded answers &middot; attach screenshots or error logs for context
          </p>
        </div>
        <button onClick={clearChat} className="btn-secondary text-xs gap-1">
          <RotateCcw size={14} /> Clear
        </button>
      </header>

      {/* Ticket-ID strip (shown once chat has assistant messages) */}
      {messages.some((m) => m.role === 'assistant') && (
        <div className="flex-shrink-0 flex items-center gap-2 px-6 py-2 bg-amber-50 border-b border-amber-100">
          <Ticket size={14} className="text-amber-600 shrink-0" />
          <span className="text-xs text-amber-700 font-medium">Update ticket with resolution:</span>
          <input
            className="input !py-1 !text-xs w-40"
            placeholder="INC0000000"
            value={ticketId}
            onChange={(e) => setTicketId(e.target.value)}
          />
          <span className="text-xs text-amber-600">then click &quot;Update Ticket&quot; on any answer</span>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 space-y-3">
            <BookOpen size={40} strokeWidth={1} />
            <p className="text-sm font-medium text-gray-600">How can I help you today?</p>
            <p className="text-xs max-w-xs text-gray-400">
              Ask anything about the knowledge base. Attach a screenshot or error log for OCR-assisted resolution.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={clsx('flex', msg.role === 'human' ? 'justify-end' : 'justify-start')}>
            <div
              className={clsx(
                'max-w-2xl rounded-2xl px-4 py-3 text-sm',
                msg.role === 'human'
                  ? 'bg-brand-600 text-white rounded-br-sm'
                  : msg.isError
                    ? 'bg-red-50 border border-red-200 shadow-sm rounded-bl-sm'
                    : 'bg-white border border-gray-200 shadow-sm rounded-bl-sm'
              )}
            >
              {msg.role === 'human' ? (
                <>
                  <div className="whitespace-pre-wrap break-words text-left leading-7">{msg.content}</div>
                  {msg.attachmentPreview && (
                    <img
                      src={msg.attachmentPreview}
                      alt="attachment"
                      className="mt-2 rounded-lg max-h-40 object-contain border border-white/30"
                    />
                  )}
                  {msg.attachmentName && !msg.attachmentPreview && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-white/80">
                      <FileText size={12} /> {msg.attachmentName}
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="answer-prose">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  </div>

                  {/* Confidence + Sources */}
                  <div className="mt-3 pt-2 border-t border-gray-100 flex flex-wrap items-center gap-2">
                    {msg.confidence !== undefined && (
                      <ConfidenceBadge value={msg.confidence} contextUsed={msg.context_used} />
                    )}
                    {msg.sources?.length > 0 && <SourceBadges sources={msg.sources} />}
                  </div>

                  {/* Feedback + Ticket Update */}
                  <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-400">
                    <span>Helpful?</span>
                    <button
                      onClick={() => handleFeedback(msg, 3)}
                      className="hover:text-green-600 transition-colors p-1 rounded"
                      title="Helpful"
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button
                      onClick={() => handleFeedback(msg, 1)}
                      className="hover:text-red-500 transition-colors p-1 rounded"
                      title="Not helpful"
                    >
                      <ThumbsDown size={14} />
                    </button>

                    {/* Update Ticket CTA */}
                    <span className="flex-1" />
                    {updatedTickets[msg.id] ? (
                      <span className="flex items-center gap-1 text-green-600 font-medium">
                        <CheckCircle size={13} /> Updated {updatedTickets[msg.id]}
                      </span>
                    ) : (
                      <button
                        onClick={() => handleUpdateTicket(msg)}
                        disabled={updatingTicket === msg.id}
                        className={clsx(
                          'flex items-center gap-1 px-2 py-1 rounded-md border text-xs font-medium transition-colors',
                          updatingTicket === msg.id
                            ? 'text-gray-400 border-gray-200 cursor-not-allowed'
                            : 'text-brand-700 border-brand-200 hover:bg-brand-50'
                        )}
                        title="Push this resolution to the ServiceNow ticket"
                      >
                        {updatingTicket === msg.id
                          ? <><Loader2 size={12} className="animate-spin" /> Updating…</>
                          : <><Ticket size={12} /> Update Ticket</>
                        }
                      </button>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 shadow-sm rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex gap-1 items-center">
                <span className="w-2 h-2 rounded-full bg-brand-400 animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 rounded-full bg-brand-400 animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 rounded-full bg-brand-400 animate-bounce" />
                <span className="ml-2 text-xs text-gray-400">Thinking&hellip; (may take 30-90s with Ollama)</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Attachment preview bar */}
      {attachment && (
        <div className="flex-shrink-0 px-6 py-2 border-t bg-gray-50 flex items-center gap-3">
          {attachment.preview
            ? <img src={attachment.preview} alt="preview" className="h-10 w-10 rounded object-cover border" />
            : <FileText size={20} className="text-gray-500" />
          }
          <span className="text-xs text-gray-600 flex-1 truncate">{attachment.file.name}</span>
          <button onClick={clearAttachment} className="text-gray-400 hover:text-red-500 transition-colors">
            <X size={16} />
          </button>
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0 px-6 py-4 border-t bg-white">
        <div className="flex gap-2 items-end">
          {/* Attach button */}
          <button
            onClick={handleAttachClick}
            title="Attach screenshot or error log"
            className={clsx(
              'self-end p-2 rounded-lg border transition-colors',
              attachment
                ? 'border-brand-400 text-brand-600 bg-brand-50'
                : 'border-gray-300 text-gray-500 hover:text-brand-600 hover:border-brand-300'
            )}
          >
            <Paperclip size={16} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".png,.jpg,.jpeg,.txt,.log,.csv"
            className="hidden"
            onChange={handleFileChange}
          />

          <textarea
            className="input resize-none flex-1"
            rows={2}
            placeholder="Describe the issue, paste an error, or attach a screenshot…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="btn-primary self-end"
          >
            <Send size={16} />
            Send
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-1">
          Enter to send &middot; Shift+Enter for new line &middot;{' '}
          <button onClick={handleAttachClick} className="underline hover:text-brand-600">
            attach screenshot or error log
          </button>
        </p>
      </div>
    </div>
  )
}
