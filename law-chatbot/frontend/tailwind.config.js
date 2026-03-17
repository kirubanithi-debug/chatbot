/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        legal: {
          50: '#f3f8f6',
          100: '#dceee6',
          200: '#b9ddd0',
          300: '#8ec7b4',
          400: '#5faa93',
          500: '#3d8e78',
          600: '#1f6f58',
          700: '#155342',
          800: '#133d33',
          900: '#112c25',
        },
        sidebar: '#0c0c1d',
        content: '#f1f5f9',
      },
    },
  },
  plugins: [],
}
