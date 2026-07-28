// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/pages (ExecutiveCockpit.jsx)
// Date: 2025-10-03
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Layers,
  AlertTriangle,
  GitBranch,
  CheckCircle,
  Clock,
  Zap,
  Activity,
  Shield,
  BarChart2,
  Repeat,
  UserCheck,
  TrendingUp,
  TrendingDown,
  Target,
  ChevronRight,
  ArrowRight,
} from 'lucide-react'
import DrilldownDrawer from '../components/DrilldownDrawer'
import ExportPDFButton from '../components/ExportPDFButton'
import { FRM_METRICS } from '../data/frmData'
import {
  getKPIs,
  getInsights,
  getIncidents,
  getRepeatIncidents,
  getRCAOwnership,
  getMonthlyVolume,
  getApplicationHotspots,
  getAutomationCandidates,
  getChanges,
  getServiceRequests,
} from '../api'
import { useDashboard } from '../context/DashboardContext'

// ---------------------------------------------------------------------------
// Rolling Alert Ticker
// ---------------------------------------------------------------------------
// Function: AlertTicker
function AlertTicker({ alerts }) {
  if (!alerts || alerts.length === 0) return null
  const text = alerts
    .map((a) => `🔴 [${a.priority || 'P1 CRITICAL'}]  ${a.number} — ${a.short_description}`)
    .join('          ●          ')
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 gradient-bg-danger border-t-2 border-accent-rose/50 overflow-hidden flex items-stretch shadow-elevation-3">
      <div className="flex-shrink-0 flex items-center gap-2 px-4 py-2 bg-red-500/85 text-white text-[11px] font-bold uppercase tracking-wider whitespace-nowrap">
        <span className="relative flex h-2 w-2 mr-1">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-300 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-200" />
        </span>
        CRITICAL ALERT
      </div>
      <div className="flex-1 overflow-hidden py-2">
        <div className="ticker-track text-white text-[11px] font-semibold whitespace-nowrap">
          {text}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{text}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Circular Health Gauge
// ---------------------------------------------------------------------------
// Function: HealthGauge
function HealthGauge({ score }) {
  const pct = Math.min(100, Math.max(0, score ?? 0))
  const color = pct >= 80 ? '#10b981' : pct >= 60 ? '#f59e0b' : '#f43f5e'
  const glow = pct >= 80 ? 'rgba(16,185,129,0.5)' : pct >= 60 ? 'rgba(245,158,11,0.5)' : 'rgba(244,63,94,0.5)'
  const label = pct >= 80 ? 'Healthy' : pct >= 60 ? 'At Risk' : 'Critical'
  const r = 36
  const circ = 2 * Math.PI * r
  const dash = (pct / 100) * circ

  return (
    <div className="flex flex-col items-center justify-center gap-1 py-1">
      <div className="relative" style={{ width: 96, height: 96 }}>
        <svg width="96" height="96" viewBox="0 0 96 96" style={{ transform: 'rotate(-90deg)' }}>
          <defs>
            <linearGradient id="healthGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={color} stopOpacity="0.6" />
              <stop offset="100%" stopColor={color} />
            </linearGradient>
          </defs>
          <circle cx="48" cy="48" r={r} fill="none" stroke="rgba(71,85,105,0.3)" strokeWidth="9" />
          <circle
            cx="48" cy="48" r={r} fill="none"
            stroke={`url(#healthGrad)`}
            strokeWidth="9" strokeLinecap="round"
            strokeDasharray={`${dash} ${circ}`}
            style={{ filter: `drop-shadow(0 0 6px ${glow})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-xl font-bold leading-none tabular-nums" style={{ color }}>{pct}%</div>
          <div className="text-[9px] text-slate-500 mt-0.5 uppercase tracking-widest">Score</div>
        </div>
      </div>
      <div className="text-xs font-bold tracking-wide" style={{ color }}>{label}</div>
      <div className="text-[10px] text-slate-500">Operational Health</div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Modernized Metric Pill
// ---------------------------------------------------------------------------
// Function: MetricPill
function MetricPill({ label, value, sub, color = 'slate', icon: Icon, pulse, onClick }) {
  const cfg = {
    slate:   { bg: '#f8fbff', border: '#d9e8f8', text: '#334155', accent: '#64748b' },
    rose:    { bg: '#fff2f4', border: '#f8c7d1', text: '#be123c', accent: '#f43f5e' },
    emerald: { bg: '#ecfdf5', border: '#bae6d3', text: '#047857', accent: '#10b981' },
    amber:   { bg: '#fff7ed', border: '#fed7aa', text: '#b45309', accent: '#f59e0b' },
    indigo:  { bg: '#eef2ff', border: '#c7d2fe', text: '#4338ca', accent: '#6366f1' },
    sky:     { bg: '#eff6ff', border: '#bfdbfe', text: '#0369a1', accent: '#38bdf8' },
  }[color] || { bg: '#f8fbff', border: '#d9e8f8', text: '#334155', accent: '#64748b' }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full flex items-center gap-3 rounded-xl px-4 py-3.5 transition-all duration-300
        ${onClick ? 'cursor-pointer hover:-translate-y-1' : 'cursor-default'}`}
      style={{
        background: cfg.bg,
        border: `1px solid ${cfg.border}`,
        boxShadow: onClick ? undefined : undefined,
      }}
      onMouseEnter={(e) => {
        if (onClick) e.currentTarget.style.boxShadow = `0 12px 24px rgba(15,23,42,0.08), 0 0 0 1px ${cfg.accent}40`
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = ''
      }}
    >
      {/* Left accent line */}
      <div className="w-0.5 h-10 rounded-full flex-shrink-0" style={{ background: `linear-gradient(to bottom, ${cfg.accent}, transparent)` }} />

      {Icon && (
        <div className={`p-2 rounded-lg flex-shrink-0 ${pulse ? 'animate-pulse' : ''}`}
             style={{ background: `${cfg.accent}20` }}>
          <Icon className="w-4 h-4" style={{ color: cfg.accent }} />
        </div>
      )}
      <div className="min-w-0 flex-1">
        <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider truncate">{label}</div>
        {value == null
          ? <div className="h-7 w-16 rounded skeleton mt-1" />
          : <div className="text-2xl font-bold leading-tight tabular-nums" style={{ color: cfg.text }}>{value}</div>
        }
        {sub && <div className="text-[10px] text-slate-500 truncate mt-0.5">{sub}</div>}
      </div>
      {onClick && <ChevronRight className="w-4 h-4 text-slate-500 flex-shrink-0 ml-auto" />}
    </button>
  )
}

// ---------------------------------------------------------------------------
// Single insight line
// ---------------------------------------------------------------------------
// Function: InsightLine
function InsightLine({ text, severity }) {
  const dot = severity === 'critical' ? 'bg-accent-rose' : severity === 'warning' ? 'bg-accent-amber' : 'bg-accent-emerald'
  return (
    <li className="flex items-start gap-2 text-xs text-slate-700 py-1.5 border-b border-slate-200 last:border-0">
      <span className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${dot}`} />
      <span>{text}</span>
    </li>
  )
}

// ---------------------------------------------------------------------------
// FRM Roadmap Card — single KPI milestone (Baseline → Y1 → Y3)
// ---------------------------------------------------------------------------
// Function: FRMRoadmapCard
function FRMRoadmapCard({ metric, onClick }) {
  const isUp = metric.direction === 'up'
  const DirectionIcon = isUp ? TrendingUp : TrendingDown

  return (
    <button
      type="button"
      onClick={onClick}
      className="relative flex flex-col p-4 rounded-2xl text-left w-full transition-all duration-300 hover:-translate-y-1.5 group"
      style={{
        background: metric.bgColor,
        border: `1px solid ${metric.borderColor}`,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = `0 12px 32px rgba(0,0,0,0.4), 0 0 0 1px ${metric.accentColor}50, inset 0 1px 0 ${metric.accentColor}20`
        e.currentTarget.style.borderColor = metric.accentColor
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = ''
        e.currentTarget.style.borderColor = metric.borderColor
      }}
    >
      {/* Direction badge */}
      <div className="absolute top-3 right-3 flex items-center gap-1 rounded-full px-1.5 py-0.5"
           style={{ background: `${metric.accentColor}20`, border: `1px solid ${metric.accentColor}40` }}>
        <DirectionIcon className="w-2.5 h-2.5" style={{ color: metric.accentColor }} />
        <span className="text-[9px] font-bold uppercase tracking-wider" style={{ color: metric.accentColor }}>
          {isUp ? 'Up' : 'Down'}
        </span>
      </div>

      {/* Label */}
      <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-4 pr-12">
        {metric.label}
      </div>

      {/* Timeline nodes */}
      <div className="flex-1 space-y-0">
        {/* Baseline */}
        <div className="flex items-start gap-2.5">
          <div className="flex flex-col items-center">
            <div className="w-2.5 h-2.5 rounded-full border-2 border-slate-500 bg-slate-700 flex-shrink-0" />
            <div className="w-px flex-1 min-h-[20px]" style={{ background: `linear-gradient(to bottom, rgba(100,116,139,0.5), ${metric.accentColor}60)` }} />
          </div>
          <div className="pb-2">
            <div className="text-[9px] text-slate-500 font-semibold uppercase tracking-wider leading-none mb-0.5">Baseline</div>
            <div className="text-sm font-semibold text-slate-400">{metric.baseline}</div>
          </div>
        </div>

        {/* Year 1 */}
        <div className="flex items-start gap-2.5">
          <div className="flex flex-col items-center">
            <div className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                 style={{ background: metric.accentColor, boxShadow: `0 0 6px ${metric.glowColor}`, opacity: 0.8 }} />
            <div className="w-px flex-1 min-h-[20px]" style={{ background: `linear-gradient(to bottom, ${metric.accentColor}80, ${metric.accentColor})` }} />
          </div>
          <div className="pb-2">
            <div className="text-[9px] font-semibold uppercase tracking-wider leading-none mb-0.5" style={{ color: `${metric.accentColor}99` }}>Year 1</div>
            <div className="text-sm font-bold" style={{ color: metric.accentColor }}>{metric.year1}</div>
          </div>
        </div>

        {/* Year 3 */}
        <div className="flex items-start gap-2.5">
          <div className="w-3 h-3 rounded-full flex-shrink-0 ring-2 ring-offset-1"
               style={{
                 background: metric.accentColor,
                 boxShadow: `0 0 10px ${metric.glowColor}`,
                 ringColor: metric.accentColor,
                 ringOffsetColor: 'transparent',
               }} />
          <div>
            <div className="text-[9px] font-bold uppercase tracking-wider leading-none mb-0.5" style={{ color: metric.accentColor }}>Year 3 Target</div>
            <div className="text-xl font-extrabold leading-tight" style={{ color: metric.accentColor }}>{metric.year3}</div>
          </div>
        </div>
      </div>

      {/* Drilldown hint */}
      <div className="flex items-center gap-1 mt-3 pt-3 border-t border-slate-700/30 text-[10px] text-slate-500 group-hover:text-slate-400 transition-colors">
        <ArrowRight className="w-3 h-3" />
        <span>Measurement · Owner · Risk</span>
      </div>
    </button>
  )
}

// ---------------------------------------------------------------------------
// Row 1 — Health gauge + 4 hero KPIs
// ---------------------------------------------------------------------------
// Function: slaTierColor
function slaTierColor(pct) {
  if (!pct) return 'slate'
  if (pct >= 90) return 'emerald'
  if (pct >= 75) return 'amber'
  return 'rose'
}

// Function: mttrTierColor
function mttrTierColor(hours) {
  if (!hours) return 'slate'
  if (hours <= 4) return 'emerald'
  if (hours <= 12) return 'amber'
  return 'rose'
}

// Function: HeroKPIRow
function HeroKPIRow({ loading, healthScore, k, openCriticalCount, openDrilldown }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-5 items-stretch animate-slide-up">
      <button
        type="button"
        onClick={() => openDrilldown('executive-overview', 'Operational Health Overview')}
        className="card-modern flex items-center justify-center p-4 hover:-translate-y-1 transition-all duration-300 rounded-2xl"
        style={{ minHeight: 120 }}
      >
        {loading
          ? <div className="h-20 w-24 rounded skeleton" />
          : <HealthGauge score={healthScore} />}
      </button>
      <MetricPill
        label="Total Tickets"
        value={loading ? null : k.total_tickets?.toLocaleString() ?? '—'}
        sub="All ITSM records"
        icon={Layers}
        color="sky"
        onClick={() => openDrilldown('executive-overview', 'Total Tickets Overview')}
      />
      <MetricPill
        label="Open Incidents"
        value={loading ? null : k.total_incidents?.toLocaleString() ?? '—'}
        sub="All severities"
        icon={AlertTriangle}
        color={openCriticalCount > 0 ? 'rose' : 'indigo'}
        pulse={openCriticalCount > 0}
        onClick={() => openDrilldown('incident-mttr', 'Open Incidents Drilldown')}
      />
      <MetricPill
        label="SLA Compliance"
        value={loading ? null : k.sla_compliance_pct != null ? `${k.sla_compliance_pct.toFixed(1)}%` : '—'}
        sub="Within SLA target"
        icon={Shield}
        color={slaTierColor(k.sla_compliance_pct)}
        onClick={() => openDrilldown('service-request-productivity', 'SLA / Service Request Drilldown')}
      />
      <MetricPill
        label="Avg MTTR"
        value={loading ? null : k.avg_mttr_hours != null ? `${k.avg_mttr_hours.toFixed(1)}h` : '—'}
        sub="Mean time to resolve"
        icon={Clock}
        color={mttrTierColor(k.avg_mttr_hours)}
        onClick={() => openDrilldown('incident-mttr', 'MTTR Trend Drilldown')}
      />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Row 2 — Secondary KPIs
// ---------------------------------------------------------------------------
// Function: SecondaryKPIRow
function SecondaryKPIRow({ loading, k, openDrilldown }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6 animate-slide-up">
      <MetricPill
        label="Changes"
        value={loading ? null : k.total_changes?.toLocaleString() ?? '—'}
        sub="All change records"
        icon={GitBranch}
        color="indigo"
        onClick={() => openDrilldown('change-risk', 'Change Records Drilldown')}
      />
      <MetricPill
        label="Emergency Changes"
        value={loading ? null : k.emergency_change_pct != null ? `${k.emergency_change_pct.toFixed(1)}%` : '—'}
        sub="% of total changes"
        icon={AlertTriangle}
        color={!k.emergency_change_pct ? 'slate' : k.emergency_change_pct > 10 ? 'rose' : 'amber'}
        onClick={() => openDrilldown('change-risk', 'Emergency Changes Drilldown')}
      />
      <MetricPill
        label="Avg Cycle Time"
        value={loading ? null : k.avg_cycle_time_hours != null ? `${k.avg_cycle_time_hours.toFixed(1)}h` : '—'}
        sub="Open → close"
        icon={Clock}
        color="amber"
        onClick={() => openDrilldown('service-request-productivity', 'Cycle Time Drilldown')}
      />
      <MetricPill
        label="Automation Score"
        value={loading ? null : k.automation_score != null ? `${k.automation_score.toFixed(0)}` : '—'}
        sub="Opportunity index"
        icon={Zap}
        color="indigo"
        onClick={() => openDrilldown('automation-opportunities', 'Automation Opportunities Drilldown')}
      />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Critical / High Incidents panel
// ---------------------------------------------------------------------------
// Function: CriticalIncidentsPanel
function CriticalIncidentsPanel({ criticalAlerts, openCriticalCount }) {
  return (
    <div className="lg:col-span-1 card-modern p-5 rounded-2xl">
      <div className="flex items-center gap-2 mb-3">
        <AlertTriangle className={`w-4 h-4 ${openCriticalCount > 0 ? 'text-accent-rose animate-pulse' : 'text-slate-500'}`} />
        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">Critical / High Incidents</span>
        {openCriticalCount > 0 && (
          <span className="ml-auto text-xs font-bold bg-red-100 text-red-700 px-2.5 py-1 rounded-full border border-red-200">{openCriticalCount} Open</span>
        )}
      </div>
      {openCriticalCount === 0 ? (
        <div className="flex items-center gap-2 text-accent-emerald text-xs py-2">
          <CheckCircle className="w-4 h-4" /> No critical or high incidents open
        </div>
      ) : (
        <ul className="space-y-2 max-h-80 overflow-y-auto pr-2">
          {criticalAlerts.slice(0, 8).map((a) => (
            <li key={a.number} className="flex items-start gap-2 text-xs bg-red-50 p-2.5 rounded-xl border border-red-200 hover:border-red-300 transition-colors">
              <span className="mt-1 w-2 h-2 rounded-full bg-accent-rose flex-shrink-0 animate-pulse" />
              <div className="min-w-0">
                <span className="font-semibold text-red-700">{a.number}</span>
                <span className="text-slate-600 ml-1">— {a.short_description}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// Function: insightSeverity
function insightSeverity(ins, text) {
  if (typeof ins === 'object') return ins.severity || ins.level
  const lower = text?.toLowerCase() || ''
  if (lower.includes('critical') || lower.includes('breach')) return 'critical'
  if (lower.includes('warn') || lower.includes('risk')) return 'warning'
  return 'info'
}

// ---------------------------------------------------------------------------
// Leadership Insights panel
// ---------------------------------------------------------------------------
// Function: LeadershipInsightsPanel
function LeadershipInsightsPanel({ insightsLoading, insightsEnriching, execInsights }) {
  return (
    <div className="lg:col-span-2 card-modern p-5 rounded-2xl">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 rounded-lg bg-primary-500/20">
          <BarChart2 className="w-4 h-4 text-accent-cyan" />
        </div>
        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">Leadership Insights</span>
        {insightsEnriching && (
          <span className="ml-auto flex items-center gap-1.5 text-[10px] text-slate-600">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse" />
            AI enhancing...
          </span>
        )}
      </div>
      {insightsLoading ? (
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => <div key={i} className="h-4 w-full rounded skeleton" />)}
        </div>
      ) : execInsights.length > 0 ? (
        <ul className="divide-y divide-slate-200 space-y-2">
          {execInsights.slice(0, 6).map((ins, i) => {
            const text = typeof ins === 'string' ? ins : ins.text || ins.insight || JSON.stringify(ins)
            return <InsightLine key={i} text={text} severity={insightSeverity(ins, text)} />
          })}
        </ul>
      ) : (
        <p className="text-xs text-slate-500 italic">No insights available — sync data to generate AI-powered insights.</p>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Repeat Incidents panel
// ---------------------------------------------------------------------------
// Function: RepeatIncidentsPanel
function RepeatIncidentsPanel({ loading, repeatIncidents, openDrilldown }) {
  return (
    <button
      type="button"
      onClick={() => openDrilldown('repeat-incidents', 'Repeat Incidents L2 / L3')}
      className="card-modern p-5 text-left hover:-translate-y-1 transition-all duration-300 rounded-2xl"
    >
      <div className="flex items-center gap-2 mb-3">
        <Repeat className="w-4 h-4 text-accent-amber" />
        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">Repeat Incidents</span>
        {!loading && repeatIncidents && (
          <span className="ml-auto text-xs font-bold bg-amber-100 text-amber-700 px-2.5 py-1 rounded-full border border-amber-200">
            {repeatIncidents.repeat_pct || 0}%
          </span>
        )}
      </div>
      {loading ? (
        <div className="space-y-2">{[...Array(3)].map((_, i) => <div key={i} className="h-12 rounded skeleton" />)}</div>
      ) : repeatIncidents && repeatIncidents.top_repeats && repeatIncidents.top_repeats.length > 0 ? (
        <ul className="space-y-2 max-h-56 overflow-y-auto pr-2">
          {repeatIncidents.top_repeats.slice(0, 5).map((repeat, i) => (
            <li key={i} className="flex items-start gap-2 text-xs p-2.5 bg-amber-50 rounded-xl border border-amber-200 hover:border-amber-300 transition-colors">
              <Repeat className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <div className="min-w-0">
                <p className="font-semibold text-amber-700">{repeat.occurrences}x</p>
                <p className="text-slate-600 text-[10px] truncate">{repeat.description}</p>
                {repeat.avg_mttr_hours > 0 && (
                  <p className="text-slate-500 text-[10px] mt-1">Avg MTTR: {repeat.avg_mttr_hours.toFixed(1)}h</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-slate-500 italic">No repeat incidents detected.</p>
      )}
    </button>
  )
}

// ---------------------------------------------------------------------------
// RCA & Ownership panel
// ---------------------------------------------------------------------------
// Function: RCAOwnershipPanel
function RCAOwnershipPanel({ loading, rcaOwnership, openDrilldown }) {
  return (
    <button
      type="button"
      onClick={() => openDrilldown('rca-ownership', 'RCA & Ownership L2 / L3')}
      className="card-modern p-5 text-left hover:-translate-y-1 transition-all duration-300 rounded-2xl"
    >
      <div className="flex items-center gap-2 mb-3">
        <UserCheck className="w-4 h-4 text-accent-emerald" />
        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">RCA & Ownership</span>
        {!loading && rcaOwnership && (
          <span className="ml-auto text-xs font-bold bg-emerald-100 text-emerald-700 px-2.5 py-1 rounded-full border border-emerald-200">
            {rcaOwnership.rca_identified_pct || 0}%
          </span>
        )}
      </div>
      {loading ? (
        <div className="space-y-2">{[...Array(3)].map((_, i) => <div key={i} className="h-12 rounded skeleton" />)}</div>
      ) : rcaOwnership ? (
        <div className="space-y-3">
          {rcaOwnership.top_root_causes && rcaOwnership.top_root_causes.length > 0 ? (
            <div>
              <p className="text-[10px] text-slate-600 mb-2 font-semibold">Top Root Causes</p>
              <ul className="space-y-1">
                {rcaOwnership.top_root_causes.slice(0, 3).map((cause, i) => (
                  <li key={i} className="flex items-center justify-between text-xs text-slate-700 p-1.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="truncate">{cause.cause}</span>
                    <span className="font-semibold text-emerald-400 flex-shrink-0">{cause.count}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {rcaOwnership.ownership_distribution && rcaOwnership.ownership_distribution.length > 0 ? (
            <div className="pt-2 border-t border-slate-200">
              <p className="text-[10px] text-slate-600 mb-2 font-semibold">Top Ownership</p>
              <ul className="space-y-1">
                {rcaOwnership.ownership_distribution.slice(0, 3).map((owner, i) => (
                  <li key={i} className="flex items-center justify-between text-xs text-slate-700 p-1.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="truncate">{owner.assigned_to}</span>
                    <span className="font-semibold text-sky-400 flex-shrink-0">{owner.count}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : (
        <p className="text-xs text-slate-500 italic">No RCA data available.</p>
      )}
    </button>
  )
}

// ---------------------------------------------------------------------------
// FRM End State Targets panel
// ---------------------------------------------------------------------------
// Function: FRMEndStatePanel
function FRMEndStatePanel({ openDrilldown }) {
  return (
    <div className="mb-8 animate-slide-up">
      <div className="relative rounded-2xl overflow-hidden"
           style={{
             background: 'linear-gradient(180deg, #ffffff 0%, #f6faff 100%)',
             border: '1px solid #d8e4f3',
             boxShadow: '0 16px 30px rgba(15,23,42,0.08)',
           }}>

        {/* Subtle grid pattern */}
        <div className="absolute inset-0 opacity-[0.06]"
             style={{
               backgroundImage: 'linear-gradient(rgba(14,116,206,0.14) 1px, transparent 1px), linear-gradient(90deg, rgba(14,116,206,0.14) 1px, transparent 1px)',
               backgroundSize: '48px 48px',
             }} />

        <div className="relative p-5">
          {/* Panel header */}
          <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl shadow-glow-md flex-shrink-0"
                   style={{ background: 'linear-gradient(135deg, #6366f1, #a855f7)' }}>
                <Target className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-extrabold text-slate-800 uppercase tracking-widest flex items-center gap-2">
                  End State Targets
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                        style={{ background: 'rgba(99,102,241,0.2)', border: '1px solid rgba(99,102,241,0.4)', color: '#a5b4fc' }}>
                    FRM
                  </span>
                </h2>
                <p className="text-xs text-slate-600 mt-0.5">
                  5 transformation KPI commitments · Baseline → Year 1 → Year 3 · Novastra · June 2026
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => openDrilldown('frm-end-state', 'FRM End State — L2 / L3 Detail')}
              className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl transition-all duration-300 hover:-translate-y-0.5"
              style={{
                background: 'rgba(99,102,241,0.15)',
                border: '1px solid rgba(99,102,241,0.35)',
                color: '#a5b4fc',
                boxShadow: '0 0 20px rgba(99,102,241,0.1)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(99,102,241,0.25)'
                e.currentTarget.style.boxShadow = '0 0 30px rgba(99,102,241,0.25)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(99,102,241,0.15)'
                e.currentTarget.style.boxShadow = '0 0 20px rgba(99,102,241,0.1)'
              }}
            >
              <BarChart2 className="w-3.5 h-3.5" />
              Expand All KPIs
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* 5 roadmap cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {FRM_METRICS.map((metric) => (
              <FRMRoadmapCard
                key={metric.id}
                metric={metric}
                onClick={() => openDrilldown('frm-end-state', `FRM — ${metric.fullName}`)}
              />
            ))}
          </div>

          {/* Footer note */}
          <div className="mt-4 flex items-center gap-2 text-[10px] text-slate-600">
            <div className="w-3 h-px bg-slate-300" />
            <span>Click any card for full measurement, owner, effort &amp; risk context</span>
            <div className="w-3 h-px bg-slate-300" />
          </div>
        </div>
      </div>
    </div>
  )
}

// Function: twoTierColors
function twoTierColors(isAlarmed) {
  return isAlarmed
    ? { color: '#f43f5e', glow: 'rgba(244,63,94,0.15)', border: 'rgba(244,63,94,0.2)' }
    : { color: '#10b981', glow: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.2)' }
}

// Function: healthScoreColors
function healthScoreColors(score) {
  if (score >= 80) return { color: '#10b981', glow: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.2)' }
  if (score >= 60) return { color: '#f59e0b', glow: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.2)' }
  return { color: '#f43f5e', glow: 'rgba(244,63,94,0.15)', border: 'rgba(244,63,94,0.2)' }
}

// Function: buildSummaryStripItems
function buildSummaryStripItems({ loading, k, openCriticalCount, healthScore, openDrilldown }) {
  return [
    {
      label: 'Changes',
      value: loading ? '—' : k.total_changes?.toLocaleString() ?? '—',
      color: '#6366f1',
      glow: 'rgba(99,102,241,0.15)',
      border: 'rgba(99,102,241,0.2)',
      action: () => openDrilldown('change-risk', 'Changes L2 / L3'),
    },
    {
      label: 'SLA Breach Risk',
      value: loading ? '—' : k.sla_compliance_pct != null ? `${(100 - k.sla_compliance_pct).toFixed(1)}%` : '—',
      ...twoTierColors(k.sla_compliance_pct < 90),
      action: () => openDrilldown('service-request-productivity', 'SLA Breach Risk L2 / L3'),
    },
    {
      label: 'P1 / P2 Open',
      value: loading ? '—' : openCriticalCount,
      ...twoTierColors(openCriticalCount > 0),
      pulse: openCriticalCount > 0,
      action: () => openDrilldown('incident-mttr', 'P1 / P2 Open L2 / L3'),
    },
    {
      label: 'Health Score',
      value: loading ? '—' : `${healthScore}%`,
      ...healthScoreColors(healthScore),
      action: () => openDrilldown('executive-overview', 'Health Score L2 / L3'),
    },
  ]
}

// ---------------------------------------------------------------------------
// Summary strip
// ---------------------------------------------------------------------------
// Function: SummaryStrip
function SummaryStrip(props) {
  const items = buildSummaryStripItems(props)
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center mb-6 animate-slide-up">
      {items.map(({ label, value, color, glow, border, pulse, action }) => (
        <button
          key={label}
          type="button"
          onClick={action}
          className="rounded-2xl py-6 px-4 transition-all duration-300 hover:-translate-y-1"
          style={{
            background: `radial-gradient(ellipse at 50% 0%, ${glow} 0%, #ffffff 78%)`,
            border: `1px solid ${border}`,
            boxShadow: `0 8px 22px rgba(15,23,42,0.08)`,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.boxShadow = `0 12px 28px rgba(15,23,42,0.12), 0 0 16px ${glow}`
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.boxShadow = '0 8px 22px rgba(15,23,42,0.08)'
          }}
        >
          <div className="text-[11px] uppercase tracking-widest text-slate-500 mb-3 font-semibold">{label}</div>
          <div className={`text-4xl font-extrabold tabular-nums ${pulse ? 'animate-pulse' : ''}`} style={{ color }}>{value}</div>
        </button>
      ))}
    </div>
  )
}

