/**
 * BMAD Dash - Timeline View
 * Timeline view placeholder (to be implemented in Story 3.2)
 */

/**
 * Render the Timeline View
 * @param {Object} data - Dashboard data from API
 */
export function render(data) {
    const container = document.getElementById('main-content');
    if (!container) {
        console.error('Main content container not found');
        return;
    }

    container.innerHTML = `
        <div class="text-center text-bmad-text p-12">
            <div class="max-w-md mx-auto bg-bmad-gray rounded-lg p-8">
                <svg class="w-16 h-16 mx-auto mb-4 text-bmad-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <h2 class="text-2xl font-bold mb-2">Timeline View Coming Soon</h2>
                <p class="text-bmad-muted">
                    The timeline view will be implemented in Story 3.2: Kanban Board & Timeline View
                </p>
            </div>
        </div>
    `;
}
