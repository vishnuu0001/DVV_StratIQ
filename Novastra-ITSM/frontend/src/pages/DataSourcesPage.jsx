// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (DataSourcesPage.jsx)
// Date: 2025-12-18
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Plus, Trash2, RefreshCw, Folder, Cloud, Globe, CheckCircle,
  XCircle, Clock, Loader2, ChevronDown, ChevronUp, Database, Files, Upload,
  Network,
} from 'lucide-react'
import { clsx } from 'clsx'
import {
  apiBase, dsListSources, dsGetTypes, dsAddSource, dsDeleteSource, dsSyncSource,
} from '../services/api.js'
import { useAuth } from '../contexts/AuthContext.jsx'

const TYPE_ICONS = {
  local_folder: Folder,
  sharepoint:   Cloud,
  url:          Globe,
}

const STATUS_CONFIG = {
  idle:     { label: 'Idle',     color: 'text-gray-400',  icon: Clock },
  syncing:  { label: 'Syncing',  color: 'text-blue-400',  icon: Loader2 },
  ok:       { label: 'Synced',   color: 'text-green-400', icon: CheckCircle },
  error:    { label: 'Error',    color: 'text-red-400',   icon: XCircle },
  pending:  { label: 'Pending',  color: 'text-yellow-400', icon: Clock },
}

const STEP_ICON_MAP = {
  progress:       { Icon: Loader2,     className: 'text-blue-400 mt-0.5 shrink-0 animate-spin' },
  file_done:      { Icon: CheckCircle, className: 'text-green-400 mt-0.5 shrink-0' },
  file_error:     { Icon: XCircle,     className: 'text-red-400 mt-0.5 shrink-0' },
  error:          { Icon: XCircle,     className: 'text-red-400 mt-0.5 shrink-0' },
  building_graph: { Icon: Network,     className: 'text-purple-400 mt-0.5 shrink-0' },
  complete:       { Icon: CheckCircle, className: 'text-green-400 mt-0.5 shrink-0' },
  start:          { Icon: Database,    className: 'text-blue-400 mt-0.5 shrink-0' },
}

const STEP_TEXT_CLASS_MAP = {
  file_error:     'text-red-400',
  error:          'text-red-400',
  file_done:      'text-gray-300',
  building_graph: 'text-purple-300',
  complete:       'text-green-300',
  progress:       'text-blue-300',
}

// Function: fmtTime
function fmtTime(ts) {
  if (!ts) return 'Never'
  return new Date(ts * 1000).toLocaleString()
}

// Monotonic counter for React list keys — avoids Math.random() (flagged as an
// insecure PRNG by static analysis even though this is just a key, not a secret).
let _stepKeyCounter = 0
// Function: nextStepKey
function nextStepKey() {
  _stepKeyCounter += 1
  return `${Date.now()}-${_stepKeyCounter}`
}

