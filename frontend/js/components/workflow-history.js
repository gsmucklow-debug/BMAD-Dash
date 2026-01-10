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
     * Clear the component
     */
    clear() {
        if (this.container) {
            this.container.remove();
            this.container = null;
        }
    }
}
