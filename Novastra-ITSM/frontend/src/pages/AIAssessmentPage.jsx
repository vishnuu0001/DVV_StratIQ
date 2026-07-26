// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (AIAssessmentPage.jsx)
// Date: 2026-03-18
// ---------------------------------------------------------------------------
import { useMemo, useState } from 'react'
import toast from 'react-hot-toast'
import * as XLSX from 'xlsx'
import {
  BrainCircuit,
  CheckCircle2,
  Clock,
  Download,
  FileSpreadsheet,
  Layers,
  Loader2,
  Sparkles,
  Tag,
  TicketCheck,
  TrendingUp,
  Upload,
  Zap,
} from 'lucide-react'

import { ticketAnalyzeExcel, ticketPredictAutomation } from '../services/api.js'

const OPP_CSV_HEADERS = [
  'ID', 'Title', 'Opportunity Type', 'Confidence', 'Impact', 'Effort',
  'Est. Monthly Hrs Saved', 'Description', 'Evidence', 'Recommended Steps',
]

// Function: oppToRow
function oppToRow(opp) {
  return [
    opp.id ?? '',
    opp.title ?? '',
    opp.opportunity_type ?? '',
    opp.confidence ?? '',
    opp.impact ?? '',
    opp.effort ?? '',
    opp.estimated_monthly_hours_saved ?? 0,
    opp.description ?? '',
    Array.isArray(opp.evidence) ? opp.evidence.join(' | ') : '',
    Array.isArray(opp.recommended_steps) ? opp.recommended_steps.join(' | ') : '',
  ]
}

