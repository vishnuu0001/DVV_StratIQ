// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (AILabCatalog.jsx)
// Date: 2026-08-14
// ---------------------------------------------------------------------------
// Implements the "AI Lab · Unified Interface" use case described in
// LabRobot/data/Ahlstrom_AI_Lab_Implementation_Usecase.pptx:
//
//   Slide 1 — the six-step end-user journey (Portal -> AI Gateway ->
//   Innovation Zone -> Portal -> AI Gateway -> Enterprise Zone).
//   Slide 2 — the catalog UI itself: one portal, one search box, and two
//   card states — licensed tools that "OPEN" straight away, and new tools
//   that show "REQUEST ACCESS" instead.
//   Slide 3 — the request flow for a tool that isn't licensed yet (Google
//   VEO is the deck's worked example): Gateway risk classification -> a
//   TechM-provisioned scoped/usage-capped sandbox trial in the Innovation
//   Zone -> trial feedback -> Ahlstrom/TechM governance review -> the tool
//   is registered as a governed connector and becomes an ordinary catalog
//   entry from then on.
//
// MOSTLY SIMULATION, ONE REAL CALL — read before touching this file.
// There is no real Copilot/Claude/Runway backend, AI Gateway, or LLM behind
// most of this tab. Gateway risk classification, TechM sandbox provisioning,
// and governance review are still fixed, human-authored outcomes driven by
// simulateProcessingDelay() (a plain setTimeout) — the same heuristic-timer
// pattern PlaceChemicalModal already uses for its barcode-scanner
// simulation. Every transition is still written to a shared, timestamped
// audit trail — this is a deterministic demo of the audit/governance UX,
// not a shortcut that skips it.
//
// The one exception: Google VEO's Innovation Zone trial (see VeoChatPanel
// below) is a real chat — modeled on the Google AI Studio playground —
// backed by POST /api/ai-lab/veo/chat (main.py), which calls Gemini with a
// trial key held server-side, never the browser. VEO itself is a separate,
// billed video model; this is Gemini text standing in as a conversational
// partner so the trial feels live instead of a single canned line. It falls
// back to a fixed simulated reply if the backend call fails, so the demo
// never visibly breaks. main.py also exposes a single-shot
// POST /api/ai-lab/veo/sample with the same real call, kept for a
// non-chat "Generate Sample Output" use if this ever needs to shrink back
// down — nothing here calls it today. Runway and the Studio tools
// (Copilot/Claude) are untouched by this and remain pure simulation — don't
// silently extend the real call to them without the same deliberation this
// notice is asking for.
import { useEffect, useMemo, useRef, useState } from 'react'
import { chatWithVeo } from '../api'
import { useToast } from './Toast'
import DocumentStudio from './DocumentStudio'

// ─── Reference content (verbatim from the deck) ────────────────────────────

const JOURNEY_STEPS = [
  { n: '01', zone: 'Portal', title: 'Browse the catalog',
    body: 'Browse the AI Lab catalog in the unified portal, from Copilot and Claude AI Studio to specialist tools like Google VEO or Runway.' },
  { n: '02', zone: 'AI Gateway', title: 'Request access',
    body: 'Submit a short access request with a use-case note, and the Gateway auto-classifies its risk tier under the EU AI Act.' },
  { n: '03', zone: 'Innovation Zone', title: 'Try it out',
    body: 'Try it out on sample or synthetic data in the Innovation Zone, with no tenant approvals in the way.' },
  { n: '04', zone: 'Portal', title: 'Rate the trial',
    body: "Rate the trial, confirm it's worth pursuing, and flag anything that needs real data or wider scale." },
  { n: '05', zone: 'AI Gateway', title: 'Governance review',
    body: "TechM and Ahlstrom governance look over the request and, if it's a go, open up broader access." },
  { n: '06', zone: 'Enterprise Zone', title: 'Adopted',
    body: "The tool shows up in the user's workspace from then on, with usage, cost and audit tracked centrally." },
]

const RISK_TIER = 'External SaaS tool · sample-data-only risk tier (EU AI Act)'

