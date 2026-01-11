/**
 * BMAD Dash - Main Application Entry Point
 * Initializes the application, fetches dashboard data, and orchestrates component rendering
 */

import { Router } from './router.js';
import { render as renderBreadcrumb } from './components/breadcrumb.js';
import { render as renderQuickGlance } from './components/quick-glance.js';
import { render as renderViewSwitcher, updateActive } from './components/view-switcher.js';
import { init as initEvidenceModal } from './components/evidence-modal.js';
import { AIChat } from './components/ai-chat.js';
import { render as renderDashboard } from './views/dashboard.js';
import { render as renderTimeline } from './views/timeline.js';
import { render as renderList } from './views/list.js';

const DEFAULT_PROJECT_ROOT = '';

// Global state
let router = null;
let dashboardData = null;
let aiChatInstance = null;

/**
 * Initialize the application on page load
 */
async function init() {
    console.time('Dashboard Load Time');

    // Initialize modal component (Story 2.4)
    initEvidenceModal();

    // Initialize router (Story 3.1)
    router = new Router();
    setupRoutes();

    // Load project root from localStorage or use default
    const projectRoot = localStorage.getItem('bmad_project_root') || DEFAULT_PROJECT_ROOT;
    document.getElementById('project-root-input').value = projectRoot;

    try {
        showLoading();
        dashboardData = await fetchDashboardData(projectRoot);
        hideLoading();

        // Render view switcher (Story 3.1)
        renderViewSwitcher(router, router.getCurrentRoute());

        // Initialize AI Chat once (persists across views)
        if (!aiChatInstance) {
            aiChatInstance = new AIChat('ai-chat-container');
        }

        // Update AI chat with project context (Story 5.2: Enhanced context)
        if (aiChatInstance && dashboardData.project) {
            const currentStory = dashboardData.quick_glance?.current || {};
            const currentEpic = dashboardData.breadcrumb?.epic || {};

            // Get detailed task info from action_card
            const actionCard = dashboardData.action_card || {};
            const storyLayer = actionCard.story_layer || {};
            const taskLayer = actionCard.task_layer || {};

            // Find full story data in kanban for task list
            const allStories = [
                ...(dashboardData.kanban?.todo || []),
                ...(dashboardData.kanban?.in_progress || []),
                ...(dashboardData.kanban?.review || []),
                ...(dashboardData.kanban?.done || [])
            ];
            const fullStoryData = allStories.find(s => s.story_id === currentStory.story_id) || {};
            const tasks = fullStoryData.tasks || [];

            aiChatInstance.setProjectContext({
                // Basic fields (legacy compatibility)
                phase: dashboardData.project.phase || 'Unknown',
                epic: currentEpic.id || 'Unknown',
                story: currentStory.story_id || 'Unknown',
                task: taskLayer.title || dashboardData.breadcrumb?.task?.title || 'Unknown',

                // Enhanced fields for Story 5.2
                epicId: currentEpic.id || 'Unknown',
                epicTitle: currentEpic.title || '',
                storyId: currentStory.story_id || 'Unknown',
                storyTitle: currentStory.title || '',
                storyStatus: currentStory.status || 'Unknown',

                // Task-level details (AC4: AI knows task context)
                taskProgress: currentStory.progress || taskLayer.progress || '0/0 tasks',
                currentTask: taskLayer.title || 'No active task',
                currentTaskStatus: taskLayer.status || 'unknown',
                tasks: tasks.map(t => ({
                    id: t.task_id || t.id,
                    title: t.title,
                    status: t.status
                })),

                // Acceptance criteria summary
                acceptanceCriteria: storyLayer.acceptance_criteria_summary || []
            });

            // Update suggested prompts with new context
            aiChatInstance.updateSuggestedPrompts();
        }

        // Router will handle view rendering based on hash
        router.handleRoute();

        console.timeEnd('Dashboard Load Time');

        // Warn if page load exceeds 500ms
        const loadTime = performance.now();
        if (loadTime > 500) {
            console.warn(`⚠ Page load time exceeded 500ms: ${loadTime.toFixed(2)}ms`);
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
        console.error('Dashboard load failed:', error);
    }
}

/**
 * Setup router routes (Story 3.1)
 */
function setupRoutes() {
    router.register('/dashboard', () => {
        if (dashboardData) {
            renderDashboard(dashboardData);
            updateActive('/dashboard');
        }
    });

    router.register('/timeline', () => {
        if (dashboardData) {
            renderTimeline(dashboardData);
            updateActive('/timeline');
        }
    });

    router.register('/list', () => {
        if (dashboardData) {
            renderList(dashboardData);
            updateActive('/list');
        }
    });

    router.setDefault('/dashboard');
}

/**
 * Fetch dashboard data from API
 * @param {string} projectRoot - Path to the BMAD project root
 * @returns {Promise<Object>} Dashboard data
 */
async function fetchDashboardData(projectRoot) {
    const url = `/api/dashboard?project_root=${encodeURIComponent(projectRoot)}`;

    const response = await fetch(url);

    if (!response.ok) {
        let errorMessage = 'Failed to load dashboard';
        try {
            const error = await response.json();
            errorMessage = error.message || errorMessage;
        } catch (e) {
            // Response not JSON, use default message
        }
        throw new Error(errorMessage);
    }

    const data = await response.json();
    return data;
}

/**
 * Show loading indicator
 */
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = `Error: ${message}`;
    errorDiv.classList.remove('hidden');
}

