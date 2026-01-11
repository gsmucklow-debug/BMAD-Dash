/**
 * BMAD Dash - Prompt Generator Utility
 * Generates context-aware suggested prompts based on project state
 */

export class PromptGenerator {
    constructor() {
        this.promptTemplates = this._initializeTemplates();
    }

    /**
     * Initialize prompt templates for each story status
     * @returns {Object} Template mappings
     * @private
     */
    _initializeTemplates() {
        return {
            'TODO': [
                {
                    text: 'How do I start Story {storyId}?',
                    icon: '🚀',
                    category: 'workflow'
                },
                {
                    text: 'What are the acceptance criteria for this story?',
                    icon: '✓',
                    category: 'info'
                },
                {
                    text: 'What should I do next?',
                    icon: '🎯',
                    category: 'workflow'
                },
                {
                    text: 'Show me the architecture for Epic {epicId}',
                    icon: '🏗️',
                    category: 'info'
                }
            ],
            'IN_PROGRESS': [
                {
                    text: 'What tasks remain in Story {storyId}?',
                    icon: '📋',
                    category: 'workflow'
                },
                {
                    text: 'Show me the acceptance criteria',
                    icon: '✓',
                    category: 'info'
                },
                {
                    text: 'Should I run code-review now?',
                    icon: '🔍',
                    category: 'workflow'
                },
                {
                    text: 'What should I do next?',
                    icon: '🎯',
                    category: 'workflow'
                }
            ],
            'REVIEW': [
                {
                    text: 'Did the AI agent complete Story {storyId} correctly?',
                    icon: '🤖',
                    category: 'validation'
                },
                {
                    text: 'Should I run code-review workflow?',
                    icon: '🔍',
                    category: 'workflow'
                },
                {
                    text: 'What\'s the status of my current epic?',
                    icon: '📊',
                    category: 'info'
                },
                {
                    text: 'What should I do next?',
                    icon: '🎯',
                    category: 'workflow'
                }
            ],
            'COMPLETE': [
                {
                    text: 'What\'s my next story?',
                    icon: '➡️',
                    category: 'workflow'
                },
                {
                    text: 'Show me the sprint status',
                    icon: '📊',
                    category: 'info'
                },
                {
                    text: 'Should I run retrospective for Epic {epicId}?',
                    icon: '🔄',
                    category: 'workflow'
                },
                {
                    text: 'What should I do next?',
                    icon: '🎯',
                    category: 'workflow'
                }
            ],
            'DEFAULT': [
                {
                    text: 'What should I do next?',
                    icon: '🎯',
                    category: 'workflow'
                },
                {
                    text: 'What\'s my current story status?',
                    icon: '📊',
                    category: 'info'
                },
                {
                    text: 'Show me my progress',
                    icon: '📈',
                    category: 'info'
                },
                {
                    text: 'Explain the BMAD Method',
                    icon: '📚',
                    category: 'help'
                }
            ]
        };
    }

    /**
     * Generate prompts for current project context
     * @param {Object} context - Project context
     * @param {string} context.storyId - Current story ID (e.g., '5.2')
     * @param {string} context.storyStatus - Story status (TODO/IN_PROGRESS/REVIEW/COMPLETE)
     * @param {string} context.epicId - Current epic ID (e.g., 'epic-5')
     * @param {string} context.storyTitle - Current story title
     * @returns {Array<Object>} Array of prompt objects
     */
    generatePrompts(context) {
        const { storyStatus = 'DEFAULT', storyId = 'X.X', epicId = 'epic-X', storyTitle = 'Unknown' } = context;

        // Normalize status to uppercase and replace spaces/hyphens
        const normalizedStatus = this._normalizeStatus(storyStatus);

        // Get templates for this status, fallback to DEFAULT
        const templates = this.promptTemplates[normalizedStatus] || this.promptTemplates['DEFAULT'];

        // Substitute placeholders with actual values
        return templates.map(template => ({
            ...template,
            text: this._substituteValues(template.text, {
                storyId,
                epicId,
                storyTitle
            })
        }));
    }

    /**
     * Normalize status string to match template keys
     * @param {string} status - Raw status string
     * @returns {string} Normalized status
     * @private
     */
    _normalizeStatus(status) {
        if (!status) return 'DEFAULT';

        const normalized = status.toString().toUpperCase().replace(/[-\s]/g, '_');

        // Map common variations
        const statusMap = {
            'READY_FOR_DEV': 'TODO',
            'BACKLOG': 'TODO',
            'DONE': 'COMPLETE',
            'COMPLETED': 'COMPLETE',
            'IN_REVIEW': 'REVIEW'
        };

        return statusMap[normalized] || normalized;
    }

    /**
     * Substitute template placeholders with actual values
     * @param {string} text - Template text with {placeholders}
     * @param {Object} values - Values to substitute
     * @returns {string} Text with substituted values
     * @private
     */
    _substituteValues(text, values) {
        let result = text;

        Object.keys(values).forEach(key => {
            const placeholder = `{${key}}`;
            result = result.replace(new RegExp(placeholder, 'g'), values[key]);
        });

        return result;
    }

    /**
     * Get all available prompt categories
     * @returns {Array<string>} Category names
     */
    getCategories() {
        return ['workflow', 'info', 'validation', 'help'];
    }

    /**
     * Filter prompts by category
     * @param {Array<Object>} prompts - Prompts to filter
     * @param {string} category - Category to filter by
     * @returns {Array<Object>} Filtered prompts
     */
    filterByCategory(prompts, category) {
        return prompts.filter(prompt => prompt.category === category);
    }
}
