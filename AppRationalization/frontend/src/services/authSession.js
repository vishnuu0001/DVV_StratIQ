// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/services (authSession.js)
// Date: 2025-12-05
// ---------------------------------------------------------------------------
const STORAGE_KEY = 'portal_auth_session';

// Function: getAuthSession
export const getAuthSession = () => {
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw);
    if (!parsed?.token || !parsed?.user) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
};

// Function: setAuthSession
export const setAuthSession = (sessionPayload) => {
  if (!sessionPayload?.token || !sessionPayload?.user) {
    return;
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(sessionPayload));
};

// Function: clearAuthSession
export const clearAuthSession = () => {
  sessionStorage.removeItem(STORAGE_KEY);
};

// Function: getAuthToken
export const getAuthToken = () => {
  const session = getAuthSession();
  return session?.token || null;
};

// Function: getAuthUser
export const getAuthUser = () => {
  const session = getAuthSession();
  return session?.user || null;
};

// Function: hasAppPermission
export const hasAppPermission = (appKey) => {
  const user = getAuthUser();
  if (!user) {
    return false;
  }
  if (user.role === 'admin') {
    return true;
  }
  const apps = Array.isArray(user.apps) ? user.apps : [];
  return apps.includes(appKey);
};
