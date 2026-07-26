// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * AITestDataPanel.jsx
// Date: 2025-09-20
// ---------------------------------------------------------------------------
/**
 * AITestDataPanel.jsx
 * --------------------
 * Test data generation strategy and sample records.
 */
import { FlaskConical, Table2, Workflow, Wrench } from 'lucide-react'
import { motion } from 'framer-motion'

const SCENARIO_COLOR = {
  'happy-path':   'bg-green-100 text-green-700',
  'edge-case':    'bg-yellow-100 text-yellow-700',
  negative:       'bg-red-100 text-red-700',
  performance:    'bg-blue-100 text-blue-700',
  security:       'bg-purple-100 text-purple-700',
}

// Function: AITestDataPanel
export default function AITestDataPanel({ data }) {
  if (!data) return null
  if (data.error) return <div className="bg-white rounded-2xl shadow p-6 text-red-500 text-sm">{data.error}</div>

  const entities   = data.entities   || []
  const scenarios  = data.test_scenarios || []
  const tools      = data.data_generation_tools || []

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">

      {/* Header */}
      <div className="bg-white rounded-2xl shadow p-6">
        <div className="flex items-center gap-2 mb-3">
          <FlaskConical size={18} className="text-pink-600" />
          <h3 className="font-semibold text-blue-800">Test Data Intelligence</h3>
        </div>
        <p className="text-sm text-blue-700">{data.summary}</p>
        {data.seeding_strategy && (
          <div className="mt-3 p-3 bg-pink-50 rounded-xl text-sm text-pink-800">
            <strong>Seeding Strategy:</strong> {data.seeding_strategy}
          </div>
        )}
        {tools.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {tools.map((t, i) => (
              <span key={i} className="flex items-center gap-1 text-xs bg-gray-100 text-blue-700 px-2 py-0.5 rounded-full">
                <Wrench size={10}/>{t}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Entities */}
      {entities.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Table2 size={15} className="text-pink-500" />
            <h3 className="font-semibold text-blue-800">Entities & Sample Data</h3>
          </div>
          <div className="space-y-4">
            {entities.map((ent, i) => (
              <div key={i} className="border border-pink-100 rounded-xl overflow-hidden">
                <div className="bg-pink-50 px-4 py-2 border-b border-pink-100">
                  <span className="font-semibold text-sm text-blue-800">{ent.name}</span>
                </div>
                {/* Fields table */}
                {(ent.fields || []).length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-xs">
                      <thead>
                        <tr className="bg-gray-50 border-b">
                          <th className="text-left px-3 py-1.5 text-blue-500 font-semibold">Field</th>
                          <th className="text-left px-3 py-1.5 text-blue-500 font-semibold">Type</th>
                          <th className="text-left px-3 py-1.5 text-blue-500 font-semibold">Sample Values</th>
                          <th className="text-left px-3 py-1.5 text-blue-500 font-semibold">Constraints</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ent.fields.map((f, j) => (
                          <tr key={j} className="border-b border-gray-50 hover:bg-gray-50">
                            <td className="px-3 py-1.5 font-mono text-blue-700">{f.name}</td>
                            <td className="px-3 py-1.5 text-blue-600 font-mono">{f.type}</td>
                            <td className="px-3 py-1.5 text-blue-500">
                              {(f.sample_values || []).join(', ')}
                            </td>
                            <td className="px-3 py-1.5 text-blue-400">{f.constraints}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                {/* Sample records */}
                {(ent.sample_records || []).length > 0 && (
                  <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
                    <p className="text-xs font-semibold text-blue-500 mb-2">Sample Records:</p>
                    <div className="space-y-1">
                      {ent.sample_records.slice(0, 2).map((rec, k) => (
                        <pre key={k} className="text-xs bg-white border rounded p-2 text-blue-600 overflow-x-auto">
                          {JSON.stringify(rec, null, 2)}
                        </pre>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Test scenarios */}
      {scenarios.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Workflow size={15} className="text-pink-500" />
            <h3 className="font-semibold text-blue-800">Test Scenarios ({scenarios.length})</h3>
          </div>
          <div className="space-y-2">
            {scenarios.map((s, i) => (
              <div key={i} className="border border-gray-100 rounded-xl p-3">
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  {s.type && (
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${SCENARIO_COLOR[s.type] || 'bg-gray-100 text-blue-600'}`}>
                      {s.type}
                    </span>
                  )}
                  <span className="text-sm font-semibold text-blue-800">{s.name}</span>
                </div>
                <p className="text-xs text-blue-600 mb-1">{s.description}</p>
                {s.test_data && (
                  <p className="text-xs text-blue-500 italic">Data needed: {s.test_data}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