// Governed tools that open into a document-upload/Q&A Studio simulation
// instead of the generic Enterprise Zone usage panel. Only assistant-style
// tools get a Studio — a video-generation tool that later becomes governed
// (VEO/Runway) still opens the plain usage/audit workspace.
const STUDIO_KIND = {
  'm365-copilot': 'copilot',
  'claude-ai-studio': 'claude',
}

const EMPTY_DOCUMENT_LIBRARY = { documents: [], activeId: null, conversations: {} }

const INITIAL_TOOLS = [
  {
    key: 'm365-copilot', name: 'M365 Copilot', kind: 'Assistant · Productivity',
    tags: ['assistant', 'copilot', 'productivity', 'writing', 'm365'],
    state: 'governed', zone: 'Enterprise Zone',
  },
  {
    key: 'claude-ai-studio', name: 'Claude AI Studio', kind: 'Assistant · Coding & writing',
    tags: ['assistant', 'claude', 'writing', 'coding', 'ai studio'],
    state: 'governed', zone: 'Enterprise Zone',
  },
  {
    key: 'google-veo', name: 'Google VEO', kind: 'Video generation',
    tags: ['video generation', 'veo', 'google'],
    state: 'available', zone: 'Sandbox trial',
  },
  {
    key: 'runway', name: 'Runway', kind: 'Video generation',
    tags: ['video generation', 'runway'],
    state: 'available', zone: 'Sandbox trial',
  },
]

const STATE_META = {
  governed:          { statusLabel: (t) => `Licensed · ${t.zone}`, buttonLabel: 'Open', buttonKind: 'solid' },
  available:         { statusLabel: (t) => `${t.kind} · ${t.zone}`, buttonLabel: 'Request Access', buttonKind: 'outline' },
  classifying:       { statusLabel: () => 'AI Gateway classifying request…', buttonLabel: 'Classifying…', buttonKind: 'busy' },
  provisioning:      { statusLabel: () => 'TechM provisioning sandbox trial…', buttonLabel: 'Provisioning…', buttonKind: 'busy' },
  trial:             { statusLabel: (t) => `Sandbox trial active · ${t.zone}`, buttonLabel: 'Try in Sandbox', buttonKind: 'outline' },
  governance_review: { statusLabel: () => 'Pending governance review · TechM & Ahlstrom', buttonLabel: 'Under Review', buttonKind: 'disabled' },
}

// Function: nowLabel
function nowLabel() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// Function: simulateProcessingDelay
// A heuristic pacing timer, not a network/LLM call — see the file header.
function simulateProcessingDelay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// ─── Small building blocks ──────────────────────────────────────────────────

// Function: ToolIcon
function ToolIcon() {
  return (
    <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style={{ background: '#0078D4' }}>
      <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
        <path d="M13 3L4 14h6l-1 7 9-11h-6l1-7z" />
      </svg>
    </div>
  )
}

// Function: JourneyStrip
function JourneyStrip() {
  const [open, setOpen] = useState(false)
  return (
    <div className="rounded-lg border shadow-fluent mb-5 bg-white" style={{ borderColor: '#EDEBE9' }}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-3 text-left"
      >
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.14em]" style={{ color: '#0078D4' }}>
            AI Lab · End User Journey
          </p>
          <p className="text-sm font-semibold" style={{ color: '#201F1E' }}>
            From discovery to daily use, in one front door
          </p>
        </div>
        <svg
          className="w-5 h-5 transition-transform shrink-0"
          style={{ color: '#605E5C', transform: open ? 'rotate(180deg)' : 'none' }}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="px-5 pb-5">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {JOURNEY_STEPS.map((step) => (
              <div key={step.n} className="rounded-lg border p-3" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center text-white shrink-0" style={{ background: '#0078D4' }}>
                    {step.n}
                  </span>
                  <span className="text-[10px] font-bold uppercase tracking-wide" style={{ color: '#5C2E91' }}>{step.zone}</span>
                </div>
                <p className="text-xs font-semibold mb-1" style={{ color: '#201F1E' }}>{step.title}</p>
                <p className="text-[11px] leading-snug" style={{ color: '#605E5C' }}>{step.body}</p>
              </div>
            ))}
          </div>
          <p className="text-xs mt-3" style={{ color: '#605E5C' }}>
            <span className="font-semibold" style={{ color: '#201F1E' }}>One front door:</span>{' '}
            these same six steps hold whether it's Copilot, Claude, or a brand-new request like VEO or Runway.
          </p>
        </div>
      )}
    </div>
  )
}

