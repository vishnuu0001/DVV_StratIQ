// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (PlaceChemicalModal.jsx)
// Date: 2026-01-18
// ---------------------------------------------------------------------------
import { useState, useEffect, useRef } from 'react'
import { searchChemical, placeChemical, getPlacements } from '../api'

// All 10 seeded chemical barcodes the scanner can "pick"
const BARCODE_POOL = [
  'CHEM-001','CHEM-002','CHEM-003','CHEM-004','CHEM-005',
  'CHEM-006','CHEM-007','CHEM-008','CHEM-009','CHEM-010',
]

/* ── tiny hook: typewriter ────────────────────────────────────────── */
// Function: useTypewriter
function useTypewriter(target, active, delayPerChar = 75) {
  const [displayed, setDisplayed] = useState('')
  const timerRef = useRef(null)

  useEffect(() => {
    if (!active) { setDisplayed(''); return }
    setDisplayed('')
    let idx = 0
    // Function: tick
    const tick = () => {
      idx++
      setDisplayed(target.slice(0, idx))
      if (idx < target.length) timerRef.current = setTimeout(tick, delayPerChar)
    }
    timerRef.current = setTimeout(tick, delayPerChar)
    return () => clearTimeout(timerRef.current)
  }, [target, active, delayPerChar])

  return displayed
}

/* ── Scan-phase status message (mutually-exclusive, so a lookup is safe) ── */
// Function: scanPhaseMessage
function scanPhaseMessage(scanPhase, typedBarcode) {
  switch (scanPhase) {
    case 'idle': return 'Press Simulate Scan — laser will auto-capture & search a barcode'
    case 'scanning': return 'Laser beam sweeping… aligning barcode…'
    case 'typing': return `Reading: ${typedBarcode}█`
    case 'done': return 'Barcode captured — auto-searching…'
    default: return ''
  }
}

/* ── Scanner laser beam widget ────────────────────────────────────── */
// Function: ScannerBeam
function ScannerBeam({ scanning }) {
  return (
    <div className="relative w-full h-14 bg-slate-900 rounded-lg overflow-hidden border border-slate-600 flex items-center justify-center">
      {/* barcode stripes */}
      <div className="flex gap-0.5 items-end h-9 px-4 opacity-60">
        {[3,1,4,1,5,2,3,2,4,1,2,3,1,4,2,1,3,2,4,1,3,2,1,4,2].map((h, i) => (
          <div key={i} className="bg-slate-200" style={{ width: 2, height: `${h * 8}%` }} />
        ))}
      </div>
      {/* laser sweep */}
      {scanning && (
        <div
          className="absolute top-0 bottom-0 w-0.5 shadow-[0_0_8px_2px_rgba(209,52,56,0.8)]"
          style={{ background: '#D13438', animation: 'scanSweep 0.9s ease-in-out infinite alternate' }}
        />
      )}
      {!scanning && (
        <span className="absolute text-xs text-slate-500 font-mono tracking-widest select-none">
          READY TO SCAN
        </span>
      )}
      <style>{`@keyframes scanSweep { from { left: 8%; } to { left: 92%; } }`}</style>
    </div>
  )
}

/* ── Success state shown after a chemical has been placed ─────────── */
// Function: PlacedSuccessView
function PlacedSuccessView({ reassignmentMsg }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 px-6 gap-4">
      <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ background: '#DFF6DD' }}>
        <svg className="w-9 h-9" style={{ color: '#0B6A0B' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <p className="font-semibold text-lg" style={{ color: '#0B6A0B' }}>Chemical Placed!</p>
      <p className="text-sm" style={{ color: '#8A8886' }}>
        Status updated to <span className="font-semibold" style={{ color: '#0B6A0B' }}>Placed</span>
      </p>
      {reassignmentMsg && (
        <div className="w-full rounded border px-4 py-3 text-sm flex items-start gap-2" style={{ background: '#FFF4CE', borderColor: '#F0CB55', color: '#835C00' }}>
          <svg className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: '#835C00' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
          <span>{reassignmentMsg}</span>
        </div>
      )}
    </div>
  )
}

