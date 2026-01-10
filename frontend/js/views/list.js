/**
 * BMAD Dash - List View
 * List view placeholder (to be implemented in Story 3.3)
 */

/**
 * Render the List View
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
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
                </svg>
                <h2 class="text-2xl font-bold mb-2">List View Coming Soon</h2>
                <p class="text-bmad-muted">
                    The list view will be implemented in Story 3.3: Minimal List View & Manual Refresh
                </p>
            </div>
        </div>
    `;
}
