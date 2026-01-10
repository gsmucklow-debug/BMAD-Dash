/**
 * Evidence Modal Component
 * Displays detailed Git and Test evidence in an overlay modal
 */

let modalContainer = null;
let modalContent = null;
let currentAbortController = null;

/**
 * Initialize the modal component
 * Creates the DOM structure if it doesn't exist
 */
export function init() {
    if (document.getElementById('evidence-modal')) {
        modalContainer = document.getElementById('evidence-modal');
        modalContent = document.getElementById('evidence-modal-content');
        return;
    }

    // Create modal HTML structure
    const modalHTML = `
        <div id="evidence-modal" class="fixed inset-0 z-50 hidden" aria-labelledby="modal-title" role="dialog" aria-modal="true">
            <!-- Backdrop -->
            <div class="fixed inset-0 bg-black/80 transition-opacity backdrop-blur-sm" aria-hidden="true" id="evidence-modal-backdrop"></div>

            <!-- Modal Panel -->
            <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
                <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                    <div class="relative transform overflow-hidden rounded-lg bg-bmad-bg border border-bmad-gray text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-3xl">
                        
                        <!-- Header -->
                        <div class="bg-bmad-surface px-4 py-3 sm:px-6 flex justify-between items-center border-b border-bmad-gray">
                            <h3 class="text-lg font-semibold leading-6 text-white" id="modal-title">Evidence Details</h3>
                            <button type="button" class="rounded-md text-bmad-muted hover:text-white focus:outline-none" id="evidence-modal-close">
                                <span class="sr-only">Close</span>
                                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        <!-- Content -->
                        <div class="px-4 py-5 sm:p-6 min-h-[200px]" id="evidence-modal-content">
                            <!-- Dynamic content goes here -->
                        </div>

                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    modalContainer = document.getElementById('evidence-modal');
    modalContent = document.getElementById('evidence-modal-content');
    const closeBtn = document.getElementById('evidence-modal-close');
    const backdrop = document.getElementById('evidence-modal-backdrop');

    // Event listeners
    closeBtn.addEventListener('click', close);
    backdrop.addEventListener('click', close);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modalContainer.classList.contains('hidden')) {
            close();
        }
    });
}

/**
 * Open the modal and load Git evidence
 * @param {string} storyId - Story ID to fetch evidence for
 * @param {string} projectRoot - Project root path
 */
export async function openGitEvidence(storyId, projectRoot) {
    open();
    setTitle(`Git Evidence: ${storyId}`);
    showLoading();

    try {
        if (currentAbortController) currentAbortController.abort();
        currentAbortController = new AbortController();

        const response = await fetch(`/api/git-evidence/${storyId}?project_root=${encodeURIComponent(projectRoot)}`, {
            signal: currentAbortController.signal
        });

        if (!response.ok) throw new Error('Failed to fetch evidence');

        const data = await response.json();
        renderGitContent(data);
    } catch (error) {
        if (error.name !== 'AbortError') {
            renderError(error.message);
        }
    }
}

/**
 * Open the modal and load Test evidence
 * @param {string} storyId - Story ID to fetch evidence for
 * @param {string} projectRoot - Project root path
 */
export async function openTestEvidence(storyId, projectRoot) {
    open();
    setTitle(`Test Evidence: ${storyId}`);
    showLoading();

    try {
        if (currentAbortController) currentAbortController.abort();
        currentAbortController = new AbortController();

        const response = await fetch(`/api/test-evidence/${storyId}?project_root=${encodeURIComponent(projectRoot)}`, {
            signal: currentAbortController.signal
        });

        if (!response.ok) throw new Error('Failed to fetch evidence');

        const data = await response.json();
        renderTestContent(data);
    } catch (error) {
        if (error.name !== 'AbortError') {
            renderError(error.message);
        }
    }
}

/**
 * Render Git evidence content
 * @param {Object} data - Git evidence data
 */
function renderGitContent(data) {
    if (!data.commits || data.commits.length === 0) {
        modalContent.innerHTML = `
            <div class="text-center py-8">
                <div class="text-bmad-gray-light text-xl mb-2">No Commits Found</div>
                <p class="text-bmad-muted">No git commits were found referencing this story ID.</p>
            </div>
        `;
        return;
    }

    const commitsHTML = data.commits.map(commit => `
        <div class="border-l-2 border-bmad-purple pl-4 mb-4 last:mb-0 relative">
            <div class="absolute -left-[5px] top-1.5 w-2 h-2 rounded-full bg-bmad-purple"></div>
            <div class="flex justify-between items-start mb-1">
                <div class="font-mono text-xs text-bmad-purple-light">${commit.sha.substring(0, 7)}</div>
                <div class="text-xs text-bmad-muted" title="${commit.timestamp}">${formatRelativeTime(commit.timestamp)}</div>
            </div>
            <div class="text-bmad-text text-sm font-medium mb-1">${escapeHtml(commit.message)}</div>
            <div class="text-xs text-bmad-muted">
                ${commit.files_changed} file${commit.files_changed !== 1 ? 's' : ''} changed
            </div>
        </div>
    `).join('');

    modalContent.innerHTML = `
        <div class="space-y-4">
            <div class="flex items-center justify-between pb-4 border-b border-bmad-gray">
                <div>
                    <div class="text-sm text-bmad-muted">Status</div>
                    <div class="font-medium ${getStatusColorClass(data.status)} uppercase tracking-wider text-xs">
                        ${data.status}
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-sm text-bmad-muted">Commits Detected</div>
                    <div class="font-mono text-xl text-white">${data.commits.length}</div>
                </div>
            </div>
            <div class="max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
                ${commitsHTML}
            </div>
        </div>
    `;
}

/**
 * Render Test evidence content
 * @param {Object} data - Test evidence data
 */
function renderTestContent(data) {
    const hasFailures = data.fail_count > 0;
    const failureList = data.failing_test_names || [];

    modalContent.innerHTML = `
        <div class="space-y-6">
            <!-- Summary Stats -->
            <div class="grid grid-cols-3 gap-4 pb-6 border-b border-bmad-gray">
                <div class="text-center p-3 bg-bmad-gray/30 rounded-lg">
                    <div class="text-xs text-bmad-muted mb-1">Total Tests</div>
                    <div class="text-2xl font-bold text-white">${data.total_tests || 0}</div>
                </div>
                <div class="text-center p-3 bg-green-900/10 border border-green-900/30 rounded-lg">
                    <div class="text-xs text-green-400 mb-1">Passing</div>
                    <div class="text-2xl font-bold text-green-400">${data.pass_count || 0}</div>
                </div>
                <div class="text-center p-3 ${hasFailures ? 'bg-red-900/10 border border-red-900/30' : 'bg-bmad-gray/30'} rounded-lg">
                    <div class="text-xs ${hasFailures ? 'text-red-400' : 'text-bmad-muted'} mb-1">Failing</div>
                    <div class="text-2xl font-bold ${hasFailures ? 'text-red-400' : 'text-bmad-muted'}">${data.fail_count || 0}</div>
                </div>
            </div>

            <!-- Details -->
            <div>
                <div class="flex justify-between items-center mb-4">
                    <h4 class="text-sm font-medium text-bmad-muted uppercase tracking-wider">Test Files</h4>
                    <span class="text-xs text-bmad-muted">Last run: ${data.last_run_time ? formatRelativeTime(data.last_run_time) : 'Never'}</span>
                </div>
                
                ${data.test_files && data.test_files.length > 0 ? `
                    <div class="space-y-2 mb-6">
                        ${data.test_files.map(file => `
                            <div class="flex items-center text-sm text-bmad-text bg-bmad-gray/30 p-2 rounded">
                                <svg class="w-4 h-4 mr-2 text-bmad-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <span class="truncate ml-1" title="${file}">${file.split(/[\\/]/).pop()}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : '<div class="text-sm text-bmad-muted italic mb-6">No test files found</div>'}

                ${hasFailures ? `
                    <h4 class="text-sm font-medium text-red-400 uppercase tracking-wider mb-2">Failing Tests</h4>
                    <div class="bg-red-950/30 border border-red-900/50 rounded-lg p-3 max-h-[30vh] overflow-y-auto custom-scrollbar">
                        <ul class="space-y-2">
                            ${failureList.map(name => `
                                <li class="text-sm text-red-300 font-mono break-all flex items-start">
                                    <span class="mr-2 mt-1">×</span>
                                    ${escapeHtml(name)}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
            
            ${!hasFailures && (data.pass_count > 0) ? `
                <div class="flex items-center justify-center p-4 bg-green-900/10 border border-green-900/30 rounded-lg text-green-400">
                    <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span class="font-medium">All discovered tests passed</span>
                </div>
            ` : ''}
        </div>
    `;
}

function showLoading() {
    modalContent.innerHTML = `
        <div class="flex justify-center items-center h-40">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-bmad-purple"></div>
        </div>
    `;
}

function renderError(message) {
    modalContent.innerHTML = `
        <div class="flex items-center justify-center h-40 text-red-400">
            <svg class="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
}

function open() {
    modalContainer.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

export function close() {
    if (modalContainer) {
        modalContainer.classList.add('hidden');
        document.body.style.overflow = '';
        if (currentAbortController) {
            currentAbortController.abort();
        }
    }
}

function setTitle(title) {
    document.getElementById('modal-title').textContent = title;
}

function getStatusColorClass(status) {
    switch (status) {
        case 'green': return 'text-bmad-green';
        case 'red': return 'text-red-500';
        case 'yellow': return 'text-yellow-500';
        default: return 'text-bmad-muted';
    }
}

function formatRelativeTime(dateStr) {
    if (!dateStr) return '';
    try {
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.round(diffMs / 60000);
        const diffHours = Math.round(diffMs / 3600000);
        const diffDays = Math.round(diffMs / 86400000);

        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    } catch (e) {
        return dateStr;
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
