/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand Colors
        brand: {
          primary: "#1e3a8a", // --brand-primary
          secondary: "#3b82f6", // --brand-secondary
          accent: "#2563eb", // --brand-accent
          "accent-dark": "#1d4ed8", // --brand-accent-dark
        },
        // Surface Colors
        surface: {
          white: "#ffffff", // --surface-white
          light: "#f8fafc", // --surface-light
          lighter: "#f1f5f9", // --surface-lighter
        },
        // Text Colors
        text: {
          primary: "#0f172a", // --text-primary
          secondary: "#64748b", // --text-secondary
          light: "#f8fafc", // --text-light
          muted: "#94a3b8", // --text-muted
        },
        // Feedback Colors
        success: {
          base: "#22c55e", // --success-base
          light: "#ecfdf5", // --success-light
        },
        error: {
          base: "#ef4444", // --error-base
          light: "#fee2e2", // --error-light
          dark: "#dc2626", // --error-dark
          border: "#fecaca", // --error-border
        },
        warning: {
          base: "#ca8a04", // --warning-base
          light: "#fefce8", // --warning-light
        },
      },
      boxShadow: {
        xs: "0 1px 2px rgba(0, 0, 0, 0.05)",
        sm: "0 1px 3px rgba(0, 0, 0, 0.1)",
        md: "0 4px 6px rgba(0, 0, 0, 0.1)",
        lg: "0 10px 15px rgba(0, 0, 0, 0.1)",
      },
      spacing: {
        "layout-xs": "0.375rem", // --layout-spacing-xs
        "layout-sm": "0.5rem", // --layout-spacing-sm
        "layout-md": "0.75rem", // --layout-spacing-md
        "layout-lg": "1rem", // --layout-spacing-lg
        "layout-xl": "1.5rem", // --layout-spacing-xl
      },
      maxWidth: {
        layout: "1500px", // --layout-max-width
      },
      height: {
        header: "60px", // --header-height
      },
      fontSize: {
        brand: "1.25rem", // --brand-font-size
        "brand-icon": "1.3rem", // --brand-icon-size
      },
      borderRadius: {
        nav: "6px", // --nav-border-radius
      },
      transitionDuration: {
        fast: "200ms", // --transition-fast
        normal: "300ms", // --transition-normal
      },
    },
  },
  plugins: [],
};
