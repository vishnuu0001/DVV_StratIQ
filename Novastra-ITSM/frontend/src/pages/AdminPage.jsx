// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (AdminPage.jsx)
// Date: 2026-02-25
// ---------------------------------------------------------------------------
import { useEffect, useMemo, useState } from 'react'
import toast from 'react-hot-toast'
import { ShieldCheck, Trash2, Users, Grid2X2, UserPlus } from 'lucide-react'
import api from '../services/api.js'
import { useAuth } from '../contexts/AuthContext.jsx'

const APP_LABELS = {
  APP_RATIONALIZATION: 'App Rationalization',
  CODE_ANALYSIS: 'Code Analysis',
  INFRA_SCAN: 'Infra Scan',
  MODERNIZATION: 'Modernization',
  AI_PLAYBOOK: 'AI Playbook',
  NOVASTRA_ITSM: 'STM-ITSM',
  LAB_ROBOT: 'Lab Robot',
  HOSPITAL_MANAGEMENT_SYSTEM: 'Hospital Management System',
  IMAGE_VISION: 'ImageVision',
  ROBOT_AUTOMATION: 'Robot Automation',
  TOOL_ANALYSIS_QUALIFICATION: 'Tool Analysis Qualification',
  DASHBOARD: 'Dashboard',
  INTUNE_AUTOMATION: 'Intune Automation',
}

