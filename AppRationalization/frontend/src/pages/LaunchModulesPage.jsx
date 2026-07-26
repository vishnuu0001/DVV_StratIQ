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
  Lock,
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
const GROUP_DETAILS = {
  'Portfolio & Analysis': {
    eyebrow: 'Portfolio intelligence',
    title: 'Map the estate, then move with intent.',
    description: 'Start with discovery, prioritization, and rationalization before you launch into transformation work.',
    accent: 'linear-gradient(135deg, rgba(59,130,246,0.9), rgba(14,165,233,0.88))',
  },
  'Modernization & AI': {
    eyebrow: 'Modernization studio',
    title: 'Transform code, docs, and delivery with AI-native workflows.',
    description: 'Use the modernization and AI modules as a connected workspace for migrations, automation, and artifact generation.',
    accent: 'linear-gradient(135deg, rgba(99,102,241,0.9), rgba(168,85,247,0.82))',
  },
  Operations: {
    eyebrow: 'Operations cockpit',
    title: 'Run the business with controlled, observable actions.',
    description: 'Use the operational tools for service workflows, governance, lab flows, and live control surfaces.',
    accent: 'linear-gradient(135deg, rgba(15,23,42,0.94), rgba(34,197,94,0.72))',
  },
  'ATM Pipeline': {
    eyebrow: 'Pipeline radar',
    title: 'Track commercial motion and pipeline momentum.',
    description: 'Move from opportunity discovery to execution planning with the same launch surface.',
    accent: 'linear-gradient(135deg, rgba(249,115,22,0.9), rgba(244,63,94,0.82))',
  },
};
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

  const visibleCount = applications.length;
  const accessibleCount = applications.filter((app) => hasAccess(app.key)).length;
  const lockedCount = visibleCount - accessibleCount;

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
    <div className="ar-shell">
      <div className="relative z-10">
        <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/72 backdrop-blur-xl">
          <div className="mx-auto flex w-full max-w-[1500px] flex-col gap-4 px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-slate-950 via-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-900/20">
                <Factory size={18} />
              </div>
              <div>
                <p className="ar-badge">Workspace launcher</p>
                <h1 className="font-[Space_Grotesk] text-lg font-bold tracking-tight text-slate-950 sm:text-xl">Strat-Aqorynth launch surface</h1>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="ar-pill">
                <Sparkles size={12} className="text-cyan-600" />
                {visibleCount} visible modules
              </span>
              <span className="ar-pill">
                <ShieldCheck size={12} className="text-emerald-600" />
                {accessibleCount} launchable now
              </span>
              <span className="ar-pill">
                <Lock size={12} className="text-slate-500" />
                {lockedCount} access-gated
              </span>
              <button type="button" onClick={() => navigate('/home')} className="ar-secondary-btn inline-flex items-center gap-1.5 rounded-2xl px-3.5 py-2 text-xs font-semibold">
                <ArrowLeft size={13} />
                Home
              </button>
              {user?.role === 'admin' && (
                <button type="button" onClick={() => navigate('/admin')} className="ar-secondary-btn rounded-2xl px-3.5 py-2 text-xs font-semibold">
                  Admin Console
                </button>
              )}
              <button type="button" onClick={onLogout} className="rounded-2xl bg-slate-950 px-3.5 py-2 text-xs font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-slate-800">
                <span className="inline-flex items-center gap-1.5">
                  <LogOut size={13} />
                  Logout
                </span>
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1500px] px-5 py-8 lg:py-10">
          <section className="ar-module-hero overflow-hidden p-6 text-white sm:p-8 lg:p-10">
            <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
              <div>
                <p className="ar-badge border-white/15 bg-white/10 text-white">Launch modules</p>
                <h2 className="mt-4 max-w-3xl font-[Space_Grotesk] text-4xl leading-[1.04] tracking-tight text-balance sm:text-5xl">
                  Choose the right workspace for the next decision.
                </h2>
                <p className="mt-5 max-w-2xl text-base leading-8 text-slate-200 sm:text-lg">
                  This launcher is intentionally different from the infrastructure assessment page. It uses a
                  product-like dashboard composition, deeper contrast, and clear module separation so the suite
                  feels like a distinct workspace rather than a cloned template.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                {[
                  { label: 'Modules', value: visibleCount },
                  { label: 'Accessible', value: accessibleCount },
                  { label: 'Gated', value: lockedCount },
                ].map((item) => (
                  <div key={item.label} className="rounded-[22px] border border-white/12 bg-white/10 p-4 backdrop-blur-sm">
                    <p className="text-xs uppercase tracking-[0.28em] text-cyan-100/70">{item.label}</p>
                    <p className="mt-3 font-[Space_Grotesk] text-4xl font-bold text-white">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <div className="mt-8 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
            <section className="ar-panel rounded-[28px] p-6 sm:p-8">
              <div className="flex flex-wrap items-end justify-between gap-4 border-b border-slate-200 pb-5">
                <div>
                  <p className="ar-badge">Module map</p>
                  <h3 className="mt-3 font-[Space_Grotesk] text-2xl font-bold tracking-tight text-slate-950">Curated entry points by domain</h3>
                </div>
                <p className="max-w-md text-sm leading-7 text-slate-600">
                  Every card is designed to feel like a standalone product, not a generic shell. Launch what you need and keep the surface focused.
                </p>
              </div>

              <div className="mt-6 grid gap-4 sm:grid-cols-2 2xl:grid-cols-3">
                {groupOrder.filter((group) => groupedModules[group]?.length).flatMap((group) => (
                  groupedModules[group].map((app) => {
                    const Icon = app.icon || LayoutPanelTop;
                    const canUse = hasAccess(app.key);
                    const groupMeta = GROUP_DETAILS[group] || GROUP_DETAILS.Operations;
                    const moduleIndex = moduleDisplayNumbers[app.key];
                    return (
                      <article
                        key={app.key}
                        className="ar-module-card flex h-full flex-col rounded-[26px] p-5 transition duration-200"
                        style={{ '--module-accent': groupMeta.accent }}
                      >
                        <div className="relative overflow-hidden rounded-[22px] border border-slate-200 bg-slate-50 p-5">
                          <div className="absolute inset-0 opacity-50 ar-soft-grid" />
                          <div className="relative flex items-center justify-between gap-4">
                            <div>
                              <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-500">Module {moduleIndex}</p>
                              <h4 className="mt-3 font-[Space_Grotesk] text-2xl font-bold tracking-tight text-slate-950">{app.name}</h4>
                            </div>
                            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-white shadow-lg">
                              <Icon size={26} />
                            </div>
                          </div>
                          <p className="relative mt-4 text-sm leading-7 text-slate-600">{app.description}</p>
                        </div>

                        <div className="mt-4 flex items-center justify-between gap-3">
                          <span className="ar-pill text-[11px] font-semibold">{app.chip}</span>
                          <span className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-400">{group}</span>
                        </div>

                        <button
                          type="button"
                          disabled={!canUse}
                          onClick={() => openModule(app)}
                          className="ar-primary-btn mt-5 inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55"
                        >
                          {canUse ? `Open ${app.name}` : 'Access not granted'}
                          {canUse && <ArrowRight size={16} />}
                        </button>
                      </article>
                    );
                  })
                ))}
              </div>
            </section>

            <aside className="space-y-5">
              {groupOrder.filter((group) => groupedModules[group]?.length).map((group) => {
                const detail = GROUP_DETAILS[group];
                return (
                  <section key={group} className="ar-panel rounded-[28px] p-6">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="ar-badge">{detail.eyebrow}</p>
                        <h3 className="mt-3 font-[Space_Grotesk] text-2xl font-bold tracking-tight text-slate-950">{group}</h3>
                      </div>
                      <div className="h-12 w-12 rounded-2xl" style={{ background: detail.accent }} />
                    </div>
                    <p className="mt-4 text-sm leading-7 text-slate-600">{detail.title}</p>
                    <p className="mt-3 text-sm leading-7 text-slate-500">{detail.description}</p>
                    <div className="mt-5 grid gap-3">
                      {groupedModules[group].slice(0, 3).map((app) => {
                        const canUse = hasAccess(app.key);
                        return (
                          <button
                            key={app.key}
                            type="button"
                            onClick={() => openModule(app)}
                            disabled={!canUse}
                            className="flex items-center justify-between rounded-[20px] border border-slate-200 bg-white px-4 py-3 text-left transition hover:-translate-y-0.5 hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-55"
                          >
                            <span>
                              <span className="block text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{app.chip}</span>
                              <span className="mt-1 block font-[Space_Grotesk] text-base font-bold text-slate-950">{app.name}</span>
                            </span>
                            <ArrowRight size={16} className={canUse ? 'text-slate-500' : 'text-slate-300'} />
                          </button>
                        );
                      })}
                    </div>
                  </section>
                );
              })}
            </aside>
          </div>
        </main>
      </div>
    </div>
  );
};

export default LaunchModulesPage;
