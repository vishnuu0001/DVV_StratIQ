// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/api (client.js)
// Date: 2025-08-07
// ---------------------------------------------------------------------------
import axios from 'axios'

const AUTH_TOKEN_KEY = 'modernization_portal_auth_token'
const SHARED_AUTH_TOKEN_KEY = 'portal_auth_token'
const PORTAL_AUTH_SESSION_KEY = 'portal_auth_session'
// Dev: falls back to '/api' so vite proxy (/api → localhost:8084) still works.
// Prod: VITE_MODERNIZATION_API_URL=/api/mod → IIS rewrites /api/mod/* → localhost:8084/api/*
const API_BASE         = import.meta.env.VITE_MODERNIZATION_API_URL ||
  (import.meta.env.DEV ? '/api' : '/api/mod')
const PORTAL_HOME_URL  = import.meta.env.VITE_PORTAL_HOME_URL  || '/launch-modules'
const PORTAL_LOGIN_URL = import.meta.env.VITE_PORTAL_LOGIN_URL || '/login'

// Function: getPortalLoginUrl
export const getPortalLoginUrl = () => PORTAL_LOGIN_URL
// Function: getPortalHomeUrl
export const getPortalHomeUrl  = () => PORTAL_HOME_URL

// Function: getSharedPortalSessionToken
const getSharedPortalSessionToken = () => {
  const raw = sessionStorage.getItem(PORTAL_AUTH_SESSION_KEY)
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    return parsed?.token || null
  } catch {
    return null
  }
}

// Function: isTokenCurrent
const isTokenCurrent = (token) => {
  try {
    const parts = String(token || '').split('.')
    if (parts.length !== 3 || parts[0] !== 'v1') return false
    const encoded = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(atob(encoded.padEnd(Math.ceil(encoded.length / 4) * 4, '=')))
    return Number(payload.exp || 0) > Math.floor(Date.now() / 1000) + 15
  } catch {
    return false
  }
}

// Function: getPortalToken
export const getPortalToken = () => {
  const token = sessionStorage.getItem(AUTH_TOKEN_KEY) ||
    sessionStorage.getItem(SHARED_AUTH_TOKEN_KEY) ||
    localStorage.getItem(SHARED_AUTH_TOKEN_KEY) ||
    getSharedPortalSessionToken()
  if (!token || !isTokenCurrent(token)) {
    clearPortalToken()
    return null
  }
  return token
}

// Function: setPortalToken
export const setPortalToken = (token) => {
  if (!token) return
  sessionStorage.setItem(AUTH_TOKEN_KEY, token)
  sessionStorage.setItem(SHARED_AUTH_TOKEN_KEY, token)
}

// Function: clearPortalToken
export const clearPortalToken = () => {
  sessionStorage.removeItem(AUTH_TOKEN_KEY)
  sessionStorage.removeItem(SHARED_AUTH_TOKEN_KEY)
  localStorage.removeItem(SHARED_AUTH_TOKEN_KEY)
}

// Function: clearSharedPortalSession
const clearSharedPortalSession = () => {
  clearPortalToken()
  sessionStorage.removeItem(PORTAL_AUTH_SESSION_KEY)
}

// Function: consumePortalTokenFromHash
export const consumePortalTokenFromHash = () => {
  const hash = window.location.hash || ''
  const hashParams = hash.startsWith('#') ? new URLSearchParams(hash.slice(1)) : null
  const searchParams = new URLSearchParams(window.location.search || '')
  const token =
    hashParams?.get('authToken') ||
    hashParams?.get('token') ||
    searchParams.get('authToken') ||
    searchParams.get('token')
  if (!token) return null
  setPortalToken(token)
  window.history.replaceState(null, document.title,
    window.location.pathname + window.location.search)
  return token
}

// Function: logoutFromPortal
export const logoutFromPortal = () => {
  clearSharedPortalSession()
  window.location.href = PORTAL_HOME_URL
}

// ─── Axios instance ────────────────────────────────────────────────────────
const api = axios.create({ baseURL: API_BASE })

