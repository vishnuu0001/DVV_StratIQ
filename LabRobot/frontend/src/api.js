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

// Function: getPortalToken
const getPortalToken = () =>
  sessionStorage.getItem(AUTH_TOKEN_KEY)

// Function: setPortalToken
const setPortalToken = (token) => {
  if (!token) return
  sessionStorage.setItem(AUTH_TOKEN_KEY, token)
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

api.interceptors.request.use((config) => {
  const token = getPortalToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      document.dispatchEvent(new CustomEvent(AUTH_EXPIRED_EVENT))
    }
    return Promise.reject(error)
  }
)

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
