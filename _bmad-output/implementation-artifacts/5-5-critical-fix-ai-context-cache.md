---
story_id: "5.5"
title: "Critical Fix - AI Context Injection & Dashboard Caching"
epic: "epic-5"
status: "done"
completed: "2026-01-12"
created: "2026-01-12"
priority: "critical"
dependencies: ["5.4"]
tags: ["bugfix", "performance", "ai-context", "caching"]
---

# Story 5.5: Critical Fix - AI Context Injection & Dashboard Caching

## User Story
**As a** user experiencing a slow, "lobotomized" dashboard,
**I want** the AI to actually know my project state and the dashboard to load instantly (single request),
**So that** the tool works as promised in Epics 1-5.

## Problem Statement
1.  **AI Lobotomy:** The AI Coach fails to answer basic questions about project state (e.g., "Status of Story 3.2?"). It asks the user to provide context, proving the system prompt injection is broken.
2.  **Performance N+1 Disaster:** The dashboard is ignoring the `project-state.json` cache and firing individual `/api/git-evidence` and `/api/test-evidence` calls for every single story card, resulting in 2.6s+ latency and massive log spam.

## Solution

### 1. Fix Dashboard Data Loading (Frontend)
*   **Current Behavior:** `dashboard.js` renders cards, then each card's `evidence-badge.js` triggers its own async fetch.
*   **Required Behavior:**
    1.  `app.js` fetches `/api/dashboard` (which includes the full `project-state` payload).
    2.  `dashboard.js` passes this complete data down to `story-card.js`.
    3.  `story-card.js` passes the specific story's evidence data (already in memory) to `evidence-badge.js`.
    4.  **ZERO** additional network requests during rendering.

### 2. Fix AI Context Injection (Backend)
*   **Current Behavior:** `ai_chat.py` is likely failing to load the json, or failing to stringify it, or the prompt template is truncating it.
*   **Required Behavior:**
    1.  Load `project-state.json`.
    2.  Inject a concise summary (Project Phase, Current Epic, List of Story Statuses) into the System Instruction.
    3.  Ensure Gemini actually sees it.

## Acceptance Criteria

### AC1: Single-Request Dashboard Load
**Given** a project with 20 stories
**When** the dashboard loads
**Then** there is exactly **ONE** API call to `/api/dashboard`
**And** there are **ZERO** calls to `/api/git-evidence/*` or `/api/test-evidence/*`
**And** all evidence badges still display correct data (green/red/yellow)

### AC2: Functioning AI Memory
**Given** the dashboard is loaded
**When** I ask "What is the status of Story 3.2?"
**Then** the AI answers correctly ("Story 3.2 is [Status]...") without asking for context

### AC3: Performance Target
**Given** a warm cache
**When** I refresh the dashboard
**Then** the `GET /api/dashboard` call completes in <300ms
**And** total time-to-interactive is <500ms

## Implementation Tasks

### Frontend Refactoring
- [x] **Modify `frontend/js/app.js`**: Ensure `fetchDashboardData` returns the fully populated `project-state` structure.
- [x] **Modify `frontend/js/views/dashboard.js`**: Stop independent fetching. Pass `story.evidence` data directly to children.
- [x] **Modify `frontend/js/components/evidence-badge.js`**: Remove the `fetchEvidence` logic. Accept `evidenceData` as a prop.

### Backend Debugging
- [x] **Debug `backend/services/ai_coach.py`**: Verify `_build_system_prompt` content. Add logging to print the exact system prompt size and content.
- [x] **Optimize Context**: If `project-state.json` is huge, implement a `summarize_for_ai()` method in `ProjectStateCache` that strips unnecessary details (like full task lists for old completed stories) to ensure it fits/is focused.

## Verification Evidence (Required)
1.  **Network Tab Screenshot:** Showing only 1 API call on load.
2.  **AI Chat Screenshot:** Showing correct answer to "Status of Story 3.2?".

## Dev Notes
*   **Do not overcomplicate.** We already have the data in `project-state.json`. We just need to **plumb it** correctly to the UI and the AI.
*   **Critical Path:** Fix the frontend N+1 issue first. That is a performance killer.
