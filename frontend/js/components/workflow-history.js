/**
 * BMAD Dash - Workflow History Component
 * Displays workflow execution history and detected gaps for a story
 */

export class WorkflowHistory {
    constructor() {
        this.container = null;
    }

    /**
     * Render workflow history and gaps for a story
     * 
     * @param {Object} storyData - Story object with workflow_history and gaps
     * @returns {HTMLElement} - Rendered workflow history element
     */
    render(storyData) {
        const { workflow_history = [], gaps = [] } = storyData;
        
        // Create container
        const container = document.createElement('div');
        container.className = 'workflow-history';
        
        // Render gaps first (prominent warnings)
        if (gaps.length > 0) {
            const gapsSection = this._renderGaps(gaps);
            container.appendChild(gapsSection);
        }
        
        // Render workflow history
        if (workflow_history.length > 0) {
            const historySection = this._renderWorkflowHistory(workflow_history);
            container.appendChild(historySection);
        } else {
            // No workflow history found
            const emptyState = document.createElement('div');
            emptyState.className = 'workflow-history-empty';
            emptyState.textContent = 'No workflow history recorded yet';
            container.appendChild(emptyState);
        }
        
        this.container = container;
        return container;
    }

    /**
     * Render gap warning banners
     * 
     * @param {Array} gaps - Array of gap objects
     * @returns {HTMLElement} - Rendered gaps section
     */
    _renderGaps(gaps) {
        const section = document.createElement('div');
        section.className = 'workflow-gaps';
        
        const header = document.createElement('h4');
        header.className = 'workflow-gaps-header';
        header.textContent = '⚠️ Workflow Gaps Detected';
        section.appendChild(header);
        
        gaps.forEach(gap => {
            const gapBanner = this._renderGapBanner(gap);
            section.appendChild(gapBanner);
        });
        
        return section;
    }

    /**
     * Render individual gap banner
     * 
     * @param {Object} gap - Gap object with type, message, suggested_command, severity
     * @returns {HTMLElement} - Rendered gap banner
     */
    _renderGapBanner(gap) {
        const banner = document.createElement('div');
        banner.className = `gap-banner gap-${gap.severity}`;
        
        const message = document.createElement('div');
        message.className = 'gap-message';
        message.textContent = gap.message;
        banner.appendChild(message);
        
        const suggestion = document.createElement('div');
        suggestion.className = 'gap-suggestion';
        
        const commandLabel = document.createElement('span');
        commandLabel.className = 'gap-command-label';
        commandLabel.textContent = 'Fix it: ';
        suggestion.appendChild(commandLabel);
        
        const command = document.createElement('code');
        command.className = 'gap-command';
        command.textContent = gap.suggested_command;
        command.setAttribute('title', 'Click to copy command');
        command.style.cursor = 'pointer';
        command.addEventListener('click', () => {
            navigator.clipboard.writeText(gap.suggested_command);
            command.textContent = '✓ Copied!';
            setTimeout(() => {
                command.textContent = gap.suggested_command;
            }, 1000);
        });
        suggestion.appendChild(command);
        
        banner.appendChild(suggestion);
        
        return banner;
    }

    /**
     * Render workflow history timeline
     * 
     * @param {Array} workflowHistory - Array of workflow execution records
     * @returns {HTMLElement} - Rendered history section
     */
    _renderWorkflowHistory(workflowHistory) {
        const section = document.createElement('div');
        section.className = 'workflow-history-list';
        
        const header = document.createElement('h4');
        header.className = 'workflow-history-header';
        header.textContent = 'Workflow Execution History';
        section.appendChild(header);
        
        // Sort by timestamp (most recent first)
        const sortedHistory = [...workflowHistory].sort((a, b) => {
            const timeA = new Date(a.timestamp || 0);
            const timeB = new Date(b.timestamp || 0);
            return timeB - timeA;
        });
        
        const timeline = document.createElement('div');
        timeline.className = 'workflow-timeline';
        
        sortedHistory.forEach((workflow, index) => {
            const item = this._renderWorkflowItem(workflow, index === 0);
            timeline.appendChild(item);
        });
        
        section.appendChild(timeline);
        
        return section;
    }

    /**
     * Render individual workflow item
     * 
     * @param {Object} workflow - Workflow record with name, timestamp, result
     * @param {boolean} isMostRecent - Whether this is the most recent workflow
     * @returns {HTMLElement} - Rendered workflow item
     */
    _renderWorkflowItem(workflow, isMostRecent) {
        const item = document.createElement('div');
        item.className = `workflow-item ${isMostRecent ? 'workflow-item-latest' : ''}`;
        
        // Timeline dot
        const dot = document.createElement('div');
        dot.className = 'workflow-dot';
        item.appendChild(dot);
        
        // Content
        const content = document.createElement('div');
        content.className = 'workflow-content';
        
        const name = document.createElement('div');
        name.className = 'workflow-name';
        name.textContent = workflow.name || 'Unknown workflow';
        content.appendChild(name);
        
        const details = document.createElement('div');
        details.className = 'workflow-details';
        
        if (workflow.timestamp) {
            const timestamp = document.createElement('span');
            timestamp.className = 'workflow-timestamp';
            timestamp.textContent = this._formatTimestamp(workflow.timestamp);
            details.appendChild(timestamp);
        }
        
        if (workflow.result) {
            const status = document.createElement('span');
            status.className = `workflow-status workflow-status-${workflow.result.toLowerCase()}`;
            status.textContent = workflow.result;
            details.appendChild(status);
        }
        
        content.appendChild(details);
        item.appendChild(content);
        
        return item;
    }

