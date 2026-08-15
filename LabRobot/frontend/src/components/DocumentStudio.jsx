// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (DocumentStudio.jsx)
// Date: 2026-08-14
// ---------------------------------------------------------------------------
// The "Copilot Studio" / "Claude Studio" simulation opened from a governed
// AI Lab catalog card (see AILabCatalog.jsx). Users upload a PDF/DOCX/XLSX
// and ask questions about it — answered entirely by documentParsing.js +
// heuristicQA.js (keyword/frequency heuristics over text extracted
// client-side). There is no LLM call anywhere in this component or its
// dependencies; every answer bubble is labeled "Heuristic" for the same
// reason AILabCatalog.jsx's file header documents that constraint.
import { useRef, useState } from 'react'
import { ACCEPTED_EXTENSIONS } from '../lib/documentTypes'
import { answerHeuristically } from '../lib/heuristicQA'

const THEMES = {
  copilot: {
    label: 'Copilot Studio',
    gradient: 'linear-gradient(135deg, #185ABD 0%, #0F6CBD 55%, #2B88D8 100%)',
    accent: '#0F6CBD',
    accentBg: '#EFF6FC',
    accentBorder: '#C7E0F4',
  },
  claude: {
    label: 'Claude Studio',
    gradient: 'linear-gradient(135deg, #B15B33 0%, #C15F3C 55%, #D97757 100%)',
    accent: '#B15B33',
    accentBg: '#FBEEE6',
    accentBorder: '#EAC7AE',
  },
}

