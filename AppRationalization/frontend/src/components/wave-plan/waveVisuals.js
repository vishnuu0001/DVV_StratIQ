// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components/wave-plan (waveVisuals.js)
// Date: 2026-07-20
// ---------------------------------------------------------------------------
// Shared color roles for the Wave Plan Gantt — ordinal sequential ramp for
// T-shirt size (the bar's primary encoding) and the fixed status palette for
// risk/complexity badges (icon + label, never color-alone). Values match the
// dataviz skill's validated dark-mode steps.

// T-shirt size -> ordinal blue ramp (lightest = smallest effort). Step 300 is
// the lightest step that still clears 2:1 on a dark surface per the skill's
// ordinal-ramp rule; step 600 is the darkest allowed.
export const TSHIRT_RAMP = {
  S: '#6da7ec',
  M: '#3987e5',
  L: '#256abf',
  XL: '#184f95',
};
export const TSHIRT_FALLBACK = '#52525b'; // slate-600 — unsized apps

// Function: tshirtColor
export const tshirtColor = (size) => TSHIRT_RAMP[(size || '').trim().toUpperCase()] || TSHIRT_FALLBACK;

// Fixed status palette — never reused for series identity.
export const STATUS_COLORS = {
  low: '#0ca30c',
  medium: '#fab219',
  high: '#d03b3b',
};

// Function: statusColor
export const statusColor = (value) => STATUS_COLORS[(value || '').trim().toLowerCase()] || '#898781';

// Four-tier complexity ramp (Simple -> Very Complex), distinct from the
// 3-step STATUS_COLORS above since the wave schedule uses a 4-tier scale.
export const TIER_COLORS = {
  simple: '#0ca30c',
  medium: '#fab219',
  complex: '#ec835a',
  very_complex: '#d03b3b',
};

// Function: tierColor
export const tierColor = (tier) => TIER_COLORS[(tier || '').trim().toLowerCase()] || '#898781';

// Function: formatDate
export const formatDate = (iso) => {
  if (!iso) return '—';
  const d = new Date(`${iso}T00:00:00`);
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
};

// Function: formatDateShort
export const formatDateShort = (iso) => {
  if (!iso) return '—';
  const d = new Date(`${iso}T00:00:00`);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
};
