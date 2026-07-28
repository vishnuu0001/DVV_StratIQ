// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (LandingPage.jsx)
// Date: 2025-09-17
// ---------------------------------------------------------------------------
import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Github, FolderOpen, Building2, ChevronRight, Code2, Cpu, Cloud, Shield, TrendingUp, Zap, FolderSearch, UploadCloud } from 'lucide-react'
import clsx from 'clsx'
import JSZip from 'jszip'
import { startAnalysisUpload } from '../api/client.js'

// Directories excluded client-side before zipping — matches the noise the
// backend analyzer already skips server-side (dependency trees, VCS metadata,
// build output). Filtering these out before upload rather than after keeps
// the upload itself small and fast instead of transferring megabytes of
// node_modules just to have the server ignore them.
const _UPLOAD_SKIP_DIRS = new Set([
  'node_modules', '.git', '.svn', '.hg', 'dist', 'build', 'out', 'target',
  '.venv', 'venv', '__pycache__', '.pytest_cache', '.mypy_cache',
  '.next', '.nuxt', 'coverage', '.idea', '.vscode', 'bin', 'obj',
])

// Function: _shouldSkipUploadPath
function _shouldSkipUploadPath(relativePath) {
  return relativePath.split('/').some((seg) => _UPLOAD_SKIP_DIRS.has(seg))
}

const TABS = [
  { id: 'github',    label: 'GitHub Repo',    icon: Github },
  { id: 'portfolio', label: 'Organisation',   icon: Building2 },
  { id: 'local',     label: 'Local Path',     icon: FolderOpen },
]

const FEATURES = [
  { icon: Cpu,       label: 'Software Health',    desc: 'Resiliency · Agility · Elegance' },
  { icon: TrendingUp,label: 'Technical Debt',     desc: 'COCOMO II FTE & cost estimation' },
  { icon: Cloud,     label: 'Cloud Maturity',     desc: '6-dimension cloud readiness score' },
  { icon: Shield,    label: 'OSS Safety',         desc: 'CVE scan · licensing · freshness' },
  { icon: Zap,       label: 'Business Impact',    desc: 'Criticality index for IT decisions' },
]

const SUPPORTED = [
  // Core languages
  'Java', '.NET', 'Python', 'JavaScript', 'TypeScript',
  // Java EE / Spring
  'Spring MVC', 'Struts', 'JSP', 'Servlets', 'EJB',
  // Web
  'REST API', 'SOAP', 'jQuery', 'Bootstrap',
  // IBM Mainframe
  'COBOL', 'JCL', 'CICS', 'VSAM', 'DB2', 'CSP', 'PANVALET', 'ISPF', 'z/OS',
  // Other mainframe
  'ASM', 'PL/I', 'REXX',
  // IBM Platform
  'IBM WAS', 'UDB',
]

