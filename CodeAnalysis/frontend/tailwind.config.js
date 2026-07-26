// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: @type {import('tailwindcss').Config}
// Date: 2025-12-10
// ---------------------------------------------------------------------------
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#ffffff',
          card:    '#ffffff',
          hover:   '#f8fafc',
          border:  '#dbe3f0',
        },
        brand: {
          cyan:   '#61dafb',
          blue:   '#3b82f6',
          indigo: '#6366f1',
          purple: '#a78bfa',
        },
        success: '#4ade80',
        warning: '#fb923c',
        danger:  '#f87171',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #a78bfa 100%)',
        'gradient-cyan':  'linear-gradient(90deg, #3b82f6, #06b6d4)',
        'gradient-green': 'linear-gradient(90deg, #22c55e, #06b6d4)',
        'gradient-warn':  'linear-gradient(90deg, #f59e0b, #ef4444)',
      },
      animation: {
        'fade-in':    'fadeIn 0.4s ease-out',
        'slide-up':   'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'spin-slow':  'spin 8s linear infinite',
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(20px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
