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
        bg: '#f5f5f5',
        'bg-sidebar': '#f3f2f1',
        surface: '#ffffff',
        'surface-hover': '#fafafa',
        'surface-raised': '#ffffff',
        hairline: '#d2d0ce',
        'hairline-strong': '#bfbdbb',
        ink: '#242424',
        'ink-dim': '#45413d',
        'ink-muted': '#605e5c',
        'ink-faint': '#797775',
        gold: {
          DEFAULT: '#0078d4',
          soft: '#106ebe',
          dim: '#005a9e',
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
