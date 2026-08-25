// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/pages (AnalysisPage.jsx)
// Date: 2026-04-28
// ---------------------------------------------------------------------------
import {
  ArrowLeft,
  ChevronRight,
  FileText,
  FolderOpen,
  LayoutTemplate,
  Paperclip,
  WandSparkles,
} from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { getLlmStatus, startAnalysis, startPromptAnalysis } from '../api/client.js'
import Layout from '../components/Layout.jsx'
import { modelDisplayName } from '../modelDisplay.js'

// The backend derives the actual target stack (frontend framework, backend
// language/runtime, ORM, auth provider, deployment target) directly from the
// prompt text — see _detect_stack_signals in services/modernizer.py. This is
// just the internal seed value passed to the API; it has no UI representation
// and gets overridden the moment the prompt names a real technology.
const DEFAULT_TARGET_STACK = 'aveva_mes'

// Function: AnalysisPage
export default function AnalysisPage() {
  const navigate        = useNavigate()
  const [searchParams]  = useSearchParams()

  const folderQ = searchParams.get('folder') || ''
  const promptQ = searchParams.get('prompt') || ''
  const outputQ = searchParams.get('output') === 'single_file' ? 'single_file' : 'project'

  const [attachedFiles, setAttachedFiles]   = useState([])
  const [customStackDesc, setCustomStackDesc] = useState('')
  const [outputMode, setOutputMode]         = useState(outputQ)
  const [loading, setLoading]               = useState(false)
  const [llmStatus, setLlmStatus]           = useState(null)
  const fileInputRef = useRef(null)

  const FILE_ICON_MAP = { pdf: '📄', txt: '📝', md: '📝', doc: '📋', docx: '📋', csv: '📊', json: '📊', yaml: '⚙️', yml: '⚙️', xml: '📰', sql: '🗃️', py: '🐍', js: '🟨', ts: '🔷', cs: '💎', java: '☕', sh: '🖥️', bat: '🖥️', ps1: '🖥️' }
  // Function: getFileIcon
  const getFileIcon = (name) => FILE_ICON_MAP[(name || '').split('.').pop().toLowerCase()] || '📎'
  const ACCEPTED_EXTS = new Set(['pdf', 'txt', 'md', 'doc', 'docx', 'csv', 'json', 'yaml', 'yml', 'xml', 'sql', 'py', 'js', 'ts', 'cs', 'java', 'sh', 'bat', 'ps1', 'jsx', 'tsx'])

  const addFiles = useCallback((fileList) => {
    const accepted = Array.from(fileList || []).filter((file) => {
      if (!file) return false
      if (file.type?.startsWith('image/')) return true
      return ACCEPTED_EXTS.has((file.name || '').split('.').pop().toLowerCase())
    })
    if (!accepted.length) return
    setAttachedFiles((prev) => [
      ...prev,
      ...accepted.map((file) => {
        const isImage = file.type?.startsWith('image/')
        return { id: Math.random().toString(36).slice(2), file, url: isImage ? URL.createObjectURL(file) : null, name: file.name, isImage }
      }),
    ].slice(0, 10))
  }, [ACCEPTED_EXTS])

  const removeFile = useCallback((id) => {
    setAttachedFiles((prev) => {
      const item = prev.find((e) => e.id === id)
      if (item?.url) URL.revokeObjectURL(item.url)
      return prev.filter((e) => e.id !== id)
    })
  }, [])

  useEffect(() => {
    getLlmStatus()
      .then(setLlmStatus)
      .catch(() => setLlmStatus({ available: false, recommended: 'deepseek-coder:6.7b' }))
  }, [])

  useEffect(() => () => {
    attachedFiles.forEach((item) => { if (item.url) URL.revokeObjectURL(item.url) })
  }, [attachedFiles])

  const docCount            = attachedFiles.filter((f) => !f.isImage).length
  const imgCount            = attachedFiles.filter((f) => f.isImage).length
  const canSubmit           = !loading && (!!folderQ.trim() || !!promptQ.trim())

  // Function: handleSubmit
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!folderQ.trim() && !promptQ.trim()) {
      toast.error('No source provided — go back to the home page to enter a folder path or prompt.')
      return
    }
    setLoading(true)
    try {
      if (folderQ.trim()) {
        const combinedDesc = [promptQ, customStackDesc].filter(Boolean).join('\n\n')
        const { job_id } = await startAnalysis(folderQ.trim(), DEFAULT_TARGET_STACK, combinedDesc, attachedFiles, outputMode)
        toast.success('Analysis started!')
        navigate(`/jobs/${job_id}`)
      } else {
        const { job_id } = await startPromptAnalysis(promptQ.trim(), attachedFiles, DEFAULT_TARGET_STACK, customStackDesc, outputMode)
        toast.success('Code generation started!')
        navigate(`/jobs/${job_id}`)
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || err.message || 'Failed to start')
    } finally { setLoading(false) }
  }

  // Function: FileChip
  const FileChip = ({ item }) => (
    <div className="group relative shrink-0">
      {item.isImage ? (
        <img src={item.url} alt={item.name} className="h-14 w-14 rounded-xl border border-hairline object-cover" />
      ) : (
        <div className="flex h-14 w-14 flex-col items-center justify-center gap-0.5 rounded-xl border border-hairline bg-white/[0.03]">
          <span className="text-xl leading-none">{getFileIcon(item.name)}</span>
          <span className="w-full truncate px-0.5 text-center text-[8px] font-bold uppercase tracking-wide text-ink-faint">{item.name.split('.').pop()}</span>
        </div>
      )}
      <button
        type="button"
        onClick={() => removeFile(item.id)}
        className="absolute -right-1.5 -top-1.5 z-10 flex h-5 w-5 items-center justify-center rounded-full border border-hairline bg-surface text-xs font-bold text-ink-faint opacity-0 transition group-hover:opacity-100 hover:border-red-400/50 hover:text-red-400"
      >
        ×
      </button>
      <p className="mt-0.5 w-14 truncate text-center text-[9px] text-ink-faint">{item.name.split('/').pop()}</p>
    </div>
  )

  return (
    <Layout>
      {/* LLM status banner */}
      {llmStatus && (
        <div className={`flex items-center justify-between border-b px-6 py-2.5 text-xs ${
          llmStatus.available
            ? 'border-emerald-500/20 bg-emerald-500/[0.05]'
            : 'border-amber-500/20 bg-amber-500/[0.05]'
        }`}>
          <div className="flex items-center gap-2.5">
            <span className={`h-2 w-2 rounded-full ${llmStatus.available ? 'animate-pulse bg-emerald-400' : 'bg-amber-400'}`} />
            {llmStatus.available ? (
              <span className="text-emerald-300">
                LLM ready — <strong className="font-semibold text-ink">{modelDisplayName(llmStatus.active_model)}</strong> · GPU-powered generation
              </span>
            ) : (
              <span className="text-amber-300">
                LLM offline — templates only.{' '}
                <code className="rounded-md border border-amber-500/25 bg-amber-500/10 px-1.5 py-0.5 font-mono text-[11px]">
                  Install the configured OpenSource LLM in Ollama
                </code>{' '}
                to enable AI generation
              </span>
            )}
          </div>
          <span className="hidden text-ink-faint lg:block">Code generation uses OpenSource LLM with GPU acceleration</span>
        </div>
      )}

      <main className="mx-auto max-w-2xl px-6 py-8 lg:py-10">
        {/* Page header */}
        <div className="mb-6">
          <Link to="/" className="mb-4 inline-flex items-center gap-1.5 text-xs font-medium text-ink-faint transition hover:text-ink">
            <ArrowLeft className="h-3.5 w-3.5" />
            Home
          </Link>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gold/15">
              <WandSparkles className="h-5 w-5 text-gold-soft" />
            </div>
            <div>
              <h1 className="font-display text-2xl font-medium text-ink">Review &amp; generate</h1>
              <p className="text-sm text-ink-muted">The target stack is inferred from your prompt — add any extra constraints and pick an output format below.</p>
            </div>
          </div>
        </div>

        {/* Source summary */}
        {(folderQ || promptQ) ? (
          <div className="mb-5 overflow-hidden rounded-xl border border-hairline bg-surface shadow-sm">
            {folderQ && (
              <div className="flex items-start gap-3 px-4 py-3">
                <span className="shrink-0 text-base leading-tight">📁</span>
                <div className="min-w-0 flex-1">
                  <p className="text-[11px] font-semibold uppercase tracking-widest text-ink-faint">Project folder</p>
                  <p className="mt-0.5 truncate font-mono text-sm text-ink" title={folderQ}>{folderQ}</p>
                </div>
              </div>
            )}
            {folderQ && promptQ && <div className="border-t border-hairline" />}
            {promptQ && (
              <div className="flex items-start gap-3 px-4 py-3">
                <span className="shrink-0 text-base leading-tight">✨</span>
                <div className="min-w-0 flex-1">
                  <p className="text-[11px] font-semibold uppercase tracking-widest text-ink-faint">Prompt</p>
                  <p className="mt-0.5 line-clamp-2 text-sm text-ink">{promptQ}</p>
                </div>
              </div>
            )}
            <div className="flex justify-end border-t border-hairline px-4 py-2">
              <Link to="/" className="text-xs font-medium text-ink-faint transition hover:text-ink">← Edit source</Link>
            </div>
          </div>
        ) : (
          <div className="mb-5 rounded-xl border border-amber-500/25 bg-amber-500/[0.06] px-4 py-3.5">
            <p className="text-sm text-amber-300">
              No source set.{' '}
              <Link to="/" className="font-medium underline hover:text-amber-200">
                Go back to enter a folder path or prompt.
              </Link>
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">

          {/* File attachments */}
          <div className="overflow-hidden rounded-2xl border border-hairline bg-surface shadow-sm">
            <div className="border-b border-hairline px-5 py-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-ink">
                <Paperclip className="h-4 w-4 text-ink-faint" />
                Reference files
                <span className="ml-1 text-xs font-normal text-ink-faint">(optional)</span>
              </div>
              <p className="mt-0.5 text-xs text-ink-muted">Attach specs, docs, or code snippets for additional context.</p>
            </div>
            <div className="px-5 py-4">
              <div
                onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('border-gold/50', 'bg-gold/[0.04]') }}
                onDragLeave={(e) => e.currentTarget.classList.remove('border-gold/50', 'bg-gold/[0.04]')}
                onDrop={(e) => { e.preventDefault(); e.currentTarget.classList.remove('border-gold/50', 'bg-gold/[0.04]'); addFiles(e.dataTransfer.files) }}
                onClick={() => fileInputRef.current?.click()}
                className="flex min-h-[6rem] cursor-pointer items-center justify-center rounded-xl border border-dashed border-hairline-strong bg-white/[0.02] px-4 py-4 text-center transition-colors hover:border-white/25 hover:bg-white/[0.04]"
              >
                {attachedFiles.length > 0 ? (
                  <div className="flex w-full flex-wrap items-start gap-3" onClick={(e) => e.stopPropagation()}>
                    {attachedFiles.map((item) => <FileChip key={item.id} item={item} />)}
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-ink-dim">Drop files here or click to browse</p>
                    <p className="mt-1 text-xs text-ink-faint">PDF, DOCX, TXT, MD, CSV, JSON, YAML, source files, images</p>
                  </div>
                )}
              </div>
              {attachedFiles.length > 0 && (
                <p className="mt-2 text-xs text-ink-faint">
                  {attachedFiles.length} file{attachedFiles.length !== 1 ? 's' : ''} attached
                  {docCount > 0 && ` · ${docCount} doc${docCount !== 1 ? 's' : ''}`}
                  {imgCount > 0 && ` · ${imgCount} image${imgCount !== 1 ? 's' : ''}`}
                  {' · '}
                  <button type="button" onClick={() => setAttachedFiles([])} className="text-red-400 hover:underline">clear all</button>
                </p>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,.pdf,.txt,.md,.doc,.docx,.csv,.json,.yaml,.yml,.xml,.sql,.py,.js,.ts,.cs,.java,.jsx,.tsx"
                multiple
                className="hidden"
                onChange={(e) => addFiles(e.target.files)}
                disabled={loading}
              />
            </div>
          </div>

          {/* Extra instructions & output */}
          <div className="overflow-hidden rounded-2xl border border-hairline bg-surface shadow-sm">
            <div className="border-b border-hairline px-5 py-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gold/15">
                  <LayoutTemplate className="h-4 w-4 text-gold-soft" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-ink">Extra instructions &amp; output</p>
                  <p className="mt-0.5 text-xs text-ink-muted">The target stack comes from your prompt — add any extra constraints and pick an output format.</p>
                </div>
              </div>
            </div>

            <div className="space-y-4 px-5 py-5">
              {/* Extra instructions */}
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase tracking-widest text-ink-faint">
                  Extra instructions{' '}
                  <span className="font-normal normal-case text-ink-faint">(optional)</span>
                </label>
                <textarea
                  value={customStackDesc}
                  onChange={(e) => setCustomStackDesc(e.target.value)}
                  placeholder="Optional notes: auth model, architecture constraints, coding style, testing expectations, deployment notes."
                  rows={5}
                  disabled={loading}
                  className="w-full resize-none rounded-xl border border-hairline bg-bg px-4 py-3 text-sm leading-7 text-ink placeholder-ink-faint outline-none transition focus:border-gold/50 focus:ring-2 focus:ring-gold/10"
                />
              </div>

              {/* Output format */}
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase tracking-widest text-ink-faint">Output format</label>
                <div className="flex gap-2">
                  {[
                    { id: 'project',     icon: FolderOpen, label: 'Full project' },
                    { id: 'single_file', icon: FileText,   label: 'Single file' },
                  ].map(({ id, icon: Icon, label }) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setOutputMode(id)}
                      className={`inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-xs font-medium transition ${
                        outputMode === id
                          ? 'border-gold/40 bg-gold/15 text-gold-soft'
                          : 'border-hairline bg-white/[0.02] text-ink-dim hover:bg-white/[0.05]'
                      }`}
                    >
                      <Icon className="h-3.5 w-3.5" />
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={!canSubmit}
            className="flex w-full items-center justify-center gap-2.5 rounded-2xl bg-gold px-5 py-4 text-sm font-semibold text-bg transition hover:bg-gold-soft disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading
              ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-bg border-t-transparent" />
              : <ChevronRight className="h-4 w-4" />
            }
            {loading ? 'Starting…' : 'Generate / Analyze'}
          </button>

        </form>
      </main>
    </Layout>
  )
}