// ─────────────────────────────────────────────────────────────────────────────
// Folder picker — uses File System Access API (showDirectoryPicker)
// with a <input webkitdirectory> fallback for browsers that don't support it.
// Defined at module scope (NOT inside LandingPage) so HMR can track it.
// ─────────────────────────────────────────────────────────────────────────────
// Function: LocalPathPicker
function LocalPathPicker({ value, onChange }) {
  const fileInputRef = useRef(null)
  const inputRef = useRef(null)
  const [picking, setPicking] = useState(false)
  const [pickedName, setPickedName] = useState('')   // friendly display name
  const [storedFullPath, setStoredFullPath] = useState('')  // store full path from manual entry
  // Tracks how `value` was populated so the UI never claims false certainty.
  // Browsers' folder pickers (showDirectoryPicker / webkitdirectory) only ever
  // expose the bare leaf folder name, never a full path — 'history-guess' means
  // the full path shown was *inferred* by matching that bare name against
  // previously-saved paths in localStorage, which can silently produce a wrong
  // (stale or unrelated) path if any earlier entry happens to end in the same
  // folder name. Only 'typed' and 'drag' reflect a path the browser/user
  // actually gave us directly and can be trusted without a re-check.
  const [pathSource, setPathSource] = useState('')

  /* Load recently used paths from localStorage */
  // Function: getRecentPaths
  const getRecentPaths = () => {
    try {
      const stored = localStorage.getItem('recentFolderPaths')
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  }

  /* Save path to localStorage */
  // Function: saveRecentPath
  const saveRecentPath = (path) => {
    try {
      const recent = getRecentPaths()
      const updated = [path, ...recent.filter(p => p !== path)].slice(0, 10)
      localStorage.setItem('recentFolderPaths', JSON.stringify(updated))
    } catch {}
  }

  /* Remove one specific path from history — lets a user self-heal a stale/wrong
     entry that keeps getting guessed for a folder name it no longer matches. */
  // Function: forgetRecentPath
  const forgetRecentPath = (path) => {
    try {
      const recent = getRecentPaths().filter(p => p !== path)
      localStorage.setItem('recentFolderPaths', JSON.stringify(recent))
    } catch {}
  }

  /* Find matching full path from history based on folder name */
  // Function: findFullPathInHistory
  const findFullPathInHistory = (folderName) => {
    const recent = getRecentPaths()
    return recent.find(p => p.endsWith(`\\${folderName}`) || p.endsWith(`/${folderName}`))
  }

  /* Extract folder name from a full path */
  // Function: extractFolderName
  const extractFolderName = (path) => {
    return path.replace(/\\/g, '/').split('/').filter(p => p).pop() || ''
  }

  /* Handle manual path input - store full path when typed */
  // Function: handleInputChange
  const handleInputChange = (e) => {
    const newValue = e.target.value
    onChange(newValue)
    setPathSource('typed')

    // If user typed a path with backslashes or slashes, extract and store the folder name
    if (newValue.includes('\\') || (newValue.includes('/') && newValue.length > 1)) {
      const folderName = extractFolderName(newValue)
      if (folderName) {
        setPickedName(folderName)
        setStoredFullPath(newValue)
        saveRecentPath(newValue)  // Save to history immediately
      }
    }
  }

  /* Handle drag and drop to capture full path */
  // Function: handleDragOver
  const handleDragOver = (e) => {
    e.preventDefault()
    e.currentTarget.classList.add('ring-2', 'ring-emerald-500', 'bg-emerald-500/10')
  }

  // Function: handleDragLeave
  const handleDragLeave = (e) => {
    e.currentTarget.classList.remove('ring-2', 'ring-emerald-500', 'bg-emerald-500/10')
  }

  // Function: handleDrop
  const handleDrop = (e) => {
    e.preventDefault()
    e.currentTarget.classList.remove('ring-2', 'ring-emerald-500', 'bg-emerald-500/10')
    
    // Try to get paths from dataTransfer
    if (e.dataTransfer.items) {
      for (let item of e.dataTransfer.items) {
        if (item.kind === 'file') {
          const entry = item.webkitGetAsEntry?.()
          if (entry && entry.isDirectory) {
            const fullPath = entry.fullPath || entry.name
            onChange(fullPath)
            setPathSource('drag')
            setPickedName(extractFolderName(fullPath))
            setStoredFullPath(fullPath)
            saveRecentPath(fullPath)
            return
          }
        }
      }
    }
  }

  /* Native folder dialog via File System Access API */
  // Function: openPicker
  const openPicker = async () => {
    // Modern browsers: File System Access API
    if (typeof window.showDirectoryPicker === 'function') {
      try {
        setPicking(true)
        const handle = await window.showDirectoryPicker({ mode: 'read' })
        const folderName = handle.name
        setPickedName(folderName)

        // The browser ONLY ever gives us the bare folder name here — never a full
        // path (a deliberate browser-security restriction). Anything below is a
        // GUESS, not a fact, so it's flagged 'history-guess' and must not be
        // presented to the user as a verified/confirmed path.
        const fullPathFromHistory = findFullPathInHistory(folderName)
        if (fullPathFromHistory) {
          onChange(fullPathFromHistory)
          setPathSource('history-guess')
          setStoredFullPath(fullPathFromHistory)
          return
        }

        // If we have a stored full path with same folder name, use it (also a guess)
        if (storedFullPath && extractFolderName(storedFullPath) === folderName) {
          onChange(storedFullPath)
          setPathSource('history-guess')
          return
        }

        // Otherwise, just set the folder name and prompt for full path
        onChange(folderName)
        setPathSource('bare-name-only')
      } catch (err) {
        if (err.name !== 'AbortError') console.warn('Folder picker error:', err)
      } finally {
        setPicking(false)
      }
      return
    }
    // Fallback: hidden <input webkitdirectory>
    fileInputRef.current?.click()
  }

  /* Fallback: extract full path from files' webkitRelativePath */
  // Function: onFallbackChange
  const onFallbackChange = (e) => {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return

    // Try to extract root folder name and reconstruct path
    const firstFile = files[0]
    const webkitPath = firstFile.webkitRelativePath || ''
    const pathParts = webkitPath.split('/')
    const rootFolder = pathParts[0]
    
    setPickedName(rootFolder)

    // Try to find full path from history first — a GUESS, see openPicker() comment.
    const fullPathFromHistory = findFullPathInHistory(rootFolder)
    if (fullPathFromHistory) {
      onChange(fullPathFromHistory)
      setPathSource('history-guess')
      e.target.value = ''
      return
    }

    // Fallback: just use the root folder name
    onChange(rootFolder)
    setPathSource('bare-name-only')
    e.target.value = ''
  }

  return (
    <div>
      <label className="block text-xs font-medium text-slate-600 mb-1.5">
        Local Repository Path <span className="text-red-400">*</span> (full path required)
      </label>

      {/* Path input + Browse button */}
      <div className="flex gap-2 items-stretch">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          placeholder="Full path: C:\Projects\my-repo  or  /home/user/project  (or drag folder here)"
          className="input-field flex-1 min-w-0 transition-all"
          autoFocus
        />
        <button
          type="button"
          onClick={openPicker}
          disabled={picking}
          title="Browse for folder"
          className={clsx(
            'flex items-center gap-1.5 px-3 py-2 rounded-xl border text-xs font-medium',
            'transition-all duration-150 flex-shrink-0 whitespace-nowrap',
            picking
              ? 'border-brand-cyan/40 text-brand-cyan bg-brand-cyan/5 cursor-wait'
              : 'border-surface-border text-slate-600 bg-surface hover:border-brand-cyan/50',
            'hover:text-brand-cyan hover:bg-brand-cyan/5',
          )}
        >
          <FolderSearch size={14} className={picking ? 'animate-pulse' : ''} />
          {picking ? 'Opening…' : 'Browse…'}
        </button>
      </div>

      {/* Picked folder info */}
      {pickedName && (
        <motion.div
          initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-[11px] text-slate-400 space-y-1"
        >
          <div>
            📁 Folder picked: <span className="font-mono text-emerald-400">{pickedName}</span>
          </div>
          {pathSource === 'history-guess' && value && value.length > pickedName.length ? (
            <div className="text-amber-400 space-y-1">
              <div>
                ⚠️ <strong>Guessed from a previous entry — please verify:</strong>{' '}
                <span className="font-mono">{value}</span>
              </div>
              <div className="text-slate-400 text-[10px]">
                Your browser only tells us the folder's name ("{pickedName}"), not its full location —
                this path was matched from something you entered before and may be wrong or stale.
                Edit the field above if this isn't the folder you just picked, or{' '}
                <button
                  type="button"
                  className="underline hover:text-amber-300"
                  onClick={() => {
                    forgetRecentPath(value)
                    onChange(pickedName)
                    setPathSource('bare-name-only')
                  }}
                >
                  forget this suggestion
                </button>
                {' '}so it stops being guessed.
              </div>
            </div>
          ) : (pathSource === 'typed' || pathSource === 'drag') && value && value.length > pickedName.length ? (
            <div className="text-emerald-400">
              ✓ <strong>Full path:</strong> <span className="font-mono">{value}</span>
            </div>
          ) : (
            <div className="text-amber-400 space-y-1">
              <div>
                ⚠️ <strong>Complete the full path:</strong>
              </div>
              <div className="text-slate-400 text-[10px]">
                • Drag the folder from Windows Explorer into the input field, OR
              </div>
              <div className="text-slate-400 text-[10px]">
                • Manually type/paste the complete path
              </div>
              <div className="text-slate-500 mt-1">
                Example: <span className="font-mono text-cyan-300">C:\Projects\my-repo</span>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Hidden fallback input */}
      <input
        ref={fileInputRef}
        type="file"
        // @ts-ignore – webkitdirectory is non-standard
        webkitdirectory=""
        directory=""
        multiple
        className="hidden"
        onChange={onFallbackChange}
      />
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Upload Folder — the actual way to analyse a folder that only exists on the
// user's own device. Browsers cannot expose a real filesystem path to a
// server (by design, for security), so LocalPathPicker above only works when
// the analysed folder ALSO happens to exist on the machine running the
// backend. This component sidesteps that limitation entirely: it reads the
// real file contents via <input webkitdirectory>, zips them client-side, and
// uploads the archive — no path-guessing involved.
// ─────────────────────────────────────────────────────────────────────────────
// Function: UploadFolderPicker
function UploadFolderPicker({ onUploaded, users, revenue, disabled }) {
  const fileInputRef = useRef(null)
  const [stage, setStage] = useState('idle')   // idle | zipping | uploading | error
  const [folderName, setFolderName] = useState('')
  const [fileCount, setFileCount] = useState(0)
  const [progressPct, setProgressPct] = useState(0)
  const [errorMsg, setErrorMsg] = useState('')

  // Function: handleFiles
  const handleFiles = async (e) => {
    const allFiles = Array.from(e.target.files || [])
    e.target.value = ''
    if (allFiles.length === 0) return

    const rootFolder = (allFiles[0].webkitRelativePath || '').split('/')[0] || 'folder'
    const included = allFiles.filter((f) => !_shouldSkipUploadPath(f.webkitRelativePath || f.name))

    if (included.length === 0) {
      setStage('error')
      setErrorMsg('No analysable files found in this folder (everything matched an excluded directory).')
      return
    }

    setFolderName(rootFolder)
    setFileCount(included.length)
    setStage('zipping')
    setErrorMsg('')

    try {
      const zip = new JSZip()
      for (const f of included) {
        zip.file(f.webkitRelativePath || f.name, f)
      }
      const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE', compressionOptions: { level: 6 } })

      setStage('uploading')
      setProgressPct(0)
      // Submit directly here (not via onAnalyse) so the zip/upload progress UI
      // stays visible on this screen — onAnalyse is only called once a job_id
      // actually exists, at which point the parent hands off to the same
      // polling/dashboard flow every other analysis type already uses.
      const { job_id } = await startAnalysisUpload(blob, { users, revenue }, (pct) => setProgressPct(pct))
      onUploaded(job_id)
    } catch (err) {
      setStage('error')
      setErrorMsg(err?.response?.data?.detail || err?.message || 'Upload failed.')
    }
  }

  const busy = stage === 'zipping' || stage === 'uploading'

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        // @ts-ignore – webkitdirectory is non-standard
        webkitdirectory=""
        directory=""
        multiple
        className="hidden"
        onChange={handleFiles}
      />
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        disabled={disabled || busy}
        className={clsx(
          'w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border text-xs font-medium',
          'transition-all duration-150',
          busy
            ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/5 cursor-wait'
            : 'border-emerald-500/40 text-emerald-400 bg-emerald-500/5 hover:bg-emerald-500/10',
        )}
      >
        <UploadCloud size={14} className={busy ? 'animate-pulse' : ''} />
        {stage === 'zipping' && `Zipping ${fileCount} files from "${folderName}"…`}
        {stage === 'uploading' && `Uploading "${folderName}"… ${progressPct}%`}
        {(stage === 'idle' || stage === 'error') && 'Upload a folder from this device'}
      </button>
      {stage === 'error' && (
        <p className="mt-1.5 text-[11px] text-red-400">⚠️ {errorMsg}</p>
      )}
      {stage === 'idle' && (
        <p className="mt-1.5 text-[10px] text-slate-500">
          Reads and zips the folder's files in your browser, then uploads them for analysis —
          this is the only way to analyse code that lives solely on your own device.
        </p>
      )}
    </div>
  )
}

// Function: LandingPage
export default function LandingPage({ onAnalyse }) {
  const [tab, setTab]     = useState('github')
  const [repo, setRepo]   = useState('')
  const [org, setOrg]     = useState('')
  const [limit, setLimit] = useState(20)
  const [local, setLocal] = useState('')
  const [users, setUsers] = useState(100)
  const [revenue, setRevenue] = useState(0)
  const [advanced, setAdvanced] = useState(false)

  /* Save path to localStorage */
  // Function: saveLocalPathToHistory
  const saveLocalPathToHistory = (path) => {
    try {
      const recent = JSON.parse(localStorage.getItem('recentFolderPaths') || '[]')
      const updated = [path, ...recent.filter(p => p !== path)].slice(0, 10)
      localStorage.setItem('recentFolderPaths', JSON.stringify(updated))
    } catch {}
  }

  // Function: handleSubmit
  const handleSubmit = (e) => {
    e.preventDefault()
    if (tab === 'github')    onAnalyse({ type: 'single',    repo,  users, revenue })
    if (tab === 'portfolio') onAnalyse({ type: 'portfolio', org,   limit })
    if (tab === 'local') {
      saveLocalPathToHistory(local)
      onAnalyse({ type: 'single',    local, users, revenue })
    }
  }

  const isValid =
    (tab === 'github'    && repo.trim()) ||
    (tab === 'portfolio' && org.trim())  ||
    (tab === 'local'     && local.trim())

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#faf9f8' }}>
      {/* ── Navbar ────────────────────────────────────────────────────── */}
      <nav className="flex items-center justify-between px-8 py-4 border-b" style={{ borderColor: '#edebe9' }}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-sm flex items-center justify-center" style={{ background: '#0078d4' }}>
            <Code2 size={16} className="text-white" />
          </div>
          <span className="font-semibold text-slate-900 tracking-tight">CodeAnalysis</span>
          <span className="pill">v1.0</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="w-2 h-2 rounded-full" style={{ background: '#107c10' }} />
          API ready
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col items-center justify-start pt-16 px-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="text-center max-w-2xl mb-12"
        >
          {/* Icon */}
          <div className="w-20 h-20 mx-auto mb-8 rounded-sm flex items-center justify-center" style={{ background: '#0078d4' }}>
            <Code2 size={36} className="text-white" />
          </div>

          <h1 className="text-4xl font-bold mb-4 leading-tight text-slate-900">
            Deep Code
            <br />
            Intelligence
          </h1>
          <p className="text-slate-600 text-lg leading-relaxed">
            Automated insights into software health, technical debt, and portfolio-level
            risks across <span className="text-slate-900 font-medium">Java · .NET · Python · COBOL · Mainframe · Web</span>.
          </p>
        </motion.div>

        {/* ── Form card ─────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full max-w-xl"
        >
          <div className="glass p-6">
            {/* Tabs */}
            <div className="flex gap-1.5 mb-6 p-1 bg-surface-hover rounded-sm">
              {TABS.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setTab(id)}
                  className={clsx(
                    'tab-btn flex-1 flex items-center justify-center gap-2',
                    tab === id ? 'tab-btn-active' : 'tab-btn-inactive'
                  )}
                >
                  <Icon size={14} />
                  {label}
                </button>
              ))}
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {tab === 'github' && (
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1.5">
                    GitHub Repository URL or owner/repo
                  </label>
                  <input
                    type="text"
                    value={repo}
                    onChange={(e) => setRepo(e.target.value)}
                    placeholder="https://github.com/owner/repo"
                    className="input-field"
                    autoFocus
                  />
                </div>
              )}

              {tab === 'portfolio' && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1.5">
                      GitHub Organisation Name
                    </label>
                    <input
                      type="text"
                      value={org}
                      onChange={(e) => setOrg(e.target.value)}
                      placeholder="my-github-org"
                      className="input-field"
                      autoFocus
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1.5">
                      Max Repositories to Scan
                    </label>
                    <input
                      type="number"
                      value={limit}
                      onChange={(e) => setLimit(Number(e.target.value))}
                      min={1} max={100}
                      className="input-field w-32"
                    />
                  </div>
                </div>
              )}

              {tab === 'local' && (
                <div className="space-y-3">
                  <LocalPathPicker value={local} onChange={setLocal} />
                  <div className="flex items-center gap-2 text-[10px] text-slate-500">
                    <div className="flex-1 h-px bg-surface-border" />
                    OR, if your code lives only on this device
                    <div className="flex-1 h-px bg-surface-border" />
                  </div>
                  <UploadFolderPicker
                    users={users}
                    revenue={revenue}
                    onUploaded={(jobId) => onAnalyse({ type: 'uploaded', jobId })}
                  />
                </div>
              )}

              {/* Advanced options */}
              {tab !== 'portfolio' && (
                <div>
                  <button
                    type="button"
                    onClick={() => setAdvanced(!advanced)}
                    className="text-xs text-slate-500 hover:text-gray-300 flex items-center gap-1 transition-colors"
                  >
                    <ChevronRight size={12} className={clsx('transition-transform duration-200', advanced && 'rotate-90')} />
                    Business context (optional)
                  </button>

                  {advanced && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-3 grid grid-cols-2 gap-3"
                    >
                      <div>
                        <label className="block text-xs text-slate-500 mb-1">Estimated Users</label>
                        <input
                          type="number"
                          value={users}
                          onChange={(e) => setUsers(Number(e.target.value))}
                          min={1}
                          className="input-field"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-slate-500 mb-1">Annual Revenue Impact ($)</label>
                        <input
                          type="number"
                          value={revenue}
                          onChange={(e) => setRevenue(Number(e.target.value))}
                          min={0}
                          className="input-field"
                        />
                      </div>
                    </motion.div>
                  )}
                </div>
              )}

              <button type="submit" disabled={!isValid} className="btn-primary w-full mt-2">
                <span className="flex items-center justify-center gap-2">
                  <Zap size={16} />
                  Analyse Now
                </span>
              </button>
            </form>
          </div>
        </motion.div>

        {/* ── Supported languages strip ─────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 flex items-center gap-3 flex-wrap justify-center"
        >
          <span className="text-xs text-slate-500">Supports</span>
          {SUPPORTED.map((lang) => (
            <span key={lang} className="pill bg-surface-hover border border-surface-border text-slate-600">
              {lang}
            </span>
          ))}
        </motion.div>

        {/* ── Feature pills ─────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-12 grid grid-cols-2 sm:grid-cols-5 gap-3 max-w-3xl w-full"
        >
          {FEATURES.map(({ icon: Icon, label, desc }) => (
            <div key={label} className="glass p-4 flex flex-col items-center text-center gap-2 hover:border-brand-indigo/50 transition-colors group">
              <div className="w-9 h-9 rounded-lg bg-brand-indigo/10 flex items-center justify-center group-hover:bg-brand-indigo/20 transition-colors">
                <Icon size={18} className="text-brand-purple" />
              </div>
              <div>
                <div className="text-xs font-semibold text-slate-900">{label}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">{desc}</div>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  )
}
