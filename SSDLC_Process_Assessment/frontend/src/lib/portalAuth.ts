// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/lib (portalAuth.ts)
// Date: 2026-06-10
// ---------------------------------------------------------------------------
// Lightweight bridge to the shared StratIQ portal session.
// This module has no backend auth of its own — it only reads the shared
// portal token (for display / navigation) and never enforces access.
const AUTH_TOKEN_KEY = 'portal_auth_token'

export interface PortalUser {
  uid?: number
  username?: string
  role?: string
  apps?: string[]
  exp?: number
}

// Function: getPortalHomeUrl
export const getPortalHomeUrl = (): string =>
  (import.meta.env.VITE_PORTAL_HOME_URL as string) || '/launch-modules'

// Function: getPortalLoginUrl
export const getPortalLoginUrl = (): string =>
  (import.meta.env.VITE_PORTAL_LOGIN_URL as string) || '/login'

// Function: getPortalAdminUrl
export const getPortalAdminUrl = (): string => {
  try {
    return new URL('/admin', getPortalHomeUrl()).href
  } catch {
    return '/admin'
  }
}

// Function: getPortalToken
export const getPortalToken = (): string | null =>
  sessionStorage.getItem(AUTH_TOKEN_KEY)

// Function: setPortalToken
const setPortalToken = (token: string) => {
  sessionStorage.setItem(AUTH_TOKEN_KEY, token)
}

// Function: clearPortalToken
export const clearPortalToken = (): void => {
  sessionStorage.removeItem(AUTH_TOKEN_KEY)
}

// Function: consumePortalTokenFromHash
export const consumePortalTokenFromHash = (): void => {
  const hash = window.location.hash || ''
  if (!hash.startsWith('#')) return
  const params = new URLSearchParams(hash.slice(1))
  const token = params.get('authToken')
  if (!token) return
  setPortalToken(token)
  window.history.replaceState(null, document.title, window.location.pathname + window.location.search)
}

// Decodes the shared platform token (`v1.{base64url(payload)}.{sig}`) for
// display purposes only — no signature check, this never gates access.
// Function: decodePortalUser
export const decodePortalUser = (token: string | null): PortalUser | null => {
  if (!token) return null
  try {
    const [version, payloadB64] = token.split('.')
    if (version !== 'v1' || !payloadB64) return null
    const base64 = payloadB64.replace(/-/g, '+').replace(/_/g, '/').padEnd(
      payloadB64.length + ((4 - (payloadB64.length % 4)) % 4),
      '='
    )
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + c.charCodeAt(0).toString(16).padStart(2, '0'))
        .join('')
    )
    const payload = JSON.parse(json) as PortalUser
    if (payload.exp && payload.exp * 1000 < Date.now()) return null
    return payload
  } catch {
    return null
  }
}

// Function: logoutFromPortal
export const logoutFromPortal = (): void => {
  clearPortalToken()
  window.location.href = getPortalLoginUrl()
}
