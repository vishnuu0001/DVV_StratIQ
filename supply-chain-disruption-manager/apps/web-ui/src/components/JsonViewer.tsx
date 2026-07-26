// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (JsonViewer.tsx)
// Date: 2025-12-16
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { ChevronRight, ChevronDown, Copy, Check } from 'lucide-react'

interface TokenProps {
  value: unknown
  depth: number
  collapsed?: boolean
}

// Function: JsonValue
function JsonValue({ value, depth, collapsed: initCollapsed = false }: TokenProps) {
  const [collapsed, setCollapsed] = useState(initCollapsed || depth > 2)

  if (value === null) return <span className="text-text-3 font-mono text-xs">null</span>
  if (typeof value === 'boolean') return <span className="text-purple-400 font-mono text-xs">{String(value)}</span>
  if (typeof value === 'number') return <span className="text-cyan-400 font-mono text-xs">{value}</span>
  if (typeof value === 'string') return <span className="text-green-400 font-mono text-xs break-all">"{value}"</span>

  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="text-text-2 font-mono text-xs">[]</span>
    return (
      <span>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-text-3 hover:text-text inline-flex items-center gap-0.5"
        >
          {collapsed ? <ChevronRight size={10} /> : <ChevronDown size={10} />}
          <span className="font-mono text-xs text-text-2">[{value.length}]</span>
        </button>
        {!collapsed && (
          <div className="ml-4 border-l border-border pl-2">
            {value.map((item, i) => (
              <div key={i} className="flex gap-1 items-start">
                <span className="text-text-3 font-mono text-xs shrink-0">{i}:</span>
                <JsonValue value={item} depth={depth + 1} />
                {i < value.length - 1 && <span className="text-text-3 font-mono text-xs">,</span>}
              </div>
            ))}
          </div>
        )}
      </span>
    )
  }

  if (typeof value === 'object') {
    const keys = Object.keys(value as Record<string, unknown>)
    if (keys.length === 0) return <span className="text-text-2 font-mono text-xs">{'{}'}</span>
    return (
      <span>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-text-3 hover:text-text inline-flex items-center gap-0.5"
        >
          {collapsed ? <ChevronRight size={10} /> : <ChevronDown size={10} />}
          <span className="font-mono text-xs text-text-2">{'{'}…{'}'} {keys.length} keys</span>
        </button>
        {!collapsed && (
          <div className="ml-4 border-l border-border pl-2">
            {keys.map((key, i) => (
              <div key={key} className="flex gap-1 items-start flex-wrap">
                <span className="text-amber-400/80 font-mono text-xs shrink-0">"{key}":</span>
                <JsonValue value={(value as Record<string, unknown>)[key]} depth={depth + 1} />
                {i < keys.length - 1 && <span className="text-text-3 font-mono text-xs">,</span>}
              </div>
            ))}
          </div>
        )}
      </span>
    )
  }

  return <span className="text-text font-mono text-xs">{String(value)}</span>
}

interface JsonViewerProps {
  data: unknown
  collapsed?: boolean
}

// Function: JsonViewer
export function JsonViewer({ data, collapsed = false }: JsonViewerProps) {
  const [copied, setCopied] = useState(false)

  // Function: copy
  const copy = () => {
    void navigator.clipboard.writeText(JSON.stringify(data, null, 2)).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="relative group">
      <button
        onClick={copy}
        className="absolute top-1 right-1 p-1 rounded text-text-3 hover:text-text opacity-0 group-hover:opacity-100 transition-opacity bg-surface-2"
        title="Copy JSON"
      >
        {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
      </button>
      <div className="bg-surface-2 border border-border rounded p-3 overflow-auto max-h-96 text-xs">
        <JsonValue value={data} depth={0} collapsed={collapsed} />
      </div>
    </div>
  )
}
