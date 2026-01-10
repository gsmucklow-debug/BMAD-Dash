---
story_id: "3.2"
title: "Kanban Board & Timeline View"
epic: "epic-3"
status: done
completed: "2026-01-10"
last_updated: "2026-01-10"
---

# Story 3.2: Kanban Board & Timeline View

As a **user**,
I want **a full Kanban board showing stories in rules and a visual workflow timeline**,
So that **I can see all project work organized by status and understand the execution history**.

## Acceptance Criteria

### Kanban Board
- [x] **Render Kanban Columns**
    - [x] Display 4 columns: TODO | IN PROGRESS | REVIEW | COMPLETE
    - [x] Filter stories from API data into correct columns
    - [x] Sort stories within columns (e.g., by ID or priority)
    - [x] Render generous whitespace between cards (UX)

- [x] **Render Story Cards**
    - [x] Display title, story ID, and epic reference
    - [x] Show status badges (color-coded)
    - [x] Clickable to show details (if applicable, or just visual for now)

- [x] **Unified Action Card (Current Story)**
    - [x] Display prominently for the active story
    - [x] Show combined Story + Task + Command layers (Story 4.1 preview functionality)
    - [x] Identify current task from story data

- [x] **Performance (NFRs)**
    - [x] Board renders in <100ms
    - [x] Supports 100+ stories without degradation

### Timeline View
- [x] **Render Visual Timeline**
    - [x] Display vertical timeline of workflow execution history
    - [x] Show which BMAD workflows were run and when (from Story 4.2 data or placeholder if not ready)
    - [x] Order by most recent at top
    - [x] Clickable entries to see details

- [x] **Integration**
    - [x] Swapping between Dashboard (Kanban) and Timeline retains state
    - [x] No memory leaks

## Implementation Tasks

- [x] **Update Dashboard View** (`frontend/js/views/dashboard.js`)
    - [x] Remove placeholder text
    - [x] Implement `renderKanbanBoard(data)` function
    - [x] Implement `renderColumn(stories, status)`
    - [x] Implement `renderStoryCard(story)`

- [x] **Update Timeline View** (`frontend/js/views/timeline.js`)
    - [x] Remove placeholder text
    - [x] Implement `renderTimeline(data)` function
    - [x] Parse workflow history from story data (or mock if not available yet)

- [x] **Styling**
    - [x] Add Kanban grid styles to `input.css`
    - [x] Add Timeline component styles

- [x] **Tests**
    - [x] Update frontend tests to verify Kanban structure
    - [x] Verify sorting logic
    - [x] Verify timeline rendering

## Dev Notes
- Reuse `evidence-badge.js` for status indicators on cards
- For Action Card, we might need a new component `action-card.js` if it's complex, or keep it in dashboard view for now until Story 4.1 fully defines it. For this story, we'll focus on the *placement* and basic *rendering* of the card.
