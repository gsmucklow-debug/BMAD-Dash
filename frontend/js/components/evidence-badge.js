/**
 * Evidence Badge Component
 * Renders Git and Test status badges and handles data fetching
 */

import { openGitEvidence, openTestEvidence } from './evidence-modal.js';

/**
 * Generate HTTP for evidence badges skeleton (loading state)
 * @returns {string} HTML string
 */
export function getBadgesSkeletonHTML() {
    return `
        <div id="evidence-badges-container" class="mt-3 flex gap-2 animate-pulse">
            <div class="h-6 w-20 bg-bmad-surface rounded"></div>
            <div class="h-6 w-20 bg-bmad-surface rounded"></div>
        </div>
    `;
}

/**
 * Render badges from pre-fetched evidence data (no network calls)
 * @param {string} containerId - ID of the container element
 * @param {Object} evidenceData - Pre-fetched evidence data from dashboard
 * @param {string} storyId - Story ID
 * @param {string} projectRoot - Project root path
 */
export function renderBadgesFromData(containerId, evidenceData, storyId, projectRoot) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Pass the full rich evidence data directly
    // Check for commits array, commit_count, or status field to determine if git evidence exists
    const gitData = (evidenceData.commits || evidenceData.commit_count !== undefined || evidenceData.status) ? evidenceData : null;
    const testData = (evidenceData.tests_total !== undefined || evidenceData.tests_passed !== undefined) ? evidenceData : null;

    renderBadges(container, gitData, testData, null, storyId, projectRoot);
}

/**
 * Update the badges container with actual data (legacy - kept for backward compatibility)
 * @param {string} containerId - ID of the container element
 * @param {string} storyId - Story ID
 * @param {string} projectRoot - Project root path
 */
export async function updateBadges(containerId, storyId, projectRoot) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
        // Fetch evidences in parallel
        const [gitRes, testRes, reviewRes] = await Promise.all([
            fetch(`/api/git-evidence/${storyId}?project_root=${encodeURIComponent(projectRoot)}`),
            fetch(`/api/test-evidence/${storyId}?project_root=${encodeURIComponent(projectRoot)}`),
            fetch(`/api/review-evidence/${storyId}?project_root=${encodeURIComponent(projectRoot)}`)
        ]);

        const gitData = gitRes.ok ? await gitRes.json() : null;
        const testData = testRes.ok ? await testRes.json() : null;
        const reviewData = reviewRes.ok ? await reviewRes.json() : null;

        renderBadges(container, gitData, testData, reviewData, storyId, projectRoot);

    } catch (error) {
        console.error('Failed to load evidence badges:', error);
        container.innerHTML = `<div class="text-xs text-red-400">Failed to load evidence</div>`;
    }
}

/**
 * Render the actual badges into the container
 */
function renderBadges(container, gitData, testData, reviewData, storyId, projectRoot) {
    container.innerHTML = '';
    container.className = 'mt-3 flex gap-2 flex-wrap';

    // GIT BADGE
    const gitBadge = document.createElement('button');
    gitBadge.className = `flex items-center px-2 py-1 rounded text-xs font-medium transition-colors border ${getGitBadgeColor(gitData)}`;
    gitBadge.innerHTML = getGitBadgeContent(gitData);
    gitBadge.onclick = (e) => {
        e.stopPropagation(); // Don't trigger story card click
        openGitEvidence(storyId, projectRoot, gitData);
    };
    container.appendChild(gitBadge);

    // TEST BADGE
    const testBadge = document.createElement('button');
    testBadge.className = `flex items-center px-2 py-1 rounded text-xs font-medium transition-colors border ${getTestBadgeColor(testData)}`;
    testBadge.innerHTML = getTestBadgeContent(testData);
    testBadge.onclick = (e) => {
        e.stopPropagation(); // Don't trigger story card click
        openTestEvidence(storyId, projectRoot, testData);
    };
    container.appendChild(testBadge);

    // REVIEWED BADGE (if review status is 'reviewed')
    if (reviewData?.status === 'reviewed') {
        const reviewBadge = document.createElement('div');
        reviewBadge.className = 'flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-900/20 text-blue-400 border border-blue-900/50';
        reviewBadge.innerHTML = `
            <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            REVIEWED
        `;
        container.appendChild(reviewBadge);
    }

    // HEALTHY BADGE (if both green and recent)
    if (isHealthy(gitData, testData)) {
        const healthyBadge = document.createElement('div');
        healthyBadge.className = 'flex items-center px-2 py-1 rounded text-xs font-medium bg-green-900/20 text-green-400 border border-green-900/50';
        healthyBadge.innerHTML = `
            <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            HEALTHY
        `;
        container.appendChild(healthyBadge);
    }
}

