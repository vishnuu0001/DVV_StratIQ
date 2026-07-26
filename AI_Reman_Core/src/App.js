// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Reman_Core — src (App.js)
// Date: 2025-09-01
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react';
import { Bot, Home, LogOut, ShieldCheck } from 'lucide-react';
import Dashboard from './components/Dashboard';
import './styles/App.css';

const PORTAL_TOKEN_KEY = 'stratiq_portal_auth_token';
const PORTAL_LOGIN_URL = process.env.REACT_APP_PORTAL_LOGIN_URL || '/login';
const PORTAL_HOME_URL  = process.env.REACT_APP_PORTAL_HOME_URL  || '/launch-modules';

// Minimal, non-verifying decode of the shared platform token format
// `v1.{base64url(json_payload)}.{signature}` — used ONLY to read `role`
// for UI display gating. Real enforcement happens server-side.
// Function: decodeRoleFromToken
function decodeRoleFromToken(token) {
  try {
    const segment = token.split('.')[1];
    if (!segment) return null;
    let base64 = segment.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4 !== 0) base64 += '=';
    const payload = JSON.parse(atob(base64));
    return payload?.role || null;
  } catch {
    return null;
  }
}

// Function: consumeTokenFromHash
function consumeTokenFromHash() {
  const hash = window.location.hash || '';
  const params = hash.startsWith('#') ? new URLSearchParams(hash.slice(1)) : null;
  const token = params?.get('authToken') || params?.get('token');
  if (!token) return null;
  sessionStorage.setItem(PORTAL_TOKEN_KEY, token);
  window.history.replaceState(null, document.title,
    window.location.pathname + window.location.search);
  return token;
}

// Function: getStoredToken
function getStoredToken() {
  return sessionStorage.getItem(PORTAL_TOKEN_KEY);
}

// Function: App
function App() {
  const [username, setUsername] = useState('');
  const [role, setRole] = useState(null);

  useEffect(() => {
    const hashToken = consumeTokenFromHash();
    const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);
    if (isLocal) {
      setUsername('local-admin');
      setRole('admin');
      return;
    }
    const token = hashToken || getStoredToken();
    if (!token) {
      window.location.href = PORTAL_LOGIN_URL;
    } else {
      setUsername('portal-user');
      setRole(decodeRoleFromToken(token));
    }
  }, []);

  // Function: handleLogout
  const handleLogout = () => {
    sessionStorage.removeItem(PORTAL_TOKEN_KEY);
    localStorage.removeItem(PORTAL_TOKEN_KEY);
    window.location.href = PORTAL_LOGIN_URL;
  };

  return (
    <div className="App">
      <header className="portal-nav">
        <div className="portal-nav-brand">
          <div className="portal-nav-badge">
            <Bot size={16} />
          </div>
          <div>
            <p className="portal-nav-eyebrow">Unified Modernization Suite</p>
            <p className="portal-nav-title">AI Reman Core Workspace</p>
          </div>
        </div>
        <div className="portal-nav-actions">
          {username && (
            <span className="portal-nav-user">Signed in as {username}</span>
          )}
          <button
            type="button"
            className="portal-nav-btn"
            onClick={() => { window.location.href = PORTAL_HOME_URL; }}
          >
            <Home size={14} />
            Homepage
          </button>
          {role === 'admin' && (
            <button
              type="button"
              className="portal-nav-btn"
              onClick={() => {
                let adminUrl = '/admin';
                try {
                  adminUrl = new URL('/admin', PORTAL_HOME_URL).href;
                } catch {
                  adminUrl = '/admin';
                }
                window.location.href = adminUrl;
              }}
            >
              <ShieldCheck size={14} />
              Admin Console
            </button>
          )}
          <button
            type="button"
            className="portal-nav-btn portal-nav-btn--danger"
            onClick={handleLogout}
          >
            <LogOut size={14} />
            Logout
          </button>
        </div>
      </header>
      <Dashboard />
    </div>
  );
}

export default App;
