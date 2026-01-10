/**
 * BMAD Dash - Dashboard View
 * Main dashboard view showing breadcrumb, quick glance, and current project data
 */

import { render as renderBreadcrumb } from '../components/breadcrumb.js';
import { render as renderQuickGlance } from '../components/quick-glance.js';

/**
 * Render the Dashboard View
 * @param {Object} data - Dashboard data from API
 */
export function render(data) {
    const container = document.getElementById('main-content');
    if (!container) {
        console.error('Main content container not found');
        return;
    }

    // Render breadcrumb and quick glance components
    renderBreadcrumb(data.breadcrumb);
    renderQuickGlance(data);

    // Clear main content and show dashboard message
    container.innerHTML = `
        <div class="text-center text-bmad-muted p-8">
            <p class="text-lg">Dashboard view is active</p>
            <p class="text-sm mt-2">Future: Kanban board will be displayed here (Story 3.2)</p>
        </div>
    `;
}
