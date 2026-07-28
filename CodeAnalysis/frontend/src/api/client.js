// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis â€” frontend/src/api (client.js)
// Date: 2025-11-12
// ---------------------------------------------------------------------------
import axios from 'axios'

const AUTH_TOKEN_KEY = 'portal_auth_token'
const CODE_ANALYSIS_API_BASE =
  import.meta.env.VITE_CODE_ANALYSIS_API_URL ||
  (import.meta.env.DEV ? '' : '/api/codeanalysis')
const PORTAL_API_BASE = import.meta.env.VITE_PORTAL_API_URL || '/api'
const PORTAL_LOGIN_URL = import.meta.env.VITE_PORTAL_LOGIN_URL || '/login'
const PORTAL_HOME_URL = import.meta.env.VITE_PORTAL_HOME_URL || '/launch-modules'

// Function: getPortalLoginUrl
export const getPortalLoginUrl = () => PORTAL_LOGIN_URL
// Function: getPortalHomeUrl
export const getPortalHomeUrl = () => PORTAL_HOME_URL

// Function: getPortalToken
export const getPortalToken = () =>
  sessionStorage.getItem(AUTH_TOKEN_KEY)

// Function: setPortalToken
export const setPortalToken = (token) => {
  if (!token) {
    return
  }
  sessionStorage.setItem(AUTH_TOKEN_KEY, token)
}

// Function: clearPortalToken
export const clearPortalToken = () => {
  sessionStorage.removeItem(AUTH_TOKEN_KEY)
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
  if (!token) {
    return null
  }

  setPortalToken(token)
  window.history.replaceState(null, document.title, window.location.pathname + window.location.search)
  return token
}