// Function: formatBytes
function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// Function: DocumentStudio
// `library` ({ documents, activeId, conversations }) and `onLibraryChange`
// are owned by AILabCatalog, not this component, and keyed per tool — so
// closing the Studio and reopening it (or switching to another AI Lab tab
// and back) keeps everything uploaded so far, instead of the previous
// behavior where every upload/conversation was thrown away the moment the
// modal unmounted. This is in-memory, session-scoped persistence (survives
// for as long as the AI Lab tab itself stays mounted); it does not survive
// a full page reload — that would need a backend (SQLite) store, which
// wasn't built here to keep this feature client-only like the rest of the
// AI Lab tab's heuristic simulation.
export default function DocumentStudio({ tool, studioKind, library, onLibraryChange, onClose }) {
  const theme = THEMES[studioKind] || THEMES.copilot
  const { documents, activeId, conversations } = library
  const [question, setQuestion] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)

  // Function: setDocuments
  const setDocuments = (updater) => {
    onLibraryChange((prev) => ({
      ...prev,
      documents: typeof updater === 'function' ? updater(prev.documents) : updater,
    }))
  }

  // Function: setActiveId
  const setActiveId = (id) => {
    onLibraryChange((prev) => ({ ...prev, activeId: id }))
  }

  // Function: setConversations
  const setConversations = (updater) => {
    onLibraryChange((prev) => ({
      ...prev,
      conversations: typeof updater === 'function' ? updater(prev.conversations) : updater,
    }))
  }

  // Function: deleteDocument
  const deleteDocument = (id) => {
    onLibraryChange((prev) => {
      const remaining = prev.documents.filter((d) => d.id !== id)
      const conversationsCopy = { ...prev.conversations }
      delete conversationsCopy[id]
      return {
        documents: remaining,
        conversations: conversationsCopy,
        activeId: prev.activeId === id ? (remaining[0]?.id ?? null) : prev.activeId,
      }
    })
  }

  const activeDoc = documents.find((d) => d.id === activeId) || null
  const activeMessages = activeId ? conversations[activeId] || [] : []

  // Function: ingestFiles
  // pdfjs-dist + jszip (~1.3 MB combined) are only fetched here, the first
  // time a file is actually dropped/picked — not on every page load of the
  // app, and not even every time this tab or this modal opens.
  const ingestFiles = async (fileList) => {
    const files = Array.from(fileList)
    const tempIds = files.map((file) => `${file.name}-${file.lastModified}-${file.size}`)

    // Add every file as a visible "parsing" row up front. Previously the
    // parser module import happened before any of this, so if THAT one
    // import failed, nothing was ever added to the list at all — the drop
    // zone just looked like it silently ignored the file, with no error
    // anywhere in the UI (only an unhandled promise rejection in the
    // console). Now every drop always shows up, even if it ends in Error.
    setDocuments((docs) => {
      const next = [...docs]
      files.forEach((file, i) => {
        if (!next.some((d) => d.id === tempIds[i])) {
          next.push({ id: tempIds[i], fileName: file.name, sizeBytes: file.size, status: 'parsing' })
        }
      })
      return next
    })
    if (tempIds[0]) setActiveId(tempIds[0])

    let parseDocument
    try {
      ;({ parseDocument } = await import('../lib/documentParsing'))
    } catch (err) {
      const message = `The document parser failed to load: ${err.message || err}. Try reloading the page.`
      setDocuments((docs) => docs.map((d) => (tempIds.includes(d.id) ? { ...d, status: 'error', error: message } : d)))
      return
    }

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const tempId = tempIds[i]
      try {
        const parsed = await parseDocument(file)
        setDocuments((docs) => docs.map((d) => (d.id === tempId ? { ...parsed, status: 'ready' } : d)))
        setConversations((c) => ({
          ...c,
          [parsed.id]: [{
            role: 'system',
            text: `Loaded "${parsed.fileName}" — ${Object.entries(parsed.stats).map(([k, v]) => `${k}: ${v}`).join(' · ')}. ` +
              'Ask a question about the content, or click Summarize.',
          }],
        }))
      } catch (err) {
        setDocuments((docs) => docs.map((d) => (d.id === tempId ? { ...d, status: 'error', error: err.message } : d)))
      }
    }
  }

  // Function: onFileInputChange
  const onFileInputChange = (e) => {
    if (e.target.files?.length) ingestFiles(e.target.files)
    e.target.value = ''
  }

  // Function: onDrop
  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files?.length) ingestFiles(e.dataTransfer.files)
  }

  // Function: ask
  const ask = (text) => {
    const trimmed = text.trim()
    if (!trimmed || !activeDoc || activeDoc.status !== 'ready') return
    const result = answerHeuristically(trimmed, activeDoc)
    setConversations((c) => ({
      ...c,
      [activeDoc.id]: [...(c[activeDoc.id] || []), { role: 'user', text: trimmed }, { role: 'assistant', ...result }],
    }))
    setQuestion('')
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded shadow-2xl w-full max-w-4xl overflow-hidden flex flex-col" style={{ height: 'min(720px, 92vh)' }}>
        {/* Header */}
        <div className="px-6 py-4 flex items-start justify-between text-white shrink-0" style={{ background: theme.gradient }}>
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-white/75">Enterprise Zone · Governed Connector</p>
            <h2 className="text-lg font-semibold">{theme.label} — {tool.name}</h2>
            <p className="text-sm text-white/85 mt-0.5">Upload a PDF, DOCX, or XLSX and ask questions about it — answered heuristically, not by an LLM.</p>
          </div>
          <button type="button" onClick={onClose} className="text-white/75 hover:text-white mt-0.5 shrink-0">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 min-h-0 flex">
          {/* Left: document manager */}
          <div className="w-64 shrink-0 border-r flex flex-col" style={{ borderColor: '#EDEBE9' }}>
            <div className="p-3">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
                className="w-full rounded-lg border-2 border-dashed px-3 py-6 text-center transition-colors"
                style={{ borderColor: dragOver ? theme.accent : '#D2D0CE', background: dragOver ? theme.accentBg : '#FAF9F8' }}
              >
                <svg className="w-6 h-6 mx-auto mb-1.5" style={{ color: theme.accent }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M12 16V4m0 0L7 9m5-5l5 5M5 20h14" />
                </svg>
                <p className="text-xs font-semibold" style={{ color: '#201F1E' }}>Upload document</p>
                <p className="text-[11px] mt-0.5" style={{ color: '#8A8886' }}>PDF · DOCX · XLSX</p>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_EXTENSIONS.join(',')}
                multiple
                onChange={onFileInputChange}
                className="hidden"
              />
            </div>
            <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1.5">
              {documents.length === 0 && (
                <p className="text-xs px-1" style={{ color: '#8A8886' }}>No documents yet.</p>
              )}
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="relative rounded-lg border transition-colors"
                  style={{
                    borderColor: activeId === doc.id ? theme.accent : '#EDEBE9',
                    background: activeId === doc.id ? theme.accentBg : '#FFFFFF',
                  }}
                >
                  <button
                    type="button"
                    onClick={() => setActiveId(doc.id)}
                    className="w-full text-left px-2.5 py-2 pr-7"
                  >
                    <p className="text-xs font-semibold truncate" style={{ color: '#201F1E' }}>{doc.fileName}</p>
                    <div className="flex items-center justify-between mt-0.5">
                      <span className="text-[10px]" style={{ color: '#8A8886' }}>{formatBytes(doc.sizeBytes)}</span>
                      {doc.status === 'parsing' && (
                        <span className="text-[10px] font-semibold flex items-center gap-1" style={{ color: '#835C00' }}>
                          <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                          </svg>
                          Parsing
                        </span>
                      )}
                      {doc.status === 'ready' && (
                        <span className="text-[10px] font-semibold" style={{ color: '#0B6A0B' }}>Ready</span>
                      )}
                      {doc.status === 'error' && (
                        <span className="text-[10px] font-semibold" style={{ color: '#A4262C' }}>Error</span>
                      )}
                    </div>
                    {doc.status === 'error' && (
                      <p className="text-[10px] mt-1" style={{ color: '#A4262C' }}>{doc.error}</p>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); deleteDocument(doc.id) }}
                    title={`Remove ${doc.fileName}`}
                    className="absolute top-1.5 right-1.5 p-0.5 rounded transition-colors"
                    style={{ color: '#8A8886' }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = '#A4262C' }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = '#8A8886' }}
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Right: chat */}
          <div className="flex-1 min-w-0 flex flex-col">
            {!activeDoc ? (
              <div className="flex-1 flex items-center justify-center px-6 text-center">
                <p className="text-sm" style={{ color: '#8A8886' }}>Upload a document on the left to start asking questions.</p>
              </div>
            ) : (
              <>
                <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
                  {activeMessages.map((m, idx) => (
                    <ChatBubble key={idx} message={m} theme={theme} />
                  ))}
                  {activeDoc.status === 'parsing' && (
                    <p className="text-xs" style={{ color: '#8A8886' }}>Extracting text from "{activeDoc.fileName}"…</p>
                  )}
                </div>
                <div className="border-t p-3" style={{ borderColor: '#EDEBE9' }}>
                  <div className="flex gap-2 mb-2">
                    <button
                      type="button"
                      onClick={() => ask('Summarize this document')}
                      disabled={activeDoc.status !== 'ready'}
                      className="text-xs font-semibold px-2.5 py-1 rounded-full border transition-colors disabled:opacity-40"
                      style={{ borderColor: theme.accentBorder, color: theme.accent, background: theme.accentBg }}
                    >
                      Summarize
                    </button>
                    <button
                      type="button"
                      onClick={() => ask('How many pages does this have?')}
                      disabled={activeDoc.status !== 'ready'}
                      className="text-xs font-semibold px-2.5 py-1 rounded-full border transition-colors disabled:opacity-40"
                      style={{ borderColor: theme.accentBorder, color: theme.accent, background: theme.accentBg }}
                    >
                      Document stats
                    </button>
                  </div>
                  <form
                    onSubmit={(e) => { e.preventDefault(); ask(question) }}
                    className="flex gap-2"
                  >
                    <input
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      disabled={activeDoc.status !== 'ready'}
                      placeholder={activeDoc.status === 'ready' ? `Ask about ${activeDoc.fileName}…` : 'Waiting for the document to finish parsing…'}
                      className="flex-1 border rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 disabled:opacity-50"
                      style={{ borderColor: '#8A8886', color: '#201F1E' }}
                    />
                    <button
                      type="submit"
                      disabled={activeDoc.status !== 'ready' || !question.trim()}
                      className="px-4 py-2 rounded-full text-sm font-semibold text-white transition-colors disabled:opacity-40"
                      style={{ background: theme.accent }}
                    >
                      Ask
                    </button>
                  </form>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Function: ChatBubble
function ChatBubble({ message, theme }) {
  if (message.role === 'system') {
    return (
      <div className="rounded-lg border px-3 py-2 text-xs" style={{ background: '#FAF9F8', borderColor: '#EDEBE9', color: '#605E5C' }}>
        {message.text}
      </div>
    )
  }
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="rounded-2xl rounded-tr-sm px-4 py-2 text-sm text-white max-w-[80%]" style={{ background: theme.accent }}>
          {message.text}
        </div>
      </div>
    )
  }
  // assistant
  return (
    <div className="flex justify-start">
      <div className="rounded-2xl rounded-tl-sm border px-4 py-3 text-sm max-w-[85%]" style={{ background: '#FFFFFF', borderColor: '#EDEBE9' }}>
        <div className="flex items-center gap-1.5 mb-1.5">
          <span className="text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded" style={{ background: theme.accentBg, color: theme.accent }}>
            Heuristic
          </span>
          {message.kind === 'none' && (
            <span className="text-[10px] font-semibold" style={{ color: '#835C00' }}>No match</span>
          )}
        </div>
        <p style={{ color: '#201F1E' }}>{message.text}</p>
        {message.citations && message.citations.length > 0 && (
          <div className="mt-2 space-y-1.5">
            {message.citations.map((c, i) => (
              <div key={i} className="rounded border px-2.5 py-1.5" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
                <p className="text-[10px] font-bold" style={{ color: theme.accent }}>{c.ref}</p>
                <p className="text-xs mt-0.5" style={{ color: '#3B3A39' }}>{c.snippet}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
