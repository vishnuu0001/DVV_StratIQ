// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/utils (format.ts)
// Date: 2025-10-30
// ---------------------------------------------------------------------------
// Function: formatCurrencyCompact
export function formatCurrencyCompact(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return '$0'
  const m = value / 1_000_000
  if (m >= 1000) return `$${(m / 1000).toFixed(1)}B`
  if (m >= 1) return `$${m.toFixed(m < 10 ? 3 : m < 100 ? 2 : 1)}M`
  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`
  return `$${value.toFixed(0)}`
}

// Function: formatCurrencyFull
export function formatCurrencyFull(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

// Function: formatPct
export function formatPct(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return '0.0%'
  return `${(value * 100).toFixed(1)}%`
}

// Function: formatPctDirect
export function formatPctDirect(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return '0.0%'
  return `${value.toFixed(1)}%`
}

// Function: formatNumber
export function formatNumber(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return '0'
  return new Intl.NumberFormat('en-US').format(value)
}

// Function: formatMillions
export function formatMillions(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return '0'
  return `${(value / 1_000_000).toFixed(1)}M`
}
