// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src (utils.js)
// Date: 2026-04-23
// ---------------------------------------------------------------------------
// Function: riskColor
export function riskColor(label = '') {
  const l = label.toUpperCase()
  if (['EXCELLENT', 'GOOD', 'LOW', 'LOW RISK'].some((x) => l.includes(x.replace(' RISK', ''))))
    return { text: 'text-success', bg: 'bg-green-500/10', border: 'border-green-500/30', hex: '#4ade80' }
  if (['FAIR', 'MEDIUM', 'MEDIUM RISK'].some((x) => l.includes(x.replace(' RISK', ''))))
    return { text: 'text-warning', bg: 'bg-orange-500/10', border: 'border-orange-500/30', hex: '#fb923c' }
  return { text: 'text-danger', bg: 'bg-red-500/10', border: 'border-red-500/30', hex: '#f87171' }
}

// Function: scoreColor
export function scoreColor(score) {
  if (score >= 75) return '#4ade80'
  if (score >= 50) return '#fb923c'
  return '#f87171'
}

// Function: fmtNumber
export function fmtNumber(n) {
  if (n == null) return '—'
  return Number(n).toLocaleString()
}

// Function: fmtUSD
export function fmtUSD(n) {
  if (n == null) return '—'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
}

// Function: clamp
export function clamp(v, min = 0, max = 100) {
  return Math.min(max, Math.max(min, v))
}

/** Animated counter hook helper – called externally */
// Function: lerp
export function lerp(a, b, t) {
  return a + (b - a) * t
}

const TAB_ANALYSIS_MAP = {
  overview: ['tech_debt', 'cloud_blockers', 'transformation', 'microservices'],
  security: ['cloud_blockers', 'tech_debt', 'transformation'],
  cloud: ['cloud_blockers', 'transformation'],
  cloud_services: ['cloud_blockers', 'transformation'],
  co2: ['transformation', 'tech_debt'],
  green: ['transformation', 'tech_debt'],
  health_tech: ['tech_debt', 'transformation'],
  debt_detail: ['tech_debt', 'transformation'],
  architecture: ['microservices', 'transformation'],
  languages: ['tech_debt', 'business_rules'],
  practices: ['tech_debt', 'business_rules'],
  knowledge_graph: ['microservices', 'business_rules', 'transformation'],
}

// Function: toList
function toList(value) {
  return Array.isArray(value) ? value : []
}

// Function: uniqStrings
function uniqStrings(items, limit = 4) {
  const seen = new Set()
  const out = []
  for (const item of items) {
    const text = String(item || '').trim()
    if (!text || seen.has(text)) continue
    seen.add(text)
    out.push(text)
    if (out.length >= limit) break
  }
  return out
}

// Function: priorityScore
function priorityScore(priority) {
  if (priority === 'high') return 3
  if (priority === 'medium') return 2
  return 1
}

// Function: techDebtSummary
function techDebtSummary(data) {
  const hotspots = toList(data.hotspots)
  const drivers = hotspots
    .map((h) => h?.issue || h?.file)
    .filter(Boolean)
  const actions = [
    ...toList(data.quick_wins),
    ...toList(data.strategic_actions),
    ...hotspots.map((h) => h?.recommendation).filter(Boolean),
  ]
  const hotspotPriority = hotspots
    .map((h) => String(h?.priority || '').toLowerCase())
    .filter(Boolean)
    .sort((a, b) => priorityScore(b) - priorityScore(a))[0] || 'medium'
  return {
    summary: data.summary || 'Tech debt risk assessment is available for this tab.',
    priority: hotspotPriority,
    confidence: 78,
    drivers,
    recommended_actions: actions,
  }
}

// Function: cloudBlockersSummary
function cloudBlockersSummary(data) {
  const blockers = toList(data.blockers)
  const drivers = blockers
    .map((b) => b?.title || b?.description)
    .filter(Boolean)
  const actions = blockers
    .map((b) => b?.remediation)
    .filter(Boolean)
  const readiness = String(data.migration_readiness || '').toLowerCase()
  const hasCritical = blockers.some((b) => ['critical', 'high'].includes(String(b?.severity || '').toLowerCase()))
  const priority = (readiness === 'not_ready' || readiness === 'major_refactor' || hasCritical)
    ? 'high'
    : (readiness === 'ready' ? 'low' : 'medium')
  return {
    summary: data.summary || 'Cloud migration assessment is available for this tab.',
    priority,
    confidence: 80,
    drivers,
    recommended_actions: actions,
  }
}

