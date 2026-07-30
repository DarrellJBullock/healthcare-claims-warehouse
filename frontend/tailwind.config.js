/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          950: "#05070a",
          900: "#0b0f16",
          850: "#0f141d",
          800: "#141a25",
          700: "#1b2330",
          600: "#28323f",
          500: "#3a4757",
        },
        accent: {
          400: "#4fd1c5",
          500: "#2dd4bf",
          600: "#14b8a6",
        },
        risk: {
          low: "#22c55e",
          medium: "#eab308",
          high: "#f97316",
          critical: "#ef4444",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
      },
    },
  },
  plugins: [],
};
