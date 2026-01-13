# BMAD Dash: Error Handling & Graceful Degradation Guide

**Version:** 1.0  
**Date:** 2026-01-13  
**Scope:** Developer guide for understanding how BMAD Dash handles missing or malformed data

## Overview

BMAD Dash is designed to be resilient against incomplete or malformed BMAD Method artifacts. This guide documents how the system degrades gracefully when encountering various project states.

---

## 1. Parser Layer Robustness

### Missing `_bmad-output` Directory
- **Logic:** `BMADParser` checks for standard directories.
- **Behavior:** If missing, returns a `Project` object with an empty list of epics.
- **UI Impact:** Dashboard loads successfully but shows "No stories found" and an empty Kanban board.
- **Suggested Action:** AI Coach will suggest creating the first story.

### Malformed `sprint-status.yaml`
- **Logic:** `YAMLParser` uses defensive parsing with fallback to empty dicts.
- **Behavior:** Logs an error and returns an empty project structure.
- **UI Impact:** Dashboard loads, shows project name from directory, but empty board.

### Unsupported Story ID Format
- **Logic:** Regex matching in `bmad_parser.py`.
- **Behavior:** If a key in `development_status` doesn't match the expected `epic-story-name` pattern, it is ignored by the parser.
- **Robustness:** Handles hyphenated (`5-1`) and decimal (`5.1`) formats via ProjectState translation.

---

## 2. API & Data Layer Robustness

### Project Not Found
- **Logic:** `/api/dashboard` validates `project_root` parameter.
- **Behavior:** Returns `404 Not Found` with a specific error message.
- **UI Impact:** Error toast message "Project not found" shown to user.

### Missing Story Markdown Files
- **Logic:** `BMADParser` searches for `{story_key}-*.md`.
- **Behavior:** If not found, the story exists in the Kanban board but has no "Content" available in the detail modal.
- **UI Impact:** Modal shows "Error reading story file" or empty content.

### Git Unavailable
- **Logic:** `GitCorrelator` wraps git commands in try-except blocks.
- **Behavior:** Returns empty commit lists if git is not installed or the project is not a repository.
- **UI Impact:** Evidence badges show "0 Commits".

---

## 3. Frontend Layer Robustness

### Unknown Project State
- **Logic:** Breadcrumb and Quick Glance use fallbacks.
- **Behavior:** Shows "Unknown" or "Implementation" as default phase.
- **UI Impact:** UI remains functional; breadcrumb reflects current knowledge.

### Partial Dashboard Data
- **Logic:** Component renderers use optional chaining (`?.`) and default values.
- **Behavior:** Missing fields (e.g., missing tasks, missing epic title) render as empty strings or placeholders.
- **UI Impact:** Layout preserves integrity; missing data doesn't "break" the page.

---

## 4. Cache Isolation & Recovery

### Cache Invalidation
- **Logic:** Manual refresh button calls `/api/cache/clear`.
- **Behavior:** Deletes `project-state.json` and SmartCache directories.
- **Recovery:** Next load triggers a full bootstrap from the file system.

### Multi-Project Isolation
- **Logic:** Caches are keyed by `project_root` in the backend.
- **Robustness:** Validated by `test_multi_project_support.py` ensuring zero data leakage between sequential project loads.

---

## Troubleshooting Guide for Users

1. **Dashboard is Empty:** Check if `_bmad-output/implementation-artifacts/sprint-status.yaml` exists and is correctly formatted.
2. **Stories Missing from Kanban:** Ensure story IDs in `sprint-status.yaml` match the expected pattern.
3. **Evidence Badges Show 0:** Verify the project is a Git repository and `pytest` is configured appropriately.
4. **Incorrect Progress Bar:** Ensure tasks in story markdown files use the standard GitHub checkbox format `- [x]`.

---

**Contact:** For technical issues regarding parser robustness, refer to `backend/parsers/bmad_parser.py`.
