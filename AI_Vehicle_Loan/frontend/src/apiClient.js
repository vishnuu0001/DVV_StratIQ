// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src (apiClient.js)
// Date: 2026-07-21
// ---------------------------------------------------------------------------
import axios from 'axios';

const AUTH_TOKEN_KEY = 'portal_auth_token';

// Function: getPortalToken
const getPortalToken = () =>
  sessionStorage.getItem(AUTH_TOKEN_KEY);

// Function: setPortalToken
const setPortalToken = (token) => {
  if (!token) return;
  sessionStorage.setItem(AUTH_TOKEN_KEY, token);
};

// Consumes the `#authToken=` handoff the central portal's LaunchModulesPage
// appends when launching this module (see withAuthHash in
// AppRationalization/frontend/src/pages/LaunchModulesPage.jsx).
const hash = window.location.hash || '';
const hashParams = hash.startsWith('#') ? new URLSearchParams(hash.slice(1)) : null;
const searchParams = new URLSearchParams(window.location.search || '');
const handoffToken =
  hashParams?.get('authToken') || hashParams?.get('token') ||
  searchParams.get('authToken') || searchParams.get('token');
if (handoffToken) {
  setPortalToken(handoffToken);
  window.history.replaceState(null, document.title, window.location.pathname + window.location.search);
}

const apiClient = axios.create();

apiClient.interceptors.request.use((config) => {
  const token = getPortalToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
