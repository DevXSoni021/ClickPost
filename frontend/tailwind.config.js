/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        display: ['var(--font-jakarta)', 'sans-serif'],
      },
      colors: {
        primary: "#6366f1", // Indigo 500
        secondary: "#10b981", // Emerald 500
        "background-light": "#f8fafc",
        "background-dark": "#020617",
      },
      animation: {
        'mesh-move': 'mesh-move 20s ease infinite alternate',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'wave': 'wave 2s infinite ease-in-out',
      },
      keyframes: {
        'mesh-move': {
          '0%': { transform: 'scale(1)' },
          '100%': { transform: 'scale(1.1)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        wave: {
          '0%, 100%': { transform: 'scaleY(0.5)', opacity: '0.5' },
          '50%': { transform: 'scaleY(1.2)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
