// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (CloudRecommendationsPanel.jsx)
// Date: 2026-01-06
// ---------------------------------------------------------------------------
import React from 'react'
import { motion } from 'framer-motion'
import { Cloud, Shield, Database, Cpu, Globe, Brain, Box, Zap, BarChart2 } from 'lucide-react'

const CATEGORY_META = {
  'Security & Identity': {
    icon: Shield,
    color: 'text-purple-400',
    bg: 'bg-purple-900/20',
    border: 'border-purple-700/30',
    hdr: 'bg-purple-900/40',
  },
  Container: {
    icon: Box,
    color: 'text-blue-400',
    bg: 'bg-blue-900/20',
    border: 'border-blue-700/30',
    hdr: 'bg-blue-900/40',
  },
  Integration: {
    icon: Zap,
    color: 'text-yellow-400',
    bg: 'bg-yellow-900/20',
    border: 'border-yellow-700/30',
    hdr: 'bg-yellow-900/40',
  },
  Storage: {
    icon: Database,
    color: 'text-cyan-400',
    bg: 'bg-cyan-900/20',
    border: 'border-cyan-700/30',
    hdr: 'bg-cyan-900/40',
  },
  Databases: {
    icon: Database,
    color: 'text-green-400',
    bg: 'bg-green-900/20',
    border: 'border-green-700/30',
    hdr: 'bg-green-900/40',
  },
  'AI + Machine Learning': {
    icon: Brain,
    color: 'text-fuchsia-400',
    bg: 'bg-fuchsia-900/20',
    border: 'border-fuchsia-700/30',
    hdr: 'bg-fuchsia-900/40',
  },
  Web: {
    icon: Globe,
    color: 'text-sky-400',
    bg: 'bg-sky-900/20',
    border: 'border-sky-700/30',
    hdr: 'bg-sky-900/40',
  },
  Compute: {
    icon: Cpu,
    color: 'text-orange-400',
    bg: 'bg-orange-900/20',
    border: 'border-orange-700/30',
    hdr: 'bg-orange-900/40',
  },
  Analytics: {
    icon: BarChart2,
    color: 'text-teal-400',
    bg: 'bg-teal-900/20',
    border: 'border-teal-700/30',
    hdr: 'bg-teal-900/40',
  },
}

// Function: CategoryCard
function CategoryCard({ category, services, index }) {
  const meta = CATEGORY_META[category] || {
    icon: Cloud, color: 'text-blue-400', bg: 'bg-gray-800/20',
    border: 'border-gray-700/30', hdr: 'bg-gray-800/40',
  }
  const Icon = meta.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      className={`rounded-xl border ${meta.border} ${meta.bg} overflow-hidden`}
    >
      {/* Header */}
      <div className={`${meta.hdr} px-4 py-2.5 flex items-center justify-between border-b ${meta.border}`}>
        <div className="flex items-center gap-2">
          <Icon size={14} className={meta.color} />
          <span className={`text-sm font-semibold ${meta.color}`}>{category}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-blue-500">{category === 'Databases' || category === 'Compute' ? 'Services' : category} Services</span>
          <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${meta.bg} ${meta.color} border ${meta.border}`}>
            Total Apps: {services.reduce((s, e) => s + e.count, 0)}
          </span>
        </div>
      </div>

      {/* Services list */}
      <div className="divide-y divide-gray-800/50">
        {services.map((entry, i) => (
          <div key={entry.service} className="flex items-center justify-between px-4 py-2.5 hover:bg-white/[0.02] transition-colors">
            <div className="flex items-center gap-2.5 min-w-0">
              <span className="text-sm text-blue-200 truncate">{entry.service}</span>
              {entry.reason && (
                <span className="text-[10px] text-blue-600 hidden lg:block truncate max-w-48"
                      title={entry.reason}>
                  {entry.reason}
                </span>
              )}
            </div>
            <span className={`ml-2 text-xs font-bold ${meta.color} flex-shrink-0`}>
              {entry.count}
            </span>
          </div>
        ))}
        {/* Grand Total */}
        <div className="flex items-center justify-between px-4 py-2 bg-gray-900/30">
          <span className="text-sm font-semibold text-blue-300">Grand Total</span>
          <span className={`text-sm font-bold ${meta.color}`}>
            {services.reduce((s, e) => s + e.count, 0)}
          </span>
        </div>
      </div>
    </motion.div>
  )
}

// Function: CloudRecommendationsPanel
export default function CloudRecommendationsPanel({ cloudRecs }) {
  if (!cloudRecs?.by_category || Object.keys(cloudRecs.by_category).length === 0) {
    return (
      <div className="py-16 text-center text-blue-500">
        <Cloud size={32} className="mx-auto mb-3 opacity-40" />
        <p>No cloud service recommendations available. Re-run analysis to generate recommendations.</p>
      </div>
    )
  }

  const { by_category, total_services, detected_triggers } = cloudRecs
  const categories = Object.keys(by_category)

  return (
    <div className="space-y-5">
      {/* Title */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-base font-semibold text-blue-300 flex items-center gap-2">
            <Cloud size={16} className="text-blue-400" />
            Cloud Service Recommendation Summary
          </h3>
          <p className="text-xs text-blue-500 mt-0.5">
            Based on detected technologies, frameworks, and dependencies in this repository.
          </p>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-blue-400">{total_services}</div>
          <div className="text-xs text-blue-500">Azure Services recommended</div>
        </div>
      </div>

      {/* Triggers */}
      {detected_triggers?.length > 0 && (
        <div className="flex flex-wrap gap-2 p-3 rounded-xl bg-gray-900/40 border border-surface-border">
          <span className="text-xs text-blue-500 mr-1">Detected signals:</span>
          {detected_triggers.slice(0, 12).map(t => (
            <span key={t} className="px-2 py-0.5 rounded bg-gray-800 text-blue-300 text-[10px] border border-gray-700">
              {t}
            </span>
          ))}
          {detected_triggers.length > 12 && (
            <span className="text-xs text-blue-600">+{detected_triggers.length - 12} more</span>
          )}
        </div>
      )}

      {/* Category cards grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {categories.map((cat, i) => (
          <CategoryCard
            key={cat}
            category={cat}
            services={by_category[cat]}
            index={i}
          />
        ))}
      </div>

      {/* Logos strip (Azure service icons) */}
      <div className="flex flex-wrap gap-4 justify-center py-4 opacity-40">
        {[
          'Azure Kubernetes Service (AKS)',
          'Azure Database for PostgreSQL',
          'Azure Cosmos DB',
        ].filter(s => Object.values(by_category).flat().some(e => e.service === s)).map(s => (
          <span key={s} className="text-[10px] text-blue-600 px-2 py-1 rounded border border-gray-800">
            {s}
          </span>
        ))}
      </div>
    </div>
  )
}
