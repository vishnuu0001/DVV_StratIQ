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
          hover:   '#f3f2f1',
          border:  '#edebe9',
        },
        brand: {
          cyan:   '#50e6ff',
          blue:   '#0078d4',
          indigo: '#0078d4',
          green:  '#107c10',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #0078d4 0%, #0078d4 100%)',
      },
    },
  },
  plugins: [],
}
