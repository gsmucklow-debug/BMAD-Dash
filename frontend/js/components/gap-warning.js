/**
 * BMAD Dash - Gap Warning Component
 * Displays proactive workflow gap warnings at dashboard level
 * Story 5.3: AI Agent Output Validation & Workflow Gap Warnings (AC3, AC4)
 */

export class GapWarning {
    constructor() {
        this.container = null;
        this.gapData = [];
    }

    /**
     * Escape HTML entities to prevent XSS attacks
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text safe for innerHTML
     */
    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Render proactive gap warnings for the entire project
     *
     * @param {Array} gaps - Array of gap objects from detect_workflow_gaps API
     * @returns {HTMLElement|null} - Rendered gap warnings element or null if no gaps
     */
    render(gaps = []) {
        this.gapData = gaps;

        // No gaps - return null (don't show anything)
        if (!gaps || gaps.length === 0) {
            return null;
        }

        // Create container
        const container = document.createElement('div');
        container.className = 'gap-warning-container';
        container.setAttribute('role', 'alert');
        container.setAttribute('aria-live', 'polite');

        // Create header
        const header = document.createElement('div');
        header.className = 'gap-warning-header';

        const icon = document.createElement('span');
        icon.className = 'gap-warning-icon';
        icon.textContent = '⚠️';

        const title = document.createElement('h3');
        title.className = 'gap-warning-title';
        title.textContent = `Workflow Gaps Detected (${gaps.length} ${gaps.length === 1 ? 'story' : 'stories'})`;

        header.appendChild(icon);
        header.appendChild(title);
        container.appendChild(header);

        // Create gap list
        const gapList = document.createElement('div');
        gapList.className = 'gap-warning-list';

        gaps.forEach(gapStory => {
            const gapItem = this._renderGapStory(gapStory);
            gapList.appendChild(gapItem);
        });

        container.appendChild(gapList);

        // Create dismiss button
        const dismissButton = document.createElement('button');
        dismissButton.className = 'gap-warning-dismiss';
        dismissButton.textContent = '✕ Dismiss';
        dismissButton.setAttribute('aria-label', 'Dismiss gap warnings');
        dismissButton.addEventListener('click', () => {
            container.remove();
        });
        container.appendChild(dismissButton);

        this.container = container;
        return container;
    }

    /**
     * Render a single story's gap information
     *
     * @param {Object} gapStory - Gap story object with story_id, gaps array, etc.
     * @returns {HTMLElement} - Rendered gap story element
     */
    _renderGapStory(gapStory) {
        const { story_id, story_title, story_key, gaps = [] } = gapStory;

        const item = document.createElement('div');
        item.className = 'gap-warning-item';

        // Story identifier (escaped to prevent XSS)
        const storyHeader = document.createElement('div');
        storyHeader.className = 'gap-warning-story-header';
        storyHeader.innerHTML = `<strong>Story ${this._escapeHtml(story_id)}</strong>: ${this._escapeHtml(story_title)}`;
        item.appendChild(storyHeader);

        // List individual gaps
        const gapDetails = document.createElement('ul');
        gapDetails.className = 'gap-warning-details';

        gaps.forEach(gap => {
            const gapItem = document.createElement('li');
            gapItem.className = `gap-warning-detail gap-severity-${gap.severity || 'medium'}`;

            // Gap message
            const message = document.createElement('span');
            message.className = 'gap-message';
            message.textContent = gap.message || gap.type;
            gapItem.appendChild(message);

            // Suggested command (AC4)
            if (gap.suggested_command) {
                const suggestion = document.createElement('div');
                suggestion.className = 'gap-suggestion';

                const suggestionLabel = document.createElement('span');
                suggestionLabel.className = 'gap-suggestion-label';
                suggestionLabel.textContent = 'Suggestion: ';

                const commandButton = document.createElement('button');
                commandButton.className = 'gap-command-button';
                commandButton.textContent = gap.suggested_command;
                commandButton.setAttribute('data-command', gap.suggested_command);
                commandButton.setAttribute('data-story-id', story_id);
                commandButton.addEventListener('click', (e) => {
                    this._copyCommandToClipboard(e.currentTarget.dataset.command, e.currentTarget);
                });

                suggestion.appendChild(suggestionLabel);
                suggestion.appendChild(commandButton);
                gapItem.appendChild(suggestion);
            }

            gapDetails.appendChild(gapItem);
        });

        item.appendChild(gapDetails);
        return item;
    }

    /**
     * Copy command to clipboard and show feedback
     *
     * @param {string} command - Command to copy
     * @param {HTMLElement} button - The button element that was clicked
     */
    _copyCommandToClipboard(command, button) {
        navigator.clipboard.writeText(command).then(() => {
            // Show temporary success feedback
            const feedback = document.createElement('span');
            feedback.className = 'copy-feedback';
            feedback.textContent = 'Copied!';
            feedback.style.cssText = 'color: green; margin-left: 8px; font-size: 12px;';

            button.parentNode.appendChild(feedback);

            setTimeout(() => {
                feedback.remove();
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy command:', err);
        });
    }

    /**
     * Fetch gap data from backend API
     *
     * @returns {Promise<Array>} - Array of gap objects
     */
    async fetchGaps() {
        try {
            const response = await fetch('/api/workflow-gaps');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data.gaps || [];
        } catch (error) {
            console.error('Error fetching workflow gaps:', error);
            return [];
        }
    }

    /**
     * Initialize and render gap warnings (called on dashboard load)
     *
     * @param {HTMLElement} targetElement - Element to insert warnings into
     */
    async initialize(targetElement) {
        const gaps = await this.fetchGaps();

        if (gaps.length > 0) {
            const warningElement = this.render(gaps);
            if (warningElement && targetElement) {
                // Insert at the top of the target element
                targetElement.insertBefore(warningElement, targetElement.firstChild);
            }
        }
    }
}