// Function: DataSourcesPage
export default function DataSourcesPage() {
  const { user, token } = useAuth()
  const isAdmin = user?.role === 'admin'
  const navigate = useNavigate()

  const [sources, setSources] = useState([])
  const [types, setTypes]     = useState([])
  const [loading, setLoading] = useState(false)
  const [showAdd, setShowAdd] = useState(false)
  const [expanded, setExpanded] = useState({})

  // Add-source form state
  const [newName, setNewName]   = useState('')
  const [newType, setNewType]   = useState('')
  const [newConfig, setNewConfig] = useState({})

  // Local-folder selection mode
  const [localFolderMode, setLocalFolderMode] = useState('folder') // 'folder' | 'files'
  const [selectedFiles, setSelectedFiles] = useState([])
  const [processing, setProcessing] = useState(false)
  const fileInputRef   = useRef(null)
  const folderInputRef = useRef(null)

  // Progress modal state
  const [showProgress, setShowProgress]         = useState(false)
  const [progressSteps, setProgressSteps]       = useState([])
  const [progressTotal, setProgressTotal]       = useState(0)
  const [progressCurrent, setProgressCurrent]   = useState(0)
  const [processingComplete, setProcessingComplete] = useState(false)
  const [processingResult, setProcessingResult] = useState(null)
  const progressEndRef = useRef(null)

  // Auto-scroll progress log as steps arrive
  useEffect(() => {
    progressEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [progressSteps])

  const load = useCallback(async () => {
    setLoading(true)
    // Load types (no auth required) and sources (auth required) independently
    // so the add-source form always works even if the sources list fails
    const [typesResult, sourcesResult] = await Promise.allSettled([
      dsGetTypes(),
      dsListSources(),
    ])
    if (typesResult.status === 'fulfilled') {
      setTypes(typesResult.value.data)
      if (!newType && typesResult.value.data.length > 0) setNewType(typesResult.value.data[0].type)
    }
    if (sourcesResult.status === 'fulfilled') {
      setSources(sourcesResult.value.data)
    } else {
      const err = sourcesResult.reason
      toast.error(err.response?.data?.detail || 'Failed to load data sources')
    }
    setLoading(false)
  }, [newType])

  useEffect(() => { load() }, [])  // eslint-disable-line react-hooks/exhaustive-deps

  const selectedTypeDef = types.find((t) => t.type === newType)

  // Function: handleTypeChange
  const handleTypeChange = (t) => {
    setNewType(t)
    setNewConfig({})
    setLocalFolderMode('folder')
    setSelectedFiles([])
  }

  // Function: handleReset
  const handleReset = () => {
    setNewName('')
    setNewConfig({})
    setShowAdd(false)
    setLocalFolderMode('folder')
    setSelectedFiles([])
    if (fileInputRef.current)   fileInputRef.current.value   = ''
    if (folderInputRef.current) folderInputRef.current.value = ''
  }

  // Function: applyFileResultEvent
  const applyFileResultEvent = (data) => {
    setProgressCurrent(data.current)
    // Replace the matching in-flight progress step with the result
    setProgressSteps((prev) => {
      const filtered = prev.filter((s) => !(s.type === 'progress' && s.file === data.file))
      return [...filtered, { ...data, _key: nextStepKey() }]
    })
  }

  // Function: applyStreamEvent
  const applyStreamEvent = (data) => {
    const handlers = {
      start: () => setProgressSteps([{ ...data, _key: Date.now() }]),
      progress: () => {
        setProgressCurrent(data.current)
        setProgressSteps((prev) => [...prev, { ...data, _key: nextStepKey() }])
      },
      file_done: () => applyFileResultEvent(data),
      file_error: () => applyFileResultEvent(data),
      building_graph: () => setProgressSteps((prev) => [...prev, { ...data, _key: nextStepKey() }]),
      complete: () => {
        setProcessingComplete(true)
        setProcessingResult(data)
        setProgressSteps((prev) => [...prev, { ...data, _key: nextStepKey() }])
        handleReset()
        load()
      },
      error: () => {
        toast.error(data.message)
        setShowProgress(false)
      },
    }
    const handler = handlers[data.type]
    if (handler) handler()
  }

  // Function: consumeProcessStream
  const consumeProcessStream = async (response) => {
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        let data
        try { data = JSON.parse(line.slice(6)) } catch { continue }
        applyStreamEvent(data)
      }
    }
  }

  // Function: handleProcessLocalFolder
  const handleProcessLocalFolder = async () => {
    if (!selectedFiles.length) return toast.error('Please select a folder or files first')

    setProcessing(true)
    setProgressSteps([])
    setProgressTotal(selectedFiles.length)
    setProgressCurrent(0)
    setProcessingComplete(false)
    setProcessingResult(null)
    setShowProgress(true)

    try {
      const formData = new FormData()
      selectedFiles.forEach((f) => formData.append('files', f))

      const response = await fetch(`${apiBase}/datasources/process-files-stream`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      })

      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${response.status}`)
      }

      await consumeProcessStream(response)
    } catch (err) {
      toast.error(err.message || 'Processing failed')
      setShowProgress(false)
    } finally {
      setProcessing(false)
    }
  }

  // Function: handleProcessRemoteSource
  const handleProcessRemoteSource = async () => {
    // Folder path / SharePoint / URL: validate, add source, and for local_folder auto-sync
    if (!newName.trim()) return toast.error('Name is required')
    if (!newType) return toast.error('Select a source type')
    const requiredFields = selectedTypeDef?.fields?.filter((f) => f.required) || []
    for (const f of requiredFields) {
      if (!newConfig[f.key]?.trim()) return toast.error(`${f.label} is required`)
    }
    setProcessing(true)
    try {
      const res = await dsAddSource({ name: newName.trim(), type: newType, config: newConfig })
      if (newType === 'local_folder') {
        await dsSyncSource(res.data.id)
        toast.success(`"${newName}" added — indexing started`)
      } else {
        toast.success(`Data source "${newName}" added`)
      }
      handleReset()
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add source')
    } finally {
      setProcessing(false)
    }
  }

  // Function: handleProcess
  const handleProcess = async (e) => {
    e.preventDefault()

    if (newType === 'local_folder') {
      await handleProcessLocalFolder()
    } else {
      await handleProcessRemoteSource()
    }
  }

  // Function: handleDelete
  const handleDelete = async (source) => {
    if (!confirm(`Delete data source "${source.name}"?`)) return
    try {
      await dsDeleteSource(source.id)
      toast.success(`Deleted "${source.name}"`)
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete')
    }
  }

  // Function: handleSync
  const handleSync = async (source) => {
    try {
      await dsSyncSource(source.id)
      toast.success(`Sync started for "${source.name}"`)
      // Poll for updated status
      setTimeout(load, 2000)
      setTimeout(load, 5000)
      setTimeout(load, 10000)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Sync failed')
    }
  }

  // Function: toggleExpand
  const toggleExpand = (id) => setExpanded((p) => ({ ...p, [id]: !p[id] }))

  // Source list content — an if/else chain (not a nested ternary) picking
  // between the loading, empty, and populated states.
  let sourcesSection
  if (loading && sources.length === 0) {
    sourcesSection = (
      <div className="flex items-center justify-center py-16 text-gray-600">
        <Loader2 size={20} className="animate-spin mr-2" />
        <span className="text-sm">Loading sources…</span>
      </div>
    )
  } else if (sources.length === 0) {
    sourcesSection = (
      <div className="text-center py-16 bg-gray-900 border border-white/10 rounded-xl">
        <Database size={32} className="mx-auto text-gray-700 mb-3" />
        <p className="text-gray-400 font-medium">No data sources configured</p>
        {isAdmin && (
          <p className="text-sm text-gray-600 mt-1">
            Click <strong className="text-gray-400">Add Source</strong> to connect your first data repository.
          </p>
        )}
      </div>
    )
  } else {
    sourcesSection = (
      <div className="space-y-3">
        {sources.map((source) => {
          const Icon = TYPE_ICONS[source.type] || Database
          const statusCfg = STATUS_CONFIG[source.status] || STATUS_CONFIG.idle
          const StatusIcon = statusCfg.icon
          const isExpanded = expanded[source.id]

          return (
            <div
              key={source.id}
              className="bg-gray-900 border border-white/10 rounded-xl overflow-hidden"
            >
              <div className="flex items-center gap-3 p-4">
                {/* Type icon */}
                <div className="w-9 h-9 rounded-lg bg-blue-600/20 flex items-center justify-center shrink-0">
                  <Icon size={17} className="text-blue-400" />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-white truncate">{source.name}</p>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-gray-400 uppercase font-mono shrink-0">
                      {source.type.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className={clsx('flex items-center gap-1 text-xs', statusCfg.color)}>
                      <StatusIcon
                        size={11}
                        className={source.status === 'syncing' ? 'animate-spin' : ''}
                      />
                      {statusCfg.label}
                    </span>
                    {source.chunks_indexed > 0 && (
                      <span className="text-xs text-gray-500">
                        {source.chunks_indexed.toLocaleString()} chunks
                      </span>
                    )}
                    <span className="text-xs text-gray-600">
                      Last sync: {fmtTime(source.last_synced)}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 shrink-0">
                  {isAdmin && (
                    <button
                      onClick={() => handleSync(source)}
                      disabled={source.status === 'syncing'}
                      title="Sync now"
                      className="p-1.5 rounded-lg text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 disabled:opacity-40 transition"
                    >
                      <RefreshCw
                        size={14}
                        className={source.status === 'syncing' ? 'animate-spin' : ''}
                      />
                    </button>
                  )}
                  {isAdmin && (
                    <button
                      onClick={() => handleDelete(source)}
                      title="Delete"
                      className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                  <button
                    onClick={() => toggleExpand(source.id)}
                    className="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 transition"
                  >
                    {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                </div>
              </div>

              {/* Expanded details */}
              {isExpanded && (
                <div className="border-t border-white/5 px-4 py-3 bg-black/20">
                  <dl className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs">
                    <dt className="text-gray-500">ID</dt>
                    <dd className="text-gray-400 font-mono">{source.id}</dd>
                    <dt className="text-gray-500">Created</dt>
                    <dd className="text-gray-400">{fmtTime(source.created_at)}</dd>
                    {source.last_result?.message && (
                      <>
                        <dt className="text-gray-500">Last message</dt>
                        <dd className="text-gray-400 truncate col-span-1">{source.last_result.message}</dd>
                      </>
                    )}
                  </dl>

                  {/* Config values */}
                  {Object.keys(source.config).length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-white/5">
                      <p className="text-[10px] font-semibold text-gray-600 uppercase tracking-wide mb-1.5">
                        Configuration
                      </p>
                      <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs">
                        {Object.entries(source.config).map(([k, v]) => (
                          <div key={k} className="contents">
                            <dt className="text-gray-500">{k}</dt>
                            <dd className="text-gray-400 font-mono truncate">
                              {['secret', 'password', 'client_secret'].includes(k.toLowerCase())
                                ? '••••••••'
                                : String(v)}
                            </dd>
                          </div>
                        ))}
                      </dl>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <>
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              <Database size={20} className="text-blue-400" />
              Data Sources
            </h1>
            <p className="text-sm text-gray-400 mt-0.5">
              Connect knowledge repositories to index into the AI knowledge base
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={load}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition"
              title="Refresh"
            >
              <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
            </button>
            {isAdmin && (
              <button
                onClick={() => setShowAdd((p) => !p)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition"
              >
                <Plus size={15} />
                Add Source
              </button>
            )}
          </div>
        </div>

        {/* Add source form */}
        {showAdd && isAdmin && (
          <div className="mb-5 bg-gray-900 border border-white/10 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-white mb-4">New Data Source</h2>
            <form onSubmit={handleProcess} className="space-y-4">

              {/* Name — only needed for SharePoint / URL sources */}
              {newType !== 'local_folder' && (
              <div>
                <label htmlFor="ds-source-name" className="block text-xs font-medium text-gray-400 mb-1.5">
                  Source Name *
                </label>
                <input
                  id="ds-source-name"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="My Knowledge Library"
                  className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-white/10 text-white text-sm focus:outline-none focus:border-blue-500 transition"
                />
              </div>
              )}

              {/* Type selector */}
              <div>
                {/* Not a <label> — this heads a button group, not a single form control */}
                <span className="block text-xs font-medium text-gray-400 mb-1.5">
                  Source Type *
                </span>
                <div className="grid grid-cols-3 gap-2">
                  {types.map((t) => {
                    const Icon = TYPE_ICONS[t.type] || Database
                    return (
                      <button
                        key={t.type}
                        type="button"
                        onClick={() => handleTypeChange(t.type)}
                        className={clsx(
                          'flex flex-col items-center gap-1.5 p-3 rounded-lg border text-sm font-medium transition',
                          newType === t.type
                            ? 'border-blue-500 bg-blue-600/20 text-white'
                            : 'border-white/10 bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                        )}
                      >
                        <Icon size={18} />
                        <span className="text-xs">{t.label}</span>
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Dynamic config fields */}
              {/* Folder / Files toggle (Local Folder only) */}
              {newType === 'local_folder' && (
                <div>
                  {/* Not a <label> — this heads a button group, not a single form control */}
                  <span className="block text-xs font-medium text-gray-400 mb-1.5">
                    Selection Mode
                  </span>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setLocalFolderMode('folder')
                        setSelectedFiles([])
                        if (folderInputRef.current) {
                          folderInputRef.current.value = ''
                          folderInputRef.current.click()
                        }
                      }}
                      className={clsx(
                        'flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition',
                        localFolderMode === 'folder'
                          ? 'border-blue-500 bg-blue-600/20 text-white'
                          : 'border-white/10 bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white',
                      )}
                    >
                      <Folder size={13} />
                      Entire Folder
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setLocalFolderMode('files')
                        setSelectedFiles([])
                        if (fileInputRef.current) {
                          fileInputRef.current.value = ''
                          fileInputRef.current.click()
                        }
                      }}
                      className={clsx(
                        'flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition',
                        localFolderMode === 'files'
                          ? 'border-blue-500 bg-blue-600/20 text-white'
                          : 'border-white/10 bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white',
                      )}
                    >
                      <Files size={13} />
                      Select Files
                    </button>
                  </div>

                  {/* Hidden inputs — must NOT be display:none so .click() works cross-browser */}
                  <input
                    ref={(el) => {
                      folderInputRef.current = el
                      if (el) el.webkitdirectory = true
                    }}
                    type="file"
                    multiple
                    onChange={(e) => {
                      setLocalFolderMode('folder')
                      setSelectedFiles(Array.from(e.target.files || []))
                    }}
                    style={{ position: 'absolute', opacity: 0, pointerEvents: 'none', width: 0, height: 0 }}
                    tabIndex={-1}
                    aria-hidden="true"
                  />
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".docx,.xlsx,.xls,.csv,.txt,.md,.pdf,.png,.jpg,.jpeg"
                    onChange={(e) => {
                      setLocalFolderMode('files')
                      setSelectedFiles(Array.from(e.target.files || []))
                    }}
                    style={{ position: 'absolute', opacity: 0, pointerEvents: 'none', width: 0, height: 0 }}
                    tabIndex={-1}
                    aria-hidden="true"
                  />
                </div>
              )}

              {/* Selected files list */}
              {newType === 'local_folder' && selectedFiles.length > 0 && (
                <div className="rounded-lg border border-white/10 bg-gray-800/60 p-3">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-medium text-gray-400">
                      {selectedFiles.length} file(s) selected
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedFiles([])
                        if (fileInputRef.current)   fileInputRef.current.value   = ''
                        if (folderInputRef.current) folderInputRef.current.value = ''
                      }}
                      className="text-[10px] text-gray-500 hover:text-red-400 transition"
                    >
                      Clear
                    </button>
                  </div>
                  <ul className="space-y-0.5 max-h-32 overflow-y-auto">
                    {selectedFiles.map((f) => (
                      <li key={f.webkitRelativePath || f.name} className="text-xs text-gray-400 truncate">
                        {f.webkitRelativePath || f.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Drop zone prompt when nothing selected yet (local folder) */}
              {newType === 'local_folder' && selectedFiles.length === 0 && (
                <div className="flex flex-col items-center justify-center w-full px-4 py-5 rounded-lg border-2 border-dashed border-white/10 bg-gray-800/40 text-center">
                  <Upload size={20} className="text-gray-600 mb-1.5" />
                  <span className="text-xs text-gray-500">
                    Use the buttons above to open a folder or pick files
                  </span>
                  <span className="text-[10px] text-gray-600 mt-1">
                    .docx .xlsx .csv .txt .md .pdf .png .jpg
                  </span>
                </div>
              )}

              {/* Config fields for SharePoint / URL */}
              {newType !== 'local_folder' && selectedTypeDef && (
                <div className="space-y-3">
                  <p className="text-xs text-gray-500">{selectedTypeDef.description}</p>
                  {selectedTypeDef.fields.map((field) => (
                    <div key={field.key}>
                      <label className="block text-xs font-medium text-gray-400 mb-1.5">
                        {field.label} {field.required && <span className="text-red-400">*</span>}
                      </label>
                      <input
                        type={field.type === 'password' ? 'password' : 'text'}
                        value={newConfig[field.key] || ''}
                        onChange={(e) =>
                          setNewConfig((p) => ({ ...p, [field.key]: e.target.value }))
                        }
                        placeholder={field.placeholder || ''}
                        className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-white/10 text-white text-sm focus:outline-none focus:border-blue-500 transition"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-1">
                <button
                  type="submit"
                  disabled={processing}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-medium transition"
                >
                  {processing && <Loader2 size={14} className="animate-spin" />}
                  Process
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 text-sm transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Source list */}
        {sourcesSection}
      </div>
    </div>

    {/* ── Processing Progress Modal ──────────────────────────────── */}
    {showProgress && (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-gray-900 border border-white/10 rounded-xl w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]">

          {/* Header */}
          <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10 shrink-0">
            <Network size={17} className="text-blue-400 shrink-0" />
            <h2 className="text-sm font-bold text-white flex-1">
              {processingComplete ? 'Knowledge Base Updated' : 'Processing Documents'}
            </h2>
            {!processingComplete
              ? <Loader2 size={15} className="animate-spin text-blue-400 shrink-0" />
              : <CheckCircle size={15} className="text-green-400 shrink-0" />}
          </div>

          {/* Progress bar */}
          <div className="px-5 pt-4 shrink-0">
            <div className="flex justify-between text-[11px] text-gray-500 mb-1.5">
              <span>Progress</span>
              <span>{Math.min(progressCurrent, progressTotal)} / {progressTotal} file(s)</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
              <div
                className={clsx(
                  'h-1.5 rounded-full transition-all duration-500',
                  processingComplete ? 'bg-green-500' : 'bg-blue-500'
                )}
                style={{ width: `${progressTotal > 0 ? (Math.min(progressCurrent, progressTotal) / progressTotal) * 100 : 0}%` }}
              />
            </div>
          </div>

          {/* Step log */}
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-2 min-h-0">
            {progressSteps.map((step) => {
              const icon = STEP_ICON_MAP[step.type]
              const textClass = STEP_TEXT_CLASS_MAP[step.type] || 'text-gray-500'
              const isDone = step.type === 'file_done'
              return (
                <div key={step._key} className="flex items-start gap-2.5 text-xs">
                  {icon && <icon.Icon size={12} className={icon.className} />}
                  <span className={clsx('flex-1', textClass)}>
                    {step.message}
                  </span>
                  {isDone && step.chunks > 0 && (
                    <span className="shrink-0 text-blue-400 font-mono">{step.chunks} chunks</span>
                  )}
                </div>
              )
            })}
            <div ref={progressEndRef} />
          </div>

          {/* Completion actions */}
          {processingComplete && processingResult && (
            <div className="px-5 pb-5 pt-1 shrink-0 space-y-3">
              <div className="rounded-lg bg-green-900/20 border border-green-500/20 p-3">
                <p className="text-xs font-medium text-green-400">
                  ✓ {processingResult.files_processed} file(s) indexed — {processingResult.total_chunks} chunks added to knowledge base
                </p>
                {processingResult.files_failed > 0 && (
                  <p className="text-xs text-amber-400 mt-1">
                    ⚠ {processingResult.files_failed} file(s) could not be indexed
                  </p>
                )}
              </div>
              <p className="text-[11px] text-gray-500">
                The knowledge graph has been updated with the newly indexed content.
                You can explore entity relationships and connections in the Knowledge Graph view.
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => { setShowProgress(false); navigate('/knowledge-graph') }}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition"
                >
                  <Network size={14} />
                  View Knowledge Graph
                </button>
                <button
                  onClick={() => setShowProgress(false)}
                  className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 text-sm transition"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    )}
    </>
  )
}
