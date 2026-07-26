// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (FeedbackPage.jsx)
// Date: 2025-10-17
// ---------------------------------------------------------------------------
import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { BarChart2, RefreshCw, ThumbsUp, ThumbsDown, Minus } from 'lucide-react'
import { getFeedbackStats, getFeedbackAll } from '../services/api.js'

const RATING_ICONS = {
  1: <ThumbsDown size={14} className="text-red-500" />,
  2: <Minus size={14} className="text-yellow-500" />,
  3: <ThumbsUp size={14} className="text-green-500" />,
}

const RATING_LABELS = { 1: 'Not helpful', 2: 'Neutral', 3: 'Helpful' }

// Function: FeedbackPage
export default function FeedbackPage() {
  const [stats, setStats] = useState(null)
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)

  // Function: load
  const load = async () => {
    setLoading(true)
    try {
      const [s, r] = await Promise.all([getFeedbackStats(), getFeedbackAll()])
      setStats(s.data)
      setRecords(r.data.feedback || [])
    } catch (err) {
      toast.error(err.message)
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  // Function: pct
  const pct = (n) => stats?.total ? Math.round((n / stats.total) * 100) : 0

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <header className="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b bg-white">
        <div>
          <h1 className="font-semibold text-gray-900">Feedback & Ratings</h1>
          <p className="text-xs text-gray-500">User ratings help rank and improve knowledge quality</p>
        </div>
        <button onClick={load} disabled={loading} className="btn-secondary text-xs">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </header>

      <div className="flex-1 px-6 py-6 space-y-6 max-w-4xl">
        {/* Stats cards */}
        {stats && (
          <div className="grid grid-cols-3 gap-4">
            <div className="card text-center">
              <BarChart2 size={22} className="mx-auto text-brand-500 mb-1" />
              <p className="text-2xl font-bold">{stats.total}</p>
              <p className="text-xs text-gray-500">Total Feedback</p>
            </div>
            <div className="card text-center">
              <p className="text-2xl font-bold">{stats.average_rating?.toFixed(1) ?? '—'}</p>
              <p className="text-xs text-gray-500">Average Rating (1–3)</p>
            </div>
            <div className="card space-y-1.5">
              {[3, 2, 1].map((r) => {
                const count = stats.rating_distribution?.[String(r)] || 0
                return (
                  <div key={r} className="flex items-center gap-2 text-xs">
                    {RATING_ICONS[r]}
                    <div className="flex-1 bg-gray-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${r === 3 ? 'bg-green-400' : r === 1 ? 'bg-red-400' : 'bg-yellow-300'}`}
                        style={{ width: `${pct(count)}%` }}
                      />
                    </div>
                    <span className="w-6 text-right text-gray-500">{count}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Records table */}
        <div className="card space-y-3">
          <h2 className="font-medium text-sm text-gray-700">Recent Feedback</h2>
          {records.length === 0 ? (
            <p className="text-sm text-gray-400">No feedback collected yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left border-b text-gray-500">
                    <th className="pb-2 pr-4 font-medium">Rating</th>
                    <th className="pb-2 pr-4 font-medium">Question</th>
                    <th className="pb-2 pr-4 font-medium">Comment</th>
                    <th className="pb-2 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {records.map((r) => (
                    <tr key={r.feedback_id} className="hover:bg-gray-50">
                      <td className="py-2 pr-4">
                        <div className="flex items-center gap-1">
                          {RATING_ICONS[r.rating]}
                          <span className={r.rating === 3 ? 'text-green-600' : r.rating === 1 ? 'text-red-500' : 'text-yellow-600'}>
                            {RATING_LABELS[r.rating]}
                          </span>
                        </div>
                      </td>
                      <td className="py-2 pr-4 max-w-xs truncate text-gray-700">{r.question}</td>
                      <td className="py-2 pr-4 max-w-xs truncate text-gray-400">{r.comment || '—'}</td>
                      <td className="py-2 text-gray-400 whitespace-nowrap">
                        {new Date(r.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
