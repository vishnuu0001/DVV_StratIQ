// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src_ssdlc_archive (App.jsx)
// Date: 2025-08-17
// ---------------------------------------------------------------------------
import React, { useEffect, useMemo, useRef, useState } from 'react'
import {
  BarChart2,
  BrainCircuit,
  FileText,
  Filter,
  Home,
  LayoutPanelTop,
  LogOut,
  Paperclip,
  RefreshCcw,
  Search,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  X,
  Zap,
} from 'lucide-react'

const CSM_URL = import.meta.env.VITE_CSM_URL || 'http://localhost:5173'

const API_BASE = import.meta.env.VITE_API_BASE || '/api/ssdlc'
const PORTAL_TOKEN_KEY = 'ssdlc_portal_auth_token'
const PORTAL_LOGIN_URL = import.meta.env.VITE_PORTAL_LOGIN_URL || '/login'
const PORTAL_HOME_URL = import.meta.env.VITE_PORTAL_HOME_URL || '/launch-modules'

// Function: getPortalToken
function getPortalToken() {
  return sessionStorage.getItem(PORTAL_TOKEN_KEY) || localStorage.getItem(PORTAL_TOKEN_KEY)
}

// Function: setPortalToken
function setPortalToken(token) {
  if (!token) return
  sessionStorage.setItem(PORTAL_TOKEN_KEY, token)
  localStorage.setItem(PORTAL_TOKEN_KEY, token)
}

// Function: clearPortalToken
function clearPortalToken() {
  sessionStorage.removeItem(PORTAL_TOKEN_KEY)
  localStorage.removeItem(PORTAL_TOKEN_KEY)
}

// Function: consumePortalTokenFromHash
function consumePortalTokenFromHash() {
  const hash = window.location.hash || ''
  const params = hash.startsWith('#') ? new URLSearchParams(hash.slice(1)) : null
  const token = params?.get('authToken') || params?.get('token')
  if (!token) return null
  setPortalToken(token)
  window.history.replaceState(null, document.title, window.location.pathname + window.location.search)
  return token
}

// Function: authFetch
async function authFetch(url, options = {}) {
  const token = getPortalToken()
  const headers = { ...(options.headers || {}) }
  if (token) headers.Authorization = `Bearer ${token}`
  return fetch(url, { ...options, headers })
}

// Function: uniqueValues
function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))]
}


// Function: scoreColor
function scoreColor(pct) {
  if (pct == null) return '#cbd5e1'
  if (pct >= 85) return '#16a34a'
  if (pct >= 65) return '#65a30d'
  if (pct >= 40) return '#d97706'
  return '#dc2626'
}

const TOWER_COLORS = ['#1e6b8a', '#e07b39', '#16a34a', '#3b82f6', '#9333ea', '#ec4899']

// Function: flattenRows
function flattenRows(towers, towerOrder) {
  return towerOrder.flatMap((towerKey) => {
    const tower = towers[towerKey]
    if (!tower) return []
    return tower.responses.map((row) => ({
      towerKey,
      towerName: tower.name,
      id: row.id,
      rowNumber: row.rowNumber,
      dimension: row.dimension,
      phase: row.phase,
      question: row.question,
      weight: row.weight,
      maturityOptions: row.maturityOptions,
      evidenceFiles: row.evidenceFiles || [],
    }))
  })
}

// Function: createDraftRows
function createDraftRows(count) {
  return Array.from({ length: count }, (_, index) => ({
    uiId: `draft-${index + 1}`,
    application: '',
    dimension: '',
    phase: '',
    question: '',
    currentState: '',
    predictedWeight: null,
    evidence: '',
    gapRecommendation: '',
    recommendationSource: '',
    recommendationModel: '',
    predictionAttempted: false,
  }))
}

// Function: resolveCatalogEntry
function resolveCatalogEntry(catalogRows, draftRow) {
  if (!draftRow.application || !draftRow.dimension || !draftRow.phase || !draftRow.question) {
    return null
  }
  return (
    catalogRows.find(
      (row) =>
        row.towerKey === draftRow.application &&
        row.dimension === draftRow.dimension &&
        row.phase === draftRow.phase &&
        row.question === draftRow.question,
    ) ||
    catalogRows.find(
      (row) =>
        row.towerKey === draftRow.application &&
        row.question === draftRow.question,
    ) ||
    catalogRows.find((row) => row.question === draftRow.question) ||
    null
  )
}

// Function: buildRowOptions
function buildRowOptions(collections) {
  return {
    applications: collections.applications || [],
    dimensions: collections.dimensions || [],
    phases: collections.phases || [],
    questions: collections.questions || [],
    currentStates: collections.currentStates || [],
  }
}

// Function: enrichDraftRow
function enrichDraftRow(draftRow, catalogRows, towers, currentStateMap, uiCollections) {
  const entry = resolveCatalogEntry(catalogRows, draftRow)
  const mappedState = currentStateMap[draftRow.currentState] || null
  const estimatedScore = mappedState?.score || 0
  const weight = draftRow.predictedWeight || entry?.weight || 0
  const weightedScore = estimatedScore && weight ? estimatedScore * weight : 0
  return {
    ...draftRow,
    towerName: draftRow.application ? towers[draftRow.application]?.name || '' : '',
    entry,
    currentStateOptions: uiCollections.currentStates || [],
    selectedValue: mappedState?.key || '',
    estimatedScore,
    weight,
    weightedScore,
    evidenceFiles: entry?.evidenceFiles || [],
  }
}

// Function: filterRows
function filterRows(rows, filters) {
  const query = filters.search.trim().toLowerCase()
  return rows.filter((row) => {
    if (filters.application && row.application !== filters.application) return false
    if (filters.dimension && row.dimension !== filters.dimension) return false
    if (filters.phase && row.phase !== filters.phase) return false
    if (filters.question && row.question !== filters.question) return false
    if (filters.currentState && row.currentState !== filters.currentState) return false
    if (!query) return true
    return [
      row.towerName,
      row.dimension,
      row.phase,
      row.question,
      row.currentState,
      row.evidence,
      row.gapRecommendation,
    ]
      .join(' ')
      .toLowerCase()
      .includes(query)
  })
}

// Function: scoreToLevel
function scoreToLevel(score) {
  if (score == null) return 'Not started'
  if (score < 40) return 'Early'
  if (score < 65) return 'Emerging'
  if (score < 85) return 'Mature'
  return 'Fully Mature'
}

// Function: getVisibleSummary
function getVisibleSummary(rows) {
  const answered = rows.filter((row) => row.estimatedScore > 0)
  const totalWeight = answered.reduce((sum, row) => sum + row.weight, 0)
  const totalWeightedScore = answered.reduce((sum, row) => sum + row.weightedScore, 0)
  const scorePct = totalWeight ? Number(((totalWeightedScore / (totalWeight * 4)) * 100).toFixed(2)) : null
  return {
    answeredCount: answered.length,
    totalCount: rows.length,
    scorePct,
    level: scoreToLevel(scorePct),
  }
}

// Function: readEventStream
// Consumes a `data: {...}\n\n` SSE-style stream, invoking onPayload for each parsed event.
// Returning `false` from onPayload stops processing further events in the current chunk.
// Function: readEventStream
async function readEventStream(response, onPayload) {
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() || ''
    for (const part of parts) {
      if (!part.startsWith('data: ')) continue
      const payload = JSON.parse(part.slice(6).trim())
      if (onPayload(payload) === false) break
    }
  }
}

// Function: buildBatchPredictionPayload
function buildBatchPredictionPayload(rows) {
  return rows.map((r) => ({
    uiId: r.uiId,
    application: r.application,
    applicationName: r.towerName,
    dimension: r.dimension,
    phase: r.phase,
    question: r.question,
    selectedLevelKey: r.selectedValue,
    currentState: r.currentState,
    evidence: r.evidence || '',
  }))
}

// Function: buildBatchCompletionStatus
function buildBatchCompletionStatus(successCount, failCount, total, modelName) {
  if (failCount > 0) {
    return `${successCount}/${total} predictions generated — ${failCount} returned empty. Check: ollama pull ${modelName || 'llama3.1'}`
  }
  return `All ${successCount} predictions complete`
}

