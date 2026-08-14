// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (LabAssistantPanel.jsx)
// Date: 2026-03-22
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback } from 'react'
import { getScientists, getPlacements } from '../api'
import { PICKUP_SUCCESS_EVENT } from '../pickupMessaging'

// Same restrained Fluent accent rotation used in ScientistPanel (azure /
// green / purple) — accent-only, not full pastel card backgrounds.
const SCI_THEME = [
  { accent: '#0078D4', icon: '#0078D4', badge: 'bg-azure-50 text-azure-800 border border-azure-200', rackAccent: '#106EBE' },
  { accent: '#107C10', icon: '#107C10', badge: 'bg-[#DFF6DD] text-[#0B6A0B] border border-[#9FD89B]', rackAccent: '#0B6A0B' },
  { accent: '#8764B8', icon: '#8764B8', badge: 'bg-[#F1E9FB] text-[#5C2E91] border border-[#D6C2EE]', rackAccent: '#5C2E91' },
]

const CATEGORY_THEME = {
  acid:        { fill: '#FDE7E9', border: '#F1B7BB' },
  base:        { fill: '#DEECF9', border: '#A9D3F2' },
  solvent:     { fill: '#FFF4CE', border: '#F0CB55' },
  oxidizer:    { fill: '#F1E9FB', border: '#D6C2EE' },
  hydrocarbon: { fill: '#DFF6DD', border: '#9FD89B' },
  neutral:     { fill: '#E1DFDD', border: '#C8C6C4' },
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
      <div className="flex items-center justify-center py-24" style={{ color: '#8A8886' }}>
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
          <h2 className="text-lg font-semibold" style={{ color: '#201F1E' }}>Lab Assistant — Chemical Inventory</h2>
          <p className="text-sm mt-0.5" style={{ color: '#605E5C' }}>
            {placedItems.length} placed · {fetchedItems.length} fetched
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium" style={{ color: '#3B3A39' }}>Scientist:</label>
          <select
            value={filterScientistId}
            onChange={(e) => setFilterScientistId(e.target.value)}
            className="rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2"
            style={{ borderColor: '#8A8886', color: '#201F1E' }}
          >
            <option value="">All Scientists</option>
            {scientists.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => loadPlacements(filterScientistId)}
            className="flex items-center gap-1.5 text-white px-4 py-2 rounded text-sm font-semibold transition-colors"
            style={{ background: '#3B3A39' }}
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
        <div className="rounded border bg-white px-4 py-3 shadow-fluent" style={{ borderColor: '#EDEBE9' }}>
          <p className="text-[11px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Used Slots</p>
          <p className="text-2xl font-bold" style={{ color: '#201F1E' }}>{usedSlots}</p>
        </div>
        <div className="rounded border bg-white px-4 py-3 shadow-fluent" style={{ borderColor: '#EDEBE9' }}>
          <p className="text-[11px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Available Slots</p>
          <p className="text-2xl font-bold" style={{ color: '#201F1E' }}>{availableSlots}</p>
        </div>
        <div className="rounded border bg-white px-4 py-3 shadow-fluent" style={{ borderColor: '#EDEBE9' }}>
          <p className="text-[11px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Utilization</p>
          <p className="text-2xl font-bold" style={{ color: '#0078D4' }}>{utilizationPct}%</p>
        </div>
        <div className="rounded border bg-white px-4 py-3 shadow-fluent" style={{ borderColor: '#EDEBE9' }}>
          <p className="text-[11px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Fetched Ledger</p>
          <p className="text-2xl font-bold" style={{ color: '#201F1E' }}>{fetchedItems.length}</p>
        </div>
      </div>

      <div className="rounded border px-4 py-3 mb-6" style={{ background: '#FFF4CE', borderColor: '#F0CB55' }}>
        <p className="text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: '#835C00' }}>Operations Alerts</p>
        {riskAlerts.length === 0 ? (
          <p className="text-sm font-medium" style={{ color: '#0B6A0B' }}>No active risks. Operations are within defined thresholds.</p>
        ) : (
          <div className="space-y-1.5">
            {riskAlerts.map((alert) => (
              <p key={alert} className="text-sm" style={{ color: '#5C4400' }}>- {alert}</p>
            ))}
          </div>
        )}
      </div>

      {/* ── Tab switcher ─────────────────────────────────────────────── */}
      <div className="flex gap-1 rounded p-1 mb-6 w-fit border" style={{ background: '#F3F2F1', borderColor: '#E1DFDD' }}>
        <button
          type="button"
          onClick={() => setActiveTab('inventory')}
          className="px-5 py-2 rounded text-sm font-semibold transition-colors"
          style={activeTab === 'inventory'
            ? { background: '#FFFFFF', color: '#106EBE', boxShadow: '0 1px 2px rgba(0,0,0,0.08)' }
            : { color: '#605E5C' }}
        >
          Rack Inventory
          {placedItems.length > 0 && (
            <span className="ml-2 text-xs px-1.5 py-0.5 rounded-full font-bold" style={{ background: '#DEECF9', color: '#004578' }}>
              {placedItems.length}
            </span>
          )}
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('fetched')}
          className="px-5 py-2 rounded text-sm font-semibold transition-colors"
          style={activeTab === 'fetched'
            ? { background: '#FFFFFF', color: '#B4680B', boxShadow: '0 1px 2px rgba(0,0,0,0.08)' }
            : { color: '#605E5C' }}
        >
          Fetched Items
          {fetchedItems.length > 0 && (
            <span className="ml-2 text-xs px-1.5 py-0.5 rounded-full font-bold" style={{ background: '#FFF0E1', color: '#B4680B' }}>
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
              <div key={scientist.id} className="mb-8 rounded-lg border bg-white p-4 md:p-5 shadow-fluent relative overflow-hidden" style={{ borderColor: '#EDEBE9' }}>
                <div className="absolute top-0 left-0 right-0 h-1" style={{ background: theme.accent }} />

                <div className="flex flex-wrap items-center justify-between gap-3 mb-4 mt-1">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full text-white font-bold text-lg flex items-center justify-center" style={{ background: theme.icon }}>
                      {scientist.name.charAt(scientist.name.lastIndexOf(' ') + 1)}
                    </div>
                    <div>
                      <h3 className="text-base font-semibold leading-tight" style={{ color: '#201F1E' }}>{scientist.name}</h3>
                      <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded-full ${theme.badge}`}>
                        {scientist.code}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold px-2 py-1 rounded border" style={{ borderColor: '#D2D0CE', background: '#FAF9F8', color: '#3B3A39' }}>
                      {scientistPlaced}/{scientistCapacity} slots used
                    </span>
                    {!anyPlaced && (
                      <span className="text-xs italic" style={{ color: '#8A8886' }}>No chemicals placed</span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {scientist.racks.map((rack) => {
                    const rackSlots = placementsByRack(rack.id)
                    const count = placedCount(rackSlots)
                    return (
                      <div key={rack.id} className="rounded border overflow-hidden p-1.5" style={{ borderColor: '#D2D0CE', background: '#FAF9F8' }}>
                        <div className="h-1 rounded-sm mb-1.5" style={{ background: theme.accent }} />
                        <div className="border rounded px-2 py-1.5 flex items-center justify-between mb-1.5" style={{ background: '#FFFFFF', borderColor: '#E1DFDD' }}>
                          <div>
                            <p className="text-sm font-semibold" style={{ color: '#3B3A39' }}>{rack.name}</p>
                            <p className="text-xs font-mono" style={{ color: theme.rackAccent }}>{rack.barcode}</p>
                          </div>
                          <span
                            className="text-xs font-bold px-2 py-0.5 rounded-full"
                            style={count > 0 ? { background: '#DEECF9', color: '#004578' } : { background: '#F3F2F1', color: '#A19F9D' }}
                          >
                            {count}/3 placed
                          </span>
                        </div>

                        <div className="space-y-1.5">
                          {[1, 2, 3].map((slot) => {
                            const placement = rackSlots[slot]
                            if (!placement) {
                              return (
                                <div key={slot} className="flex items-center justify-between rounded px-2 py-1.5 border" style={{ background: '#FFFFFF', borderColor: '#E1DFDD' }}>
                                  <p className="text-xs font-semibold" style={{ color: '#605E5C' }}>Compartment C{slot}</p>
                                  <p className="text-xs italic" style={{ color: '#A19F9D' }}>Empty</p>
                                </div>
                              )
                            }
                            const category = inferChemicalCategory(placement)
                            const tone = CATEGORY_THEME[category]
                            return (
                              <div
                                key={slot}
                                className="flex items-center gap-2 rounded px-2 py-1.5 border"
                                style={{ background: tone.fill, borderColor: tone.border }}
                              >
                                <div className="flex-1 min-w-0">
                                  <p className="text-xs font-semibold" style={{ color: '#106EBE' }}>Compartment C{slot}</p>
                                  <p className="text-sm font-semibold truncate" style={{ color: '#201F1E' }}>
                                    {placement.chemical.name}
                                  </p>
                                  <p className="text-xs font-mono" style={{ color: '#605E5C' }}>{placement.chemical.barcode}</p>
                                  {placement.chemical.description && (
                                    <p className="text-xs truncate" style={{ color: '#8A8886' }}>{placement.chemical.description}</p>
                                  )}
                                </div>
                                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                                  <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#DFF6DD', color: '#0B6A0B' }}>
                                    Placed
                                  </span>
                                  <button
                                    type="button"
                                    onClick={() =>
                                      onDispatch?.({
                                        placementId: placement.id,
                                        rackId: placement.rack_id,
                                        barcode: placement.chemical.barcode,
                                        itemLabel: placement.chemical.name,
                                      })
                                    }
                                    className="text-[11px] font-semibold px-2.5 py-1 rounded border text-center transition-colors"
                                    style={{ background: '#FFF4CE', color: '#835C00', borderColor: '#F0CB55' }}
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
            <div className="text-center py-20" style={{ color: '#D2D0CE' }}>
              <svg className="w-20 h-20 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <p className="text-lg" style={{ color: '#A19F9D' }}>No chemicals placed yet</p>
              <p className="text-sm mt-1" style={{ color: '#C8C6C4' }}>Switch to the Scientist View to place chemicals into racks.</p>
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
            <div className="text-center py-20" style={{ color: '#D2D0CE' }}>
              <svg className="w-20 h-20 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
              <p className="text-lg" style={{ color: '#A19F9D' }}>No chemicals fetched yet</p>
              <p className="text-sm mt-1" style={{ color: '#C8C6C4' }}>Use the 3D Rack View to send a pickup message and wait for robot success confirmation.</p>
            </div>
          ) : (
            <>
              {/* Summary stats bar */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="rounded border px-5 py-4" style={{ background: '#FFF0E1', borderColor: '#F5CB8C' }}>
                  <p className="text-2xl font-bold" style={{ color: '#B4680B' }}>{fetchedItems.length}</p>
                  <p className="text-sm mt-0.5" style={{ color: '#605E5C' }}>Total Fetched</p>
                </div>
                <div className="rounded border px-5 py-4" style={{ background: '#EFF6FC', borderColor: '#C7E0F4' }}>
                  <p className="text-2xl font-bold" style={{ color: '#0078D4' }}>
                    {new Set(fetchedItems.map(p => rackToScientist[p.rack_id]?.id)).size}
                  </p>
                  <p className="text-sm mt-0.5" style={{ color: '#605E5C' }}>Scientists Involved</p>
                </div>
                <div className="rounded border px-5 py-4" style={{ background: '#DFF6DD', borderColor: '#9FD89B' }}>
                  <p className="text-2xl font-bold" style={{ color: '#107C10' }}>{placedItems.length}</p>
                  <p className="text-sm mt-0.5" style={{ color: '#605E5C' }}>Still in Racks</p>
                </div>
              </div>

              {/* Fetched items table */}
              <div className="bg-white rounded-lg border shadow-fluent overflow-hidden" style={{ borderColor: '#EDEBE9' }}>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b" style={{ background: '#FAF9F8', borderColor: '#EDEBE9' }}>
                      <th className="text-left px-5 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: '#605E5C' }}>#</th>
                      <th className="text-left px-5 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: '#605E5C' }}>Chemical Name</th>
                      <th className="text-left px-5 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: '#605E5C' }}>Rack</th>
                      <th className="text-left px-5 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: '#605E5C' }}>Scientist</th>
                      <th className="text-left px-5 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: '#605E5C' }}>Date Fetched</th>
                      <th className="text-left px-5 py-3 text-xs font-bold uppercase tracking-wide" style={{ color: '#605E5C' }}>Status</th>
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
                          <tr
                            key={p.id}
                            className="border-b transition-colors hover:bg-chrome-50"
                            style={{ borderColor: '#F3F2F1', background: i % 2 === 0 ? 'transparent' : '#FAF9F8' }}
                          >
                            <td className="px-5 py-3 font-mono text-xs" style={{ color: '#A19F9D' }}>{i + 1}</td>
                            <td className="px-5 py-3">
                              <p className="font-semibold" style={{ color: '#201F1E' }}>{p.chemical.name}</p>
                              <p className="text-xs font-mono" style={{ color: '#8A8886' }}>{p.chemical.barcode}</p>
                            </td>
                            <td className="px-5 py-3">
                              <p className="font-semibold" style={{ color: '#3B3A39' }}>{p.rack?.name ?? `Rack #${p.rack_id}`}</p>
                              <p className="text-xs font-mono" style={{ color: '#8A8886' }}>{p.rack?.barcode ?? ''}</p>
                            </td>
                            <td className="px-5 py-3">
                              {sci ? (
                                <>
                                  <p className="font-semibold" style={{ color: '#3B3A39' }}>{sci.name}</p>
                                  <p className="text-xs font-mono" style={{ color: '#8A8886' }}>{sci.code}</p>
                                </>
                              ) : (
                                <span style={{ color: '#A19F9D' }}>—</span>
                              )}
                            </td>
                            <td className="px-5 py-3">
                              {fetchedDate ? (
                                <>
                                  <p style={{ color: '#3B3A39' }}>{fetchedDate.toLocaleDateString()}</p>
                                  <p className="text-xs" style={{ color: '#8A8886' }}>{fetchedDate.toLocaleTimeString()}</p>
                                </>
                              ) : (
                                <span style={{ color: '#A19F9D' }}>—</span>
                              )}
                            </td>
                            <td className="px-5 py-3">
                              <span className="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: '#FFF0E1', color: '#B4680B' }}>
                                <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#B4680B' }} />
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
