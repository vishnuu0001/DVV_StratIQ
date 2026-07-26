// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/pages (LaunchModulesPage.jsx)
// Date: 2026-05-27
// ---------------------------------------------------------------------------
import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  Bot,
  Car,
  Code2,
  Factory,
  FlaskConical,
  Gauge,
  GitBranch,
  LayoutPanelTop,
  LogOut,
  Network,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Truck,
  Zap,
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';
import { fetchApplications } from '../services/authApi';

const MODULES = [
  {
    key: 'APP_RATIONALIZATION',
    number: '01',
    name: 'App Rationalization',
    group: 'Portfolio & Analysis',
    chip: 'Portfolio Decisions',
    icon: BarChart3,
    url: () => `${window.location.origin}/app-rationalization`,
    description: 'Inventory, correlation, capability mapping, and rationalization decisions.',
  },
  {
    key: 'CODE_ANALYSIS',
    number: '02',
    name: 'Code Analysis',
    group: 'Portfolio & Analysis',
    chip: 'Code Intelligence',
    icon: Code2,
    url: () => process.env.REACT_APP_CODE_ANALYSIS_URL || 'http://localhost:5173/ca/',
    description: 'Repository health scoring, technical debt analysis, cloud maturity, and engineering reports.',
  },
  {
    key: 'INFRA_SCAN',
    number: '03',
    name: 'Infra Rationalization',
    group: 'Portfolio & Analysis',
    chip: 'Infra Scanner',
    icon: ScanSearch,
    url: () => process.env.REACT_APP_INFRA_SCAN_URL || 'http://localhost:5174/infra/',
    description: 'Infrastructure scan, assessment, and cloud migration classification.',
  },
  {
    key: 'MODERNIZATION',
    number: '04',
    name: 'Modernization Studio',
    group: 'Modernization & AI',
    chip: 'Modernization',
    icon: Zap,
    url: () => process.env.REACT_APP_MODERNIZATION_URL || 'http://localhost:5175/',
    description: 'AI-assisted legacy code analysis, stack migration, and modernization workflows.',
  },
  {
    key: 'NOVASTRA_ITSM',
    number: '05',
    name: 'Novastra-ITSM',
    group: 'Operations',
    chip: 'Knowledge Graph',
    icon: Network,
    url: () => process.env.REACT_APP_NOVASTRA_ITSM_URL || 'http://localhost:5177/novastra-itsm/ticket-analysis',
    description: 'Ticket analysis, knowledge graph queries, and operational insight exploration.',
  },
  {
    key: 'DASHBOARD',
    number: '06',
    name: 'Dashboard',
    group: 'Operations',
    chip: 'Digital Cockpit',
    icon: Gauge,
    url: () => process.env.REACT_APP_DASHBOARD_URL || 'http://localhost:5178/dash/connect?autostart=1',
    description: 'Digital operations monitoring, KPI views, analytics, and reporting.',
  },
  {
    key: 'SSDLC_PROCESS_ASSESSMENT',
    number: '07',
    name: 'SSDLC Process Assessment',
    group: 'Operations',
    chip: 'SSDLC Governance',
    icon: ShieldCheck,
    url: () => process.env.REACT_APP_SSDLC_PROCESS_ASSESSMENT_URL || 'http://localhost:5182/ssdlc/',
    description: 'Weighted maturity scoring, evidence capture, recommendations, and dashboard review.',
  },
  {
    key: 'LAB_ROBOT',
    number: '08',
    name: 'Lab Robot',
    group: 'Operations',
    chip: 'Lab Robot',
    icon: FlaskConical,
    url: () => process.env.REACT_APP_LAB_ROBOT_URL || 'http://localhost:7000/',
    description: 'Virtual rack management, barcode tracking, chemical placement, and lab workflows.',
  },
  {
    key: 'OPPORTUNITY_TRACKER',
    number: '09',
    name: 'Opportunity Tracker',
    group: 'ATM Pipeline',
    chip: "FY'27 Pipeline",
    icon: TrendingUp,
    url: () => process.env.REACT_APP_OPPORTUNITY_TRACKER_URL || 'http://localhost:5183/ot/',
    description: 'Pipeline opportunities, commercial values, and consolidated reporting.',
  },
  {
    key: 'AI_REMAN_CORE',
    number: '10',
    name: 'AI Reman Core',
    group: 'Modernization & AI',
    chip: 'AI Inspection',
    icon: Bot,
    url: () => process.env.REACT_APP_AI_REMAN_CORE_URL || 'http://localhost:5184/',
    description: 'Image-driven remanufactured core inspection, confidence scoring, and warranty estimation.',
  },
  {
    key: 'AI_VEHICLE_LOAN',
    number: '11',
    name: 'AI Vehicle Loan',
    group: 'Operations',
    chip: 'Vehicle Loans',
    icon: Car,
    url: () => process.env.REACT_APP_AI_VEHICLE_LOAN_URL || 'http://localhost:5185/',
    description: 'Vehicle financing simulation, credit scoring, lender matching, and loan analysis.',
  },
  {
    key: 'MICROSITE_DATA_ANALYSIS',
    number: '12',
    name: 'Data Analysis Studio',
    group: 'Portfolio & Analysis',
    chip: 'Tower Consolidation',
    icon: LayoutPanelTop,
    url: () => process.env.REACT_APP_MICROSITE_DATA_ANALYSIS_URL || 'http://localhost:5187/mda/',
    description: 'Tower consolidation simulation, transformation intelligence, scenarios, and roadmap planning.',
  },
  {
    key: 'SUPPLY_CHAIN_DISRUPTION_MANAGER',
    number: '13',
    name: 'Supply Chain Disruption Manager',
    group: 'Operations',
    chip: 'Supply Chain',
    icon: Truck,
    url: () => process.env.REACT_APP_SUPPLY_CHAIN_DISRUPTION_MANAGER_URL || 'http://localhost:5188/',
    description: 'Sense-Understand-Act disruption management: signal ingestion, knowledge graph blast radius, and agentic incident response.',
  },
  {
    key: 'TRACEFORGE',
    number: '14',
    name: 'TraceForge',
    group: 'Modernization & AI',
    chip: 'SDLC Artifact Factory',
    icon: GitBranch,
    url: () => process.env.REACT_APP_TRACEFORGE_URL || 'http://localhost:5186/tf/',
    description: 'AI-assisted requirements extraction, BRD authoring, test design, and script generation with a full traceability spine.',
  },
];

