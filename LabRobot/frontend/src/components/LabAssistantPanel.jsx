// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (LabAssistantPanel.jsx)
// Date: 2026-03-22
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback } from 'react'
import { getScientists, getPlacements } from '../api'
import { PICKUP_SUCCESS_EVENT } from '../pickupMessaging'

const SCI_THEME = [
  {
    card: 'bg-blue-50 border-blue-200',
    icon: 'bg-blue-600',
    badge: 'bg-blue-100 text-blue-800',
    rackAccent: 'text-blue-600',
  },
  {
    card: 'bg-emerald-50 border-emerald-200',
    icon: 'bg-emerald-600',
    badge: 'bg-emerald-100 text-emerald-800',
    rackAccent: 'text-emerald-600',
  },
  {
    card: 'bg-violet-50 border-violet-200',
    icon: 'bg-violet-600',
    badge: 'bg-violet-100 text-violet-800',
    rackAccent: 'text-violet-600',
  },
]

const CATEGORY_THEME = {
  acid: 'from-rose-100 to-red-100 border-rose-200',
  base: 'from-indigo-100 to-blue-100 border-indigo-200',
  solvent: 'from-amber-100 to-yellow-100 border-amber-200',
  oxidizer: 'from-fuchsia-100 to-pink-100 border-fuchsia-200',
  hydrocarbon: 'from-emerald-100 to-lime-100 border-emerald-200',
  neutral: 'from-cyan-100 to-sky-100 border-cyan-200',
}

// Function: inferChemicalCategory
function inferChemicalCategory(placement) {
  const raw = `${placement?.chemical?.name || ''} ${placement?.chemical?.description || ''}`.toLowerCase()
  if (raw.includes('acid')) return 'acid'
  if (raw.includes('hydroxide') || raw.includes('ammonia') || raw.includes('base')) return 'base'
  if (raw.includes('solvent') || raw.includes('acetone') || raw.includes('alcohol') || raw.includes('ethanol') || raw.includes('methanol')) return 'solvent'
  if (raw.includes('peroxide') || raw.includes('oxidizing')) return 'oxidizer'
  if (raw.includes('benzene') || raw.includes('hydrocarbon')) return 'hydrocarbon'
  return 'neutral'
}

// Function: placedCount
function placedCount(slots) {
  return [1, 2, 3].filter((slot) => !!slots[slot]).length
}

