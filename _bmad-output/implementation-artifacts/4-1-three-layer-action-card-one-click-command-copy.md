---
story_id: "4.1"
title: "Three-Layer Action Card & One-Click Command Copy"
epic: "epic-4"
status: "done"
completed: "2026-01-10"
last_updated: "2026-01-10"
---

# Story 4.1: Three-Layer Action Card & One-Click Command Copy

As a **user**,
I want **a unified Action Card showing Story + Task + Command with one-click copy**,
So that **I can go from "what do I do next?" to executing work in <10 seconds**.

## Acceptance Criteria

### Unified Action Card Display
- [x] **Three-Layer Visibility**
    - [x] Displays three layers in single unified card:
        - **Layer 1 (Story Level):** Story title and acceptance criteria summary
        - **Layer 2 (Task Level):** Current task description (e.g., "Task 2/5: Write API route handler")
        - **Layer 3 (Command Level):** BMAD workflow command based on story state
    - [x] All three layers visible simultaneously (no tabs or hidden sections)
    - [x] Generous spacing between layers (UX requirement)

- [x] **Context-Specific Command Suggestions**
    - [x] If story status is `todo`  suggests `/bmad-bmm-workflows-dev-story`
    - [x] If story status is `in-progress`  suggests continuing dev-story or `/bmad-bmm-workflows-code-review`
    - [x] If story status is `review`  suggests `/bmad-bmm-workflows-code-review`
    - [x] If story status is `done`  suggests next story's command

### One-Click Command Copy
- [x] **Copy Functionality**
    - [x] "Copy Command" button is prominent (44x44px minimum - NFR10)
    - [x] Clicking button copies command text to clipboard
    - [x] Visual feedback shows "Copied!"
    - [x] ARIA live region for screen reader feedback
    - [x] Copy action completes instantly (<20ms)

### Performance & Accessibility
- [x] **Performance Targets**
    - [x] Action Card renders in <50ms (NFR requirement)
    - [x] Component is reactive to data updates (<100ms)
- [x] **Accessibility**
    - [x] Dark theme (#1a1a1a) consistency
    - [x] Mouse-only operation (NFR13)
    - [x] High contrast color-coded indicators (NFR11)

## Implementation Tasks

### Backend - API Enhancements

- [x] **Update Dashboard API** (`backend/api/dashboard.py`)
    - [x] Include `action_card` object in `/api/dashboard` response
    - [x] Implement logic to derive suggested BMAD command based on story state
    - [x] Extract current task index and total task count
    - [x] Summarize acceptance criteria for Layer 1

### Frontend - Action Card Component

- [x] **Implement Component** (`frontend/js/components/action-card.js`)
    - [x] Create `renderActionCard(data)` function
    - [x] Create sub-components for Story, Task, and Command layers
    - [x] Implement clipboard copy logic with visual feedback
    - [x] Ensure persistent feedback (no auto-dismiss per NFR17)

- [x] **Integrate into Views**
    - [x] Update `frontend/js/views/dashboard.js` to include Action Card
    - [x] Update `frontend/js/views/list.js` to use standardized Action Card data

### Styling & UX

- [x] **Custom Styles** (`frontend/css/input.css`)
    - [x] Add `.action-card` container styles (vibrant border, glassmorphism)
    - [x] Add layer separators and spacing
    - [x] Style "Copy Command" button with hover/active states
    - [x] Ensure 44x44px minimum click targets (NFR10)

### Verification

- [x] **Automated Tests**
    - [x] Backend: Test `action_card` data structure in API response
    - [x] Backend: Test command derivation logic for all 4 story states
- [x] **Manual Verification**
    - [x] Verify rendering in <50ms
    - [x] Verify clipboard copy works on all platforms
    - [x] Verify visual feedback persists until next action

## Dev Notes

### Architecture Compliance

**Technical Stack:**
- Frontend: Vanilla JavaScript (ES6+), no frameworks
- Styling: Tailwind CSS v3+ with JIT mode
- Backend: Flask >=3.0.0
- State: Stateless (derived from artifact parse)

**Critical NFRs:**
- Render time <50ms
- Click targets >= 44x44px
- No time-limited interactions (NFR17)
- Dark theme mandatory (#1a1a1a)

### Logic for Command Suggestions

| Story Status  | Suggested Command                          |
| :------------ | :----------------------------------------- |
| `todo`        | `/bmad-bmm-workflows-dev-story`            |
| `in-progress` | `/bmad-bmm-workflows-dev-story`            |
| `review`      | `/bmad-bmm-workflows-code-review`          |
| `done`        | `[Suggest next story's dev-story command]` |

### Previous Story Intelligence (Story 3.3)

**Learnings from Minimal List View & Manual Refresh:**
1. **API Data Path Awareness:** The dashboard API returns current story data at `quick_glance.current`, not `current_story`. The frontend must be careful with this path.
2. **NFR17 Compliance:** Strict no-auto-dismiss policy for notifications. The "Copied!" feedback must persist until the next user action.
3. **Error Handling:** Clipboard API can fail (e.g., if site not in secure context). Always provide fallback guidance ("Select text manually") in the UI.
4. **Render Performance:** Minimal UI components (like the List view) easily hit the <50ms target. The Action Card should aim for similar efficiency by avoiding complex deep-renders if possible.

### Git Intelligence - Recent Work Patterns

**Recent Commits Analysis:**
- **Story 3.3 Implementation:** Followed pattern of `Component creation` → `API integration` → `Styling` → `Manual Verification`.
- **Refactoring:** Recent work on `app.js` and `list.js` focused on removing production console logs and improving keyboard accessibility (Enter/Space on buttons).
- **Badge Logic:** `evidence-badge.js` and `evidence-modal.js` provide a stable pattern for status visualization that the Action Card should align with visually.

### Library & Framework Requirements

- **Tailwind CSS v3.4+:** Use custom colors (`bg-bmad-dark`, `text-bmad-text`) and utilities (`min-h-[44px]`).
- **Vanilla JS:** No React/Vue. Use ES6 modules and export a clean `renderActionCard(data)` function.
- **Flask:** Backend logic for the Action Card should reside in `backend/api/dashboard.py` to minimize extra API calls.

### Refined Logic for Command Suggestions

1. **State: `todo`**
   - Command: `/bmad-bmm-workflows-dev-story`
   - Reasoning: Story hasn't started, need to initiate dev workflow.

2. **State: `in-progress`**
   - Command: `/bmad-bmm-workflows-dev-story` (continuing)
   - Alternative: `/bmad-bmm-workflows-code-review` if tasks are nearing completion.

3. **State: `review`**
   - Command: `/bmad-bmm-workflows-code-review`
   - Reasoning: Story is in review, needs adversarial review workflow.

4. **State: `done`**
   - Command: `/bmad-bmm-workflows-create-story [next_story_id]`
   - Reasoning: Current work finished, move to next story in backlog.

### Reference Documents
- [Epics: Story 4.1](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/epics.md#story-41-three-layer-action-card--one-click-command-copy)
- [Architecture: Frontend Architecture](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/architecture.md#frontend-architecture)
- [UX Design: Effortless Interactions](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/ux-design-specification.md#effortless-interactions)