// Function: AdminPage
export default function AdminPage() {
  const { user } = useAuth()
  const [users, setUsers] = useState([])
  const [applications, setApplications] = useState([])
  const [form, setForm] = useState({ username: '', password: '', role: 'user', apps: ['APP_RATIONALIZATION'] })
  const [passwords, setPasswords] = useState({})

  const activeUsers = useMemo(() => users.filter((item) => item.is_active).length, [users])

  // Function: load
  const load = async () => {
    try {
      const { data } = await api.get('/auth/admin/users')
      setUsers(data.users || [])
      setApplications(data.applications || [])
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Unable to load users')
    }
  }

  useEffect(() => { load() }, [])

  // Function: toggleFormApp
  const toggleFormApp = (appId) => {
    setForm((prev) => ({
      ...prev,
      apps: prev.apps.includes(appId) ? prev.apps.filter((id) => id !== appId) : [...prev.apps, appId],
    }))
  }

  // Function: createUser
  const createUser = async (event) => {
    event.preventDefault()
    try {
      await api.post('/auth/admin/users', form)
      toast.success('User created')
      setForm({ username: '', password: '', role: 'user', apps: ['APP_RATIONALIZATION'] })
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Unable to create user')
    }
  }

  // Function: updateUser
  const updateUser = async (target, patch) => {
    try {
      await api.put(`/auth/admin/users/${target.id}`, patch)
      toast.success('Changes saved')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Unable to save changes')
    }
  }

  // Function: toggleUserApp
  const toggleUserApp = (target, appId) => {
    const apps = target.apps.includes(appId)
      ? target.apps.filter((id) => id !== appId)
      : [...target.apps, appId]
    updateUser(target, { apps })
  }

  // Function: deleteUser
  const deleteUser = async (target) => {
    if (!confirm(`Delete ${target.username}?`)) return
    try {
      await api.delete(`/auth/admin/users/${target.id}`)
      toast.success('User deleted')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Unable to delete user')
    }
  }

  return (
    <div className="min-h-full overflow-y-auto bg-[linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),radial-gradient(circle_at_48%_0%,rgba(79,70,229,0.18),transparent_36rem),radial-gradient(circle_at_86%_18%,rgba(6,182,212,0.14),transparent_36rem),#020617] bg-[length:64px_64px,64px_64px,auto,auto,auto] px-8 py-6 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <section className="mb-5 flex items-center gap-3 border-b border-slate-800 pb-5">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-cyan-500 text-slate-950">
            <ShieldCheck size={24} />
          </div>
          <div>
            <p className="text-xs font-black uppercase tracking-[0.25em] text-cyan-300">Administration</p>
            <h1 className="text-xs font-black text-white">User Access Management</h1>
          </div>
          <p className="ml-auto text-xs text-slate-300">Admin: {user?.username}</p>
        </section>

        <div className="mb-5 grid gap-4 md:grid-cols-3">
          <Stat icon={Users} label="Users" value={users.length} text="Accounts managed through the portal." />
          <Stat icon={ShieldCheck} label="Active" value={activeUsers} text="Enabled users with current portal access." />
          <Stat icon={Grid2X2} label="Applications" value={applications.length} text="Assignable modules across this modernization suite." />
        </div>

        <form onSubmit={createUser} className="mb-5 rounded-3xl border border-slate-700/80 bg-slate-950/70 p-6">
          <div className="mb-4 flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-2xl bg-indigo-500/20 text-indigo-200">
              <UserPlus size={20} />
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-[0.25em] text-cyan-300">Provision Access</p>
              <h2 className="text-xs font-black uppercase tracking-widest text-white">Create New User</h2>
            </div>
          </div>
          <div className="grid gap-4 lg:grid-cols-[1fr_1fr_1fr_1fr]">
            <input className="rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-xs outline-none focus:border-cyan-300" placeholder="Username" value={form.username} onChange={(e) => setForm((p) => ({ ...p, username: e.target.value }))} />
            <input className="rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-xs outline-none focus:border-cyan-300" placeholder="Temporary password" type="password" value={form.password} onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))} />
            <select className="rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-xs outline-none focus:border-cyan-300" value={form.role} onChange={(e) => setForm((p) => ({ ...p, role: e.target.value }))}>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
            <button className="rounded-xl bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500 px-4 py-2.5 text-xs font-black text-white">Create User</button>
          </div>
          <AppChecks apps={applications} selected={form.apps} onToggle={toggleFormApp} />
        </form>

        <section className="rounded-3xl border border-slate-700/80 bg-slate-950/70 p-6">
          <div className="mb-4 flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.25em] text-cyan-300">User Directory</p>
              <h2 className="text-xs font-black uppercase tracking-widest text-white">Existing Users</h2>
            </div>
            <p className="text-xs text-slate-400">Admins can update role, status, password resets, and application assignments.</p>
          </div>
          <div className="space-y-4">
            {users.map((target) => (
              <article key={target.id} className="rounded-2xl border border-slate-700/80 bg-slate-900/40 p-5">
                <div className="mb-4 flex flex-wrap items-center gap-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white">{target.username}</h3>
                    <p className="text-xs text-slate-400">Provider: {target.provider} | Admin accounts: {target.role === 'admin' ? 'yes' : 'no'}</p>
                  </div>
                  <select className="ml-auto rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm" value={target.role} onChange={(e) => updateUser(target, { role: e.target.value })}>
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                  <label className="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-3 py-1.5 text-xs font-semibold">
                    <input type="checkbox" checked={target.is_active} onChange={(e) => updateUser(target, { is_active: e.target.checked })} />
                    Active
                  </label>
                </div>
                <AppChecks apps={applications} selected={target.apps || []} onToggle={(appId) => toggleUserApp(target, appId)} compact />
                <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_auto_auto]">
                  <input className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs outline-none focus:border-cyan-300" placeholder="Set new password (optional)" type="password" value={passwords[target.id] || ''} onChange={(e) => setPasswords((p) => ({ ...p, [target.id]: e.target.value }))} />
                  <button type="button" className="rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 px-4 py-2 text-xs font-black text-white" onClick={() => updateUser(target, { password: passwords[target.id] || undefined })}>Save Changes</button>
                  <button type="button" className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-400/30 bg-red-500/20 px-4 py-2 text-xs font-black text-red-100" onClick={() => deleteUser(target)}>
                    <Trash2 size={16} /> Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

// Function: Stat
function Stat({ icon: Icon, label, value, text }) {
  return (
    <article className="rounded-2xl border border-slate-700/80 bg-slate-950/70 p-5">
      <Icon size={20} className="mb-2 text-cyan-300" />
      <h2 className="font-black text-white">{label}</h2>
      <strong className="block text-3xl font-black text-white">{value}</strong>
      <p className="m-0 text-xs text-slate-400">{text}</p>
    </article>
  )
}

// Function: AppChecks
function AppChecks({ apps, selected, onToggle, compact = false }) {
  return (
    <div className={compact ? 'mt-3 flex flex-wrap gap-2' : 'mt-5 flex flex-wrap gap-2'}>
      {apps.map((appId) => (
        <label key={appId} className="inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-2 text-xs font-bold text-slate-300">
          <input type="checkbox" checked={selected.includes(appId)} onChange={() => onToggle(appId)} />
          {APP_LABELS[appId] || appId}
        </label>
      ))}
    </div>
  )
}
