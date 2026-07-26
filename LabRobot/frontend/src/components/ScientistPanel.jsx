// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (ScientistPanel.jsx)
// Date: 2025-10-06
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback, useMemo } from 'react'
import { getScientists, getPlacements } from '../api'
import PlaceChemicalModal from './PlaceChemicalModal'
import { PICKUP_SUCCESS_EVENT } from '../pickupMessaging'

const PALETTE = [
  {
    card: 'bg-blue-50 border-blue-200',
    badge: 'bg-blue-100 text-blue-800',
    rack: 'bg-blue-600',
    btn: 'bg-blue-700 hover:bg-blue-800',
    icon: 'text-blue-400',
  },
  {
    card: 'bg-emerald-50 border-emerald-200',
    badge: 'bg-emerald-100 text-emerald-800',
    rack: 'bg-emerald-600',
    btn: 'bg-emerald-700 hover:bg-emerald-800',
    icon: 'text-emerald-400',
  },
  {
    card: 'bg-violet-50 border-violet-200',
    badge: 'bg-violet-100 text-violet-800',
    rack: 'bg-violet-600',
    btn: 'bg-violet-700 hover:bg-violet-800',
    icon: 'text-violet-400',
  },
]

const CATEGORY_THEME = {
  acid: {
    fill: 'from-rose-300/90 to-red-400/90',
    border: 'border-rose-300/90',
    text: 'text-rose-950',
    badge: 'bg-rose-100 text-rose-800 border-rose-300/80',
    tag: 'Acid',
  },
  base: {
    fill: 'from-indigo-300/90 to-blue-400/90',
    border: 'border-indigo-300/90',
    text: 'text-indigo-950',
    badge: 'bg-indigo-100 text-indigo-800 border-indigo-300/80',
    tag: 'Base',
  },
  solvent: {
    fill: 'from-amber-300/90 to-yellow-400/90',
    border: 'border-amber-300/90',
    text: 'text-amber-950',
    badge: 'bg-amber-100 text-amber-800 border-amber-300/80',
    tag: 'Solvent',
  },
  oxidizer: {
    fill: 'from-fuchsia-300/90 to-pink-400/90',
    border: 'border-fuchsia-300/90',
    text: 'text-fuchsia-950',
    badge: 'bg-fuchsia-100 text-fuchsia-800 border-fuchsia-300/80',
    tag: 'Oxidizer',
  },
  hydrocarbon: {
    fill: 'from-emerald-300/90 to-lime-400/90',
    border: 'border-emerald-300/90',
    text: 'text-emerald-950',
    badge: 'bg-emerald-100 text-emerald-800 border-emerald-300/80',
    tag: 'Hydrocarbon',
  },
  neutral: {
    fill: 'from-cyan-300/90 to-sky-400/90',
    border: 'border-cyan-300/90',
    text: 'text-cyan-950',
    badge: 'bg-cyan-100 text-cyan-800 border-cyan-300/80',
    tag: 'Neutral',
  },
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

// Function: RackCompartments2D
function RackCompartments2D({ compartments }) {
  return (
    <div className="rounded-md border border-slate-300/70 bg-slate-100/90 p-1.5 space-y-1.5">
      {[3, 2, 1].map((slot) => {
        const placement = compartments[slot]
        const category = placement ? inferChemicalCategory(placement) : null
        const theme = category ? CATEGORY_THEME[category] : null
        return (
          <div
            key={slot}
            className={`relative h-7 rounded border overflow-hidden ${
              placement ? theme.border : 'border-slate-200 bg-white'
            }`}
          >
            {placement && (
              <div className={`absolute inset-0 bg-gradient-to-r ${theme.fill}`} />
            )}
            <div className="relative z-10 h-full px-1.5 flex items-center justify-between gap-1">
              <div className="flex items-center gap-1">
                <span className="text-[10px] font-bold text-slate-600">C{slot}</span>
                {placement && (
                  <span className={`text-[9px] px-1 rounded border ${theme.badge}`}>
                    {theme.tag}
                  </span>
                )}
              </div>
              <span className={`text-[10px] font-mono truncate max-w-[70px] ${placement ? `${theme.text} font-semibold` : 'text-slate-400 italic'}`}>
                {placement ? placement.chemical.barcode : 'Empty'}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Function: RackPanelCard
function RackPanelCard({ rack, compartments, colors }) {
  const occupiedCount = [1, 2, 3].filter((slot) => !!compartments[slot]).length

  return (
    <div className="rounded-lg border border-slate-300/80 bg-[#d7e4e8] shadow-[inset_0_1px_0_rgba(255,255,255,0.65)] p-1.5">
      <div className="h-1.5 rounded-sm bg-slate-900 mb-1.5" />
      <div className="flex items-center justify-between mb-1">
        <span className={`text-[10px] font-mono font-bold leading-none ${colors.icon}`}>{rack.barcode}</span>
        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${occupiedCount > 0 ? 'bg-emerald-100 text-emerald-800 border-emerald-300/80' : 'bg-slate-100 text-slate-500 border-slate-300/70'}`}>
          {occupiedCount}/3
        </span>
      </div>
      <RackCompartments2D compartments={compartments} />
    </div>
  )
}

// Function: ScientistPanel
export default function ScientistPanel() {
  const [scientists, setScientists] = useState([])
  const [rackChemicals, setRackChemicals] = useState({})   // rackId → { 1: placement|null, 2: placement|null, 3: placement|null }
  const [loading, setLoading] = useState(true)
  const [selectedScientist, setSelectedScientist] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('utilization')

  const loadData = useCallback(() => {
    Promise.all([getScientists(), getPlacements()])
      .then(([sciRes, plRes]) => {
        setScientists(sciRes.data)
        // Build rackId → fixed 3-compartment map (Placed only)
        const map = {}
        plRes.data.forEach((p) => {
          if (p.status !== 'Placed') return
          if (!map[p.rack_id]) map[p.rack_id] = { 1: null, 2: null, 3: null }
          const slot = Number.isInteger(p.compartment) ? p.compartment : 1
          if ([1, 2, 3].includes(slot)) {
            map[p.rack_id][slot] = p
          }
        })
        setRackChemicals(map)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { loadData() }, [loadData])

  useEffect(() => {
    // Function: handlePickupSuccess
    const handlePickupSuccess = () => loadData()
    document.addEventListener(PICKUP_SUCCESS_EVENT, handlePickupSuccess)
    return () => document.removeEventListener(PICKUP_SUCCESS_EVENT, handlePickupSuccess)
  }, [loadData])

  const scientistCards = useMemo(() => {
    return scientists.map((scientist) => {
      const placedCount = scientist.racks.reduce((sum, rack) => {
        const comps = rackChemicals[rack.id] || { 1: null, 2: null, 3: null }
        return sum + [1, 2, 3].filter((slot) => !!comps[slot]).length
      }, 0)
      const capacity = scientist.racks.length * 3
      const utilization = capacity > 0 ? Math.round((placedCount / capacity) * 100) : 0
      const freeSlots = Math.max(0, capacity - placedCount)
      const riskBand = utilization >= 85 ? 'High Load' : utilization >= 60 ? 'Moderate Load' : 'Optimal'
      return {
        scientist,
        placedCount,
        capacity,
        utilization,
        freeSlots,
        riskBand,
      }
    })
  }, [scientists, rackChemicals])

  const filteredCards = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase()
    const matched = scientistCards.filter(({ scientist }) => {
      if (!needle) return true
      return scientist.name.toLowerCase().includes(needle) || scientist.code.toLowerCase().includes(needle)
    })

    const sorted = [...matched]
    if (sortBy === 'utilization') {
      sorted.sort((a, b) => b.utilization - a.utilization)
    } else if (sortBy === 'free') {
      sorted.sort((a, b) => a.freeSlots - b.freeSlots)
    } else {
      sorted.sort((a, b) => a.scientist.name.localeCompare(b.scientist.name))
    }
    return sorted
  }, [scientistCards, searchTerm, sortBy])

  const globalStats = useMemo(() => {
    const totalScientists = scientistCards.length
    const totalCapacity = scientistCards.reduce((sum, row) => sum + row.capacity, 0)
    const totalPlaced = scientistCards.reduce((sum, row) => sum + row.placedCount, 0)
    const constrainedScientists = scientistCards.filter((row) => row.freeSlots <= 2).length
    const utilPct = totalCapacity > 0 ? Math.round((totalPlaced / totalCapacity) * 100) : 0
    return {
      totalScientists,
      totalCapacity,
      totalPlaced,
      constrainedScientists,
      utilPct,
    }
  }, [scientistCards])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-gray-400">
        <svg className="animate-spin w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        Loading scientists…
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-800">Scientists &amp; Virtual Racks</h2>
        <p className="text-sm text-gray-500 mt-0.5">
          Production-ready operations cockpit with rack utilization, slot pressure, and hazard-aware compartment visibility.
        </p>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="rounded-xl border border-slate-200 bg-white px-3 py-2.5">
            <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">Scientists</p>
            <p className="text-xl font-bold text-slate-800">{globalStats.totalScientists}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white px-3 py-2.5">
            <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">Slots Used</p>
            <p className="text-xl font-bold text-slate-800">{globalStats.totalPlaced}/{globalStats.totalCapacity}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white px-3 py-2.5">
            <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">Utilization</p>
            <p className="text-xl font-bold text-slate-800">{globalStats.utilPct}%</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white px-3 py-2.5">
            <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">Constrained Labs</p>
            <p className="text-xl font-bold text-slate-800">{globalStats.constrainedScientists}</p>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
          {Object.values(CATEGORY_THEME).map((theme) => (
            <span key={theme.tag} className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border ${theme.badge}`}>
              <span className={`w-2 h-2 rounded-full bg-gradient-to-r ${theme.fill}`} />
              {theme.tag}
            </span>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="min-w-[240px] flex-1 max-w-md rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            placeholder="Search scientist by name or code"
          />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option value="utilization">Sort: Highest Utilization</option>
            <option value="free">Sort: Lowest Free Slots</option>
            <option value="name">Sort: Name</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {filteredCards.map(({ scientist, placedCount: scientistPlacedCount, capacity: scientistCapacity, utilization, freeSlots, riskBand }, idx) => {
          const colors = PALETTE[idx % PALETTE.length]

          return (
            <div
              key={scientist.id}
              className={`rounded-2xl border-2 ${colors.card} p-5 shadow-sm flex flex-col relative overflow-hidden`}
            >
              <div className="absolute top-0 left-0 right-0 h-1.5 bg-slate-900/90" />

              {/* Scientist header */}
              <div className="flex items-center gap-3 mb-4 mt-1">
                <div className={`w-10 h-10 rounded-xl ${colors.rack} flex items-center justify-center text-white font-bold text-lg`}>
                  {scientist.name.charAt(scientist.name.lastIndexOf(' ') + 1)}
                </div>
                <div>
                  <p className="font-bold text-gray-800 text-base leading-tight">{scientist.name}</p>
                  <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded-full ${colors.badge}`}>
                    {scientist.code}
                  </span>
                </div>
              </div>

              <div className="mb-4 grid grid-cols-2 gap-2">
                <div className="rounded-lg border border-slate-300/70 bg-white/70 px-2 py-1.5">
                  <p className="text-[10px] uppercase tracking-wide text-slate-500 font-semibold">Filled Slots</p>
                  <p className="text-sm font-bold text-slate-800">{scientistPlacedCount}/{scientistCapacity}</p>
                </div>
                <div className="rounded-lg border border-slate-300/70 bg-white/70 px-2 py-1.5">
                  <p className="text-[10px] uppercase tracking-wide text-slate-500 font-semibold">Rack Units</p>
                  <p className="text-sm font-bold text-slate-800">{scientist.racks.length}</p>
                </div>
              </div>

              <div className="mb-4 grid grid-cols-3 gap-2">
                <div className="rounded-lg border border-slate-300/70 bg-white/80 px-2 py-1.5">
                  <p className="text-[10px] uppercase tracking-wide text-slate-500 font-semibold">Util</p>
                  <p className="text-sm font-bold text-slate-800">{utilization}%</p>
                </div>
                <div className="rounded-lg border border-slate-300/70 bg-white/80 px-2 py-1.5">
                  <p className="text-[10px] uppercase tracking-wide text-slate-500 font-semibold">Free</p>
                  <p className="text-sm font-bold text-slate-800">{freeSlots}</p>
                </div>
                <div className="rounded-lg border border-slate-300/70 bg-white/80 px-2 py-1.5">
                  <p className="text-[10px] uppercase tracking-wide text-slate-500 font-semibold">Load</p>
                  <p className={`text-[11px] font-bold ${riskBand === 'High Load' ? 'text-rose-700' : riskBand === 'Moderate Load' ? 'text-amber-700' : 'text-emerald-700'}`}>
                    {riskBand}
                  </p>
                </div>
              </div>

              {/* Racks — 3×3 grid */}
              <div className="mb-5 flex-1">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                  Virtual Racks (3 × 3 = 9)
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {scientist.racks.map((rack) => {
                    const compartments = rackChemicals[rack.id] || { 1: null, 2: null, 3: null }

                    return (
                      <RackPanelCard
                        key={rack.id}
                        rack={rack}
                        compartments={compartments}
                        colors={colors}
                      />
                    )
                  })}
                </div>
              </div>

              <button
                onClick={() => setSelectedScientist(scientist)}
                className={`w-full ${colors.btn} text-white font-semibold py-2.5 px-4 rounded-xl transition-colors flex items-center justify-center gap-2`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 4v16m8-8H4" />
                </svg>
                Place Chemical
              </button>
            </div>
          )
        })}
      </div>

      {filteredCards.length === 0 && (
        <div className="rounded-xl border border-slate-300 bg-white px-4 py-6 text-sm text-slate-500">
          No scientist matched this filter. Try a different name, code, or sorting option.
        </div>
      )}

      {selectedScientist && (
        <PlaceChemicalModal
          scientist={selectedScientist}
          onClose={(placed) => {
            setSelectedScientist(null)
            if (placed) loadData()   // refresh rack contents after a new placement
          }}
        />
      )}
    </div>
  )
}
