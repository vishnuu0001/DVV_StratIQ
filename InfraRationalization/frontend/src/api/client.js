// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/api (client.js)
// Date: 2026-06-05
// ---------------------------------------------------------------------------
import axios from 'axios'

const AUTH_TOKEN_KEY = 'infra_portal_auth_token'
// Dev: falls back to '/api' so vite proxy (/api → localhost:8083) still works.
// Prod: VITE_INFRA_API_URL=/api/infra → IIS rewrites /api/infra/* → localhost:8083/api/*
const API_BASE = import.meta.env.VITE_INFRA_API_URL ||
  (import.meta.env.DEV ? '/api' : '/api/infra')
const PORTAL_HOME_URL = import.meta.env.VITE_PORTAL_HOME_URL || '/launch-modules'
const PORTAL_LOGIN_URL = import.meta.env.VITE_PORTAL_LOGIN_URL || '/login'

// Function: getPortalLoginUrl
export const getPortalLoginUrl = () => PORTAL_LOGIN_URL
// Function: getPortalHomeUrl
export const getPortalHomeUrl = () => PORTAL_HOME_URL

// Function: getPortalToken
export const getPortalToken = () => sessionStorage.getItem(AUTH_TOKEN_KEY)

// Function: setPortalToken
export const setPortalToken = (token) => {
  if (!token) return
  sessionStorage.setItem(AUTH_TOKEN_KEY, token)
}

// Function: clearPortalToken
export const clearPortalToken = () => {
  sessionStorage.removeItem(AUTH_TOKEN_KEY)
}

// Function: consumePortalTokenFromHash
export const consumePortalTokenFromHash = () => {
  const hash = window.location.hash || ''
  if (!hash.startsWith('#')) return null
  const params = new URLSearchParams(hash.slice(1))
  const token = params.get('authToken') || params.get('token')
  if (!token) return null
  setPortalToken(token)
  window.history.replaceState(null, document.title, window.location.pathname + window.location.search)
  return token
}

// Function: logoutFromPortal
export const logoutFromPortal = () => {
  clearPortalToken()
  window.location.href = PORTAL_HOME_URL
}

const api = axios.create({ baseURL: API_BASE })