// Function: ToolButton
function ToolButton({ tool, onClick }) {
  const meta = STATE_META[tool.state]
  const busy = meta.buttonKind === 'busy'
  const disabled = meta.buttonKind === 'disabled' || busy
  const base = 'w-full rounded-full py-2.5 text-sm font-bold tracking-wide transition-colors flex items-center justify-center gap-2'
  if (meta.buttonKind === 'solid') {
    return (
      <button type="button" onClick={onClick} className={base} style={{ background: '#0078D4', color: '#FFFFFF' }}>
        {meta.buttonLabel.toUpperCase()}
      </button>
    )
  }
  if (meta.buttonKind === 'outline') {
    return (
      <button type="button" onClick={onClick} className={`${base} border-2 bg-white`} style={{ borderColor: '#0078D4', color: '#0078D4' }}>
        {meta.buttonLabel.toUpperCase()}
      </button>
    )
  }
  return (
    <button type="button" disabled={disabled} className={`${base} border`} style={{ borderColor: '#D2D0CE', color: '#8A8886', background: '#F3F2F1' }}>
      {busy && (
        <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
      )}
      {meta.buttonLabel.toUpperCase()}
    </button>
  )
}

// Function: ToolCard
function ToolCard({ tool, onPrimaryAction }) {
  const meta = STATE_META[tool.state]
  const governed = tool.state === 'governed'
  return (
    <div
      className="rounded-2xl border-2 bg-white p-5 flex flex-col shadow-fluent"
      style={{ borderColor: governed || tool.state === 'trial' ? '#0078D4' : '#C7E0F4' }}
    >
      <ToolIcon />
      <p className="font-bold text-base mt-4" style={{ color: '#0B1220' }}>{tool.name}</p>
      <p className="text-sm mt-1 mb-6" style={{ color: '#605E5C' }}>{meta.statusLabel(tool)}</p>
      {tool.state === 'governance_review' && (
        <p className="text-[11px] mb-2" style={{ color: '#8A8886' }}>
          Waiting in the Governance Review Queue below.
        </p>
      )}
      <div className="mt-auto">
        <ToolButton tool={tool} onClick={() => onPrimaryAction(tool)} />
      </div>
    </div>
  )
}

// Function: Modal
function Modal({ title, subtitle, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded shadow-2xl w-full max-w-lg overflow-hidden max-h-[88vh] flex flex-col">
        <div className="px-6 py-4 flex items-start justify-between text-white shrink-0" style={{ background: 'linear-gradient(135deg, #106EBE, #0078D4)' }}>
          <div>
            <h2 className="text-base font-semibold">{title}</h2>
            {subtitle && <p className="text-sm text-white/80 mt-0.5">{subtitle}</p>}
          </div>
          <button type="button" onClick={onClose} className="text-white/75 hover:text-white mt-0.5">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="p-6 space-y-4 overflow-y-auto">{children}</div>
      </div>
    </div>
  )
}

