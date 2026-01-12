/**
 * BMAD Dash - AI Chat Component
 * Right sidebar chat interface with streaming support
 */

import { API } from '../api.js';
import { SuggestedPrompts } from './suggested-prompts.js';
import { PromptGenerator } from '../utils/prompt-generator.js';

export class AIChat {
    constructor(containerId, api = new API()) {
        this.container = document.getElementById(containerId);
        this.api = api;
        this.messages = [];
        this.isExpanded = true;
        this.isStreaming = false;

        // Initialize suggested prompts (Story 5.2)
        this.promptGenerator = new PromptGenerator();
        this.suggestedPrompts = null; // Will be initialized after render

        this.init();
    }

    init() {
        if (!this.container) {
            console.error(`AI Chat container not found: ${this.containerId}`);
            return;
        }

        this.render();
        this.attachEventListeners();
    }

    render() {
        this.container.innerHTML = `
            <div class="ai-chat-sidebar ${this.isExpanded ? 'expanded' : 'collapsed'}">
                <div id="ai-suggested-prompts"></div>
                
                <div class="ai-chat-messages custom-scrollbar" id="ai-chat-messages">
                    <div class="ai-message ai-message-assistant animate-fadeIn">
                        <div class="ai-message-content">
                            <p>Hello! I'm your BMAD Coach. I'm aware of your current project state and ready to help. What would you like to know?</p>
                        </div>
                    </div>
                </div>
                
                <div class="ai-chat-input-area">
                    <div class="ai-chat-input-wrapper">
                        <textarea 
                            id="ai-chat-input" 
                            class="ai-chat-textarea" 
                            placeholder="Type a message..."
                            rows="1"
                        ></textarea>
                        <button id="ai-chat-send" class="ai-chat-send-btn" aria-label="Send message">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Store references to DOM elements
        this.messagesContainer = document.getElementById('ai-chat-messages');
        this.inputTextarea = document.getElementById('ai-chat-input');
        this.sendButton = document.getElementById('ai-chat-send');

        // Initialize suggested prompts component
        this.suggestedPrompts = new SuggestedPrompts('ai-suggested-prompts', (promptText) => {
            this.sendProgrammaticMessage(promptText);
        });

        // Generate and render initial prompts
        this.updateSuggestedPrompts();

        // Auto-resize textarea
        this.inputTextarea.addEventListener('input', () => {
            this.inputTextarea.style.height = 'auto';
            this.inputTextarea.style.height = (this.inputTextarea.scrollHeight) + 'px';
        });
    }

    attachEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key (Shift+Enter for new line)
        this.inputTextarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Clear chat (added to toggle menu or similar in future, for now simplified)
    }



    async sendMessage() {
        const message = this.inputTextarea.value.trim();

        if (!message || this.isStreaming) {
            return;
        }

        // Add user message to chat
        this.addMessage(message, 'user');

        // Clear input
        this.inputTextarea.value = '';

        // Create assistant message placeholder
        const assistantMessageId = this.addMessage('', 'assistant', true);

        // Set streaming state
        this.isStreaming = true;
        this.sendButton.disabled = true;
        this.sendButton.innerHTML = '<span class="ai-chat-loading">...</span>';

        // Get project context from state (will be integrated with state.js)
        const context = this.getProjectContext();

        try {
            let fullResponse = '';

            await this.api.streamChatResponse(
                message,
                context,
                // onToken callback
                (token) => {
                    fullResponse += token;
                    this.updateMessage(assistantMessageId, fullResponse);
                },
                // onError callback
                (error) => {
                    this.updateMessage(assistantMessageId, `Error: ${error}`);
                },
                // onComplete callback
                () => {
                    this.isStreaming = false;
                    this.sendButton.disabled = false;
                    this.sendButton.innerHTML = `
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    `;
                    this.addCopyButtonsToCodeBlocks();
                }
            );
        } catch (error) {
            console.error('Error sending message:', error);
            this.updateMessage(assistantMessageId, `Error: ${error.message}`);
            this.isStreaming = false;
            this.sendButton.disabled = false;
            this.sendButton.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
            `;
        }
    }

    addMessage(content, role, isStreaming = false) {
        // Use combination of timestamp and random suffix for unique IDs
        const messageId = `ai-message-${role}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const messageElement = document.createElement('div');
        messageElement.id = messageId;
        messageElement.className = `ai-message ai-message-${role}`;

        const streamingIndicator = isStreaming ? '<span class="ai-streaming-indicator">●</span>' : '';

        messageElement.innerHTML = `
            <div class="ai-message-content">
                ${this.formatMessage(content)}
                ${streamingIndicator}
            </div>
        `;

        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();

        return messageId;
    }

    updateMessage(messageId, content) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            const contentElement = messageElement.querySelector('.ai-message-content');
            const streamingIndicator = contentElement.querySelector('.ai-streaming-indicator');

            contentElement.innerHTML = this.formatMessage(content);

            if (streamingIndicator) {
                contentElement.appendChild(streamingIndicator);
            }

            this.scrollToBottom();
        }
    }

    formatMessage(content) {
        if (!content) return '';

        // Improved markdown formatting with better edge case handling
        // Code blocks (process first to avoid conflicts)
        content = content.replace(/```([\w]*)?\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre class="ai-code-block"><code class="language-${lang || 'text'}">${this.escapeHtml(code.trim())}</code><button class="ai-copy-code-btn" aria-label="Copy code">Copy</button></pre>`;
        });

        // Inline code (match non-greedy, avoid conflicts with code blocks)
        content = content.replace(/`([^`\n]+?)`/g, '<code class="ai-inline-code">$1</code>');

        // Bold (non-greedy, avoid matching single asterisks)
        content = content.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>');

        // Italic (non-greedy, require space or start/end of line to avoid conflicts)
        content = content.replace(/(^|\s)\*([^*\n]+?)\*(\s|$)/g, '$1<em>$2</em>$3');

        // Line breaks
        content = content.replace(/\n/g, '<br>');

        return content;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    clearChat() {
        this.messages = [];
        this.messagesContainer.innerHTML = `
            <div class="ai-message ai-message-assistant animate-fadeIn">
                <div class="ai-message-content">
                    <p>Hello! I'm your BMAD Coach. I'm aware of your current project state and ready to help. What would you like to know?</p>
                </div>
            </div>
        `;
    }



    addCopyButtonsToCodeBlocks() {
        const codeBlocks = this.messagesContainer.querySelectorAll('.ai-code-block');
        codeBlocks.forEach(block => {
            const copyBtn = block.querySelector('.ai-copy-code-btn');
            if (copyBtn && !copyBtn.hasListener) {
                copyBtn.addEventListener('click', () => {
                    const code = block.querySelector('code').textContent;
                    navigator.clipboard.writeText(code).then(() => {
                        copyBtn.textContent = 'Copied!';
                        setTimeout(() => {
                            copyBtn.textContent = 'Copy';
                        }, 2000);
                    });
                });
                copyBtn.hasListener = true;
            }
        });
    }

    /**
     * Set project context externally
     * @param {Object} context - Project context (phase, epic, story, task)
     */
    setProjectContext(context) {
        console.log('AIChat context updated:', context);
        this.projectContext = context;
    }

    /**
     * Get current project context
     * @returns {Object} Project context
     */
    getProjectContext() {
        // Return minimal/unknown context if not set - avoid hardcoded fallbacks
        return this.projectContext || {
            phase: 'Unknown',
            epicId: 'Unknown',
            epic: 'Unknown',
            storyId: 'Unknown',
            story: 'Unknown',
            storyTitle: '',
            storyStatus: 'Unknown',
            task: ''
        };
    }

    /**
     * Send a message programmatically (for suggested prompts)
     * @param {string} text - Message text to send
     */
    sendProgrammaticMessage(text) {
        if (!text || this.isStreaming) {
            return;
        }

        // Set the input value and trigger send
        this.inputTextarea.value = text;
        this.sendMessage();
    }

    /**
     * Update suggested prompts based on current project context
     */
    updateSuggestedPrompts() {
        if (!this.suggestedPrompts) return;

        const context = this.getProjectContext();
        const prompts = this.promptGenerator.generatePrompts(context);
        this.suggestedPrompts.render(prompts);
    }
}
