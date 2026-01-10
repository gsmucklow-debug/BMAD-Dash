# Story 3.2: Kanban Board & Timeline View

Implement the full Kanban Board and Timeline View to complete the "Multi-View Dashboard" epic.

## User Review Required

> [!NOTE]
> The Timeline View (Story 4.2 dependency) will be implemented with **mock/placeholder data** for now, as the full workflow history API is part of a future story. We will structure it correctly to receive real data later.

## Proposed Changes

### Frontend Logic

#### [MODIFY] [dashboard.js](file:///f:/BMAD%20Dash/frontend/js/views/dashboard.js)
-   Remove placeholder text.
-   Implement `renderKanbanBoard(data)` to create the 4-column layout:
    -   **TODO**: Backlog stories
    -   **IN PROGRESS**: Ready for Dev & In Progress stories
    -   **REVIEW**: Review stories
    -   **COMPLETE**: Done stories
-   Implement `renderStoryCard(story)` reusing `evidence-badge.js`.
-   Implement `renderActionCard(story)` for the "Current" story (unified view).

#### [MODIFY] [timeline.js](file:///f:/BMAD%20Dash/frontend/js/views/timeline.js)
-   Remove placeholder text.
-   Implement `renderTimeline(data)` to show a vertical list of events.
-   *Temporary Logic*: Derive "events" from story `last_updated` and `completed` timestamps to populate the timeline since full history isn't available yet.

### Styling

#### [MODIFY] [input.css](file:///f:/BMAD%20Dash/frontend/css/input.css)
-   Add grid/flex utilities for Kanban columns.
-   Add card styling (bg-bmad-gray, borders, hover states).
-   Add timeline connecting lines and dots styling.

### Tests

#### [NEW] [test_views.py](file:///f:/BMAD%20Dash/tests/test_views.py)
-   New test file to verify the HTML structure of the views.
-   `test_dashboard_renders_kanban_columns`: Verify 4 columns exist.
-   `test_dashboard_renders_cards`: Verify story cards are generated from data.
-   `test_timeline_renders_events`: Verify timeline list structure.

## Verification Plan

### Automated Tests
-   Run the new view tests: `pytest tests/test_views.py`
-   Run all frontend tests: `pytest tests/`

### Manual Verification
-   **Kanban Board**:
    -   Verify all 4 columns are visible.
    -   Verify stories are in the correct columns (based on `sprint-status.yaml`).
    -   Verify "Current Focus" story appears as a unified Action Card (or distinct style).
-   **Timeline View**:
    -   Verify timeline renders with dates.
    -   Switch back and forth to ensure no state loss.
