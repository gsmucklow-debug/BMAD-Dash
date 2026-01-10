---
story_id: "3.1"
title: "Hash-Based Router & View Mode Switching"
epic: "epic-3"
status: "done"
last_updated: "2026-01-10"
---

# Story 3.1: Hash-Based Router & View Mode Switching

As a **user**,
I want **to switch between Dashboard, Timeline, and List views using clickable buttons**,
So that **I can adapt the interface to my current cognitive state**.

## Acceptance Criteria

- [x] **Hash-Based Router Implementation**
    - [x] Implement simple hash router in `frontend/js/router.js`
    - [x] Handle routes: `#/dashboard` (default), `#/timeline`, `#/list`
    - [x] Listen for `hashchange` events to update view
    - [x] Update browser URL hash when view changes programmatically

- [x] **View Switcher Component**
    - [x] Create UI control with 3 buttons: Dashboard, Timeline, List
    - [x] Highlight active view button
    - [x] Place at top of page (header area)
    - [x] Ensure buttons meet minimum click target size (44x44px - NFR10)

- [x] **View Rendering Logic**
    - [x] renderDashboard() displays current Grid/Kanban layout
    - [x] renderTimeline() displays placeholder "Timeline View Coming Soon"
    - [x] renderList() displays placeholder "List View Coming Soon"
    - [x] Views are swapped dynamically without page reload

- [x] **Performance & UX**
    - [x] Transitions complete in <100ms (NFR5)
    - [x] Smooth opacity fade transition (60fps - NFR4)
    - [x] Back/Forward browser buttons work to navigate history

## Implementation Tasks

- [x] **Create Router Module** (`frontend/js/router.js`)
    - [x] Implement `initRouter(routes)` function
    - [x] Implement `navigateTo(route)` function
    - [x] Define route handlers map

- [x] **Update App Shell** (`frontend/index.html`)
    - [x] Add container for View Switcher in header
    - [x] Ensure main content area has ID for view injection

- [x] **Create View Switcher Component** (`frontend/js/components/view-switcher.js`)
    - [x] Render buttons with active state logic
    - [x] Bind click events to `navigateTo`

- [x] **Create View Placeholders**
    - [x] Create `frontend/js/views/dashboard.js` (refactor existing render logic)
    - [x] Create `frontend/js/views/timeline.js` (placeholder)
    - [x] Create `frontend/js/views/list.js` (placeholder)

- [x] **Update Main App Entry** (`frontend/js/app.js`)
    - [x] Initialize router on startup
    - [x] Integrate View Switcher

## Dev Notes

- **Architecture**: Move away from monolithic `app.js` rendering. 
- **Refactoring**: Extract current dashboard rendering logic into `views/dashboard.js`.
- **CSS**: Use CSS transitions for the opacity fade on view change.
- **State**: Ensure project data is cached or passed to views so switching doesn't re-fetch API every time (unless needed).

## Dev Agent Record

### Implementation Plan

Implemented hash-based routing system following TDD red-green-refactor cycle:

1. **Test-First Approach (RED)**:
   - Created comprehensive test suite with 21 tests covering router functionality, view switching, HTML structure, and NFRs
   - Tests initially failed as expected

2. **Implementation (GREEN)**:
   - Enhanced `Router` class with default route support, hash normalization, and CSS transitions for <100ms swaps (NFR5)
   - Created `view-switcher.js` component with three 44x44px buttons (NFR10) and active state management
   - Created view modules: `dashboard.js`, `timeline.js`, `list.js`
   - Refactored `app.js` to integrate router and manage global dashboard data state
   - Added view-switcher container to `index.html`

3. **Validation**:
   - All 21 new router tests passing
   - Full test suite: 196 tests passing, 0 failures
   - Transitions use opacity fade with 80ms timing for smooth 60fps rendering (NFR4)

### Technical Decisions

- **Data Caching**: Dashboard data stored in global `dashboardData` variable to prevent API re-fetch on view switching
- **Transition Timing**: Used 80ms opacity transition (40ms fade-out + 40ms fade-in) to meet <100ms requirement (NFR5) with buffer
- **Route Normalization**: Router automatically adds leading `/` to hash for consistent route handling
- **Default Route**: Set `/dashboard` as default for empty hash (`#` or `#/`)
- **Browser History**: Native hash-based routing automatically supports back/forward buttons

### Completion Notes

✅ Story 3.1 successfully implemented with all acceptance criteria met:
- Hash-based router handles `/dashboard`, `/timeline`, `/list` routes
- View switcher component with properly sized buttons (44x44px min - NFR10)
- Three views created: dashboard (shows breadcrumb + quick-glance), timeline (placeholder), list (placeholder)
- Smooth opacity transitions <100ms at 60fps (NFR4, NFR5)
- Browser back/forward buttons work correctly
- All 196 tests passing including 21 new router-specific tests

## File List

### New Files
- `frontend/js/components/view-switcher.js` - View switcher UI component
- `frontend/js/views/dashboard.js` - Dashboard view module
- `frontend/js/views/timeline.js` - Timeline view placeholder
- `frontend/js/views/list.js` - List view placeholder
- `tests/test_router.py` - Comprehensive router test suite (21 tests)

### Modified Files
- `frontend/js/router.js` - Enhanced with default routes, transitions, normalization
- `frontend/js/app.js` - Integrated router, view switcher, and view modules
- `frontend/index.html` - Added view-switcher-container div

## Change Log

- **2026-01-10**: Story 3.1 implementation complete
  - Implemented hash-based router with `/dashboard`, `/timeline`, `/list` routes
  - Created view switcher component with 44x44px buttons in header
  - Created three view modules (dashboard, timeline, list)
  - Added smooth opacity transitions (<100ms, 60fps)
  - All 196 tests passing (21 new router tests added)
  - Ready for code review

## Status

**Current Status**: review
**Last Updated**: 2026-01-10
