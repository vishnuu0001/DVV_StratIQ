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
          hover:   '#f3f2f1',
          border:  '#edebe9',
        },
        brand: {
          cyan:   '#50e6ff',
          blue:   '#0078d4',
          indigo: '#0078d4',
          purple: '#8764b8',
        },
        success: '#107c10',
        warning: '#ca5010',
        danger:  '#a4262c',
      },
      fontFamily: {
        sans: ['Segoe UI', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #0078d4 0%, #0078d4 100%)',
        'gradient-cyan':  'linear-gradient(90deg, #0078d4, #50e6ff)',
        'gradient-green': 'linear-gradient(90deg, #107c10, #50e6ff)',
        'gradient-warn':  'linear-gradient(90deg, #ca5010, #a4262c)',
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
