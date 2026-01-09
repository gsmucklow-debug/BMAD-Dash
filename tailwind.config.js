/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./frontend/**/*.{html,js}"],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                'bmad-dark': '#1a1a1a',
                'bmad-gray': '#2a2a2a',
                'bmad-accent': '#3a3a3a',
                'bmad-green': '#10b981',
                'bmad-red': '#ef4444',
                'bmad-yellow': '#f59e0b',
            },
        },
    },
    plugins: [],
}