// Function: getDrilldownData
function getDrilldownData(chartType, ctx) {
  const map = {
    'incident-mttr': ctx.incidentData,
    'change-risk': ctx.changesData,
    'service-request-productivity': ctx.serviceRequestData,
    'automation-opportunities': { candidates: ctx.automationCandidates },
    'executive-overview': ctx.executiveDrillData,
    'repeat-incidents': ctx.repeatIncidents,
    'rca-ownership': ctx.rcaOwnership,
    'frm-end-state': FRM_METRICS,
  }
  return map[chartType] ?? {}
}

// ---------------------------------------------------------------------------
// Main ExecutiveCockpit
// ---------------------------------------------------------------------------
// Function: ExecutiveCockpit
export default function ExecutiveCockpit() {
  const { criticalAlerts, dateRange } = useDashboard()
  const printRef = useRef(null)
  const [kpis, setKpis] = useState(null)
  const [insights, setInsights] = useState(null)
  const [incidentData, setIncidentData] = useState(null)
  const [monthlyVolume, setMonthlyVolume] = useState([])
  const [applicationHotspots, setApplicationHotspots] = useState([])
  const [automationCandidates, setAutomationCandidates] = useState([])
  const [changesData, setChangesData] = useState(null)
  const [serviceRequestData, setServiceRequestData] = useState(null)
  const [repeatIncidents, setRepeatIncidents] = useState(null)
  const [rcaOwnership, setRcaOwnership] = useState(null)
  const [loading, setLoading] = useState(true)
  const [insightsLoading, setInsightsLoading] = useState(true)
  const [insightsEnriching, setInsightsEnriching] = useState(false)
  const [drawer, setDrawer] = useState({ open: false, chartType: null, title: '' })

  const fetchAll = useCallback(async () => {
    try {
      const [kpiRes, incRes, repeatRes, rcaRes, volumeRes, hotspotsRes, autoRes, changesRes, srRes, insQuickRes] = await Promise.allSettled([
        getKPIs(dateRange),
        getIncidents(dateRange),
        getRepeatIncidents(dateRange),
        getRCAOwnership(dateRange),
        getMonthlyVolume(12, dateRange),
        getApplicationHotspots(10, dateRange),
        getAutomationCandidates(20, { deepAnalysis: false }, dateRange),
        getChanges(dateRange),
        getServiceRequests(dateRange),
        getInsights({ quick: true }, dateRange),
      ])
      if (kpiRes.status === 'fulfilled') setKpis(kpiRes.value.data)
      if (incRes.status === 'fulfilled') setIncidentData(incRes.value.data)
      if (repeatRes.status === 'fulfilled') setRepeatIncidents(repeatRes.value.data)
      if (rcaRes.status === 'fulfilled') setRcaOwnership(rcaRes.value.data)
      if (volumeRes.status === 'fulfilled') setMonthlyVolume(volumeRes.value.data || [])
      if (hotspotsRes.status === 'fulfilled') setApplicationHotspots(hotspotsRes.value.data || [])
      if (autoRes.status === 'fulfilled') setAutomationCandidates(autoRes.value.data || [])
      if (changesRes.status === 'fulfilled') setChangesData(changesRes.value.data)
      if (srRes.status === 'fulfilled') setServiceRequestData(srRes.value.data)
      if (insQuickRes.status === 'fulfilled') setInsights(insQuickRes.value.data)
    } catch (e) {
      console.error('Failed to load executive data', e)
    } finally {
      setLoading(false)
      setInsightsLoading(false)
    }

    setInsightsEnriching(true)
    try {
      const insRes = await getInsights({}, dateRange)
      setInsights(insRes.data)
    } catch (e) {
      console.error('Failed to load LLM insights', e)
    } finally {
      setInsightsEnriching(false)
    }
  }, [dateRange])

  useEffect(() => { fetchAll() }, [fetchAll])

  const k = kpis || {}
  const openCriticalCount = criticalAlerts.length

  // Function: healthScore
  const healthScore = (() => {
    let score = k.sla_compliance_pct ?? 100
    if (openCriticalCount > 0) score = Math.max(0, score - openCriticalCount * 5)
    if (k.emergency_change_pct != null && k.emergency_change_pct > 10) score -= 10
    return Math.round(Math.min(100, Math.max(0, score)))
  })()

  const execInsights = insights?.executive || []
  const executiveDrillData = { kpis: k, volume: monthlyVolume, hotspots: applicationHotspots }

  // Function: openDrilldown
  function openDrilldown(chartType, title) {
    setDrawer({ open: true, chartType, title })
  }

  return (
    <div ref={printRef} className="px-4 lg:px-6 py-8 max-w-screen-2xl mx-auto pb-20 min-h-screen">

      {/* ── Header ── */}
      <div className="mb-8 animate-fade-in flex items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold gradient-text flex items-center gap-3">
            <div className="p-2.5 rounded-xl gradient-bg-primary shadow-glow-md">
              <Activity className="w-7 h-7 text-white" />
            </div>
            Executive Operations — 360° Overview
          </h1>
          <p className="text-sm text-slate-400 mt-3 flex items-center gap-2">
            <span className="inline-flex w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
            Live ITSM health pulse across incidents, changes, service requests &amp; SLAs
          </p>
        </div>
        <ExportPDFButton printRef={printRef} title="Executive Cockpit" />
      </div>

      <HeroKPIRow loading={loading} healthScore={healthScore} k={k} openCriticalCount={openCriticalCount} openDrilldown={openDrilldown} />

      <SecondaryKPIRow loading={loading} k={k} openDrilldown={openDrilldown} />

      {/* ── Row 3 — Critical incidents list + AI insights ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6 animate-slide-up">
        <CriticalIncidentsPanel criticalAlerts={criticalAlerts} openCriticalCount={openCriticalCount} />
        <LeadershipInsightsPanel insightsLoading={insightsLoading} insightsEnriching={insightsEnriching} execInsights={execInsights} />
      </div>

      {/* ── Row 3.5 — Repeat Incidents & RCA/Ownership ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8 animate-slide-up">
        <RepeatIncidentsPanel loading={loading} repeatIncidents={repeatIncidents} openDrilldown={openDrilldown} />
        <RCAOwnershipPanel loading={loading} rcaOwnership={rcaOwnership} openDrilldown={openDrilldown} />
      </div>

      <FRMEndStatePanel openDrilldown={openDrilldown} />

      <SummaryStrip loading={loading} k={k} openCriticalCount={openCriticalCount} healthScore={healthScore} openDrilldown={openDrilldown} />

      {/* Drilldown drawer */}
      <DrilldownDrawer
        open={drawer.open}
        onClose={() => setDrawer((d) => ({ ...d, open: false }))}
        title={drawer.title}
        chartType={drawer.chartType}
        data={getDrilldownData(drawer.chartType, {
          incidentData, changesData, serviceRequestData, automationCandidates,
          executiveDrillData, repeatIncidents, rcaOwnership,
        })}
      />

      <AlertTicker alerts={criticalAlerts} />
    </div>
  )
}
