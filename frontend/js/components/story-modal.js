/**
 * Story Modal Component
 * Displays detailed story information including markdown content and tasks
 */

let modalContainer = null;
let modalContent = null;
let currentAbortController = null;

/**
 * Initialize the story modal
 */
export function init() {
    if (document.getElementById('story-modal')) {
        modalContainer = document.getElementById('story-modal');
        modalContent = document.getElementById('story-modal-body');
        return;
    }

    const modalHTML = `
        <div id="story-modal" class="fixed inset-0 z-[60] hidden" aria-labelledby="story-modal-title" role="dialog" aria-modal="true">
            <div class="fixed inset-0 bg-black/80 transition-opacity backdrop-blur-sm" id="story-modal-backdrop"></div>

            <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
                <div class="flex min-h-full items-center justify-center p-4">
                    <div class="relative transform overflow-hidden rounded-xl bg-bmad-surface/95 border border-bmad-gray/50 text-left shadow-2xl transition-all w-full max-w-4xl backdrop-blur-md">
                        
                        <!-- Header -->
                        <div class="bg-bmad-gray/50 px-6 py-4 flex justify-between items-center border-b border-bmad-gray">
                            <div class="flex items-center gap-3">
                                <span id="story-modal-id" class="text-xs font-mono px-2 py-0.5 rounded bg-bmad-accent/20 text-bmad-accent border border-bmad-accent/30"></span>
                                <h3 class="text-xl font-bold text-white truncate max-w-xl" id="story-modal-title">Story Details</h3>
                            </div>
                            <button type="button" class="p-1 rounded-md text-bmad-muted hover:text-white transition-colors" id="story-modal-close">
                                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        <!-- Content Area -->
                        <div class="flex flex-col md:flex-row h-[75vh]">
                            <!-- Sidebar: Information & Tasks -->
                            <div class="w-full md:w-80 border-b md:border-b-0 md:border-r border-bmad-gray p-6 overflow-y-auto custom-scrollbar bg-bmad-dark/30">
                                <div id="story-modal-meta" class="mb-6">
                                    <!-- Meta info status badge goes here -->
                                </div>

                                <h4 class="text-xs font-semibold text-bmad-muted uppercase tracking-widest mb-4">Implementation Tasks</h4>
                                <div id="story-modal-tasks" class="space-y-3">
                                    <!-- Tasks go here -->
                                </div>
                            </div>

                            <!-- Main: Markdown Content -->
                            <div class="flex-1 p-8 overflow-y-auto custom-scrollbar bg-bmad-surface/20">
                                <div id="story-modal-body" class="prose prose-invert prose-sm max-w-none prose-pre:bg-bmad-dark prose-pre:border prose-pre:border-bmad-gray">
                                    <!-- Markdown renders here -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    modalContainer = document.getElementById('story-modal');
    modalContent = document.getElementById('story-modal-body');

    document.getElementById('story-modal-close').addEventListener('click', close);
    document.getElementById('story-modal-backdrop').addEventListener('click', close);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modalContainer.classList.contains('hidden')) {
            close();
        }
    });
}

/**
 * Open the story detail modal
 * @param {string} storyId 
 * @param {string} projectRoot 
 */
export async function openStoryDetail(storyId, projectRoot) {
    if (!modalContainer) init();

    open();
    showLoading();

    try {
        if (currentAbortController) currentAbortController.abort();
        currentAbortController = new AbortController();

        const response = await fetch(`/api/dashboard/story/${storyId}?project_root=${encodeURIComponent(projectRoot)}`, {
            signal: currentAbortController.signal
        });

        if (!response.ok) throw new Error('Failed to fetch story details');

        const data = await response.json();
        renderContent(data);
    } catch (error) {
        if (error.name !== 'AbortError') {
            modalContent.innerHTML = `<div class="text-red-400 p-4">Error: ${error.message}</div>`;
        }
    }
}

function open() {
    modalContainer.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

export function close() {
    if (modalContainer) {
        modalContainer.classList.add('hidden');
        document.body.style.overflow = '';
        if (currentAbortController) currentAbortController.abort();
    }
}

function showLoading() {
    document.getElementById('story-modal-id').textContent = '...';
    document.getElementById('story-modal-title').textContent = 'Loading...';
    document.getElementById('story-modal-tasks').innerHTML = '<div class="animate-pulse space-y-2"><div class="h-4 bg-bmad-gray rounded w-3/4"></div><div class="h-4 bg-bmad-gray rounded w-1/2"></div></div>';
    modalContent.innerHTML = '<div class="flex justify-center items-center h-full"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-bmad-accent"></div></div>';
}

function renderContent(data) {
    document.getElementById('story-modal-id').textContent = data.story_id;
    document.getElementById('story-modal-title').textContent = data.title;

    // Meta Info
    const metaContainer = document.getElementById('story-modal-meta');
    metaContainer.innerHTML = `
        <div class="flex items-center gap-2 mb-2">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${getStatusColorClass(data.status)} bg-opacity-20 border border-opacity-30">
                ${data.status}
            </span>
        </div>
    `;

    // Tasks
    const tasksContainer = document.getElementById('story-modal-tasks');
    const tasks = Array.isArray(data.tasks) ? data.tasks : [];

    if (tasks.length > 0) {
        tasksContainer.innerHTML = tasks.map(task => `
            <div class="flex items-start gap-3 p-2 rounded hover:bg-white/5 transition-colors group">
                <div class="mt-1 flex-shrink-0">
                    ${task.status === 'done' ?
                `<div class="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center">
                            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                        </div>` :
                `<div class="w-4 h-4 rounded-full border-2 border-bmad-muted"></div>`
            }
                </div>
                <div>
                    <div class="text-sm ${task.status === 'done' ? 'text-bmad-muted line-through' : 'text-bmad-text'}">
                        ${task.title}
                    </div>
                    ${task.inferred ? `<span class="text-[10px] text-bmad-accent/80 font-mono">inferred</span>` : ''}
                </div>
            </div>
        `).join('');
    } else {
        tasksContainer.innerHTML = '<div class="text-sm text-bmad-muted italic">No tasks defined</div>';
    }

    // Body (Markdown)
    if (data.content) {
        // Strip frontmatter if present
        let md = data.content;
        if (md.startsWith('---')) {
            const endIdx = md.indexOf('---', 3);
            if (endIdx !== -1) {
                md = md.substring(endIdx + 3).trim();
            }
        }

        if (typeof window.marked !== 'undefined') {
            modalContent.innerHTML = window.marked.parse(md);
        } else {
            modalContent.innerHTML = `<pre class="whitespace-pre-wrap text-sm text-bmad-text font-mono">${md}</pre>`;
        }
    } else {
        modalContent.innerHTML = '<div class="text-bmad-muted italic py-10 text-center">No additional description available.</div>';
    }
}

function getStatusColorClass(status) {
    switch (status) {
        case 'done': return 'text-green-400 border-green-500';
        case 'review': return 'text-blue-400 border-blue-500';
        case 'in-progress': return 'text-yellow-400 border-yellow-500';
        case 'ready-for-dev': return 'text-purple-400 border-purple-500';
        default: return 'text-bmad-muted border-bmad-gray';
    }
}
