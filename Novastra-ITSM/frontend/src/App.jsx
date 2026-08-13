// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src (App.jsx)
// Date: 2025-09-01
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { Routes, Route, NavLink, Navigate, useNavigate, useLocation } from 'react-router-dom'
import {
  Bot, Settings, Shield, Ticket, BarChart2, MessageSquare, LayoutDashboard,
  Plus, Trash2, ChevronDown, ChevronUp, Database, Network, FileSpreadsheet, BrainCircuit,
  LogOut, User, Home, X, Tag, Zap, BookOpen, TrendingUp, Search, Heart, ShieldCheck, BarChart3, Languages,
  GitBranch, Lock, Layers, MonitorDot,
} from 'lucide-react'
import { clsx } from 'clsx'

const PORTAL_HOME_URL = import.meta.env.VITE_PORTAL_HOME_URL || '/launch-modules'
const PORTAL_LOGIN_URL = import.meta.env.VITE_PORTAL_LOGIN_URL || '/login'

import ChatPage           from './pages/ChatPage.jsx'
import ServiceNowPage     from './pages/ServiceNowPage.jsx'
import AdminPage          from './pages/AdminPage.jsx'
import SettingsPage       from './pages/SettingsPage.jsx'
import FeedbackPage       from './pages/FeedbackPage.jsx'
import TicketAnalysisPage from './pages/TicketAnalysisPage.jsx'
import AIAssessmentPage  from './pages/AIAssessmentPage.jsx'
import LaunchModulesPage  from './pages/LaunchModulesPage.jsx'
import LoginPage          from './pages/LoginPage.jsx'
import DataSourcesPage    from './pages/DataSourcesPage.jsx'
import KnowledgeGraphPage      from './pages/KnowledgeGraphPage.jsx'
import TicketIntelligencePage  from './pages/TicketIntelligencePage.jsx'
import VirtualAgentPage        from './pages/VirtualAgentPage.jsx'
import KnowledgeMgmtPage       from './pages/KnowledgeMgmtPage.jsx'
import PredictivePage          from './pages/PredictivePage.jsx'
import AutomationPage          from './pages/AutomationPage.jsx'
import RCAPage                 from './pages/RCAPage.jsx'
import SentimentPage           from './pages/SentimentPage.jsx'
import CMDBPage                from './pages/CMDBPage.jsx'
import ReportsPage             from './pages/ReportsPage.jsx'
import CompliancePage          from './pages/CompliancePage.jsx'
import EventCorrelationPage    from './pages/EventCorrelationPage.jsx'
import GovernancePage          from './pages/GovernancePage.jsx'
import NovastraItsmHomePage              from './pages/NovastraItsmHomePage.jsx'
import ITSMDashboardPage       from './pages/ITSMDashboardPage.jsx'
import OmnichannelPage         from './pages/OmnichannelPage.jsx'
import UnifiedTopMenu          from './components/UnifiedTopMenu.jsx'
import ProtectedRoute     from './components/ProtectedRoute.jsx'
import { useChatContext } from './contexts/ChatContext.jsx'
import { useAuth }        from './contexts/AuthContext.jsx'
import { TicketProvider } from './context/TicketContext.jsx'

const MODULE_HOME_ROUTE = '/home'

const PRIMARY_NAV = [
  { to: '/ticket-analysis',     label: 'Ticket Analysis',    icon: FileSpreadsheet },
  { to: '/ai-assessment',       label: 'AI Assessment',      icon: BrainCircuit    },
  { to: '/knowledge-graph',     label: 'Knowledge Graph',    icon: Network         },
  { to: '/ticket-intelligence', label: 'Ticket Intelligence',icon: Tag             },
  { to: '/virtual-agent',       label: 'Virtual Agent',      icon: Bot             },
  { to: '/knowledge-mgmt',      label: 'Knowledge Mgmt',     icon: BookOpen        },
  { to: '/predictive',          label: 'Predictive AIOps',   icon: TrendingUp      },
  { to: '/automation',          label: 'Automation',         icon: Zap             },
  { to: '/rca',                 label: 'Root Cause Analysis',icon: Search          },
  { to: '/sentiment',           label: 'Sentiment Analysis', icon: Heart           },
  { to: '/cmdb',                label: 'CMDB Intelligence',  icon: Database        },
  { to: '/reports',             label: 'Reports & Insights', icon: BarChart3       },
  { to: '/compliance',          label: 'Compliance',         icon: ShieldCheck     },
  { to: '/event-correlation',   label: 'Event Correlation',  icon: GitBranch       },
  { to: '/governance',          label: 'Governance',         icon: Lock            },
  { to: '/itsm-dashboard',      label: 'ITSM Dashboard',     icon: MonitorDot      },
  { to: '/omnichannel',         label: 'Omnichannel Intake', icon: Layers          },
]

