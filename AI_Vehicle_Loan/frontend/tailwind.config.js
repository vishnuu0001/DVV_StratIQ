// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: @type {import('tailwindcss').Config}
// Date: 2025-12-19
// ---------------------------------------------------------------------------
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#00b36b', // The green from the image
          dark: '#009e5f',
          light: '#e6f7f0'
        }
      }
    },
  },
  plugins: [],
}