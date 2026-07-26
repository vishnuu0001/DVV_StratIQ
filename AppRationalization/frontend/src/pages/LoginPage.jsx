// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/pages (LoginPage.jsx)
// Date: 2026-03-20
// ---------------------------------------------------------------------------
import React, { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowRight, BarChart3, Factory, Gauge, Lock, ShieldCheck, Sparkles, TrendingUp, Zap } from 'lucide-react';

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
    <div className="portal-app-shell flex items-center justify-center p-5 lg:p-8">
      <div className="portal-content portal-page-width grid xl:grid-cols-[1.08fr_0.92fr] gap-6">
        <section className="portal-glass rounded-[30px] p-8 sm:p-10 lg:p-12 flex flex-col justify-between">
          <div>
            <div className="flex flex-wrap gap-2">
              <span className="portal-chip">
                <Sparkles size={14} className="text-cyan-300" />
                13 AI-powered modules
              </span>
              <span className="portal-chip">
                <ShieldCheck size={14} className="text-indigo-300" />
                Role-based access
              </span>
            </div>

            <div className="mt-8 flex items-center gap-3">
              <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-indigo-500 via-cyan-500 to-sky-500 flex items-center justify-center shadow-lg shadow-cyan-950/30">
                <Factory size={22} className="text-white" />
              </div>
              <div>
                <p className="portal-section-label"></p>
                <h1 className="text-3xl sm:text-4xl font-semibold leading-tight text-white">Secure entry to the StratIQ project workspace</h1>
              </div>
            </div>

            <p className="mt-6 max-w-2xl text-sm sm:text-base leading-8 text-slate-300">
              One login for the full StratIQ suite — portfolio rationalization, modernization,
              ITSM intelligence, and supply-chain resilience — with only the modules assigned to
              your role ever visible or launchable.
            </p>

            <div className="mt-8 grid sm:grid-cols-3 gap-4">
              <div className="portal-stat-card">
                <Sparkles size={18} className="text-cyan-300" />
                <p className="mt-3 text-2xl font-semibold text-white">13</p>
                <p className="mt-1 text-xs leading-6 text-slate-400">Modules spanning portfolio, modernization, ITSM, and supply-chain tooling.</p>
              </div>
              <div className="portal-stat-card">
                <Factory size={18} className="text-indigo-300" />
                <p className="mt-3 text-2xl font-semibold text-white">4</p>
                <p className="mt-1 text-xs leading-6 text-slate-400">Domains — Portfolio & Analysis, Modernization & AI, Operations, ATM Pipeline.</p>
              </div>
              <div className="portal-stat-card">
                <Lock size={18} className="text-sky-300" />
                <p className="mt-3 text-base font-semibold text-white">Role-based</p>
                <p className="mt-1 text-xs leading-6 text-slate-400">Only the modules assigned to your account are ever shown or launchable.</p>
              </div>
            </div>
          </div>

          <div className="portal-illustration-frame mt-8 p-5">
            <p className="portal-section-label">Workspace at a glance</p>
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
              {WORKSPACE_DOMAINS.map((domain) => {
                const Icon = domain.icon;
                return (
                  <div key={domain.name} className="portal-panel-soft rounded-2xl p-4 flex flex-col gap-2">
                    <Icon size={18} className={domain.accent} />
                    <p className="text-xl font-semibold text-white">{domain.count}</p>
                    <p className="text-[11px] leading-5 text-slate-400">{domain.name}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="portal-panel rounded-[30px] p-8 sm:p-10 lg:p-12">
          <p className="portal-section-label">Portal access</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">Welcome</h2>
          <p className="mt-3 text-sm leading-7 text-slate-400">
            Sign in to continue to the project workspace.
          </p>

          {(error || oauthError) && (
            <div className="mt-6 rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
              {error || `OAuth sign-in failed: ${oauthError}`}
            </div>
          )}

          <form className="mt-7 space-y-4" onSubmit={handleLogin}>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
                className="portal-input"
                placeholder="Enter your username"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
                className="portal-input"
                placeholder="Enter your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="portal-btn-primary w-full rounded-2xl py-3 font-semibold inline-flex items-center justify-center gap-2"
            >
              {loading ? 'Signing in...' : 'Sign in'}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          <div className="mt-6 flex items-center gap-3 text-xs text-slate-500">
            <span className="h-px flex-1 bg-slate-800" />
            <span>or continue with</span>
            <span className="h-px flex-1 bg-slate-800" />
          </div>

          <div className="mt-4 grid sm:grid-cols-2 gap-3">
            <button
              type="button"
              disabled={!providerState.google?.enabled}
              onClick={() => {
                window.location.href = getGoogleAuthUrl();
              }}
              className="portal-btn-secondary rounded-2xl py-3 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue with Google
            </button>
            <button
              type="button"
              disabled={!providerState.github?.enabled}
              onClick={() => {
                window.location.href = getGithubAuthUrl();
              }}
              className="portal-btn-secondary rounded-2xl py-3 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
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
