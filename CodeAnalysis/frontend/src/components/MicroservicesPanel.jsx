// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * MicroservicesPanel.jsx — Microservices decomposition with charts
// Date: 2025-11-27
// ---------------------------------------------------------------------------
/**
 * MicroservicesPanel.jsx — Microservices decomposition with charts
 */
import { useState } from 'react'
import { Network, ArrowRight, Package, Database, AlertCircle, BarChart2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import AIDetailModal from './AIDetailModal.jsx'

const API_COLORS = {
  REST:           'bg-blue-100 text-blue-700',
  gRPC:           'bg-purple-100 text-purple-700',
  'event-driven': 'bg-orange-100 text-orange-700',
  GraphQL:        'bg-pink-100 text-pink-700',
}
const API_HEX = { REST: '#3b82f6', gRPC: '#8b5cf6', 'event-driven': '#f97316', GraphQL: '#ec4899' }

// Function: TIP
const TIP = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow px-3 py-2 text-xs">
      <p className="font-semibold text-blue-700 mb-1">{label}</p>
      {payload.map((p, i) => <p key={i} style={{ color: p.fill || p.color }}>{p.name}: <strong>{p.value}</strong></p>)}
    </div>
  )
}

// Function: MicroservicesPanel
export default function MicroservicesPanel({ data }) {
  if (!data) return null
  if (data.error) return <div className="bg-white rounded-2xl shadow p-6 text-red-500 text-sm">{data.error}</div>

  const services = data.microservices      || []
  const phases   = (data.modernisation_phases && data.modernisation_phases.length > 0)
    ? data.modernisation_phases
    : (services.length > 0 && data.migration_timeline_weeks
        ? [{
            phase: 1,
            title: 'Microservices rollout',
            items: services.map(s => s.name).filter(Boolean),
            duration_months: Math.max(1, Math.round((Number(data.migration_timeline_weeks) || 0) / 4)),
            milestone: 'Initial service extraction complete',
            _panelColor: 'sky',
          }]
        : [])
  const risks    = data.risks               || []

  const [modal, setModal] = useState(null)
  // Function: openServices
  const openServices = (filterFn, label) =>
    setModal({ type: 'service', title: label, items: filterFn ? services.filter(filterFn) : services })
  // Function: openPhases
  const openPhases = () =>
    setModal({ type: 'phase', title: 'Modernisation Phases', items: phases.map(p => ({ ...p, _panelColor: 'sky' })) })

  // Service size bar
  const sizeData = services
    .filter(s => s.estimated_size_kloc)
    .map(s => ({
      name: s.name?.slice(0, 18) || '?',
      kloc: parseFloat(s.estimated_size_kloc) || 0,
      deps: (s.dependencies || []).length,
      fill: API_HEX[s.api_type] || '#6366f1',
      _original: s,
    }))

  // API type donut
  const apiCounts = services.reduce((a, s) => { a[s.api_type || 'REST'] = (a[s.api_type || 'REST'] || 0) + 1; return a }, {})
  const apiPie = Object.entries(apiCounts).map(([name, value]) => ({
    name, value, color: API_HEX[name] || '#94a3b8'
  }))

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">

      {/* Header */}
      <div className="bg-white rounded-2xl shadow p-6">
        <div className="flex items-center gap-2 mb-3">
          <Network size={18} className="text-violet-600" />
          <h3 className="font-semibold text-blue-800">Microservices Decomposition</h3>
          {data.decomposition_strategy && (
            <span className="ml-auto text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded font-semibold">
              {data.decomposition_strategy.replace(/-/g, ' ')}
            </span>
          )}
        </div>
        <p className="text-sm text-blue-700">{data.summary}</p>
        {data.data_store_strategy && (
          <div className="mt-3 p-3 bg-violet-50 rounded-xl text-sm text-violet-800">
            <Database size={13} className="inline mr-1" />
            <strong>Data Strategy:</strong> {data.data_store_strategy}
          </div>
        )}

        {/* Stat row */}
        <div className="mt-4 grid grid-cols-3 gap-3">
          <button onClick={() => openServices(null, 'All Services')} className="bg-violet-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-violet-300 transition-all">
            <div className="text-2xl font-bold text-violet-600">{services.length}</div>
            <div className="text-xs text-blue-500 mt-1">Services</div>
          </button>
          <button onClick={openPhases} className="bg-blue-50 rounded-xl p-3 text-center w-full hover:ring-2 hover:ring-blue-300 transition-all">
            <div className="text-2xl font-bold text-blue-600">{phases.length}</div>
            <div className="text-xs text-blue-500 mt-1">Phases</div>
          </button>
          <div className="bg-orange-50 rounded-xl p-3 text-center">
            <div className="text-2xl font-bold text-orange-600">{risks.length}</div>
            <div className="text-xs text-blue-500 mt-1">Risks</div>
          </div>
        </div>
      </div>

      {/* Charts row */}
      {(sizeData.length > 0 || apiPie.length > 1) && (
        <div className="grid md:grid-cols-3 gap-5">
          {sizeData.length > 0 && (
            <div className="md:col-span-2 bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <BarChart2 size={14} className="text-violet-500" /> Service Size (kLOC) &amp; Deps
              </h3>
              <ResponsiveContainer width="100%" height={210}>
                <BarChart data={sizeData} margin={{ left: 0, right: 16, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <Tooltip content={<TIP />} />
                  <Bar dataKey="kloc" name="kLOC" radius={[4, 4, 0, 0]} maxBarSize={40}
                    onClick={(d) => d._original && setModal({ type: 'service', title: d.name, items: services, initialItem: d._original })} style={{ cursor: 'pointer' }}>
                    {sizeData.map((e, i) => <Cell key={i} fill={e.fill} fillOpacity={0.85} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {apiPie.length > 0 && (
            <div className="bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold text-blue-800 text-sm mb-4 flex items-center gap-2">
                <Network size={14} className="text-violet-500" /> API Types
              </h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={apiPie} cx="50%" cy="44%" innerRadius={48} outerRadius={72} paddingAngle={3} dataKey="value"
                    onClick={(d) => openServices(s => (s.api_type || 'REST') === d.name, `${d.name} Services`)}
                    style={{ cursor: 'pointer' }}>
                    {apiPie.map((e, i) => <Cell key={i} fill={e.color} />)}
                  </Pie>
                  <Tooltip formatter={(v, n) => [v + ' services', n]} />
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Services */}
      {services.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Package size={16} className="text-violet-500" />
            <h3 className="font-semibold text-blue-800">Service Candidates ({services.length})</h3>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            {services.map((s, i) => (
              <button key={i} onClick={() => setModal({ type: 'service', title: s.name, items: services, initialItem: s })}
                className="w-full text-left border border-violet-100 rounded-xl p-4 bg-violet-50/30 hover:bg-violet-100/60 hover:shadow-sm transition-all">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-violet-600 text-blue-300 text-xs font-bold flex items-center justify-center shrink-0">
                        {s.migration_order || i + 1}
                      </span>
                      <span className="font-semibold text-sm text-blue-800">{s.name}</span>
                    </div>
                  </div>
                  {s.api_type && (
                    <span className={`text-xs px-2 py-0.5 rounded font-semibold shrink-0 ${API_COLORS[s.api_type] || 'bg-gray-100 text-blue-600'}`}>
                      {s.api_type}
                    </span>
                  )}
                </div>
                <p className="text-xs text-blue-600 mb-2">{s.responsibility}</p>
                {(s.current_tech || s.suggested_tech_stack) && (
                  <p className="text-xs text-blue-600 mb-1">
                    <strong>Current:</strong> {s.current_tech || 'unknown'}
                  </p>
                )}
                {s.suggested_tech_stack && (
                  <p className="text-xs text-indigo-700 mb-1">
                    <strong>→ Target:</strong> {s.suggested_tech_stack}
                  </p>
                )}
                {s.estimated_size_kloc && (
                  <p className="text-xs text-blue-500">~{s.estimated_size_kloc} kLOC</p>
                )}
                {(s.dependencies || []).length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {s.dependencies.map((d, j) => (
                      <span key={j} className="flex items-center gap-0.5 text-xs bg-gray-100 text-blue-600 px-1.5 py-0.5 rounded">
                        <ArrowRight size={10}/>{d}
                      </span>
                    ))}
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Risks */}
      {risks.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-5">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle size={15} className="text-orange-500" />
            <h3 className="font-semibold text-blue-700 text-sm">Migration Risks</h3>
          </div>
          <ul className="space-y-1">
            {risks.map((r, i) => (
              <li key={i} className="text-sm text-blue-600 flex gap-2">
                <span className="text-orange-400 shrink-0 mt-0.5">⚠</span>{r}
              </li>
            ))}
          </ul>
        </div>
      )}
      <AnimatePresence>
        {modal && <AIDetailModal {...modal} onClose={() => setModal(null)} />}
      </AnimatePresence>
    </motion.div>
  )
}
