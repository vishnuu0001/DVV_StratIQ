// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/contexts (AuthContext.jsx)
// Date: 2025-12-27
// ---------------------------------------------------------------------------
import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import api, { setAuthToken } from '../services/api.js'

const AUTH_KEY = 'novastra_itsm_auth'
const PORTAL_TOKEN_KEY = 'portal_auth_token'
const PORTAL_SSO_MARKER_KEY = 'novastra_portal_sso_in_progress'
const AuthContext = createContext(null)
// Capture the handoff once at module load. React StrictMode can remount this
// provider after the first effect has removed the hash from the address bar;
// reading window.location.hash again on that remount would lose the token and
// briefly restore a stale local session.
// Function: incomingPortalToken
const incomingPortalToken = (() => {
  try {
    const hash = window.location.hash || ''
    if (!hash.startsWith('#')) return null
    return new URLSearchParams(hash.slice(1)).get('authToken')
  } catch {
    return null
  }
})()
if (incomingPortalToken) {
  sessionStorage.setItem(PORTAL_SSO_MARKER_KEY, 'true')
} else {
  sessionStorage.removeItem(PORTAL_SSO_MARKER_KEY)
}
const allowLocalAuthBypass =
  import.meta.env.VITE_ALLOW_LOCAL_AUTH_BYPASS !== 'false' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')

const localDevUser = {
  id: 'local-admin',
  username: 'admin',
  display_name: 'admin',
  role: 'admin',
}

// Function: AuthProvider
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    if (incomingPortalToken) return null
    try {
      const stored = localStorage.getItem(AUTH_KEY)
      return stored ? JSON.parse(stored).user : allowLocalAuthBypass ? localDevUser : null
    } catch { return null }
  })
  const [token, setToken] = useState(() => {
    if (incomingPortalToken) return null
    try {
      const stored = localStorage.getItem(AUTH_KEY)
      return stored ? JSON.parse(stored).token : null
    } catch { return null }
  })
  const [loading, setLoading] = useState(false)
  // True from the very first render whenever the URL still carries a
  // #authToken= hash from the portal launcher. Computed synchronously (not
  // inside an effect) so ProtectedRoute's very first render already knows
  // to wait rather than redirect to /login — React fires a child's effects
  // (ProtectedRoute's implicit Navigate) before its parent's (this
  // provider's hash-consuming effect below), so by the time this effect
  // would otherwise get to read window.location.hash, ProtectedRoute may
  // have already replaced the URL with a hash-free "/login" and the SSO
  // exchange below would silently no-op.
  const [checkingSso, setCheckingSso] = useState(!!incomingPortalToken)

  // Keep token in localStorage and on axios default headers
  useEffect(() => {
    setAuthToken(token)
  }, [token])

  // Function: _persist
  const _persist = (t, u) => {
    setAuthToken(t)
    setToken(t)
    setUser(u)
    if (t) {
      localStorage.setItem(AUTH_KEY, JSON.stringify({ token: t, user: u }))
      // Shared portal token: sessionStorage only (not also localStorage) —
      // this module's own AUTH_KEY above is a deliberate "stay logged in
      // across restarts" record for Novastra-ITSM itself, but the shared
      // portal_auth_token doesn't need that same persistence, and writing
      // it to both storages just widens the XSS blast radius for no gain.
      sessionStorage.setItem(PORTAL_TOKEN_KEY, t)
    } else {
      localStorage.removeItem(AUTH_KEY)
      sessionStorage.removeItem(PORTAL_TOKEN_KEY)
      if (allowLocalAuthBypass) {
        setUser(localDevUser)
      }
    }
  }

  // Portal SSO: consume #authToken from URL hash on first load
  useEffect(() => {
    if (!incomingPortalToken) { setCheckingSso(false); return }
    // Clear hash from URL immediately
    window.history.replaceState(null, document.title, window.location.pathname + window.location.search)
    setLoading(true)
    api.post(
      '/auth/portal-sso',
      { portal_token: incomingPortalToken },
      { skipAuthRedirect: true },
    )
      .then(({ data }) => { _persist(data.access_token, data.user) })
      .catch(() => { _persist(null, null) })
      .finally(() => {
        sessionStorage.removeItem(PORTAL_SSO_MARKER_KEY)
        setLoading(false)
        setCheckingSso(false)
      })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const login = useCallback(async (username, password) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { username, password })
      _persist(data.access_token, data.user)
      return { ok: true }
    } catch (err) {
      return { ok: false, error: err.response?.data?.detail || 'Login failed' }
    } finally {
      setLoading(false)
    }
  }, [])

  const loginWithToken = useCallback(async (t) => {
    // Called after OAuth redirect — decode user from the returned token
    try {
      setAuthToken(t)
      const { data } = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${t}` },
      })
      _persist(t, data)
    } catch {
      _persist(null, null)
    }
  }, [])

  const logout = useCallback(() => {
    _persist(null, null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        checkingSso,
        login,
        loginWithToken,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// Function: useAuth
export const useAuth = () => useContext(AuthContext)
