/**
 * BMAD Dash - Action Card Component
 * Three-layer card: Story > Task > Command with one-click copy
 * Story 4.1: Three-Layer Action Card & One-Click Command Copy
 */

/**
 * Render the Action Card component
 * Displays three layers: Story info, Task progress, and Command suggestion
 *
 * @param {Object} data - Action card data from API
 * @returns {string} HTML string for the action card
 */
export function renderActionCard(data) {
    if (!data || !data.action_card) {
        return '<div class="action-card-placeholder">No action card data available</div>';
    }

    const actionCard = data.action_card;
    const storyLayer = actionCard.story_layer;
    const taskLayer = actionCard.task_layer;
    const commandLayer = actionCard.command_layer;

    // Build acceptance criteria list (Layer 1)
    let acList = '';
    if (storyLayer && storyLayer.acceptance_criteria_summary && storyLayer.acceptance_criteria_summary.length > 0) {
        acList = '<ul class="list-disc list-inside text-sm text-bmad-text opacity-80 mt-2 space-y-1">';
        storyLayer.acceptance_criteria_summary.forEach(ac => {
            acList += `<li>${escapeHtml(ac)}</li>`;
        });
        acList += '</ul>';
    }

    return `
        <div class="action-card bg-bmad-gray border-2 border-blue-500 rounded-lg p-6 space-y-6 backdrop-blur-sm bg-opacity-90">
            <!-- Layer 1: Story -->
            ${storyLayer ? `
                <div class="story-layer">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="text-lg font-bold text-bmad-text">
                            Story ${escapeHtml(storyLayer.story_id)}: ${escapeHtml(storyLayer.title)}
                        </h3>
                        <div class="flex items-center gap-2">
                            <!-- Evidence Badges -->
                            <div id="action-card-badges-${escapeHtml(storyLayer.story_id)}">
                                <!-- Badges will be dynamically loaded -->
                            </div>
                            <span class="status-badge px-3 py-1 rounded text-xs font-semibold ${getStatusColor(storyLayer.status)}">
                                ${escapeHtml(storyLayer.status.toUpperCase())}
                            </span>
                        </div>
                    </div>
                    ${acList}
                </div>
                <div class="layer-separator border-t border-bmad-text opacity-20"></div>
            ` : ''}

            <!-- Layer 2: Task -->
            ${taskLayer ? `
                <div class="task-layer">
                    <div class="flex items-center justify-between">
                        <p class="text-md text-bmad-text">
                            <span class="font-semibold text-blue-400">${escapeHtml(taskLayer.progress)}:</span>
                            ${escapeHtml(taskLayer.title)}
                        </p>
                    </div>
                </div>
                <div class="layer-separator border-t border-bmad-text opacity-20"></div>
            ` : ''}

            <!-- Layer 3: Command -->
            ${commandLayer ? `
                <div class="command-layer">
                    <p class="text-sm text-bmad-text opacity-80 mb-3">
                        ${escapeHtml(commandLayer.description)}
                    </p>
                    <div class="flex items-center gap-3">
                        <code id="action-command" class="flex-1 bg-bmad-dark text-bmad-text font-mono text-sm px-4 py-2 rounded select-all">
                            ${escapeHtml(commandLayer.command)}
                        </code>
                        <button
                            id="action-copy-btn"
                            class="copy-button min-h-[44px] min-w-[44px] bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-2 rounded transition-colors"
                            aria-label="Copy command to clipboard"
                        >
                            Copy
                        </button>
                    </div>
                    <!-- ARIA live region for screen reader feedback -->
                    <div id="action-copy-status" aria-live="polite" aria-atomic="true" class="sr-only"></div>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Attach event listeners to the action card after rendering
 * Must be called after the HTML is inserted into the DOM
 *
 * @param {Object} data - Action card data from API
 */
export function attachActionCardListeners(data) {
    if (!data || !data.action_card || !data.action_card.command_layer) {
        return;
    }

    const copyButton = document.getElementById('action-copy-btn');
    const statusRegion = document.getElementById('action-copy-status');
    const command = data.action_card.command_layer.command;

    if (!copyButton) {
        return;
    }

    // Initialize evidence badges for current story
    const storyLayer = data.action_card.story_layer;
    if (storyLayer && storyLayer.story_id && data.project && data.project.root_path) {
        const badgeContainerId = `action-card-badges-${storyLayer.story_id}`;
        const badgeContainer = document.getElementById(badgeContainerId);
        if (badgeContainer) {
            // Dynamically import and use evidence badge module
            import('../components/evidence-badge.js').then(module => {
                badgeContainer.innerHTML = module.getBadgesSkeletonHTML();
                module.updateBadges(badgeContainerId, storyLayer.story_id, data.project.root_path);
            }).catch(error => {
                console.error('Failed to load evidence badges:', error);
            });
        }
    }

    // Track copy state to reset on next click (NFR17: no time-limited interactions)
    let isCopied = false;

    copyButton.addEventListener('click', async () => {
        // Reset state if already showing success/error
        if (isCopied) {
            copyButton.textContent = 'Copy';
            copyButton.classList.remove('bg-green-600', 'bg-red-600');
            copyButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
            isCopied = false;
            return; // Exit early - don't copy again immediately
        }

        try {
            await navigator.clipboard.writeText(command);

            // Provide persistent visual feedback (NFR17: no auto-dismiss)
            copyButton.textContent = '✓ Copied!';
            copyButton.classList.add('bg-green-600');
            copyButton.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            isCopied = true;

            // Update ARIA live region for screen readers
            if (statusRegion) {
                statusRegion.textContent = 'Command copied to clipboard';
            }
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);

            // Show persistent error with guidance (NFR17: no auto-dismiss)
            copyButton.textContent = '✗ Failed';
            copyButton.classList.add('bg-red-600');
            copyButton.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            isCopied = true;

            // Update ARIA live region for screen readers
            if (statusRegion) {
                statusRegion.textContent = 'Copy failed. Please select the command text manually.';
            }
        }
    });

    // Add keyboard support (Enter/Space)
    copyButton.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            copyButton.click();
        }
    });
}

/**
 * Get status color class based on story status
 * @param {string} status - Story status
 * @returns {string} Tailwind color classes
 */
function getStatusColor(status) {
    const statusColors = {
        'todo': 'bg-gray-600 text-white',
        'backlog': 'bg-gray-600 text-white',
        'ready-for-dev': 'bg-blue-600 text-white',
        'in-progress': 'bg-yellow-600 text-white',
        'review': 'bg-purple-600 text-white',
        'done': 'bg-green-600 text-white'
    };
    return statusColors[status] || 'bg-gray-600 text-white';
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
