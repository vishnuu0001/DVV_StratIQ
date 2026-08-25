// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/pages (JobsPage.jsx)
// Date: 2026-02-07
// ---------------------------------------------------------------------------
import { CheckCircle2, Clock, PlusCircle, Trash2, XCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'
import { deleteJob, listJobs } from '../api/client.js'
import Layout from '../components/Layout.jsx'

const STATUS_CONFIG = {
  running: {
    label: 'Running',
    icon: Clock,
    badge: 'border-gold/30 bg-gold/10 text-gold-soft',
    dot: 'bg-gold animate-pulse',
    bar: 'bg-gold',
  },
  completed: {
    label: 'Completed',
    icon: CheckCircle2,
    badge: 'border-emerald-500/25 bg-emerald-500/10 text-emerald-300',
    dot: 'bg-emerald-400',
    bar: 'bg-emerald-400',
  },
  failed: {
    label: 'Failed',
    icon: XCircle,
    badge: 'border-red-500/25 bg-red-500/10 text-red-300',
    dot: 'bg-red-400',
    bar: 'bg-red-400',
  },
}

const PAGE_SIZES = [10, 20, 50, 100]

// Function: PaginationBar
function PaginationBar({ page, totalPages, pageSize, onPage, onPageSize, total }) {
  const start = total === 0 ? 0 : (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)
  const range = []
  for (let p = Math.max(1, page - 2); p <= Math.min(totalPages, page + 2); p++) range.push(p)

  return (
    <div className="mt-4 flex items-center justify-between text-xs text-ink-muted">
      <div className="flex items-center gap-2">
        <span>{total > 0 ? `${start}–${end} of ${total}` : '0 jobs'}</span>
        <span className="text-ink-faint">·</span>
        <span>Per page:</span>
        <select
          value={pageSize}
          onChange={(e) => { onPageSize(Number(e.target.value)); onPage(1) }}
          className="rounded-lg border border-hairline bg-surface px-2 py-1 text-xs text-ink-dim outline-none"
        >
          {PAGE_SIZES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div className="flex items-center gap-0.5">
        {[
          { label: '«', action: () => onPage(1), disabled: page === 1 },
          { label: '‹', action: () => onPage(page - 1), disabled: page === 1 },
          ...range.map((p) => ({ label: String(p), action: () => onPage(p), active: p === page })),
          { label: '›', action: () => onPage(page + 1), disabled: page === totalPages },
          { label: '»', action: () => onPage(totalPages), disabled: page === totalPages },
        ].map((btn, i) => (
          <button
            key={i}
            onClick={btn.action}
            disabled={btn.disabled}
            className={`min-w-[1.75rem] rounded-lg px-2 py-1 transition ${
              btn.active
                ? 'bg-gold text-bg font-semibold'
                : 'text-ink-muted hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-30'
            }`}
          >
            {btn.label}
          </button>
        ))}
      </div>
    </div>
  )
}

/** A job's identity line: folder path for folder-based jobs, or the user's own prompt for prompt-based ones. */
// Function: JobIdentity
function JobIdentity({ job }) {
  if (job.folder_path) {
    return <p className="truncate font-mono text-sm font-medium text-ink-dim">{job.folder_path}</p>
  }
  if (job.prompt) {
    return <p className="line-clamp-1 text-sm font-medium text-ink-dim">{job.prompt}</p>
  }
  return <p className="truncate text-sm font-medium text-ink-faint">(prompt-based generation)</p>
}

// Function: JobsPage
export default function JobsPage() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  // Function: fetchJobs
  const fetchJobs = async () => {
    try {
      const data = await listJobs()
      setJobs(data.jobs || [])
    } catch {
      toast.error('Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
    const id = setInterval(fetchJobs, 5000)
    return () => clearInterval(id)
  }, [])

  // Function: handleDelete
  const handleDelete = async (jobId) => {
    if (!window.confirm('Remove this job from the list?')) return
    try {
      await deleteJob(jobId)
      setJobs((current) => current.filter((j) => j.job_id !== jobId))
      toast.success('Job removed')
    } catch {
      toast.error('Failed to remove job')
    }
  }

  const reversed = [...jobs].reverse()
  const totalPages = Math.max(1, Math.ceil(reversed.length / pageSize))
  const paged = reversed.slice((page - 1) * pageSize, page * pageSize)

  return (
    <Layout>
      <main className="mx-auto max-w-4xl px-6 py-8 lg:py-10">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="font-display text-2xl font-medium text-ink">Analysis Jobs</h1>
            {!loading && (
              <p className="mt-0.5 text-sm text-ink-muted">
                {jobs.length} total job{jobs.length !== 1 ? 's' : ''}
                {jobs.filter((j) => j.status === 'running').length > 0 && (
                  <span className="ml-2 inline-flex items-center gap-1 text-gold-soft">
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-gold" />
                    {jobs.filter((j) => j.status === 'running').length} running
                  </span>
                )}
              </p>
            )}
          </div>
          <Link
            to="/analyze"
            className="inline-flex items-center gap-2 rounded-xl bg-gold px-4 py-2.5 text-sm font-semibold text-bg transition hover:bg-gold-soft"
          >
            <PlusCircle className="h-4 w-4" />
            New Analysis
          </Link>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-hairline border-t-gold" />
          </div>
        ) : jobs.length > 0 ? (
          <>
            <div className="space-y-2.5">
              {paged.map((job) => {
                const cfg = STATUS_CONFIG[job.status] || STATUS_CONFIG.running
                const Icon = cfg.icon
                const isActive = !['completed', 'validation_failed', 'failed'].includes(job.status)
                return (
                  <div
                    key={job.job_id}
                    className="group flex items-center gap-4 rounded-2xl border border-hairline bg-surface px-5 py-4 shadow-sm transition-all hover:border-hairline-strong hover:bg-surface-hover"
                  >
                    {/* Status dot */}
                    <div className={`h-2.5 w-2.5 shrink-0 rounded-full ${cfg.dot}`} />

                    {/* Main info */}
                    <div className="min-w-0 flex-1">
                      <JobIdentity job={job} />
                      <div className="mt-1.5 flex flex-wrap items-center gap-3">
                        {/* Status badge */}
                        <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-semibold ${cfg.badge}`}>
                          <Icon className="h-3 w-3" />
                          {cfg.label}
                        </span>
                        {/* Progress */}
                        {job.status === 'running' && (
                          <span className="text-xs text-ink-muted">{job.progress}% complete</span>
                        )}
                        {/* Timestamp */}
                        <span className="text-xs text-ink-faint">
                          {new Date(job.created_at).toLocaleString()}
                        </span>
                      </div>
                      {/* Progress bar */}
                      {job.status === 'running' && (
                        <div className="mt-2.5 h-1 overflow-hidden rounded-full bg-white/[0.06]">
                          <div
                            style={{ width: `${job.progress}%` }}
                            className={`h-full rounded-full transition-all duration-700 ${cfg.bar}`}
                          />
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex shrink-0 items-center gap-2">
                      <Link
                        to={`/jobs/${job.job_id}`}
                        className="rounded-xl border border-hairline bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-ink-dim shadow-sm transition hover:bg-white/[0.07] hover:text-ink"
                      >
                        {job.status === 'running' ? 'View Progress' : 'View Report'}
                      </Link>
                      <button
                        onClick={() => handleDelete(job.job_id)}
                        disabled={isActive}
                        className="flex h-8 w-8 items-center justify-center rounded-xl text-ink-faint transition hover:bg-red-500/10 hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-ink-faint"
                        title={isActive ? 'Running jobs cannot be removed' : 'Remove job'}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>

            {totalPages > 1 && (
              <PaginationBar
                page={page}
                totalPages={totalPages}
                pageSize={pageSize}
                onPage={setPage}
                onPageSize={(s) => { setPageSize(s); setPage(1) }}
                total={reversed.length}
              />
            )}
          </>
        ) : null}
      </main>
    </Layout>
  )
}
