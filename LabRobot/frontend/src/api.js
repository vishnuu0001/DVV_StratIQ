// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src (api.js)
// Date: 2025-07-23
// ---------------------------------------------------------------------------
import axios from 'axios'

const AUTH_TOKEN_KEY = 'portal_auth_token'

// A 401 here means sessionStorage has no token (opened /lab/ directly
// instead of via the portal launcher) or the token expired — the backend
// is correctly rejecting the request, not failing. Previously every caller
// just did `.catch(console.error)`, so this surfaced as a silent blank
// panel with only a browser-console error to explain it. Emitting a DOM
// event here (same pattern pickupMessaging.js already uses) lets App.jsx
// show one clear "sign in again" banner instead, without every call site
// needing its own 401 handling.
export const AUTH_EXPIRED_EVENT = 'labAuthExpired'

// Function: isTokenCurrent
// `bufferSeconds` lets callers ask "usable right now" (small buffer,
// default) vs. "due for a proactive refresh soon" (a larger one).
const isTokenCurrent = (token, bufferSeconds = 15) => {
  try {
    const parts = String(token || '').split('.')
    if (parts.length !== 3 || parts[0] !== 'v1') return false
    const encoded = parts[1].replaceAll('-', '+').replaceAll('_', '/')
    const payload = JSON.parse(atob(encoded.padEnd(Math.ceil(encoded.length / 4) * 4, '=')))
    return Number(payload.exp || 0) > Math.floor(Date.now() / 1000) + bufferSeconds
  } catch {
    return false
  }
}

// Function: getRawPortalToken
// Whatever token is on hand regardless of expiry — needed by the refresh
// flow, which has to send an *expired* token to the server to renew it.
const getRawPortalToken = () => {
  const token = sessionStorage.getItem(AUTH_TOKEN_KEY)
  if (!token) return null
  const parts = token.split('.')
  return parts.length === 3 && parts[0] === 'v1' ? token : null
}

// Function: getPortalToken
// A token usable right now, or null — never mutates storage. Expiry alone
// isn't grounds to wipe the session; it might still be renewable (see
// refreshPortalToken below).
const getPortalToken = () => {
  const token = getRawPortalToken()
  return token && isTokenCurrent(token) ? token : null
}

// Function: setPortalToken
const setPortalToken = (token) => {
  if (!token) return
  sessionStorage.setItem(AUTH_TOKEN_KEY, token)
}

// Function: refreshPortalToken
// Exchanges whatever raw token is stored for a fresh one via
// POST /api/auth/refresh — the backend accepts a signature-valid token even
// past its `exp` (within a grace window), so a session that expired while
// this tab sat open can renew itself instead of throwing up the "sign in
// again" banner. Concurrent callers share one in-flight request.
let _refreshPromise = null
const refreshPortalToken = () => {
  if (_refreshPromise) return _refreshPromise
  const raw = getRawPortalToken()
  if (!raw) return Promise.resolve(null)
  const base = import.meta.env.VITE_LAB_API_URL || (import.meta.env.DEV ? '/api' : '/api/lab')
  _refreshPromise = axios
    .post(`${base}/auth/refresh`, {}, { headers: { Authorization: `Bearer ${raw}` } })
    .then(({ data }) => {
      if (data?.token) {
        setPortalToken(data.token)
        return data.token
      }
      return null
    })
    .catch(() => null)
    .finally(() => {
      _refreshPromise = null
    })
  return _refreshPromise
}

// Function: getValidPortalToken
// Self-healing async token getter: the current token if it's usable,
// otherwise a refresh attempt before giving up.
const getValidPortalToken = async () => {
  const current = getPortalToken()
  if (current) return current
  return refreshPortalToken()
}

// Consumes the SSO handoff token the central portal appends to the URL when
// launching this module, same handoff shape used by every other module
// (see CodeAnalysis/frontend/src/api/client.js's consumePortalTokenFromHash).
const hashParams = window.location.hash.startsWith('#')
  ? new URLSearchParams(window.location.hash.slice(1))
  : null
const searchParams = new URLSearchParams(window.location.search || '')
const handoffToken =
  hashParams?.get('authToken') || hashParams?.get('token') ||
  searchParams.get('authToken') || searchParams.get('token')
if (handoffToken) {
  setPortalToken(handoffToken)
  window.history.replaceState(null, document.title, window.location.pathname + window.location.search)
}

const api = axios.create({
  baseURL: import.meta.env.VITE_LAB_API_URL ||
    (import.meta.env.DEV ? '/api' : '/api/lab'),
})

api.interceptors.request.use(async (config) => {
  const token = await getValidPortalToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On a 401, try one refresh-and-retry before giving up and showing the
// "sign in again" banner — this is what used to fire that banner the
// instant a token's local exp passed, even though the session might still
// be renewable server-side (see refreshPortalToken above).
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error?.config
    if (error?.response?.status === 401 && original && !original._retriedAfterRefresh) {
      original._retriedAfterRefresh = true
      const token = await refreshPortalToken()
      if (token) {
        original.headers = { ...original.headers, Authorization: `Bearer ${token}` }
        return api(original)
      }
    }
    if (error?.response?.status === 401) {
      document.dispatchEvent(new CustomEvent(AUTH_EXPIRED_EVENT))
    }
    throw error
  }
)

// Proactive refresh: keep an open tab's token from ever actually reaching
// expiry, rather than relying solely on the reactive path above. Checks
// every minute; only acts when the current token is within 5 minutes of
// expiring.
const PROACTIVE_REFRESH_WINDOW_SECONDS = 5 * 60
setInterval(() => {
  const raw = getRawPortalToken()
  if (raw && isTokenCurrent(raw) && !isTokenCurrent(raw, PROACTIVE_REFRESH_WINDOW_SECONDS)) {
    refreshPortalToken()
  }
}, 60_000)

// Function: getScientists
export const getScientists = () =>
  api.get('/scientists')

// Function: getAllChemicals
export const getAllChemicals = () =>
  api.get('/chemicals')

// Function: searchChemical
export const searchChemical = (barcode) =>
  api.get('/chemicals/search', { params: { barcode } })

// Function: placeChemical
export const placeChemical = (data) =>
  api.post('/placements', data)

// Function: getPlacements
export const getPlacements = (scientistId) =>
  api.get('/placements', scientistId ? { params: { scientist_id: scientistId } } : {})

// Function: fetchChemical
export const fetchChemical = (placementId) =>
  api.put(`/placements/${placementId}/fetch`)

// Function: resetAllPlacements
export const resetAllPlacements = () =>
  api.delete('/placements/all')

// Function: generateVeoSample
// The one real call in the AI Lab catalog demo (see AILabCatalog.jsx's
// header notice) — everything else there is a fixed, simulated outcome.
export const generateVeoSample = (useCase) =>
  api.post('/ai-lab/veo/sample', { use_case: useCase })

// Function: chatWithVeo
// Multi-turn version of the above — `messages` is the full running
// transcript ([{ role: 'user' | 'model', text }]); the endpoint is
// stateless, so the frontend resends history each turn.
export const chatWithVeo = (messages) =>
  api.post('/ai-lab/veo/chat', { messages })