    /**
     * Format timestamp for display
     * 
     * @param {string} timestamp - ISO timestamp string
     * @returns {string} - Formatted date/time
     */
    _formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        
        // Format: "Jan 10, 2026 at 2:30 PM"
        const options = {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        };
        
        return date.toLocaleDateString('en-US', options);
    }

    /**
     * Render workflow history and gaps as HTML string
     * Alternative to render() for template-based rendering
     *
     * @param {Object} storyData - Story object with workflow_history and gaps
     * @returns {string} HTML string for workflow history section
     */
    renderAsHtmlString(storyData) {
        const { workflow_history = [], gaps = [] } = storyData;
        
        // If no workflow history and no gaps, return empty string
        if (workflow_history.length === 0 && gaps.length === 0) {
            return '';
        }
        
        let html = `
            <div class="workflow-history-section border-t border-bmad-text opacity-20 pt-6">
                <h4 class="text-sm font-semibold text-bmad-text mb-3 flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Workflow History
                </h4>
        `;
        
        // Render gaps first (prominent warnings)
        if (gaps.length > 0) {
            html += `
                <div class="workflow-gaps mb-4">
            `;
            gaps.forEach(gap => {
                const severityClass = gap.severity === 'high' ? 'bg-red-900/20 border-red-500/30' :
                                      gap.severity === 'medium' ? 'bg-yellow-900/20 border-yellow-500/30' :
                                      'bg-blue-900/20 border-blue-500/30';
                html += `
                    <div class="gap-banner p-3 rounded border ${severityClass} mb-2">
                        <div class="flex items-start gap-2">
                            <span class="text-lg">${gap.message}</span>
                        </div>
                        <div class="flex items-center gap-2 mt-2">
                            <span class="text-xs text-bmad-muted">Fix it:</span>
                            <code class="bg-bmad-dark text-bmad-text font-mono text-xs px-2 py-1 rounded cursor-pointer hover:bg-bmad-surface transition-colors"
                                  title="Click to copy command"
                                  onclick="copyToClipboard('${gap.suggested_command}', this)">
                                ${this._escapeHtml(gap.suggested_command)}
                            </code>
                        </div>
                    </div>
                `;
            });
            html += `
                </div>
            `;
        }
        
        // Render workflow history
        if (workflow_history.length > 0) {
            html += `
                <div class="workflow-history-list">
            `;
            
            // Sort by timestamp (most recent first) - backend already sorts, but keep for consistency
            const sortedHistory = [...workflow_history].sort((a, b) => {
                const timeA = new Date(a.timestamp || 0);
                const timeB = new Date(b.timestamp || 0);
                return timeB - timeA;
            });
            
            sortedHistory.forEach((workflow, index) => {
                const isLatest = index === 0;
                html += this._renderWorkflowItemHtml(workflow, isLatest);
            });
            
            html += `
                </div>
            `;
        }
        
        html += `
            </div>
        `;
        
        return html;
    }

    /**
     * Render individual workflow item as HTML string
     *
     * @param {Object} workflow - Workflow record with name, timestamp, result
     * @param {boolean} isMostRecent - Whether this is the most recent workflow
     * @returns {string} HTML string for workflow item
     */
    _renderWorkflowItemHtml(workflow, isMostRecent) {
        const statusClass = workflow.result ? `workflow-status-${workflow.result.toLowerCase()}` : '';
        const latestClass = isMostRecent ? 'workflow-item-latest' : '';
        
        return `
            <div class="workflow-item flex gap-3 ${latestClass}">
                <div class="workflow-dot ${isMostRecent ? 'bg-blue-500' : 'bg-bmad-muted'}"></div>
                <div class="flex-1">
                    <div class="flex items-center justify-between">
                        <span class="text-sm font-medium text-bmad-text">${this._escapeHtml(workflow.name || 'Unknown workflow')}</span>
                        ${workflow.result ? `
                            <span class="text-xs px-2 py-0.5 rounded ${statusClass}">
                                ${this._escapeHtml(workflow.result)}
                            </span>
                        ` : ''}
                    </div>
                    ${workflow.timestamp ? `
                        <div class="text-xs text-bmad-muted mt-1">
                            ${this._formatTimestamp(workflow.timestamp)}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Clear the component
     */
    clear() {
        if (this.container) {
            this.container.remove();
            this.container = null;
        }
    }
}
