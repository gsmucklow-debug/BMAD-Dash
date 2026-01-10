/**
 * BMAD Dash - List View
 * Minimal view for brain fog days - shows only current task and next action
 * Story 3.3: Minimal List View & Manual Refresh
 */

/**
 * Render the List View - optimized for minimal cognitive load
 * Shows maximum 3 items: story title, current task, next action command
 *
 * @param {Object} data - Dashboard data from API
 */
export function render(data) {
    const startTime = performance.now();

    const container = document.getElementById('main-content');
    if (!container) {
        console.error('Main content container not found');
        return;
    }

    // Extract data (minimal info only)
    // API returns quick_glance.current, not quick_glance.current_story
    const currentStory = data.quick_glance?.current || null;
    const currentTask = currentStory?.current_task || 'No active task';
    const storyTitle = currentStory?.title || 'No Active Story';

    // Get next command from action card or provide default
    const nextCommand = data.action_card?.command || '/bmad-bmm-workflows-dev-story';

    // Render minimal UI - exactly 3 information items
    container.innerHTML = `
        <div class="list-view flex flex-col items-center justify-center min-h-screen bg-bmad-dark text-bmad-text p-8">
            <div class="max-w-2xl w-full space-y-8">
                <!-- Story Title (Large, prominent) -->
                <h1 class="list-story-title text-4xl font-bold text-center text-bmad-text">
                    ${escapeHtml(storyTitle)}
                </h1>

                <!-- Current Task Description -->
                <p class="list-task-description text-xl text-center text-bmad-text">
                    ${escapeHtml(currentTask)}
                </p>

                <!-- Next Action Command with Copy Button -->
                <div class="list-command-container bg-bmad-gray p-6 rounded-lg">
                    <code class="list-command text-lg block mb-4 text-bmad-text font-mono break-all select-all">
                        ${escapeHtml(nextCommand)}
                    </code>
                    <button
                        id="copy-command-btn"
                        class="copy-button w-full min-h-[44px] min-w-[44px] bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded transition-colors"
                        aria-label="Copy command to clipboard"
                    >
                        Copy Command
                    </button>
                    <!-- ARIA live region for screen reader feedback (NFR accessibility) -->
                    <div id="copy-status" aria-live="polite" aria-atomic="true" class="sr-only"></div>
                </div>
            </div>
        </div>
    `;

    // Add copy functionality
    const copyButton = document.getElementById('copy-command-btn');
    const statusRegion = document.getElementById('copy-status');

    if (copyButton) {
        // Track copy state to reset on next click (NFR17: no time-limited interactions)
        let isCopied = false;

        copyButton.addEventListener('click', async () => {
            // Reset state if already showing success/error
            if (isCopied) {
                copyButton.textContent = 'Copy Command';
                copyButton.classList.remove('bg-green-600', 'bg-red-600');
                copyButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
                isCopied = false;
            }

            try {
                await navigator.clipboard.writeText(nextCommand);

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
                copyButton.textContent = '✗ Copy Failed - Select text manually';
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

    // Performance check: Render time should be <50ms (NFR)
    const renderTime = performance.now() - startTime;
    // console.log(`List view rendered in ${renderTime.toFixed(2)}ms`);

    if (renderTime > 50) {
        console.warn(`⚠ List view render exceeded 50ms target: ${renderTime.toFixed(2)}ms`);
    }
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
