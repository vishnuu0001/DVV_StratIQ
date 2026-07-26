// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src/components (Navbar.js)
// Date: 2026-04-05
// ---------------------------------------------------------------------------
import React from 'react';
import { CarFront, Home, LogOut, ShieldCheck } from 'lucide-react';
import { useAuth } from '../AuthContext';

const PORTAL_HOME_URL  = process.env.REACT_APP_PORTAL_HOME_URL  || '/launch-modules';
const PORTAL_LOGIN_URL = process.env.REACT_APP_PORTAL_LOGIN_URL || '/login';

// Function: Navbar
const Navbar = ({ setView, currentView }) => {
  const { resetSelection, logout, user } = useAuth();

  // Helper to apply active styles
  // Function: getLinkClass
  const getLinkClass = (viewName) => {
    const baseClass = "text-xs font-black uppercase tracking-widest transition-all pb-1 border-b-2 ";
    return currentView === viewName
      ? baseClass + "text-brand border-brand"
      : baseClass + "text-gray-400 border-transparent hover:text-brand";
  };

  // Function: handleLogout
  const handleLogout = () => {
    // Clear this module's local auth/session state before redirecting so we
    // don't leave a stale persona selected in the mock AuthContext.
    if (typeof logout === 'function') {
      logout();
    } else {
      resetSelection();
    }
    window.location.href = PORTAL_LOGIN_URL;
  };

  // Function: handleAdminConsole
  const handleAdminConsole = () => {
    let adminUrl = '/admin';
    try {
      adminUrl = new URL('/admin', PORTAL_HOME_URL).href;
    } catch {
      adminUrl = '/admin';
    }
    window.location.href = adminUrl;
  };

  return (
    <nav className="bg-sky-300/85 backdrop-blur-xl border-b border-sky-200/80 py-4 sticky top-0 z-40 h-20 flex items-center">
      <div className="container mx-auto px-6 flex justify-between items-center">
        <div className="flex items-center gap-10">
          {/* Logo takes user back to simulation profile selection */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={resetSelection}>
            <CarFront className="h-8 w-8 text-brand" />
            <div>
              <p className="text-[11px] uppercase tracking-[0.2em] text-white">Unified Modernization Suite</p>
              <h2 className="text-lg font-semibold text-white leading-tight">AI Vehicle Loan Workspace</h2>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-10">
            {/* Nav buttons using the passed setView prop */}
            <button onClick={() => setView('home')} className={getLinkClass('home')}>Home</button>
            <button onClick={() => setView('car-loans')} className={getLinkClass('car-loans')}>Car Loans</button>
            <button onClick={() => setView('how-it-works')} className={getLinkClass('how-it-works')}>How It Works</button>
          </div>
        </div>

        <div className="flex items-center gap-3">
           {user && <span className="text-xs font-bold text-white uppercase tracking-tighter">Active: {user.name}</span>}
           <button
             onClick={() => { window.location.href = PORTAL_HOME_URL; }}
             className="inline-flex items-center gap-1.5 border border-white/45 bg-sky-400/35 text-white text-xs font-bold py-2.5 px-4 rounded-xl transition-all hover:bg-sky-400/55"
           >
             <Home size={13} />
             Portal Home
           </button>
           {!!user && (
             <button
               onClick={handleAdminConsole}
               className="inline-flex items-center gap-1.5 border border-white/45 bg-sky-400/35 text-white text-xs font-bold py-2.5 px-4 rounded-xl transition-all hover:bg-sky-400/55"
             >
               <ShieldCheck size={13} />
               Admin Console
             </button>
           )}
           <button
             onClick={handleLogout}
             className="inline-flex items-center gap-1.5 rounded-xl border border-white/45 bg-sky-400/35 text-white text-xs font-bold py-2.5 px-4 transition-all hover:bg-sky-400/55"
           >
             <LogOut size={13} />
             Logout
           </button>
           <button
             onClick={resetSelection}
             className="bg-brand text-white text-sm font-black py-3 px-8 rounded-xl shadow-lg shadow-brand/20 transition-all hover:scale-105"
           >
             Get Started
           </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;