// Function: microservicesSummary
function microservicesSummary(data) {
  const services = toList(data.microservices)
  const risks = toList(data.risks)
  const drivers = services
    .map((s) => s?.responsibility || s?.name)
    .filter(Boolean)
  const actions = services
    .sort((a, b) => Number(a?.migration_order || 999) - Number(b?.migration_order || 999))
    .map((s) => s?.name)
    .filter(Boolean)
  const priority = risks.length >= 3 ? 'high' : (risks.length === 0 ? 'low' : 'medium')
  return {
    summary: data.summary || 'Microservice decomposition assessment is available for this tab.',
    priority,
    confidence: 74,
    drivers,
    recommended_actions: [...actions, ...risks],
  }
}

// Function: businessRulesSummary
function businessRulesSummary(data) {
  const rules = toList(data.business_rules)
  const workflows = toList(data.workflows)
  const drivers = rules
    .map((r) => r?.title || r?.description)
    .filter(Boolean)
  const actions = workflows
    .flatMap((w) => toList(w?.steps || []).slice(0, 2))
    .filter(Boolean)
  return {
    summary: data.summary || 'Business-rule intelligence is available for this tab.',
    priority: 'medium',
    confidence: 72,
    drivers,
    recommended_actions: actions,
  }
}

// Function: transformationSummary
function transformationSummary(data) {
  const paths = toList(data.transformation_paths)
  const drivers = paths
    .map((p) => `${p?.current || '?'} -> ${p?.recommended || '?'}`)
    .filter(Boolean)
  const actions = paths
    .flatMap((p) => toList(p?.steps || []).slice(0, 2))
    .filter(Boolean)
  const maturity = String(data.current_maturity || '').toLowerCase()
  const priority = maturity === 'legacy' ? 'high' : (maturity === 'cloud-native' ? 'low' : 'medium')
  return {
    summary: data.summary || data.target_state || 'Transformation guidance is available for this tab.',
    priority,
    confidence: 77,
    drivers,
    recommended_actions: actions,
  }
}

const _ANALYSIS_SUMMARY_BUILDERS = {
  tech_debt: techDebtSummary,
  cloud_blockers: cloudBlockersSummary,
  microservices: microservicesSummary,
  business_rules: businessRulesSummary,
  transformation: transformationSummary,
}

// Function: analysisSummary
function analysisSummary(analysisKey, data) {
  if (!data || data.error) return null
  const builder = _ANALYSIS_SUMMARY_BUILDERS[analysisKey]
  return builder ? builder(data) : null
}

// Function: normaliseAssessment
function normaliseAssessment(tabKey, assessment, fallback = null) {
  if (!assessment && !fallback) return null

  const base = assessment || fallback || {}
  const priority = ['high', 'medium', 'low'].includes(String(base.priority || '').toLowerCase())
    ? String(base.priority).toLowerCase()
    : (fallback?.priority || 'medium')

  const confidence = clamp(Number(base.confidence ?? fallback?.confidence ?? 70), 20, 100)
  const drivers = uniqStrings(toList(base.drivers), 4)
  const actions = uniqStrings(toList(base.recommended_actions || base.actions), 4)
  const sources = uniqStrings(toList(base.sources), 5)

  return {
    tabKey,
    summary: String(base.summary || fallback?.summary || 'LLM assessment available.').trim(),
    priority,
    confidence,
    drivers: drivers.length ? drivers : uniqStrings(toList(fallback?.drivers), 4),
    recommended_actions: actions.length ? actions : uniqStrings(toList(fallback?.recommended_actions), 4),
    sources,
  }
}

// Function: getLLMTabAssessment
export function getLLMTabAssessment(aiReport, tabKey) {
  if (!aiReport || !tabKey) return null

  const analyses = aiReport.analyses || {}
  const mapped = toList(TAB_ANALYSIS_MAP[tabKey])
  const parts = mapped
    .map((analysisKey) => analysisSummary(analysisKey, analyses[analysisKey]))
    .filter(Boolean)

  const fallback = parts.length
    ? {
        summary: parts.map((p) => p.summary).filter(Boolean).slice(0, 2).join(' '),
        priority: parts
          .map((p) => p.priority)
          .sort((a, b) => priorityScore(b) - priorityScore(a))[0] || 'medium',
        confidence: Math.round(parts.reduce((sum, p) => sum + Number(p.confidence || 70), 0) / parts.length),
        drivers: uniqStrings(parts.flatMap((p) => p.drivers || []), 4),
        recommended_actions: uniqStrings(parts.flatMap((p) => p.recommended_actions || []), 4),
        sources: mapped,
      }
    : null

  const explicit = aiReport.tab_assessments?.[tabKey] || null
  return normaliseAssessment(tabKey, explicit, fallback)
}
