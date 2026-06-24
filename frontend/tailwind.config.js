/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        slate: {
          850: '#EAE6DD',
          950: '#F5F2EB',
        },
        retro: {
          bone: '#F5F2EB',
          ivory: '#FAF7F2',
          clay: '#C95A3E',
          sage: '#708A74',
          'sage-light': '#D6E0D7',
          charcoal: '#2E2925',
          border: '#DED9CE',
          glass: 'rgba(250, 247, 242, 0.7)',
        },
        risk: {
          low: '#708A74',
          'low-bg': '#EAEFEA',
          'low-badge': '#708A74',
          medium: '#D97E4A',
          'medium-bg': '#FAF0E8',
          'medium-badge': '#D97E4A',
          high: '#B8432B',
          'high-bg': '#FDF1EF',
          'high-badge': '#B8432B',
        },
        accent: {
          primary: '#C95A3E',
          secondary: '#829A86',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.4s ease-out forwards',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scan-wave': 'scanWave 1.5s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scanWave: {
          '0%, 100%': { transform: 'scaleX(0.4)', opacity: '0.5' },
          '50%': { transform: 'scaleX(1)', opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
