/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f4f7f2',  // Very light sage
          100: '#e6f4ea', // Sage Green (Secondary)
          200: '#cce3d4',
          300: '#a8cbb5',
          400: '#82af94',
          500: '#5e9174',
          600: '#3f7456',
          700: '#28583d',
          800: '#1a3c26', // Forest Green (Primary Dark)
          900: '#163300', // Deepest Green
          950: '#0a1a0d',
        },
        gold: {
          400: '#f3c448', // Golden Yellow (Accent)
          500: '#e0b135',
        },
        cream: {
          50: '#fdfdf9', // Soft Cream (Background)
          100: '#fcfcf5',
          200: '#f7f7eb',
        },
        slate: {
          850: '#1a3c26', // Replacing standard dark slate with our Forest Green for text
          900: '#0a1a0d',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'Georgia', 'serif'], // Added for headings
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(26, 60, 38, 0.08)', // Tinted with green
        'glow': '0 0 15px rgba(243, 196, 72, 0.3)', // Gold glow
      },
      backgroundImage: {
        'nature-pattern': "url('/src/assets/hero-bg.png')",
      }
    },
  },
  plugins: [],
}