/* ── Rack/compartment selector, scanner, search & place form ───────── */
// Function: PlacementForm
function PlacementForm({
  scientist,
  rackOccupancy,
  selectedRackId,
  setSelectedRackId,
  selectedCompartment,
  setSelectedCompartment,
  scanPhase,
  isScanning,
  typedBarcode,
  handleSimulateScan,
  barcode,
  setBarcode,
  setChemical,
  setError,
  setScanPhase,
  handleManualSearch,
  searching,
  error,
  chemical,
  onClose,
  handlePlace,
  placing,
}) {
  const selectedOcc = rackOccupancy[Number(selectedRackId)] || { 1: null, 2: null, 3: null }
  const selectedSlotOccupied = selectedOcc[selectedCompartment]

  return (
    <div className="p-6 space-y-5">

      {/* Rack selector — 3×3 grid */}
      <div>
        <label className="block text-xs font-bold uppercase tracking-wide mb-1.5" style={{ color: '#605E5C' }}>
          Select Rack — {scientist.name}
          <span className="ml-2 font-normal normal-case" style={{ color: '#0078D4' }}>
            (click rack, then choose compartment C1/C2/C3)
          </span>
        </label>
        <div className="grid grid-cols-3 gap-1.5">
          {scientist.racks.map((rack) => {
            const occ = rackOccupancy[rack.id] || { 1: null, 2: null, 3: null }
            const occupiedCount = [1, 2, 3].filter((slot) => !!occ[slot]).length
            const isSelected = Number(selectedRackId) === rack.id
            const style = isSelected
              ? { borderColor: '#0078D4', background: '#EFF6FC', color: '#004578', boxShadow: '0 0 0 2px #A9D3F2' }
              : occupiedCount > 0
              ? { borderColor: '#9FD89B', background: '#DFF6DD', color: '#0B6A0B' }
              : { borderColor: '#E1DFDD', background: '#FFFFFF', color: '#3B3A39' }
            return (
              <button
                key={rack.id}
                type="button"
                onClick={() => setSelectedRackId(rack.id)}
                className="relative rounded px-2 py-2 text-left border transition-all text-xs font-mono font-semibold focus:outline-none"
                style={style}
              >
                <span className="block leading-none">{rack.barcode}</span>
                <span className="block text-xs font-normal mt-0.5 leading-none" style={{ color: occupiedCount > 0 ? '#0B6A0B' : '#8A8886' }}>
                  {occupiedCount}/3 occupied
                </span>
              </button>
            )
          })}
        </div>

        <div className="mt-3">
          <label className="block text-[11px] font-bold uppercase tracking-wide mb-1" style={{ color: '#605E5C' }}>
            Select Compartment
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[1, 2, 3].map((slot) => {
              const occ = (rackOccupancy[Number(selectedRackId)] || { 1: null, 2: null, 3: null })[slot]
              const isSelected = selectedCompartment === slot
              const style = isSelected
                ? { borderColor: '#0078D4', background: '#EFF6FC', color: '#004578' }
                : occ
                ? { borderColor: '#F0CB55', background: '#FFF4CE', color: '#835C00' }
                : { borderColor: '#D2D0CE', background: '#FFFFFF', color: '#3B3A39' }
              return (
                <button
                  key={slot}
                  type="button"
                  onClick={() => setSelectedCompartment(slot)}
                  className="rounded border px-2 py-2 text-xs font-semibold transition-colors"
                  style={style}
                >
                  C{slot} · {occ ? occ.chemical.barcode : 'Empty'}
                </button>
              )
            })}
          </div>
        </div>

        {selectedSlotOccupied && (
          <p className="mt-2 text-xs rounded border px-3 py-1.5 flex items-center gap-1.5 font-semibold" style={{ color: '#A4262C', background: '#FDE7E9', borderColor: '#F1B7BB' }}>
            <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M18.364 5.636l-12.728 12.728M5.636 5.636l12.728 12.728" />
            </svg>
            Selected compartment is occupied — choose an empty compartment.
          </p>
        )}
      </div>

      {/* ── Scanner widget ─────────────────────────────────────── */}
      <div className="rounded p-4 space-y-3" style={{ background: '#252423' }}>
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wide flex items-center gap-1.5" style={{ color: '#D2D0CE' }}>
            <svg className="w-3.5 h-3.5" style={{ color: '#F1707B' }} fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 000 2h1v8H3a1 1 0 100 2h14a1 1 0 100-2h-1V6h1a1 1 0 100-2H3zm4 2h6v8H7V6z" />
            </svg>
            Barcode Scanner Simulation
          </span>
          {scanPhase === 'done' && (
            <span className="text-xs text-white px-2 py-0.5 rounded-full font-semibold" style={{ background: '#107C10' }}>
              ✓ Scanned
            </span>
          )}
          {isScanning && (
            <span className="text-xs text-white px-2 py-0.5 rounded-full font-semibold animate-pulse" style={{ background: '#D13438' }}>
              ● Scanning…
            </span>
          )}
        </div>

        <ScannerBeam scanning={isScanning} />

        <button
          type="button"
          onClick={handleSimulateScan}
          disabled={isScanning || !!selectedSlotOccupied}
          className="w-full text-white font-bold py-2.5 rounded text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ background: '#D13438' }}
        >
          {isScanning ? (
            <>
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Scanning…
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 4v1m0 14v1M4.22 4.22l.707.707m12.02 12.02.707.707M1 12h1m18 0h1M4.22 19.78l.707-.707M18.95 5.05l-.707.707" />
              </svg>
              Simulate Scan
            </>
          )}
        </button>

        <p className="text-xs text-center min-h-[1rem]" style={{ color: '#A19F9D' }}>
          {scanPhaseMessage(scanPhase, typedBarcode)}
        </p>
      </div>

      {/* ── Chemical Barcode input ──────────────────────────────── */}
      <div>
        <label className="block text-xs font-bold uppercase tracking-wide mb-1" style={{ color: '#605E5C' }}>
          Chemical Barcode
          <span className="ml-2 font-normal normal-case" style={{ color: '#0078D4' }}>
            (auto-filled by scanner · or type manually)
          </span>
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={barcode}
            readOnly={isScanning}
            onChange={(e) => {
              setBarcode(e.target.value)
              setChemical(null)
              setError('')
              setScanPhase('idle')
            }}
            onKeyDown={(e) => e.key === 'Enter' && handleManualSearch()}
            placeholder="e.g. CHEM-001  (or click Simulate Scan)"
            className="flex-1 border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 font-mono transition-colors"
            style={
              isScanning
                ? { background: '#FAF9F8', borderColor: '#A9D3F2', color: '#106EBE' }
                : scanPhase === 'done'
                ? { background: '#DFF6DD', borderColor: '#9FD89B', color: '#0B6A0B' }
                : { background: '#FFFFFF', borderColor: '#8A8886', color: '#201F1E' }
            }
          />
          <button
            type="button"
            onClick={handleManualSearch}
            disabled={searching || isScanning}
            className="text-white px-4 py-2 rounded text-sm font-semibold disabled:opacity-50 transition-colors"
            style={{ background: '#3B3A39' }}
          >
            {searching ? (
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            ) : 'Search'}
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-start gap-2 rounded border px-4 py-3 text-sm" style={{ background: '#FDE7E9', borderColor: '#F1B7BB', color: '#A4262C' }}>
          <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}

      {/* Chemical match result */}
      {chemical && (
        <div className="rounded border p-4" style={{ background: '#DFF6DD', borderColor: '#9FD89B' }}>
          <p className="text-xs font-bold uppercase tracking-wide mb-3 flex items-center gap-1.5" style={{ color: '#0B6A0B' }}>
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Chemical Matched
          </p>
          <div className="space-y-1.5">
            {[
              ['Name', chemical.name],
              ['Barcode', chemical.barcode],
              ['Description', chemical.description],
            ].map(([label, value]) => value && (
              <div key={label} className="flex justify-between text-sm">
                <span className="font-medium" style={{ color: '#605E5C' }}>{label}</span>
                <span className={`font-semibold ${label === 'Barcode' ? 'font-mono' : ''}`} style={{ color: '#201F1E' }}>
                  {value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 pt-1">
        <button
          type="button"
          onClick={onClose}
          className="flex-1 border font-semibold py-2.5 rounded transition-colors text-sm"
          style={{ borderColor: '#8A8886', color: '#201F1E' }}
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={handlePlace}
          disabled={!chemical || placing || !!selectedSlotOccupied}
          className="flex-1 bg-azure-600 hover:bg-azure-700 text-white font-semibold py-2.5 rounded transition-colors text-sm disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {placing ? (
            <>
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Placing…
            </>
          ) : 'Place in Rack'}
        </button>
      </div>
    </div>
  )
}

// Function: PlaceChemicalModal
export default function PlaceChemicalModal({ scientist, onClose }) {
  // ── Rack occupancy (fetch once on open) ──────────────────────────
  const [rackOccupancy, setRackOccupancy] = useState({})   // rackId → {1: placement|null, 2: placement|null, 3: placement|null}

  useEffect(() => {
    getPlacements(scientist.id).then((res) => {
      const map = {}
      scientist.racks.forEach((r) => {
        map[r.id] = { 1: null, 2: null, 3: null }
      })
      res.data.forEach((p) => {
        const slot = Number.isInteger(p.compartment) ? p.compartment : 1
        if (p.status === 'Placed' && [1, 2, 3].includes(slot) && map[p.rack_id]) {
          map[p.rack_id][slot] = p
        }
      })
      setRackOccupancy(map)
    }).catch(console.error)
  }, [scientist.id, scientist.racks])

  const [selectedRackId, setSelectedRackId] = useState(
    scientist.racks[0]?.id ?? ''
  )
  const [selectedCompartment, setSelectedCompartment] = useState(1)
  useEffect(() => {
    const occ = rackOccupancy[Number(selectedRackId)] || { 1: null, 2: null, 3: null }
    const firstEmpty = [1, 2, 3].find((slot) => !occ[slot])
    setSelectedCompartment(firstEmpty ?? 1)
  }, [selectedRackId, rackOccupancy])


  // scan phase: idle | scanning | typing | done
  const [scanPhase, setScanPhase] = useState('idle')
  const [scannedBarcode, setScannedBarcode] = useState('')

  const [barcode, setBarcode] = useState('')
  const [chemical, setChemical] = useState(null)
  const [searching, setSearching] = useState(false)
  const [placing, setPlacing] = useState(false)
  const [error, setError] = useState('')
  const [placed, setPlaced] = useState(false)
  const [reassignmentMsg, setReassignmentMsg] = useState(null)  // from backend when rack was busy

  // Function: mapPlacementError
  const mapPlacementError = (err) => {
    const status = err?.response?.status
    const detailRaw = err?.response?.data?.detail
    const detail = typeof detailRaw === 'string' ? detailRaw.toLowerCase() : ''

    if (status === 409) {
      if (detail.includes('compartment') && detail.includes('occupied')) {
        return `Selected slot C${selectedCompartment} is already occupied in this rack. Please choose another empty slot.`
      }
      if (detail.includes('already placed')) {
        return 'This chemical barcode is already placed. Fetch it first or choose a different chemical barcode.'
      }
      return 'Placement conflict: this slot or chemical cannot be assigned right now. Refresh and try another slot or barcode.'
    }

    if (status === 400) {
      return 'Invalid placement selection. Please reselect rack and compartment, then try again.'
    }

    return err?.response?.data?.detail ?? 'Failed to place chemical.'
  }

  // typewriter fires while scanPhase === 'typing'
  const typedBarcode = useTypewriter(scannedBarcode, scanPhase === 'typing')

  // sync typewriter output → barcode input field
  useEffect(() => {
    if (scanPhase === 'typing') setBarcode(typedBarcode)
  }, [typedBarcode, scanPhase])

  // once typewriter finishes → auto-search
  useEffect(() => {
    if (
      scanPhase === 'typing' &&
      scannedBarcode !== '' &&
      typedBarcode === scannedBarcode
    ) {
      setScanPhase('done')
      triggerSearch(scannedBarcode)
    }
  }, [typedBarcode, scannedBarcode, scanPhase])

  /* ── Simulate scan ─────────────────────────────────────────────── */
  // Function: handleSimulateScan
  const handleSimulateScan = () => {
    if (scanPhase === 'scanning' || scanPhase === 'typing') return
    const occ = rackOccupancy[Number(selectedRackId)] || { 1: null, 2: null, 3: null }
    if (occ[selectedCompartment]) {
      setError(`Compartment C${selectedCompartment} is occupied. Select an empty compartment before scanning.`)
      return
    }
    setChemical(null)
    setError('')
    setBarcode('')
    const picked = BARCODE_POOL[Math.floor(Math.random() * BARCODE_POOL.length)]
    setScannedBarcode(picked)
    setScanPhase('scanning')
    // 1.2 s laser sweep → start typewriter
    setTimeout(() => setScanPhase('typing'), 1200)
  }

  /* ── Search (shared by manual & auto paths) ────────────────────── */
  // Function: triggerSearch
  const triggerSearch = async (code) => {
    const trimmed = (code ?? barcode).trim()
    if (!trimmed) { setError('Please enter or scan a barcode.'); return }
    setSearching(true)
    setError('')
    setChemical(null)
    try {
      const res = await searchChemical(trimmed)
      setChemical(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Chemical not found for this barcode.')
    } finally {
      setSearching(false)
    }
  }

  // Function: handleManualSearch
  const handleManualSearch = () => {
    setScanPhase('idle')
    triggerSearch(barcode)
  }

  // Function: handlePlace
  const handlePlace = async () => {
    if (!chemical || !selectedRackId) return
    const occ = rackOccupancy[Number(selectedRackId)] || { 1: null, 2: null, 3: null }
    if (occ[selectedCompartment]) {
      setError(`Compartment C${selectedCompartment} is occupied. Please select an empty compartment.`)
      return
    }
    setPlacing(true)
    setError('')
    try {
      const res = await placeChemical({
        chemical_barcode: barcode.trim(),
        rack_id: Number(selectedRackId),
        scientist_id: scientist.id,
        compartment: selectedCompartment,
      })
      const msg = res.data.message || null
      setReassignmentMsg(msg)
      setPlaced(true)
      setTimeout(() => onClose(true), msg ? 3500 : 1800)
    } catch (err) {
      setError(mapPlacementError(err))
      setPlacing(false)
    }
  }

  const isScanning = scanPhase === 'scanning' || scanPhase === 'typing'

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded shadow-2xl w-full max-w-md overflow-hidden">

        {/* Modal header */}
        <div className="px-6 py-4 flex items-start justify-between text-white" style={{ background: '#106EBE' }}>
          <div>
            <h2 className="text-base font-semibold">Place Chemical</h2>
            <p className="text-sm text-white/75">
              {scientist.name} &nbsp;·&nbsp; <span className="font-mono">{scientist.code}</span>
            </p>
          </div>
          <button type="button" onClick={onClose} className="text-white/75 hover:text-white mt-0.5">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Placed success state */}
        {placed ? (
          <PlacedSuccessView reassignmentMsg={reassignmentMsg} />
        ) : (
          <PlacementForm
            scientist={scientist}
            rackOccupancy={rackOccupancy}
            selectedRackId={selectedRackId}
            setSelectedRackId={setSelectedRackId}
            selectedCompartment={selectedCompartment}
            setSelectedCompartment={setSelectedCompartment}
            scanPhase={scanPhase}
            isScanning={isScanning}
            typedBarcode={typedBarcode}
            handleSimulateScan={handleSimulateScan}
            barcode={barcode}
            setBarcode={setBarcode}
            setChemical={setChemical}
            setError={setError}
            setScanPhase={setScanPhase}
            handleManualSearch={handleManualSearch}
            searching={searching}
            error={error}
            chemical={chemical}
            onClose={onClose}
            handlePlace={handlePlace}
            placing={placing}
          />
        )}
      </div>
    </div>
  )
}
