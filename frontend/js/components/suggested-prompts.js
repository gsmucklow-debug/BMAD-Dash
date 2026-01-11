/**
 * BMAD Dash - Suggested Prompts Component
 * Displays context-aware suggested prompts with click-to-send interaction
 */

export class SuggestedPrompts {
    /**
     * Initialize SuggestedPrompts component
     * @param {string} containerId - DOM element ID for rendering
     * @param {Function} onPromptClick - Callback when prompt is clicked (receives prompt text)
     */
    constructor(containerId, onPromptClick) {
        this.container = document.getElementById(containerId);
        this.onPromptClick = onPromptClick;
        this.currentPrompts = [];

        if (!this.container) {
            console.error(`SuggestedPrompts: Container "${containerId}" not found`);
        }
    }

    /**
     * Render suggested prompts
     * @param {Array<Object>} prompts - Array of prompt objects with {text, icon, category}
     */
    render(prompts) {
        if (!this.container) return;

        this.currentPrompts = prompts || [];

        if (this.currentPrompts.length === 0) {
            this.container.innerHTML = '';
            return;
        }

        this.container.innerHTML = `
            <div class="suggested-prompts-container">
                <div class="suggested-prompts-header">
                    <span class="suggested-prompts-title">Suggested Actions</span>
                </div>
                <div class="suggested-prompts-grid">
                    ${this.currentPrompts.map((prompt, index) => this._createPromptCard(prompt, index)).join('')}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Create HTML for a single prompt card
     * @param {Object} prompt - Prompt object {text, icon, category}
     * @param {number} index - Prompt index for unique IDs
     * @returns {string} HTML string
     * @private
     */
    _createPromptCard(prompt, index) {
        const categoryClass = `prompt-category-${prompt.category}`;

        return `
            <button 
                class="suggested-prompt-card ${categoryClass}" 
                data-prompt-index="${index}"
                data-prompt-text="${this._escapeHtml(prompt.text)}"
                data-prompt-icon="${this._escapeHtml(prompt.icon)}"
                aria-label="${this._escapeHtml(prompt.text)}"
                tabindex="0"
            >
                <span class="prompt-icon"></span>
                <span class="prompt-text">${this._escapeHtml(prompt.text)}</span>
            </button>
        `;
    }

    /**
     * Attach event listeners to prompt cards
     */
    attachEventListeners() {
        if (!this.container) return;

        const promptCards = this.container.querySelectorAll('.suggested-prompt-card');

        promptCards.forEach(card => {
            // Safely inject icon using textContent (XSS prevention)
            const iconElement = card.querySelector('.prompt-icon');
            const iconData = card.getAttribute('data-prompt-icon');
            if (iconElement && iconData) {
                iconElement.textContent = iconData;
            }

            // Click event
            card.addEventListener('click', (e) => {
                this._handlePromptClick(e);
            });

            // Keyboard events (Enter and Space)
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this._handlePromptClick(e);
                }
            });

            // Add touch-friendly hover effects
            card.addEventListener('mouseenter', (e) => {
                card.classList.add('hovered');
            });

            card.addEventListener('mouseleave', (e) => {
                card.classList.remove('hovered');
            });
        });
    }

    /**
     * Handle prompt card click/activation
     * @param {Event} event - Click or keyboard event
     * @private
     */
    _handlePromptClick(event) {
        const card = event.currentTarget;
        const promptText = card.getAttribute('data-prompt-text');

        if (!promptText) {
            console.error('SuggestedPrompts: No prompt text found on card');
            return;
        }

        // Add visual feedback
        card.classList.add('clicked');
        setTimeout(() => {
            card.classList.remove('clicked');
        }, 200);

        // Call the callback with prompt text
        if (this.onPromptClick && typeof this.onPromptClick === 'function') {
            this.onPromptClick(promptText);
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     * @private
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Clear all prompts
     */
    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.currentPrompts = [];
    }

    /**
     * Update prompts (convenience method)
     * @param {Array<Object>} prompts - New prompts to display
     */
    update(prompts) {
        this.render(prompts);
    }
}