// Function: GovernanceQueue
// TechM/Ahlstrom governance is a real review, not something an algorithm can
// decide — this panel is the deliberately-labeled demo stand-in a presenter
// uses to move a request past that human step (Slide 1, step 05).
function GovernanceQueue({ tools, onDecide }) {
  if (tools.length === 0) return null
  return (
    <div className="rounded-lg border shadow-fluent mb-5" style={{ borderColor: '#F0CB55', background: '#FFF9E5' }}>
      <div className="px-4 py-3 border-b" style={{ borderColor: '#F0CB55' }}>
        <p className="text-sm font-semibold" style={{ color: '#835C00' }}>Governance Review Queue — TechM &amp; Ahlstrom</p>
        <p className="text-xs mt-0.5" style={{ color: '#835C00' }}>
          Demo control: a real review happens off-platform; use this to simulate the decision coming back.
        </p>
      </div>
      <div className="divide-y" style={{ borderColor: '#F0CB55' }}>
        {tools.map((tool) => (
          <div key={tool.key} className="px-4 py-3 flex items-center justify-between gap-3 flex-wrap">
            <p className="text-sm font-semibold" style={{ color: '#201F1E' }}>{tool.name}</p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => onDecide(tool, false)}
                className="text-xs font-semibold px-3 py-1.5 rounded border transition-colors"
                style={{ borderColor: '#A19F9D', color: '#3B3A39', background: '#FFFFFF' }}
              >
                Needs More Info
              </button>
              <button
                type="button"
                onClick={() => onDecide(tool, true)}
                className="text-xs font-semibold px-3 py-1.5 rounded transition-colors text-white"
                style={{ background: '#107C10' }}
              >
                Approve
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Function: AuditTrail
function AuditTrail({ entries }) {
  return (
    <div className="rounded-lg border bg-white shadow-fluent" style={{ borderColor: '#EDEBE9' }}>
      <div className="px-4 py-3 border-b flex items-center justify-between" style={{ borderColor: '#EDEBE9' }}>
        <p className="text-sm font-semibold" style={{ color: '#201F1E' }}>Audit Trail</p>
        <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold" style={{ background: '#DFF6DD', color: '#0B6A0B' }}>
          Same identity · policy · audit
        </span>
      </div>
      <div className="max-h-56 overflow-y-auto divide-y" style={{ borderColor: '#F3F2F1' }}>
        {entries.length === 0 && (
          <p className="text-xs px-4 py-4" style={{ color: '#8A8886' }}>
            No activity yet — request access to a tool below to see the Gateway, sandbox, and governance events land here.
          </p>
        )}
        {entries.map((e) => (
          <div key={e.id} className="px-4 py-2.5 flex items-start gap-3">
            <span className="text-[11px] font-mono mt-0.5 shrink-0" style={{ color: '#A19F9D' }}>{e.time}</span>
            <div className="min-w-0">
              <p className="text-xs font-semibold" style={{ color: '#106EBE' }}>{e.tool}</p>
              <p className="text-xs" style={{ color: '#3B3A39' }}>{e.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Main component ─────────────────────────────────────────────────────────

// Function: AILabCatalog
export default function AILabCatalog() {
  const toast = useToast()
  const [tools, setTools] = useState(INITIAL_TOOLS)
  const [query, setQuery] = useState('')
  const [auditLog, setAuditLog] = useState([])
  const [requestModal, setRequestModal] = useState(null)   // tool being requested
  const [trialModal, setTrialModal] = useState(null)       // tool being trialed
  const [workspaceModal, setWorkspaceModal] = useState(null) // governed non-Studio tool being "opened"
  const [studioModal, setStudioModal] = useState(null)      // governed Studio tool (Copilot/Claude) being "opened"
  // Per-tool document library ({ documents, activeId, conversations }),
  // keyed by tool.key. Lives here, not inside DocumentStudio, specifically
  // so closing the Studio (unmounting DocumentStudio) doesn't throw away
  // everything uploaded so far — reopening it (or switching tabs and back)
  // shows the same documents and conversations. In-memory only: a page
  // reload still clears it, since there's no backend store behind this tab.
  const [documentLibraries, setDocumentLibraries] = useState({})

  // Function: logEvent
  const logEvent = (tool, message) => {
    setAuditLog((log) => [{ id: `${Date.now()}-${Math.random()}`, time: nowLabel(), tool: tool.name, message }, ...log].slice(0, 30))
  }

  // Function: updateTool
  const updateTool = (key, patch) => {
    setTools((prev) => prev.map((t) => (t.key === key ? { ...t, ...patch } : t)))
  }

  const filteredTools = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return tools
    return tools.filter((t) =>
      t.name.toLowerCase().includes(q) ||
      t.kind.toLowerCase().includes(q) ||
      t.tags.some((tag) => tag.includes(q))
    )
  }, [tools, query])

  const licensedCount = tools.filter((t) => t.state === 'governed').length
  const requestableCount = tools.filter((t) => t.state === 'available').length
  const inFlightCount = tools.length - licensedCount - requestableCount

  // Function: handlePrimaryAction
  const handlePrimaryAction = (tool) => {
    if (tool.state === 'governed') {
      if (STUDIO_KIND[tool.key]) { setStudioModal(tool) } else { setWorkspaceModal(tool) }
      return
    }
    if (tool.state === 'available') { setRequestModal({ ...tool, useCase: '' }); return }
    if (tool.state === 'trial') { setTrialModal({ ...tool, rated: false, worthPursuing: false, needsMoreData: false }); return }
    // classifying / provisioning / governance_review — no action, card explains status
  }

  // Function: submitUseCase
  const submitUseCase = async (tool, useCase) => {
    setRequestModal(null)
    updateTool(tool.key, { state: 'classifying', useCase })
    logEvent(tool, `Access requested — use case: "${useCase || 'not specified'}"`)
    toast(`Request submitted for ${tool.name}. Routing through the AI Gateway…`, 'info')

    await simulateProcessingDelay(1100)
    updateTool(tool.key, { state: 'provisioning' })
    logEvent(tool, `AI Gateway classified the request: ${RISK_TIER}`)

    await simulateProcessingDelay(1100)
    updateTool(tool.key, { state: 'trial', zone: 'Innovation Zone' })
    logEvent(tool, 'TechM provisioned a scoped, usage-capped API key — sandbox trial ready in the Innovation Zone (no direct login handed over).')
    toast(`${tool.name} sandbox trial is ready in the Innovation Zone.`, 'success')
  }

  // Function: submitGovernanceReview
  const submitGovernanceReview = (tool, feedback) => {
    setTrialModal(null)
    updateTool(tool.key, { state: 'governance_review' })
    const flags = [
      feedback.worthPursuing ? 'confirmed worth pursuing' : null,
      feedback.needsMoreData ? 'flagged as needing real data / wider scale' : null,
    ].filter(Boolean).join(', ') || 'no flags raised'
    logEvent(tool, `Trial feedback submitted (${flags}) — routed to TechM & Ahlstrom governance for review.`)
    toast(`${tool.name} trial feedback sent for governance review.`, 'info')
  }

  // Function: decideGovernance
  const decideGovernance = (tool, approved) => {
    if (approved) {
      updateTool(tool.key, { state: 'governed', zone: 'Enterprise Zone' })
      logEvent(tool, 'Governance approved — registered as a governed connector in the Enterprise Zone. Usage, cost and audit now tracked centrally.')
      toast(`🎉 ${tool.name} is approved — it now opens straight from the catalog.`, 'success')
    } else {
      updateTool(tool.key, { state: 'trial' })
      logEvent(tool, 'Governance requested more evidence — returned to the Innovation Zone trial.')
      toast(`${tool.name} was sent back to trial for more evidence.`, 'warning')
    }
  }

  return (
    <div>
      <JourneyStrip />

      {/* Catalog card — mirrors the deck's "What the user actually sees" mockup */}
      <div className="rounded-2xl border shadow-fluent overflow-hidden mb-5" style={{ borderColor: '#C7E0F4' }}>
        <div className="px-6 py-4" style={{ background: 'linear-gradient(135deg, #0B2545, #0A2A4A)' }}>
          <p className="text-white font-semibold">AI Lab · Tool Catalog</p>
        </div>
        <div className="p-6 bg-white">
          <label className="flex items-center gap-2.5 rounded-full px-4 py-3 mb-6" style={{ background: '#EEF2FA' }}>
            <svg className="w-4 h-4 shrink-0" style={{ color: '#605E5C' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z" />
            </svg>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search tools — e.g. 'video generation', 'copilot', 'claude'"
              className="flex-1 bg-transparent text-sm outline-none"
              style={{ color: '#201F1E' }}
            />
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {filteredTools.map((tool) => (
              <ToolCard key={tool.key} tool={tool} onPrimaryAction={handlePrimaryAction} />
            ))}
          </div>
          {filteredTools.length === 0 && (
            <p className="text-sm text-center py-10" style={{ color: '#8A8886' }}>No tools match "{query}".</p>
          )}
        </div>
        <div className="px-6 py-4 text-sm text-center" style={{ background: 'linear-gradient(135deg, #0B2545, #0A2A4A)' }}>
          <span className="font-semibold" style={{ color: '#67E8F9' }}>Same portal, two states:</span>{' '}
          <span className="text-white/90">
            {licensedCount} tool{licensedCount === 1 ? '' : 's'} open right away, {requestableCount} new tool{requestableCount === 1 ? '' : 's'} show{requestableCount === 1 ? 's' : ''} "Request Access"
            {inFlightCount > 0 && <> ({inFlightCount} in flight through the Gateway)</>} — every path runs through the same AI Gateway.
          </span>
        </div>
      </div>

      <GovernanceQueue
        tools={tools.filter((t) => t.state === 'governance_review')}
        onDecide={decideGovernance}
      />

      <AuditTrail entries={auditLog} />

      {/* ── Request Access modal (Slide 3, steps 1-3) ──────────────────── */}
      {requestModal && (
        <Modal
          title={`Request Access — ${requestModal.name}`}
          subtitle="Describe the use case; the AI Gateway classifies the risk tier automatically."
          onClose={() => setRequestModal(null)}
        >
          <div>
            <label className="block text-xs font-bold uppercase tracking-wide mb-1.5" style={{ color: '#605E5C' }}>
              Use-case note
            </label>
            <textarea
              rows={3}
              value={requestModal.useCase}
              onChange={(e) => setRequestModal((m) => ({ ...m, useCase: e.target.value }))}
              placeholder="e.g. Draft a marketing video from sample brand assets"
              className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2"
              style={{ borderColor: '#8A8886', color: '#201F1E' }}
            />
          </div>
          <div className="rounded border px-4 py-3 text-xs" style={{ background: '#DEECF9', borderColor: '#A9D3F2', color: '#004578' }}>
            After you submit, the Gateway auto-classifies this as an <strong>{RISK_TIER}</strong>, and TechM
            opens a scoped, usage-capped sandbox trial in the Innovation Zone — no direct login to {requestModal.name} is ever handed over.
          </div>
          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={() => setRequestModal(null)}
              className="flex-1 border font-semibold py-2.5 rounded transition-colors text-sm"
              style={{ borderColor: '#8A8886', color: '#201F1E' }}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => submitUseCase(requestModal, requestModal.useCase.trim())}
              className="flex-1 bg-azure-600 hover:bg-azure-700 text-white font-semibold py-2.5 rounded transition-colors text-sm"
            >
              Submit Request
            </button>
          </div>
        </Modal>
      )}

      {/* ── Innovation Zone trial modal (Slide 1 step 03-04, Slide 3 step 4) ── */}
      {trialModal && (
        <Modal
          title={`Innovation Zone — ${trialModal.name}`}
          subtitle="Sample or synthetic data only. No tenant approvals in the way."
          onClose={() => setTrialModal(null)}
        >
          <TrialForm
            tool={trialModal}
            toast={toast}
            onSubmit={(feedback) => submitGovernanceReview(trialModal, feedback)}
            onCancel={() => setTrialModal(null)}
          />
        </Modal>
      )}

      {/* ── Enterprise Zone workspace (Slide 1 step 06) ────────────────── */}
      {workspaceModal && (
        <Modal
          title={`${workspaceModal.name} — Enterprise Zone`}
          subtitle="Governed connector · usage, cost and audit tracked centrally"
          onClose={() => setWorkspaceModal(null)}
        >
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded border px-3 py-3" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
              <p className="text-[10px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Requests (30d)</p>
              <p className="text-xl font-bold" style={{ color: '#201F1E' }}>1,248</p>
            </div>
            <div className="rounded border px-3 py-3" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
              <p className="text-[10px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Est. cost (30d)</p>
              <p className="text-xl font-bold" style={{ color: '#201F1E' }}>$186</p>
            </div>
            <div className="rounded border px-3 py-3" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
              <p className="text-[10px] uppercase tracking-wide font-semibold" style={{ color: '#605E5C' }}>Risk tier</p>
              <p className="text-sm font-bold mt-1" style={{ color: '#0B6A0B' }}>Enterprise · Licensed</p>
            </div>
          </div>
          <div className="rounded border px-4 py-3 text-sm" style={{ background: '#DFF6DD', borderColor: '#9FD89B', color: '#0B6A0B' }}>
            Opening {workspaceModal.name} in the Enterprise Zone with your portal identity — same policy and audit trail as every other governed tool.
          </div>
        </Modal>
      )}

      {/* ── Copilot Studio / Claude Studio document Q&A simulation ─────── */}
      {studioModal && (
        <DocumentStudio
          tool={studioModal}
          studioKind={STUDIO_KIND[studioModal.key]}
          library={documentLibraries[studioModal.key] || EMPTY_DOCUMENT_LIBRARY}
          onLibraryChange={(updater) => setDocumentLibraries((prev) => ({
            ...prev,
            [studioModal.key]: typeof updater === 'function'
              ? updater(prev[studioModal.key] || EMPTY_DOCUMENT_LIBRARY)
              : updater,
          }))}
          onClose={() => setStudioModal(null)}
        />
      )}
    </div>
  )
}

// Function: VeoChatPanel
// A minimal chat playground — modeled on the Google AI Studio prompt
// interface — for the Google VEO trial. Every reply here is a real Gemini
// turn via chatWithVeo() (see the file header notice), not a canned line.
// State lives in this component so leaving and reopening the trial modal
// starts a fresh conversation, matching "sandbox trial" — nothing here is
// meant to persist.
// Function: makeMessageId
let messageSeq = 0
const makeMessageId = () => `veo-msg-${Date.now()}-${messageSeq++}`

function VeoChatPanel({ tool, toast, onExchange }) {
  const [messages, setMessages] = useState([
    { id: makeMessageId(), role: 'model', text: "Tell me what you'd like the sample video to show, and I'll describe it back to you." },
  ])
  const [draft, setDraft] = useState(tool.useCase || '')
  const [sending, setSending] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    const node = scrollRef.current
    if (node) node.scrollTop = node.scrollHeight
  }, [messages, sending])

  // Function: send
  const send = async () => {
    const text = draft.trim()
    if (!text || sending) return
    const nextMessages = [...messages, { id: makeMessageId(), role: 'user', text }]
    setMessages(nextMessages)
    setDraft('')
    setSending(true)
    try {
      const { data } = await chatWithVeo(nextMessages)
      setMessages((prev) => [...prev, { id: makeMessageId(), role: 'model', text: data.reply }])
    } catch {
      toast?.('Live chat unavailable — showing a simulated reply instead.', 'warning')
      setMessages((prev) => [...prev, {
        id: makeMessageId(),
        role: 'model',
        text: `Here's a synthetic sample based on that: a short clip built from placeholder brand assets illustrating "${text}".`,
      }])
    }
    setSending(false)
    onExchange?.()
  }

  // Function: onKeyDown
  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="rounded border overflow-hidden" style={{ borderColor: '#EDEBE9' }}>
      <div className="px-3 py-2 border-b flex items-center justify-between" style={{ borderColor: '#EDEBE9', background: '#FAF9F8' }}>
        <p className="text-xs font-bold uppercase tracking-wide" style={{ color: '#605E5C' }}>
          Sandbox chat · sample / synthetic data only
        </p>
        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{ background: '#DFF6DD', color: '#0B6A0B' }}>
          Live
        </span>
      </div>
      <div ref={scrollRef} className="px-3 py-3 space-y-2 overflow-y-auto" style={{ maxHeight: 240, background: '#FFFFFF' }}>
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <p
              className="max-w-[85%] rounded-lg px-3 py-2 text-xs leading-snug whitespace-pre-wrap"
              style={m.role === 'user' ? { background: '#0078D4', color: '#FFFFFF' } : { background: '#F3F2F1', color: '#201F1E' }}
            >
              {m.text}
            </p>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <p className="rounded-lg px-3 py-2 text-xs" style={{ background: '#F3F2F1', color: '#8A8886' }}>Generating…</p>
          </div>
        )}
      </div>
      <div className="flex items-end gap-2 px-3 py-2.5 border-t" style={{ borderColor: '#EDEBE9' }}>
        <textarea
          rows={1}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Describe the video you want, or ask a follow-up…"
          className="flex-1 resize-none border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2"
          style={{ borderColor: '#8A8886', color: '#201F1E' }}
        />
        <button
          type="button"
          onClick={send}
          disabled={sending || !draft.trim()}
          className="rounded px-4 py-2 text-sm font-semibold text-white transition-colors disabled:opacity-50"
          style={{ background: '#0078D4' }}
        >
          Send
        </button>
      </div>
    </div>
  )
}

// Function: TrialForm
function TrialForm({ tool, toast, onSubmit, onCancel }) {
  const isVeo = tool.key === 'google-veo'
  const [generated, setGenerated] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [sampleText, setSampleText] = useState('')
  const [worthPursuing, setWorthPursuing] = useState(true)
  const [needsMoreData, setNeedsMoreData] = useState(false)

  const FALLBACK_SAMPLE = `Sample output generated from synthetic brand assets — ${tool.name} trial run complete.`

  // Function: runSample
  // Simulated single-shot generation for every trial tool except Google
  // VEO, which gets the live chat panel above instead (see file header).
  const runSample = async () => {
    setGenerating(true)
    setGenerated(false)
    await simulateProcessingDelay(900)
    setSampleText(FALLBACK_SAMPLE)
    setGenerating(false)
    setGenerated(true)
  }

  return (
    <>
      {isVeo ? (
        <VeoChatPanel tool={tool} toast={toast} onExchange={() => setGenerated(true)} />
      ) : (
        <div className="rounded p-4" style={{ background: '#252423' }}>
          <p className="text-xs font-bold uppercase tracking-wide mb-2" style={{ color: '#D2D0CE' }}>
            Sample / synthetic data only
          </p>
          <button
            type="button"
            onClick={runSample}
            disabled={generating}
            className="w-full text-white font-bold py-2.5 rounded text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
            style={{ background: '#0078D4' }}
          >
            {generating ? (
              <>
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Generating…
              </>
            ) : 'Generate Sample Output'}
          </button>
          {generated && (
            <p className="mt-3 text-xs font-mono" style={{ color: '#6FCF97' }}>
              ✓ {sampleText}
            </p>
          )}
        </div>
      )}

      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm" style={{ color: '#201F1E' }}>
          <input type="checkbox" checked={worthPursuing} onChange={(e) => setWorthPursuing(e.target.checked)} className="w-4 h-4" />
          Confirm this is worth pursuing
        </label>
        <label className="flex items-center gap-2 text-sm" style={{ color: '#201F1E' }}>
          <input type="checkbox" checked={needsMoreData} onChange={(e) => setNeedsMoreData(e.target.checked)} className="w-4 h-4" />
          Flag: needs real data or wider scale
        </label>
      </div>

      <div className="flex gap-3 pt-1">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 border font-semibold py-2.5 rounded transition-colors text-sm"
          style={{ borderColor: '#8A8886', color: '#201F1E' }}
        >
          Keep Trialing
        </button>
        <button
          type="button"
          onClick={() => onSubmit({ worthPursuing, needsMoreData })}
          disabled={!generated}
          className="flex-1 bg-azure-600 hover:bg-azure-700 text-white font-semibold py-2.5 rounded transition-colors text-sm disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Submit for Governance Review
        </button>
      </div>
    </>
  )
}
