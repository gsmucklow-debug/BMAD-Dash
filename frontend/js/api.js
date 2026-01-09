/**
 * BMAD Dash - API Client
 * Handles all backend API communication
 */

export class API {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    /**
     * Fetches dashboard data
     * Will be implemented in Story 1.2
     */
    async getDashboard() {
        throw new Error('Will be implemented in Story 1.2');
    }

    /**
     * Fetches Git evidence for a story
     * Will be implemented in Story 2.2
     */
    async getGitEvidence(storyId) {
        throw new Error('Will be implemented in Story 2.2');
    }

    /**
     * Fetches test evidence for a story
     * Will be implemented in Story 2.3
     */
    async getTestEvidence(storyId) {
        throw new Error('Will be implemented in Story 2.3');
    }

    /**
     * Sends AI chat message
     * Will be implemented in Story 3.1
     */
    async sendChatMessage(message, context) {
        throw new Error('Will be implemented in Story 3.1');
    }

    /**
     * Triggers cache refresh
     * Will be implemented in Story 1.2
     */
    async refresh() {
        throw new Error('Will be implemented in Story 1.2');
    }
}
