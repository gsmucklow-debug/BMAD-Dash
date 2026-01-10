---
story_id: "4.2"
title: "Workflow History & Gap Detection"
epic: "epic-4"
status: "ready-for-dev"
last_updated: "2026-01-10"
---

# Story 4.2: Workflow History & Gap Detection

As a **user**,
I want **to see which BMAD workflows were executed and detect missing steps**,
So that **I can verify I followed the proper sequence and catch skipped workflows**.

## Acceptance Criteria

### Workflow History Display
- [ ] **Chronological History**
    - [ ] Displays execution sequence with timestamps.
    - [ ] Entries are ordered chronologically (most recent first).
    - [ ] Each entry shows: workflow name, timestamp, and result status.
- [ ] **Visibility**
    - [ ] Workflow history is easily accessible on the dashboard for each story.

### Gap Detection Logic
- [ ] **Gap Identification**
    - [ ] Detects if story is "done" but no `dev-story` workflow was ever run.
    - [ ] Detects if `dev-story` is complete but no `code-review` was executed.
    - [ ] Detects if `code-review` is done but 0 passing tests are found (test-gap).
- [ ] **Warning & Suggestions**
    - [ ] Displays prominent warning: e.g., "⚠️ Missing: code-review workflow".
    - [ ] Suggests the next correct command to execute to close the gap.
    - [ ] Gap detection triggers automatically on dashboard load.

### Technical & Performance
- [ ] **Data Parsing**
    - [ ] History is parsed from story file frontmatter (e.g., `workflows` list).
    - [ ] System falls back to Git commit message analysis if frontmatter history is missing.
- [ ] **Performance**
    - [ ] Gap detection logic completes in <50ms.
    - [ ] History parsing doesn't block the UI.

## Implementation Tasks

### Backend - Logic & Parsing
- [ ] **Update Parser** (`backend/parsers/bmad_parser.py`)
    - [ ] Extract `workflows` metadata from story frontmatter.
- [ ] **Implement Gap Engine** (`backend/api/dashboard.py`)
    - [ ] Create logic to compare story state and workflow evidence.
- [ ] **API Enhancement**
    - [ ] Include `workflow_history` and `gaps` in the `/api/dashboard` response.

### Frontend - Components
- [ ] **Create History Component** (`frontend/js/components/workflow-history.js`)
    - [ ] Render timeline-style list of workflows.
    - [ ] Render gap warning banners with "Fix it" commands.
- [ ] **Dashboard Integration**
    - [ ] Add the new component to the main dashboard view.

### Styling & UX
- [ ] **Timeline Styling** (`frontend/css/input.css`)
    - [ ] Design a clean, high-contrast timeline.
    - [ ] Use BMAD warning colors (🟡) for detected gaps.

### Verification
- [ ] **Automated Tests**
    - [ ] Backend: Test gap detection logic with mock story data.
    - [ ] Backend: Test workflow history parsing.
- [ ] **Manual Verification**
    - [ ] Verify that skipping a step triggers the correct warning.
    - [ ] Verify history updates after running a workflow.

## Dev Notes

### NFR Requirements
- Performance: Gap detection <50ms.
- Accessibility: 44x44px for any executable links.
- Trust: "Proof over promises" - gap detection must be accurate based on file modification times and Git.

### Reference Documents
- [Architecture: Data Models](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/architecture.md#data-models)
- [UX Design: Trust through Transparency](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/ux-design-specification.md#trust-through-transparency)
