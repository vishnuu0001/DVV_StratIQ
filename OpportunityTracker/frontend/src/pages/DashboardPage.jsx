// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages (DashboardPage.jsx)
// Date: 2025-09-12
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, Plus, BarChart3, LogOut, Home, RefreshCw, DollarSign, Target, CheckCircle, ShieldCheck, LineChart, UploadCloud } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import OpportunityForm from './OpportunityForm';
import OpportunityReport from './OpportunityReport';
import OpportunityImportPanel from './OpportunityImportPanel';
import FinancialDashboard from './FinancialDashboard';
import api from '../services/api';
import { isClosedWonStage } from '../constants/stages';

const PORTAL_HOME = import.meta.env.VITE_PORTAL_HOME_URL || '/home';

// Function: StatCard
function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="ot-card px-5 py-4 flex items-center gap-4">
      <div className={`h-10 w-10 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
        <Icon size={18} className="text-white" />
      </div>
      <div>
        <p className="text-xs text-slate-400 uppercase tracking-wider">{label}</p>
        <p className="text-xl font-bold text-white mt-0.5">{value}</p>
      </div>
    </div>
  );
}

// Function: DashboardPage
export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [tab, setTab] = useState('opportunity'); // top-level: 'opportunity' | 'financial'
  const [oppSubTab, setOppSubTab] = useState('report'); // 'report' | 'new', only relevant under the Opportunity tab
  const [reportRefresh, setReportRefresh] = useState(0);
  const [stats, setStats] = useState({ total: 0, total_tcv: 0, total_fy27: 0, won: 0 });

  const loadStats = useCallback(async () => {
    try {
      const { data } = await api.get('opportunities');
      setStats({
        total: data.length,
        total_tcv: data.reduce((s, r) => s + (r.tcv_mn || 0), 0),
        total_fy27: data.reduce((s, r) => s + (r.fy27_mn || 0), 0),
        won: data.filter((r) => isClosedWonStage(r.oppty_stage)).length,
      });
    } catch { /* stats are non-critical */ }
  }, []);

  useEffect(() => {
    if (tab === 'opportunity') loadStats();
  }, [loadStats, reportRefresh, tab]);

  // Function: onOpportunityCreated
  const onOpportunityCreated = () => {
    setReportRefresh((k) => k + 1);
    setOppSubTab('report');
  };

  // Function: onLogout
  const onLogout = async () => {
    await logout();
    window.location.href = `${import.meta.env.BASE_URL}login`;
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-30 border-b border-sky-200/80 bg-sky-300/85 backdrop-blur-xl">
        <div className="max-w-[1600px] mx-auto px-5 py-3.5 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-violet-600 via-blue-600 to-cyan-500 flex items-center justify-center shadow-lg">
              <TrendingUp size={18} className="text-white" />
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white">Unified Modernization Suite</p>
              <p className="text-base font-bold text-white leading-tight">Opportunity Tracker Workspace</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2.5 text-sm">
            <span className="text-white text-xs">
              Signed in as <span className="text-white font-semibold">{user?.username}</span>
            </span>
            <a
              href={PORTAL_HOME}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
            >
              <Home size={13} /> Portal Home
            </a>
            {user?.role === 'admin' && (
              <a
                href={(() => {
                  try {
                    return new URL('/admin', PORTAL_HOME).href;
                  } catch {
                    return '/admin';
                  }
                })()}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
              >
                <ShieldCheck size={13} /> Admin Console
              </a>
            )}
            <button
              onClick={onLogout}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
            >
              <LogOut size={13} /> Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-[1600px] mx-auto px-5 py-8 space-y-8">

        {/* Top-level tabs */}
        <div className="flex items-center gap-1 border-b border-slate-800 pb-0">
          {[
            { id: 'opportunity', label: 'Opportunity', icon: Target },
            { id: 'financial', label: 'Financial Dashboard', icon: LineChart },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-colors ${
                tab === id
                  ? 'border-cyan-500 text-cyan-400'
                  : 'border-transparent text-slate-500 hover:text-slate-300'
              }`}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </div>

        {tab === 'opportunity' && (
          <>
            {/* Stats row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard icon={Target} label="Total Opportunities" value={stats.total} color="bg-violet-600" />
              <StatCard icon={DollarSign} label="Total TCV $Mn" value={stats.total_tcv.toFixed(2)} color="bg-cyan-600" />
              <StatCard icon={BarChart3} label="FY'27 Pipeline $Mn" value={stats.total_fy27.toFixed(2)} color="bg-blue-600" />
              <StatCard icon={CheckCircle} label="Closed Won" value={stats.won} color="bg-emerald-600" />
            </div>

            {/* Opportunity sub-tabs */}
            <div className="flex items-center gap-1 border-b border-slate-800 pb-0">
              {[
                { id: 'report', label: 'Pipeline Report', icon: BarChart3 },
                { id: 'new', label: 'New Opportunity', icon: Plus },
                { id: 'import', label: 'Import Workbook', icon: UploadCloud },
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setOppSubTab(id)}
                  className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-colors ${
                    oppSubTab === id
                      ? 'border-cyan-500 text-cyan-400'
                      : 'border-transparent text-slate-500 hover:text-slate-300'
                  }`}
                >
                  <Icon size={15} />
                  {label}
                </button>
              ))}
              <div className="flex-1" />
              {oppSubTab === 'report' && (
                <button onClick={() => setReportRefresh((k) => k + 1)} className="mb-0.5 ot-btn-secondary text-xs px-3 py-1.5">
                  <RefreshCw size={13} /> Refresh
                </button>
              )}
            </div>

            {oppSubTab === 'report' && (
              <OpportunityReport refreshKey={reportRefresh} />
            )}
            {oppSubTab === 'new' && (
              <OpportunityForm onCreated={onOpportunityCreated} />
            )}
            {oppSubTab === 'import' && (
              <OpportunityImportPanel onImported={onOpportunityCreated} />
            )}
          </>
        )}

        {tab === 'financial' && <FinancialDashboard refreshKey={reportRefresh} />}
      </main>
    </div>
  );
}
