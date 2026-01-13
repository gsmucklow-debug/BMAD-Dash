---
story_id: "5.6"
title: "Automated BMAD Documentation Sync"
epic: "epic-5"
status: "done"
priority: "medium"
dependencies: ["5.5"]
tags: ["documentation", "sync", "automation"]
completed: "2026-01-12"
---

# Story 5.6: Automated BMAD Documentation Sync

## Overview
This story implements an automated system to keep the local BMAD documentation in sync with the official GitHub repository. The AI Coach relies on BMAD documentation to provide accurate guidance, and this feature ensures users always have access to the latest best practices and methods.

## Acceptance Criteria

### AC1: Daily Update Check
- [x] System checks GitHub for documentation updates every 24 hours.
- [x] `last_check` timestamp is persisted to prevent redundant API calls.

### AC2: Update Notification
- [x] Dashboard displays a visual notification when a BMAD documentation update is available.
- [x] Notification includes the latest version/commit message.

### AC3: One-Click Update
- [x] User can trigger the documentation sync with a single click.
- [x] System merges updates into the local `_bmad/` folder while preserving local overrides.

### AC4: AI Coach Version Awareness
- [x] AI Coach can report the current BMAD documentation version.
- [x] AI Coach warns the user if documentation is significantly out of date.

## Implementation Tasks

### Backend - Sync Service
- [x] **Create `backend/services/bmad_sync.py`**: Implement GitHub API client and state management.
- [x] **Create `backend/api/bmad_sync.py`**: Implement status, check, and update endpoints.
- [x] **Update `backend/app.py`**: Register the `bmad_sync` blueprint.
- [x] **Update `backend/services/ai_coach.py`**: Inject BMAD version info into the system prompt.

### Frontend - Sync UI
- [x] **Create `frontend/js/components/bmad-sync.js`**: Create the update banner/status component.
- [x] **Modify `frontend/js/views/dashboard.js`**: Integrate the sync component into the main dashboard view.
- [x] **Modify `frontend/index.html`**: Add the sync container.

## Verification Evidence
1.  **Sync Status API**: Verify `/api/bmad-sync/status` returns correct versioning information.
2.  **Dashboard Check**: Verify the "Up to Date" or "Update Available" banner appears.