// Function: buildLoadedRowBase
function buildLoadedRowBase(appKey, dim, catalogRow, savedById, reverseStateMap) {
  const saved = savedById[catalogRow.id] || {}
  const savedCurrentState = saved.selectedLevelKey ? (reverseStateMap[saved.selectedLevelKey] || '') : ''
  return {
    application: appKey,
    dimension: dim,
    phase: catalogRow.phase,
    question: catalogRow.question,
    currentState: savedCurrentState,
    predictedWeight: saved.predictedWeight || null,
    evidence: saved.evidence || '',
    gapRecommendation: saved.gapRecommendation || '',
    recommendationSource: saved.recommendationSource || null,
    recommendationModel: saved.recommendationModel || null,
    predictionAttempted: !!(saved.gapRecommendation || saved.recommendationSource),
  }
}

// Function: placeLoadedRow
function placeLoadedRow(updated, blankIdx, appKey, dim, base) {
  if (blankIdx < updated.length) {
    updated[blankIdx] = { ...updated[blankIdx], ...base }
    return blankIdx + 1
  }
  updated.push({ uiId: `row-${appKey}-${dim.replace(/\W/g, '-')}`, ...base })
  return blankIdx
}

// Function: ollamaGateTitle
function ollamaGateTitle(ollama, ollamaModelReady, batchPredicting, batchMessage, readyTitle) {
  if (!ollama?.available) return 'Ollama offline — run: ollama serve  then: ollama pull llama3.1'
  if (!ollamaModelReady) return `Model not loaded — run: ollama pull ${ollama?.default_model || 'llama3.1'}`
  if (batchPredicting) return batchMessage
  return readyTitle
}

// Function: PortalHeader
function PortalHeader({ authUser, onLogout }) {
  return (
    <header className="portal-bar">
      <div className="portal-brand">
        <div className="brand-badge"><ShieldCheck size={18} /></div>
        <div>
          <p className="eyebrow">Launch Modules</p>
          <h2>SSDLC Process Assessment</h2>
        </div>
      </div>
      <div className="portal-actions">
        <span>Signed in as {authUser?.username || 'admin'}</span>
        <button type="button" onClick={() => { window.location.href = PORTAL_HOME_URL }}>
          <Home size={16} /> Homepage
        </button>
        <button type="button" className="csm-link-button" onClick={() => window.open(CSM_URL, '_blank', 'noopener')}>
          <TrendingUp size={16} /> Consolidation Model
        </button>
        <button type="button" className="logout-button" onClick={onLogout}>
          <LogOut size={16} /> Logout
        </button>
      </div>
    </header>
  )
}

// Function: HeroPanel
function HeroPanel({ status, lastSavedAt, ollama, ollamaModelReady }) {
  return (
    <section className="hero-panel">
      <div className="hero-copy">
        <div className="hero-kicker">
          <Sparkles size={16} />
          SSDLC Assessment Workspace
        </div>
        <h1>Modernized SSDLC Process Assessment</h1>
        <p>Assess maturity, capture evidence, and generate recommendations in a streamlined workspace.</p>
      </div>
      <div className="hero-status">
        <div className="status-card">
          <span>Status</span>
          <strong>{status}</strong>
          <p>{lastSavedAt ? `Last saved at ${lastSavedAt}` : 'No saved changes yet'}</p>
        </div>
        <div className={`status-card ${ollamaModelReady ? 'accent-online' : 'accent-warning'}`}>
          <span>Ollama LLM</span>
          <strong>
            {ollamaModelReady ? 'Ready' : ollama?.available ? 'Model not loaded' : 'Offline'}
          </strong>
          <p>
            {ollamaModelReady
              ? ollama.default_model
              : ollama?.available
                ? `Run: ollama pull ${ollama?.default_model || 'llama3.1'}`
                : 'Run: ollama serve  ·  ollama pull llama3.1'}
          </p>
        </div>
      </div>
    </section>
  )
}

// Function: AppChip
function AppChip({ app, enrichedRows }) {
  const rowCount = enrichedRows.filter((r) => r.application === app.value).length
  const answeredCount = enrichedRows.filter((r) => r.application === app.value && r.estimatedScore > 0).length
  const allAnswered = rowCount > 0 && answeredCount === rowCount
  if (!rowCount) return <span className="app-chip">{app.label}</span>
  return (
    <span className={`app-chip ${allAnswered ? 'fully-assessed' : 'has-rows'}`}>
      {app.label}: {answeredCount}/{rowCount}
    </span>
  )
}

// Function: MetricsGrid
function MetricsGrid({ appStats, uiCollections, enrichedRows, visibleSummary, dashboard }) {
  return (
    <section className="metrics-grid">
      <article className="metric-card">
        <span>Applications</span>
        <strong>{appStats.assessed}/{appStats.total}</strong>
        <p>Assessed</p>
        <div className="app-chips">
          {uiCollections.applications.map((app) => (
            <AppChip key={app.value} app={app} enrichedRows={enrichedRows} />
          ))}
        </div>
      </article>
      <article className="metric-card">
        <span>Visible Rows</span>
        <strong>{visibleSummary.totalCount}</strong>
      </article>
      <article className="metric-card">
        <span>Assessed Rows</span>
        <strong>{visibleSummary.answeredCount}/{visibleSummary.totalCount}</strong>
      </article>
      <article className="metric-card">
        <span>Assessment Score</span>
        <strong>{visibleSummary.scorePct == null ? '--' : `${visibleSummary.scorePct}%`}</strong>
        <p>{visibleSummary.level}</p>
      </article>
      <article className="metric-card">
        <span>Portfolio Score</span>
        <strong>{dashboard?.portfolio?.overallScorePct == null ? '--' : `${dashboard.portfolio.overallScorePct}%`}</strong>
        <p>{dashboard?.portfolio?.overallLevel || 'Not started'}</p>
      </article>
    </section>
  )
}

