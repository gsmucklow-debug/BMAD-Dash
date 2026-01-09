/**
 * BMAD Dash - Breadcrumb Navigation Component
 * Shows current location: Project → Phase → Epic → Story → Task
 */

/**
 * Render breadcrumb navigation
 * @param {Object} breadcrumbData - Breadcrumb data from dashboard API
 * @param {string} breadcrumbData.project - Project name
 * @param {string} breadcrumbData.phase - Phase name
 * @param {Object} breadcrumbData.epic - Epic object {id, title}
 * @param {Object} breadcrumbData.story - Story object {id, title}
 * @param {Object} breadcrumbData.task - Task object {id, title}
 */
export function render(breadcrumbData) {
    const container = document.getElementById('breadcrumb-container');

    if (!breadcrumbData) {
        container.innerHTML = '<p class="text-bmad-muted text-sm">No breadcrumb data available</p>';
        return;
    }

    const levels = [];

    // Build breadcrumb levels array
    if (breadcrumbData.project) {
        levels.push({ label: breadcrumbData.project, type: 'project' });
    }
    if (breadcrumbData.phase) {
        levels.push({ label: breadcrumbData.phase, type: 'phase' });
    }
    if (breadcrumbData.epic) {
        levels.push({
            label: breadcrumbData.epic.title,
            type: 'epic',
            id: breadcrumbData.epic.id
        });
    }
    if (breadcrumbData.story) {
        levels.push({
            label: breadcrumbData.story.title,
            type: 'story',
            id: breadcrumbData.story.id
        });
    }
    if (breadcrumbData.task) {
        levels.push({
            label: breadcrumbData.task.title,
            type: 'task',
            id: breadcrumbData.task.id
        });
    }

    // Handle case where no levels exist
    if (levels.length === 0) {
        container.innerHTML = '<p class="text-bmad-muted text-sm">No breadcrumb data available</p>';
        return;
    }

    // Render breadcrumb with semantic HTML
    const breadcrumbHTML = `
        <nav aria-label="Breadcrumb navigation" class="bg-bmad-gray p-4 rounded-lg">
            <ol class="flex items-center flex-wrap gap-2 text-base">
                ${levels.map((level, index) => {
        const isLast = index === levels.length - 1;
        const classes = isLast
            ? 'text-bmad-accent font-semibold'
            : 'text-bmad-muted hover:text-bmad-text transition-colors cursor-pointer';

        return `
                        <li class="flex items-center">
                            <span 
                                class="${classes}" 
                                data-type="${level.type}" 
                                data-id="${level.id || ''}"
                            >
                                ${escapeHtml(level.label)}
                            </span>
                            ${!isLast ? '<span class="ml-2 text-bmad-muted select-none">→</span>' : ''}
                        </li>
                    `;
    }).join('')}
            </ol>
        </nav>
    `;

    container.innerHTML = breadcrumbHTML;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
