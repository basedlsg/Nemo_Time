/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ChatGPT Brand Colors (Teal Green)
        brand: {
          50: '#E6F7F2',
          100: '#CCEFE5',
          200: '#99DFCB',
          300: '#66CFB1',
          400: '#33BF97',
          500: '#10a37f',  // PRIMARY - ChatGPT Teal
          600: '#0D8A6A',  // Hover states
          700: '#0A7156',  // Active states
          800: '#085843',
          900: '#05402F',
        },
        // Cool Grays (Blue undertones like ChatGPT)
        neutral: {
          50: '#F7F7F8',   // Cool light gray
          100: '#ECECF1',  // Very light gray
          200: '#E5E5E5',  // Light gray
          300: '#D1D1D6',  // Medium light gray
          400: '#A0A0AB',  // Medium gray
          500: '#6E6E80',  // Dark gray
          600: '#565869',  // Darker gray
          700: '#40414F',  // ChatGPT message bg
          800: '#343540',  // ChatGPT main surface
          900: '#202123',  // Dark surface
          950: '#000000',  // Pure black (sidebar)
        },
        // Avatar Colors
        purple: {
          500: '#AB68FF',  // User avatar
          600: '#9553E0',
        },
        teal: {
          500: '#10a37f',  // AI avatar (same as brand)
          600: '#0D8A6A',
        },
      },
      fontFamily: {
        sans: [
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Noto Sans SC"',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
      },
      keyframes: {
        'slide-in': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      animation: {
        'slide-in': 'slide-in 0.3s ease-out',
        'fade-in': 'fade-in 0.3s ease-out',
      },
    },
  },
  plugins: [],
}
