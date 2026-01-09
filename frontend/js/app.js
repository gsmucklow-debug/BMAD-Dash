/**
 * BMAD Dash - Main Application Entry Point
 * Initializes the application and sets up routing
 */

// Initialize app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('BMAD Dash initializing...');

    const app = document.getElementById('app');

    // Temporary placeholder until Story 1.2 implements the UI
    app.innerHTML = `
        <div class="flex items-center justify-center min-h-screen">
            <div class="text-center">
                <h1 class="text-4xl font-bold mb-4">BMAD Dash</h1>
                <p class="text-bmad-green">Project scaffold successfully initialized!</p>
                <p class="text-gray-400 mt-2">Story 0.1 Complete</p>
            </div>
        </div>
    `;
});
