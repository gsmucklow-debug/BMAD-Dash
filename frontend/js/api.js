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
     Will be implemented in Story 1.2
     */
    async getDashboard() {
        throw new Error('Will be implemented in Story 1.2');
    }

    /**
     * Fetches Git evidence for a story
     Will be implemented in Story 2.2
     */
    async getGitEvidence(storyId) {
        throw new Error('Will be implemented in Story 2.2');
    }

    /**
     * Fetches test evidence for a story
     Will be implemented in Story 2.3
     */
    async getTestEvidence(storyId) {
        throw new Error('Will be implemented in Story 2.3');
    }

    /**
     * Sends AI chat message with streaming response
     
     * @param {string} message - User's question or prompt
     * @param {Object} context - Project context (phase, epic, story, task)
     * @param {Function} onToken - Callback function for each token received
     * @param {Function} onError - Callback function for errors
     * @param {Function} onComplete - Callback function when stream completes
     * @returns {Promise<void>} - Resolves when stream completes
     */
    async streamChatResponse(message, context, onToken, onError, onComplete) {
        try {
            const response = await fetch(`${this.baseUrl}/api/ai-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    project_context: context
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    if (onComplete) onComplete();
                    break;
                }

                // Decode the chunk and add to buffer
                buffer += decoder.decode(value, { stream: true });

                // Process complete SSE messages
                const lines = buffer.split('\n\n');
                buffer = lines.pop() || ''; // Keep incomplete message in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.error) {
                                if (onError) onError(data.error);
                            } else if (data.token) {
                                if (onToken) onToken(data.token);
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }
        } catch (error) {
            if (onError) onError(error.message);
            throw error;
        }
    }

    /**
     * Sends AI chat message (non-streaming, for backward compatibility)
     Will be deprecated in favor of streamChatResponse
     */
    async sendChatMessage(message, context) {
        throw new Error('Use streamChatResponse instead for streaming support');
    }

    /**
     * Triggers cache refresh
     Will be implemented in Story 1.2
     */
    async refresh() {
        throw new Error('Will be implemented in Story 1.2');
    }

    /**
     * Get SmartCache statistics
     * Story 5.55: Smart Per-Project Cache Layer
     * @param {string} projectRoot - Path to project root
     * @returns {Promise<Object>} Cache statistics
     */
    async getCacheStats(projectRoot) {
        try {
            const response = await fetch(`${this.baseUrl}/api/cache/stats?project_root=${encodeURIComponent(projectRoot)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Get cache stats failed:', error);
            return null;
        }
    }

    /**
     * Clear all SmartCache data for project
     * Story 5.55: Smart Per-Project Cache Layer
     * @param {string} projectRoot - Path to project root
     * @returns {Promise<Object>} Response with success status
     */
    async clearCache(projectRoot) {
        try {
            const response = await fetch(`${this.baseUrl}/api/cache/clear?project_root=${encodeURIComponent(projectRoot)}`, {
                method: 'POST'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Clear cache failed:', error);
            throw error;
        }
    }

    /**
     * Invalidate SmartCache for a specific story
     * Story 5.55: Smart Per-Project Cache Layer
     * @param {string} projectRoot - Path to project root
     * @param {string} storyId - Story identifier (e.g., "5.4")
     * @returns {Promise<Object>} Response with success status
     */
    async invalidateStoryCache(projectRoot, storyId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/cache/invalidate/${storyId}?project_root=${encodeURIComponent(projectRoot)}`, {
                method: 'POST'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Invalidate story cache failed:', error);
            throw error;
        }
    }

    /**
     * Checks AI chat service health
     * @returns {Promise<Object>} Health status
     */
    async checkAIHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/api/ai-chat/health`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('AI health check failed:', error);
            return { status: 'error', api_key_configured: false };
        }
    }
}