api.interceptors.request.use((config) => {
  const token = getPortalToken()
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

// ─── Auth ──────────────────────────────────────────────────────────────────
// Function: validateSession
export const validateSession = async () => {
  const { data } = await api.get('/auth/session')
  return data
}

// ─── Jobs ──────────────────────────────────────────────────────────────────

// Function: startAnalysis
export const startAnalysis = async (folderPath, targetStack = 'aveva_mes', customStackDesc = '', guideFiles = [], outputMode = 'project') => {
  const validGuides = (guideFiles || []).filter(item => item && item.file)
  if (validGuides.length > 0) {
    const fd = new FormData()
    fd.append('folder_path', folderPath)
    fd.append('target_stack', targetStack)
    if (customStackDesc) fd.append('custom_stack_desc', customStackDesc)
    fd.append('output_mode', outputMode)
    validGuides.forEach(({ file }) => fd.append('files', file))
    const { data } = await api.post('/modernize/analyze-with-guides', fd)
    return data
  }
  const { data } = await api.post('/modernize/analyze', {
    folder_path:       folderPath,
    target_stack:      targetStack,
    custom_stack_desc: customStackDesc || undefined,
    output_mode:       outputMode,
  })
  return data
}

// Function: startPromptAnalysis
export const startPromptAnalysis = async (prompt, files = [], targetStack = 'aveva_mes', customStackDesc = '', outputMode = 'project') => {
  const validFiles = (files || []).filter(({ file }) => file)
  if (validFiles.length === 0) {
    const body = new URLSearchParams()
    body.set('prompt', prompt)
    body.set('target_stack', targetStack)
    if (customStackDesc) body.set('custom_stack_desc', customStackDesc)
    body.set('output_mode', outputMode)
    const { data } = await api.post('/modernize/analyze-prompt', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return data
  }
  const fd = new FormData()
  fd.append('prompt', prompt)
  fd.append('target_stack', targetStack)
  if (customStackDesc) fd.append('custom_stack_desc', customStackDesc)
  fd.append('output_mode', outputMode)
  validFiles.forEach(({ file }) => fd.append('files', file))
  const { data } = await api.post('/modernize/analyze-prompt', fd)
  return data
}

// Function: getLlmStatus
export const getLlmStatus = async () => {
  const { data } = await api.get('/llm/status')
  return data
}

// Function: detectFolder
export const detectFolder = async (path) => {
  const params = new URLSearchParams({ path })
  const { data } = await api.get(`/fs/detect?${params}`)
  return data
}

// Function: listJobs
export const listJobs = async () => {
  const { data } = await api.get('/modernize/jobs')
  return data
}

// Function: getJob
export const getJob = async (jobId) => {
  const { data } = await api.get(`/modernize/jobs/${jobId}`)
  return data
}

// Function: deleteJob
export const deleteJob = async (jobId) => {
  const { data } = await api.delete(`/modernize/jobs/${jobId}`)
  return data
}

// Function: getDownloadUrl
export const getDownloadUrl = (jobId) =>
  `${API_BASE}/modernize/jobs/${jobId}/output?token=${encodeURIComponent(getPortalToken() || '')}`

// Function: getStreamUrl
export const getStreamUrl = (jobId) =>
  `${API_BASE}/modernize/jobs/${jobId}/stream?token=${encodeURIComponent(getPortalToken() || '')}`

// ─── Filesystem browser ────────────────────────────────────────────────────
// Function: getFsLs
export const getFsLs = async (path = '') => {
  const token = getPortalToken() || ''
  const params = new URLSearchParams({ token })
  if (path) params.set('path', path)
  const { data } = await api.get(`/fs/ls?${params}`)
  return data
}

// ─── Upload-from-browser folder intake ─────────────────────────────────────
// Mirrors the backend's _UPLOAD_SKIP_DIRS in api/server.py — filtered out
// client-side too so we don't waste bandwidth uploading node_modules/.git/
// build output that would just be dropped server-side anyway.
const UPLOAD_SKIP_DIRS = new Set([
  '.git', '.vs', '.vscode', 'bin', 'obj', 'node_modules',
  '__pycache__', '.venv', 'venv', 'env', 'dist', 'build',
  'target', 'out', 'packages', '.nuget', 'TestResults',
  '.gradle', '.idea', 'coverage', '.next', '.nuxt',
  '.mvn', '.svn', '.hg',
])

// `fileList` is a FileList/array from <input type="file" webkitdirectory>,
// where each File's `.webkitRelativePath` looks like "MyProject/src/Foo.cs".
// Function: filterUploadFiles
export const filterUploadFiles = (fileList) =>
  Array.from(fileList).filter((file) => {
    const parts = (file.webkitRelativePath || file.name).split('/')
    return !parts.slice(0, -1).some((seg) => UPLOAD_SKIP_DIRS.has(seg))
  })

// Function: uploadFolder
export const uploadFolder = async (files, onProgress) => {
  const fd = new FormData()
  files.forEach((file) => {
    fd.append('files', file, file.webkitRelativePath || file.name)
  })
  const { data } = await api.post('/fs/upload-folder', fd, {
    onUploadProgress: onProgress
      ? (evt) => onProgress(evt.total ? evt.loaded / evt.total : 0)
      : undefined,
  })
  return data
}

// ── Requirements documentation ────────────────────────────────────────────
export const getRequirementDocument = async (projectId, documentType) =>
  (await api.get(`/projects/${projectId}/requirements/${documentType}`)).data
export const generateRequirementDocument = async (projectId, documentType) =>
  (await api.post(`/projects/${projectId}/requirements/${documentType}/generate`, {})).data
export const getRequirementGenerationJob = async jobId =>
  (await api.get(`/requirements/jobs/${jobId}`)).data
export const downloadRequirementDocument = async (projectId, documentType) =>
  (await api.get(`/projects/${projectId}/requirements/${documentType}/export`, { responseType: 'blob' })).data
export const getGeneratedAssets = async projectId =>
  (await api.get(`/projects/${projectId}/generated-assets`)).data
export const downloadGeneratedAssets = async projectId =>
  (await api.get(`/projects/${projectId}/generated-assets/export`, { responseType: 'blob' })).data

// ── Governed projects ──────────────────────────────────────────────────────
// Function: listProjects
export const listProjects = async () => (await api.get('/projects')).data
// Function: createProject
export const createProject = async (payload) => (await api.post('/projects', payload)).data
// Function: getProject
export const getProject = async (id) => (await api.get(`/projects/${id}`)).data
// Function: deleteProject
export const deleteProject = async (id) => (await api.post(`/projects/${id}/delete`, {})).data
// Function: getProjectJobs
export const getProjectJobs = async (id, sourcePath = '') => {
  const result = await listJobs()
  return { jobs: (result.jobs || []).filter(job => job.project_id === id || (sourcePath && job.folder_path === sourcePath)) }
}
// Function: analyzeProject
export const analyzeProject = async (id, target_stack, custom_stack_desc = '') =>
  (await api.post(`/projects/${id}/analyze`, { target_stack, custom_stack_desc })).data
// Function: generateProjectPlan
export const generateProjectPlan = async (id, target_stack, custom_stack_desc = '') =>
  (await api.post(`/projects/${id}/plans`, { target_stack, custom_stack_desc })).data
// Function: getTargetStacks
export const getTargetStacks = async () => (await api.get('/modernize/target-stacks')).data
// Function: getToolchainStatus
export const getToolchainStatus = async () => (await api.get('/modernize/toolchains')).data
// Function: installToolchain
export const installToolchain = async (tool_id) => (await api.post('/modernize/toolchains/install', { tool_id })).data
// Function: getToolchainInstallStatus
export const getToolchainInstallStatus = async (jobId) => (await api.get(`/modernize/toolchains/install/${jobId}`)).data
// Function: decideProjectSnapshot
export const decideProjectSnapshot = async (id, snapshotId, decision) =>
  (await api.post(`/projects/${id}/snapshots/${snapshotId}/decision`, { decision })).data
// Function: transformProject
export const transformProject = async (id) => (await api.post(`/projects/${id}/transform`, {})).data
// Function: compareSnapshots
export const compareSnapshots = async (id, left, right) =>
  (await api.get(`/projects/${id}/compare`, { params: { left_snapshot_id: left, right_snapshot_id: right } })).data
// Function: getSnapshotArtifact
export const getSnapshotArtifact = async (id, snapshotId) =>
  (await api.get(`/projects/${id}/snapshots/${snapshotId}/artifact`)).data
// Function: reviseProjectPlan
export const reviseProjectPlan = async (id, snapshotId, payload) =>
  (await api.patch(`/projects/${id}/plans/${snapshotId}`, payload)).data
// Function: restoreProjectSnapshot
export const restoreProjectSnapshot = async (id, snapshotId) =>
  (await api.post(`/projects/${id}/snapshots/${snapshotId}/restore`, {})).data
// Function: validateProjectContracts
export const validateProjectContracts = async (id) => (await api.get(`/projects/${id}/contracts/validate`)).data
// Function: getProjectQualityGate
export const getProjectQualityGate = async (id, outputSnapshotId) =>
  (await api.get(`/projects/${id}/quality-gate`, { params: { output_snapshot_id: outputSnapshotId } })).data
// Function: approveProjectRelease
export const approveProjectRelease = async (id, outputSnapshotId, comment = '') =>
  (await api.post(`/projects/${id}/releases`, { output_snapshot_id: outputSnapshotId, comment })).data
// Function: submitProjectReview
export const submitProjectReview = async (id, outputSnapshotId, decision, feedback, fileFeedback = []) =>
  (await api.post(`/projects/${id}/reviews`, { output_snapshot_id: outputSnapshotId, decision, feedback, file_feedback: fileFeedback })).data
// Function: purgeProjectSnapshots
export const purgeProjectSnapshots = async (id) => (await api.post(`/projects/${id}/retention/purge`)).data
// Function: getComparisonExportUrl
export const getComparisonExportUrl = (id, left, right, format) =>
  `${API_BASE}/projects/${id}/compare/export?left_snapshot_id=${encodeURIComponent(left)}&right_snapshot_id=${encodeURIComponent(right)}&format=${format}&token=${encodeURIComponent(getPortalToken() || '')}`
// Function: getReleaseExportUrl
export const getReleaseExportUrl = (id, snapshotId) =>
  `${API_BASE}/projects/${id}/releases/${snapshotId}/export?token=${encodeURIComponent(getPortalToken() || '')}`
