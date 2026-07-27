// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/pages (AdminUsersPage.jsx)
// Date: 2026-02-07
// ---------------------------------------------------------------------------
import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, LayoutGrid, LogOut, ShieldCheck, Trash2, UserPlus, Users } from 'lucide-react';

import { useAuth } from '../context/AuthContext';
import { createUser, deleteUser, fetchApplications, listUsers, updateUser } from '../services/authApi';

const emptyCreateState = {
  username: '',
  password: '',
  role: 'user',
  apps: ['APP_RATIONALIZATION'],
};

// Function: normalizeApps
const normalizeApps = (apps) => {
  if (!Array.isArray(apps)) {
    return [];
  }
  return [...new Set(apps)];
};

// Function: AdminUsersPage
const AdminUsersPage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [applications, setApplications] = useState([]);
  const [users, setUsers] = useState([]);
  const [drafts, setDrafts] = useState({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [createState, setCreateState] = useState(emptyCreateState);

  const appOptions = useMemo(() => {
    if (applications.length > 0) {
      return applications;
    }
    return [
      { key: 'APP_RATIONALIZATION', name: 'App Rationalization' },
      { key: 'CODE_ANALYSIS', name: 'Code Analysis' },
      { key: 'INFRA_SCAN', name: 'Infra Rationalization' },
      { key: 'MODERNIZATION', name: 'Modernization Studio' },
      { key: 'NOVASTRA_ITSM', name: 'Novastra-ITSM' },
      { key: 'DASHBOARD', name: 'Dashboard' },
      { key: 'SSDLC_PROCESS_ASSESSMENT', name: 'SSDLC Process Assessment' },
      { key: 'LAB_ROBOT', name: 'Lab Robot' },
      { key: 'OPPORTUNITY_TRACKER', name: 'Opportunity Tracker' },
      { key: 'AI_REMAN_CORE', name: 'AI Reman Core' },
      { key: 'AI_VEHICLE_LOAN', name: 'AI Vehicle Loan' },
      { key: 'MICROSITE_DATA_ANALYSIS', name: 'Data Analysis Studio' },
      { key: 'SUPPLY_CHAIN_DISRUPTION_MANAGER', name: 'Supply Chain Disruption Manager' },
    ];
  }, [applications]);

  const activeUsers = users.filter((entry) => entry.is_active).length;
  const adminUsers = users.filter((entry) => entry.role === 'admin').length;

  // Function: loadData
  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [appsResponse, usersResponse] = await Promise.all([fetchApplications(), listUsers()]);
      const apps = appsResponse?.applications || [];
      const userRows = usersResponse?.users || [];
      setApplications(apps);
      setUsers(userRows);
      const nextDrafts = {};
      userRows.forEach((u) => {
        nextDrafts[u.id] = {
          role: u.role,
          is_active: Boolean(u.is_active),
          apps: normalizeApps(u.apps),
          password: '',
        };
      });
      setDrafts(nextDrafts);
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Function: updateDraft
  const updateDraft = (userId, patch) => {
    setDrafts((prev) => ({
      ...prev,
      [userId]: {
        ...(prev[userId] || {}),
        ...patch,
      },
    }));
  };

  // Function: toggleDraftApp
  const toggleDraftApp = (userId, appKey) => {
    const current = normalizeApps(drafts[userId]?.apps || []);
    const has = current.includes(appKey);
    const next = has ? current.filter((a) => a !== appKey) : [...current, appKey];
    updateDraft(userId, { apps: next });
  };

  // Function: toggleCreateApp
  const toggleCreateApp = (appKey) => {
    const current = normalizeApps(createState.apps);
    const has = current.includes(appKey);
    const next = has ? current.filter((a) => a !== appKey) : [...current, appKey];
    setCreateState((prev) => ({ ...prev, apps: next }));
  };

  // Function: handleCreateUser
  const handleCreateUser = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    setSuccess('');
    try {
      await createUser({
        username: createState.username,
        password: createState.password,
        role: createState.role,
        apps: normalizeApps(createState.apps),
      });
      setCreateState(emptyCreateState);
      setSuccess('User created successfully');
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to create user');
    } finally {
      setBusy(false);
    }
  };

  // Function: handleUpdateUser
  const handleUpdateUser = async (userId) => {
    const draft = drafts[userId];
    if (!draft) {
      return;
    }

    setBusy(true);
    setError('');
    setSuccess('');
    try {
      await updateUser(userId, {
        role: draft.role,
        is_active: draft.is_active,
        apps: normalizeApps(draft.apps),
        ...(draft.password ? { password: draft.password } : {}),
      });
      setSuccess('User updated successfully');
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to update user');
    } finally {
      setBusy(false);
    }
  };

  // Function: handleDeleteUser
  const handleDeleteUser = async (userId, username) => {
    const confirmed = window.confirm(`Delete user '${username}'? This cannot be undone.`);
    if (!confirmed) {
      return;
    }

    setBusy(true);
    setError('');
    setSuccess('');
    try {
      await deleteUser(userId);
      setSuccess('User deleted successfully');
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to delete user');
    } finally {
      setBusy(false);
    }
  };

  // Function: onLogout
  const onLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="az-shell">
      <header className="az-topbar">
        <div className="az-logo-mark">
          <ShieldCheck size={15} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="az-topbar-eyebrow">Administration</p>
          <p className="az-topbar-title">User Access Management</p>
        </div>
        <span className="az-topbar-user">Admin: {user?.username}</span>
        <button type="button" onClick={() => navigate('/launch-modules')} className="az-topbar-btn">
          <ArrowLeft size={13} />
          Back to Launcher
        </button>
        <button type="button" onClick={onLogout} className="az-topbar-btn">
          <LogOut size={13} />
          Logout
        </button>
      </header>

      <main className="az-content space-y-6">
        <section className="grid md:grid-cols-3 gap-4">
          <div className="az-stat-card">
            <p className="az-stat-label"><Users size={16} className="text-blue-500" /> Users</p>
            <p className="az-stat-value">{users.length}</p>
            <p className="az-stat-desc">Accounts managed through the portal.</p>
          </div>
          <div className="az-stat-card">
            <p className="az-stat-label"><CheckCircle2 size={16} className="text-emerald-600" /> Active</p>
            <p className="az-stat-value">{activeUsers}</p>
            <p className="az-stat-desc">Enabled users with current portal access.</p>
          </div>
          <div className="az-stat-card">
            <p className="az-stat-label"><LayoutGrid size={16} className="text-violet-600" /> Applications</p>
            <p className="az-stat-value">{appOptions.length}</p>
            <p className="az-stat-desc">Assignable modules across this modernization suite.</p>
          </div>
        </section>

        {(error || success) && (
          <div className={`az-alert ${error ? 'az-alert-error' : 'az-alert-success'}`}>
            {error || success}
          </div>
        )}

        <section className="az-panel">
          <div className="az-panel-head">
            <div className="az-panel-icon">
              <UserPlus size={18} />
            </div>
            <div>
              <p className="az-panel-eyebrow">Provision access</p>
              <h2 className="az-panel-title">Create New User</h2>
            </div>
          </div>
          <form className="mt-4 grid md:grid-cols-2 lg:grid-cols-4 gap-4" onSubmit={handleCreateUser}>
            <input
              type="text"
              value={createState.username}
              onChange={(e) => setCreateState((prev) => ({ ...prev, username: e.target.value }))}
              placeholder="Username"
              required
              className="az-field"
            />
            <input
              type="password"
              value={createState.password}
              onChange={(e) => setCreateState((prev) => ({ ...prev, password: e.target.value }))}
              placeholder="Temporary password"
              required
              className="az-field"
            />
            <select
              value={createState.role}
              onChange={(e) => setCreateState((prev) => ({ ...prev, role: e.target.value }))}
              className="az-field"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
            <button type="submit" disabled={busy} className="az-btn az-btn-primary">
              Create User
            </button>

            <div className="md:col-span-2 lg:col-span-4">
              <p className="az-panel-eyebrow mb-3">Application Access</p>
              <div className="flex flex-wrap gap-2.5">
                {appOptions.map((app) => (
                  <label key={app.key} className="az-checkbox-pill" data-checked={createState.apps.includes(app.key)}>
                    <input
                      type="checkbox"
                      checked={createState.apps.includes(app.key)}
                      onChange={() => toggleCreateApp(app.key)}
                    />
                    {app.name}
                  </label>
                ))}
              </div>
            </div>
          </form>
        </section>

        <section className="az-panel">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-3">
            <div>
              <p className="az-panel-eyebrow">User directory</p>
              <h2 className="az-panel-title">Existing Users</h2>
            </div>
            <p className="text-sm" style={{ color: 'var(--az-text-muted)' }}>Admins can update role, status, password resets, and application assignments.</p>
          </div>

          {loading ? (
            <div className="mt-4 text-sm" style={{ color: 'var(--az-text-muted)' }}>Loading users...</div>
          ) : (
            <div className="mt-4 space-y-3">
              {users.map((u) => {
                const draft = drafts[u.id] || { role: u.role, is_active: u.is_active, apps: u.apps || [], password: '' };
                return (
                  <article key={u.id} className="az-user-row">
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="font-medium" style={{ color: 'var(--az-text)' }}>{u.username}</p>
                          {u.role === 'admin' && <span className="az-tag">Admin</span>}
                          {!u.is_active && <span className="az-tag">Inactive</span>}
                        </div>
                        <p className="text-xs mt-1" style={{ color: 'var(--az-text-muted)' }}>Provider: {u.oauth_provider || 'local'} | Admin accounts: {adminUsers}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <select
                          value={draft.role}
                          onChange={(e) => updateDraft(u.id, { role: e.target.value })}
                          className="az-field min-w-[132px]"
                        >
                          <option value="user">User</option>
                          <option value="admin">Admin</option>
                        </select>
                        <label className="az-checkbox-pill" data-checked={Boolean(draft.is_active)}>
                          <input
                            type="checkbox"
                            checked={Boolean(draft.is_active)}
                            onChange={(e) => updateDraft(u.id, { is_active: e.target.checked })}
                          />
                          Active
                        </label>
                      </div>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2.5">
                      {appOptions.map((app) => (
                        <label key={app.key} className="az-checkbox-pill" data-checked={(draft.apps || []).includes(app.key)}>
                          <input
                            type="checkbox"
                            checked={(draft.apps || []).includes(app.key)}
                            onChange={() => toggleDraftApp(u.id, app.key)}
                            disabled={draft.role === 'admin'}
                          />
                          {app.name}
                        </label>
                      ))}
                    </div>

                    <div className="mt-3 grid md:grid-cols-[1fr_auto] gap-3">
                      <input
                        type="password"
                        value={draft.password || ''}
                        onChange={(e) => updateDraft(u.id, { password: e.target.value })}
                        placeholder="Set new password (optional)"
                        className="az-field"
                      />
                      <div className="flex items-center gap-2 justify-end">
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => handleDeleteUser(u.id, u.username)}
                          className="az-btn az-btn-danger"
                        >
                          <Trash2 size={14} />
                          Delete
                        </button>
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => handleUpdateUser(u.id)}
                          className="az-btn az-btn-primary"
                        >
                          Save Changes
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default AdminUsersPage;