// ... helper functions ...

function getGitBadgeColor(data) {
    if (!data) return 'bg-bmad-surface border-bmad-gray text-bmad-muted hover:bg-bmad-gray';

    switch (data.status) {
        case 'green': return 'bg-green-900/20 border-green-900/50 text-green-400 hover:bg-green-900/30';
        case 'yellow': return 'bg-yellow-900/20 border-yellow-900/50 text-yellow-500 hover:bg-yellow-900/30';
        case 'red': return 'bg-red-900/20 border-red-900/50 text-red-400 hover:bg-red-900/30';
        default: return 'bg-bmad-surface border-bmad-gray text-bmad-muted hover:bg-bmad-gray';
    }
}

function getGitBadgeContent(data) {
    // Check if we have any git evidence at all
    const hasGitData = data && (
        data.commit_count !== undefined ||
        data.commits !== undefined ||
        data.count !== undefined
    );

    if (!hasGitData) return `
        <svg class="w-3 h-3 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
        No Commits
    `;

    // Handle multiple evidence formats:
    // 1. commit_count field (new format)
    // 2. commits as integer (old cached format)
    // 3. commits as array (live format)
    // 4. count field (legacy)
    let count;
    if (data.commit_count !== undefined) {
        count = data.commit_count;
    } else if (typeof data.commits === 'number') {
        count = data.commits;
    } else if (Array.isArray(data.commits)) {
        count = data.commits.length;
    } else if (data.count !== undefined) {
        count = data.count;
    } else {
        count = 0;
    }

    if (count === 0) return `
        <svg class="w-3 h-3 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
        No Commits
    `;

    return `
        <svg class="w-3 h-3 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
        ${count} Commit${count !== 1 ? 's' : ''}
    `;
}

function getTestBadgeColor(data) {
    if (!data) return 'bg-bmad-surface border-bmad-gray text-bmad-muted hover:bg-bmad-gray';

    switch (data.status) {
        case 'green': return 'bg-green-900/20 border-green-900/50 text-green-400 hover:bg-green-900/30';
        case 'yellow': return 'bg-yellow-900/20 border-yellow-900/50 text-yellow-500 hover:bg-yellow-900/30';
        case 'red': return 'bg-red-900/20 border-red-900/50 text-red-400 hover:bg-red-900/30';
        default: return 'bg-bmad-surface border-bmad-gray text-bmad-muted hover:bg-bmad-gray';
    }
}

function getTestBadgeContent(data) {
    // Check for both field name variations
    const totalTests = data.tests_total !== undefined ? data.tests_total : data.total_tests;
    const passedTests = data.tests_passed !== undefined ? data.tests_passed : data.pass_count;

    if (!data || (totalTests === undefined && data.total_tests === undefined && data.tests_total === undefined)) return `
        <svg class="w-3 h-3 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        No Tests
    `;

    return `
        <svg class="w-3 h-3 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Tests: ${passedTests || 0}/${totalTests || 0}
    `;
}

function isHealthy(git, test) {
    return git?.status === 'green' && test?.status === 'green';
}
