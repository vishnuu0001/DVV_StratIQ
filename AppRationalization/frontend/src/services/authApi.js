// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/services (authApi.js)
// Date: 2026-04-30
// ---------------------------------------------------------------------------
import axios from 'axios';

import { API_BASE } from './api';
import { getAuthToken } from './authSession';

const authClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

authClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Function: loginWithPassword
export const loginWithPassword = (username, password) =>
  authClient.post('/auth/login', { username, password }).then((r) => r.data);

// Function: logoutSession
export const logoutSession = () => authClient.post('/auth/logout').then((r) => r.data);

// Function: fetchCurrentUser
export const fetchCurrentUser = () => authClient.get('/auth/me').then((r) => r.data);

// Function: fetchOauthProviders
export const fetchOauthProviders = () => authClient.get('/auth/oauth/providers').then((r) => r.data);

// Function: fetchApplications
export const fetchApplications = () => authClient.get('/auth/apps').then((r) => r.data);

// Function: createDesktopLaunch
export const createDesktopLaunch = () =>
  authClient.post('/auth/desktop-launch').then((r) => r.data);

// Function: listUsers
export const listUsers = () => authClient.get('/auth/users').then((r) => r.data);

// Function: createUser
export const createUser = (payload) => authClient.post('/auth/users', payload).then((r) => r.data);

// Function: updateUser
export const updateUser = (userId, payload) => authClient.put(`/auth/users/${userId}`, payload).then((r) => r.data);

// Function: deleteUser
export const deleteUser = (userId) => authClient.delete(`/auth/users/${userId}`).then((r) => r.data);

// Function: getGoogleAuthUrl
export const getGoogleAuthUrl = () => `${API_BASE}/auth/google/start`;

// Function: getGithubAuthUrl
export const getGithubAuthUrl = () => `${API_BASE}/auth/github/start`;
