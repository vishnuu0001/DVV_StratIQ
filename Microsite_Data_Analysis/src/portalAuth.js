// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Microsite_Data_Analysis — src (portalAuth.js)
// Date: 2025-10-29
// ---------------------------------------------------------------------------
// Lightweight bridge to the shared StratIQ portal session.
// This module has no backend auth of its own — it only reads the shared
// portal token (for display / navigation) and never enforces access.
const AUTH_TOKEN_KEY = 'portal_auth_token';

// Function: getPortalHomeUrl
export const getPortalHomeUrl = () => import.meta.env.VITE_PORTAL_HOME_URL || '/launch-modules';
// Function: getPortalLoginUrl
export const getPortalLoginUrl = () => import.meta.env.VITE_PORTAL_LOGIN_URL || '/login';
// Function: getPortalAdminUrl
export const getPortalAdminUrl = () => {
  try {
    return new URL('/admin', getPortalHomeUrl()).href;
  } catch {
    return '/admin';
  }
};

// Function: getPortalToken
export const getPortalToken = () =>
  sessionStorage.getItem(AUTH_TOKEN_KEY) || localStorage.getItem(AUTH_TOKEN_KEY);

// Function: setPortalToken
const setPortalToken = (token) => {
  if (!token) return;
  sessionStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(AUTH_TOKEN_KEY, token);
};

// Function: clearPortalToken
export const clearPortalToken = () => {
  sessionStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_TOKEN_KEY);
};

// Function: consumePortalTokenFromHash
export const consumePortalTokenFromHash = () => {
  const hash = window.location.hash || '';
  const hashParams = hash.startsWith('#') ? new URLSearchParams(hash.slice(1)) : null;
  const token = hashParams?.get('authToken');
  if (!token) return;
  setPortalToken(token);
  window.history.replaceState(null, document.title, window.location.pathname + window.location.search);
};

// Decodes the shared platform token (`v1.{base64url(payload)}.{sig}`) for
// display purposes only — no signature check, this never gates access.
// Function: decodePortalUser
export const decodePortalUser = (token) => {
  if (!token) return null;
  try {
    const [version, payloadB64] = token.split('.');
    if (version !== 'v1' || !payloadB64) return null;
    const base64 = payloadB64.replace(/-/g, '+').replace(/_/g, '/').padEnd(
      payloadB64.length + ((4 - (payloadB64.length % 4)) % 4),
      '='
    );
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + c.charCodeAt(0).toString(16).padStart(2, '0'))
        .join('')
    );
    const payload = JSON.parse(json);
    if (payload.exp && payload.exp * 1000 < Date.now()) return null;
    return payload;
  } catch {
    return null;
  }
};

// Function: logoutFromPortal
export const logoutFromPortal = () => {
  clearPortalToken();
  window.location.href = getPortalLoginUrl();
};
