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

### Review Follow-ups (AI Code Review)

#### Task 6: Add Frontend Unit Tests for JavaScript Logic
**Priority:** Medium  
**Source:** AI Code Review 2026-01-10  
**Implementation Details:**
- Set up Jest or similar JavaScript test framework
- Write unit tests for `parseProgress()` function
  - Test valid inputs: "2/8 tasks" → 25%
  - Test edge cases: "0/0", "10/5 tasks", "-1/5", "abc/xyz"
  - Verify bounds checking (0-100%)
- Write unit tests for `escapeHtml()` function
  - Test XSS prevention: `"<script>"` → escaped
- Write unit tests for render functions
  - Test null/undefined data handling
  - Test empty state rendering

**Acceptance:**
- Jest configured in project
- All logic functions have unit test coverage
- Tests verify edge cases and security (XSS)

#### Task 7: Consider Structured API Progress Format
**Priority:** Low (Nice to Have)  
**Source:** AI Code Review 2026-01-10  
**Implementation Details:**
- Evaluate changing API progress format from string to structured object
- Current: `"progress": "2/8 tasks"` (requires client-side regex parsing)
- Proposed: `"progress": {"completed": 2, "total": 8, "unit": "tasks", "percentage": 25}`
- Would eliminate fragile string parsing on frontend
- Requires coordination: backend API changes + frontend component updates

**Acceptance:**
- Decision made: keep string format OR migrate to structured
- If migrating: backend and frontend updated together
- Tests updated to reflect new format

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

## Code Review Findings

**Review Date:** 2026-01-10  
**Review Type:** Adversarial Senior Developer Code Review  
**Reviewer:** AI Code Review Agent

### Issues Found: 7 Total (2 Critical, 4 Medium, 1 Low)

#### Critical Issues (Fixed)
1. ✅ **Status Desynchronization** - Story marked "done" but sprint-status.yaml showed "review"
   - **Fix:** Updated sprint-status.yaml to sync status to "done"
   
2. ✅ **Missing Dev Agent Record** - No file list or change log documented
   - **Fix:** Added complete Dev Agent Record section with file list and change log

#### Medium Issues (Fixed)
3. ✅ **Inconsistent Error Handling** - Sub-render functions could receive undefined parameters
   - **Fix:** Added defensive destructuring with default values in render()

4. ✅ **Progress Bar Parsing Fragile** - No bounds checking, could return >100% on malformed data
   - **Fix:** Added validation, NaN checks, and bounds capping (0-100%)

5. ✅ **Hard-Coded DOM IDs** - Magic string 'quick-glance-container'
   - **Fix:** Replaced with CONTAINER_ID constant

#### Medium Issues (Deferred - Action Items Created)
6. 📋 **No Frontend Unit Tests** - Tests only verify file serving, not logic execution
   - **Action:** Add Jest tests for parseProgress(), escapeHtml(), render functions

7. 📋 **API Progress Format** - Returns string "2/8 tasks" requiring client-side parsing
   - **Action:** Consider structured format: `{"completed": 2, "total": 8, "unit": "tasks"}`

#### Low Issues
- None remaining (magic strings fixed)

### Review Outcome
- **Status:** ✅ PASSED
- **Issues Fixed:** 5 of 7 (2 deferred as improvements)
- **All Critical Issues:** Resolved
- **Story Status:** done (review complete)

---

## Status
**Current Status:** done  
**Dependencies:** Story 1.4 (Shell), Story 1.3 (API)
**Completed:** 2026-01-10  
**Code Review:** Completed 2026-01-10

## Implementation Summary

All 5 tasks completed:
1. ✅ Created `frontend/js/components/quick-glance.js` component with render function
2. ✅ Implemented VSCode-style progress bars with Tailwind CSS
3. ✅ Integrated component into `app.js` (already imported, now functional)
4. ✅ Added error handling and empty state handling
5. ✅ Added tests to `tests/test_frontend_integration.py`

**Key Features:**
- Three-section layout: Done | Current | Next
- Progress bar parsing from "X/Y tasks" format
- Responsive grid layout (stacks on mobile, 3-column on desktop)
- Empty state handling for start/end of project
- XSS protection via HTML escaping
- Dark theme integration with BMAD color scheme

**Tests:** All 101 tests passing (25 frontend integration tests + 76 other tests)

---

## Dev Agent Record

### File List

**Created:**
- `frontend/js/components/quick-glance.js` - Quick Glance component with Done/Current/Next sections and progress bars

**Modified:**
- `frontend/js/app.js` - Integrated Quick Glance component rendering (lines 6, 30)
- `tests/test_frontend_integration.py` - Added Quick Glance component tests (lines 67-246)
- `backend/api/dashboard.py` - Quick Glance data builder already implemented in Story 1.3 (lines 190-264)

### Change Log

**2026-01-10:**
- Created Quick Glance component with three-section layout (Done | Current | Next)
- Implemented VSCode-style progress bar with "X/Y tasks" parsing
- Added XSS protection via HTML escaping
- Integrated component into app.js main render flow
- Added error handling for missing/malformed data
- Added 6 frontend integration tests for Quick Glance component
- Verified responsive grid layout (stacks on mobile, 3-column on desktop)
- All 101 tests passing

**Code Review (2026-01-10):**
- Fixed progress bar bounds checking to prevent overflow on malformed data
- Added defensive error handling with default values
- Replaced magic strings with constants (CONTAINER_ID)
- Validated against architecture requirements (Story 1.3 API contract)
- Status synced: review → done