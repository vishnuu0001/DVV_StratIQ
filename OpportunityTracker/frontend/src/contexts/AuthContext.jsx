// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/contexts (AuthContext.jsx)
// Date: 2025-12-30
// ---------------------------------------------------------------------------
import React, { createContext, useContext, useEffect, useState } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

const STORAGE_KEY = 'ot_auth';
const PORTAL_SESSION_KEY = 'portal_auth_session';

// Function: decodePortalIdentity
function decodePortalIdentity(token) {
  try {
    const body = token.split('.')[1];
    if (!body) return {};
    const normalized = body.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), '=');
    const payload = JSON.parse(atob(padded));
    return {
      username: payload.username || 'portal-user',
      role: payload.role || 'user',
    };
  } catch {
    return { username: 'portal-user', role: 'user' };
  }
}

// Function: consumePortalHandoff
function consumePortalHandoff() {
  const hash = window.location.hash || '';
  if (!hash.startsWith('#')) return null;
  const token = new URLSearchParams(hash.slice(1)).get('authToken');
  if (!token) return null;
  window.history.replaceState(
    null,
    document.title,
    window.location.pathname + window.location.search,
  );
  return token;
}

// Function: getPortalSessionToken
function getPortalSessionToken() {
  try {
    return JSON.parse(sessionStorage.getItem(PORTAL_SESSION_KEY) || 'null')?.token || null;
  } catch {
    return null;
  }
}

// Function: AuthProvider
export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const portalToken = consumePortalHandoff() || getPortalSessionToken();
    try {
      const stored = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || 'null');
      const selected = portalToken
        ? { token: portalToken, ...decodePortalIdentity(portalToken) }
        : stored;
      if (selected?.token) {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(selected));
        setToken(selected.token);
        setUser({ username: selected.username, role: selected.role });
        api.defaults.headers.common['Authorization'] = `Bearer ${selected.token}`;
      }
    } catch { /* ignore */ }
    setLoading(false);
  }, []);

  // Function: login
  const login = async (username, password) => {
    const { data } = await api.post('auth/login', { username, password });
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    api.defaults.headers.common['Authorization'] = `Bearer ${data.token}`;
    setToken(data.token);
    setUser({ username: data.username, role: data.role });
    return data;
  };

  // Function: logout
  const logout = () => {
    setToken(null);
    setUser(null);
    delete api.defaults.headers.common['Authorization'];
    sessionStorage.removeItem(STORAGE_KEY);
  };

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Function: useAuth
export const useAuth = () => useContext(AuthContext);
