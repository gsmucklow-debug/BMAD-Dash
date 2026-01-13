/**
 * BMAD Dash - Dashboard View
 * Main dashboard view showing breadcrumb, quick glance, and Kanban board
 * Story 5.55: Smart Per-Project Cache Layer
 */

import { render as renderBreadcrumb } from '../components/breadcrumb.js';
import { render as renderQuickGlance } from '../components/quick-glance.js';
import { getBadgesSkeletonHTML, renderBadgesFromData } from '../components/evidence-badge.js';
import { renderActionCard, attachActionCardListeners } from '../components/action-card.js';
import { render as renderCacheStatus, attachListeners as attachCacheListeners } from '../components/cache-status.js';
import { getBMADSync } from '../components/bmad-sync.js';
import { openStoryDetail } from '../components/story-modal.js';

/**
 * Render the Dashboard View
 * @param {Object} data - Dashboard data from API
 */
export async function render(data) {
    const container = document.getElementById('main-content');
    if (!container) {
        console.error('Main content container not found');
        return;
    }

    // Render breadcrumb and quick glance components
    renderBreadcrumb(data.breadcrumb);
    renderQuickGlance(data);

    // Flatten stories for badge initialization
    const allStories = [];
    if (data.kanban) {
        Object.values(data.kanban).forEach(list => allStories.push(...list));
    }

    // Clear main content and show Action Card + Kanban board
    const projectRoot = data.project.root_path;
    container.innerHTML = `
        <div class="flex flex-col gap-6 h-full">
            ${renderCacheStatus(data.smart_cache, projectRoot)}
            ${renderActionCard(data)}
            ${renderKanbanBoard(data.kanban, projectRoot)}
        </div>
    `;

    // Attach action card event listeners after rendering
    attachActionCardListeners(data);

    // Attach cache status event listeners - will trigger project reload
    attachCacheListeners(projectRoot, async () => {
        // Trigger project reload which will refresh dashboard
        const loadButton = document.getElementById('load-project-btn');
        if (loadButton) loadButton.click();
    });

    // Initialize BMAD sync (Story 5.6) - fire and forget, non-blocking
    const bmadSync = getBMADSync();
    bmadSync.init(projectRoot).catch(err => console.error('BMAD sync init failed:', err));

    // Initialize badges for all stories using pre-fetched evidence data
    allStories.forEach(story => {
        // Update Board Card badge
        const boardBadgeId = `board-badges-${story.id}`;
        if (document.getElementById(boardBadgeId)) {
            renderBadgesFromData(
                boardBadgeId,
                story.evidence || {},
                story.id,
                projectRoot
            );
        }
    });

    // Attach delegated click listener for story cards
    container.addEventListener('click', (e) => {
        const card = e.target.closest('[data-story-id]');
        if (card && !e.target.closest('button') && !e.target.closest('a')) {
            const storyId = card.getAttribute('data-story-id');
            openStoryDetail(storyId, projectRoot);
        }
    });
}

function renderKanbanBoard(kanbanData, projectRoot) {
    const columns = {
        'todo': { title: 'To Do', items: kanbanData.todo || [], color: 'bg-gray-500/10 border-gray-500/20' },
        'in_progress': { title: 'In Progress', items: kanbanData.in_progress || [], color: 'bg-blue-500/10 border-blue-500/20' },
        'review': { title: 'Review', items: kanbanData.review || [], color: 'bg-purple-500/10 border-purple-500/20' },
        'done': { title: 'Complete', items: kanbanData.done || [], color: 'bg-green-500/10 border-green-500/20' }
    };

    return `
        <div class="grid grid-cols-4 gap-4 flex-1 min-h-0 overflow-x-auto custom-scrollbar pb-2">
            ${Object.entries(columns).map(([id, col]) => renderColumn(id, col, projectRoot)).join('')}
        </div>
    `;
}

function normalizeStatus(status) {
    const s = status?.toLowerCase() || 'todo';
    if (['pending', 'todo', 'backlog'].includes(s)) return 'todo';
    if (['in-progress', 'active', 'blocked'].includes(s)) return 'in-progress';
    if (['review', 'validating'].includes(s)) return 'review';
    if (['done', 'complete', 'closed'].includes(s)) return 'done';
    return 'todo';
}

