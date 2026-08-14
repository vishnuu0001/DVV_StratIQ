// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (ScientistPanel.jsx)
// Date: 2025-10-06
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback, useMemo } from 'react'
import { getScientists, getPlacements } from '../api'
import PlaceChemicalModal from './PlaceChemicalModal'
import { PICKUP_SUCCESS_EVENT } from '../pickupMessaging'

// Fluent-accessible accent set — a restrained 3-color rotation (Azure blue,
// Fluent green, Fluent purple) rather than a full pastel card-background
// palette, matching how Azure Portal differentiates resource cards with a
// small accent + icon instead of tinting the whole card.
const PALETTE = [
  { accent: '#0078D4', accentBg: '#EFF6FC', badge: 'bg-azure-50 text-azure-800 border border-azure-200', btn: 'bg-azure-600 hover:bg-azure-700' },
  { accent: '#0B6A0B', accentBg: '#DFF6DD', badge: 'bg-[#DFF6DD] text-[#0B6A0B] border border-[#9FD89B]', btn: 'bg-[#107C10] hover:bg-[#0B6A0B]' },
  { accent: '#8764B8', accentBg: '#F1E9FB', badge: 'bg-[#F1E9FB] text-[#5C2E91] border border-[#D6C2EE]', btn: 'bg-[#8764B8] hover:bg-[#5C2E91]' },
]

