// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/components (DateRangeFilter.jsx)
// Date: 2025-12-22
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { Calendar, ChevronDown, X } from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'

const PRESETS = [
  { label: 'Last 7 days',  id: '7d',   days: 7 },
  { label: 'Last 30 days', id: '30d',  days: 30 },
  { label: 'Last 90 days', id: '90d',  days: 90 },
  { label: 'Last 6 months', id: '6m',  days: 180 },
  { label: 'Last year',    id: '1y',   days: 365 },
  { label: 'All Time',     id: 'all',  days: null },
]

// Function: toISODate
function toISODate(d) {
  return d.toISOString().slice(0, 10)
}

// Function: presetToRange
function presetToRange(preset) {
  if (!preset.days) return { startDate: null, endDate: null }
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - preset.days)
  return { startDate: toISODate(start), endDate: toISODate(end) }
}

// Function: formatDateRange
function formatDateRange(dateRange) {
  if (!dateRange.startDate && !dateRange.endDate) return 'All Time'
  // Function: fmt
  const fmt = (s) => new Date(s + 'T00:00:00').toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
  if (dateRange.startDate && dateRange.endDate) return `${fmt(dateRange.startDate)} — ${fmt(dateRange.endDate)}`
  if (dateRange.startDate) return `From ${fmt(dateRange.startDate)}`
  return `Until ${fmt(dateRange.endDate)}`
}

// Function: DateRangeFilter
export default function DateRangeFilter() {
  const { dateRange, setDateRange } = useDashboard()
  const [open, setOpen] = useState(false)
  const [customStart, setCustomStart] = useState('')
  const [customEnd, setCustomEnd] = useState('')

  // Function: applyPreset
  function applyPreset(preset) {
    const range = presetToRange(preset)
    setDateRange({ ...range, preset: preset.id })
    setOpen(false)
  }

  // Function: applyCustom
  function applyCustom() {
    if (!customStart && !customEnd) return
    setDateRange({ startDate: customStart || null, endDate: customEnd || null, preset: 'custom' })
    setOpen(false)
  }

  // Function: clearFilter
  function clearFilter() {
    setDateRange({ startDate: null, endDate: null, preset: 'all' })
    setCustomStart('')
    setCustomEnd('')
    setOpen(false)
  }

  const isFiltered = dateRange.startDate || dateRange.endDate
  const activePreset = PRESETS.find(p => p.id === dateRange.preset)

  return (
    <div className="relative">
      {/* Trigger button */}
      <button
        onClick={() => setOpen(v => !v)}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
          isFiltered
            ? 'bg-cyan-500/20 border-cyan-500/40 text-accent-cyan shadow-glow-sm'
            : 'bg-slate-700/30 border-slate-600/30 text-slate-300 hover:bg-slate-700/50'
        }`}
      >
        <Calendar className="w-3.5 h-3.5 shrink-0" />
        <span className="hidden sm:inline max-w-[180px] truncate">
          {isFiltered ? formatDateRange(dateRange) : 'Date Range'}
        </span>
        {isFiltered ? (
          <button
            onClick={(e) => { e.stopPropagation(); clearFilter() }}
            className="ml-1 text-slate-400 hover:text-slate-200"
          >
            <X className="w-3 h-3" />
          </button>
        ) : (
          <ChevronDown className={`w-3 h-3 transition-transform ${open ? 'rotate-180' : ''}`} />
        )}
      </button>

      {/* Dropdown panel */}
      {open && (
        <>
          {/* backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-2 z-50 w-72 rounded-xl border border-slate-600/30 bg-slate-800/95 backdrop-blur shadow-elevation-3 p-3">

            {/* Quick presets */}
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Quick Select</p>
            <div className="grid grid-cols-2 gap-1 mb-3">
              {PRESETS.map(preset => (
                <button
                  key={preset.id}
                  onClick={() => applyPreset(preset)}
                  className={`text-left px-2.5 py-2 rounded-lg text-xs font-medium transition-all ${
                    dateRange.preset === preset.id
                      ? 'bg-cyan-500/20 text-accent-cyan border border-cyan-500/30'
                      : 'text-slate-300 hover:bg-slate-700/50 border border-transparent'
                  }`}
                >
                  {preset.label}
                </button>
              ))}
            </div>

            {/* Custom range */}
            <div className="border-t border-slate-700/40 pt-3">
              <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Custom Range</p>
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <label className="text-xs text-slate-400 w-10 shrink-0">From</label>
                  <input
                    type="date"
                    value={customStart}
                    onChange={e => setCustomStart(e.target.value)}
                    max={customEnd || undefined}
                    className="flex-1 bg-slate-700/50 border border-slate-600/40 rounded-lg px-2 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <label className="text-xs text-slate-400 w-10 shrink-0">To</label>
                  <input
                    type="date"
                    value={customEnd}
                    onChange={e => setCustomEnd(e.target.value)}
                    min={customStart || undefined}
                    className="flex-1 bg-slate-700/50 border border-slate-600/40 rounded-lg px-2 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50"
                  />
                </div>
                <button
                  onClick={applyCustom}
                  disabled={!customStart && !customEnd}
                  className="w-full mt-1 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500/20 text-accent-cyan border border-cyan-500/30 hover:bg-cyan-500/30 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                >
                  Apply Range
                </button>
              </div>
            </div>

            {/* Clear */}
            {isFiltered && (
              <button
                onClick={clearFilter}
                className="w-full mt-2 py-1.5 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-700/30 transition-all"
              >
                Clear Filter
              </button>
            )}
          </div>
        </>
      )}
    </div>
  )
}
