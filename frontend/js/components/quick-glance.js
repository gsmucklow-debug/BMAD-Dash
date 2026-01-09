/**
 * Quick Glance Component
 * Renders the Done | Current | Next status bar with progress indicators
 */

/**
 * Render the Quick Glance component
 * @param {Object} data - The dashboard data containing quick_glance object
 */
export function render(data) {
    const container = document.getElementById('quick-glance-container');
    if (!container) return;

    const glanceData = data.quick_glance;

    if (!glanceData) {
        container.innerHTML = ''; // Clear if no data
        return;
    }

    container.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 bg-bmad-gray/50 p-4 rounded-lg border border-bmad-gray shadow-md">
            ${renderDoneSection(glanceData.done)}
            ${renderCurrentSection(glanceData.current)}
            ${renderNextSection(glanceData.next)}
        </div>
    `;
}

/**
 * Render the 'Done' section
 * @param {Object|null} doneStory 
 */
function renderDoneSection(doneStory) {
    if (!doneStory) {
        return `
            <div class="flex flex-col opacity-50">
                <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Last Completed</span>
                <div class="font-medium text-bmad-text italic">None</div>
            </div>
        `;
    }

    return `
        <div class="flex flex-col">
            <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Last Completed</span>
            <div class="font-medium text-bmad-text truncate" title="${escapeHtml(doneStory.title)}">
                Story ${doneStory.story_id}: ${escapeHtml(doneStory.title)}
            </div>
            <div class="text-xs text-bmad-green mt-1 flex items-center">
                <span class="w-2 h-2 rounded-full bg-bmad-green mr-2"></span> Done
            </div>
        </div>
    `;
}

/**
 * Render the 'Current' section (Highlighted)
 * @param {Object|null} currentStory 
 */
function renderCurrentSection(currentStory) {
    // If no active story
    if (!currentStory) {
        return `
            <div class="flex flex-col relative pl-4 border-l border-bmad-muted/30">
                <span class="text-xs uppercase tracking-wider text-bmad-accent mb-1 font-bold">Current Focus</span>
                <div class="font-bold text-white text-lg italic text-bmad-muted">No active story</div>
            </div>
        `;
    }

    // Parse progress string "X/Y tasks" -> percent
    const progressPercent = calculateProgress(currentStory.progress);

    return `
        <div class="flex flex-col relative pl-4 border-l border-bmad-muted/30">
            <span class="text-xs uppercase tracking-wider text-bmad-accent mb-1 font-bold">Current Focus</span>
            <div class="font-bold text-white text-lg truncate" title="${escapeHtml(currentStory.title)}">
                Story ${currentStory.story_id}: ${escapeHtml(currentStory.title)}
            </div>
            
            <!-- Story Progress -->
            <div class="mt-2 w-full">
                <div class="flex justify-between text-xs text-bmad-muted mb-1">
                    <span>Story Progress</span>
                    <span>${escapeHtml(currentStory.progress || '0/0 tasks')}</span>
                </div>
                <div class="h-1 w-full bg-gray-700 rounded-full overflow-hidden">
                    <div class="h-full bg-bmad-accent transition-all duration-500" style="width: ${progressPercent}%"></div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Render the 'Next' section
 * @param {Object|null} nextStory 
 */
function renderNextSection(nextStory) {
    if (!nextStory) {
        return `
            <div class="flex flex-col pl-4 border-l border-bmad-muted/30 opacity-50">
                <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Up Next</span>
                <div class="font-medium text-bmad-text italic">Project Complete</div>
            </div>
        `;
    }

    return `
        <div class="flex flex-col pl-4 border-l border-bmad-muted/30">
            <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Up Next</span>
            <div class="font-medium text-bmad-text truncate" title="${escapeHtml(nextStory.title)}">
                Story ${nextStory.story_id}: ${escapeHtml(nextStory.title)}
            </div>
            <div class="text-xs text-bmad-muted mt-1">
                Status: Ready for Dev
            </div>
        </div>
    `;
}

/**
 * Calculate percentage from "X/Y tasks" string
 * @param {string} progressStr 
 * @returns {number} percentage 0-100
 */
function calculateProgress(progressStr) {
    if (!progressStr) return 0;

    // Match "2/8 tasks" or "2/8"
    const match = progressStr.match(/(\d+)\s*\/\s*(\d+)/);
    if (match && match[2] !== '0') {
        const completed = parseInt(match[1]);
        const total = parseInt(match[2]);
        return Math.min(100, Math.max(0, (completed / total) * 100));
    }
    return 0;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} str 
 */
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
