/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./frontend/**/*.{html,js}"],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                'bmad-dark': '#1a1a1a',
                'bmad-gray': '#2a2a2a',
                'bmad-surface': '#1e1e1e',
                'bmad-surface-hover': '#252525',
                'bmad-accent': '#4a9eff',
                'bmad-text': '#e0e0e0',
                'bmad-muted': '#888888',
                'bmad-green': '#10b981',
                'bmad-red': '#ef4444',
                'bmad-yellow': '#f59e0b',
            },
        },
    },
    plugins: [],
}
