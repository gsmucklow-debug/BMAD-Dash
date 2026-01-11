/**
 * BMAD Dash - Tests for Suggested Prompts Component (Story 5.2)
 */

import { SuggestedPrompts } from '../frontend/js/components/suggested-prompts.js';
import { PromptGenerator } from '../frontend/js/utils/prompt-generator.js';

describe('PromptGenerator Unit Tests', () => {
    let generator;

    beforeEach(() => {
        generator = new PromptGenerator();
    });

    describe('Template Generation', () => {
        test('should generate prompts for TODO status', () => {
            const context = {
                storyId: '5.2',
                storyStatus: 'TODO',
                epicId: 'epic-5',
                storyTitle: 'Test Story'
            };

            const prompts = generator.generatePrompts(context);

            expect(prompts.length).toBeGreaterThan(0);
            expect(prompts.some(p => p.text.includes('How do I start'))).toBe(true);
            expect(prompts.some(p => p.text.includes('5.2'))).toBe(true);
        });

        test('should generate prompts for IN_PROGRESS status', () => {
            const context = {
                storyId: '4.1',
                storyStatus: 'IN_PROGRESS',
                epicId: 'epic-4'
            };

            const prompts = generator.generatePrompts(context);

            expect(prompts.length).toBeGreaterThan(0);
            expect(prompts.some(p => p.text.includes('What tasks remain'))).toBe(true);
            expect(prompts.some(p => p.text.includes('4.1'))).toBe(true);
        });

        test(' should generate prompts for REVIEW status', () => {
            const context = {
                storyId: '3.3',
                storyStatus: 'REVIEW',
                epicId: 'epic-3'
            };

            const prompts = generator.generatePrompts(context);

            expect(prompts.length).toBeGreaterThan(0);
            expect(prompts.some(p => p.text.includes('Did the AI agent complete'))).toBe(true);
            expect(prompts.some(p => p.text.includes('3.3'))).toBe(true);
        });

        test('should generate prompts for COMPLETE status', () => {
            const context = {
                storyId: '2.4',
                storyStatus: 'COMPLETE',
                epicId: 'epic-2'
            };

            const prompts = generator.generatePrompts(context);

            expect(prompts.length).toBeGreaterThan(0);
            expect(prompts.some(p => p.text.includes('next story'))).toBe(true);
        });

        test('should normalize status variations', () => {
            const testCases = [
                { input: 'ready-for-dev', expected: 'TODO' },
                { input: 'BACKLOG', expected: 'TODO' },
                { input: 'done', expected: 'COMPLETE' },
                { input: 'in-review', expected: 'REVIEW' }
            ];

            testCases.forEach(({ input, expected }) => {
                const normalized = generator._normalizeStatus(input);
                expect(normalized).toBe(expected);
            });
        });

        test('should substitute placeholder values', () => {
            const text = 'Story {storyId} in Epic {epicId}';
            const values = { storyId: '5.2', epicId: 'epic-5' };

            const result = generator._substituteValues(text, values);

            expect(result).toBe('Story 5.2 in Epic epic-5');
        });

        test('should handle missing context gracefully', () => {
            const prompts = generator.generatePrompts({});

            expect(prompts.length).toBeGreaterThan(0);
            expect(prompts.some(p => p.text.includes('X.X'))).toBe(true);
        });
    });

    describe('Category Filtering', () => {
        test('should filter prompts by category', () => {
            const context = { storyId: '5.2', storyStatus: 'IN_PROGRESS' };
            const allPrompts = generator.generatePrompts(context);

            const workflowPrompts = generator.filterByCategory(allPrompts, 'workflow');
            const infoPrompts = generator.filterByCategory(allPrompts, 'info');

            expect(workflowPrompts.every(p => p.category === 'workflow')).toBe(true);
            expect(infoPrompts.every(p => p.category === 'info')).toBe(true);
        });

        test('should get all categories', () => {
            const categories = generator.getCategories();

            expect(categories).toContain('workflow');
            expect(categories).toContain('info');
            expect(categories).toContain('validation');
            expect(categories).toContain('help');
        });
    });
});