// Function: LabAssistantPanel
export default function LabAssistantPanel({ onDispatch }) {
  const [scientists, setScientists] = useState([])
  const [placements, setPlacements] = useState([])
  const [filterScientistId, setFilterScientistId] = useState('')
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('inventory') // 'inventory' | 'fetched'

  const loadPlacements = useCallback(async (scientistId) => {
    try {
      const res = await getPlacements(scientistId || null)
      setPlacements(res.data)
    } catch (err) {
      console.error('Failed to load placements', err)
    }
  }, [])

  useEffect(() => {
    getScientists()
      .then((res) => setScientists(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    loadPlacements(filterScientistId)
  }, [filterScientistId, loadPlacements])

  useEffect(() => {
    // Function: handlePickupSuccess
    const handlePickupSuccess = () => loadPlacements(filterScientistId)
    document.addEventListener(PICKUP_SUCCESS_EVENT, handlePickupSuccess)
    return () => document.removeEventListener(PICKUP_SUCCESS_EVENT, handlePickupSuccess)
  }, [filterScientistId, loadPlacements])

  const visibleScientists = scientists.filter(
    (s) => !filterScientistId || s.id === Number(filterScientistId)
  )

  const placedItems   = placements.filter((p) => p.status === 'Placed')
  const fetchedItems  = placements.filter((p) => p.status === 'Fetched')
  const totalSlots = scientists.reduce((sum, sci) => sum + ((sci.racks?.length || 0) * 3), 0)
  const usedSlots = placedItems.length
  const availableSlots = Math.max(0, totalSlots - usedSlots)
  const utilizationPct = totalSlots > 0 ? Math.round((usedSlots / totalSlots) * 100) : 0

  // Build rack → scientist lookup for the fetched dashboard
  const rackToScientist = {}
  scientists.forEach((s) => s.racks?.forEach((r) => { rackToScientist[r.id] = s }))

  const riskAlerts = []
  if (utilizationPct >= 85) {
    riskAlerts.push(`Capacity alert: utilization is ${utilizationPct}%. Reserve emergency slots before next inbound batch.`)
  }
  if (fetchedItems.length > placedItems.length && fetchedItems.length > 3) {
    riskAlerts.push('Dispatch skew detected: fetched volume exceeds placed inventory. Validate replenishment workflow.')
  }
  const lowFreeScientists = scientists.filter((s) => {
    const placed = placements.filter((p) => p.status === 'Placed' && p.scientist_id === s.id).length
    const cap = (s.racks?.length || 0) * 3
    return cap > 0 && (cap - placed) <= 2
  })
  if (lowFreeScientists.length > 0) {
    riskAlerts.push(`Low free-slot labs: ${lowFreeScientists.map((s) => s.code).join(', ')}`)
  }

  // Function: placementsByRack
  const placementsByRack = (rackId) => {
    const slots = { 1: null, 2: null, 3: null }
    placements
      .filter((p) => p.rack_id === rackId && p.status === 'Placed')
      .forEach((p) => {
        const slot = Number.isInteger(p.compartment) ? p.compartment : 1
        if ([1, 2, 3].includes(slot)) {
          slots[slot] = p
        }
      })
    return slots
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-gray-400">
        <svg className="animate-spin w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        Loading inventory…
      </div>
    )
  }

  return (
    <div>
      {/* ── Toolbar ──────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">Lab Assistant — Chemical Inventory</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            {placedItems.length} placed · {fetchedItems.length} fetched
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium text-gray-600">Scientist:</label>
          <select
            value={filterScientistId}
            onChange={(e) => setFilterScientistId(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Scientists</option>
            {scientists.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <button
            onClick={() => loadPlacements(filterScientistId)}
            className="flex items-center gap-1.5 bg-slate-700 hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-5">
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">Used Slots</p>
          <p className="text-2xl font-bold text-slate-800">{usedSlots}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">Available Slots</p>
          <p className="text-2xl font-bold text-slate-800">{availableSlots}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">Utilization</p>
          <p className="text-2xl font-bold text-slate-800">{utilizationPct}%</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-3">
          <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">Fetched Ledger</p>
          <p className="text-2xl font-bold text-slate-800">{fetchedItems.length}</p>
        </div>
      </div>

      <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 mb-6">
        <p className="text-xs font-semibold uppercase tracking-wide text-amber-700 mb-2">Operations Alerts</p>
        {riskAlerts.length === 0 ? (
          <p className="text-sm text-emerald-700 font-medium">No active risks. Operations are within defined thresholds.</p>
        ) : (
          <div className="space-y-1.5">
            {riskAlerts.map((alert) => (
              <p key={alert} className="text-sm text-amber-900">- {alert}</p>
            ))}
          </div>
        )}
      </div>

      {/* ── Tab switcher ─────────────────────────────────────────────── */}
      <div className="flex gap-1 bg-slate-200/80 rounded-xl p-1 mb-6 w-fit border border-slate-300/70">
        <button
          onClick={() => setActiveTab('inventory')}
          className={`px-5 py-2 rounded-lg text-sm font-semibold transition-colors ${
            activeTab === 'inventory'
              ? 'bg-white text-blue-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Rack Inventory
          {placedItems.length > 0 && (
            <span className="ml-2 bg-blue-100 text-blue-700 text-xs px-1.5 py-0.5 rounded-full font-bold">
              {placedItems.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('fetched')}
          className={`px-5 py-2 rounded-lg text-sm font-semibold transition-colors ${
            activeTab === 'fetched'
              ? 'bg-white text-orange-600 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Fetched Items
          {fetchedItems.length > 0 && (
            <span className="ml-2 bg-orange-100 text-orange-600 text-xs px-1.5 py-0.5 rounded-full font-bold">
              {fetchedItems.length}
            </span>
          )}
        </button>
      </div>

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* TAB 1 — Rack Inventory (Placed chemicals only)               */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {activeTab === 'inventory' && (
        <>
          {visibleScientists.map((scientist, idx) => {
            const theme = SCI_THEME[idx % SCI_THEME.length]
            const anyPlaced = scientist.racks.some(
              (r) => placedCount(placementsByRack(r.id)) > 0
            )
            const scientistPlaced = scientist.racks.reduce((sum, rack) => sum + placedCount(placementsByRack(rack.id)), 0)
            const scientistCapacity = scientist.racks.length * 9
            return (
              <div key={scientist.id} className={`mb-8 rounded-2xl border ${theme.card} p-4 md:p-5 shadow-sm relative overflow-hidden`}>
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-slate-900/90" />

                <div className="flex flex-wrap items-center justify-between gap-3 mb-4 mt-1">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl ${theme.icon} text-white font-bold text-lg flex items-center justify-center`}>
                      {scientist.name.charAt(scientist.name.lastIndexOf(' ') + 1)}
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-gray-800 leading-tight">{scientist.name}</h3>
                      <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded-full ${theme.badge}`}>
                        {scientist.code}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold px-2 py-1 rounded-md border border-slate-300 bg-white/70 text-slate-700">
                      {scientistPlaced}/{scientistCapacity} slots used
                    </span>
                    {!anyPlaced && (
                      <span className="text-xs text-gray-400 italic">No chemicals placed</span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {scientist.racks.map((rack) => {
                    const rackSlots = placementsByRack(rack.id)
                    const count = placedCount(rackSlots)
                    return (
                      <div key={rack.id} className="rounded-lg border border-slate-300/80 bg-[#d7e4e8] shadow-[inset_0_1px_0_rgba(255,255,255,0.65)] overflow-hidden p-1.5">
                        <div className="h-1.5 rounded-sm bg-slate-900 mb-1.5" />
                        <div className="bg-white/70 border border-slate-300 rounded-md px-2 py-1.5 flex items-center justify-between mb-1.5">
                          <div>
                            <p className="text-sm font-bold text-gray-700">{rack.name}</p>
                            <p className={`text-xs font-mono ${theme.rackAccent}`}>{rack.barcode}</p>
                          </div>
                          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                            count > 0 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-400'
                          }`}>
                            {count}/3 placed
                          </span>
                        </div>

                        <div className="space-y-1.5">
                          {[1, 2, 3].map((slot) => {
                            const placement = rackSlots[slot]
                            if (!placement) {
                              return (
                                <div key={slot} className="flex items-center justify-between rounded-md px-2 py-1.5 bg-white/80 border border-slate-300">
                                  <p className="text-xs font-semibold text-slate-600">Compartment C{slot}</p>
                                  <p className="text-xs text-gray-400 italic">Empty</p>
                                </div>
                              )
                            }
                            const category = inferChemicalCategory(placement)
                            const tone = CATEGORY_THEME[category]
                            return (
                              <div
                                key={slot}
                                className={`flex items-center gap-2 rounded-md px-2 py-1.5 bg-gradient-to-r ${tone}`}
                              >
                                <div className="flex-1 min-w-0">
                                  <p className="text-xs font-semibold text-blue-700">Compartment C{slot}</p>
                                  <p className="text-sm font-semibold text-gray-800 truncate">
                                    {placement.chemical.name}
                                  </p>
                                  <p className="text-xs font-mono text-gray-400">{placement.chemical.barcode}</p>
                                  {placement.chemical.description && (
                                    <p className="text-xs text-gray-400 truncate">{placement.chemical.description}</p>
                                  )}
                                </div>
                                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                                  <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                                    Placed
                                  </span>
                                  <button
                                    onClick={() =>
                                      onDispatch?.({
                                        placementId: placement.id,
                                        rackId: placement.rack_id,
                                        barcode: placement.chemical.barcode,
                                        itemLabel: placement.chemical.name,
                                      })
                                    }
                                    className="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-amber-100 text-amber-700 border border-amber-200 text-center hover:bg-amber-200 transition-colors"
                                  >
                                    Dispatch in 3D View
                                  </button>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}

          {placedItems.length === 0 && (
            <div className="text-center py-20 text-gray-300">
              <svg className="w-20 h-20 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <p className="text-lg text-gray-400">No chemicals placed yet</p>
              <p className="text-sm text-gray-300 mt-1">Switch to the Scientist View to place chemicals into racks.</p>
            </div>
          )}
        </>
      )}

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* TAB 2 — Fetched Items Dashboard                              */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {activeTab === 'fetched' && (
        <>
          {fetchedItems.length === 0 ? (
            <div className="text-center py-20 text-gray-300">
              <svg className="w-20 h-20 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
              <p className="text-lg text-gray-400">No chemicals fetched yet</p>
              <p className="text-sm text-gray-300 mt-1">Use the 3D Rack View to send a pickup message and wait for robot success confirmation.</p>
            </div>
          ) : (
            <>
              {/* Summary stats bar */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-orange-50 border border-orange-100 rounded-xl px-5 py-4">
                  <p className="text-2xl font-bold text-orange-600">{fetchedItems.length}</p>
                  <p className="text-sm text-gray-500 mt-0.5">Total Fetched</p>
                </div>
                <div className="bg-blue-50 border border-blue-100 rounded-xl px-5 py-4">
                  <p className="text-2xl font-bold text-blue-600">
                    {new Set(fetchedItems.map(p => rackToScientist[p.rack_id]?.id)).size}
                  </p>
                  <p className="text-sm text-gray-500 mt-0.5">Scientists Involved</p>
                </div>
                <div className="bg-green-50 border border-green-100 rounded-xl px-5 py-4">
                  <p className="text-2xl font-bold text-green-600">{placedItems.length}</p>
                  <p className="text-sm text-gray-500 mt-0.5">Still in Racks</p>
                </div>
              </div>

              {/* Fetched items table */}
              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200">
                      <th className="text-left px-5 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide">#</th>
                      <th className="text-left px-5 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide">Chemical Name</th>
                      <th className="text-left px-5 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide">Rack</th>
                      <th className="text-left px-5 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide">Scientist</th>
                      <th className="text-left px-5 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide">Date Fetched</th>
                      <th className="text-left px-5 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fetchedItems
                      .slice()
                      .sort((a, b) => new Date(b.fetched_at) - new Date(a.fetched_at))
                      .map((p, i) => {
                        const sci = rackToScientist[p.rack_id]
                        const fetchedDate = p.fetched_at ? new Date(p.fetched_at) : null
                        return (
                          <tr key={p.id} className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${i % 2 === 0 ? '' : 'bg-gray-50/50'}`}>
                            <td className="px-5 py-3 text-gray-400 font-mono text-xs">{i + 1}</td>
                            <td className="px-5 py-3">
                              <p className="font-semibold text-gray-800">{p.chemical.name}</p>
                              <p className="text-xs font-mono text-gray-400">{p.chemical.barcode}</p>
                            </td>
                            <td className="px-5 py-3">
                              <p className="font-semibold text-gray-700">{p.rack?.name ?? `Rack #${p.rack_id}`}</p>
                              <p className="text-xs font-mono text-gray-400">{p.rack?.barcode ?? ''}</p>
                            </td>
                            <td className="px-5 py-3">
                              {sci ? (
                                <>
                                  <p className="font-semibold text-gray-700">{sci.name}</p>
                                  <p className="text-xs font-mono text-gray-400">{sci.code}</p>
                                </>
                              ) : (
                                <span className="text-gray-400">—</span>
                              )}
                            </td>
                            <td className="px-5 py-3">
                              {fetchedDate ? (
                                <>
                                  <p className="text-gray-700">{fetchedDate.toLocaleDateString()}</p>
                                  <p className="text-xs text-gray-400">{fetchedDate.toLocaleTimeString()}</p>
                                </>
                              ) : (
                                <span className="text-gray-400">—</span>
                              )}
                            </td>
                            <td className="px-5 py-3">
                              <span className="inline-flex items-center gap-1 bg-orange-100 text-orange-700 text-xs font-bold px-2.5 py-1 rounded-full">
                                <span className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                                Fetched
                              </span>
                            </td>
                          </tr>
                        )
                      })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
