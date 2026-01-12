---
story_id: "5.6"
title: "Automated BMAD Documentation Sync"
epic: "epic-5"
status: "todo"
created: "2026-01-12"
priority: "medium"
dependencies: ["5.5"]
tags: ["documentation", "automation", "github-api"]
---

# Story 5.6: Automated BMAD Documentation Sync

## User Story
**As a** user who wants the latest BMAD intelligence,
**I want** the system to check the official BMAD GitHub repository daily for documentation updates,
**So that** my AI Coach is always referencing the most current best practices and methods.

## Problem Statement
*   BMAD is an evolving method.
*   The project's local documentation (used by the AI Coach) becomes stale over time.
*   The user currently has to manually check for updates.

## Solution
1.  **Daily Check:** On dashboard startup, check `last_update_check` timestamp. If > 24h, query GitHub API.
2.  **Repo Comparison:** Compare local BMAD doc versions/hashes with `google-deepmind/bmad` (or specified repo).
3.  **Notification:** If updates found, alert the user via the Dashboard or AI Chat.
4.  **Auto-Update (Optional/Prompted):** Allow user to "One-Click Update" to pull latest docs into `_bmad/` folder (carefully avoiding project-specific overrides).

## Acceptance Criteria
*   [ ] System checks GitHub for updates at most once every 24 hours.
*   [ ] User is notified if local BMAD version lags behind remote.
*   [ ] AI Coach context includes "BMAD Version: X.Y.Z (Latest)" or "(Outdated)".
*   [ ] "Update Docs" button available if outdated.

## Dev Notes
*   Use `requests` or `GitPython` to check remote refs.
*   Ensure we respect GitHub API rate limits.
*   Store `last_checked` in `project-state.json`.
