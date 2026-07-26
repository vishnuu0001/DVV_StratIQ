// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/components (ChartImage.jsx)
// Date: 2026-04-16
// ---------------------------------------------------------------------------
import React, { useState, useEffect, useCallback } from 'react'
import { RefreshCw, AlertCircle, BarChart2, Maximize2, X, ExternalLink } from 'lucide-react'
import { renderChart } from '../api'

// Function: ChartImage
export default function ChartImage({
  endpoint,
  title,
  height = 400,
  className = '',
  refreshKey = 0,
  onDrilldown = null,   // () => void — if provided, chart is clickable for L2/L3 drilldown
}) {
  const [src, setSrc] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  const [fullscreen, setFullscreen] = useState(false)

  const loadImage = useCallback(() => {
    setLoading(true)
    setError(false)
    const url = renderChart(endpoint)
    const img = new Image()
    img.onload = () => { setSrc(url); setLoading(false) }
    img.onerror = () => { setLoading(false); setError(true) }
    img.src = url
  }, [endpoint, retryCount, refreshKey])

  useEffect(() => { loadImage() }, [loadImage])

  useEffect(() => {
    // Function: handleKey
    function handleKey(e) { if (e.key === 'Escape') setFullscreen(false) }
    if (fullscreen) {
      document.addEventListener('keydown', handleKey)
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.removeEventListener('keydown', handleKey)
      document.body.style.overflow = ''
    }
  }, [fullscreen])

  // Function: handleRetry
  function handleRetry() { setRetryCount((c) => c + 1) }

  const isDrillable = !!onDrilldown && !error && !!src

  return (
    <>
      <div
        className={`relative rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden ${className}`}
        style={{ minHeight: height }}
      >
        {/* Title bar */}
        {title && (
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-sky-600" />
              <span className="text-sm font-medium text-slate-700">{title}</span>
            </div>
            <div className="flex items-center gap-1.5">
              {isDrillable && (
                <button
                  onClick={onDrilldown}
                  title="Drill down to L2/L3 detail"
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-sky-50 hover:bg-sky-100 border border-sky-200 text-sky-600 text-xs font-medium transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                  Drill Down
                </button>
              )}
              {!error && src && (
                <button
                  onClick={() => setFullscreen(true)}
                  title="Expand fullscreen"
                  className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-400 hover:text-slate-700 transition-colors"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        )}

        {/* Overlay buttons when no title */}
        {!title && !error && src && (
          <div className="absolute top-2 right-2 z-10 flex items-center gap-1.5">
            {isDrillable && (
              <button
                onClick={onDrilldown}
                title="Drill down to L2/L3 detail"
                className="flex items-center gap-1 px-2 py-1 rounded-lg bg-sky-50/90 hover:bg-sky-100 border border-sky-200 text-sky-600 text-xs font-medium transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
                Drill Down
              </button>
            )}
            <button
              onClick={() => setFullscreen(true)}
              title="Expand fullscreen"
              className="p-1.5 rounded-lg bg-white/90 hover:bg-slate-100 border border-slate-300 text-slate-400 hover:text-slate-700 transition-colors"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Chart area */}
        <div
          className={`relative flex items-center justify-center ${isDrillable ? 'cursor-pointer group' : ''}`}
          style={{ minHeight: title ? height - 45 : height }}
          onClick={isDrillable ? onDrilldown : undefined}
        >
          {/* Loading state */}
          {loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-50 gap-3">
              <div className="w-8 h-8 border-2 border-sky-400 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-500">Rendering chart...</p>
            </div>
          )}

          {/* Error state */}
          {error && !loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-50 gap-3">
              <AlertCircle className="w-8 h-8 text-slate-400" />
              <p className="text-sm text-slate-500">Chart unavailable</p>
              <button
                onClick={(e) => { e.stopPropagation(); handleRetry() }}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs rounded-lg border border-slate-300 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry
              </button>
            </div>
          )}

          {/* Image */}
          {!error && src && (
            <>
              <img
                src={src}
                alt={title || endpoint}
                className={`w-full h-auto block transition-opacity duration-300 ${loading ? 'opacity-0' : 'opacity-100'} ${isDrillable ? 'group-hover:brightness-[0.97]' : ''}`}
              />
              {/* Drilldown hover hint */}
              {isDrillable && (
                <div className="absolute inset-0 flex items-end justify-center pb-3 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                  <span className="px-3 py-1 bg-sky-600/90 text-white text-xs rounded-full shadow font-medium">
                    Click to drill down ↗
                  </span>
                </div>
              )}
            </>
          )}
        </div>

        {/* Matplotlib badge */}
        {!error && !loading && src && (
          <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded text-[10px] text-slate-400 bg-white/90 border border-slate-200 font-mono">
            Powered by Matplotlib
          </div>
        )}
      </div>

      {/* Fullscreen overlay */}
      {fullscreen && src && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm"
          onClick={() => setFullscreen(false)}
        >
          <div
            className="relative max-w-[95vw] max-h-[95vh] rounded-xl overflow-hidden border border-slate-300 shadow-2xl bg-white"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-sky-600" />
                <span className="text-sm font-medium text-slate-700">{title || endpoint}</span>
              </div>
              <button
                onClick={() => setFullscreen(false)}
                className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-500 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-2 flex items-center justify-center" style={{ maxHeight: 'calc(95vh - 52px)' }}>
              <img
                src={src}
                alt={title || endpoint}
                className="object-contain"
                style={{ maxWidth: '90vw', maxHeight: 'calc(95vh - 72px)' }}
              />
            </div>
          </div>
        </div>
      )}
    </>
  )
}