function renderColumn(id, column, projectRoot) {
    return `
        <div class="flex flex-col h-full rounded-lg border ${column.color} bg-bmad-surface/30 backdrop-blur-sm overflow-hidden min-w-[280px]">
            <div class="p-3 border-b border-bmad-gray flex justify-between items-center bg-bmad-surface/50">
                <h3 class="font-medium text-sm text-bmad-text uppercase tracking-wider">${column.title}</h3>
                <span class="text-xs text-bmad-muted bg-bmad-surface px-2 py-0.5 rounded-full">${column.items.length}</span>
            </div>
            <div class="p-3 overflow-y-auto custom-scrollbar flex-1 flex flex-col gap-3">
                ${column.items.map(story => renderStoryCard(story, projectRoot)).join('')}
            </div>
        </div>
    `;
}

function renderStoryCard(story, projectRoot) {
    // Only render badges container here if it's NOT the current story, 
    // BUT we need unique IDs. The update loop targets 'badges-{id}'.
    // If the same story is in Current Focus AND the board, we might have ID conflicts.
    // However, usually current story is "in-progress".
    // Let's render it in both places but use a slightly different logic for the ID if needed?
    // Actually, document.getElementById returns the first one. 
    // updateBadges does not support multiple targets yet.
    // To handle this, let's just make the ID unique in the board: 'board-badges-{id}'
    // And we update both loops.

    // Simplification: reusing specific ID for now. 
    // If duplicates exist, only the first one (Action Card) updates. 
    // Let's handle generic case:

    let formattedEpic = '';
    if (story.epic) {
        const epicStr = String(story.epic).toLowerCase();
        formattedEpic = epicStr.startsWith('epic-') ? epicStr : `epic-${epicStr}`;
    }

    const totalTasks = story.tasks ? story.tasks.length : 0;
    const officialDone = story.tasks ? story.tasks.filter(t => t.status === 'done' && !t.inferred).length : 0;
    const inferredDone = story.tasks ? story.tasks.filter(t => t.inferred).length : 0;
    const totalDone = officialDone + inferredDone;

    let progressHtml = '';
    if (totalTasks > 0) {
        if (inferredDone > 0) {
            progressHtml = `
                <div class="mt-2 text-xs text-bmad-muted group/progress relative cursor-help">
                    <div class="flex items-center gap-1">
                        <span>${totalDone}/${totalTasks} tasks</span>
                        <span class="text-[10px] text-bmad-accent">(${officialDone} off., ${inferredDone} inf.)</span>
                    </div>
                     <!-- Tooltip -->
                    <div class="absolute bottom-full left-0 mb-2 hidden group-hover/progress:block w-48 bg-gray-900 text-white text-[10px] p-2 rounded shadow-lg z-10">
                        ${inferredDone} tasks detected complete via evidence (Git commits) but not marked in story file.
                    </div>
                </div>
            `;
        } else {
            progressHtml = `
                <div class="mt-2 text-xs text-bmad-muted">
                    ${totalDone}/${totalTasks} tasks
                </div>
            `;
        }
    }

    return `
        <div class="bg-bmad-surface hover:bg-bmad-surface-hover border border-bmad-gray hover:border-bmad-accent/50 rounded p-3 transition-all cursor-pointer group shadow-sm" 
             data-story-id="${story.id}">
            <div class="flex justify-between items-start mb-2">
                <span class="text-xs font-mono text-bmad-muted group-hover:text-bmad-accent transition-colors">${story.id}</span>
                ${formattedEpic ? `<span class="text-[10px] bg-bmad-gray/50 px-1.5 py-0.5 rounded text-bmad-muted truncate max-w-[80px]">${formattedEpic}</span>` : ''}
            </div>
            <h4 class="text-sm font-medium text-bmad-text mb-2 line-clamp-2">${story.title}</h4>
            
            ${progressHtml}

             <!-- We use a specific ID to avoid conflict with top card if present. 
                  Actually, let's just use the same ID logic for now, noticing the conflict.
                  Correction: create a unique class or just accept the limitation for this sprint.
                  Better: Use 'board-badges-${story.id}' and update the loop.
             -->
            <div id="board-badges-${story.id}" class="mt-2">
                ${getBadgesSkeletonHTML()}
            </div>
        </div>
    `;
}
