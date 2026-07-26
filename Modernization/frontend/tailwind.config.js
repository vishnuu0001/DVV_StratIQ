// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: @type {import('tailwindcss').Config}
// Date: 2026-06-24
// ---------------------------------------------------------------------------
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0d0d13',
        'bg-sidebar': '#09090d',
        surface: '#15151e',
        'surface-hover': '#1b1b27',
        'surface-raised': '#1a1a24',
        hairline: 'rgba(255,255,255,0.08)',
        'hairline-strong': 'rgba(255,255,255,0.14)',
        ink: '#f3ede2',
        'ink-dim': '#c9c4d6',
        'ink-muted': '#9c9aab',
        'ink-faint': '#68667a',
        gold: {
          DEFAULT: '#e3b23c',
          soft: '#f3d38a',
          dim: '#8a6a26',
        },
      },
      fontFamily: {
        display: ['"Fraunces"', 'ui-serif', 'Georgia', 'serif'],
        sans: ['"Manrope"', '"Segoe UI"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Cascadia Code"', '"Fira Code"', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
