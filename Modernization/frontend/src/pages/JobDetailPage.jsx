// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/pages (JobDetailPage.jsx)
// Date: 2025-10-19
// ---------------------------------------------------------------------------
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  Download,
  XCircle,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { Link, useParams } from 'react-router-dom'
import { getDownloadUrl, getJob, getJobStatus, getStreamUrl } from '../api/client.js'
import Layout from '../components/Layout.jsx'

// Function: isTerminalStatus
const isTerminalStatus = (s) => ['completed', 'validation_failed', 'failed'].includes(s)

const STATUS_CONFIG = {
  queued:    { label: 'Queued',    icon: Clock,        classes: 'border-sky-500/25 bg-sky-500/10 text-sky-300',          bar: 'bg-sky-400',     dot: 'bg-sky-400 animate-pulse' },
  pending:   { label: 'Queued',    icon: Clock,        classes: 'border-sky-500/25 bg-sky-500/10 text-sky-300',          bar: 'bg-sky-400',     dot: 'bg-sky-400 animate-pulse' },
  running:   { label: 'Running',   icon: Clock,        classes: 'border-gold/30 bg-gold/10 text-gold-soft',              bar: 'bg-gold',        dot: 'bg-gold animate-pulse' },
  completed: { label: 'Completed', icon: CheckCircle2, classes: 'border-emerald-500/25 bg-emerald-500/10 text-emerald-300', bar: 'bg-emerald-400', dot: 'bg-emerald-400' },
  validation_failed: { label: 'Validation failed', icon: XCircle, classes: 'border-red-500/25 bg-red-500/10 text-red-300', bar: 'bg-red-400', dot: 'bg-red-400' },
  failed:    { label: 'Failed',    icon: XCircle,       classes: 'border-red-500/25 bg-red-500/10 text-red-300',           bar: 'bg-red-400',     dot: 'bg-red-400' },
}

const TABS = [
  { id: 'progress',      label: 'Progress' },
  { id: 'tech-stack',    label: 'Tech Stack' },
  { id: 'database',      label: 'Database' },
  { id: 'anti-patterns', label: 'Anti-patterns' },
  { id: 'output',        label: 'Output' },
]

