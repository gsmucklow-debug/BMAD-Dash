---
story_id: "4.2"
title: "Workflow History & Gap Detection"
epic: "epic-4"
status: "done"
last_updated: "2026-01-10"
---

# Story 4.2: Workflow History & Gap Detection

As a **user**,
I want **to see which BMAD workflows were executed and detect missing steps**,
So that **I can verify I followed the proper sequence and catch skipped workflows**.

## Acceptance Criteria

### Workflow History Display
- [x] **Chronological History**
    - [x] Displays execution sequence with timestamps.
    - [x] Entries are ordered chronologically (most recent first).
    - [x] Each entry shows: workflow name, timestamp, and result status.
- [x] **Visibility**
    - [x] Workflow history is easily accessible on the dashboard for each story.

### Gap Detection Logic
- [x] **Gap Identification**
    - [x] Detects if story is "done" but no `dev-story` workflow was ever run.
    - [x] Detects if `dev-story` is complete but no `code-review` was executed.
    - [x] Detects if `code-review` is done but 0 passing tests are found (test-gap).
- [x] **Warning & Suggestions**
    - [x] Displays prominent warning: e.g., "⚠️ Missing: code-review workflow".
    - [x] Suggests the next correct command to execute to close the gap.
    - [x] Gap detection triggers automatically on dashboard load.

### Technical & Performance
- [x] **Data Parsing**
    - [x] History is parsed from story file frontmatter (e.g., `workflows` list).
    - [x] System falls back to Git commit message analysis if frontmatter history is missing.
- [x] **Performance**
    - [x] Gap detection logic completes in <50ms.
    - [x] History parsing doesn't block the UI.

## Implementation Tasks

### Backend - Logic & Parsing
- [x] **Update Parser** (`backend/parsers/bmad_parser.py`)
    - [x] Extract `workflows` metadata from story frontmatter.
- [x] **Implement Gap Engine** (`backend/api/dashboard.py`)
    - [x] Create logic to compare story state and workflow evidence.   
- [x] **API Enhancement**
    - [x] Include `workflow_history` and `gaps` in the `/api/dashboard` response.

### Frontend - Components
- [x] **Create History Component** (`frontend/js/components/workflow-history.js`)
    - [x] Render timeline-style list of workflows.
    - [x] Render gap warning banners with "Fix it" commands.
- [x] **Dashboard Integration**
    - [x] Add the new component to the main dashboard view.

### Styling & UX
- [x] **Timeline Styling** (`frontend/css/input.css`)
    - [x] Design a clean, high-contrast timeline.
    - [x] Use BMAD warning colors (ðŸŸ¡) for detected gaps.

### Verification
- [x] **Automated Tests**
    - [x] Backend: Test gap detection logic with mock story data.      
    - [x] Backend: Test workflow history parsing.
- [x] **Manual Verification**
    - [x] Verify that skipping a step triggers the correct warning.    
    - [x] Verify history updates after running a workflow.

## Dev Notes

### NFR Requirements
- Performance: Gap detection <50ms.
- Accessibility: 44x44px for any executable links.
- Trust: "Proof over promises" - gap detection must be accurate based on file modification times and Git.

### Reference Documents
- [Architecture: Data Models](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/architecture.md#data-models)
- [UX Design: Trust through Transparency](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/ux-design-specification.md#trust-through-transparency)

---

## File List

### Backend Files
- `backend/parsers/bmad_parser.py` - Updated to extract workflow history from frontmatter, detect gaps, implement Git fallback, and use severity constants
- `backend/api/dashboard.py` - Updated to include workflow_history and gaps in kanban data (via build_kanban function)
- `backend/models/story.py` - Added workflow_history and gaps fields to Story dataclass
- `backend/services/git_correlator.py` - Used for Git fallback workflow history extraction
- `backend/services/test_discoverer.py` - Used for test-gap detection
- `backend/utils/story_test_parser.py` - Used for parsing test results

### Frontend Files
- `frontend/js/components/workflow-history.js` - New component for rendering workflow history and gaps, includes renderAsHtmlString method for template-based rendering
- `frontend/js/components/action-card.js` - Updated to use WorkflowHistory class instead of duplicating rendering logic
- `frontend/js/views/dashboard.js` - Updated to render workflow history in story cards
- `frontend/css/input.css` - Added styles for workflow timeline and gap banners

### Test Files
- `tests/test_workflow_history.py` - Tests for workflow history parsing and gap detection
- `tests/test_parsers.py` - Updated tests for gap detection logic

---

## Change Log

### 2026-01-10 - Initial Implementation
- Added workflow history extraction from story frontmatter
- Implemented gap detection logic for missing workflows
- Created WorkflowHistory component for frontend rendering
- Integrated workflow history into dashboard and action card
- Added test coverage for workflow history parsing

---

## Evidence

### Automated Tests
- `tests/test_workflow_history.py` - All tests passing (4/4)
  - Test workflow history extraction from frontmatter
  - Test gap detection for missing dev-story workflow
  - Test gap detection for missing code-review workflow
  - Test gap detection for test-gap

### Manual Verification
- Verified workflow history displays chronologically
- Verified gap warnings appear when workflows are missing
- Verified "Fix it" commands are clickable and copy to clipboard
- Verified history updates after running workflows
- Verified gap detection triggers automatically on dashboard load

### Screenshots
- Workflow history timeline with gaps detected
- Gap warning banner with "Fix it" command
- Action card with integrated workflow history section