// Function: downloadCSV
function downloadCSV(opportunities) {
  const rows = [OPP_CSV_HEADERS, ...opportunities.map(oppToRow)]
  const csvContent = rows.map((row) =>
    row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')
  ).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `automation_opportunities_${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

// Function: downloadXLSX
function downloadXLSX(opportunities) {
  const rows = [OPP_CSV_HEADERS, ...opportunities.map(oppToRow)]
  const ws = XLSX.utils.aoa_to_sheet(rows)
  // Auto column widths
  ws['!cols'] = OPP_CSV_HEADERS.map((h, i) => {
    const maxLen = Math.max(h.length, ...opportunities.map((o) => String(oppToRow(o)[i] ?? '').length))
    return { wch: Math.min(maxLen + 4, 60) }
  })
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Opportunities')
  XLSX.writeFile(wb, `automation_opportunities_${new Date().toISOString().slice(0,10)}.xlsx`)
}

// Function: formatApiError
const formatApiError = (err, fallback = 'Request failed') => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (Array.isArray(detail)) {
    const msg = detail.map((e) => (typeof e === 'string' ? e : e?.msg || JSON.stringify(e))).filter(Boolean).join('; ')
    if (msg) return msg
  }
  if (detail && typeof detail === 'object') {
    if (typeof detail.msg === 'string' && detail.msg.trim()) return detail.msg
    try { return JSON.stringify(detail) } catch { return fallback }
  }
  return err?.message || fallback
}

const TONE = {
  high:   { ring: 'border-red-500/50',     bg: 'bg-red-500/15',     text: 'text-red-300',     dot: 'bg-red-400' },
  medium: { ring: 'border-amber-500/50',   bg: 'bg-amber-500/15',   text: 'text-amber-300',   dot: 'bg-amber-400' },
  low:    { ring: 'border-emerald-500/50', bg: 'bg-emerald-500/15', text: 'text-emerald-300', dot: 'bg-emerald-400' },
}
// Function: tone
const tone = (v) => TONE[String(v || '').toLowerCase()] || { ring: 'border-slate-600', bg: 'bg-slate-700/40', text: 'text-slate-300', dot: 'bg-slate-500' }

// Function: safeNumber
const safeNumber = (v) => { const n = Number(v); return Number.isFinite(n) ? n : 0 }

// Function: KpiCard
function KpiCard({ icon: Icon, label, value, accent }) {
  const accents = {
    blue:    { border: 'border-blue-500/20',    iconBg: 'bg-blue-500/10',    iconColor: 'text-blue-400',    val: 'text-blue-100' },
    violet:  { border: 'border-violet-500/20',  iconBg: 'bg-violet-500/10',  iconColor: 'text-violet-400',  val: 'text-violet-100' },
    emerald: { border: 'border-emerald-500/20', iconBg: 'bg-emerald-500/10', iconColor: 'text-emerald-400', val: 'text-emerald-100' },
    amber:   { border: 'border-amber-500/20',   iconBg: 'bg-amber-500/10',   iconColor: 'text-amber-400',   val: 'text-amber-100' },
  }
  const a = accents[accent] || accents.blue
  return (
    <div className={`relative rounded-2xl border ${a.border} bg-gray-900/80 p-5 flex flex-col gap-3 overflow-hidden backdrop-blur-sm`}>
      <div className="absolute inset-0 pointer-events-none opacity-30"
        style={{ background: `radial-gradient(ellipse at top left, var(--tw-gradient-stops))` }} />
      <div className={`w-9 h-9 rounded-xl ${a.iconBg} flex items-center justify-center shrink-0`}>
        <Icon size={17} className={a.iconColor} />
      </div>
      <div>
        <p className="text-[11px] uppercase tracking-widest text-gray-500 font-medium">{label}</p>
        <p className={`mt-0.5 text-2xl font-bold ${a.val} tabular-nums`}>{value}</p>
      </div>
    </div>
  )
}

// Function: DistBar
function DistBar({ name, count, max }) {
  const pct = max > 0 ? Math.round((count / max) * 100) : 0
  return (
    <div className="group">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-300 truncate pr-3 group-hover:text-white transition-colors">{name}</span>
        <span className="text-xs font-mono text-gray-400 shrink-0">{count.toLocaleString()}</span>
      </div>
      <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-violet-500 transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// Function: OppCard
function OppCard({ opp, idx }) {
  const t = tone(opp.confidence)
  const hrs = safeNumber(opp.estimated_monthly_hours_saved)
  return (
    <article className={`rounded-2xl border ${t.ring} bg-gray-900/60 p-5 backdrop-blur-sm relative overflow-hidden`}>
      {/* Subtle glow behind card */}
      <div className={`absolute -top-8 -right-8 w-32 h-32 rounded-full ${t.bg} blur-2xl pointer-events-none opacity-40`} />

      {/* Header */}
      <div className="flex items-start gap-3">
        <div className={`mt-0.5 w-7 h-7 rounded-xl ${t.bg} flex items-center justify-center shrink-0`}>
          <span className={`text-xs font-bold ${t.text}`}>{idx + 1}</span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-white leading-snug">{opp.title}</h3>
          <span className="inline-block mt-1 text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300">
            {opp.opportunity_type}
          </span>
        </div>
        <div className="shrink-0 text-right">
          <div className="text-sm font-bold text-white tabular-nums">~{Math.round(hrs)}</div>
          <div className="text-[10px] text-gray-500">hrs saved/mo</div>
        </div>
      </div>

      {/* Badges */}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {[
          { label: 'Confidence', value: opp.confidence },
          { label: 'Impact', value: opp.impact },
          { label: 'Effort', value: opp.effort },
        ].map(({ label, value }) => {
          const b = tone(value)
          return (
            <span key={label} className={`text-[10px] px-2 py-0.5 rounded-full border ${b.ring} ${b.bg} ${b.text} flex items-center gap-1`}>
              <span className={`w-1.5 h-1.5 rounded-full ${b.dot}`} />
              {label}: {value}
            </span>
          )
        })}
      </div>

      {/* Description */}
      <p className="mt-3 text-sm text-gray-400 leading-relaxed">{opp.description}</p>

      {/* Evidence + Steps */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
        {Array.isArray(opp.evidence) && opp.evidence.length > 0 && (
          <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3">
            <p className="text-[10px] font-bold uppercase tracking-widest text-amber-500/80 mb-2.5 flex items-center gap-1">
              <TrendingUp size={10} /> Evidence
            </p>
            <ul className="space-y-2">
              {opp.evidence.map((item, i) => (
                <li key={i} className="flex gap-2 text-xs text-gray-400">
                  <span className="mt-0.5 w-1.5 h-1.5 rounded-full bg-amber-500/60 shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
        {Array.isArray(opp.recommended_steps) && opp.recommended_steps.length > 0 && (
          <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3">
            <p className="text-[10px] font-bold uppercase tracking-widest text-emerald-500/80 mb-2.5 flex items-center gap-1">
              <Zap size={10} /> Recommended Steps
            </p>
            <ol className="space-y-2">
              {opp.recommended_steps.map((step, i) => (
                <li key={i} className="flex gap-2 text-xs text-gray-400">
                  <span className="text-emerald-400 font-bold shrink-0 tabular-nums">{i + 1}.</span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </article>
  )
}

// Function: AIAssessmentPage
export default function AIAssessmentPage() {
  const [excelFile, setExcelFile] = useState(null)
  const [fileInputKey, setFileInputKey] = useState(0)
  const [sheetName, setSheetName] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [predicting, setPredicting] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [automationResult, setAutomationResult] = useState(null)
  const [showEmptySections, setShowEmptySections] = useState(false)

  const summary = analysisResult?.summary || {}
  const topCategories = analysisResult?.issues_by_category || []
  const topTypes = analysisResult?.issues_by_type || []
  const opportunities = automationResult?.automation_opportunities?.opportunities || []
  const hasDatasetContext = Boolean(excelFile || analysisResult)
  const showExpandedSections = hasDatasetContext || showEmptySections

  const totalPotentialHours = useMemo(
    () => opportunities.reduce((sum, item) => sum + safeNumber(item?.estimated_monthly_hours_saved), 0),
    [opportunities],
  )

  const maxCatCount = useMemo(() => Math.max(0, ...topCategories.map((r) => r.count)), [topCategories])
  const maxTypeCount = useMemo(() => Math.max(0, ...topTypes.map((r) => r.count)), [topTypes])

  // Function: onAnalyzeExcel
  const onAnalyzeExcel = async () => {
    if (!excelFile) { toast.error('Please upload an Excel file first.'); return }
    const formData = new FormData()
    formData.append('file', excelFile)
    if (sheetName.trim()) formData.append('sheet_name', sheetName.trim())
    setAnalyzing(true); setAutomationResult(null)
    try {
      const { data } = await ticketAnalyzeExcel(formData)
      setAnalysisResult(data)
      toast.success('Excel ticket analysis completed.')
    } catch (err) {
      toast.error(formatApiError(err, 'Excel analysis failed'))
    } finally { setAnalyzing(false) }
  }

  // Function: onPredictAutomation
  const onPredictAutomation = async () => {
    if (!analysisResult) { toast.error('Run analysis first.'); return }
    setPredicting(true)
    try {
      const { data } = await ticketPredictAutomation(analysisResult)
      setAutomationResult(data)
      const src = data?.automation_opportunities?.generated_with_llm ? 'Ollama LLM' : 'heuristic fallback'
      toast.success(`Automation opportunities generated using ${src}.`)
    } catch (err) {
      toast.error(formatApiError(err, 'Prediction failed'))
    } finally { setPredicting(false) }
  }

  // Function: onClearExcelAnalysis
  const onClearExcelAnalysis = () => {
    setExcelFile(null)
    setFileInputKey((k) => k + 1)
    setSheetName('')
    setAnalysisResult(null)
    setAutomationResult(null)
    setShowEmptySections(false)
    toast.success('Cleared uploaded file, Excel analysis, and AI predictions.')
  }

  // Function: onClearPredictions
  const onClearPredictions = () => {
    setAutomationResult(null)
    toast.success('AI predictions cleared.')
  }

  return (
    <div className="flex-1 overflow-auto bg-gray-950 text-white">
      {/* Page background texture */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-violet-600/5 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-5 py-6 space-y-6">

        {/* -- Hero header -- */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <BrainCircuit size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-xs font-black uppercase tracking-widest text-gray-400">AI Assessment</h1>
              <p className="text-xs text-gray-500">Upload ticket data  -  Analyze  -  Predict automation opportunities</p>
            </div>
          </div>
          {analysisResult && (
            <span className="shrink-0 flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-full">
              <CheckCircle2 size={12} /> Dataset loaded
            </span>
          )}
        </div>

        {/* -- Upload section -- */}
        <div className="rounded-2xl border border-white/10 bg-gray-900/70 p-5 backdrop-blur-sm">
          <p className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-4 flex items-center gap-2">
            <FileSpreadsheet size={13} className="text-blue-400" /> Upload & Analyze
          </p>
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_200px_180px] gap-3">
            <label className="rounded-xl border border-dashed border-white/15 bg-white/[0.03] px-4 py-3.5 flex items-center gap-3 cursor-pointer hover:border-blue-500/40 hover:bg-white/5 transition-all group">
              <Upload size={16} className="text-blue-400 group-hover:scale-110 transition-transform shrink-0" />
              <span className="truncate text-sm text-gray-400 group-hover:text-gray-200 transition-colors">
                {excelFile ? (
                  <><span className="text-blue-300 font-medium">{excelFile.name}</span></>
                ) : 'Choose Excel file (.xlsx, .xls, .xlsm)'}
              </span>
              <input key={fileInputKey} type="file" accept=".xlsx,.xls,.xlsm" className="hidden"
                onChange={(e) => setExcelFile(e.target.files?.[0] || null)} />
            </label>

            <input type="text" value={sheetName} onChange={(e) => setSheetName(e.target.value)}
              placeholder="Sheet name (optional)"
              className="rounded-xl bg-white/[0.03] border border-white/10 px-4 py-3 text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500/60 focus:bg-white/5 transition-all" />

            <button type="button" onClick={onAnalyzeExcel} disabled={analyzing}
              className="rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold px-4 py-3 flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 transition-all">
              {analyzing ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
              {analyzing ? 'Analyzing...' : 'Analyze Excel'}
            </button>
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={onClearExcelAnalysis}
              disabled={analyzing || predicting || (!excelFile && !analysisResult && !automationResult && !sheetName)}
              className="rounded-lg border border-white/15 bg-white/[0.03] hover:bg-white/[0.06] disabled:opacity-40 disabled:cursor-not-allowed text-xs font-medium px-3 py-2 transition-all"
            >
              Clear Excel Analysis
            </button>
            <button
              type="button"
              onClick={onClearPredictions}
              disabled={analyzing || predicting || !automationResult}
              className="rounded-lg border border-white/15 bg-white/[0.03] hover:bg-white/[0.06] disabled:opacity-40 disabled:cursor-not-allowed text-xs font-medium px-3 py-2 transition-all"
            >
              Clear AI Predictions
            </button>
          </div>
        </div>

        {!hasDatasetContext && (
          <div className="rounded-2xl border border-white/10 bg-gray-900/70 p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between gap-3">
              <p className="text-xs text-gray-400">
                Analysis and prediction panels are collapsed until a file is uploaded.
              </p>
              <button
                type="button"
                onClick={() => setShowEmptySections((s) => !s)}
                className="rounded-lg border border-white/15 bg-white/[0.03] hover:bg-white/[0.06] text-xs font-medium px-3 py-2 transition-all"
              >
                {showExpandedSections ? 'Hide Empty Panels' : 'Show Empty Panels'}
              </button>
            </div>
          </div>
        )}

        {showExpandedSections && (
          <>
        {/* -- KPI cards -- */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <KpiCard icon={TicketCheck} label="Total Tickets"    value={(summary.total_issues    ?? 0).toLocaleString()} accent="blue" />
          <KpiCard icon={Layers}     label="Open Tickets"      value={(summary.open_count      ?? 0).toLocaleString()} accent="violet" />
          <KpiCard icon={CheckCircle2} label="Resolved Tickets" value={(summary.resolved_count ?? 0).toLocaleString()} accent="emerald" />
          <KpiCard icon={Clock}      label="Avg TAT (days)"    value={summary.average_tat_days != null ? Number(summary.average_tat_days).toFixed(1) : 'N/A'} accent="amber" />
        </div>

        {/* -- Distribution panels -- */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {/* Categories */}
          <div className="rounded-2xl border border-white/10 bg-gray-900/70 p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-gray-500 flex items-center gap-2">
                <Layers size={12} className="text-blue-400" /> All Categories
              </p>
              {topCategories.length > 0 && (
                <span className="text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full">
                  {topCategories.length} types
                </span>
              )}
            </div>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-1 custom-scrollbar">
              {topCategories.length === 0
                ? <p className="text-xs text-gray-600 py-6 text-center">Upload and analyze a file to view category distribution.</p>
                : topCategories.map((row) => (
                    <DistBar key={row.category} name={row.category || 'Uncategorized'} count={row.count} max={maxCatCount} />
                  ))}
            </div>
          </div>

          {/* Issue types */}
          <div className="rounded-2xl border border-white/10 bg-gray-900/70 p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-gray-500 flex items-center gap-2">
                <Tag size={12} className="text-violet-400" /> All Issue Types
              </p>
              {topTypes.length > 0 && (
                <span className="text-xs bg-violet-500/10 border border-violet-500/20 text-violet-400 px-2 py-0.5 rounded-full">
                  {topTypes.length} types
                </span>
              )}
            </div>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-1 custom-scrollbar">
              {topTypes.length === 0
                ? <p className="text-xs text-gray-600 py-6 text-center">Upload and analyze a file to view issue type distribution.</p>
                : topTypes.map((row) => (
                    <DistBar key={row.issue_type} name={row.issue_type || 'Unspecified'} count={row.count} max={maxTypeCount} />
                  ))}
            </div>
          </div>
        </div>

        {/* -- Automation Predictor -- */}
        <div className="rounded-2xl border border-white/10 bg-gray-900/70 p-5 backdrop-blur-sm">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <Sparkles size={16} className="text-white" />
              </div>
              <div>
                <h2 className="text-sm font-bold">Automation Opportunity Predictor</h2>
                <p className="text-xs text-gray-500 mt-0.5">AI-powered analysis via Ollama LLM -- identifies all viable automation opportunities</p>
              </div>
            </div>
            <button type="button" onClick={onPredictAutomation} disabled={!analysisResult || predicting}
              className="shrink-0 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-semibold px-5 py-2.5 flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all">
              {predicting ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
              {predicting ? 'Predicting...' : 'Predict Automation'}
            </button>
          </div>

          {predicting && (
            <div className="mt-6 flex flex-col items-center gap-3 py-8 text-center">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                <Loader2 size={22} className="text-emerald-400 animate-spin" />
              </div>
              <p className="text-sm text-gray-400">Running Ollama LLM analysis...</p>
              <p className="text-xs text-gray-600">Identifying all high-impact automation opportunities across ITSM categories</p>
            </div>
          )}

          {!predicting && automationResult?.automation_opportunities && (
            <div className="mt-5 space-y-4">
              {/* Summary strip */}
              <div className="rounded-xl bg-gradient-to-r from-emerald-500/10 to-teal-500/5 border border-emerald-500/20 p-4">
                <p className="text-sm font-medium text-emerald-100 leading-relaxed">
                  {automationResult.automation_opportunities.overall_recommendation}
                </p>
                <div className="mt-3 flex flex-wrap gap-5">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center">
                      <Sparkles size={14} className="text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-xl font-bold text-white tabular-nums">{opportunities.length}</div>
                      <div className="text-[10px] text-emerald-400/70 uppercase tracking-wider">Opportunities</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-teal-500/15 flex items-center justify-center">
                      <Clock size={14} className="text-teal-400" />
                    </div>
                    <div>
                      <div className="text-xl font-bold text-white tabular-nums">{Math.round(totalPotentialHours)}</div>
                      <div className="text-[10px] text-teal-400/70 uppercase tracking-wider">Hrs saved / month</div>
                    </div>
                  </div>
                  {automationResult.automation_opportunities.generated_with_llm && (
                    <div className="flex items-center gap-2 ml-auto">
                      <span className="text-xs bg-violet-500/10 border border-violet-500/20 text-violet-300 px-3 py-1 rounded-full flex items-center gap-1.5">
                        <BrainCircuit size={11} /> Powered by Ollama LLM
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Opportunity cards */}
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs text-gray-500">{opportunities.length} opportunit{opportunities.length === 1 ? 'y' : 'ies'} identified</p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => downloadCSV(opportunities)}
                    className="flex items-center gap-1.5 rounded-lg border border-white/15 bg-white/[0.03] hover:bg-white/[0.07] text-xs font-medium px-3 py-1.5 transition-all text-gray-300 hover:text-white"
                  >
                    <Download size={12} /> Download CSV
                  </button>
                  <button
                    type="button"
                    onClick={() => downloadXLSX(opportunities)}
                    className="flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 text-xs font-medium px-3 py-1.5 transition-all text-emerald-300 hover:text-emerald-100"
                  >
                    <Download size={12} /> Download XLSX
                  </button>
                </div>
              </div>
              <div className="space-y-3">
                {opportunities.map((opp, i) => <OppCard key={opp.id} opp={opp} idx={i} />)}
              </div>
            </div>
          )}
        </div>

          </>
        )}

      </div>
    </div>
  )
}
