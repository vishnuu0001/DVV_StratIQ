// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui (tailwind.config.ts)
// Date: 2025-07-18
// ---------------------------------------------------------------------------
import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0a0e14',
        'bg-grid': '#0d1219',
        surface: '#131820',
        'surface-2': '#1a2028',
        'surface-3': '#232b36',
        border: '#2a3440',
        'border-hi': '#3a4654',
        text: '#e8eef5',
        'text-2': '#8b9bac',
        'text-3': '#5a6778',
        // Domain colors
        'd-procurement': '#f59e0b',
        'd-logistics': '#a78bfa',
        'd-warehouse': '#06b6d4',
        'd-production': '#10b981',
        'd-people': '#f43f5e',
        'd-system': '#facc15',
        // Severity colors
        'severity-critical': '#ef4444',
        'severity-high': '#f59e0b',
        'severity-med': '#facc15',
        'severity-low': '#38bdf8',
        'severity-info': '#5a6778',
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        display: ['"Instrument Serif"', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'pulse-border': 'pulse-border 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fade-in 0.2s ease-out',
        'blink': 'blink 1s step-end infinite',
      },
      keyframes: {
        'pulse-border': {
          '0%, 100%': { borderColor: 'rgba(239, 68, 68, 0.5)' },
          '50%': { borderColor: 'rgba(239, 68, 68, 1)' },
        },
        'fade-in': {
          from: { opacity: '0', transform: 'translateY(-4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'blink': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
    },
  },
  plugins: [],
}

export default config
