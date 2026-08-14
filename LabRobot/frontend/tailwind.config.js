// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: @type {import('tailwindcss').Config}
// Date: 2025-09-11
// ---------------------------------------------------------------------------
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Microsoft Fluent / Azure Portal design tokens — matched to the real
      // portal.azure.com palette so this app reads as a native Azure blade
      // rather than a generic Tailwind dashboard.
      colors: {
        azure: {
          50:  '#EFF6FC',
          100: '#DEECF9',
          200: '#C7E0F4',
          300: '#A9D3F2',
          400: '#71AFE5',
          500: '#2B88D8',
          600: '#0078D4', // Microsoft Communication Blue — primary brand/action color
          700: '#106EBE',
          800: '#005A9E',
          900: '#004578',
          950: '#002642',
        },
        // Fluent neutral ramp — used for the masthead, chrome, borders and text
        // instead of Tailwind's default slate/gray scales.
        chrome: {
          50:  '#FAF9F8',
          100: '#F3F2F1',
          200: '#EDEBE9',
          300: '#E1DFDD',
          400: '#D2D0CE',
          500: '#C8C6C4',
          600: '#A19F9D',
          700: '#605E5C',
          800: '#3B3A39',
          900: '#252423',
          950: '#1B1A19', // Azure Portal masthead/left-nav near-black
        },
      },
      fontFamily: {
        sans: [
          '"Segoe UI"', '"Segoe UI Web (West European)"', '-apple-system',
          'BlinkMacSystemFont', 'Roboto', '"Helvetica Neue"', 'sans-serif',
        ],
      },
      boxShadow: {
        // Fluent's card elevation (depth4) — soft, low-spread.
        fluent: '0 1.6px 3.6px rgba(0,0,0,0.13), 0 0.3px 0.9px rgba(0,0,0,0.1)',
      },
    },
  },
  plugins: [],
}