// Function: JobDetailPage
export default function JobDetailPage() {
  const { jobId } = useParams()
  const [job, setJob] = useState(null)
  const [logs, setLogs] = useState([])
  const [pollErrorStreak, setPollErrorStreak] = useState(0)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('progress')
  const [streamConnected, setStreamConnected] = useState(false)
  const logsEndRef = useRef(null)
  const esRef = useRef(null)
  const showedPollWarningRef = useRef(false)

  useEffect(() => {
    getJob(jobId)
      .then((data) => {
        setJob(data)
        if (Array.isArray(data?.events)) setLogs(data.events)
        setLoading(false)
      })
      .catch(() => {
        toast.error('Job not found')
        setLoading(false)
      })
  }, [jobId])

  useEffect(() => {
    let stopped = false
    let timer = null
    // Function: refreshJob
    const refreshJob = async () => {
      try {
        const data = await getJobStatus(jobId)
        if (stopped) return
        setJob((previous) => previous ? { ...previous, ...data } : data)
        setPollErrorStreak(0)
        showedPollWarningRef.current = false
        if (isTerminalStatus(data?.status)) stopped = true
      } catch {
        if (stopped) return
        setPollErrorStreak((prev) => prev + 1)
      } finally {
        // Recursive scheduling guarantees there is never more than one status
        // request in flight. setInterval previously accumulated overlapping
        // requests whenever the proxy or backend took longer than two seconds.
        if (!stopped) timer = setTimeout(refreshJob, 10000)
      }
    }
    timer = setTimeout(refreshJob, 5000)
    return () => { stopped = true; clearTimeout(timer) }
  }, [jobId])

  useEffect(() => {
    if (esRef.current) return
    const es = new EventSource(getStreamUrl(jobId))
    esRef.current = es
    es.onopen = () => {
      setStreamConnected(true)
      setPollErrorStreak(0)
      showedPollWarningRef.current = false
    }
    es.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data)
        setStreamConnected(true)
        setPollErrorStreak(0)
        showedPollWarningRef.current = false
        setLogs((prev) => [...prev, event])
        if (event.type === 'queued') {
          setJob((prev) => prev ? { ...prev, progress: 0, phase: 'queued', status: 'queued' } : prev)
        } else if (event.type === 'progress') {
          setJob((prev) => prev ? { ...prev, progress: event.progress, phase: event.phase, status: 'running' } : prev)
        } else if (event.type === 'analysis_complete') {
          setJob((prev) => prev ? { ...prev, analysis: event.analysis, progress: 50 } : prev)
        } else if (event.type === 'complete') {
          setJob((prev) => prev ? { ...prev, status: 'completed', progress: 100, ...(event.output ? { output: event.output } : {}) } : prev)
          es.close()
          getJob(jobId).then((data) => { setJob(data); setLogs(Array.isArray(data?.events) ? data.events : []) }).catch(() => {})
        } else if (event.type === 'validation_failed') {
          setJob((prev) => prev ? { ...prev, status: 'validation_failed', progress: 100, output: event.output, validation: event.validation } : prev)
          es.close()
          getJob(jobId).then((data) => { setJob(data); setLogs(Array.isArray(data?.events) ? data.events : []) }).catch(() => {})
        } else if (event.type === 'error') {
          setJob((prev) => prev ? { ...prev, status: 'failed', error: event.message } : prev)
          es.close()
        }
      } catch { /* ignore parse errors */ }
    }
    es.onerror = () => {
      setStreamConnected(false)
      if (isTerminalStatus(job?.status)) es.close()
    }
    return () => { es.close(); esRef.current = null; setStreamConnected(false) }
  }, [jobId, job?.status])

  useEffect(() => {
    if (pollErrorStreak >= 3 && !streamConnected && !showedPollWarningRef.current) {
      showedPollWarningRef.current = true
      toast.error('Live status is temporarily unavailable. Reconnecting...')
    }
  }, [pollErrorStreak, streamConnected])

  useEffect(() => {
    if (job?.status === 'completed' && job?.output == null) {
      getJob(jobId).then((data) => setJob(data)).catch(() => {})
    }
  }, [job?.status, job?.output, jobId])

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  if (loading) {
    return (
      <Layout>
        <div className="flex h-full items-center justify-center py-32">
          <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-hairline border-t-gold" />
        </div>
      </Layout>
    )
  }

  if (!job) {
    return (
      <Layout>
        <div className="flex h-full items-center justify-center py-32">
          <p className="text-ink-muted">Job not found.</p>
        </div>
      </Layout>
    )
  }

  const cfg = STATUS_CONFIG[job.status] || STATUS_CONFIG.running
  const StatusIcon = cfg.icon
  const analysis = job.analysis

  return (
    <Layout>
      <main className="mx-auto max-w-5xl px-6 py-8 lg:py-10">
        {/* Back link */}
        <Link to="/jobs" className="mb-6 inline-flex items-center gap-1.5 text-xs font-medium text-ink-faint transition hover:text-ink">
          <ArrowLeft className="h-3.5 w-3.5" />
          Analysis Jobs
        </Link>

        {/* Job header card */}
        <div className="mb-6 overflow-hidden rounded-2xl border border-hairline bg-surface shadow-sm">
          <div className="flex items-start justify-between gap-4 px-6 py-5">
            <div className="min-w-0 flex-1">
              <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-ink-faint">
                {job.folder_path ? 'Folder path' : 'Prompt'}
              </p>
              {job.folder_path ? (
                <p className="truncate font-mono text-sm text-ink-dim">{job.folder_path}</p>
              ) : (
                <p className="text-sm leading-6 text-ink-dim">{job.prompt || '(prompt-based generation)'}</p>
              )}
              {job.error && (
                <p className="mt-2 rounded-lg bg-red-500/10 px-3 py-2 text-xs text-red-300">
                  Error: {job.error}
                </p>
              )}
              {pollErrorStreak >= 3 && !streamConnected && !isTerminalStatus(job.status) && (
                <p className="mt-2 rounded-lg bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
                  Live status is temporarily unavailable. Reconnecting in the background; the generation job continues on the server.
                </p>
              )}
            </div>
            <span className={`inline-flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold ${cfg.classes}`}>
              <StatusIcon className="h-3.5 w-3.5" />
              {cfg.label}
            </span>
          </div>

          {/* Progress bar */}
          <div className="px-6 pb-5">
            <div className="mb-1.5 flex items-center justify-between text-xs text-ink-faint">
              <span>{job.phase ? job.phase.replace(/_/g, ' ') : 'Progress'}</span>
              <span className="font-semibold tabular-nums text-ink-dim">{job.progress || 0}%</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
              <div
                style={{ width: `${job.progress || 0}%` }}
                className={`h-full rounded-full transition-all duration-500 ${cfg.bar}`}
              />
            </div>
          </div>
        </div>

        {/* Tab bar */}
        <div className="mb-5 flex gap-1 overflow-x-auto rounded-xl border border-hairline bg-surface p-1 shadow-sm">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition ${
                activeTab === id
                  ? 'bg-gold text-bg shadow-sm'
                  : 'text-ink-muted hover:bg-white/[0.06] hover:text-ink'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {activeTab === 'progress'      && <ProgressTab logs={logs} logsEndRef={logsEndRef} job={job} />}
        {activeTab === 'tech-stack'    && <TechStackTab analysis={analysis} />}
        {activeTab === 'database'      && <DatabaseTab analysis={analysis} />}
        {activeTab === 'anti-patterns' && <AntiPatternsTab analysis={analysis} />}
        {activeTab === 'output'        && <OutputTab job={job} downloadUrl={getDownloadUrl(jobId)} />}
      </main>
    </Layout>
  )
}

