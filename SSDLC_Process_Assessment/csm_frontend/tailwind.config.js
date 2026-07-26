// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: @type {import('tailwindcss').Config}
// Date: 2025-08-16
// ---------------------------------------------------------------------------
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0A1628',
          800: '#0F1E30',
          700: '#162338',
          600: '#1E2D42',
          500: '#243349',
        },
        accent: {
          blue: '#3B82F6',
          purple: '#8B5CF6',
          cyan: '#22D3EE',
          green: '#34D399',
          amber: '#FCD34D',
          red: '#F87171',
          pink: '#F9A8D4',
        },
      },
    },
  },
  plugins: [],
}
