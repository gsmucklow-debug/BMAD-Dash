---
story_id: "1.5"
story_key: "1-5-quick-glance-bar-progress-indicators"
epic: 1
title: "Quick Glance Bar & Progress Indicators"
status: "done"
created: "2026-01-09"
completed: "2026-01-10"
context_engine_version: "v1.0"
---

# Story 1.5: Quick Glance Bar & Progress Indicators

## User Story

As a **user**,  
I want **a Quick Glance Bar showing Done | Current | Next stories with progress bars**,  
So that **I understand my temporal position in the project at a glance**.

## Business Context

This story builds on the Frontend Shell (Story 1.4) by adding the "head-up display" of the project. While the breadcrumb shows hierarchical context (where am I in the structure?), the Quick Glance Bar shows temporal context (where am I in the timeline?).

**Value:** Reduces cognitive load by answering "What did I just finish?", "What am I doing now?", and "What's next?" without requiring the user to scan a full Kanban board.

## Acceptance Criteria

**Given** the dashboard is loaded  
**When** Quick Glance Bar renders below breadcrumbs  
**Then** displays three sections: Done | Current | Next

**And** Done section shows title of last completed story  
**And** Current section shows title of in-progress story (highlighted)  
**And** Next section shows title of next TODO story  
**And** Epic progress bar shows "N/M stories complete" format  
**And** Story progress bar shows "N/M tasks complete" format  
**And** progress bars use VSCode-style visual indicators (thin lines, color-coded)  
**And** generous whitespace between sections (UX requirement)  
**And** temporal focus is instantly scannable (<3 seconds to orient)  
**And** component renders in <100ms (NFR4 requirement)

---

## Implementation Tasks

### Task 1: Create `frontend/js/components/quick-glance.js` Component
**Implementation Details:**
- Create component module `quick-glance.js`
- Export `render(data)` function that accepts `data.quick_glance` and `data.project`
- Parse data to extract done, current, and next stories
- Handle null values (e.g., start of project has no 'done', end has no 'next')
- Calculate progress percentages for visual bars
- Render semantic HTML structure describing the flow
- Apply CSS classes for layout and styling

**Acceptance:**
- Component renders correctly with full data
- Component renders gracefully with partial data (start/end of project)
- Structure matches design requirements

### Task 2: Implement Progress Bar Logic & Styling
**Implementation Details:**
- Create utility function to generate progress bar HTML
- Update `input.css` with progress bar specific styles if needed (or use Tailwind utilities)
- Implement "VSCode-style" aesthetics:
    - Thin graphical bar (height: 2px or 4px)
    - Background trace (darker gray)
    - Progress fill (accent color or specific status color)
- Add text labels for "X/Y complete" next to bars
- Ensure high contrast and readability

**Acceptance:**
- Progress bars visually represent the data
- Text labels are accurate and readable
- Styling matches dark theme and VSCode aesthetic

### Task 3: Integrate Component into `app.js` and `index.html`
**Implementation Details:**
- Update `index.html` to ensure `quick-glance-container` is ready (done in 1.4)
- Update `app.js` to import and call `renderQuickGlance`
- Pass appropriate data subset from the global dashboard API response
- Ensure integration doesn't block main render

**Acceptance:**
- Quick Glance bar appears on page load
- Updates when project root changes (via existing app.js logic)

### Task 4: Add Error Handling & Empty States
**Implementation Details:**
- Handle case where `quick_glance` object is missing from API
- Handle case where specific stories are missing properties
- Display friendly "No active story" message if Current is null
- Ensure layout remains stable regardless of content length (truncate if necessary or wrap)

**Acceptance:**
- No console errors on malformed data
- UI looks broken? No -> UI degrades gracefully

### Task 5: Write Frontend Tests for Quick Glance
**Implementation Details:**
- Create `frontend/js/__tests__/quick-glance.test.js` (if using JS test runner) OR
- Update `tests/test_frontend_integration.py` to check for Quick Glance elements
- Verify presence of Done/Current/Next sections
- Verify text content matches mock data
- Check visibility of progress bars

**Acceptance:**
- Tests pass
- Verifies core functionality

---

## Technical Specifications

### Data Structure (from API)

The `/api/dashboard` endpoint already returns this structure (Story 1.3):

```json
"quick_glance": {
    "done": {
        "story_id": "1.3",
        "title": "Flask API - Dashboard Endpoint",
        "completed": "2026-01-09 20:00"
    },
    "current": {
        "story_id": "1.4",
        "title": "Frontend Shell & Breadcrumb Navigation",
        "status": "in-progress",
        "progress": "2/8 tasks"
    },
    "next": {
        "story_id": "1.5",
        "title": "Quick Glance Bar & Progress Indicators"
    }
}
```

### HTML Structure (`quick-glance.js` output)

```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 bg-bmad-gray/50 p-4 rounded-lg border border-bmad-gray">
    <!-- Done Section -->
    <div class="flex flex-col">
        <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Last Completed</span>
        <div class="font-medium text-bmad-text truncate">Story 1.3: Flask API</div>
        <div class="text-xs text-bmad-green mt-1 flex items-center">
             <span class="w-2 h-2 rounded-full bg-bmad-green mr-2"></span> Done
        </div>
    </div>

    <!-- Current Section (Highlighted) -->
    <div class="flex flex-col relative pl-4 border-l border-bmad-muted/30">
        <span class="text-xs uppercase tracking-wider text-bmad-accent mb-1 font-bold">Current Focus</span>
        <div class="font-bold text-white text-lg truncate">Story 1.4: Frontend Shell</div>
        
        <!-- Story Progress -->
        <div class="mt-2 w-full">
            <div class="flex justify-between text-xs text-bmad-muted mb-1">
                <span>Story Progress</span>
                <span>2/8 tasks</span>
            </div>
            <div class="h-1 w-full bg-gray-700 rounded-full overflow-hidden">
                <div class="h-full bg-bmad-accent transition-all duration-500" style="width: 25%"></div>
            </div>
        </div>
    </div>

    <!-- Next Section -->
    <div class="flex flex-col pl-4 border-l border-bmad-muted/30">
        <span class="text-xs uppercase tracking-wider text-bmad-muted mb-1">Up Next</span>
        <div class="font-medium text-bmad-text truncate">Story 1.5: Quick Glance</div>
        <div class="text-xs text-bmad-muted mt-1">
            Status: Ready for Dev
        </div>
    </div>
</div>
```

### Styling
- Use `truncate` to handle long titles.
- Use `grid-cols-1 md:grid-cols-3` for responsive layout (stack on mobile, side-by-side on desktop).
- Current section gets visual weight (bolder text, accent color).

---

## Testing Strategy

### Manual Testing
1. Load dashboard.
2. Verify "Last Completed", "Current Focus", and "Up Next" labels exist.
3. Check that titles match the current project state.
4. Verify progress bar for current story exists and shows correct width/text.
5. Check responsiveness: resize window to ensure layout adapts.

### Automated Testing
- `test_frontend_integration.py` will inspect the DOM for `quick-glance-container` content.
- Verify that necessary classes are applied.

---

## Status
**Current Status:** ready-for-dev  
**Dependencies:** Story 1.4 (Shell), Story 1.3 (API)
