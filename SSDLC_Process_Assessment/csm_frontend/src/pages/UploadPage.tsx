// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/pages (UploadPage.tsx)
// Date: 2025-11-04
// ---------------------------------------------------------------------------
import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload,
  FileSpreadsheet,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  X,
} from 'lucide-react'
import { uploadWorkbook } from '../api/client'
import { useWorkbook } from '../context/WorkbookContext'
import type { WorkbookUploadResponse } from '../types'

type UploadState = 'idle' | 'uploading' | 'parsing' | 'calculating' | 'ready' | 'error'

const STATE_LABELS: Record<UploadState, string> = {
  idle: 'Ready to upload',
  uploading: 'Uploading file...',
  parsing: 'Parsing workbook...',
  calculating: 'Running calculations...',
  ready: 'Ready',
  error: 'Upload failed',
}

// Function: UploadPage
export default function UploadPage() {
  const navigate = useNavigate()
  const { setWorkbookId } = useWorkbook()
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<WorkbookUploadResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.xlsx')) {
      setError('Please upload a .xlsx file (Excel workbook).')
      return
    }
    setSelectedFile(file)
    setError(null)
    setResult(null)

    try {
      setUploadState('uploading')
      await new Promise((r) => setTimeout(r, 400))
      setUploadState('parsing')
      const response = await uploadWorkbook(file)
      setUploadState('calculating')
      await new Promise((r) => setTimeout(r, 500))
      setUploadState('ready')
      setResult(response)
      setWorkbookId(response.workbook_id)
    } catch (err) {
      setUploadState('error')
      setError(err instanceof Error ? err.message : 'Upload failed')
    }
  }, [setWorkbookId])

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragActive(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  // Function: onInputChange
  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  // Function: clearFile
  const clearFile = () => {
    setSelectedFile(null)
    setResult(null)
    setError(null)
    setUploadState('idle')
    if (inputRef.current) inputRef.current.value = ''
  }

  const isProcessing = ['uploading', 'parsing', 'calculating'].includes(uploadState)

  return (
    <div className="min-h-screen bg-navy-900 flex flex-col">
      {/* Hero */}
      <div className="bg-gradient-to-br from-navy-800 via-navy-900 to-navy-900 border-b border-navy-700 px-8 py-12">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-accent-blue/10 border border-accent-blue/20 rounded-full text-xs font-semibold text-accent-blue uppercase tracking-wider mb-6">
            Executive Analytics Platform
          </div>
          <h1 className="text-4xl font-extrabold text-slate-100 mb-4 tracking-tight">
            Consolidation Savings Model
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mx-auto">
            Upload your Excel workbook to instantly generate interactive financial dashboards,
            tower-level savings models, and vendor consolidation insights.
          </p>
        </div>
      </div>

      {/* Upload area */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 py-12">
        <div className="w-full max-w-2xl space-y-6">
          {/* Drop zone */}
          {!result && (
            <div
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200 ${
                dragActive
                  ? 'border-accent-blue bg-accent-blue/10'
                  : isProcessing
                  ? 'border-navy-600 bg-navy-800 cursor-not-allowed'
                  : 'border-navy-600 hover:border-accent-blue/60 hover:bg-navy-800/60 bg-navy-800/30'
              }`}
              onDragEnter={(e) => { e.preventDefault(); setDragActive(true) }}
              onDragLeave={() => setDragActive(false)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={onDrop}
              onClick={() => !isProcessing && inputRef.current?.click()}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".xlsx"
                className="hidden"
                onChange={onInputChange}
                disabled={isProcessing}
              />

              {isProcessing ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-center">
                    <div className="w-12 h-12 border-2 border-accent-blue/30 border-t-accent-blue rounded-full animate-spin" />
                  </div>
                  <div>
                    <div className="text-accent-blue font-semibold text-lg">
                      {STATE_LABELS[uploadState]}
                    </div>
                    <div className="text-slate-500 text-sm mt-1">{selectedFile?.name}</div>
                  </div>
                  {/* Progress steps */}
                  <div className="flex items-center justify-center gap-3 mt-4">
                    {(['uploading', 'parsing', 'calculating'] as const).map((step, i) => {
                      const steps = ['uploading', 'parsing', 'calculating']
                      const currentIdx = steps.indexOf(uploadState)
                      const stepIdx = steps.indexOf(step)
                      const done = stepIdx < currentIdx
                      const active = stepIdx === currentIdx
                      return (
                        <div key={step} className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${done ? 'bg-accent-green' : active ? 'bg-accent-blue animate-pulse' : 'bg-navy-600'}`} />
                          <span className={`text-xs ${active ? 'text-accent-blue' : done ? 'text-accent-green' : 'text-slate-600'}`}>
                            {STATE_LABELS[step]}
                          </span>
                          {i < 2 && <div className="w-6 h-px bg-navy-600" />}
                        </div>
                      )
                    })}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-center">
                    <div className="w-16 h-16 bg-accent-blue/10 rounded-2xl flex items-center justify-center">
                      <FileSpreadsheet size={32} className="text-accent-blue" />
                    </div>
                  </div>
                  <div>
                    <div className="text-slate-200 font-semibold text-lg mb-1">
                      {dragActive ? 'Drop your file here' : 'Drop your Excel workbook here'}
                    </div>
                    <div className="text-slate-500 text-sm">
                      or click to browse · <span className="text-accent-blue">.xlsx files only</span>
                    </div>
                  </div>
                  {selectedFile && !isProcessing && (
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-navy-700 rounded-lg text-xs text-slate-300">
                      <FileSpreadsheet size={12} className="text-accent-blue" />
                      {selectedFile.name}
                      <button
                        onClick={(e) => { e.stopPropagation(); clearFile() }}
                        className="text-slate-500 hover:text-slate-300"
                      >
                        <X size={12} />
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-accent-red/10 border border-accent-red/30 rounded-xl">
              <AlertTriangle size={16} className="text-accent-red shrink-0 mt-0.5" />
              <div>
                <div className="text-accent-red font-semibold text-sm">Upload Error</div>
                <div className="text-slate-300 text-sm mt-0.5">{error}</div>
              </div>
              <button onClick={clearFile} className="ml-auto text-slate-500 hover:text-slate-300">
                <X size={14} />
              </button>
            </div>
          )}

          {/* Success result */}
          {result && (
            <div className="bg-navy-800 border border-navy-700 rounded-2xl overflow-hidden">
              <div className="flex items-center gap-3 px-6 py-4 bg-accent-green/10 border-b border-accent-green/20">
                <CheckCircle size={20} className="text-accent-green" />
                <div>
                  <div className="font-semibold text-accent-green">Workbook Loaded Successfully</div>
                  <div className="text-xs text-slate-400 mt-0.5">{result.filename}</div>
                </div>
                <button onClick={clearFile} className="ml-auto text-slate-500 hover:text-slate-300">
                  <X size={14} />
                </button>
              </div>

              <div className="p-6 space-y-4">
                {/* Sheet cards */}
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                    {result.sheet_count} Sheets Detected
                  </div>
                  <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                    {result.sheets.map((sheet) => (
                      <div
                        key={sheet}
                        className="flex items-center gap-2 px-3 py-2 bg-navy-700/50 rounded-lg text-xs"
                      >
                        <CheckCircle size={12} className="text-accent-green shrink-0" />
                        <span className="text-slate-300 truncate">{sheet}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Validation warnings */}
                {result.validation?.warnings?.length > 0 && (
                  <div className="flex items-start gap-3 p-3 bg-accent-amber/10 border border-accent-amber/20 rounded-lg">
                    <AlertTriangle size={14} className="text-accent-amber shrink-0 mt-0.5" />
                    <div>
                      <div className="text-xs font-semibold text-accent-amber mb-1">Validation Warnings</div>
                      <ul className="space-y-0.5">
                        {result.validation.warnings.map((w, i) => (
                          <li key={i} className="text-xs text-slate-400">• {w}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                <button
                  onClick={() => navigate('/dashboard')}
                  className="w-full flex items-center justify-center gap-2 py-3 bg-accent-blue hover:bg-blue-500 text-white rounded-xl font-semibold text-sm transition-colors"
                >
                  Open Dashboard
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {/* Instructions */}
          {!result && !isProcessing && (
            <div className="grid grid-cols-3 gap-4">
              {[
                { step: '1', title: 'Upload', desc: 'Drop your Consolidation_Savings_Model.xlsx file' },
                { step: '2', title: 'Analyze', desc: 'System parses all sheets and runs calculations' },
                { step: '3', title: 'Explore', desc: 'Navigate interactive dashboards and scenarios' },
              ].map((item) => (
                <div key={item.step} className="bg-navy-800/50 border border-navy-700 rounded-xl p-4 text-center">
                  <div className="w-7 h-7 bg-accent-blue/10 rounded-lg flex items-center justify-center text-accent-blue font-bold text-sm mx-auto mb-2">
                    {item.step}
                  </div>
                  <div className="text-xs font-semibold text-slate-200 mb-1">{item.title}</div>
                  <div className="text-xs text-slate-500">{item.desc}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Upload button if file selected but not processing */}
      {selectedFile && !isProcessing && !result && (
        <div className="pb-8 flex justify-center">
          <button
            onClick={() => handleFile(selectedFile)}
            className="flex items-center gap-2 px-8 py-3 bg-accent-blue hover:bg-blue-500 text-white rounded-xl font-semibold transition-colors"
          >
            <Upload size={16} />
            Upload & Analyze
          </button>
        </div>
      )}
    </div>
  )
}