/* ─── Progress tab ─── */
// Function: ProgressTab
function ProgressTab({ logs, logsEndRef, job }) {
  const singleFileCode = isTerminalStatus(job?.status) ? job?.output?.__single_file__ : null
  const validationFailed = job?.status === 'validation_failed'
  return (
    <div className="space-y-4">
      <div className="overflow-hidden rounded-2xl border border-hairline bg-surface">
        <div className="flex items-center gap-2 border-b border-hairline bg-surface-soft px-4 py-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-500/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/60" />
          <span className="ml-2 text-xs text-ink-faint">Event log</span>
        </div>
        <div className="h-64 overflow-y-auto px-4 py-3 font-mono text-xs leading-6">
          {logs.length === 0 ? (
            <p className="text-ink-faint">Waiting for events…</p>
          ) : (
            logs.map((log, i) => (
              <div
                key={i}
                className={
                  ['error', 'validation_failed'].includes(log.type) ? 'text-red-400' :
                  log.type === 'complete' ? 'text-emerald-400' :
                  log.type === 'progress' ? 'text-gold-soft' :
                  'text-ink-muted'
                }
              >
                <span className="text-ink-faint">[{log.type?.toUpperCase() || 'EVENT'}]</span>
                {log.phase && <span className="text-ink-faint"> [{log.phase}]</span>}
                {log.progress != null && <span className="text-ink-faint"> {log.progress}%</span>}
                {' '}{log.message || JSON.stringify(log)}
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>

      {singleFileCode && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-ink">Generated Code</p>
            <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${validationFailed ? 'border-red-500/25 bg-red-500/10 text-red-300' : 'border-emerald-500/25 bg-emerald-500/10 text-emerald-300'}`}>
              {validationFailed ? <XCircle className="h-3 w-3" /> : <CheckCircle2 className="h-3 w-3" />}
              {validationFailed ? 'Validation failed' : 'Validated'}
            </span>
          </div>
          {validationFailed && <ValidationDiagnostics validation={job.validation} />}
          <SingleFileViewer code={singleFileCode} />
        </div>
      )}
    </div>
  )
}

/* ─── Tech stack tab ─── */
// Function: TechStackTab
function TechStackTab({ analysis }) {
  const techStack = analysis?.tech_stack || {}
  const metrics = analysis?.metrics || {}
  const arch = analysis?.architecture || {}
  const languages = analysis?.languages || {}
  const detectedTechs = Object.entries(techStack)
  const hasArch = !!(arch.pattern || arch.era || arch.database || arch.complexity || arch.total_loc != null || metrics.class_count != null)
  const hasLangs = Object.keys(languages).length > 0

  return (
    <div className="grid gap-5 md:grid-cols-2">
      {/* Architecture */}
      <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm">
        <p className="mb-4 text-sm font-semibold text-ink">Architecture</p>
        {hasArch ? (
          <dl className="space-y-2">
            <InfoRow label="Pattern"    value={arch.pattern} />
            <InfoRow label="Era"        value={arch.era} />
            <InfoRow label="Database"   value={arch.database} />
            <InfoRow label="Complexity" value={arch.complexity} />
            <InfoRow label="Total LOC"  value={arch.total_loc != null ? arch.total_loc.toLocaleString() : null} />
            <InfoRow label="Classes"    value={metrics.class_count != null ? String(metrics.class_count) : null} />
            <InfoRow label="Methods"    value={metrics.method_count != null ? String(metrics.method_count) : null} />
          </dl>
        ) : <Nil />}
      </div>

      {/* Detected technologies */}
      <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm">
        <p className="mb-4 text-sm font-semibold text-ink">
          Detected Technologies
          {detectedTechs.length > 0 && (
            <span className="ml-2 rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-bold text-ink-muted">{detectedTechs.length}</span>
          )}
        </p>
        <div className="flex flex-wrap gap-2">
          {detectedTechs.length > 0 ? (
            detectedTechs
              .sort((a, b) => (b[1]?.file_count || 0) - (a[1]?.file_count || 0))
              .map(([tech, meta]) => (
                <span
                  key={tech}
                  title={(meta?.sample_files || []).join('\n')}
                  className="rounded-full border border-gold/25 bg-gold/10 px-2.5 py-1 text-xs font-medium text-gold-soft"
                >
                  {tech.replace(/_/g, ' ')}{meta?.file_count ? ` (${meta.file_count})` : ''}
                </span>
              ))
          ) : <Nil />}
        </div>
      </div>

      {/* Language distribution */}
      <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm md:col-span-2">
        <p className="mb-4 text-sm font-semibold text-ink">Language Distribution</p>
        {hasLangs ? (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {Object.entries(languages).map(([lang, data]) => (
              <div key={lang} className="rounded-xl border border-hairline bg-white/[0.02] p-3 text-center">
                <p className="text-xl font-bold text-ink">{data.files}</p>
                <p className="text-[11px] text-ink-faint">files</p>
                <p className="mt-1 text-xs font-medium capitalize text-ink-dim">{lang.replace(/-/g, ' ')}</p>
                <p className="text-[11px] text-ink-faint">{(data.lines || 0).toLocaleString()} lines</p>
              </div>
            ))}
          </div>
        ) : <Nil />}
      </div>
    </div>
  )
}

/* ─── Database tab ─── */
// Function: DatabaseTab
function DatabaseTab({ analysis }) {
  const db = analysis?.database || {}
  const migration = analysis?.modernization_targets?.migration || {}
  const notes = analysis?.modernization_targets?.notes || []
  const hasOracle = (db.oracle_patterns || []).length > 0
  const hasTables = (db.table_names || []).length > 0
  const hasConns = (db.connection_strings || []).length > 0
  const hasMig = !!(migration.from_db || migration.to_db || (migration.oracle_constructs_to_migrate || []).length || notes.length)

  return (
    <div className="grid gap-5 md:grid-cols-2">
      <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm">
        <p className="mb-4 text-sm font-semibold text-ink">Oracle Patterns Detected</p>
        {hasOracle ? (
          <ul className="space-y-2">
            {db.oracle_patterns.map((p, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="mt-0.5 h-4 w-4 shrink-0 rounded-full bg-amber-500/15 text-center text-[10px] font-bold leading-4 text-amber-300">!</span>
                <span className="text-ink-dim">{p}</span>
              </li>
            ))}
          </ul>
        ) : <Nil />}
      </div>

      <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm">
        <p className="mb-4 text-sm font-semibold text-ink">
          Table Names
          {hasTables && <span className="ml-2 rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-bold text-ink-muted">{db.table_names.length}</span>}
        </p>
        {hasTables ? (
          <div className="flex flex-wrap gap-1.5">
            {db.table_names.map((t) => (
              <span key={t} className="rounded-lg border border-hairline bg-white/[0.02] px-2 py-0.5 font-mono text-xs text-ink-dim">{t}</span>
            ))}
          </div>
        ) : <Nil />}
      </div>

      <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm">
        <p className="mb-4 text-sm font-semibold text-ink">Database Access</p>
        <dl className="space-y-2">
          <InfoRow label="Raw SQL Files" value={db.raw_sql_files != null ? String(db.raw_sql_files) : null} />
          <InfoRow label="ORM Detected"  value={db.orm_detected != null ? (db.orm_detected ? 'Yes' : 'No') : null} />
        </dl>
        {hasConns && (
          <div className="mt-4 space-y-2">
            <p className="text-xs font-semibold text-ink-muted">Connection strings</p>
            {db.connection_strings.map((entry, i) => (
              <div key={i} className="rounded-xl border border-hairline bg-white/[0.02] p-3">
                <p className="truncate text-[11px] text-ink-faint">{entry.file}</p>
                <p className="mt-1 break-all font-mono text-xs text-ink-dim">{entry.value}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm">
        <p className="mb-4 text-sm font-semibold text-ink">Migration Targets</p>
        {hasMig ? (
          <>
            <dl className="mb-3 space-y-2">
              <InfoRow label="From DB" value={migration.from_db} />
              <InfoRow label="To DB"   value={migration.to_db} />
            </dl>
            {(migration.oracle_constructs_to_migrate || []).map((c, i) => (
              <p key={i} className="mb-1 text-sm text-ink-dim">
                <span className="mr-1.5 font-bold text-gold-soft">›</span>{c}
              </p>
            ))}
            {notes.length > 0 && (
              <div className="mt-3 rounded-xl bg-white/[0.02] p-3">
                <p className="mb-2 text-xs font-semibold text-ink-faint">Migration notes:</p>
                {notes.map((n, i) => <p key={i} className="mb-1 text-xs text-ink-dim">– {n}</p>)}
              </div>
            )}
          </>
        ) : <Nil />}
      </div>
    </div>
  )
}

/* ─── Anti-patterns tab ─── */
// Function: AntiPatternsTab
function AntiPatternsTab({ analysis }) {
  const issues = analysis?.antipatterns || []

  const SEVERITY_COLOR = {
    hardcoded_credential: 'bg-red-500/15 text-red-300 border-red-500/25',
    sql_concatenation: 'bg-orange-500/15 text-orange-300 border-orange-500/25',
    god_class: 'bg-amber-500/15 text-amber-300 border-amber-500/25',
  }

  return (
    <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm">
      <p className="mb-4 text-sm font-semibold text-ink">
        Anti-patterns Found
        {issues.length > 0 && (
          <span className="ml-2 rounded-full bg-red-500/15 px-2 py-0.5 text-[11px] font-bold text-red-300">{issues.length}</span>
        )}
      </p>
      {issues.length === 0 ? (
        <div className="flex items-center gap-2 rounded-xl border border-emerald-500/25 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          No anti-patterns detected — clean result!
        </div>
      ) : (
        <div className="space-y-2">
          {issues.map((issue, i) => {
            const typeKey = (issue.type || 'unknown').toLowerCase()
            const badgeCls = SEVERITY_COLOR[typeKey] || 'bg-white/10 text-ink-muted border-hairline'
            return (
              <div key={i} className="rounded-xl border border-hairline bg-white/[0.02] p-3">
                <div className="mb-1.5 flex items-center justify-between gap-3">
                  <span className={`rounded-full border px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide ${badgeCls}`}>
                    {typeKey.replace(/_/g, ' ')}
                  </span>
                  {issue.line && <span className="text-xs text-ink-faint">line {issue.line}</span>}
                </div>
                {issue.file && <p className="truncate text-[11px] text-ink-faint">{issue.file}</p>}
                {issue.snippet && (
                  <p className="mt-1.5 truncate rounded-lg bg-black/30 px-2.5 py-1.5 font-mono text-xs text-ink-dim ring-1 ring-hairline">
                    {issue.snippet}
                  </p>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// Function: ValidationDiagnostics
function ValidationDiagnostics({ validation }) {
  const failures = validation?.files || []
  return (
    <div className="rounded-2xl border border-red-500/25 bg-red-500/[0.06] p-4">
      <div className="flex items-start gap-3">
        <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-300" />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-red-200">Strict validation did not pass</p>
          <p className="mt-1 text-xs leading-5 text-ink-muted">
            The generated source is retained for review, but it is not marked ready. Correct the diagnostics below and regenerate before using it.
          </p>
          {failures.map((file, index) => (
            <div key={`${file.path || 'file'}-${index}`} className="mt-3 rounded-xl border border-red-500/20 bg-surface-soft p-3">
              <p className="break-all font-mono text-xs font-semibold text-gold-soft">
                {file.path || 'Generated file'} · {file.language || 'unknown'} · {file.checker || 'validator'} · {file.attempts || 1} attempt(s)
              </p>
              <ul className="mt-2 space-y-1">
                {(file.diagnostics || ['Validation failed without a diagnostic.']).map((diagnostic, diagnosticIndex) => (
                  <li key={diagnosticIndex} className="break-words font-mono text-xs leading-5 text-red-200">• {diagnostic}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ─── Output tab ─── */
// Function: OutputTab
function OutputTab({ job, downloadUrl }) {
  if (!['completed', 'validation_failed'].includes(job.status)) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-hairline bg-surface py-16 text-center shadow-sm">
        <div className="mb-3 h-10 w-10 rounded-full bg-white/[0.06] flex items-center justify-center">
          {job.status === 'running'
            ? <Clock className="h-5 w-5 text-ink-faint" />
            : <XCircle className="h-5 w-5 text-ink-faint" />
          }
        </div>
        <p className="text-sm text-ink-muted">
          {job.status === 'running'
            ? 'Modernized output will appear here once the analysis finishes.'
            : 'The analysis did not complete successfully.'}
        </p>
      </div>
    )
  }

  const singleFileCode = job.output?.__single_file__
  if (singleFileCode) {
    const validationFailed = job.status === 'validation_failed'
    return (
      <div className="space-y-4">
        {validationFailed && <ValidationDiagnostics validation={job.validation} />}
        <div className="flex items-center justify-between rounded-2xl border border-hairline bg-surface px-5 py-4 shadow-sm">
          <div>
            <p className="text-sm font-semibold text-ink">Generated Code</p>
            <p className="mt-0.5 text-xs text-ink-faint">
              Target: {job.target_stack?.replace(/_/g, ' ')} · Single file
            </p>
          </div>
          <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold ${validationFailed ? 'border-red-500/25 bg-red-500/10 text-red-300' : 'border-emerald-500/25 bg-emerald-500/10 text-emerald-300'}`}>
            {validationFailed ? <XCircle className="h-3.5 w-3.5" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
            {validationFailed ? 'Validation failed' : 'Validated'}
          </span>
        </div>
        <SingleFileViewer code={singleFileCode} />
      </div>
    )
  }

  const targets = job.analysis?.modernization_targets
  const validationFailed = job.status === 'validation_failed'
  return (
    <div className="space-y-5">
      {validationFailed && <ValidationDiagnostics validation={job.validation} />}
      <div className="flex flex-col items-center rounded-2xl border border-hairline bg-surface px-8 py-10 text-center shadow-sm">
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gold/15 text-3xl">
          {validationFailed ? '⚠️' : '🎉'}
        </div>
        <h2 className="font-display text-xl font-medium text-ink">
          {validationFailed ? 'Generated output requires review' : 'Modernization Complete!'}
        </h2>
        <p className="mt-2 max-w-sm text-sm text-ink-muted">
          {validationFailed
            ? 'Strict build or semantic acceptance did not pass. You can download the complete diagnostic artifact, including its validation report, but it is not marked production-ready.'
            : <>Your legacy code has been analysed and a modernized{' '}
                <strong className="font-semibold text-ink-dim">{job.target_stack?.replace(/_/g, ' ') || 'target'}</strong>{' '}
                project has been generated.</>}
        </p>
        <a
          href={downloadUrl}
          className={`mt-6 inline-flex items-center gap-2.5 rounded-xl px-6 py-3 text-sm font-semibold transition ${
            validationFailed ? 'bg-amber-400 text-slate-950 hover:bg-amber-300' : 'bg-gold text-bg hover:bg-gold-soft'
          }`}
        >
          <Download className="h-4 w-4" />
          {validationFailed ? 'Download review artifact (.zip)' : 'Download modernized code (.zip)'}
        </a>
      </div>

      {/* Architecture summary */}
      {targets && (
        <div className="rounded-2xl border border-hairline bg-surface p-5 shadow-sm">
          <p className="mb-4 text-sm font-semibold text-ink">Generated Architecture</p>
          <dl className="space-y-2">
            <InfoRow label="Frontend" value={targets.frontend} />
            <InfoRow label="Backend"  value={targets.backend} />
            <InfoRow label="Database" value={targets.database} />
            <InfoRow label="From DB"  value={targets.migration?.from_db} />
            <InfoRow label="To DB"    value={targets.migration?.to_db} />
          </dl>
        </div>
      )}
    </div>
  )
}

/* ─── Single-file code viewer ─── */
// Function: SingleFileViewer
function SingleFileViewer({ code }) {
  const [copied, setCopied] = useState(false)
  const lines = (code || '').split('\n')

  // Function: handleCopy
  const handleCopy = async () => {
    try { await navigator.clipboard.writeText(code || '') }
    catch {
      const ta = document.createElement('textarea')
      ta.value = code || ''
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    setCopied(true)
    setTimeout(() => setCopied(false), 2500)
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-hairline bg-surface">
      <div className="flex items-center justify-between border-b border-hairline bg-surface-soft px-4 py-2.5">
        <div className="flex items-center gap-3">
          <span className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-500/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/60" />
          <span className="ml-2 text-xs text-ink-faint">Generated Code</span>
          <span className="text-ink-faint/40">·</span>
          <span className="text-xs text-ink-faint">{lines.length.toLocaleString()} lines</span>
          <span className="text-ink-faint/40">·</span>
          <span className="text-xs text-ink-faint">{(code || '').length.toLocaleString()} chars</span>
        </div>
        <button
          onClick={handleCopy}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1 text-xs font-medium transition ${
            copied
              ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300'
              : 'border-hairline-strong bg-white/[0.04] text-ink-muted hover:border-white/25 hover:text-ink'
          }`}
        >
          {copied ? '✓ Copied!' : '⧉ Copy'}
        </button>
      </div>
      <div className="flex" style={{ maxHeight: '72vh', overflow: 'hidden' }}>
        <div
          className="shrink-0 select-none overflow-hidden px-3 py-4 text-right text-xs leading-5 font-mono text-ink-faint"
          style={{ minWidth: '3.5rem', background: '#fafafa' }}
        >
          {lines.map((_, i) => <div key={i}>{i + 1}</div>)}
        </div>
        <textarea
          readOnly
          value={code || ''}
          spellCheck={false}
          className="flex-1 overflow-auto py-4 pl-4 pr-6 font-mono text-xs leading-5 focus:outline-none"
          style={{
            background: '#ffffff',
            color: '#242424',
            minHeight: '320px',
            resize: 'none',
          }}
        />
      </div>
    </div>
  )
}

/* ─── Shared helpers ─── */
// Function: InfoRow
function InfoRow({ label, value }) {
  return (
    <div className="flex items-start gap-3">
      <dt className="w-28 shrink-0 pt-0.5 text-xs text-ink-faint">{label}</dt>
      <dd className="text-xs text-ink-dim">{value || <span className="text-ink-faint/60">—</span>}</dd>
    </div>
  )
}

// Function: Nil
function Nil() {
  return <p className="text-sm text-ink-faint">Not applicable</p>
}