// Fluent semantic hues for hazard categories — light tint background with a
// dark-enough foreground to hold WCAG AA contrast (>= 4.5:1) at this size.
const CATEGORY_THEME = {
  acid: {
    fill: '#FDE7E9', border: '#F1B7BB', text: '#A4262C',
    badge: 'bg-[#FDE7E9] text-[#A4262C] border-[#F1B7BB]',
    tag: 'Acid',
  },
  base: {
    fill: '#DEECF9', border: '#A9D3F2', text: '#004578',
    badge: 'bg-[#DEECF9] text-[#004578] border-[#A9D3F2]',
    tag: 'Base',
  },
  solvent: {
    fill: '#FFF4CE', border: '#F0CB55', text: '#835C00',
    badge: 'bg-[#FFF4CE] text-[#835C00] border-[#F0CB55]',
    tag: 'Solvent',
  },
  oxidizer: {
    fill: '#F1E9FB', border: '#D6C2EE', text: '#5C2E91',
    badge: 'bg-[#F1E9FB] text-[#5C2E91] border-[#D6C2EE]',
    tag: 'Oxidizer',
  },
  hydrocarbon: {
    fill: '#DFF6DD', border: '#9FD89B', text: '#0B6A0B',
    badge: 'bg-[#DFF6DD] text-[#0B6A0B] border-[#9FD89B]',
    tag: 'Hydrocarbon',
  },
  neutral: {
    fill: '#E1DFDD', border: '#C8C6C4', text: '#3B3A39',
    badge: 'bg-[#E1DFDD] text-[#3B3A39] border-[#C8C6C4]',
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
    <div className="rounded border border-chrome-300 bg-chrome-100 p-1.5 space-y-1.5">
      {[3, 2, 1].map((slot) => {
        const placement = compartments[slot]
        const category = placement ? inferChemicalCategory(placement) : null
        const theme = category ? CATEGORY_THEME[category] : null
        return (
          <div
            key={slot}
            className="relative h-7 rounded border overflow-hidden"
            style={{
              borderColor: placement ? theme.border : '#E1DFDD',
              background: placement ? theme.fill : '#FFFFFF',
            }}
          >
            <div className="relative z-10 h-full px-1.5 flex items-center justify-between gap-1">
              <div className="flex items-center gap-1">
                <span className="text-[10px] font-bold" style={{ color: '#3B3A39' }}>C{slot}</span>
                {placement && (
                  <span className="text-[9px] px-1 rounded border font-medium" style={{ color: theme.text, borderColor: theme.border, background: 'rgba(255,255,255,0.55)' }}>
                    {theme.tag}
                  </span>
                )}
              </div>
              <span
                className="text-[10px] font-mono truncate max-w-[70px]"
                style={{ color: placement ? theme.text : '#8A8886', fontStyle: placement ? 'normal' : 'italic', fontWeight: placement ? 600 : 400 }}
              >
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
    <div className="rounded border border-chrome-300 bg-chrome-50 p-1.5">
      <div className="h-1 rounded-sm mb-1.5" style={{ background: colors.accent }} />
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] font-mono font-bold leading-none" style={{ color: colors.accent }}>{rack.barcode}</span>
        <span
          className="text-[10px] font-bold px-1.5 py-0.5 rounded border"
          style={occupiedCount > 0
            ? { color: '#0B6A0B', background: '#DFF6DD', borderColor: '#9FD89B' }
            : { color: '#605E5C', background: '#F3F2F1', borderColor: '#D2D0CE' }}
        >
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
      <div className="flex items-center justify-center py-24" style={{ color: '#605E5C' }}>
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
        <h2 className="text-lg font-semibold" style={{ color: '#201F1E' }}>Scientists &amp; Virtual Racks</h2>
        <p className="text-sm mt-0.5" style={{ color: '#605E5C' }}>
          Production-ready operations cockpit with rack utilization, slot pressure, and hazard-aware compartment visibility.
        </p>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="rounded border border-chrome-200 bg-white px-3 py-2.5 shadow-fluent">
            <p className="text-[11px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Scientists</p>
            <p className="text-xl font-bold" style={{ color: '#201F1E' }}>{globalStats.totalScientists}</p>
          </div>
          <div className="rounded border border-chrome-200 bg-white px-3 py-2.5 shadow-fluent">
            <p className="text-[11px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Slots Used</p>
            <p className="text-xl font-bold" style={{ color: '#201F1E' }}>{globalStats.totalPlaced}/{globalStats.totalCapacity}</p>
          </div>
          <div className="rounded border border-chrome-200 bg-white px-3 py-2.5 shadow-fluent">
            <p className="text-[11px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Utilization</p>
            <p className="text-xl font-bold" style={{ color: '#0078D4' }}>{globalStats.utilPct}%</p>
          </div>
          <div className="rounded border border-chrome-200 bg-white px-3 py-2.5 shadow-fluent">
            <p className="text-[11px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Constrained Labs</p>
            <p className="text-xl font-bold" style={{ color: globalStats.constrainedScientists > 0 ? '#A4262C' : '#201F1E' }}>{globalStats.constrainedScientists}</p>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
          {Object.values(CATEGORY_THEME).map((theme) => (
            <span key={theme.tag} className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full border font-medium ${theme.badge}`}>
              <span className="w-2 h-2 rounded-full" style={{ background: theme.text }} />
              {theme.tag}
            </span>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="min-w-[240px] flex-1 max-w-md rounded border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2"
            style={{ borderColor: '#8A8886', color: '#201F1E' }}
            placeholder="Search scientist by name or code"
          />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded border bg-white px-3 py-2 text-sm focus:outline-none"
            style={{ borderColor: '#8A8886', color: '#201F1E' }}
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
              className="rounded-lg border bg-white p-5 shadow-fluent flex flex-col relative overflow-hidden"
              style={{ borderColor: '#EDEBE9' }}
            >
              <div className="absolute top-0 left-0 right-0 h-1" style={{ background: colors.accent }} />

              {/* Scientist header */}
              <div className="flex items-center gap-3 mb-4 mt-1">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg shrink-0"
                  style={{ background: colors.accent }}
                >
                  {scientist.name.charAt(scientist.name.lastIndexOf(' ') + 1)}
                </div>
                <div>
                  <p className="font-semibold text-base leading-tight" style={{ color: '#201F1E' }}>{scientist.name}</p>
                  <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded-full ${colors.badge}`}>
                    {scientist.code}
                  </span>
                </div>
              </div>

              <div className="mb-4 grid grid-cols-2 gap-2">
                <div className="rounded border px-2 py-1.5" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
                  <p className="text-[10px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Filled Slots</p>
                  <p className="text-sm font-bold" style={{ color: '#201F1E' }}>{scientistPlacedCount}/{scientistCapacity}</p>
                </div>
                <div className="rounded border px-2 py-1.5" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
                  <p className="text-[10px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Rack Units</p>
                  <p className="text-sm font-bold" style={{ color: '#201F1E' }}>{scientist.racks.length}</p>
                </div>
              </div>

              <div className="mb-4 grid grid-cols-3 gap-2">
                <div className="rounded border px-2 py-1.5" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
                  <p className="text-[10px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Util</p>
                  <p className="text-sm font-bold" style={{ color: '#201F1E' }}>{utilization}%</p>
                </div>
                <div className="rounded border px-2 py-1.5" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
                  <p className="text-[10px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Free</p>
                  <p className="text-sm font-bold" style={{ color: '#201F1E' }}>{freeSlots}</p>
                </div>
                <div className="rounded border px-2 py-1.5" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
                  <p className="text-[10px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Load</p>
                  <p
                    className="text-[11px] font-bold"
                    style={{ color: riskBand === 'High Load' ? '#A4262C' : riskBand === 'Moderate Load' ? '#835C00' : '#0B6A0B' }}
                  >
                    {riskBand}
                  </p>
                </div>
              </div>

              {/* Racks — 3×3 grid */}
              <div className="mb-5 flex-1">
                <p className="text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: '#8A8886' }}>
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
                type="button"
                onClick={() => setSelectedScientist(scientist)}
                className={`w-full ${colors.btn} text-white font-semibold py-2.5 px-4 rounded transition-colors flex items-center justify-center gap-2`}
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
        <div className="rounded border bg-white px-4 py-6 text-sm" style={{ borderColor: '#E1DFDD', color: '#605E5C' }}>
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