const SECONDARY_NAV = [
  { to: '/servicenow', label: 'ServiceNow', icon: Ticket    },
  { to: '/admin',      label: 'Admin',      icon: Shield    },
  { to: '/feedback',   label: 'Feedback',   icon: BarChart2 },
  { to: '/settings',   label: 'Settings',   icon: Settings  },
]

// Function: groupSessions
function groupSessions(sessions) {
  const now       = new Date()
  const today     = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 86_400_000)
  const weekAgo   = new Date(today.getTime() - 7 * 86_400_000)

  const buckets = { today: [], yesterday: [], week: [], older: [] }
  sessions.forEach((s) => {
    const d = new Date(s.createdAt)
    if (d >= today)          buckets.today.push(s)
    else if (d >= yesterday) buckets.yesterday.push(s)
    else if (d >= weekAgo)   buckets.week.push(s)
    else                     buckets.older.push(s)
  })
  return [
    { label: 'Today',           items: buckets.today },
    { label: 'Yesterday',       items: buckets.yesterday },
    { label: 'Previous 7 Days', items: buckets.week },
    { label: 'Older',           items: buckets.older },
  ].filter((g) => g.items.length > 0)
}

// Function: AppShell
function AppShell() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  const {
    sessions, activeSessionId, setActiveSessionId,
    startNewChat, deleteSession,
    selectedModel, serverSettings, changeModel,
  } = useChatContext()

  const [modelOpen, setModelOpen] = useState(false)
  const [historyPopupSession, setHistoryPopupSession] = useState(null)

  const groups = groupSessions(sessions)

  // Function: handleNewChat
  const handleNewChat = () => {
    startNewChat()
    navigate('/chat')
  }

  // Function: handleSelectSession
  const handleSelectSession = (id) => {
    const session = sessions.find((s) => s.id === id)
    if (session) setHistoryPopupSession(session)
  }

  // Function: handleLogout
  const handleLogout = async () => {
    await logout()
    window.location.href = PORTAL_LOGIN_URL
  }

  // Function: handlePortalHome
  const handlePortalHome = () => {
    window.location.href = PORTAL_HOME_URL
  }

  // Function: portalAdminUrl
  const portalAdminUrl = (() => { try { return new URL('/admin', PORTAL_HOME_URL).href } catch { return '/admin' } })()
  const workspaceTitle = location.pathname.startsWith('/launch-modules')
    ? 'Open the right workspace for the next decision'
    : 'Novastra ITSM Workspace'

  const modelLabel = selectedModel === 'openai'
    ? `OpenAI · ${serverSettings?.openai_model || 'gpt-4o'}`
    : `Ollama · ${serverSettings?.ollama_model || 'llama3'}`

  return (
    <div className="novastra-azure-shell">
      <UnifiedTopMenu
        workspaceTitle={workspaceTitle}
        username={user?.display_name || user?.username}
        portalHomeUrl={PORTAL_HOME_URL}
        portalAdminUrl={portalAdminUrl}
        onLogout={handleLogout}
      />

      <div className="novastra-azure-body">
      {/* ── Sidebar ── */}
      <aside className="az-side-nav">

        {/* Header */}
        <div className="az-side-nav-header">
          <button onClick={() => navigate('/home')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="az-logo-mark">
              <Bot size={15} />
            </div>
            <div className="text-left">
              <p className="az-side-nav-brand">Novastra ITSM</p>
              <p className="az-side-nav-sub">17 AI-powered capabilities</p>
            </div>
          </button>
          <button
            onClick={handleNewChat}
            title="New Chat"
            className="p-1.5 rounded-sm text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            <Plus size={17} />
          </button>
        </div>

        {/* Primary nav */}
        <nav className="pt-2 pb-1 overflow-y-auto" style={{ borderBottom: '1px solid #edebe9', maxHeight: '42vh' }}>
          {PRIMARY_NAV.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className="az-navf-item">
              <Icon size={13} />
              <span className="az-nav-label flex-1 truncate">{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto py-2">

          {groups.length === 0 ? (
            <div className="px-3 py-6 text-center">
              <p className="text-xs text-slate-500">No conversations yet.</p>
              <p className="text-[10px] text-slate-400 mt-1">Click + to start a new chat.</p>
            </div>
          ) : (
            groups.map((group) => (
              <div key={group.label} className="mb-3">
                <p className="px-3 py-1 text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
                  {group.label}
                </p>
                {group.items.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => handleSelectSession(session.id)}
                    className={clsx(
                      'group flex items-center gap-2 px-2 py-2 mx-1 rounded-sm cursor-pointer transition-colors',
                      session.id === activeSessionId
                        ? 'bg-[#eff6fc] text-[#0078d4]'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                    )}
                  >
                    <MessageSquare size={13} className="flex-shrink-0 text-slate-400" />
                    <span className="flex-1 truncate text-xs leading-snug">{session.title}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteSession(session.id) }}
                      title="Delete"
                      className="opacity-0 group-hover:opacity-100 p-0.5 rounded-sm text-slate-400 hover:text-red-600 transition-all shrink-0"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            ))
          )}
        </div>

        {/* Bottom section */}
        <div className="az-side-nav-footer">

          {/* Secondary nav */}
          <nav className="py-1">
            {SECONDARY_NAV.map(({ to, label, icon: Icon }) => (
              <NavLink key={to} to={to} className="az-navf-item">
                <Icon size={14} />
                <span className="az-nav-label">{label}</span>
              </NavLink>
            ))}
          </nav>

          {/* Model Selector */}
          <div className="px-2 py-2 relative" style={{ borderTop: '1px solid #edebe9' }}>
            <button onClick={() => setModelOpen((p) => !p)} className="az-model-btn">
              <div className="flex items-center gap-2 min-w-0">
                <Bot size={13} className="text-[#0078d4] shrink-0" />
                <span className="font-medium truncate">{modelLabel}</span>
              </div>
              {modelOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>

            {modelOpen && (
              <div className="absolute bottom-full left-2 right-2 mb-1 bg-white border rounded-sm shadow-lg z-50 overflow-hidden" style={{ borderColor: '#edebe9' }}>
                <div className="p-2">
                  <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide px-2 pb-1.5">
                    Switch Model
                  </p>
                  {[
                    { id: 'ollama', label: 'Ollama (Open-Source)', sub: serverSettings?.ollama_model || 'llama3' },
                    { id: 'openai', label: 'OpenAI',               sub: serverSettings?.openai_model  || 'gpt-4o' },
                  ].map((m) => (
                    <button
                      key={m.id}
                      onClick={() => { changeModel(m.id); setModelOpen(false) }}
                      className={clsx(
                        'w-full flex items-center gap-3 px-3 py-2.5 rounded-sm text-left transition-colors',
                        selectedModel === m.id
                          ? 'bg-[#eff6fc] text-[#0078d4]'
                          : 'text-slate-700 hover:bg-slate-100'
                      )}
                    >
                      <Bot size={14} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold">{m.label}</p>
                        <p className="text-[10px] text-slate-500">{m.sub}</p>
                      </div>
                      {selectedModel === m.id && <span className="text-xs">✓</span>}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* User info + logout */}
          <div className="az-user-footer">
            <div className="w-7 h-7 rounded-full bg-[#0078d4] flex items-center justify-center shrink-0 text-xs font-bold text-white overflow-hidden">
              {user?.avatar_url
                ? <img src={user.avatar_url} alt="" className="w-full h-full object-cover" />
                : (user?.display_name?.[0] || user?.username?.[0] || <User size={13} />)
              }
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-900 truncate">
                {user?.display_name || user?.username}
              </p>
              <p className="text-[10px] text-slate-500 capitalize">{user?.role}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="p-1 rounded-sm text-slate-400 hover:text-red-600 transition-colors"
            >
              <LogOut size={13} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Chat History Popup ────────────────────────────── */}
      {historyPopupSession && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.65)' }}
          onClick={() => setHistoryPopupSession(null)}
        >
          <div
            className="relative bg-white rounded-2xl shadow-2xl flex flex-col"
            style={{ width: '680px', maxWidth: '95vw', maxHeight: '80vh' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Popup Header */}
            <div className="flex items-start justify-between px-5 py-4 border-b border-gray-100 shrink-0">
              <div className="flex-1 min-w-0">
                <p className="text-[10px] uppercase tracking-widest text-gray-400 mb-0.5">Chat History</p>
                <h3 className="text-sm font-semibold text-gray-900 truncate">
                  {historyPopupSession.title}
                </h3>
                <p className="text-[10px] text-gray-400 mt-0.5">
                  {new Date(historyPopupSession.createdAt || historyPopupSession.created_at).toLocaleString()}
                  {' · '}{(historyPopupSession.messages || []).length} messages
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0 ml-3">
                <button
                  onClick={() => setHistoryPopupSession(null)}
                  className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
              {(historyPopupSession.messages || []).length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                  <MessageSquare size={32} strokeWidth={1} className="mb-2" />
                  <p className="text-sm">No messages in this session.</p>
                </div>
              ) : (
                (historyPopupSession.messages || []).map((msg, idx) => (
                  <div key={idx} className={clsx('flex', msg.role === 'human' ? 'justify-end' : 'justify-start')}>
                    <div
                      className={clsx(
                        'max-w-lg rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
                        msg.role === 'human'
                          ? 'bg-blue-600 text-white rounded-br-sm'
                          : 'bg-gray-50 border border-gray-200 text-gray-800 rounded-bl-sm'
                      )}
                    >
                      <p style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{msg.content}</p>
                      {msg.role !== 'human' && msg.confidence !== undefined && (
                        <p className="mt-1.5 text-[10px] text-gray-400">
                          Confidence: {Math.round(msg.confidence * 100)}%
                        </p>
                      )}
                      {msg.role !== 'human' && msg.sources?.length > 0 && (
                        <div className="mt-1.5 flex flex-wrap gap-1">
                          {msg.sources.map((s, si) => (
                            <span key={si} className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-gray-200 text-gray-600 text-[10px] font-mono truncate max-w-[140px]">
                              {typeof s === 'string' ? s : (s.source || s.filename || 'source')}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Main content ──────────────────────────────────── */}
      <main className="novastra-azure-main">
        <div className="novastra-itsm-content flex-1 overflow-hidden flex flex-col">
          <Routes>
            <Route path="/"               element={<Navigate to={MODULE_HOME_ROUTE} replace />} />
            <Route path="/home"           element={<NovastraItsmHomePage />} />
            <Route path="/launch-modules" element={<LaunchModulesPage />} />
            <Route path="/chat"           element={<ChatPage />} />
            <Route path="/datasources"    element={<DataSourcesPage />} />
            <Route path="/ticket-analysis" element={<TicketAnalysisPage />} />
            <Route path="/ai-assessment" element={<AIAssessmentPage />} />
            <Route path="/knowledge-graph"     element={<KnowledgeGraphPage />}     />
            <Route path="/ticket-intelligence" element={<TicketIntelligencePage />} />
            <Route path="/virtual-agent"       element={<VirtualAgentPage />}       />
            <Route path="/knowledge-mgmt"      element={<KnowledgeMgmtPage />}      />
            <Route path="/predictive"          element={<PredictivePage />}         />
            <Route path="/automation"          element={<AutomationPage />}         />
            <Route path="/rca"                 element={<RCAPage />}                />
            <Route path="/sentiment"           element={<SentimentPage />}          />
            <Route path="/cmdb"                element={<CMDBPage />}               />
            <Route path="/reports"             element={<ReportsPage />}            />
            <Route path="/compliance"          element={<CompliancePage />}         />
            <Route path="/event-correlation"   element={<EventCorrelationPage />}   />
            <Route path="/governance"          element={<GovernancePage />}         />
            <Route path="/itsm-dashboard"      element={<ITSMDashboardPage />}      />
            <Route path="/omnichannel"         element={<OmnichannelPage />}        />
            <Route path="/servicenow"     element={<ServiceNowPage />} />
            <Route path="/admin"          element={<AdminPage />} />
            <Route path="/feedback"       element={<FeedbackPage />} />
            <Route path="/settings"       element={<SettingsPage />} />
          </Routes>
        </div>
      </main>
      </div>
    </div>
  )
}

// Function: App
export default function App() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login"          element={<LoginPage />} />
      <Route path="/auth/callback"  element={<LoginPage />} />

      {/* Protected shell  all app routes live inside */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <TicketProvider>
              <AppShell />
            </TicketProvider>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
