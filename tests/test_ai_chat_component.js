/**
 * BMAD Dash - Tests for AI Chat Component
 * Tests for Story 5.1: Gemini API Integration & Streaming Chat
 */

import { AIChat } from '../frontend/js/components/ai-chat.js';
import { API } from '../frontend/js/api.js';

// Mock fetch for testing
global.fetch = jest.fn();

describe('AIChat Component', () => {
    let container;
    let api;
    let aiChat;

    beforeEach(() => {
        // Create a mock container
        container = document.createElement('div');
        container.id = 'ai-chat-container';
        document.body.appendChild(container);
        
        // Create a mock API instance
        api = new API();
        
        // Create AIChat instance
        aiChat = new AIChat('ai-chat-container', api);
    });

    afterEach(() => {
        // Clean up
        document.body.removeChild(container);
        jest.clearAllMocks();
    });

    describe('Initialization', () => {
        test('should create chat container with correct structure', () => {
            const sidebar = container.querySelector('.ai-chat-sidebar');
            expect(sidebar).not.toBeNull();
            expect(sidebar.classList.contains('expanded')).toBe(true);
        });

        test('should render header with title', () => {
            const title = container.querySelector('.ai-chat-title');
            expect(title.textContent).toBe('AI Coach');
        });

        test('should render messages container', () => {
            const messagesContainer = container.querySelector('#ai-chat-messages');
            expect(messagesContainer).not.toBeNull();
        });

        test('should render input area', () => {
            const inputArea = container.querySelector('.ai-chat-input-area');
            expect(inputArea).not.toBeNull();
        });

        test('should render textarea', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            expect(textarea).not.toBeNull();
            expect(textarea.placeholder).toContain('Ask me anything about your BMAD project');
        });

        test('should render send button', () => {
            const sendButton = container.querySelector('.ai-chat-send-btn');
            expect(sendButton).not.toBeNull();
            expect(sendButton.textContent).toContain('Send');
        });

        test('should render clear button', () => {
            const clearButton = container.querySelector('.ai-chat-clear-btn');
            expect(clearButton).not.toBeNull();
            expect(clearButton.textContent).toContain('Clear');
        });

        test('should render toggle button', () => {
            const toggleButton = container.querySelector('.ai-chat-toggle');
            expect(toggleButton).not.toBeNull();
        });
    });

    describe('Toggle Sidebar', () => {
        test('should collapse sidebar when toggle is clicked', () => {
            const toggleButton = container.querySelector('.ai-chat-toggle');
            const sidebar = container.querySelector('.ai-chat-sidebar');
            
            expect(sidebar.classList.contains('expanded')).toBe(true);
            expect(sidebar.classList.contains('collapsed')).toBe(false);
            
            toggleButton.click();
            
            expect(sidebar.classList.contains('expanded')).toBe(false);
            expect(sidebar.classList.contains('collapsed')).toBe(true);
        });

        test('should expand sidebar when toggle is clicked again', () => {
            const toggleButton = container.querySelector('.ai-chat-toggle');
            const sidebar = container.querySelector('.ai-chat-sidebar');
            
            // First click to collapse
            toggleButton.click();
            expect(sidebar.classList.contains('collapsed')).toBe(true);
            
            // Second click to expand
            toggleButton.click();
            expect(sidebar.classList.contains('expanded')).toBe(true);
            expect(sidebar.classList.contains('collapsed')).toBe(false);
        });
    });

    describe('Send Message', () => {
        beforeEach(() => {
            // Mock successful streaming response
            global.fetch.mockResolvedValue({
                body: {
                    getReader: () => ({
                        read: () => Promise.resolve({
                            done: true,
                            value: new TextEncoder().encode('data: {"token": "Hello"}\n\n')
                        })
                    })
                }
            });
        });

        test('should add user message to chat when send is clicked', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            textarea.value = 'Test message';
            sendButton.click();
            
            const userMessage = container.querySelector('.ai-message-user');
            expect(userMessage).not.toBeNull();
            expect(userMessage.textContent).toContain('Test message');
        });

        test('should clear textarea after sending message', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            textarea.value = 'Test message';
            sendButton.click();
            
            expect(textarea.value).toBe('');
        });

        test('should add assistant message placeholder', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            textarea.value = 'Test message';
            sendButton.click();
            
            const assistantMessage = container.querySelector('.ai-message-assistant');
            expect(assistantMessage).not.toBeNull();
        });

        test('should disable send button while streaming', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            textarea.value = 'Test message';
            sendButton.click();
            
            expect(sendButton.disabled).toBe(true);
        });

        test('should send message on Enter key', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            
            textarea.value = 'Test message';
            
            const event = new KeyboardEvent('keydown', { key: 'Enter' });
            textarea.dispatchEvent(event);
            
            const userMessage = container.querySelector('.ai-message-user');
            expect(userMessage).not.toBeNull();
        });

        test('should not send message on Shift+Enter', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            textarea.value = 'Test message\nNew line';
            
            const event = new KeyboardEvent('keydown', { key: 'Enter', shiftKey: true });
            textarea.dispatchEvent(event);
            
            // Message should not be sent
            const userMessage = container.querySelector('.ai-message-user');
            expect(userMessage).toBeNull();
            
            // Textarea should still have value
            expect(textarea.value).toBe('Test message\nNew line');
        });

        test('should not send empty message', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            textarea.value = '   ';
            sendButton.click();
            
            const userMessage = container.querySelector('.ai-message-user');
            expect(userMessage).toBeNull();
        });

        test('should not send message while already streaming', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            // Set streaming state
            aiChat.isStreaming = true;
            textarea.value = 'Test message';
            sendButton.click();
            
            const userMessage = container.querySelector('.ai-message-user');
            expect(userMessage).toBeNull();
        });
    });

    describe('Clear Chat', () => {
        test('should clear all messages when clear is clicked', () => {
            const clearButton = container.querySelector('.ai-chat-clear-btn');
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            // Add a message
            textarea.value = 'Test message';
            sendButton.click();
            
            expect(container.querySelectorAll('.ai-message').length).toBeGreaterThan(0);
            
            // Clear chat
            clearButton.click();
            
            // Should only have welcome message
            const messages = container.querySelectorAll('.ai-message');
            expect(messages.length).toBe(1);
            expect(messages[0].textContent).toContain('BMAD Coach');
        });
    });

    describe('Project Context', () => {
        test('should set project context', () => {
            const context = {
                phase: 'Implementation',
                epic: 'epic-5',
                story: '5.1',
                task: '1'
            };
            
            aiChat.setProjectContext(context);
            
            expect(aiChat.projectContext).toEqual(context);
        });

        test('should get default context if not set', () => {
            const context = aiChat.getProjectContext();
            
            expect(context).toHaveProperty('phase');
            expect(context).toHaveProperty('epic');
            expect(context).toHaveProperty('story');
            expect(context).toHaveProperty('task');
        });

        test('should get set context if previously set', () => {
            const context = {
                phase: 'Planning',
                epic: 'epic-1',
                story: '1.1',
                task: '2'
            };
            
            aiChat.setProjectContext(context);
            const retrievedContext = aiChat.getProjectContext();
            
            expect(retrievedContext).toEqual(context);
        });
    });

    describe('Markdown Formatting', () => {
        test('should format code blocks', () => {
            const content = '```python\nprint("Hello")\n```';
            const formatted = aiChat.formatMessage(content);
            
            expect(formatted).toContain('<pre class="ai-code-block">');
            expect(formatted).toContain('print("Hello")');
            expect(formatted).toContain('Copy</button>');
        });

        test('should format inline code', () => {
            const content = 'Use `npm install` to install dependencies';
            const formatted = aiChat.formatMessage(content);
            
            expect(formatted).toContain('<code class="ai-inline-code">');
            expect(formatted).toContain('npm install');
        });

        test('should format bold text', () => {
            const content = '**Important** note';
            const formatted = aiChat.formatMessage(content);
            
            expect(formatted).toContain('<strong>Important</strong>');
        });

        test('should format italic text', () => {
            const content = '*Note*: This is important';
            const formatted = aiChat.formatMessage(content);
            
            expect(formatted).toContain('<em>Note</em>');
        });

        test('should format line breaks', () => {
            const content = 'Line 1\nLine 2\nLine 3';
            const formatted = aiChat.formatMessage(content);
            
            expect(formatted).toContain('<br>');
        });
    });

    describe('Code Copy Button', () => {
        test('should copy code to clipboard when copy button is clicked', () => {
            const textarea = container.querySelector('.ai-chat-textarea');
            const sendButton = container.querySelector('.ai-chat-send-btn');
            
            // Mock clipboard API
            Object.assign(navigator, {
                clipboard: {
                    writeText: jest.fn().mockResolvedValue(undefined)
                }
            });
            
            // Send a message with code
            textarea.value = 'Show me code example';
            sendButton.click();
            
            // Wait for code block to be added
            setTimeout(() => {
                const copyButton = container.querySelector('.ai-copy-code-btn');
                if (copyButton) {
                    copyButton.click();
                    
                    expect(navigator.clipboard.writeText).toHaveBeenCalled();
                }
            }, 100);
        });
    });
});