/**
 * Load a new project root
 * @param {string} projectRoot - Path to the new project root
 */
async function loadProject(projectRoot) {
    // Save to localStorage
    localStorage.setItem('bmad_project_root', projectRoot);

    // Show loading state
    const loadingSpan = document.getElementById('project-loading');
    loadingSpan.classList.remove('hidden');

    try {
        showLoading();
        dashboardData = await fetchDashboardData(projectRoot);
        hideLoading();

        // Update AI chat with new project context (Story 5.2)
        if (aiChatInstance && dashboardData.project) {
            const currentStory = dashboardData.quick_glance?.current || {};
            const currentEpic = dashboardData.breadcrumb?.epic || {};
            const actionCard = dashboardData.action_card || {};
            const storyLayer = actionCard.story_layer || {};
            const taskLayer = actionCard.task_layer || {};
            const allStories = [
                ...(dashboardData.kanban?.todo || []),
                ...(dashboardData.kanban?.in_progress || []),
                ...(dashboardData.kanban?.review || []),
                ...(dashboardData.kanban?.done || [])
            ];
            const fullStoryData = allStories.find(s => s.story_id === currentStory.story_id) || {};
            const tasks = fullStoryData.tasks || [];

            aiChatInstance.setProjectContext({
                phase: dashboardData.project.phase || 'Unknown',
                epic: currentEpic.id || 'Unknown',
                story: currentStory.story_id || 'Unknown',
                task: taskLayer.title || dashboardData.breadcrumb?.task?.title || 'Unknown',
                epicId: currentEpic.id || 'Unknown',
                epicTitle: currentEpic.title || '',
                storyId: currentStory.story_id || 'Unknown',
                storyTitle: currentStory.title || '',
                storyStatus: currentStory.status || 'Unknown',
                taskProgress: currentStory.progress || taskLayer.progress || '0/0 tasks',
                currentTask: taskLayer.title || 'No active task',
                currentTaskStatus: taskLayer.status || 'unknown',
                tasks: tasks.map(t => ({ id: t.task_id || t.id, title: t.title, status: t.status })),
                acceptanceCriteria: storyLayer.acceptance_criteria_summary || []
            });
            aiChatInstance.updateSuggestedPrompts();
        }

        // Re-render current view with new data
        router.handleRoute();
    } catch (error) {
        hideLoading();
        showError(error.message);
        console.error('Failed to load project:', error);
    } finally {
        loadingSpan.classList.add('hidden');
    }
}

/**
 * Handle manual refresh (Story 3.3)
 * Clears cache and reloads dashboard data while preserving current view
 */
