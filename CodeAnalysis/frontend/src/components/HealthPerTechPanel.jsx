// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (HealthPerTechPanel.jsx)
// Date: 2025-12-23
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { motion } from 'framer-motion'
import { Activity } from 'lucide-react'

const LANG_COLORS = {
  Java:       '#f97316',
  Python:     '#3b82f6',
  '.NET':     '#a855f7',
  JavaScript: '#f59e0b',
  TypeScript: '#06b6d4',
  Mainframe:  '#9ca3af',
}

const INDUSTRY_BENCHMARKS = {
  resiliency: 73.68,
  agility:    62.44,
  elegance:   55.21,
}

// Function: RiskChip
function RiskChip({ risk }) {
  const map = {
    EXCELLENT: 'bg-green-900/50 text-green-300 border-green-700/40',
    GOOD:      'bg-teal-900/50 text-teal-300 border-teal-700/40',
    FAIR:      'bg-amber-900/50 text-amber-300 border-amber-700/40',
    'HIGH RISK': 'bg-red-900/50 text-red-300 border-red-700/40',
    CRITICAL:  'bg-red-900/50 text-red-300 border-red-700/40',
  }
  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${map[risk] || map.FAIR}`}>
      {risk}
    </span>
  )
}

// Function: ScoreCircle
function ScoreCircle({ value, label, color, industryAvg }) {
  const radius = 36
  const circ   = 2 * Math.PI * radius
  const offset = circ - (value / 100) * circ
  const avgOff = circ - (industryAvg / 100) * circ
  const isAbove = value >= industryAvg
  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative">
        <svg width={96} height={96} viewBox="0 0 96 96">
          {/* Track */}
          <circle cx={48} cy={48} r={radius} fill="none" stroke="#1f2937" strokeWidth={8} />
          {/* Industry average (dashed arc) */}
          <circle cx={48} cy={48} r={radius} fill="none" stroke="#4b5563"
            strokeWidth={2} strokeDasharray={circ}
            strokeDashoffset={avgOff}
            transform="rotate(-90 48 48)"
            strokeLinecap="round"
          />
          {/* Score arc */}
          <circle cx={48} cy={48} r={radius} fill="none" stroke={color}
            strokeWidth={8} strokeDasharray={circ}
            strokeDashoffset={offset}
            transform="rotate(-90 48 48)"
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-bold text-blue-300 leading-none">{value.toFixed(0)}</span>
        </div>
      </div>
      <span className="text-[10px] text-blue-400 font-medium">{label}</span>
      <span className={`text-[9px] ${isAbove ? 'text-green-400' : 'text-red-400'}`}>
        {isAbove ? '▲' : '▼'} Industry {industryAvg.toFixed(2)}
      </span>
    </div>
  )
}

// Function: TechHealthCard
function TechHealthCard({ tech, index }) {
  const color = LANG_COLORS[tech.language] || '#6b7280'
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className="rounded-xl border border-surface-border bg-gray-900/40 p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full" style={{ background: color }} />
          <span className="font-semibold text-sm text-blue-300">{tech.language}</span>
        </div>
        <RiskChip risk={tech.risk_label} />
      </div>

      {/* Three score circles */}
      <div className="flex justify-around py-2">
        <ScoreCircle
          value={tech.resiliency}
          label="SR – Resiliency"
          color={color}
          industryAvg={INDUSTRY_BENCHMARKS.resiliency}
        />
        <ScoreCircle
          value={tech.agility}
          label="SA – Agility"
          color={color}
          industryAvg={INDUSTRY_BENCHMARKS.agility}
        />
        <ScoreCircle
          value={tech.elegance}
          label="SE – Elegance"
          color={color}
          industryAvg={INDUSTRY_BENCHMARKS.elegance}
        />
      </div>

      {/* SLOC / files */}
      <div className="flex gap-3 mt-2 pt-2 border-t border-surface-border/50">
        <span className="text-[10px] text-blue-500">Overall: <span className="text-blue-300 font-bold">{tech.health.toFixed(1)}</span></span>
        <span className="text-[10px] text-blue-500">{tech.sloc?.toLocaleString()} SLOC</span>
        <span className="text-[10px] text-blue-500">{tech.files} files</span>
      </div>

      {/* Benchmark legend */}
      <div className="mt-1 text-[9px] text-blue-600 flex gap-3 flex-wrap">
        <span className="flex items-center gap-1">
          <span className="inline-block w-4 border-t border-dashed border-gray-600" />
          Industry avg
        </span>
        <span>Low/Red: below 65 · Medium/Orange: 65–87 · High/Green: above 87</span>
      </div>
    </motion.div>
  )
}

// Function: RadarComparison
function RadarComparison({ healthPerLang }) {
  // Build radar data: one axis per dimension, one series per language
  const dims = [
    { key: 'resiliency', label: 'Resiliency' },
    { key: 'agility',    label: 'Agility'    },
    { key: 'elegance',   label: 'Elegance'   },
    { key: 'health',     label: 'Overall'    },
  ]

  const radarData = dims.map(d => {
    const row = { dim: d.label }
    healthPerLang.forEach(t => {
      row[t.language] = t[d.key]
    })
    row['Industry Avg'] = INDUSTRY_BENCHMARKS[d.key] ?? 65
    return row
  })

  return (
    <div className="rounded-xl border border-surface-border bg-gray-900/40 p-4">
      <div className="text-sm font-semibold text-blue-200 mb-3 flex items-center gap-2">
        <Activity size={14} className="text-indigo-400" />
        Software Health Radar — All Technologies
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <RadarChart data={radarData}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis dataKey="dim" tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 9 }} />
          {healthPerLang.map(t => (
            <Radar
              key={t.language}
              name={t.language}
              dataKey={t.language}
              stroke={LANG_COLORS[t.language] || '#6b7280'}
              fill={LANG_COLORS[t.language] || '#6b7280'}
              fillOpacity={0.12}
              strokeWidth={2}
            />
          ))}
          <Radar
            name="Industry Avg"
            dataKey="Industry Avg"
            stroke="#6b7280"
            fill="none"
            strokeDasharray="5 3"
            strokeWidth={1.5}
          />
          <Legend
            wrapperStyle={{ fontSize: 11, color: '#9ca3af' }}
          />
          <Tooltip
            contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8, fontSize: 11 }}
            labelStyle={{ color: '#e5e7eb' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Function: HealthPerTechPanel
export default function HealthPerTechPanel({ healthPerLang }) {
  if (!healthPerLang || healthPerLang.length === 0) {
    return (
      <div className="py-16 text-center text-blue-500">
        <Activity size={32} className="mx-auto mb-3 opacity-40" />
        <p>Per-technology health data not available. Re-run analysis to generate this view.</p>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <p className="text-sm text-blue-400">
        The Software Health has been checked for each technology to identify focus areas.
        Each score ranges from 1 to 100 (the higher, the better).
        Dashed ring = industry average.
      </p>

      {/* Radar comparison */}
      {healthPerLang.length > 1 && <RadarComparison healthPerLang={healthPerLang} />}

      {/* Per-language cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {healthPerLang.map((t, i) => (
          <TechHealthCard key={t.language} tech={t} index={i} />
        ))}
      </div>

      {/* Legend note */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-blue-500">
        {Object.entries(INDUSTRY_BENCHMARKS).map(([key, val]) => (
          <div key={key} className="p-3 rounded-lg border border-surface-border bg-gray-900/30">
            <div className="font-semibold text-blue-300 mb-1 capitalize">{key}</div>
            <div>Low/Red: below 65</div>
            <div>Medium/Orange: 65–87</div>
            <div>High/Green: above 87</div>
            <div className="mt-1 text-blue-400">
              {key === 'resiliency' && 'JSP then Java is where Resiliency is low'}
              {key === 'agility'    && 'Overall portfolio is above industry average'}
              {key === 'elegance'   && 'Overall portfolio is above industry average'}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
