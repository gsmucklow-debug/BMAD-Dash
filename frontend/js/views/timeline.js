/**
 * BMAD Dash - Timeline View
 * Displays a vertical timeline of project events (derived from story updates)
 */

import { render as renderBreadcrumb } from '../components/breadcrumb.js';

/**
 * Render the Timeline View
 * @param {Object} data - Dashboard data from API
 */
export function render(data) {
    const container = document.getElementById('main-content');
    if (!container) {
        console.error('Main content container not found');
        return;
    }

    renderBreadcrumb(data.breadcrumb);

    const allStories = [];
    if (data.kanban) {
        Object.values(data.kanban).forEach(list => allStories.push(...list));
    }

    const events = getTimelineEvents(allStories);

    container.innerHTML = `
        <div class="max-w-4xl mx-auto p-6 h-[calc(100vh-100px)] overflow-y-auto custom-scrollbar">
            <div class="flex justify-between items-center mb-8">
                <h1 class="text-3xl font-bold text-bmad-text">Project Timeline</h1>
                <span class="text-xs text-bmad-muted bg-bmad-surface px-2 py-1 rounded">Derived from Story Status</span>
            </div>
            
            <div class="relative border-l border-bmad-gray ml-3 space-y-8 pb-12">
                ${events.length ? events.map(event => renderTimelineEvent(event)).join('') : renderEmptyState()}
            </div>
        </div>
    `;
}

function getTimelineEvents(stories) {
    const events = [];

    stories.forEach(story => {
        // 1. Add "Completed" event for done stories
        if (['done', 'complete', 'closed'].includes(story.status?.toLowerCase())) {
            events.push({
                date: story.completed || story.last_updated || 'Recently',
                title: `History: Story ${story.id} Completed`,
                description: story.title,
                type: 'completion',
                storyId: story.id
            });
        }

        // 2. Add "Started/Active" event for in-progress stories
        if (['in-progress', 'active'].includes(story.status?.toLowerCase())) {
            events.push({
                date: story.last_updated || 'Active Now',
                title: `Working on: Story ${story.id}`,
                description: story.title,
                type: 'progress',
                storyId: story.id
            });
        }

        // 3. Add "Created" event if we have a created date
        if (story.created) {
            events.push({
                date: story.created,
                title: `Planned: Story ${story.id} Created`,
                description: story.title,
                type: 'creation',
                storyId: story.id
            });
        }
    });

    // Mock generic "Project Initialized" event
    events.push({
        date: '2026-01-01',
        title: 'Project Initialized',
        description: 'BMAD Project Scaffold creation',
        type: 'milestone',
        storyId: '0.0'
    });

    // Sort events: Newest first (Reverse Chronological)
    events.sort((a, b) => {
        const dateA = normalizeDate(a.date);
        const dateB = normalizeDate(b.date);

        // Sort by Date Descending
        if (dateA > dateB) return -1;
        if (dateA < dateB) return 1;

        // If dates are equal, sort by Story ID Descending (propely handled as version parts)
        const partsA = (a.storyId || "0.0").split('.').map(Number);
        const partsB = (b.storyId || "0.0").split('.').map(Number);

        // Compare major version
        if (partsA[0] !== partsB[0]) return partsB[0] - partsA[0];
        // Compare minor version
        return (partsB[1] || 0) - (partsA[1] || 0);
    });

    return events;
}

function normalizeDate(dateStr) {
    if (!dateStr || dateStr === 'Recently' || dateStr === 'Active Now') {
        // Return a future date to ensure "Recently" and "Active Now" stay at top
        return '9999-12-31';
    }
    return dateStr;
}

function renderTimelineEvent(event) {
    let iconColor = 'bg-bmad-gray';
    if (event.type === 'completion') iconColor = 'bg-green-500';
    if (event.type === 'progress') iconColor = 'bg-bmad-accent';
    if (event.type === 'milestone') iconColor = 'bg-purple-500';
    if (event.type === 'creation') iconColor = 'bg-blue-500';

    return `
        <div class="ml-8 relative group">
            <span class="absolute -left-[41px] top-1 flex items-center justify-center w-6 h-6 bg-bmad-surface rounded-full ring-4 ring-bmad-surface shadow-sm text-bmad-text">
                <span class="${iconColor} w-2.5 h-2.5 rounded-full block"></span>
            </span>
            <div class="bg-bmad-surface border border-bmad-gray p-4 rounded-lg shadow-sm hover:border-bmad-accent/30 transition-colors">
                <div class="flex justify-between items-start mb-1">
                    <h3 class="text-lg font-semibold text-bmad-text group-hover:text-white transition-colors">
                        ${event.title}
                    </h3>
                    <time class="text-xs text-bmad-muted font-mono bg-bmad-gray/20 px-1.5 py-0.5 rounded">${event.date}</time>
                </div>
                <p class="text-sm text-bmad-muted-foreground">${event.description}</p>
                 ${event.storyId ? `<div class="mt-2 text-xs font-mono text-bmad-muted">Ref: ${event.storyId}</div>` : ''}
            </div>
        </div>
    `;
}

function renderEmptyState() {
    return `
        <div class="ml-8 text-bmad-muted italic">No timeline events found.</div>
    `;
}
