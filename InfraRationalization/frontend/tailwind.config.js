// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: @type {import('tailwindcss').Config}
// Date: 2026-01-15
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
          green:  '#10b981',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #10b981 0%, #3b82f6 50%, #6366f1 100%)',
      },
    },
  },
  plugins: [],
}
