/**
 * BMAD Dash - Quick Glance Component
 * Shows temporal context: Last Completed → Current Focus → Up Next
 * with progress indicators for the current story
 */

// Constants
const CONTAINER_ID = 'quick-glance-container';

/**
 * Render Quick Glance bar
 * @param {Object} data - Dashboard data from API
 * @param {Object} data.quick_glance - Quick glance data with done, current, next
 * @param {Object} data.project - Project metadata (optional)
 */
export function render(data) {
    const container = document.getElementById(CONTAINER_ID);

    if (!data || !data.quick_glance) {
        container.innerHTML = '<p class="text-bmad-muted text-sm">No quick glance data available</p>';
        return;
    }

    // Safely destructure with defaults
    const { done = null, current = null, next = null } = data.quick_glance || {};

    // Handle empty state (no current story)
    if (!current) {
        container.innerHTML = `
            <div class="bg-bmad-gray/50 p-4 rounded-lg border border-bmad-gray">
                <p class="text-bmad-muted text-sm text-center">No active story</p>
            </div>
        `;
        return;
    }

    // Build HTML structure
    const quickGlanceHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 bg-bmad-gray/50 p-4 rounded-lg border border-bmad-gray">
            ${renderDoneSection(done)}
            ${renderCurrentSection(current)}
            ${renderNextSection(next)}
        </div>
    `;

    container.innerHTML = quickGlanceHTML;
}

/**
 * Render Done section
 * @param {Object|null} done - Done story data
 * @returns {string} HTML for Done section
 */
function renderDoneSection(done) {
    if (!done) {
        return `
            <div class="flex flex-col">
                <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Last Completed</span>
                <div class="font-medium text-bmad-muted text-sm italic">None yet</div>
            </div>
        `;
    }

    const title = escapeHtml(done.title || '');
    const storyId = escapeHtml(done.story_id || '');

    return `
        <div class="flex flex-col">
            <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Last Completed</span>
            <div class="font-medium text-bmad-text truncate">${storyId ? `${storyId}: ` : ''}${title}</div>
            ${done.completed ? `
                <div class="text-xs text-bmad-green mt-1 flex items-center">
                    <span class="w-2 h-2 rounded-full bg-bmad-green mr-2"></span>
                    Done
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Render Current section with progress bar
 * @param {Object} current - Current story data
 * @returns {string} HTML for Current section
 */
function renderCurrentSection(current) {
    if (!current) {
        return `
            <div class="flex flex-col relative pl-4 border-l border-bmad-muted/30">
                <span class="text-xs uppercase tracking-wider text-bmad-accent mb-1 font-bold">Current Focus</span>
                <div class="font-medium text-bmad-muted text-sm italic">No active story</div>
            </div>
        `;
    }

    const title = escapeHtml(current.title || '');
    const storyId = escapeHtml(current.story_id || '');
    const status = escapeHtml(current.status || '');
    
    // Parse progress string (e.g., "2/8 tasks")
    const progressBar = parseProgress(current.progress);

    return `
        <div class="flex flex-col relative pl-4 border-l border-bmad-muted/30">
            <span class="text-xs uppercase tracking-wider text-bmad-accent mb-1 font-bold">Current Focus</span>
            <div class="font-bold text-white text-lg truncate">${storyId ? `${storyId}: ` : ''}${title}</div>
            
            ${progressBar ? `
                <div class="mt-2 w-full">
                    <div class="flex justify-between text-xs text-bmad-muted mb-1">
                        <span>Story Progress</span>
                        <span>${escapeHtml(current.progress || '')}</span>
                    </div>
                    <div class="h-1 w-full bg-gray-700 rounded-full overflow-hidden">
                        <div class="h-full bg-bmad-accent transition-all duration-500" style="width: ${progressBar.percentage}%"></div>
                    </div>
                </div>
            ` : ''}
            
            ${status ? `
                <div class="text-xs text-bmad-muted mt-1">
                    Status: ${status}
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Render Next section
 * @param {Object|null} next - Next story data
 * @returns {string} HTML for Next section
 */
function renderNextSection(next) {
    if (!next) {
        return `
            <div class="flex flex-col pl-4 border-l border-bmad-muted/30">
                <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Up Next</span>
                <div class="font-medium text-bmad-muted text-sm italic">No upcoming story</div>
            </div>
        `;
    }

    const title = escapeHtml(next.title || '');
    const storyId = escapeHtml(next.story_id || '');

    return `
        <div class="flex flex-col pl-4 border-l border-bmad-muted/30">
            <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Up Next</span>
            <div class="font-medium text-bmad-text truncate">${storyId ? `${storyId}: ` : ''}${title}</div>
            ${next.status ? `
                <div class="text-xs text-bmad-muted mt-1">
                    Status: ${escapeHtml(next.status)}
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Parse progress string to calculate percentage
 * @param {string|null} progressStr - Progress string like "2/8 tasks"
 * @returns {Object|null} Object with percentage, or null if invalid
 */
function parseProgress(progressStr) {
    if (!progressStr || typeof progressStr !== 'string') {
        return null;
    }

    // Match pattern like "2/8 tasks" or "5/10"
    const match = progressStr.match(/(\d+)\/(\d+)/);
    if (!match) {
        return null;
    }

    const completed = parseInt(match[1], 10);
    const total = parseInt(match[2], 10);

    // Validate numbers
    if (isNaN(completed) || isNaN(total) || completed < 0 || total < 0) {
        return null;
    }

    if (total === 0) {
        return { percentage: 0, completed: 0, total: 0 };
    }

    // Calculate percentage with bounds checking (0-100%)
    const rawPercentage = (completed / total) * 100;
    const percentage = Math.min(100, Math.max(0, Math.round(rawPercentage)));
    
    return { percentage, completed, total };
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}