// Function: logoutFromPortal
export const logoutFromPortal = async () => {
  const token = getPortalToken()
  if (token) {
    try {
      await axios.post(
        `${PORTAL_API_BASE}/auth/logout`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
    } catch {
      // Local token cleanup still runs below.
    }
  }
  clearPortalToken()
}

const api = axios.create({ baseURL: CODE_ANALYSIS_API_BASE })

api.interceptors.request.use((config) => {
  const token = getPortalToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Function: startAnalysis
export const startAnalysis = (payload) =>
  api.post(`${CODE_ANALYSIS_API_BASE ? '/analyse' : '/api/analyse'}`, payload).then((r) => r.data)

/**
 * Upload a zipped local folder for analysis â€” the actual way to analyse code
 * that only exists on the caller's own device (a server-side path string can
 * never reach it). onUploadProgress receives an integer 0-100.
 */
// Function: startAnalysisUpload
export const startAnalysisUpload = (zipBlob, { users = 100, revenue = 0 } = {}, onUploadProgress) => {
  const form = new FormData()
  form.append('file', zipBlob, 'upload.zip')
  form.append('users', String(users))
  form.append('revenue', String(revenue))
  return api
    .post(`${CODE_ANALYSIS_API_BASE ? '/analyse/upload' : '/api/analyse/upload'}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onUploadProgress
        ? (evt) => onUploadProgress(evt.total ? Math.round((evt.loaded / evt.total) * 100) : 0)
        : undefined,
    })
    .then((r) => r.data)
}

// Function: startPortfolio
export const startPortfolio = (payload) =>
  api.post(`${CODE_ANALYSIS_API_BASE ? '/portfolio' : '/api/portfolio'}`, payload).then((r) => r.data)

// Function: getJob
export const getJob = (jobId) =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '' : '/api'}/jobs/${jobId}`).then((r) => r.data)

// Function: listReports
export const listReports = () =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/reports' : '/api/reports'}`).then((r) => r.data)

// Function: getReport
export const getReport = (filename) =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/reports' : '/api/reports'}/${filename}`).then((r) => r.data)

// Function: checkHealth
export const checkHealth = () =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/health' : '/api/health'}`).then((r) => r.data)

// Function: validateSession
export const validateSession = () =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/auth/session' : '/api/auth/session'}`).then((r) => r.data)

// Function: getAiHealth
export const getAiHealth = () =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/ai/health' : '/api/ai/health'}`).then((r) => r.data)

// Function: listStratAqorynthModules
export const listStratAqorynthModules = (jobId) =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/modules' : '/api/modules'}`, { params: jobId ? { job_id: jobId } : undefined }).then((r) => r.data)

// Function: getAiJob
export const getAiJob = (jobId) =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/ai/jobs' : '/api/ai/jobs'}/${jobId}`).then((r) => r.data)

// Function: startAiAnalysis
export const startAiAnalysis = (payload) =>
  api.post(`${CODE_ANALYSIS_API_BASE ? '/ai/analyse' : '/api/ai/analyse'}`, payload).then((r) => r.data)

// Function: pullAiModel
export const pullAiModel = (modelId) =>
  api.post(`${CODE_ANALYSIS_API_BASE ? '/ai/pull-model' : '/api/ai/pull-model'}`, { model_id: modelId }).then((r) => r.data)

// Function: getKnowledgeGraph
export const getKnowledgeGraph = (jobId, maxFiles = 400) =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/ai/knowledge-graph' : '/api/ai/knowledge-graph'}`, {
    params: {
      job_id: jobId,
      max_files: maxFiles,
    },
  }).then((r) => r.data)

// Function: startStratAqorynthAnalysis
export const startStratAqorynthAnalysis = (modules) =>
  api.post(`${CODE_ANALYSIS_API_BASE ? '/strat-aqorynth/analyse' : '/api/strat-aqorynth/analyse'}`, { modules }).then((r) => r.data)

// Function: getStratAqorynthJob
export const getStratAqorynthJob = (jobId) =>
  api.get(`${CODE_ANALYSIS_API_BASE ? '/strat-aqorynth/jobs' : '/api/strat-aqorynth/jobs'}/${jobId}`).then((r) => r.data)

// Function: pollStratAqorynthJob
export const pollStratAqorynthJob = (jobId, onProgress) => {
  let cancelled = false
  let interval = null

  const promise = new Promise((resolve, reject) => {
    interval = setInterval(async () => {
      if (cancelled) { clearInterval(interval); return }
      try {
        const job = await getStratAqorynthJob(jobId)
        onProgress?.(job)
        if (job.status === 'done') {
          clearInterval(interval)
          resolve(job)
        } else if (job.status === 'error') {
          clearInterval(interval)
          reject(new Error(job.message || 'Strat-Aqorynth analysis failed'))
        }
      } catch (err) {
        clearInterval(interval)
        reject(err)
      }
    }, 1800)
  })

  // Function: cancel
  const cancel = () => { cancelled = true; clearInterval(interval) }
  return { promise, cancel }
}

/**
 * Stream Strat-Aqorynth job progress via Server-Sent Events (SSE).
 * Uses fetch() so the Authorization header is forwarded â€” EventSource does not
 * support custom headers.  Falls back to polling if SSE is unavailable.
 * Returns { promise, cancel } matching the pollStratAqorynthJob interface.
 */
// Returns { terminal: true } if a terminal status line was found and settled
// the promise, else { terminal: false } to keep reading the stream.
// Function: consumeSSELines
function consumeSSELines(lines, onProgress, resolve, reject) {
  for (const line of lines) {
    if (!line.startsWith('data: ')) continue
    try {
      const job = JSON.parse(line.slice(6))
      onProgress?.(job)
      if (job.status === 'done') { resolve(job); return { terminal: true } }
      if (job.status === 'error') {
        reject(new Error(job.message || 'Strat-Aqorynth analysis failed'))
        return { terminal: true }
      }
    } catch { /* ignore malformed SSE lines */ }
  }
  return { terminal: false }
}

// Function: readSSEStream
async function readSSEStream(resp, jobId, onProgress, resolve, reject, isCancelled) {
  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''

  while (!isCancelled()) {
    const { value, done } = await reader.read()
    if (done) break

    buf += decoder.decode(value, { stream: true })
    const lines = buf.split('\n')
    buf = lines.pop() ?? ''

    const { terminal } = consumeSSELines(lines, onProgress, resolve, reject)
    if (terminal) return
  }

  // Stream closed before terminal status â€” do one final poll.
  if (isCancelled()) return
  try {
    const job = await getStratAqorynthJob(jobId)
    onProgress?.(job)
    if (job.status === 'done') resolve(job)
    else if (job.status === 'error') reject(new Error(job.message || 'Failed'))
    else reject(new Error('Stream ended unexpectedly'))
  } catch (err) { reject(err) }
}

// Function: streamStratAqorynthJob
export const streamStratAqorynthJob = (jobId, onProgress) => {
  let cancelled = false
  let abortController = null
  let fallbackCancel = null

  const promise = new Promise((resolve, reject) => {
    const token = getPortalToken()
    const headers = { Accept: 'text/event-stream' }
    if (token) headers['Authorization'] = `Bearer ${token}`

    abortController = new AbortController()
    const base = CODE_ANALYSIS_API_BASE || '/api'
    const url = `${base}/strat-aqorynth/jobs/${jobId}/stream`

    fetch(url, { headers, signal: abortController.signal })
      .then(async (resp) => {
        if (!resp.ok) throw new Error(`SSE ${resp.status}`)
        await readSSEStream(resp, jobId, onProgress, resolve, reject, () => cancelled)
      })
      .catch((err) => {
        if (cancelled) return
        // SSE unavailable â€” fall back to 1 s polling.
        const { promise: pp, cancel: pc } = pollStratAqorynthJob(jobId, onProgress)
        fallbackCancel = pc
        pp.then(resolve).catch(reject)
      })
  })

  // Function: cancel
  const cancel = () => {
    cancelled = true
    abortController?.abort()
    fallbackCancel?.()
  }

  return { promise, cancel }
}

/**
 * Poll a job until status is 'done' or 'error'.
 * Returns { promise, cancel } so the caller can abort an in-flight poll.
 */
// Function: pollJob
export const pollJob = (jobId, onProgress) => {
  let cancelled = false
  let interval = null

  const promise = new Promise((resolve, reject) => {
    let notFoundStreak = 0
    interval = setInterval(async () => {
      if (cancelled) { clearInterval(interval); return }
      try {
        const job = await getJob(jobId)
        notFoundStreak = 0
        onProgress?.(job)
        if (job.status === 'done') {
          clearInterval(interval)
          resolve(job)
        } else if (job.status === 'error') {
          clearInterval(interval)
          reject(new Error(job.message || 'Analysis failed'))
        }
      } catch (err) {
        // Tolerate up to 5 consecutive 404s (server may be mid-reload)
        if (err?.response?.status === 404) {
          notFoundStreak++
          if (notFoundStreak >= 5) {
            clearInterval(interval)
            reject(new Error('Job not found - the server may have restarted. Please try again.'))
          }
        } else {
          clearInterval(interval)
          reject(err)
        }
      }
    }, 1500)
  })

  // Function: cancel
  const cancel = () => { cancelled = true; clearInterval(interval) }
  return { promise, cancel }
}


