// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/lib (portalAuth.ts)
// Date: 2025-11-04
// ---------------------------------------------------------------------------
// Lightweight bridge to the shared StratIQ portal session.
// This module has no backend auth of its own — it only reads the shared
// portal token (for display / navigation) and never enforces access.
const AUTH_TOKEN_KEY = 'portal_auth_token'
const PORTAL_SESSION_KEY = 'portal_auth_session'

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
export const getPortalToken = (): string | null => {
  // A launch-hash token is written here immediately before module requests
  // start, so it must take precedence over an older shared session snapshot.
  const handoffToken = sessionStorage.getItem(AUTH_TOKEN_KEY)
  if (handoffToken) return handoffToken
  // The portal's canonical session is JSON stored in sessionStorage. Reading it
  // keeps module refreshes authenticated even if the one-time launch hash was
  // consumed in another tab or predates portal_auth_token.
  try {
    const session = JSON.parse(sessionStorage.getItem(PORTAL_SESSION_KEY) || 'null')
    if (typeof session?.token === 'string') return session.token
  } catch {
    // Fall through to the token copied from the module launch hash.
  }
  return null
}

// Function: setPortalToken
const setPortalToken = (token: string) => {
  sessionStorage.setItem(AUTH_TOKEN_KEY, token)
}

// Function: clearModuleToken
export const clearModuleToken = (): void => {
  sessionStorage.removeItem(AUTH_TOKEN_KEY)
}

// Function: clearPortalToken
export const clearPortalToken = (): void => {
  clearModuleToken()
  sessionStorage.removeItem(PORTAL_SESSION_KEY)
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
