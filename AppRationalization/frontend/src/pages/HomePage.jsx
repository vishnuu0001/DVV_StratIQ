// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/pages (HomePage.jsx)
// Date: 2026-03-20
// ---------------------------------------------------------------------------
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Factory, LayoutPanelTop, LogOut, ShieldCheck, Sparkles } from 'lucide-react';

import { useAuth } from '../context/AuthContext';

// Function: HomePage
const HomePage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // Function: onLogout
  const onLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="portal-app-shell">
      <div className="portal-content">
        <header className="sticky top-0 z-30 border-b border-sky-200/80 bg-sky-300/85 backdrop-blur-xl">
          <div className="portal-page-width px-5 py-3.5 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-violet-600 via-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-violet-950/40">
                <Factory size={18} className="text-white" />
              </div>
              <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white">Strat-Aqorynth | Project Modules</p>
            </div>
            <div className="flex items-center gap-2.5 text-sm flex-wrap">
              <span className="text-white text-xs">
                Signed in as <span className="text-white font-medium">{user?.username}</span>
              </span>
              <span className="hidden lg:inline-flex text-[11px] items-center gap-1.5 rounded-full border border-white/45 bg-sky-400/35 px-3 py-1.5 text-white">
                <Sparkles size={12} className="text-white" />
                Existing modules only
              </span>
              <button type="button" onClick={() => navigate('/launch-modules')} className="px-3.5 py-2 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5 border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors">
                <LayoutPanelTop size={13} />
                Launch Modules
              </button>
              {user?.role === 'admin' && (
                <button type="button" onClick={() => navigate('/admin')} className="px-3.5 py-2 rounded-xl text-xs font-semibold border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors">
                  Admin Console
                </button>
              )}
              <button type="button" onClick={onLogout} className="px-3.5 py-2 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5 border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors">
                <LogOut size={13} />
                Logout
              </button>
            </div>
          </div>
        </header>

        <main className="portal-page-width px-5 py-12 space-y-10">
          <section className="portal-glass rounded-[28px] overflow-hidden">
            <div className="h-px w-full bg-gradient-to-r from-violet-600 via-cyan-500 to-transparent" />
            <div className="px-10 py-14 lg:py-20 flex flex-col lg:flex-row lg:items-center gap-12">
              <div className="flex-1 min-w-0">
                <p className="text-[11px] font-bold uppercase tracking-[0.28em] text-cyan-400 mb-5">
                  Launch the existing project modules
                </p>
                <h2 className="text-5xl lg:text-6xl font-extrabold leading-[1.05] tracking-tight text-white">
                  Strat-Aqorynth<br />
                  <span
                    style={{
                      background: 'linear-gradient(135deg, #a78bfa 0%, #22d3ee 55%, #bfdbfe 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                    }}
                  >
                    Workspace
                  </span>
                </h2>
                <p className="mt-6 text-base leading-8 text-slate-400 max-w-lg">
                  The launcher is configured for the module folders present in this project. The static LaunchModules folder and logs folder are excluded from startup.
                </p>
                <div className="mt-10 flex flex-wrap gap-3">
                  <button type="button" onClick={() => navigate('/launch-modules')} className="portal-btn-primary px-6 py-3.5 rounded-xl text-sm font-bold inline-flex items-center gap-2">
                    Open Launch Modules
                    <ArrowRight size={16} />
                  </button>
                </div>
              </div>

              <div className="shrink-0 flex flex-col gap-4 lg:min-w-[280px]">
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: '13', label: 'Modules' },
                    { value: '0', label: 'Missing refs' },
                    { value: '1', label: 'Portal' },
                  ].map(({ value, label }) => (
                    <div key={label} className="portal-stat-card text-center px-4 py-6">
                      <p className="text-3xl font-bold text-white">{value}</p>
                      <p className="mt-1.5 text-[11px] text-slate-400 uppercase tracking-wider">{label}</p>
                    </div>
                  ))}
                </div>
                <div className="portal-stat-card px-5 py-4 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-cyan-400/10 border border-cyan-300/15 flex items-center justify-center shrink-0">
                      <ShieldCheck size={15} className="text-cyan-300" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-white">Role-based access</p>
                      <p className="text-[10px] text-slate-500 mt-0.5">Existing modules only</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="portal-panel rounded-[24px] px-8 py-7 flex flex-col lg:flex-row lg:items-center gap-6 justify-between border-t border-t-cyan-500/15">
            <div className="max-w-3xl">
              <p className="portal-section-label">Active Launcher</p>
              <h3 className="mt-2 text-2xl font-semibold text-white">All existing modules</h3>
              <p className="mt-3 text-sm leading-7 text-slate-400">
                Start and navigate to App Rationalization, Code Analysis, Infra Rationalization, Dashboard, Novastra-ITSM, Modernization, Lab Robot, SSDLC, Opportunity Tracker, AI Reman Core, AI Vehicle Loan, Data Analysis Studio, and Supply Chain Disruption Manager.
              </p>
            </div>
            <button type="button" onClick={() => navigate('/launch-modules')} className="portal-btn-primary shrink-0 px-6 py-3 rounded-xl text-sm font-bold inline-flex items-center gap-2">
              Launch Modules
              <ArrowRight size={15} />
            </button>
          </section>
        </main>
      </div>
    </div>
  );
};

export default HomePage;
