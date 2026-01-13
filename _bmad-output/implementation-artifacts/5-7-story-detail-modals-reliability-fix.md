---
story_id: "5.7"
title: Story Detail Modals & Reliability Fix
status: done
epic: "epic-5"
priority: high
tags: [frontend, backend, reliability]
completed: "2026-01-12"
---

# Story 5.7: Story Detail Modals & Reliability Fix

As a **user**,
I want **to see the full content of any story in a rich modal and have evidence update instantly**,
So that **I can trust the data without waiting for network requests or looking at raw files**.

## Acceptance Criteria

### AC1: Instant Evidence Modals
- [x] Evidence badges (GIT/TEST) open modals instantly using pre-fetched data.
- [x] No redundant network requests when clicking badges.
- [x] Full commit history and test details are displayed correctly.

### AC2: Story Detail Modal
- [x] Clicking a story title opens a rich detail modal.
- [x] Modal renders full story content from the `.md` file using markdown.
- [x] Modal includes a task checklist for implementation tracking.
- [x] The UI matches the BMAD dark theme and VSCode aesthetic.

### AC3: Documentation Sync reliability
- [x] `BMADSyncService` uses ETags to comply with GitHub API rate limits.
- [x] Synchronization actually downloads and extracts the latest BMAD Method files.
- [x] Error handling is standardized using the `@handle_api_errors` decorator.

### AC4: Regression Fixes
- [x] Fixed `ImportError` in `bmad_sync.py` from over-zealous refactoring.
- [x] Fixed placebo update issue where status didn't reflect actual file changes.

## Implementation Tasks

### Frontend
- [x] Update `dashboard.js` with story click handlers.
- [x] Create `story-modal.js` component.
- [x] Integrate `marked.js` for markdown rendering.
- [x] Update `evidence-modal.js` and `evidence-badge.js` for instant loading.

### Backend
- [x] Implement `/api/dashboard/story/<story_id>` endpoint.
- [x] Update `ProjectStateCache` to include rich evidence in story objects.
- [x] Refactor `BMADSyncService` for ETag support and ZIP sync.
- [x] Standardize error handling in `bmad_sync.py`.

## Verification Results

### Evidence Based Progress Inference
- [x] Verified that commit lists are correctly populated for Story 5.6 and 5.7.
- [x] Verified that task lists are rendered correctly in the Story Modal.

### UI/UX Performance
- [x] First token latency < 200ms (via backend improvements).
- [x] Modal open time < 50ms (via pre-fetched data).