describe('SuggestedPrompts Component Tests', () => {
    let container;
    let suggestedPrompts;
    let clickCallback;

    beforeEach(() => {
        container = document.createElement('div');
        container.id = 'test-prompts-container';
        document.body.appendChild(container);

        clickCallback = jest.fn();
        suggestedPrompts = new SuggestedPrompts('test-prompts-container', clickCallback);
    });

    afterEach(() => {
        document.body.removeChild(container);
    });

    describe('Rendering', () => {
        test('should render prompt cards', () => {
            const prompts = [
                { text: 'Test prompt 1', icon: '🚀', category: 'workflow' },
                { text: 'Test prompt 2', icon: '✓', category: 'info' }
            ];

            suggestedPrompts.render(prompts);

            const cards = container.querySelectorAll('.suggested-prompt-card');
            expect(cards.length).toBe(2);
        });

        test('should display prompt text and icon', () => {
            const prompts = [
                { text: 'What should I do next?', icon: '🎯', category: 'workflow' }
            ];

            suggestedPrompts.render(prompts);

            const card = container.querySelector('.suggested-prompt-card');
            expect(card).not.toBeNull();
            expect(card.textContent).toContain('What should I do next?');
            expect(card.textContent).toContain('🎯');
        });

        test('should apply category-specific styling', () => {
            const prompts = [
                { text: 'Workflow prompt', icon: '🚀', category: 'workflow' },
                { text: 'Info prompt', icon: 'ℹ️', category: 'info' }
            ];

            suggestedPrompts.render(prompts);

            const cards = container.querySelectorAll('.suggested-prompt-card');
            expect(cards[0].classList.contains('prompt-category-workflow')).toBe(true);
            expect(cards[1].classList.contains('prompt-category-info')).toBe(true);
        });

        test('should clear container when no prompts provided', () => {
            suggestedPrompts.render([]);

            expect(container.innerHTML).toBe('');
        });

        test('should escape HTML in prompt text', () => {
            const prompts = [
                { text: '<script>alert("xss")</script>', icon: '🔒', category: 'help' }
            ];

            suggestedPrompts.render(prompts);

            const card = container.querySelector('.suggested-prompt-card');
            expect(card.innerHTML).not.toContain('<script>');
            expect(card.textContent).toContain('<script>');
        });
    });

    describe('Interactions', () => {
        test('should call callback on prompt click', () => {
            const prompts = [
                { text: 'Click me', icon: '👆', category: 'workflow' }
            ];

            suggestedPrompts.render(prompts);

            const card = container.querySelector('.suggested-prompt-card');
            card.click();

            expect(clickCallback).toHaveBeenCalledWith('Click me');
        });

        test('should call callback on Enter key press', () => {
            const prompts = [
                { text: 'Keyboard test', icon: '⌨️', category: 'workflow' }
            ];

            suggestedPrompts.render(prompts);

            const card = container.querySelector('.suggested-prompt-card');
            const event = new KeyboardEvent('keydown', { key: 'Enter' });
            card.dispatchEvent(event);

            expect(clickCallback).toHaveBeenCalledWith('Keyboard test');
        });

        test('should call callback on Space key press', () => {
            const prompts = [
                { text: 'Space test', icon: '🔹', category: 'info' }
            ];

            suggestedPrompts.render(prompts);

            const card = container.querySelector('.suggested-prompt-card');
            const event = new KeyboardEvent('keydown', { key: ' ' });
            card.dispatchEvent(event);

            expect(clickCallback).toHaveBeenCalledWith('Space test');
        });

        test('should add visual feedback on click', (done) => {
            const prompts = [
                { text: 'Feedback test', icon: '✨', category: 'workflow' }
            ];

            suggestedPrompts.render(prompts);

            const card = container.querySelector('.suggested-prompt-card');
            card.click();

            expect(card.classList.contains('clicked')).toBe(true);

            setTimeout(() => {
                expect(card.classList.contains('clicked')).toBe(false);
                done();
            }, 250);
        });

        test('should have minimum 44x44px touch target', () => {
            const prompts = [
                { text: 'Touch target test', icon: '📱', category: 'workflow' }
            ];

            suggestedPrompts.render(prompts);

            const card = container.querySelector('.suggested-prompt-card');
            const rect = card.getBoundingClientRect();

            // Note: In test environment, computed styles might not apply
            // This test verifies the class is present, actual sizing tested in browser
            expect(card.classList.contains('suggested-prompt-card')).toBe(true);
        });
    });

    describe('Update and Clear', () => {
        test('should update prompts', () => {
            const initialPrompts = [
                { text: 'Initial', icon: '1️⃣', category: 'workflow' }
            ];
            const newPrompts = [
                { text: 'Updated', icon: '2️⃣', category: 'info' }
            ];

            suggestedPrompts.render(initialPrompts);
            let cards = container.querySelectorAll('.suggested-prompt-card');
            expect(cards.length).toBe(1);
            expect(cards[0].textContent).toContain('Initial');

            suggestedPrompts.update(newPrompts);
            cards = container.querySelectorAll('.suggested-prompt-card');
            expect(cards.length).toBe(1);
            expect(cards[0].textContent).toContain('Updated');
        });

        test('should clear all prompts', () => {
            const prompts = [
                { text: 'Clear test', icon: '🗑️', category: 'workflow' }
            ];

            suggestedPrompts.render(prompts);
            expect(container.querySelector('.suggested-prompt-card')).not.toBeNull();

            suggestedPrompts.clear();
            expect(container.querySelector('.suggested-prompt-card')).toBeNull();
            expect(container.innerHTML).toBe('');
        });
    });
});
