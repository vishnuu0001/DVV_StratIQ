// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Safely coerce any value (including Pydantic Decimal strings) to a finite number.
// Date: 2026-01-15
// ---------------------------------------------------------------------------
/** Safely coerce any value (including Pydantic Decimal strings) to a finite number. */
// Function: toNum
export function toNum(v: unknown): number {
  if (v === null || v === undefined) return 0
  const num = typeof v === 'string' ? parseFloat(v) : Number(v)
  return isFinite(num) ? num : 0
}

// Function: formatCurrencyCompact
export function formatCurrencyCompact(value: unknown): string {
  const v = toNum(value)
  const m = v / 1_000_000
  if (m >= 1000) return `$${(m / 1000).toFixed(1)}B`
  if (m >= 1) return `$${m.toFixed(m < 10 ? 3 : m < 100 ? 2 : 1)}M`
  if (v >= 1000) return `$${(v / 1000).toFixed(0)}K`
  return `$${v.toFixed(0)}`
}

// Function: formatCurrencyFull
export function formatCurrencyFull(value: unknown): string {
  const v = toNum(value)
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v)
}

// Function: formatPct
export function formatPct(value: unknown): string {
  const v = toNum(value)
  return `${(v * 100).toFixed(1)}%`
}

// Function: formatPctDirect
export function formatPctDirect(value: unknown): string {
  const v = toNum(value)
  return `${v.toFixed(1)}%`
}

// Function: formatNumber
export function formatNumber(value: unknown): string {
  const v = toNum(value)
  return new Intl.NumberFormat('en-US').format(v)
}

// Function: formatMillions
export function formatMillions(value: unknown): string {
  const v = toNum(value)
  return `${(v / 1_000_000).toFixed(1)}M`
}
