// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages (LoginPage.jsx)
// Date: 2026-01-31
// ---------------------------------------------------------------------------
import React, { useState } from 'react';
import { TrendingUp, Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

// Function: LoginPage
export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState('');

  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Function: submit
  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username.trim(), password);
      window.location.replace(`${import.meta.env.BASE_URL}dashboard`);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Invalid credentials. This module requires Administrator access.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      {/* Background grid */}
      <div className="fixed inset-0 opacity-[0.04] bg-[linear-gradient(rgba(6,182,212,1)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,1)_1px,transparent_1px)] bg-[size:48px_48px]" />

      <div className="relative w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-violet-600 via-blue-600 to-cyan-500 flex items-center justify-center shadow-xl shadow-violet-950/40">
            <TrendingUp size={22} className="text-white" />
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-cyan-400">Strat-Aqorynth</p>
            <p className="text-xl font-bold text-white">Opportunity Tracker</p>
          </div>
        </div>

        {/* Card */}
        <div className="ot-card p-8">
          <div className="mb-6">
            <h1 className="text-lg font-bold text-white">Administrator Sign-In</h1>
            <p className="mt-1 text-sm text-slate-400">This module requires Administrator credentials.</p>
          </div>

          {error && (
            <div className="mb-5 flex items-start gap-2.5 rounded-xl bg-red-500/10 border border-red-500/25 px-4 py-3">
              <AlertCircle size={16} className="text-red-400 shrink-0 mt-0.5" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <form onSubmit={submit} autoComplete="off" className="space-y-5">
            <div>
              <label className="ot-label">Username</label>
              <input
                className="ot-input"
                name="ot_username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Administrator"
                autoComplete="off"
                required
              />
            </div>
            <div>
              <label className="ot-label">Password</label>
              <div className="relative">
                <input
                  className="ot-input pr-10"
                  name="ot_password"
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  autoComplete="new-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPw((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="ot-btn-primary w-full justify-center py-2.5"
            >
              {loading ? (
                <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
              ) : (
                <LogIn size={16} />
              )}
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
        </div>

        <p className="mt-6 text-center text-xs text-slate-600">
          Strat-Aqorynth · Opportunity Tracker · Restricted Access
        </p>
      </div>
    </div>
  );
}
