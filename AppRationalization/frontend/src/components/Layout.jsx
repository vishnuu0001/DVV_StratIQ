// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components (Layout.jsx)
// Date: 2026-05-01
// ---------------------------------------------------------------------------
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ChevronDown, ClipboardList, Home, LogOut, Map as MapIcon, ShieldCheck } from 'lucide-react';

import { useAuth } from '../context/AuthContext';

/* ── Chevron SVG ── */
// Function: Chevron
const Chevron = ({ open }) => (
  <ChevronDown size={14} className={`text-slate-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
);

// Function: Layout
const Layout = ({ children }) => {
  const [expandedSections, setExpandedSections] = useState({
    baseline: false,
    cast: false,
    correlation: false,
    capability: false,
    industry: false,
    technicalEvaluation: false,
    technicalAssessment: false,
  });
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const basePath = '/app-rationalization';
  // Function: route
  const route = (suffix = '') => `${basePath}${suffix}`;

  // Function: toggleSection
  const toggleSection = (section) =>
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));

  // Function: isActive
  const isActive = (suffix = '') => location.pathname === route(suffix);
  // Function: isUnder
  const isUnder = (suffix) => location.pathname.startsWith(route(suffix));

  // Function: handleLogout
  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  // Function: handlePortalHome
  const handlePortalHome = () => {
    navigate('/launch-modules');
  };

  // Function: handleAdminConsole
  const handleAdminConsole = () => {
    navigate('/admin');
  };

  /* ── reusable style helpers ── */
  // Function: navItem
  const navItem = (active) => 'az-nav-group-btn';

  // Function: sectionBtn
  const sectionBtn = (active) => 'az-nav-group-btn';

  // Function: subItem
  const subItem = (active) => 'az-nav-subitem';

  // Function: sectionLabel
  const sectionLabel = (text) => <p className="az-nav-section-label">{text}</p>;

  return (
    <div className="az-shell flex h-screen">
      {/* ── Sidebar ── */}
      <div className="az-side-nav">

        {/* Logo / Brand */}
        <div className="az-side-nav-header">
          <p className="az-side-nav-brand">App Rationalization Platform</p>
          <div className="az-side-nav-meta">
            <p>User: <b>{user?.username}</b></p>
            <p className="mt-1">Manufacturing modernization workspace</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-2">

          {false && (
          <>
          {/* ── DATA COLLECTION ── */}
          {sectionLabel('Data Collection')}

          {/* Infra Discovery */}
          <div>
            <button onClick={() => toggleSection('baseline')} className={sectionBtn(isUnder('/upload'))}>
              <svg className="w-4 h-4 shrink-0 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
              <span className="flex-1 text-left">Infra Discovery</span>
              <Chevron open={expandedSections.baseline} />
            </button>
            {expandedSections.baseline && (
              <Link to={route('/upload')} className={subItem(isActive('/upload'))}>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                Strat-Aqorynth Infra Analysis
              </Link>
            )}
          </div>

          {/* App Insights */}
          <div>
            <button onClick={() => toggleSection('cast')} className={sectionBtn(isUnder('/cast-analysis'))}>
              <svg className="w-4 h-4 shrink-0 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
              <span className="flex-1 text-left">App Insights</span>
              <Chevron open={expandedSections.cast} />
            </button>
            {expandedSections.cast && (
              <Link to={route('/cast-analysis')} className={subItem(isActive('/cast-analysis'))}>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                Strat-Aqorynth Code Analysis
              </Link>
            )}
          </div>

          {/* Templates */}
          <div>
            <button onClick={() => toggleSection('industry')} className={sectionBtn(isUnder('/industry-templates'))}>
              <svg className="w-4 h-4 shrink-0 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span className="flex-1 text-left">Business Templates</span>
              <Chevron open={expandedSections.industry} />
            </button>
            {expandedSections.industry && (
              <Link to={route('/industry-templates')} className={subItem(isActive('/industry-templates'))}>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                Template Upload
              </Link>
            )}
          </div>

          </>
          )}

          {/* ── ANALYSIS ── */}
          {sectionLabel('Analysis')}

          {/* Technical Evaluation */}
          <div>
            <button
              onClick={() => toggleSection('technicalEvaluation')}
              className={sectionBtn(isUnder('/technical-evaluation'))}
              data-active={isUnder('/technical-evaluation')}
            >
              <ClipboardList size={16} className="shrink-0 text-blue-600" />
              <span className="flex-1 text-left">Technical Evaluation</span>
              <Chevron open={expandedSections.technicalEvaluation} />
            </button>
            {expandedSections.technicalEvaluation && (
              <>
                <Link
                  to={route('/technical-evaluation/categorize')}
                  className={subItem(isActive('/technical-evaluation/categorize'))}
                  data-active={isActive('/technical-evaluation/categorize')}
                >
                  Categorize
                </Link>
                <Link
                  to={route('/technical-evaluation/validate')}
                  className={subItem(isActive('/technical-evaluation/validate'))}
                  data-active={isActive('/technical-evaluation/validate')}
                >
                  Validate
                </Link>
              </>
            )}
          </div>

          {/* Technical Assessment */}
          <div>
            <button
              onClick={() => toggleSection('technicalAssessment')}
              className={sectionBtn(isUnder('/technical-assessment'))}
              data-active={isUnder('/technical-assessment')}
            >
              <ClipboardList size={16} className="shrink-0 text-violet-600" />
              <span className="flex-1 text-left">Technical Assessment</span>
              <Chevron open={expandedSections.technicalAssessment} />
            </button>
            {expandedSections.technicalAssessment && (
              <>
                <Link
                  to={route('/technical-assessment/business-validations')}
                  className={subItem(isActive('/technical-assessment/business-validations'))}
                  data-active={isActive('/technical-assessment/business-validations')}
                >
                  Business Validations
                </Link>
                <Link
                  to={route('/technical-assessment/wave-inputs')}
                  className={subItem(isActive('/technical-assessment/wave-inputs'))}
                  data-active={isActive('/technical-assessment/wave-inputs')}
                >
                  Wave Inputs
                </Link>
              </>
            )}
          </div>

          {false && (
          <>
          {/* Insights Link */}
          <div>
            <button onClick={() => toggleSection('correlation')} className={sectionBtn(isUnder('/correlation'))}>
              <svg className="w-4 h-4 shrink-0 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span className="flex-1 text-left">Insights Link</span>
              <Chevron open={expandedSections.correlation} />
            </button>
            {expandedSections.correlation && (
              <Link to={route('/correlation')} className={subItem(isActive('/correlation'))}>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                Correlation & Analysis
              </Link>
            )}
          </div>

          {/* Golden Data */}
          <div className="px-0">
            <Link to={route('/golden-data')} className={navItem(isActive('/golden-data'))}>
              <svg className="w-4 h-4 shrink-0 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
              Golden Data
            </Link>
          </div>

          </>
          )}

          {/* ── OUTCOMES ── */}
          {sectionLabel('Outcomes')}

          {/* Capability Map */}
          <div>
            <button
              onClick={() => toggleSection('capability')}
              className={sectionBtn(isUnder('/capability') || isActive('/technical-assessment/wave-planning'))}
              data-active={isUnder('/capability') || isActive('/technical-assessment/wave-planning')}
            >
              <MapIcon size={16} className="shrink-0 text-emerald-600" />
              <span className="flex-1 text-left">Capability Map</span>
              <Chevron open={expandedSections.capability || isActive('/technical-assessment/wave-planning')} />
            </button>
            {(expandedSections.capability || isActive('/technical-assessment/wave-planning')) && (
              <Link
                to={route('/technical-assessment/wave-planning')}
                className={subItem(isActive('/technical-assessment/wave-planning'))}
                data-active={isActive('/technical-assessment/wave-planning')}
              >
                Wave Planning
              </Link>
            )}
          </div>

        </nav>

        {/* Footer */}
        <div className="az-side-nav-footer">v1.0 · App Rationalization Platform</div>
      </div>

      {/* ── Main Content ── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="az-topbar">
          <div className="az-logo-mark">
            <Home size={15} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="az-topbar-eyebrow">Unified Modernization Suite</p>
            <p className="az-topbar-title">App Rationalization Workspace</p>
          </div>
          <span className="az-topbar-user">{user?.username}</span>
          <button type="button" onClick={handlePortalHome} className="az-topbar-btn">
            Portal Home
          </button>
          {user?.role === 'admin' && (
            <button type="button" onClick={handleAdminConsole} className="az-topbar-btn">
              <ShieldCheck size={13} />
              Admin Console
            </button>
          )}
          <button type="button" onClick={handleLogout} className="az-topbar-btn">
            <LogOut size={13} />
            Logout
          </button>
        </header>
        <div className="az-workspace-main flex-1 overflow-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;
