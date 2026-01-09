/**
 * BMAD Dash - Main Application Entry Point
 * Initializes the application, fetches dashboard data, and orchestrates component rendering
 */

import { render as renderBreadcrumb } from './components/breadcrumb.js';

const DEFAULT_PROJECT_ROOT = 'F:/BMAD Dash';

/**
 * Initialize the application on page load
 */
async function init() {
    console.time('Dashboard Load Time');

    // Load project root from localStorage or use default
    const projectRoot = localStorage.getItem('bmad_project_root') || DEFAULT_PROJECT_ROOT;
    document.getElementById('project-root-input').value = projectRoot;

    try {
        showLoading();
        const data = await fetchDashboardData(projectRoot);
        hideLoading();

        // Render breadcrumb navigation
        renderBreadcrumb(data.breadcrumb);

        // Future: render Quick Glance (Story 1.5)
        // Future: render Kanban (Story 3.2)

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
 * Fetch dashboard data from API
 * @param {string} projectRoot - Path to the BMAD project root
 * @returns {Promise<Object>} Dashboard data
 */
async function fetchDashboardData(projectRoot) {
    const url = `/api/dashboard?project_root=${encodeURIComponent(projectRoot)}`;
    console.log('Fetching dashboard data from:', url);

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
    console.log('Dashboard data loaded:', data);
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
        const data = await fetchDashboardData(projectRoot);
        hideLoading();

        // Render components
        renderBreadcrumb(data.breadcrumb);

        console.log('Project loaded successfully:', projectRoot);
    } catch (error) {
        hideLoading();
        showError(error.message);
        console.error('Failed to load project:', error);
    } finally {
        loadingSpan.classList.add('hidden');
    }
}

/**
 * Set up event handlers
 */
function setupEventHandlers() {
    const loadButton = document.getElementById('load-project-btn');
    const projectInput = document.getElementById('project-root-input');

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
}

// Initialize app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('BMAD Dash initializing...');
    setupEventHandlers();
    init();
});

export { fetchDashboardData, init, loadProject };