// Function: FiltersPanel
function FiltersPanel({ filters, setFilters, uiCollections, onReset }) {
  return (
    <section className="workspace-card">
      <div className="section-header">
        <div>
          <p className="eyebrow">Collections</p>
          <h2>Filters</h2>
        </div>
        <div className="header-actions">
          <button type="button" className="ghost-button" onClick={onReset}>
            <Filter size={16} /> Reset Filters
          </button>
          <button type="button" className="ghost-button" onClick={() => window.location.reload()}>
            <RefreshCcw size={16} /> Refresh
          </button>
        </div>
      </div>

      <div className="filters-grid">
        <label className="field">
          <span>Applications</span>
          <select value={filters.application} onChange={(event) => setFilters((prev) => ({ ...prev, application: event.target.value }))}>
            <option value="">All applications</option>
            {uiCollections.applications.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Dimension</span>
          <select value={filters.dimension} onChange={(event) => setFilters((prev) => ({ ...prev, dimension: event.target.value }))}>
            <option value="">All dimensions</option>
            {uiCollections.dimensions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>SSDLC Phase(s)</span>
          <select value={filters.phase} onChange={(event) => setFilters((prev) => ({ ...prev, phase: event.target.value }))}>
            <option value="">All phases</option>
            {uiCollections.phases.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Assessment Question</span>
          <select value={filters.question} onChange={(event) => setFilters((prev) => ({ ...prev, question: event.target.value }))}>
            <option value="">All questions</option>
            {uiCollections.questions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Current State</span>
          <select value={filters.currentState} onChange={(event) => setFilters((prev) => ({ ...prev, currentState: event.target.value }))}>
            <option value="">All current states</option>
            {uiCollections.currentStates.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label className="field search-field">
          <span>Search</span>
          <div className="search-box">
            <Search size={16} />
            <input
              value={filters.search}
              onChange={(event) => setFilters((prev) => ({ ...prev, search: event.target.value }))}
              placeholder="Search question, evidence, or recommendation"
            />
          </div>
        </label>
      </div>
    </section>
  )
}

// Function: LoadAppButtons
function LoadAppButtons({ applications, onLoad }) {
  return applications.map((app) => (
    <button
      key={app.value}
      type="button"
      className="ghost-button"
      onClick={() => onLoad(app.value)}
    >
      <LayoutPanelTop size={15} />
      Load {app.label}
    </button>
  ))
}

// Function: BatchPredictButton
function BatchPredictButton({ enrichedRows, ollama, ollamaModelReady, batchPredicting, batchProgress, onClick }) {
  if (!enrichedRows.some((r) => r.selectedValue)) return null
  const assessedCount = enrichedRows.filter((r) => r.selectedValue).length
  const title = ollamaGateTitle(
    ollama, ollamaModelReady, batchPredicting,
    'Prediction in progress…',
    `Generate AI gap analysis for all ${assessedCount} assessed rows`,
  )
  return (
    <button
      type="button"
      className={`batch-predict-btn${!ollamaModelReady ? ' ollama-required' : ''}`}
      disabled={!ollamaModelReady || batchPredicting}
      title={title}
      onClick={onClick}
    >
      <BrainCircuit size={15} />
      {batchPredicting
        ? `Predicting ${batchProgress?.current ?? 0} / ${batchProgress?.total ?? '?'}…`
        : `Generate Predictions (${assessedCount})`}
    </button>
  )
}

// Function: PredictAllButton
function PredictAllButton({ draftRowsCount, enrichedRows, ollama, ollamaModelReady, batchPredicting, batchProgress, onClick }) {
  if (draftRowsCount === 0) return null
  const assessedCount = enrichedRows.filter((r) => r.selectedValue).length
  const title = ollamaGateTitle(
    ollama, ollamaModelReady, batchPredicting,
    'Prediction in progress…',
    assessedCount === 0
      ? 'Enter assessment data first, then run predictions'
      : `Run AI predictions for all ${assessedCount} assessed rows across all towers`,
  )
  return (
    <button
      type="button"
      className="predict-all-btn"
      disabled={batchPredicting || !ollamaModelReady || assessedCount === 0}
      title={title}
      onClick={onClick}
    >
      <Zap size={15} />
      {batchPredicting
        ? `Predicting… ${batchProgress?.current ?? 0} / ${batchProgress?.total ?? '?'}`
        : `Predict All${assessedCount > 0 ? ` (${assessedCount})` : ''}`}
    </button>
  )
}

// Function: ExecDashboardButton
function ExecDashboardButton({ dashboard, onClick }) {
  if (!(dashboard && dashboard.cards?.some((c) => c.overallScorePct != null))) return null
  return (
    <button
      type="button"
      className="exec-dashboard-btn"
      onClick={onClick}
      title="Open Executive SSDLC Maturity Dashboard"
    >
      <BarChart2 size={15} />
      Executive Dashboard
    </button>
  )
}

// Function: OllamaOfflineBanner
function OllamaOfflineBanner({ ollamaModelReady, ollama }) {
  if (ollamaModelReady) return null
  return (
    <div className="ollama-offline-banner">
      <BrainCircuit size={15} />
      <span>
        {!ollama?.available
          ? <>Ollama is offline — AI predictions require Ollama. Start it: <code>ollama serve</code> then load the model: <code>ollama pull {ollama?.default_model || 'llama3.1'}</code></>
          : <>Ollama is running but <strong>{ollama?.default_model || 'llama3.1'}</strong> is not loaded — run: <code>ollama pull {ollama?.default_model || 'llama3.1'}</code></>}
      </span>
    </div>
  )
}

// Function: recommendationPlaceholder
function recommendationPlaceholder(row, ollama, ollamaModelReady) {
  if (!row.selectedValue) return 'Select a Current State to enable predictions.'
  if (row.predictionAttempted && !row.gapRecommendation) {
    return `Ollama returned empty — ensure model is loaded: ollama pull ${ollama?.default_model || 'llama3.1'}`
  }
  if (!ollama?.available) return 'Start Ollama: ollama serve  ·  ollama pull llama3.1'
  if (!ollamaModelReady) return `Load model first: ollama pull ${ollama?.default_model || 'llama3.1'}`
  return 'Click Generate Predictions (header) or Predict (this row) to run AI analysis.'
}

// Function: recommendationSourceLabel
function recommendationSourceLabel(row) {
  if (row.recommendationSource === 'ollama') {
    return `Source: ollama${row.recommendationModel ? ` · ${row.recommendationModel}` : ''}`
  }
  return row.gapRecommendation ? 'Source: manual' : ''
}

// Function: EvidenceCell
function EvidenceCell({ row, onEvidenceChange, onEvidenceFileUpload, onEvidenceFileRemove }) {
  return (
    <div className="evidence-cell">
      <textarea
        rows={3}
        value={row.evidence}
        disabled={!row.entry}
        onChange={(event) => onEvidenceChange(row, event.target.value)}
        placeholder="Attach evidence details, control notes, or assessor comments."
      />
      <label className={`mini-button evidence-attach-btn${!row.entry ? ' disabled' : ''}`}>
        <Paperclip size={13} /> Attach files
        <input
          type="file"
          multiple
          accept=".pdf,.xlsx,.xls,.pptx,.ppt,.png,.jpg,.jpeg,.gif,.webp"
          disabled={!row.entry}
          style={{ display: 'none' }}
          onChange={(e) => {
            if (e.target.files.length) {
              onEvidenceFileUpload(row, Array.from(e.target.files))
              e.target.value = ''
            }
          }}
        />
      </label>
      {row.evidenceFiles.length > 0 && (
        <ul className="evidence-file-list">
          {row.evidenceFiles.map((f) => (
            <li key={f.storedName} className="evidence-file-item">
              <a
                href={`${API_BASE}/towers/${row.entry?.towerKey}/rows/${row.entry?.id}/evidence-files/${f.storedName}`}
                target="_blank"
                rel="noreferrer"
                title={f.originalName}
              >
                <FileText size={11} />
                <span>{f.originalName}</span>
              </a>
              <button
                type="button"
                className="file-remove-btn"
                disabled={!row.entry}
                onClick={() => onEvidenceFileRemove(row, f.storedName)}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// Function: RecommendationCell
function RecommendationCell({ row, rowBusy, batchPredicting, ollamaModelReady, ollama, onGapChange, onPredictRow }) {
  const title = ollamaGateTitle(
    ollama, ollamaModelReady, batchPredicting,
    'Batch prediction in progress — wait for it to complete',
    !row.selectedValue ? 'Select a Current State first' : 'Regenerate AI prediction for this row',
  )
  return (
    <div className="recommendation-cell">
      <textarea
        rows={5}
        value={row.gapRecommendation}
        disabled={!row.entry}
        onChange={(event) => onGapChange(row, event.target.value)}
        placeholder={recommendationPlaceholder(row, ollama, ollamaModelReady)}
      />
      <div className="recommendation-meta">
        <span>{recommendationSourceLabel(row)}</span>
        <button
          type="button"
          className="mini-button"
          disabled={!row.selectedValue || !ollamaModelReady || rowBusy || batchPredicting}
          title={title}
          onClick={() => onPredictRow(row)}
        >
          <BrainCircuit size={14} /> {rowBusy ? 'Working...' : 'Predict'}
        </button>
      </div>
    </div>
  )
}

// Function: AssessmentRow
function AssessmentRow({
  row, uiCollections, catalogRows, rowBusy, batchPredicting, ollamaModelReady, ollama,
  onSelectionChange, onCurrentStateChange, onEvidenceChange, onEvidenceFileUpload, onEvidenceFileRemove, onGapChange, onPredictRow,
}) {
  const options = buildRowOptions(uiCollections)
  // Catalog-scoped, deduplicated options for this row — all dimensions allowed per application
  const rowDimOptions = row.application
    ? uniqueValues(catalogRows.filter((r) => r.towerKey === row.application).map((r) => r.dimension))
    : options.dimensions
  // Phase: full list + current row's phase in case it's a catalog generic like "All Phases"
  const rowPhaseOptions = uniqueValues([
    ...(row.phase && !options.phases.includes(row.phase) ? [row.phase] : []),
    ...options.phases,
  ])
  // Question: always the full master list from uiCollections; catalog is for weight/metadata only
  const rowQuestionOptions = options.questions

  return (
    <tr>
      <td>
        <select value={row.application} onChange={(event) => onSelectionChange(row.uiId, 'application', event.target.value)}>
          <option value="">Select application</option>
          {options.applications.map((option) => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
      </td>
      <td>
        <select
          value={row.dimension}
          disabled={!row.application}
          onChange={(event) => onSelectionChange(row.uiId, 'dimension', event.target.value)}
        >
          <option value="">Select dimension</option>
          {rowDimOptions.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </td>
      <td>
        <select
          value={row.phase}
          disabled={!row.dimension}
          onChange={(event) => onSelectionChange(row.uiId, 'phase', event.target.value)}
        >
          <option value="">Select phase</option>
          {rowPhaseOptions.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </td>
      <td>
        <select
          value={row.question}
          disabled={!row.phase}
          onChange={(event) => onSelectionChange(row.uiId, 'question', event.target.value)}
        >
          <option value="">Select assessment question</option>
          {rowQuestionOptions.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </td>
      <td>
        <select
          value={row.currentState}
          disabled={!row.question}
          onChange={(event) => onCurrentStateChange(row, event.target.value)}
        >
          <option value="">Select current state</option>
          {options.currentStates.map((option) => (
            <option key={`${row.uiId}-${option}`} value={option}>{option}</option>
          ))}
        </select>
      </td>
      <td>
        <div className={`calc-pill ${row.selectedValue ? 'filled' : ''}`}>
          {row.selectedValue || '--'}
        </div>
      </td>
      <td>
        <div className={`score-box score-${row.estimatedScore || 0}`}>
          {row.estimatedScore || '--'}
        </div>
      </td>
      <td>
        <div className={`calc-pill ${row.weight ? 'filled' : ''}`}>
          {row.weight || '--'}
        </div>
      </td>
      <td>
        <div className={`calc-pill ${row.weightedScore ? 'filled strong' : ''}`}>
          {row.weightedScore || '--'}
        </div>
      </td>
      <td>
        <EvidenceCell
          row={row}
          onEvidenceChange={onEvidenceChange}
          onEvidenceFileUpload={onEvidenceFileUpload}
          onEvidenceFileRemove={onEvidenceFileRemove}
        />
      </td>
      <td>
        <RecommendationCell
          row={row}
          rowBusy={rowBusy}
          batchPredicting={batchPredicting}
          ollamaModelReady={ollamaModelReady}
          ollama={ollama}
          onGapChange={onGapChange}
          onPredictRow={onPredictRow}
        />
      </td>
    </tr>
  )
}

// Function: AssessmentTable
function AssessmentTable({
  filteredRows, uiCollections, catalogRows, busyRowKey, batchPredicting, ollamaModelReady, ollama,
  onSelectionChange, onCurrentStateChange, onEvidenceChange, onEvidenceFileUpload, onEvidenceFileRemove, onGapChange, onPredictRow,
}) {
  return (
    <div className="grid-table-wrap">
      <table className="grid-table">
        <thead>
          <tr>
            <th>Applications</th>
            <th>Dimension</th>
            <th>SSDLC Phase(s)</th>
            <th>Assessment Question</th>
            <th>Current State</th>
            <th>Selected Value</th>
            <th>Estimated Score</th>
            <th>Weight</th>
            <th>Weighted Score</th>
            <th>Evidence / Comments</th>
            <th>Gap / Recommendation</th>
          </tr>
        </thead>
        <tbody>
          {filteredRows.map((row) => (
            <AssessmentRow
              key={row.uiId}
              row={row}
              uiCollections={uiCollections}
              catalogRows={catalogRows}
              rowBusy={busyRowKey === row.uiId}
              batchPredicting={batchPredicting}
              ollamaModelReady={ollamaModelReady}
              ollama={ollama}
              onSelectionChange={onSelectionChange}
              onCurrentStateChange={onCurrentStateChange}
              onEvidenceChange={onEvidenceChange}
              onEvidenceFileUpload={onEvidenceFileUpload}
              onEvidenceFileRemove={onEvidenceFileRemove}
              onGapChange={onGapChange}
              onPredictRow={onPredictRow}
            />
          ))}
          {!filteredRows.length && (
            <tr>
              <td colSpan={11}>
                <div className="empty-state">
                  No rows matched the active filters. Reset the filters to see the full blank assessment register.
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

// Function: AssessmentRegisterSection
function AssessmentRegisterSection({
  uiCollections, onLoadApplication, enrichedRows, ollamaModelReady, ollama, batchPredicting, batchProgress,
  onGenerateAllPredictions, dashboard, draftRows, appStats, onOpenExecDashboard,
  filteredRows, catalogRows, busyRowKey, onSelectionChange, onCurrentStateChange, onEvidenceChange,
  onEvidenceFileUpload, onEvidenceFileRemove, onGapChange, onPredictRow,
}) {
  return (
    <section className="workspace-card">
      <div className="section-header">
        <div>
          <p className="eyebrow">Assessment Register</p>
          <h2>Assessment Data Collection</h2>
        </div>
        <div className="header-actions">
          <LoadAppButtons applications={uiCollections.applications} onLoad={onLoadApplication} />
          <BatchPredictButton
            enrichedRows={enrichedRows}
            ollama={ollama}
            ollamaModelReady={ollamaModelReady}
            batchPredicting={batchPredicting}
            batchProgress={batchProgress}
            onClick={onGenerateAllPredictions}
          />
          <PredictAllButton
            draftRowsCount={draftRows.length}
            enrichedRows={enrichedRows}
            ollama={ollama}
            ollamaModelReady={ollamaModelReady}
            batchPredicting={batchPredicting}
            batchProgress={batchProgress}
            onClick={onGenerateAllPredictions}
          />
          <ExecDashboardButton dashboard={dashboard} onClick={onOpenExecDashboard} />
          <div className="inline-pill">
            <LayoutPanelTop size={16} />
            {draftRows.length} rows · {appStats.total} application{appStats.total !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      {batchPredicting && batchProgress && (
        <div className="batch-progress">
          <div
            className="batch-progress-fill"
            style={{ width: `${Math.round((batchProgress.current / batchProgress.total) * 100)}%` }}
          />
        </div>
      )}

      <OllamaOfflineBanner ollamaModelReady={ollamaModelReady} ollama={ollama} />

      <AssessmentTable
        filteredRows={filteredRows}
        uiCollections={uiCollections}
        catalogRows={catalogRows}
        busyRowKey={busyRowKey}
        batchPredicting={batchPredicting}
        ollamaModelReady={ollamaModelReady}
        ollama={ollama}
        onSelectionChange={onSelectionChange}
        onCurrentStateChange={onCurrentStateChange}
        onEvidenceChange={onEvidenceChange}
        onEvidenceFileUpload={onEvidenceFileUpload}
        onEvidenceFileRemove={onEvidenceFileRemove}
        onGapChange={onGapChange}
        onPredictRow={onPredictRow}
      />
    </section>
  )
}

// Function: PortfolioKpiRow
function PortfolioKpiRow({ dashboard }) {
  const gapValue = dashboard.portfolio?.overallScorePct != null
    ? dashboard.targetPct - dashboard.portfolio.overallScorePct
    : null
  return (
    <div className="exec-kpi-row">
      <div className="exec-kpi-card">
        <span className="exec-kpi-value" style={{ color: scoreColor(dashboard.portfolio?.overallScorePct) }}>
          {dashboard.portfolio?.overallScorePct != null ? `${dashboard.portfolio.overallScorePct}%` : '--'}
        </span>
        <span className="exec-kpi-label">Portfolio Score</span>
        {dashboard.portfolio?.overallLevel && (
          <span className={`exec-level-chip lvl-${dashboard.portfolio.overallLevel.toLowerCase().replace(' ', '-')}`}>
            {dashboard.portfolio.overallLevel}
          </span>
        )}
      </div>
      <div className="exec-kpi-card">
        <span className="exec-kpi-value">{dashboard.portfolio?.assessedTowers}/{dashboard.portfolio?.towerCount}</span>
        <span className="exec-kpi-label">Towers Assessed</span>
      </div>
      <div className="exec-kpi-card">
        <span className="exec-kpi-value">{dashboard.targetPct}%</span>
        <span className="exec-kpi-label">Target Score</span>
      </div>
      <div className="exec-kpi-card">
        {gapValue != null
          ? (
            <span className="exec-kpi-value gap" style={{ color: gapValue > 0 ? '#dc2626' : '#16a34a' }}>
              {gapValue > 0 ? `${gapValue.toFixed(1)}% below` : 'On target'}
            </span>
          )
          : <span className="exec-kpi-value">--</span>}
        <span className="exec-kpi-label">Portfolio Gap</span>
      </div>
    </div>
  )
}

// Function: TowerSummaryRow
function TowerSummaryRow({ card }) {
  return (
    <tr>
      <td className="exec-tower-name">{card.name}</td>
      <td>
        <div className="exec-score-cell">
          <span style={{ color: scoreColor(card.overallScorePct), fontWeight: 700 }}>
            {card.overallScorePct != null ? `${card.overallScorePct}%` : '--'}
          </span>
          {card.overallScorePct != null && (
            <div className="exec-mini-bar">
              <div style={{ width: `${card.overallScorePct}%`, backgroundColor: scoreColor(card.overallScorePct) }} />
            </div>
          )}
        </div>
      </td>
      <td>
        {card.overallLevel
          ? <span className={`exec-level-chip lvl-${card.overallLevel.toLowerCase().replace(' ', '-')}`}>{card.overallLevel}</span>
          : '--'}
      </td>
      <td className="exec-num">{card.answered}</td>
      <td className="exec-num">{card.totalQuestions}</td>
      <td className="exec-concern">{card.topConcern || '--'}</td>
      <td className="exec-num">{card.targetPct}%</td>
      <td className="exec-num" style={{
        color: card.gapToTarget > 20 ? '#dc2626' : card.gapToTarget > 5 ? '#d97706' : '#16a34a',
        fontWeight: 600,
      }}>
        {card.gapToTarget != null ? `${card.gapToTarget}%` : '--'}
      </td>
    </tr>
  )
}

// Function: TowerSummaryTable
function TowerSummaryTable({ cards }) {
  return (
    <div className="exec-table-wrap">
      <table className="exec-table">
        <thead>
          <tr>
            <th>Tower</th>
            <th>Score %</th>
            <th>Level</th>
            <th>Answered</th>
            <th>Total Q</th>
            <th>Top Concern</th>
            <th>Target %</th>
            <th>Gap</th>
          </tr>
        </thead>
        <tbody>
          {cards?.map((card) => <TowerSummaryRow key={card.key} card={card} />)}
        </tbody>
      </table>
    </div>
  )
}

// Function: OverallMaturityChart
function OverallMaturityChart({ cards }) {
  return (
    <div className="exec-vchart-container">
      <div className="exec-vchart-wrap">
        <div className="exec-vchart-yaxis">
          {[100, 80, 60, 40, 20, 0].map(v => (
            <span key={v} className="exec-vchart-ylabel">{v.toFixed(1)}</span>
          ))}
        </div>
        <div className="exec-vchart-right">
          <div className="exec-vchart-area">
            {[0, 20, 40, 60, 80, 100].map(v => (
              <div key={v} className="exec-vchart-gridline" style={{ bottom: `${v}%` }} />
            ))}
            {cards?.map((card) => (
              <div key={card.key} className="exec-vchart-bar"
                style={{ height: `${card.overallScorePct ?? 0}%`, backgroundColor: '#1e6b8a' }}
                title={card.overallScorePct != null ? `${card.name}: ${card.overallScorePct}%` : `${card.name}: Not assessed`}
              />
            ))}
          </div>
          <div className="exec-vchart-xlabels">
            {cards?.map((card) => (
              <div key={card.key} className="exec-vchart-xlabel">{card.name}</div>
            ))}
          </div>
        </div>
      </div>
      <div className="exec-vchart-legend">
        <span className="exec-legend-swatch" style={{ backgroundColor: '#1e6b8a' }} />
        <span>Overall Score %</span>
      </div>
    </div>
  )
}

// Function: DimensionBarGroup
function DimensionBarGroup({ dimRow, cards }) {
  return (
    <div className="exec-vchart-group">
      {cards?.map((card, ci) => {
        const score = dimRow.towers?.[card.key]?.scorePct
        return (
          <div key={card.key} className="exec-vchart-bar exec-vchart-bar--group"
            style={{ height: `${score ?? 0}%`, backgroundColor: TOWER_COLORS[ci % TOWER_COLORS.length] }}
            title={score != null ? `${dimRow.dimension} — ${card.name}: ${score}%` : `${dimRow.dimension} — ${card.name}: Not assessed`}
          />
        )
      })}
    </div>
  )
}

// Function: DimensionHeatmap
function DimensionHeatmap({ dashboard }) {
  if (!(dashboard.dimensionMatrix?.length > 0)) return null
  const cards = dashboard.cards
  const width = Math.max(dashboard.dimensionMatrix.length * 56, 300)
  return (
    <>
      <h3 className="exec-section-title">Dimension Maturity Heatmap View</h3>
      <div className="exec-vchart-container">
        <div className="exec-vchart-wrap">
          <div className="exec-vchart-yaxis">
            {[100, 80, 60, 40, 20, 0].map(v => (
              <span key={v} className="exec-vchart-ylabel">{v.toFixed(1)}</span>
            ))}
          </div>
          <div className="exec-vchart-right exec-vchart-right--scroll">
            <div className="exec-vchart-area exec-vchart-area--grouped" style={{ minWidth: `${width}px` }}>
              {[0, 20, 40, 60, 80, 100].map(v => (
                <div key={v} className="exec-vchart-gridline" style={{ bottom: `${v}%` }} />
              ))}
              {dashboard.dimensionMatrix.map((dimRow) => (
                <DimensionBarGroup key={dimRow.dimension} dimRow={dimRow} cards={cards} />
              ))}
            </div>
            <div className="exec-vchart-xlabels exec-vchart-xlabels--rotated" style={{ minWidth: `${width}px` }}>
              {dashboard.dimensionMatrix.map((dimRow) => (
                <div key={dimRow.dimension} className="exec-vchart-xlabel exec-vchart-xlabel--rotated">
                  <span>{dimRow.dimension}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="exec-vchart-legend">
          {cards?.map((card, ci) => (
            <span key={card.key} className="exec-vchart-legend-item">
              <span className="exec-legend-swatch" style={{ backgroundColor: TOWER_COLORS[ci % TOWER_COLORS.length] }} />
              <span>{card.name}</span>
            </span>
          ))}
        </div>
      </div>
    </>
  )
}

// Function: ExecNarrativeSection
function ExecNarrativeSection({ ollamaModelReady, ollama, execNarrative, execGenerating }) {
  return (
    <>
      <h3 className="exec-section-title">
        <BrainCircuit size={16} />
        AI Executive Narrative
        {!ollamaModelReady && (
          <span className="exec-ollama-note">
            — Ollama {ollama?.available ? 'model not loaded' : 'offline'} · run: ollama pull {ollama?.default_model || 'llama3.1'}
          </span>
        )}
      </h3>
      {(execNarrative || execGenerating) ? (
        <div className="exec-narrative">
          <pre className="exec-narrative-text">{execNarrative}</pre>
          {execGenerating && <span className="exec-cursor">▌</span>}
        </div>
      ) : (
        <p className="exec-narrative-hint">
          {ollamaModelReady
            ? 'Click "Generate AI Narrative" above for Ollama-powered executive insights.'
            : `Start Ollama and pull the model to generate AI insights.`}
        </p>
      )}
    </>
  )
}

// Function: ExecDashboardModal
function ExecDashboardModal({ dashboard, ollama, ollamaModelReady, execGenerating, execNarrative, onGenerateNarrative, onClose }) {
  return (
    <div className="exec-overlay" role="dialog" aria-modal="true"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="exec-panel">
        <div className="exec-panel-header">
          <div className="exec-panel-title">
            <ShieldCheck size={20} />
            Executive SSDLC Maturity Dashboard
          </div>
          <div className="exec-header-actions">
            <button
              className="exec-ai-btn"
              disabled={!ollamaModelReady || execGenerating}
              title={!ollamaModelReady ? `Run: ollama pull ${ollama?.default_model || 'llama3.1'}` : 'Generate AI executive narrative'}
              onClick={onGenerateNarrative}
            >
              <BrainCircuit size={14} />
              {execGenerating ? 'Generating…' : 'Generate AI Narrative'}
            </button>
            <button className="exec-close-btn" onClick={onClose} title="Close">
              <X size={16} />
            </button>
          </div>
        </div>

        <PortfolioKpiRow dashboard={dashboard} />

        <h3 className="exec-section-title">Tower Summary</h3>
        <TowerSummaryTable cards={dashboard.cards} />

        <h3 className="exec-section-title">Overall Maturity by Tower</h3>
        <OverallMaturityChart cards={dashboard.cards} />

        <DimensionHeatmap dashboard={dashboard} />

        <ExecNarrativeSection
          ollamaModelReady={ollamaModelReady}
          ollama={ollama}
          execNarrative={execNarrative}
          execGenerating={execGenerating}
        />
      </div>
    </div>
  )
}

// Function: App
function App() {
  const [authReady, setAuthReady] = useState(false)
  const [authUser, setAuthUser] = useState(null)
  const [authError, setAuthError] = useState('')
  const [towers, setTowers] = useState({})
  const [towerOrder, setTowerOrder] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [ollama, setOllama] = useState(null)
  const [uiCollections, setUiCollections] = useState({
    applications: [],
    dimensions: [],
    phases: [],
    questions: [],
    currentStates: [],
  })
  const [currentStateMap, setCurrentStateMap] = useState({})
  const [draftRows, setDraftRows] = useState([])
  const [status, setStatus] = useState('Loading assessment workspace')
  const [busyRowKey, setBusyRowKey] = useState('')
  const [busyTowerKey, setBusyTowerKey] = useState('')
  const [lastSavedAt, setLastSavedAt] = useState('')
  const [batchPredicting, setBatchPredicting] = useState(false)
  const [batchProgress, setBatchProgress] = useState(null)
  const [showExecDashboard, setShowExecDashboard] = useState(false)
  const [execNarrative, setExecNarrative] = useState('')
  const [execGenerating, setExecGenerating] = useState(false)
  const [filters, setFilters] = useState({
    application: '',
    dimension: '',
    phase: '',
    question: '',
    currentState: '',
    search: '',
  })
  const saveTimers = useRef({})

  const catalogRows = useMemo(() => flattenRows(towers, towerOrder), [towers, towerOrder])
  const enrichedRows = useMemo(
    () => draftRows.map((row) => enrichDraftRow(row, catalogRows, towers, currentStateMap, uiCollections)),
    [draftRows, catalogRows, towers, currentStateMap, uiCollections],
  )
  const filteredRows = useMemo(() => filterRows(enrichedRows, filters), [enrichedRows, filters])
  const visibleSummary = useMemo(() => getVisibleSummary(filteredRows), [filteredRows])

  // One representative catalog row per unique dimension per application
  const catalogByApp = useMemo(() => {
    const map = {}
    catalogRows.forEach((row) => {
      if (!map[row.towerKey]) map[row.towerKey] = new Map()
      if (!map[row.towerKey].has(row.dimension)) map[row.towerKey].set(row.dimension, row)
    })
    return map
  }, [catalogRows])

  // Reverse of currentStateMap: selectedLevelKey → first matching description string.
  // Used to restore currentState text when loading rows from saved tower state.
  const reverseStateMap = useMemo(() => {
    const m = {}
    Object.entries(currentStateMap).forEach(([desc, v]) => {
      if (!m[v.key]) m[v.key] = desc
    })
    return m
  }, [currentStateMap])

  // True only when Ollama is reachable AND the configured model is actually loaded.
  const ollamaModelReady = useMemo(() => {
    if (!ollama?.available || !ollama?.models?.length) return false
    const modelName = ollama.default_model || 'llama3.1'
    return ollama.models.some(
      (m) => m.name === modelName || m.name?.startsWith(`${modelName}:`),
    )
  }, [ollama])

  const appStats = useMemo(() => {
    const assessed = new Set(enrichedRows.filter((r) => r.estimatedScore > 0 && r.application).map((r) => r.application))
    return { assessed: assessed.size, total: towerOrder.length }
  }, [enrichedRows, towerOrder])

  useEffect(() => {
    let active = true

    // Function: bootstrapAuth
    async function bootstrapAuth() {
      consumePortalTokenFromHash()
      const token = getPortalToken()
      const isLocalhost = ['localhost', '127.0.0.1'].includes(window.location.hostname)
      if (!token && isLocalhost) {
        setAuthUser({ username: 'local-admin', role: 'admin' })
        setAuthReady(true)
        return
      }
      if (!token) {
        setAuthError('No active portal session found. Open this module from the launcher.')
        setAuthReady(true)
        return
      }
      try {
        const response = await authFetch(`${API_BASE}/auth/session`)
        if (!response.ok) throw new Error(await response.text())
        const payload = await response.json()
        if (!payload.authenticated) throw new Error('Session expired')
        if (active) setAuthUser(payload.user)
      } catch {
        clearPortalToken()
        if (isLocalhost) {
          if (active) setAuthUser({ username: 'local-admin', role: 'admin' })
        } else if (active) {
          setAuthError('Session expired or permission denied for SSDLC Process Assessment.')
        }
      } finally {
        if (active) setAuthReady(true)
      }
    }

    // Function: bootstrapData
    async function bootstrapData() {
      try {
        const response = await authFetch(`${API_BASE}/bootstrap`)
        if (!response.ok) throw new Error(await response.text())
        const payload = await response.json()
        if (!active) return
        const nextTowers = Object.fromEntries(payload.towers.map((tower) => [tower.key, tower]))
        const nextTowerOrder = payload.towers.map((tower) => tower.key)
        const nextCollections = payload.uiCollections || {
          applications: [],
          dimensions: [],
          phases: [],
          questions: [],
          currentStates: [],
        }
        setTowers(nextTowers)
        setTowerOrder(nextTowerOrder)
        setDashboard(payload.dashboard)
        setOllama(payload.ollama)
        setUiCollections(nextCollections)
        setCurrentStateMap(payload.currentStateMap || {})
        setDraftRows(createDraftRows(nextCollections.questions.length || 22))
        setStatus('Ready for assessment')
      } catch {
        if (active) setStatus('Unable to load assessment data')
      }
    }

    bootstrapAuth().then(bootstrapData)
    return () => {
      active = false
      Object.values(saveTimers.current).forEach((timer) => window.clearTimeout(timer))
    }
  }, [])

  // Poll Ollama status every 30s so the UI auto-updates when Ollama comes online
  useEffect(() => {
    const id = window.setInterval(async () => {
      try {
        const res = await authFetch(`${API_BASE}/ollama/status`)
        if (res.ok) setOllama(await res.json())
      } catch { /* ignore */ }
    }, 30_000)
    return () => window.clearInterval(id)
  }, [])

  // Shared prediction helper.
  // currentStateText must be passed explicitly — do NOT rely on row.currentState because
  // React state updates are async and row.currentState may still hold the pre-change value.
  // Function: predictCatalogRow
  async function predictCatalogRow(row, selectedLevelKey, currentState) {
    const res = await authFetch(`${API_BASE}/towers/${row.entry.towerKey}/row-predictions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rowId: row.entry.id,
        selectedLevelKey,
        evidence: row.evidence || '',
        currentState,
      }),
    })
    if (!res.ok) {
      const errText = await res.text()
      throw new Error(`Prediction API error ${res.status}: ${errText}`)
    }
    const data = await res.json()
    setTowers((prev) => ({ ...prev, [row.entry.towerKey]: data.tower }))
    setDashboard(data.dashboard)
    setOllama(data.ollama)
    const refreshed = data.tower.responses.find((r) => r.id === row.entry.id)
    return refreshed
      ? {
          weight: refreshed.weight,
          gapRecommendation: refreshed.gapRecommendation || '',
          recommendationSource: refreshed.recommendationSource || null,
          recommendationModel: refreshed.recommendationModel || null,
        }
      : null
  }

  // Function: predictAdhocRow
  // No catalog entry — ad-hoc prediction (weight + recommendation, no persistent tower state)
  // Function: predictAdhocRow
  async function predictAdhocRow(row, selectedLevelKey, currentState) {
    const towerMeta = towers[row.application]
    const res = await authFetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        applicationName: towerMeta?.name || row.application,
        dimension: row.dimension,
        phase: row.phase,
        question: row.question,
        selectedLevelKey,
        evidence: row.evidence || '',
        currentState,
      }),
    })
    if (!res.ok) {
      const errText = await res.text()
      throw new Error(`Ad-hoc prediction error ${res.status}: ${errText}`)
    }
    const data = await res.json()
    setOllama(data.ollama)
    return {
      weight: data.weight,
      gapRecommendation: data.recommendation || '',
      recommendationSource: data.source || null,
      recommendationModel: data.model || null,
    }
  }

  // Function: runPrediction
  async function runPrediction(row, selectedLevelKey, currentStateText) {
    if (!selectedLevelKey) return null
    const currentState = (currentStateText ?? row.currentState) || ''
    return row.entry
      ? predictCatalogRow(row, selectedLevelKey, currentState)
      : predictAdhocRow(row, selectedLevelKey, currentState)
  }

  // Function: saveTower
  async function saveTower(towerKey, towerPayload, nextStatus = 'Assessment updated') {
    try {
      const response = await authFetch(`${API_BASE}/towers/${towerKey}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          responses: towerPayload.responses.map((row) => ({
            id: row.id,
            selectedLevelKey: row.selectedLevelKey || null,
            predictedWeight: row.predictedWeight || null,
            evidence: row.evidence || '',
            gapRecommendation: row.gapRecommendation || '',
            recommendationSource: row.recommendationSource || null,
            recommendationModel: row.recommendationModel || null,
          })),
        }),
      })
      if (!response.ok) throw new Error(await response.text())
      const payload = await response.json()
      setTowers((prev) => ({ ...prev, [towerKey]: payload.tower }))
      setDashboard(payload.dashboard)
      setLastSavedAt(new Date().toLocaleTimeString())
      setStatus(nextStatus)
    } catch {
      setStatus('Unable to save the latest assessment change')
    }
  }

  // Function: queueSave
  function queueSave(towerKey, towerPayload, nextStatus = 'Assessment updated') {
    if (saveTimers.current[towerKey]) {
      window.clearTimeout(saveTimers.current[towerKey])
    }
    saveTimers.current[towerKey] = window.setTimeout(() => {
      saveTower(towerKey, towerPayload, nextStatus)
    }, 700)
  }

  // Function: persistResolvedRow
  function persistResolvedRow(entry, patch, immediate = false, nextStatus = 'Assessment updated') {
    if (!entry) return
    setTowers((prev) => {
      const tower = prev[entry.towerKey]
      if (!tower) return prev
      const nextTower = {
        ...tower,
        responses: tower.responses.map((row) => (row.id === entry.id ? { ...row, ...patch } : row)),
      }
      if (immediate) {
        saveTower(entry.towerKey, nextTower, nextStatus)
      } else {
        queueSave(entry.towerKey, nextTower, nextStatus)
      }
      return { ...prev, [entry.towerKey]: nextTower }
    })
  }

  // Function: updateDraftRow
  function updateDraftRow(uiId, updater) {
    setDraftRows((prev) => prev.map((row) => (row.uiId === uiId ? updater(row) : row)))
  }

  // Function: handleSelectionChange
  function handleSelectionChange(uiId, field, value) {
    updateDraftRow(uiId, (row) => {
      if (field === 'application') {
        return {
          ...row,
          application: value,
          dimension: '',
          phase: '',
          question: '',
          currentState: '',
          predictedWeight: null,
          evidence: '',
          gapRecommendation: '',
          recommendationSource: '',
          recommendationModel: '',
        }
      }
      if (field === 'dimension') {
        return {
          ...row,
          dimension: value,
          phase: '',
          question: '',
          currentState: '',
          predictedWeight: null,
          evidence: '',
          gapRecommendation: '',
          recommendationSource: '',
          recommendationModel: '',
        }
      }
      if (field === 'phase') {
        return {
          ...row,
          phase: value,
          question: '',
          currentState: '',
          predictedWeight: null,
          evidence: '',
          gapRecommendation: '',
          recommendationSource: '',
          recommendationModel: '',
        }
      }
      if (field === 'question') {
        return {
          ...row,
          question: value,
          currentState: '',
          predictedWeight: null,
          evidence: '',
          gapRecommendation: '',
          recommendationSource: '',
          recommendationModel: '',
        }
      }
      return row
    })
  }

  // Function: handleCurrentStateChange
  function handleCurrentStateChange(row, nextDescription) {
    const mappedState = currentStateMap[nextDescription.trim()] || null

    updateDraftRow(row.uiId, (draft) => ({
      ...draft,
      currentState: nextDescription,
      predictedWeight: null,
      gapRecommendation: '',
      recommendationSource: null,
      recommendationModel: '',
    }))

    if (row.entry) {
      persistResolvedRow(
        row.entry,
        {
          selectedLevelKey: mappedState?.key || null,
          predictedWeight: null,
          evidence: row.evidence || '',
          gapRecommendation: '',
          recommendationSource: null,
          recommendationModel: null,
        },
        false,
        mappedState?.key ? 'Current state saved' : 'Current state cleared',
      )
    }
    if (mappedState?.key) {
      setStatus('Current state set — click Generate Predictions to run AI analysis')
    }
  }

  // Function: handleEvidenceChange
  function handleEvidenceChange(row, value) {
    updateDraftRow(row.uiId, (draft) => ({ ...draft, evidence: value }))
    if (!row.entry) return
    persistResolvedRow(
      row.entry,
      {
        selectedLevelKey: row.selectedValue || null,
        predictedWeight: row.weight || null,
        evidence: value,
        gapRecommendation: row.gapRecommendation || '',
        recommendationSource: row.recommendationSource || null,
        recommendationModel: row.recommendationModel || null,
      },
      false,
      'Evidence updated',
    )
  }

  // Function: handleEvidenceFileUpload
  async function handleEvidenceFileUpload(row, files) {
    if (!row.entry || !files.length) return
    setStatus('Uploading evidence file…')
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      try {
        const response = await authFetch(
          `${API_BASE}/towers/${row.entry.towerKey}/rows/${row.entry.id}/evidence-files`,
          { method: 'POST', body: formData },
        )
        if (!response.ok) throw new Error(await response.text())
        const payload = await response.json()
        setTowers((prev) => ({ ...prev, [row.entry.towerKey]: payload.tower }))
        setDashboard(payload.dashboard)
      } catch {
        setStatus('Failed to upload evidence file')
        return
      }
    }
    setLastSavedAt(new Date().toLocaleTimeString())
    setStatus('Evidence file uploaded')
  }

  // Function: handleEvidenceFileRemove
  async function handleEvidenceFileRemove(row, storedName) {
    if (!row.entry) return
    setStatus('Removing evidence file…')
    try {
      const response = await authFetch(
        `${API_BASE}/towers/${row.entry.towerKey}/rows/${row.entry.id}/evidence-files/${storedName}`,
        { method: 'DELETE' },
      )
      if (!response.ok) throw new Error(await response.text())
      const payload = await response.json()
      setTowers((prev) => ({ ...prev, [row.entry.towerKey]: payload.tower }))
      setDashboard(payload.dashboard)
      setLastSavedAt(new Date().toLocaleTimeString())
      setStatus('Evidence file removed')
    } catch {
      setStatus('Failed to remove evidence file')
    }
  }

  // Function: handleGapChange
  function handleGapChange(row, value) {
    updateDraftRow(row.uiId, (draft) => ({ ...draft, gapRecommendation: value }))
    if (!row.entry) return
    persistResolvedRow(
      row.entry,
      {
        selectedLevelKey: row.selectedValue || null,
        predictedWeight: row.weight || null,
        evidence: row.evidence || '',
        gapRecommendation: value,
        recommendationSource: row.recommendationSource || null,
        recommendationModel: row.recommendationModel || null,
      },
      false,
      'Recommendation updated',
    )
  }

  // Function: applyPredictionResult
  function applyPredictionResult(row, levelKey, result) {
    updateDraftRow(row.uiId, (draft) => ({
      ...draft,
      predictedWeight: result.weight || null,
      gapRecommendation: result.gapRecommendation || '',
      recommendationSource: result.recommendationSource || null,
      recommendationModel: result.recommendationModel || null,
      predictionAttempted: true,
    }))
    // Persist the updated prediction so it survives a page reload
    if (row.entry) {
      persistResolvedRow(row.entry, {
        selectedLevelKey: levelKey,
        predictedWeight: result.weight || null,
        evidence: row.evidence || '',
        gapRecommendation: result.gapRecommendation || '',
        recommendationSource: result.recommendationSource || null,
        recommendationModel: result.recommendationModel || null,
      }, false, 'Prediction saved')
    }
    setLastSavedAt(new Date().toLocaleTimeString())
    const modelName = ollama?.default_model || 'llama3.1'
    setStatus(result.gapRecommendation
      ? `AI recommendation generated (${result.recommendationSource || 'ollama'})`
      : `Ollama returned empty — ensure model is loaded: ollama pull ${modelName}`)
  }

  // Function: generateRecommendationForRow
  async function generateRecommendationForRow(row) {
    // selectedValue may be empty for ad-hoc rows; fall back to currentState mapping
    const levelKey = row.selectedValue || (row.currentState ? currentStateMap[row.currentState.trim()]?.key : null)
    if (!levelKey) {
      setStatus('Select a Current State before predicting')
      return
    }
    setBusyRowKey(row.uiId)
    if (row.entry) setBusyTowerKey(row.entry.towerKey)
    setStatus('Generating AI prediction…')
    try {
      // row.currentState is not stale here (user clicked Predict, no pending state update)
      const result = await runPrediction(row, levelKey, row.currentState)
      if (result) {
        applyPredictionResult(row, levelKey, result)
      } else {
        setStatus('Prediction returned no data — check backend logs')
      }
    } catch (err) {
      setStatus(`Prediction failed: ${err.message}`)
    } finally {
      setBusyRowKey('')
      setBusyTowerKey('')
    }
  }

  // Function: resetFilters
  function resetFilters() {
    setFilters({
      application: '',
      dimension: '',
      phase: '',
      question: '',
      currentState: '',
      search: '',
    })
  }

  // Function: handleLoadApplicationRows
  function handleLoadApplicationRows(appKey) {
    if (!appKey || !catalogByApp[appKey]) return
    const dimEntries = [...catalogByApp[appKey].entries()]
    const existingDims = new Set(
      draftRows.filter((r) => r.application === appKey && r.dimension).map((r) => r.dimension),
    )
    const toLoad = dimEntries.filter(([dim]) => !existingDims.has(dim))
    if (!toLoad.length) {
      setStatus(`All ${dimEntries.length} dimensions already loaded for this application`)
      return
    }

    // Build a lookup from saved tower state so rows restore prior selections + predictions
    const savedTower = towers[appKey]
    const savedById = {}
    if (savedTower) {
      savedTower.responses.forEach((r) => { savedById[r.id] = r })
    }

    setDraftRows((prev) => {
      const updated = [...prev]
      let blankIdx = 0
      for (const [dim, catalogRow] of toLoad) {
        while (blankIdx < updated.length && updated[blankIdx].application) blankIdx++
        const base = buildLoadedRowBase(appKey, dim, catalogRow, savedById, reverseStateMap)
        blankIdx = placeLoadedRow(updated, blankIdx, appKey, dim, base)
      }
      return updated
    })
    const appName = towers[appKey]?.name || appKey
    setStatus(`Loaded ${toLoad.length} dimension row${toLoad.length !== 1 ? 's' : ''} for ${appName}`)
  }

  // Function: handleGenerateAllPredictions
  async function handleGenerateAllPredictions() {
    if (!ollamaModelReady) {
      const modelName = ollama?.default_model || 'llama3.1'
      setStatus(
        ollama?.available
          ? `Model not loaded — run: ollama pull ${modelName}`
          : 'Ollama offline — run: ollama serve  then: ollama pull llama3.1',
      )
      return
    }
    const rowsToPredict = enrichedRows.filter((r) => r.selectedValue && r.application && r.question)
    if (!rowsToPredict.length) {
      setStatus('No assessed rows to predict — select a Current State for at least one row first')
      return
    }
    setBatchPredicting(true)
    setBatchProgress({ current: 0, total: rowsToPredict.length })
    setStatus(`Starting AI prediction for ${rowsToPredict.length} row${rowsToPredict.length !== 1 ? 's' : ''}…`)
    let successCount = 0
    let failCount = 0
    try {
      const response = await authFetch(`${API_BASE}/predict-batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: buildBatchPredictionPayload(rowsToPredict) }),
      })
      if (!response.ok) throw new Error(await response.text())

      await readEventStream(response, (payload) => {
        if (payload.done) return
        setBatchProgress({ current: payload.index + 1, total: payload.total })
        setStatus(`Predicting… ${payload.index + 1} / ${payload.total}`)
        if (payload.skipped) return
        const succeeded = !!payload.recommendation
        successCount += succeeded ? 1 : 0
        failCount += succeeded ? 0 : 1
        updateDraftRow(payload.uiId, (draft) => ({
          ...draft,
          predictedWeight: payload.weight ?? draft.predictedWeight,
          gapRecommendation: payload.recommendation || '',
          recommendationSource: payload.source || null,
          recommendationModel: payload.model || null,
          predictionAttempted: true,
        }))
      })

      setLastSavedAt(new Date().toLocaleTimeString())
      setStatus(buildBatchCompletionStatus(successCount, failCount, rowsToPredict.length, ollama?.default_model))
      await refreshTowersAfterBatch(rowsToPredict)
    } catch (err) {
      setStatus(`Prediction failed: ${err.message}`)
    } finally {
      setBatchPredicting(false)
      setBatchProgress(null)
    }
  }

  // Function: refreshTowersAfterBatch
  // Refresh towers so dashboard metrics reflect the newly saved predictions
  // Function: refreshTowersAfterBatch
  async function refreshTowersAfterBatch(rowsToPredict) {
    const uniqueApps = [...new Set(rowsToPredict.map((r) => r.application).filter(Boolean))]
    await Promise.all(
      uniqueApps.map(async (appKey) => {
        try {
          const res = await authFetch(`${API_BASE}/towers/${appKey}`)
          if (res.ok) {
            const data = await res.json()
            setTowers((prev) => ({ ...prev, [appKey]: data.tower }))
            setDashboard(data.dashboard)
          }
        } catch { /* ignore */ }
      }),
    )
  }

  // Function: handleGenerateExecNarrative
  async function handleGenerateExecNarrative() {
    if (!ollamaModelReady || !dashboard) return
    setExecGenerating(true)
    setExecNarrative('')
    try {
      const response = await authFetch(`${API_BASE}/executive-summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dashboard, model: ollama?.default_model }),
      })
      if (!response.ok) throw new Error(await response.text())
      await readEventStream(response, (payload) => {
        if (payload.done) return false
        if (payload.text) setExecNarrative((prev) => prev + payload.text)
      })
    } catch (e) {
      setExecNarrative(`Error generating narrative: ${e.message}`)
    } finally {
      setExecGenerating(false)
    }
  }

  // Function: handlePortalLogout
  const handlePortalLogout = () => {
    clearPortalToken()
    window.location.href = PORTAL_LOGIN_URL
  }

  if (!authReady) {
    return <div className="auth-wall">Validating portal session...</div>
  }

  if (authError) {
    return (
      <div className="auth-wall">
        <section>
          <p className="eyebrow">Access Control</p>
          <h1>SSDLC assessment session required</h1>
          <p>{authError}</p>
          <button className="solid-button" onClick={() => { window.location.href = PORTAL_LOGIN_URL }}>
            Go to Portal Login
          </button>
        </section>
      </div>
    )
  }

  return (
    <main className="app-shell">
      <PortalHeader authUser={authUser} onLogout={handlePortalLogout} />

      <section className="page-shell">
        <HeroPanel status={status} lastSavedAt={lastSavedAt} ollama={ollama} ollamaModelReady={ollamaModelReady} />

        <MetricsGrid
          appStats={appStats}
          uiCollections={uiCollections}
          enrichedRows={enrichedRows}
          visibleSummary={visibleSummary}
          dashboard={dashboard}
        />

        <FiltersPanel filters={filters} setFilters={setFilters} uiCollections={uiCollections} onReset={resetFilters} />

        <AssessmentRegisterSection
          uiCollections={uiCollections}
          onLoadApplication={handleLoadApplicationRows}
          enrichedRows={enrichedRows}
          ollamaModelReady={ollamaModelReady}
          ollama={ollama}
          batchPredicting={batchPredicting}
          batchProgress={batchProgress}
          onGenerateAllPredictions={handleGenerateAllPredictions}
          dashboard={dashboard}
          draftRows={draftRows}
          appStats={appStats}
          onOpenExecDashboard={() => { setShowExecDashboard(true); setExecNarrative('') }}
          filteredRows={filteredRows}
          catalogRows={catalogRows}
          busyRowKey={busyRowKey}
          onSelectionChange={handleSelectionChange}
          onCurrentStateChange={handleCurrentStateChange}
          onEvidenceChange={handleEvidenceChange}
          onEvidenceFileUpload={handleEvidenceFileUpload}
          onEvidenceFileRemove={handleEvidenceFileRemove}
          onGapChange={handleGapChange}
          onPredictRow={generateRecommendationForRow}
        />
      </section>

      {showExecDashboard && dashboard && (
        <ExecDashboardModal
          dashboard={dashboard}
          ollama={ollama}
          ollamaModelReady={ollamaModelReady}
          execGenerating={execGenerating}
          execNarrative={execNarrative}
          onGenerateNarrative={handleGenerateExecNarrative}
          onClose={() => setShowExecDashboard(false)}
        />
      )}
    </main>
  )
}

export default App
