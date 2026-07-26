// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (Dashboard.jsx)
// Date: 2025-12-27
// ---------------------------------------------------------------------------
import { useEffect, useState, useCallback } from 'react'
import { getDashboardStats, getRecentActivity, exportPlacementsCSV } from '../api'

// Function: StatCard
function StatCard({ value, label, sub, colorClass, icon }) {
  return (
    <div className={`rounded-2xl border p-5 flex items-start gap-4 ${colorClass}`}>
      <div className="p-2.5 rounded-xl bg-white/60 flex-shrink-0">{icon}</div>
      <div>
        <p className="text-3xl font-extrabold leading-none">{value ?? '—'}</p>
        <p className="text-sm font-semibold mt-1">{label}</p>
        {sub && <p className="text-xs opacity-70 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

// Function: OccupancyBar
function OccupancyBar({ pct }) {
  const color = pct >= 80 ? 'bg-red-400' : pct >= 50 ? 'bg-yellow-400' : 'bg-green-400'
  return (
    <div className="mt-4">
      <div className="flex justify-between text-xs font-medium text-gray-500 mb-1">
        <span>Rack Occupancy</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-gray-100 overflow-hidden">
        <div className={`h-2 rounded-full transition-all duration-700 ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

// Function: ActivityRow
function ActivityRow({ item, index }) {
  const isPlaced = item.status === 'Placed'
  const ts = new Date(isPlaced ? item.placed_at : item.fetched_at ?? item.placed_at)
  const timeStr = ts.toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
  return (
    <tr className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
      <td className="px-4 py-2.5">
        <span className={`inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full ${
          isPlaced ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-600'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${isPlaced ? 'bg-green-500' : 'bg-orange-500'}`} />
          {item.status}
        </span>
      </td>
      <td className="px-4 py-2.5 text-sm font-medium text-gray-800">{item.chemical?.name}</td>
      <td className="px-4 py-2.5 text-xs font-mono text-gray-500">{item.chemical?.barcode}</td>
      <td className="px-4 py-2.5 text-xs font-mono text-blue-600">{item.rack?.barcode}</td>
      <td className="px-4 py-2.5 text-xs text-gray-500">{timeStr}</td>
    </tr>
  )
}

// Function: Dashboard
export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(() => {
    setLoading(true)
    Promise.all([getDashboardStats(), getRecentActivity(30)])
      .then(([sRes, aRes]) => {
        setStats(sRes.data)
        setActivity(aRes.data)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-gray-400">
        <svg className="animate-spin w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        Loading dashboard…
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-800">Dashboard</h2>
          <p className="text-sm text-gray-500 mt-0.5">Live system overview</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={load}
            className="flex items-center gap-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          <button
            onClick={() => exportPlacementsCSV()}
            className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export CSV
          </button>
        </div>
      </div>

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          value={stats?.total_chemicals}
          label="Chemicals in Catalog"
          colorClass="bg-blue-50 border-blue-200 text-blue-800"
          icon={<svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>}
        />
        <StatCard
          value={stats?.placed}
          label="Currently Placed"
          sub={`across ${stats?.occupied_racks} racks`}
          colorClass="bg-green-50 border-green-200 text-green-800"
          icon={<svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
        />
        <StatCard
          value={stats?.fetched}
          label="Total Fetched"
          colorClass="bg-orange-50 border-orange-200 text-orange-800"
          icon={<svg className="w-6 h-6 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" /></svg>}
        />
        <StatCard
          value={stats ? `${stats.total_racks - stats.occupied_racks}` : '—'}
          label="Empty Racks"
          sub={`${stats?.total_racks} total racks`}
          colorClass="bg-slate-50 border-slate-200 text-slate-700"
          icon={<svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>}
        />
      </div>

      {/* Occupancy bar */}
      {stats && <OccupancyBar pct={stats.rack_occupancy_pct} />}

      {/* ── Recent Activity ── */}
      <div>
        <h3 className="text-base font-bold text-gray-700 mb-3">Recent Activity</h3>
        {activity.length === 0 ? (
          <p className="text-gray-400 text-sm italic py-6 text-center">
            No activity yet — place a chemical to get started.
          </p>
        ) : (
          <div className="rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  {['Status', 'Chemical', 'Barcode', 'Rack', 'Time'].map((h) => (
                    <th key={h} className="text-left px-4 py-2.5 text-xs font-bold uppercase tracking-wide text-gray-400">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activity.map((item, i) => (
                  <ActivityRow key={item.id} item={item} index={i} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
