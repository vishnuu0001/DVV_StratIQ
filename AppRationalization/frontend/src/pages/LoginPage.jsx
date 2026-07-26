// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/pages (LoginPage.jsx)
// Date: 2026-03-20
// ---------------------------------------------------------------------------
import React, { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  Factory,
  Gauge,
  Lock,
  Sparkles,
  ShieldCheck,
  TrendingUp,
  Zap,
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';
import { fetchOauthProviders, getGithubAuthUrl, getGoogleAuthUrl } from '../services/authApi';

const WORKSPACE_DOMAINS = [
  { name: 'Portfolio & Analysis', count: 4, icon: BarChart3, accent: 'text-cyan-300' },
  { name: 'Modernization & AI', count: 2, icon: Zap, accent: 'text-indigo-300' },
  { name: 'Operations', count: 6, icon: Gauge, accent: 'text-sky-300' },
  { name: 'ATM Pipeline', count: 1, icon: TrendingUp, accent: 'text-emerald-300' },
];

// Function: LoginPage
const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, oauthError } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [providerState, setProviderState] = useState({
    google: { enabled: false },
    github: { enabled: false },
  });

  const redirectTo = useMemo(() => {
    const from = location.state?.from?.pathname;
    return from && from !== '/login' ? from : '/launch-modules';
  }, [location.state]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/launch-modules', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    let active = true;
    fetchOauthProviders()
      .then((data) => {
        if (active) {
          setProviderState(data);
        }
      })
      .catch(() => {
        if (active) {
          setProviderState({
            google: { enabled: false },
            github: { enabled: false },
          });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  // Function: handleLogin
  const handleLogin = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err?.response?.data?.error || 'Login failed. Check username and password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ar-shell flex items-center justify-center px-4 py-6 sm:px-6 lg:px-8">
      <div className="relative z-10 grid w-full max-w-[1460px] gap-6 xl:grid-cols-[1.12fr_0.88fr]">
        <section className="ar-module-hero overflow-hidden p-6 text-white sm:p-8 lg:p-10">
          <div className="flex flex-wrap gap-2">
            <span className="ar-pill border-white/15 bg-white/10 text-white">
              <Sparkles size={14} className="text-cyan-200" />
              Purpose-built workspace access
            </span>
            <span className="ar-pill border-white/15 bg-white/10 text-white">
              <ShieldCheck size={14} className="text-emerald-200" />
              Role aware routing
            </span>
          </div>

          <div className="mt-10 grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-end">
            <div>
              <p className="ar-badge border-white/15 bg-white/10 text-white">Unified launch point</p>
              <h1 className="mt-5 max-w-3xl font-[Space_Grotesk] text-4xl leading-[1.04] tracking-tight text-balance sm:text-5xl lg:text-6xl">
                A modern control room for portfolio, modernization, and operations work.
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-8 text-slate-200 sm:text-lg">
                Sign in once and move through governed modules without the old portal framing.
                This workspace is built as a fresh, high-contrast product surface with clearer hierarchy,
                richer motion, and a more editorial layout.
              </p>

              <div className="mt-8 grid gap-3 sm:grid-cols-3">
                {[
                  { value: '14', label: 'modules ready to launch', icon: Sparkles },
                  { value: '4', label: 'domains spanning the suite', icon: Factory },
                  { value: 'SSO', label: 'token handoff supported', icon: Lock },
                ].map((stat) => {
                  const Icon = stat.icon;
                  return (
                    <div key={stat.label} className="rounded-[22px] border border-white/12 bg-white/8 p-4 backdrop-blur-sm">
                      <Icon size={18} className="text-cyan-200" />
                      <p className="mt-4 text-3xl font-semibold tracking-tight text-white">{stat.value}</p>
                      <p className="mt-1 text-sm leading-6 text-slate-200/80">{stat.label}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="rounded-[28px] border border-white/15 bg-white/10 p-5 backdrop-blur-lg">
              <p className="text-xs font-semibold uppercase tracking-[0.32em] text-cyan-100/80">Workspace signal</p>
              <div className="mt-4 grid grid-cols-2 gap-3">
                {WORKSPACE_DOMAINS.map((domain) => {
                  const Icon = domain.icon;
                  return (
                    <div key={domain.name} className="rounded-[22px] border border-white/12 bg-slate-950/20 p-4">
                      <Icon size={18} className={domain.accent} />
                      <p className="mt-4 text-2xl font-semibold text-white">{domain.count}</p>
                      <p className="mt-1 text-xs leading-5 text-slate-200/75">{domain.name}</p>
                    </div>
                  );
                })}
              </div>
              <div className="mt-4 rounded-[22px] border border-white/10 bg-slate-950/20 p-4">
                <p className="text-[10px] uppercase tracking-[0.32em] text-cyan-100/70">Design direction</p>
                <p className="mt-2 text-sm leading-7 text-slate-100/90">
                  Clean glass panels, strong typography, and a deliberate color split. No clone of the old
                  infrastructure assessment portal.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="ar-panel-strong rounded-[30px] p-6 sm:p-8 lg:p-10">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="ar-badge">Portal access</p>
              <h2 className="mt-4 font-[Space_Grotesk] text-3xl font-bold tracking-tight text-slate-950">Sign in</h2>
              <p className="mt-2 max-w-md text-sm leading-7 text-slate-600">
                Enter your credentials to continue into the workspace launcher.
              </p>
            </div>
            <div className="hidden rounded-2xl border border-slate-200 bg-white p-3 shadow-sm sm:block">
              <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-slate-950 via-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-blue-900/20">
                <Factory size={20} />
              </div>
            </div>
          </div>

          {(error || oauthError) && (
            <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {error || `OAuth sign-in failed: ${oauthError}`}
            </div>
          )}

          <form className="mt-7 space-y-4" onSubmit={handleLogin}>
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
                className="ar-input"
                placeholder="Enter your username"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
                className="ar-input"
                placeholder="Enter your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="ar-primary-btn inline-flex w-full items-center justify-center gap-2 rounded-2xl px-4 py-3.5 font-semibold"
            >
              {loading ? 'Signing in...' : 'Enter workspace'}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          <div className="mt-6 flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
            <span className="h-px flex-1 bg-slate-200" />
            <span>or continue with</span>
            <span className="h-px flex-1 bg-slate-200" />
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <button
              type="button"
              disabled={!providerState.google?.enabled}
              onClick={() => {
                window.location.href = getGoogleAuthUrl();
              }}
              className="ar-secondary-btn rounded-2xl px-4 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
            >
              Continue with Google
            </button>
            <button
              type="button"
              disabled={!providerState.github?.enabled}
              onClick={() => {
                window.location.href = getGithubAuthUrl();
              }}
              className="ar-secondary-btn rounded-2xl px-4 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
            >
              Continue with GitHub
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default LoginPage;