async function handleRefresh() {
    const refreshStartTime = performance.now();

    const refreshButton = document.getElementById('refresh-btn');
    const projectRoot = localStorage.getItem('bmad_project_root') || DEFAULT_PROJECT_ROOT;

    if (!projectRoot) {
        console.warn('No project root set, cannot refresh');
        return;
    }

    // Track refresh state to reset on next click (NFR17: no time-limited interactions)
    const wasRefreshed = refreshButton.dataset.refreshed === 'true';
    if (wasRefreshed) {
        refreshButton.textContent = '↻ Refresh';
        refreshButton.classList.remove('bg-green-700', 'bg-red-600');
        refreshButton.classList.add('bg-green-600');
        refreshButton.dataset.refreshed = 'false';
    }

    // Update button state to loading
    refreshButton.textContent = '⟳ Refreshing...';
    refreshButton.disabled = true;

    try {
        // Call refresh endpoint to clear cache
        const refreshUrl = `/api/refresh?project_root=${encodeURIComponent(projectRoot)}`;
        const refreshResponse = await fetch(refreshUrl, {
            method: 'POST'
        });

        if (!refreshResponse.ok) {
            const error = await refreshResponse.json();
            throw new Error(error.message || 'Refresh failed');
        }

        // Re-fetch dashboard data
        dashboardData = await fetchDashboardData(projectRoot);

        // Update AI chat with refreshed context (Story 5.2)
        if (aiChatInstance && dashboardData.project) {
            const currentStory = dashboardData.quick_glance?.current || {};
            const currentEpic = dashboardData.breadcrumb?.epic || {};
            const actionCard = dashboardData.action_card || {};
            const storyLayer = actionCard.story_layer || {};
            const taskLayer = actionCard.task_layer || {};
            const allStories = [
                ...(dashboardData.kanban?.todo || []),
                ...(dashboardData.kanban?.in_progress || []),
                ...(dashboardData.kanban?.review || []),
                ...(dashboardData.kanban?.done || [])
            ];
            const fullStoryData = allStories.find(s => s.story_id === currentStory.story_id) || {};
            const tasks = fullStoryData.tasks || [];

            aiChatInstance.setProjectContext({
                phase: dashboardData.project.phase || 'Unknown',
                epic: currentEpic.id || 'Unknown',
                story: currentStory.story_id || 'Unknown',
                task: taskLayer.title || dashboardData.breadcrumb?.task?.title || 'Unknown',
                epicId: currentEpic.id || 'Unknown',
                epicTitle: currentEpic.title || '',
                storyId: currentStory.story_id || 'Unknown',
                storyTitle: currentStory.title || '',
                storyStatus: currentStory.status || 'Unknown',
                taskProgress: currentStory.progress || taskLayer.progress || '0/0 tasks',
                currentTask: taskLayer.title || 'No active task',
                currentTaskStatus: taskLayer.status || 'unknown',
                tasks: tasks.map(t => ({ id: t.task_id || t.id, title: t.title, status: t.status })),
                acceptanceCriteria: storyLayer.acceptance_criteria_summary || []
            });
            aiChatInstance.updateSuggestedPrompts();
        }

        // Re-render current view (preserve view mode)
        router.handleRoute();

        // Check performance (NFR7: <300ms)
        const refreshTime = performance.now() - refreshStartTime;

        if (refreshTime > 300) {
            console.warn(`⚠ Refresh exceeded 300ms target: ${refreshTime.toFixed(2)}ms`);
        }

        // Persistent success feedback (NFR17: no auto-dismiss)
        refreshButton.textContent = '✓ Refreshed';
        refreshButton.classList.add('bg-green-700');
        refreshButton.dataset.refreshed = 'true';

    } catch (error) {
        console.error('Refresh error:', error);
        showError(error.message);

        // Persistent error feedback (NFR17: no auto-dismiss)
        refreshButton.textContent = '✗ Refresh Failed';
        refreshButton.classList.add('bg-red-600');
        refreshButton.classList.remove('bg-green-600');
        refreshButton.dataset.refreshed = 'true';
    } finally {
        refreshButton.disabled = false;
    }
}

/**
 * Set up event handlers
 */
function setupEventHandlers() {
    const loadButton = document.getElementById('load-project-btn');
    const projectInput = document.getElementById('project-root-input');
    const refreshButton = document.getElementById('refresh-btn');

    // Load project on button click
    loadButton.addEventListener('click', () => {
        const projectRoot = projectInput.value.trim();
        if (projectRoot) {
            loadProject(projectRoot);
        }
    });

    // Load project on Enter key
    projectInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const projectRoot = projectInput.value.trim();
            if (projectRoot) {
                loadProject(projectRoot);
            }
        }
    });

    // Refresh on button click (Story 3.3)
    refreshButton.addEventListener('click', () => {
        handleRefresh();
    });
}

// Initialize app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    setupEventHandlers();
    init();
});

export { fetchDashboardData, init, loadProject };