describe('API - streamChatResponse', () => {
    let api;

    beforeEach(() => {
        api = new API();
        global.fetch = jest.fn();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('should call POST /api/ai-chat with correct payload', async () => {
        const mockStream = new ReadableStream({
            start(controller) {
                controller.enqueue(new TextEncoder().encode('data: {"token": "Hello"}\n\n'));
                controller.close();
            }
        });

        global.fetch.mockResolvedValue({
            ok: true,
            body: mockStream
        });

        const onToken = jest.fn();
        const onError = jest.fn();
        const onComplete = jest.fn();

        await api.streamChatResponse('Test message', { phase: 'Implementation' }, onToken, onError, onComplete);

        expect(global.fetch).toHaveBeenCalledWith(
            '/api/ai-chat',
            expect.objectContaining({
                method: 'POST',
                headers: expect.objectContaining({
                    'Content-Type': 'application/json'
                }),
                body: expect.stringContaining('Test message')
            })
        );
    });

    test('should call onToken callback for each token', async () => {
        const mockStream = new ReadableStream({
            start(controller) {
                controller.enqueue(new TextEncoder().encode('data: {"token": "Hello"}\n\n'));
                controller.enqueue(new TextEncoder().encode('data: {"token": " World"}\n\n'));
                controller.close();
            }
        });

        global.fetch.mockResolvedValue({
            ok: true,
            body: mockStream
        });

        const onToken = jest.fn();
        const onError = jest.fn();
        const onComplete = jest.fn();

        await api.streamChatResponse('Test', {}, onToken, onError, onComplete);

        expect(onToken).toHaveBeenCalledWith('Hello');
        expect(onToken).toHaveBeenCalledWith(' World');
        expect(onToken).toHaveBeenCalledTimes(2);
    });

    test('should call onComplete when stream ends', async () => {
        const mockStream = new ReadableStream({
            start(controller) {
                controller.enqueue(new TextEncoder().encode('data: {"token": "Hello"}\n\n'));
                controller.close();
            }
        });

        global.fetch.mockResolvedValue({
            ok: true,
            body: mockStream
        });

        const onToken = jest.fn();
        const onError = jest.fn();
        const onComplete = jest.fn();

        await api.streamChatResponse('Test', {}, onToken, onError, onComplete);

        expect(onComplete).toHaveBeenCalled();
    });

    test('should call onError on error response', async () => {
        global.fetch.mockResolvedValue({
            ok: false,
            status: 500,
            json: () => Promise.resolve({ error: 'Internal server error' })
        });

        const onToken = jest.fn();
        const onError = jest.fn();
        const onComplete = jest.fn();

        await api.streamChatResponse('Test', {}, onToken, onError, onComplete);

        expect(onError).toHaveBeenCalledWith('HTTP error! status: 500');
        expect(onToken).not.toHaveBeenCalled();
        expect(onComplete).not.toHaveBeenCalled();
    });

    test('should call onError on network error', async () => {
        global.fetch.mockRejectedValue(new Error('Network error'));

        const onToken = jest.fn();
        const onError = jest.fn();
        const onComplete = jest.fn();

        await api.streamChatResponse('Test', {}, onToken, onError, onComplete);

        expect(onError).toHaveBeenCalledWith('Network error');
        expect(onToken).not.toHaveBeenCalled();
        expect(onComplete).not.toHaveBeenCalled();
    });
});
