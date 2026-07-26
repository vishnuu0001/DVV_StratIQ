// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/pages (HomePage.jsx)
// Date: 2025-12-29
// ---------------------------------------------------------------------------
import { ArrowRight, FileText, FolderOpen, FolderSearch2, Layers3, Upload, X } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { Link, useNavigate } from 'react-router-dom'
import { detectFolder, filterUploadFiles, uploadFolder } from '../api/client.js'
import FolderBrowserModal from '../components/FolderBrowserModal.jsx'
import Layout from '../components/Layout.jsx'

// Function: HomePage
export default function HomePage() {
  const navigate = useNavigate()
  const [folderPath, setFolderPath]   = useState('')
  const [uploadedLabel, setUploadedLabel] = useState('')   // set when folderPath came from an upload, not typing/browsing
  const [uploading, setUploading]     = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [promptText, setPromptText]   = useState('')
  const [showBrowser, setShowBrowser] = useState(false)
  const [detected, setDetected]       = useState(null)
  const [detecting, setDetecting]     = useState(false)
  const [outputMode, setOutputMode]   = useState('project')
  const uploadInputRef = useRef(null)

  useEffect(() => {
    if (!folderPath.trim()) { setDetected(null); return }
    const timer = setTimeout(async () => {
      setDetecting(true)
      try { setDetected(await detectFolder(folderPath.trim())) }
      catch { setDetected(null) }
      finally { setDetecting(false) }
    }, 600)
    return () => clearTimeout(timer)
  }, [folderPath])

  const handleBrowseSelect = useCallback((path) => {
    setFolderPath(path)
    setUploadedLabel('')
    setShowBrowser(false)
  }, [])

  // Function: handleUploadClick
  const handleUploadClick = () => uploadInputRef.current?.click()

  // Function: handleFilesChosen
  const handleFilesChosen = async (e) => {
    const rawFiles = Array.from(e.target.files || [])
    e.target.value = ''   // allow re-selecting the same folder later
    if (rawFiles.length === 0) return

    const files = filterUploadFiles(rawFiles)
    if (files.length === 0) {
      toast.error('That folder only contains excluded files (node_modules, .git, build output, …)')
      return
    }

    const topFolder = (rawFiles[0].webkitRelativePath || '').split('/')[0] || 'folder'
    setUploading(true)
    setUploadProgress(0)
    try {
      const { path, file_count } = await uploadFolder(files, setUploadProgress)
      setFolderPath(path)
      setUploadedLabel(`${topFolder} · ${file_count} files uploaded`)
      toast.success(`Uploaded ${file_count} files`)
    } catch (err) {
      toast.error(err?.response?.data?.detail || err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  // Function: clearFolder
  const clearFolder = () => {
    setFolderPath('')
    setUploadedLabel('')
  }

  // Function: handleSubmit
  const handleSubmit = (e) => {
    e.preventDefault()
    const folder = folderPath.trim()
    const prompt = promptText.trim()
    if (!folder && !prompt) return
    const params = new URLSearchParams()
    if (folder) params.set('folder', folder)
    if (prompt) params.set('prompt', prompt)
    params.set('output', outputMode)
    navigate(`/analyze?${params.toString()}`)
  }

  const canSubmit = !!folderPath.trim() || !!promptText.trim()

  return (
    <Layout>
      <div className="flex h-full min-h-full flex-col items-center justify-center px-6 py-10">

        {/* Heading */}
        <h1 className="mb-8 text-center font-display text-4xl font-medium tracking-tight text-ink sm:text-5xl">
          Where should we begin?
        </h1>

        {/* Unified input card */}
        <form onSubmit={handleSubmit} className="w-full max-w-2xl">
          <div className="overflow-hidden rounded-2xl border border-hairline bg-surface shadow-[0_20px_60px_-20px_rgba(0,0,0,0.6)] transition focus-within:border-hairline-strong">

            {/* Folder row */}
            <div className="flex items-center gap-3 px-4 py-3.5">
              <FolderSearch2 className="h-5 w-5 shrink-0 text-ink-faint" />
              <input
                type="text"
                value={uploadedLabel || folderPath}
                onChange={(e) => { setUploadedLabel(''); setFolderPath(e.target.value) }}
                placeholder="Paste a project folder path, or upload one from your computer"
                readOnly={!!uploadedLabel}
                disabled={uploading}
                className="flex-1 bg-transparent text-sm text-ink placeholder-ink-faint outline-none disabled:opacity-60"
              />
              {(folderPath || uploadedLabel) && !uploading && (
                <button
                  type="button"
                  onClick={clearFolder}
                  title="Clear"
                  className="shrink-0 rounded-full p-1 text-ink-faint transition hover:bg-white/10 hover:text-ink"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              )}
              <input
                ref={uploadInputRef}
                type="file"
                webkitdirectory=""
                directory=""
                multiple
                onChange={handleFilesChosen}
                className="hidden"
              />
              <button
                type="button"
                onClick={handleUploadClick}
                disabled={uploading}
                className="inline-flex shrink-0 items-center gap-1.5 rounded-xl bg-gold px-3 py-1.5 text-xs font-semibold text-bg transition hover:bg-gold-soft disabled:opacity-50"
              >
                <Upload className="h-3.5 w-3.5" />
                {uploading ? `Uploading… ${Math.round(uploadProgress * 100)}%` : 'Upload'}
              </button>
              <button
                type="button"
                onClick={() => setShowBrowser(true)}
                disabled={uploading}
                className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-hairline bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-ink-dim transition hover:bg-white/[0.07] hover:text-ink disabled:opacity-50"
              >
                <FolderOpen className="h-3.5 w-3.5" />
                Browse server
              </button>
            </div>

            {/* Upload progress */}
            {uploading && (
              <div className="h-0.5 w-full bg-white/5">
                <div
                  className="h-full bg-gold transition-all"
                  style={{ width: `${Math.max(4, Math.round(uploadProgress * 100))}%` }}
                />
              </div>
            )}

            {/* Detection strip */}
            {(detecting || detected) && (
              <div className="flex flex-wrap items-center gap-2 border-t border-hairline bg-white/[0.02] px-4 py-2.5">
                {detecting && (
                  <span className="inline-flex items-center gap-1.5 text-xs text-ink-faint">
                    <span className="h-3 w-3 animate-spin rounded-full border border-ink-faint border-t-transparent" />
                    Detecting stack…
                  </span>
                )}
                {!detecting && detected && (
                  <>
                    <span className="text-xs text-ink-faint">Detected:</span>
                    <span className="rounded-full bg-gold/15 px-2.5 py-0.5 text-xs font-medium text-gold-soft">{detected.primary_label}</span>
                    {Object.keys(detected.tech_labels || {}).slice(0, 3).map((key) => (
                      <span key={key} className="rounded-full border border-hairline bg-white/[0.03] px-2.5 py-0.5 text-xs text-ink-dim">{detected.tech_labels[key]}</span>
                    ))}
                  </>
                )}
              </div>
            )}

            {/* Divider */}
            <div className="border-t border-hairline" />

            {/* Prompt textarea */}
            <textarea
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
              placeholder={'Describe what to modernize and the target language or platform…\n\nExamples:\n· Migrate this legacy .NET 4 app to .NET 8 Blazor Server\n· Convert Oracle PL/SQL procedures to PostgreSQL 16\n· Build a Java Spring Boot 3 REST API for inventory management'}
              rows={6}
              className="w-full resize-none bg-transparent px-5 py-4 text-sm leading-7 text-ink placeholder-ink-faint outline-none"
            />

            {/* Footer: output mode toggle + submit */}
            <div className="flex items-center justify-between border-t border-hairline px-4 py-3">
              <div className="flex items-center gap-1.5">
                {[
                  { id: 'project',     icon: FolderOpen, label: 'Project' },
                  { id: 'single_file', icon: FileText,   label: 'Script'  },
                ].map(({ id, icon: Icon, label }) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setOutputMode(id)}
                    className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium transition ${
                      outputMode === id
                        ? 'border-gold/40 bg-gold/15 text-gold-soft'
                        : 'border-hairline bg-white/[0.03] text-ink-dim hover:bg-white/[0.07] hover:text-ink'
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {label}
                  </button>
                ))}
              </div>
              <button
                type="submit"
                disabled={!canSubmit}
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gold text-bg transition hover:bg-gold-soft disabled:cursor-not-allowed disabled:opacity-30"
              >
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </form>

        {/* Bottom chip */}
        <div className="mt-7">
          <Link
            to="/jobs"
            className="inline-flex items-center gap-2 rounded-full border border-hairline bg-surface px-4 py-2 text-sm text-ink-dim shadow-sm transition hover:border-hairline-strong hover:bg-surface-hover hover:text-ink"
          >
            <Layers3 className="h-3.5 w-3.5" />
            View jobs
          </Link>
        </div>
      </div>

      {showBrowser && (
        <FolderBrowserModal onSelect={handleBrowseSelect} onClose={() => setShowBrowser(false)} />
      )}
    </Layout>
  )
}
