// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * AIDetailModal.jsx
// Date: 2025-10-16
// ---------------------------------------------------------------------------
/**
 * AIDetailModal.jsx
 * L2: Filterable list of AI analysis items (hotspots, blockers, services, rules, paths, phases)
 * L3: Full detail card — click any L2 row to drill in, Back button returns to L2
 */
import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X, ChevronLeft, Search, ArrowRight,
  TrendingDown, Cloud, Network, BookOpen, Rocket, Calendar,
  AlertTriangle, Tag,
} from 'lucide-react'

// ── Badge helper ──────────────────────────────────────────────────────────────
// Function: Badge
function Badge({ label, cls }) {
  if (!label) return null
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded whitespace-nowrap ${cls || 'bg-gray-100 text-blue-600'}`}>
      {label}
    </span>
  )
}

// ── Shared detail-row ─────────────────────────────────────────────────────────
// Function: DetailRow
function DetailRow({ label, value, mono }) {
  if (value == null || value === '') return null
  return (
    <div className="flex justify-between items-start gap-4 py-1.5 border-b border-gray-100 last:border-0">
      <span className="text-xs text-blue-400 shrink-0">{label}</span>
      <span className={`text-xs text-right break-all ${mono ? 'font-mono text-blue-700' : 'text-blue-800'}`}>{value}</span>
    </div>
  )
}

// Function: TextBlock
function TextBlock({ label, text, colorCls = 'bg-gray-50', textCls = 'text-blue-800', labelCls = 'text-blue-500' }) {
  if (!text) return null
  return (
    <div className={`rounded-xl p-4 ${colorCls}`}>
      <p className={`text-xs font-semibold mb-1 ${labelCls}`}>{label}</p>
      <p className="text-sm leading-relaxed">{text}</p>
    </div>
  )
}

// ── Colour maps (mirrors per-panel maps) ──────────────────────────────────────
const PRIORITY_CLS = { high: 'bg-red-100 text-red-700', medium: 'bg-yellow-100 text-yellow-700', low: 'bg-green-100 text-green-700' }
const SEV_CLS      = { critical: 'bg-red-100 text-red-700', high: 'bg-orange-100 text-orange-700', medium: 'bg-yellow-100 text-yellow-700', low: 'bg-green-100 text-green-700' }
const TYPE_CLS     = { validation: 'bg-blue-100 text-blue-700', calculation: 'bg-purple-100 text-purple-700', workflow: 'bg-green-100 text-green-700', 'access-control': 'bg-red-100 text-red-700', integration: 'bg-orange-100 text-orange-700', 'data-transform': 'bg-teal-100 text-teal-700' }
const CAT_CLS      = { framework: 'bg-blue-100 text-blue-700', language: 'bg-purple-100 text-purple-700', database: 'bg-orange-100 text-orange-700', messaging: 'bg-teal-100 text-teal-700', cloud: 'bg-sky-100 text-sky-700', security: 'bg-red-100 text-red-700' }
const CONF_CLS     = { high: 'text-green-600', medium: 'text-yellow-600', low: 'text-blue-400' }
const RISK_CLS     = { low: 'text-green-600', medium: 'text-yellow-600', high: 'text-red-600' }

// ═══════════════════════════════════════════════════════════════════════════
//  L3  DETAIL  CARDS
// ═══════════════════════════════════════════════════════════════════════════
// Function: HotspotDetail
function HotspotDetail({ item }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge label={(item.priority || '').toUpperCase()} cls={PRIORITY_CLS[item.priority] || 'bg-gray-100 text-blue-600'} />
        <code className="text-xs bg-gray-100 px-2 py-0.5 rounded text-blue-700 break-all">{item.file}</code>
        {item.effort_days > 0 && <span className="ml-auto text-xs font-semibold bg-gray-100 px-2 py-0.5 rounded">~{item.effort_days}d</span>}
      </div>
      <TextBlock label="Issue" text={item.issue}        colorCls="bg-orange-50" labelCls="text-orange-600" />
      <TextBlock label="Fix / Recommendation" text={item.recommendation} colorCls="bg-indigo-50" labelCls="text-indigo-600" />
      <TextBlock label="Root Cause" text={item.root_cause} colorCls="bg-amber-50" labelCls="text-amber-700" />
      <TextBlock label="Predicted Impact" text={item.impact} colorCls="bg-red-50" labelCls="text-red-700" />
      {item.category        && <DetailRow label="Category"       value={item.category} />}
      {item.debt_category   && <DetailRow label="Debt Category"  value={item.debt_category} />}
      {item.prediction_confidence != null && <DetailRow label="Prediction Confidence" value={`${item.prediction_confidence}%`} />}
      {item.estimated_hours && <DetailRow label="Effort (hours)" value={item.estimated_hours} />}
      {item.metrics && Object.keys(item.metrics).length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(item.metrics).map(([key, value]) => (
            <div key={key} className="rounded-lg bg-gray-50 px-3 py-2">
              <p className="text-[10px] uppercase tracking-wide text-blue-400">{key.replace(/_/g, ' ')}</p>
              <p className="text-sm font-semibold text-blue-800">{String(value)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Function: BlockerDetail
function BlockerDetail({ item }) {
  const sc = SEV_CLS[item.severity] || 'bg-gray-100 text-blue-700'
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge label={(item.severity || '').toUpperCase()} cls={sc} />
        <span className="font-semibold text-blue-800">{item.title}</span>
        {item.effort_days > 0 && <span className="ml-auto text-xs font-semibold bg-gray-100 px-2 py-0.5 rounded">~{item.effort_days}d</span>}
      </div>
      <TextBlock label="Description" text={item.description} colorCls={`border ${sc} rounded-xl p-4`} />
      <TextBlock label="Remediation" text={item.remediation} colorCls="bg-blue-50" labelCls="text-blue-600" />
      {item.impacted_files_pattern && (
        <div className="bg-gray-50 rounded-xl p-3">
          <p className="text-xs text-blue-500 font-semibold mb-1">Impacted Files Pattern</p>
          <code className="text-xs text-blue-700 break-all">{item.impacted_files_pattern}</code>
        </div>
      )}
    </div>
  )
}

// Function: ServiceDetail
function ServiceDetail({ item }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="w-7 h-7 rounded-full bg-violet-600 text-blue-300 text-xs font-bold flex items-center justify-center shrink-0">
          {item.migration_order || '?'}
        </span>
        <span className="font-semibold text-blue-800 text-base">{item.name}</span>
        {item.api_type && <Badge label={item.api_type} cls="bg-purple-100 text-purple-700" />}
        {item.estimated_size_kloc && <span className="ml-auto text-xs text-blue-500">~{item.estimated_size_kloc} kLOC</span>}
      </div>
      <TextBlock label="Responsibility"     text={item.responsibility}     colorCls="bg-violet-50" labelCls="text-violet-700" />
      <TextBlock label="Suggested Tech Stack" text={item.suggested_tech_stack} colorCls="bg-indigo-50" labelCls="text-indigo-700" />
      {(item.dependencies || []).length > 0 && (
        <div>
          <p className="text-xs text-blue-500 font-semibold mb-1">Dependencies</p>
          <div className="flex flex-wrap gap-1.5">
            {item.dependencies.map((d, i) => (
              <span key={i} className="flex items-center gap-0.5 text-xs bg-gray-100 text-blue-600 px-1.5 py-0.5 rounded">
                <ArrowRight size={10} />{d}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Function: RuleDetail
function RuleDetail({ item }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <code className="text-xs text-blue-400 font-mono">{item.id}</code>
        <span className="font-semibold text-blue-800">{item.title}</span>
        {item.type && <Badge label={item.type} cls={TYPE_CLS[item.type] || 'bg-gray-100 text-blue-600'} />}
        {item.confidence && (
          <span className={`ml-auto text-xs font-semibold ${CONF_CLS[item.confidence] || ''}`}>
            {item.confidence} confidence
          </span>
        )}
      </div>
      <TextBlock label="Description"   text={item.description}   colorCls="bg-emerald-50" labelCls="text-emerald-700" />
      {item.source_evidence && (
        <div className="bg-gray-50 rounded-xl p-3">
          <p className="text-xs text-blue-500 font-semibold mb-1">Source Evidence</p>
          <code className="text-xs text-blue-700 break-all">{item.source_evidence}</code>
        </div>
      )}
      {(item.affected_entities || []).length > 0 && (
        <div>
          <p className="text-xs text-blue-500 font-semibold mb-1">Affected Entities</p>
          <div className="flex flex-wrap gap-1.5">
            {item.affected_entities.map((e, i) => (
              <span key={i} className="text-xs bg-gray-100 border text-blue-600 px-1.5 py-0.5 rounded">{e}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Function: TransformDetail
function TransformDetail({ item }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 flex-wrap">
        {item.category && <Badge label={item.category} cls={CAT_CLS[item.category] || 'bg-gray-100 text-blue-700'} />}
        <span className="text-sm font-mono text-red-600">{item.current}</span>
        <ArrowRight size={14} className="text-blue-400" />
        <span className="text-sm font-mono text-green-700 font-semibold">{item.recommended}</span>
        {item.value_score != null && (
          <span className="ml-auto flex items-center gap-0.5 text-xs text-blue-400">
            Value: <strong className="text-indigo-600">&nbsp;{item.value_score}/10</strong>
          </span>
        )}
        {item.risk && (
          <span className={`text-xs font-semibold ${RISK_CLS[item.risk] || ''}`}>{item.risk} risk</span>
        )}
      </div>
      <TextBlock label="Rationale" text={item.rationale} colorCls="bg-sky-50" labelCls="text-sky-700" />
      {(item.steps || []).length > 0 && (
        <div className="bg-gray-50 rounded-xl p-4">
          <p className="text-xs text-blue-500 font-semibold mb-2">Migration Steps</p>
          <ol className="space-y-1">
            {item.steps.map((s, i) => (
              <li key={i} className="flex gap-2 text-xs text-blue-700">
                <span className="text-sky-500 font-bold shrink-0">{i + 1}.</span>{s}
              </li>
            ))}
          </ol>
        </div>
      )}
      {(item.affected_file_patterns || []).length > 0 && (
        <div className="bg-gray-50 rounded-xl p-4">
          <p className="text-xs text-blue-500 font-semibold mb-2">Affected Source Patterns</p>
          <div className="flex flex-wrap gap-1.5">
            {item.affected_file_patterns.map((pattern, i) => (
              <code key={i} className="text-xs bg-white border border-gray-200 text-blue-700 px-2 py-1 rounded">{pattern}</code>
            ))}
          </div>
        </div>
      )}
      {(item.version_breaking_changes || []).length > 0 && (
        <div className="bg-red-50 rounded-xl p-4">
          <p className="text-xs text-red-700 font-semibold mb-2">Breaking Changes and Controls</p>
          <ul className="space-y-1 list-disc list-inside text-xs text-red-800">
            {item.version_breaking_changes.map((change, i) => <li key={i}>{change}</li>)}
          </ul>
        </div>
      )}
      {(item.business_benefits || []).length > 0 && (
        <div className="bg-green-50 rounded-xl p-4">
          <p className="text-xs text-green-700 font-semibold mb-2">Predicted Business Benefits</p>
          <ul className="space-y-1 list-disc list-inside text-xs text-green-800">
            {item.business_benefits.map((benefit, i) => <li key={i}>{benefit}</li>)}
          </ul>
        </div>
      )}
      {item.effort_months != null && <DetailRow label="Estimated Effort" value={`${item.effort_months} months`} />}
    </div>
  )
}

// Function: PhaseDetail
function PhaseDetail({ item }) {
  const isSky = item._panelColor === 'sky'
  const bgCls  = isSky ? 'bg-sky-50'    : 'bg-indigo-50'
  const lblCls = isSky ? 'text-sky-700' : 'text-indigo-700'
  const numBg  = isSky ? 'bg-sky-600'   : 'bg-indigo-600'
  const phaseItems = item.items || item.tasks || []
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <span className={`w-8 h-8 rounded-full ${numBg} text-blue-300 text-sm font-bold flex items-center justify-center shrink-0`}>
          {item.phase}
        </span>
        <span className="font-semibold text-blue-800">{item.title}</span>
        {(item.duration_weeks || item.duration_months) && (
          <span className="ml-auto text-xs text-blue-400">
            {item.duration_weeks ? `${item.duration_weeks}w` : `${item.duration_months}mo`}
          </span>
        )}
      </div>
      {item.description && <TextBlock label="Description" text={item.description} colorCls={bgCls} labelCls={lblCls} />}
      {phaseItems.length > 0 && (
        <div className={`${bgCls} rounded-xl p-4`}>
          <p className={`text-xs font-semibold mb-2 ${lblCls}`}>Phase Items</p>
          <ul className="space-y-1">
            {phaseItems.map((it, i) => (
              <li key={i} className="flex gap-2 text-xs text-blue-700">
                <ArrowRight size={10} className={`${lblCls} mt-0.5 shrink-0`} />{it}
              </li>
            ))}
          </ul>
        </div>
      )}
      {item.milestone && (
        <p className={`text-xs ${lblCls} italic`}>✓ {item.milestone}</p>
      )}
      {(item.success_criteria || []).length > 0 && (
        <div className="bg-green-50 rounded-xl p-4">
          <p className="text-xs text-green-700 font-semibold mb-2">Exit Criteria</p>
          <ul className="space-y-1 list-disc list-inside text-xs text-green-800">
            {item.success_criteria.map((criterion, i) => <li key={i}>{criterion}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
//  L2  LIST  ROWS
// ═══════════════════════════════════════════════════════════════════════════
// Function: HotspotRow
function HotspotRow({ item, onClick }) {
  return (
    <button onClick={onClick} className="w-full text-left border border-gray-100 rounded-xl p-3 hover:bg-orange-50/60 hover:border-orange-200 transition-colors group">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge label={(item.priority || '').toUpperCase()} cls={PRIORITY_CLS[item.priority] || 'bg-gray-100 text-blue-600'} />
        <code className="text-xs bg-gray-100 px-1.5 rounded text-blue-700 truncate max-w-[240px]">{item.file}</code>
        {item.effort_days > 0 && <span className="ml-auto text-xs text-blue-500">~{item.effort_days}d</span>}
      </div>
      <p className="text-xs text-blue-600 mt-1 line-clamp-1">{item.issue}</p>
    </button>
  )
}

// Function: BlockerRow
function BlockerRow({ item, onClick }) {
  const sc = SEV_CLS[item.severity] || 'bg-gray-100 text-blue-700'
  return (
    <button onClick={onClick} className="w-full text-left border border-gray-100 rounded-xl p-3 hover:bg-red-50/60 hover:border-red-200 transition-colors group">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge label={(item.severity || '').toUpperCase()} cls={sc} />
        <span className="text-sm font-semibold text-blue-800 truncate">{item.title}</span>
        {item.effort_days > 0 && <span className="ml-auto text-xs text-blue-500">~{item.effort_days}d</span>}
      </div>
      <p className="text-xs text-blue-600 mt-1 line-clamp-1">{item.description}</p>
    </button>
  )
}

// Function: ServiceRow
function ServiceRow({ item, onClick }) {
  return (
    <button onClick={onClick} className="w-full text-left border border-violet-100 rounded-xl p-3 hover:bg-violet-50 transition-colors group">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="w-5 h-5 rounded-full bg-violet-600 text-blue-300 text-[10px] font-bold flex items-center justify-center shrink-0">
          {item.migration_order || '?'}
        </span>
        <span className="text-sm font-semibold text-blue-800">{item.name}</span>
        {item.api_type && <Badge label={item.api_type} cls="bg-purple-100 text-purple-700" />}
        {item.estimated_size_kloc && <span className="ml-auto text-xs text-blue-500">~{item.estimated_size_kloc} kLOC</span>}
      </div>
      <p className="text-xs text-blue-600 mt-1 line-clamp-1">{item.responsibility}</p>
    </button>
  )
}

// Function: RuleRow
function RuleRow({ item, onClick }) {
  return (
    <button onClick={onClick} className="w-full text-left border border-gray-100 rounded-xl p-3 hover:bg-emerald-50/60 hover:border-emerald-200 transition-colors group">
      <div className="flex items-center gap-2 flex-wrap">
        <code className="text-xs text-blue-400 font-mono">{item.id}</code>
        {item.type && <Badge label={item.type} cls={TYPE_CLS[item.type] || 'bg-gray-100 text-blue-600'} />}
        <span className="text-sm font-semibold text-blue-800 truncate">{item.title}</span>
        {item.confidence && <span className={`ml-auto text-xs font-semibold ${CONF_CLS[item.confidence] || ''}`}>{item.confidence}</span>}
      </div>
      <p className="text-xs text-blue-600 mt-1 line-clamp-1">{item.description}</p>
    </button>
  )
}

// Function: TransformRow
function TransformRow({ item, onClick }) {
  return (
    <button onClick={onClick} className="w-full text-left border border-gray-100 rounded-xl p-3 hover:bg-sky-50/60 hover:border-sky-200 transition-colors group">
      <div className="flex items-center gap-2 flex-wrap">
        {item.category && <Badge label={item.category} cls={CAT_CLS[item.category] || 'bg-gray-100 text-blue-700'} />}
        <span className="text-xs font-mono text-red-600">{item.current}</span>
        <ArrowRight size={10} className="text-blue-400" />
        <span className="text-xs font-mono text-green-700 font-semibold">{item.recommended}</span>
        {item.value_score != null && <span className="ml-auto text-xs text-indigo-600 font-semibold">{item.value_score}/10</span>}
      </div>
      <p className="text-xs text-blue-600 mt-1 line-clamp-1">{item.rationale}</p>
    </button>
  )
}

// Function: PhaseRow
function PhaseRow({ item, onClick }) {
  const isSky = item._panelColor === 'sky'
  const numBg  = isSky ? 'bg-sky-600' : 'bg-indigo-600'
  return (
    <button onClick={onClick} className="w-full text-left border border-gray-100 rounded-xl p-3 hover:bg-indigo-50/60 hover:border-indigo-200 transition-colors group">
      <div className="flex items-center gap-2 flex-wrap">
        <span className={`w-5 h-5 rounded-full ${numBg} text-blue-300 text-[10px] font-bold flex items-center justify-center shrink-0`}>
          {item.phase}
        </span>
        <span className="text-sm font-semibold text-blue-800">{item.title}</span>
        {(item.duration_weeks || item.duration_months) && (
          <span className="ml-auto text-xs text-blue-400">
            {item.duration_weeks ? `${item.duration_weeks}w` : `${item.duration_months}mo`}
          </span>
        )}
      </div>
      {(item.items || []).length > 0 && (
        <p className="text-xs text-blue-500 mt-1 line-clamp-1">{(item.items || []).join(' · ')}</p>
      )}
    </button>
  )
}

// ── type → config map ─────────────────────────────────────────────────────────
const TYPE_CONFIG = {
  hotspot:   { Icon: TrendingDown, color: 'text-orange-500', RowCmp: HotspotRow,   DetailCmp: HotspotDetail   },
  blocker:   { Icon: Cloud,        color: 'text-blue-500',   RowCmp: BlockerRow,   DetailCmp: BlockerDetail   },
  service:   { Icon: Network,      color: 'text-violet-500', RowCmp: ServiceRow,   DetailCmp: ServiceDetail   },
  rule:      { Icon: BookOpen,     color: 'text-emerald-600',RowCmp: RuleRow,      DetailCmp: RuleDetail      },
  transform: { Icon: Rocket,       color: 'text-sky-600',    RowCmp: TransformRow, DetailCmp: TransformDetail },
  phase:     { Icon: Calendar,     color: 'text-indigo-500', RowCmp: PhaseRow,     DetailCmp: PhaseDetail     },
}

// ── getItemLabel — used for modal's title when an L3 item is selected ─────────
// Function: getItemLabel
function getItemLabel(type, item) {
  if (!item) return ''
  switch (type) {
    case 'hotspot':   return item.file || 'Hotspot'
    case 'blocker':   return item.title || 'Blocker'
    case 'service':   return item.name || 'Service'
    case 'rule':      return item.title || (item.id ? `Rule ${item.id}` : 'Rule')
    case 'transform': return `${item.current || '?'} → ${item.recommended || '?'}`
    case 'phase':     return item.title || `Phase ${item.phase}`
    default:          return 'Detail'
  }
}

// ═══════════════════════════════════════════════════════════════════════════
//  MAIN MODAL
// ═══════════════════════════════════════════════════════════════════════════
// Function: AIDetailModal
export default function AIDetailModal({ type, title, items = [], initialItem = null, onClose }) {
  const cfg = TYPE_CONFIG[type] || TYPE_CONFIG.hotspot
  const { Icon, RowCmp, DetailCmp } = cfg

  const [q, setQ]           = useState('')
  const [selected, setSelected] = useState(initialItem || null)

  // Sync initialItem when it changes from outside (e.g. direct L3 click)
  React.useEffect(() => { setSelected(initialItem || null) }, [initialItem])

  const filtered = useMemo(() => {
    if (!q.trim()) return items
    const lq = q.toLowerCase()
    return items.filter(it => JSON.stringify(it).toLowerCase().includes(lq))
  }, [items, q])

  // Heading shown in header
  const headingLabel = selected ? getItemLabel(type, selected) : title

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center"
      style={{ background: 'rgba(0,0,0,0.60)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <motion.div
        initial={{ y: '100%', opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: '100%', opacity: 0 }}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
        className="w-full max-w-3xl max-h-[85vh] flex flex-col rounded-t-2xl border border-gray-200 bg-white shadow-2xl"
      >
        {/* ── Header ── */}
        <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100 flex-shrink-0">
          {selected && (
            <button
              onClick={() => setSelected(null)}
              className="flex items-center gap-0.5 text-xs text-blue-400 hover:text-gray-700 transition-colors mr-1 shrink-0"
            >
              <ChevronLeft size={14} /> Back
            </button>
          )}
          <Icon size={15} className={`${cfg.color} shrink-0`} />
          <span className="text-sm font-semibold text-blue-800 truncate">{headingLabel}</span>
          {!selected && (
            <span className="text-xs text-blue-400 ml-0.5 shrink-0">({filtered.length}/{items.length})</span>
          )}

          {/* Search — only in L2 */}
          {!selected && (
            <div className="relative ml-auto mr-2">
              <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-blue-400" />
              <input
                value={q}
                onChange={e => setQ(e.target.value)}
                placeholder="Search…"
                className="pl-7 pr-3 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-md text-blue-700 placeholder-gray-400 focus:outline-none focus:border-indigo-400 w-40"
              />
            </div>
          )}

          <button onClick={onClose} className={`text-blue-400 hover:text-gray-700 transition-colors ${selected ? '' : ''}`}>
            <X size={18} />
          </button>
        </div>

        {/* ── Body ── */}
        <div className="overflow-y-auto flex-1 p-5">
          <AnimatePresence mode="wait">
            {selected ? (
              <motion.div
                key="detail"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.18 }}
              >
                <DetailCmp item={selected} />
              </motion.div>
            ) : (
              <motion.div
                key="list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
                className="space-y-2"
              >
                {filtered.length === 0 && (
                  <p className="text-center text-blue-400 text-sm py-10">No items match your filter.</p>
                )}
                {filtered.map((item, i) => (
                  <RowCmp key={i} item={item} onClick={() => setSelected(item)} />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  )
}
