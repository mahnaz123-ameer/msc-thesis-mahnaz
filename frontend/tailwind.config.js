/** @type {import('tailwindcss').Config} */

// Every colour the app uses points at a CSS variable (defined in src/index.css),
// so switching between dark and light mode only swaps the variables.
const v = (name) => `rgb(var(--${name}) / <alpha-value>)`
const scale = (family, shades) => Object.fromEntries(shades.map(s => [s, v(`${family}-${s}`)]))

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: v('primary'),
        'primary-dark': v('primary-dark'),
        surface: v('surface'),
        card: v('card'),
        border: v('border'),
        // "white" text = the strongest text colour of the current theme
        white: v('fg'),
        slate:  scale('slate',  [200, 300, 400, 500, 600, 700, 800, 900]),
        green:  scale('green',  [300, 400, 500, 700, 800, 900]),
        red:    scale('red',    [300, 400, 500, 700, 800, 900]),
        yellow: scale('yellow', [400, 800, 900]),
        blue:   scale('blue',   [400, 800, 900]),
        purple: scale('purple', [400, 800]),
        orange: scale('orange', [300]),
        indigo: scale('indigo', [300, 800, 950]),
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
