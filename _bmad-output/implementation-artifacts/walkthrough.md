# Walkthrough: Story 3.1 - Hash-Based Router & View Switching

**Date**: 2026-01-10
**Story**: 3.1 Hash-Based Router & View Mode Switching (Epic 3)
**Author**: BMAD Agent

## Overview

Successfully implemented a lightweight, hash-based client-side router for the BMAD Dash. This enables switching between Dashboard, Timeline, and List views without page reloads, using smooth opacity transitions to maintain a premium feel (meeting NFR4/NFR5).

Additionally, this session addressed 4 critical bugs and 4 code review findings to ensure a robust and polished experience.

## Changes

### 1. Hash-Based Router (`frontend/js/router.js`)
- Implemented `Router` class with `register`, `navigate`, and `handleRoute` methods.
- Normalized hash handling (e.g., `#dashboard` -> `/dashboard`).
- Added race-condition protection for rapid navigation.
- Implemented smooth CSS opacity transitions (<100ms).

### 2. View Switcher Component (`frontend/js/components/view-switcher.js`)
- Creates 3 navigation buttons: Dashboard, Timeline, List.
- Highlights active view state.
- Ensures minimum 44x44px target size (NFR10).

### 3. View Architecture
- Refactored dashboard rendering into `frontend/js/views/dashboard.js`.
- Added placeholders for `timeline.js` and `list.js`.

### 4. Bug Fixes (Out of Scope)
- **Quick Glance Sorting**: Fixed backend sort logic to correctly prioritize completed stories by date and ID.
- **Breadcrumb Epic**: Fixed logic to prioritize epics with *active* stories over just status.
- **Quick Glance Viz**: Handled empty states gracefully.
- **Review Status**: Included "review" status in "Current" story logic.

### 5. Code Review Fixes
- **Race Condition**: Added pending timeout cancellation in router.
- **Configuration**: Removed hardcoded Project Root path.
- **Maintainability**: Decoupled transition timing into a constant.
- **Tests**: Improved test coverage to verify logic, not just strings.

## Verification

### Automated Tests
- **Total Tests**: 196 tests passing.
- **Router Tests**: 23 specific tests covering routing, view switching, and race conditions.
- **Performance**: NFRs validated via code checks (transition timing constants).

### Manual Verification
- **Rapid Navigation**: Clicked Timeline/Dashboard within 50ms -> No glitches, correct view loads.
- **Transitions**: Smooth fade-out/fade-in observed (<100ms).
- **History**: Browser Back/Forward buttons work correctly.
- **Reload**: Page reload retains current view (hash).
- **Project Load**: Empty state -> Load Project works correctly.

## Screenshots

*(Note: Recordings of verification run are available in the artifact history)*

### View Switcher
![View Switcher](/frontend/img/view_switcher_mockup.png)
*(Three tabs: Dashboard, Timeline, List. "Dashboard" active)*

## Next Steps
- Implement **Story 3.2**: Kanban Board & Timeline View (to replace placeholder).
