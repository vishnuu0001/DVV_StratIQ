// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/api (client.ts)
// Date: 2025-08-08
// ---------------------------------------------------------------------------
import axios from 'axios'
import { clearModuleToken, getPortalLoginUrl, getPortalToken } from '../lib/portalAuth'

// Dev: vite proxies /api/tf -> localhost:8095 (see vite.config.ts).
// Prod: IIS rewrites /api/tf/* -> localhost:8095/api/* (see root web.config,
// same proven pattern as Novastra-ITSM's /api/novastra-itsm/* rule).
const API_BASE = import.meta.env.VITE_TF_API_URL || '/api/tf'

export const api = axios.create({ baseURL: `${API_BASE}/v1` })

// Function: attachToken
function attachToken() {
  const token = getPortalToken()
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}
attachToken()
window.addEventListener('storage', attachToken)

// The portal passes a fresh token in the URL hash. Module initialization can
// occur before that hash is consumed, so defaults alone may retain an older,
// expired token. Resolve storage immediately before every request instead.
api.interceptors.request.use((config) => {
  const token = getPortalToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  } else {
    delete config.headers.Authorization
  }
  return config
})

let redirectingToLogin = false

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401 && !redirectingToLogin) {
      redirectingToLogin = true
      // A module backend configuration fault must not destroy the suite-wide
      // portal session. The portal remains responsible for validating and
      // clearing its canonical session on the login route.
      clearModuleToken()
      window.location.replace(getPortalLoginUrl())
    }
    return Promise.reject(error)
  },
)

export default api