const groupOrder = ['Portfolio & Analysis', 'Modernization & AI', 'Operations', 'ATM Pipeline'];
// Function: withAuthHash
const withAuthHash = (url, token) => (token ? `${url}#authToken=${encodeURIComponent(token)}` : url);
// Function: formatModuleNumber
const formatModuleNumber = (index) => String(index + 1).padStart(2, '0');

// Function: LaunchModulesPage
const LaunchModulesPage = () => {
  const navigate = useNavigate();
  const { user, token, hasAccess, logout } = useAuth();
  const [applications, setApplications] = useState(MODULES);

  useEffect(() => {
    let active = true;
    fetchApplications()
      .then((response) => {
        if (!active) return;
        const appKeys = new Set((response?.applications || []).map((app) => app.key));
        setApplications(MODULES.filter((module) => appKeys.has(module.key)));
      })
      .catch(() => {
        if (active) setApplications(MODULES);
      });
    return () => {
      active = false;
    };
  }, []);

  const groupedModules = useMemo(
    () =>
      applications.reduce((groups, app) => {
        const group = app.group || 'Operations';
        return { ...groups, [group]: [...(groups[group] || []), app] };
      }, {}),
    [applications]
  );

  const moduleDisplayNumbers = useMemo(() => {
    let displayIndex = 0;
    return groupOrder.reduce((numbers, group) => {
      (groupedModules[group] || []).forEach((app) => {
        numbers[app.key] = formatModuleNumber(displayIndex);
        displayIndex += 1;
      });
      return numbers;
    }, {});
  }, [groupedModules]);

  // Function: openModule
  const openModule = (app) => {
    if (!hasAccess(app.key)) return;
    window.location.assign(withAuthHash(app.url(), token));
  };

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
              <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white">STRAT.iQ | Launch Modules</p>
            </div>
            <div className="flex flex-wrap items-center gap-2.5 text-sm">
              <span className="text-white text-xs">Signed in as <span className="text-white font-medium">{user?.username}</span></span>
              <span className="hidden lg:inline-flex text-[11px] items-center gap-1.5 rounded-full border border-white/45 bg-sky-400/35 px-3 py-1.5 text-white">
                <Sparkles size={12} className="text-white" />
                {applications.length} modules
              </span>
              <button type="button" onClick={() => navigate('/home')} className="px-3.5 py-2 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5 border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors">
                <ArrowLeft size={13} />
                Homepage
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

        <main className="portal-page-width px-5 py-10 space-y-14">
          {groupOrder.filter((group) => groupedModules[group]?.length).map((group) => (
            <section key={group} className="space-y-6">
              <div className="border-b border-slate-800/60 pb-4">
                <p className="portal-section-label">{group}</p>
                <h2 className="mt-1 text-xl font-semibold text-white">Available project modules</h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 items-stretch">
                {groupedModules[group].map((app) => {
                  const Icon = app.icon || LayoutPanelTop;
                  const canUse = hasAccess(app.key);
                  return (
                    <article key={app.key} className="portal-panel rounded-[28px] p-6 flex flex-col h-full">
                      <div className="portal-illustration-frame h-36 p-3 flex items-center justify-center">
                        <div className="h-full w-full rounded-[18px] border border-slate-700/70 bg-slate-900/50 flex items-center justify-center">
                          <Icon size={44} className="text-cyan-200" />
                        </div>
                      </div>
                      <div className="mt-5 flex items-center justify-between gap-3">
                        <div>
                          <p className="portal-section-label">Module {moduleDisplayNumbers[app.key]}</p>
                          <h3 className="mt-2 text-xl font-semibold text-white">{app.name}</h3>
                        </div>
                        <span className="portal-chip text-[11px]">{app.chip}</span>
                      </div>
                      <p className="mt-4 text-sm leading-7 text-slate-300 flex-1">{app.description}</p>
                      <button type="button" disabled={!canUse} onClick={() => openModule(app)} className="portal-btn-primary mt-6 px-4 py-3 rounded-xl text-sm font-semibold inline-flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed">
                        {canUse ? `Open ${app.name}` : 'Access Not Granted'}
                        {canUse && <ArrowRight size={16} />}
                      </button>
                    </article>
                  );
                })}
              </div>
            </section>
          ))}
        </main>
      </div>
    </div>
  );
};

export default LaunchModulesPage;
