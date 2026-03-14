/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        heading: ['Outfit', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        code: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        primary: {
          DEFAULT: '#2563EB',
          foreground: '#FFFFFF',
          hover: '#1D4ED8',
          active: '#1E40AF',
        },
        surface: {
          light: '#FFFFFF',
          dark: '#1E293B',
        },
      },
    },
  },
  plugins: [],
};