api.interceptors.request.use((config) => {
  const token = getPortalToken()
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

// Function: validateSession
export const validateSession = async () => {
  const { data } = await api.get('/auth/session')
  return data
}

// ── Persisted scan CRUD ──────────────────────────────────────────────────────
// Function: listScans
export const listScans = async () => {
  const { data } = await api.get('/scans')
  return data
}

// Function: getScan
export const getScan = async (scanId) => {
  const { data } = await api.get(`/scans/${scanId}`)
  return data
}

// Function: createScan
export const createScan = async (scanData) => {
  const { data } = await api.post('/scans', scanData)
  return data
}

// Function: deleteScan
export const deleteScan = async (scanId) => {
  const { data } = await api.delete(`/scans/${scanId}`)
  return data
}

// Function: deleteScanJob
export const deleteScanJob = async (scanId) => {
  const { data } = await api.delete(`/scans/jobs/${scanId}`)
  return data
}

// Function: getTemplateUrl
export const getTemplateUrl = () => `${API_BASE}/template`

// ── Scan target reachability ──────────────────────────────────────────────────
// Function: getScanTargetCandidates
export const getScanTargetCandidates = async () => {
  const { data } = await api.get('/scan-target/candidates')
  return data
}

// ── Live scan jobs ────────────────────────────────────────────────────────────
// Function: startScan
export const startScan = async (scanConfig) => {
  const { data } = await api.post('/scans/start', scanConfig)
  return data   // { scan_id, report_name, status }
}

// Function: listScanJobs
export const listScanJobs = async () => {
  const { data } = await api.get('/scans/jobs')
  return data   // { jobs: [...] }
}

// Function: getScanJob
export const getScanJob = async (scanId) => {
  const { data } = await api.get(`/scans/jobs/${scanId}`)
  return data
}

// Function: getScanReport
export const getScanReport = async (scanId) => {
  const { data } = await api.get(`/scans/jobs/${scanId}/report`)
  return data
}

// Function: getScanStreamUrl
export const getScanStreamUrl = (scanId) =>
  `${API_BASE}/scans/jobs/${scanId}/stream`

// ── LLM Intelligence ─────────────────────────────────────────────────────────

// Function: getIntelligenceStatus
export const getIntelligenceStatus = async () => {
  const { data } = await api.get('/intelligence/status')
  return data
}

// Function: runIntelligenceAnalysis
export const runIntelligenceAnalysis = async (scanId) => {
  const { data } = await api.post(`/intelligence/analyze/${scanId}`)
  return data
}

// Function: getIntelligenceAnalysis
export const getIntelligenceAnalysis = async (scanId) => {
  const { data } = await api.get(`/intelligence/analyze/${scanId}`)
  return data
}

// ── PDF OCR Infrastructure Analysis ──────────────────────────────────────────

// Function: listDataPdfs
export const listDataPdfs = async () => {
  const { data } = await api.get('/data/pdfs')
  return data
}

// Function: scanPdfs
export const scanPdfs = async () => {
  const { data } = await api.post('/scans/pdf')
  return data
}

// ── TCO & Right-sizing ────────────────────────────────────────────────────────
// Function: getTcoAnalysis
export const getTcoAnalysis = async (scanId) => {
  const { data } = await api.get(`/scans/${scanId}/tco`)
  return data
}

// ── Dependency Mapping & Wave Planning ───────────────────────────────────────
// Function: getDependencyMap
export const getDependencyMap = async (scanId) => {
  const { data } = await api.get(`/scans/${scanId}/dependencies`)
  return data
}

// ── Security & Compliance ─────────────────────────────────────────────────────
// Function: getSecurityAnalysis
export const getSecurityAnalysis = async (scanId) => {
  const { data } = await api.get(`/scans/${scanId}/security`)
  return data
}

// ── Decommissioning Candidates ────────────────────────────────────────────────
// Function: getDecommissionCandidates
export const getDecommissionCandidates = async (scanId) => {
  const { data } = await api.get(`/scans/${scanId}/decommission`)
  return data
}

// ── Hypervisor Consolidation ──────────────────────────────────────────────────
// Function: getHypervisorAnalysis
export const getHypervisorAnalysis = async (scanId) => {
  const { data } = await api.get(`/scans/${scanId}/hypervisor`)
  return data
}

// ── BCDR Gap Analysis ─────────────────────────────────────────────────────────
// Function: getBcdrAnalysis
export const getBcdrAnalysis = async (scanId) => {
  const { data } = await api.get(`/scans/${scanId}/bcdr`)
  return data
}

// ── AI Report Assistant ("chat with your report") ─────────────────────────────
// Function: sendChatMessage
export const sendChatMessage = async (scanId, message, history) => {
  const { data } = await api.post(`/scans/${scanId}/chat`, { message, history })
  return data
}

// ── Live Multi-Cloud Pricing ───────────────────────────────────────────────────
// Function: getPricingStatus
export const getPricingStatus = async () => {
  const { data } = await api.get(`/pricing/status`)
  return data
}

// Function: refreshPricing
export const refreshPricing = async () => {
  const { data } = await api.post(`/pricing/refresh`)
  return data
}

// ── Export Downloads ──────────────────────────────────────────────────────────
// Function: getExportUrl
export const getExportUrl = (scanId, format) =>
  `${API_BASE}/scans/${scanId}/export/${format}`

// Function: downloadExport
export const downloadExport = (scanId, format) => {
  const token = getPortalToken()
  const url = new URL(getExportUrl(scanId, format), window.location.origin)
  if (token) url.searchParams.set('token', token)
  window.open(url.toString(), '_blank')
}

// ── Execution Support (appliance deployment / landing zone / app DNA mapping) ─
// These workflows aren't connected to real infrastructure yet — submitting a
// request just records the requirement for when they are; nothing here
// provisions anything or simulates fake progress.
// Function: listExecutionRequests
export const listExecutionRequests = async () => {
  const { data } = await api.get(`/execution-requests`)
  return data
}

// Function: createExecutionRequest
export const createExecutionRequest = async (requestType, details) => {
  const { data } = await api.post(`/execution-requests`, { request_type: requestType, details })
  return data
}

// Function: deleteExecutionRequest
export const deleteExecutionRequest = async (requestId) => {
  const { data } = await api.delete(`/execution-requests/${requestId}`)
  return data
}

// ── Infrastructure-as-Code Template Downloads ─────────────────────────────────
// Function: downloadIac
export const downloadIac = (scanId, provider, iacFormat) => {
  const token = getPortalToken()
  const url = new URL(`${API_BASE}/scans/${scanId}/iac`, window.location.origin)
  url.searchParams.set('provider', provider)
  url.searchParams.set('format', iacFormat)
  if (token) url.searchParams.set('token', token)
  window.open(url.toString(), '_blank')
}

// Function: getPdfStreamUrl
export const getPdfStreamUrl = () =>
  `${API_BASE}/scans/pdf/stream`
