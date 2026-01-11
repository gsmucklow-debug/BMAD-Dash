---
id: '5.4'
title: 'Evidence-Based Task Progress Inference'
epic: 'Epic 5: AI Coach Integration'
status: 'backlog'
created: '2026-01-11'
updated: '2026-01-11'
assignee: 'dev-agent'
priority: 'high'
estimatedHours: 16
actualHours: 0
dependencies: ['5.2']
tags: ['ai-coach', 'automation', 'progress-tracking', 'git', 'caching']
---

# Story 5.4: Evidence-Based Task Progress Inference

## User Story
**As a** developer using BMAD Dash  
**I want** the dashboard to maintain a running project state document that tracks all epics, stories, tasks, and evidence  
**So that** the AI Coach has complete project awareness and dashboard refreshes are instant

## Problem Statement
Currently:
- **Every refresh re-parses everything**: Story files, git logs, test results - slow and wasteful
- **AI has limited context**: Only knows current story, not project history
- **Task status is stale**: Checkboxes don't reflect actual work done
- **No persistence**: Evidence collected is thrown away after each request

## Solution: `project-state.json` - The Running Document

A single JSON file that serves as **the source of truth** for:
1. **All project state** - epics, stories, tasks, statuses
2. **Cached evidence** - commits, test results, review status per story
3. **AI context** - everything the AI needs to know in one file
4. **Fast updates** - only refresh what changed, persist the rest

### File Location
```
_bmad-output/implementation-artifacts/project-state.json
```

### Structure
```json
{
  "project": {
    "name": "BMAD Dash",
    "phase": "Implementation",
    "bmad_version": "latest",
    "last_updated": "2026-01-11T13:16:52Z"
  },
  "current": {
    "epic_id": "epic-5",
    "epic_title": "AI Coach Integration",
    "story_id": "5.3",
    "story_title": "AI Agent Output Validation Workflow Gap Warnings",
    "story_status": "backlog",
    "task_id": null,
    "task_title": null,
    "next_action": "/bmad-bmm-workflows-dev-story 5.3"
  },
  "epics": {
    "epic-5": {
      "id": "epic-5",
      "title": "AI Coach Integration",
      "status": "in-progress",
      "stories_done": 2,
      "stories_total": 4,
      "stories": ["5.1", "5.2", "5.3", "5.4"]
    }
  },
  "stories": {
    "5.2": {
      "id": "5.2",
      "title": "Project-Aware Q&A & Suggested Prompts",
      "epic": "epic-5",
      "status": "done",
      "purpose": "AI suggestions based on current project state with ready-to-click prompts",
      "evidence": {
        "commits": 3,
        "tests_passed": 16,
        "tests_total": 16,
        "reviewed": true,
        "healthy": true,
        "last_commit": "2026-01-11T12:56:00Z"
      },
      "tasks": {
        "done": 8,
        "total": 8,
        "items": [
          {"id": 1, "title": "Design Suggested Prompts Component", "status": "done", "inferred": true},
          {"id": 2, "title": "Implement Context-Aware Prompt Generation", "status": "done", "inferred": true}
        ]
      },
      "last_updated": "2026-01-11T13:00:00Z"
    },
    "5.3": {
      "id": "5.3",
      "title": "AI Agent Output Validation Workflow Gap Warnings",
      "epic": "epic-5",
      "status": "backlog",
      "purpose": "Validate AI agent outputs and detect workflow gaps",
      "evidence": {
        "commits": 0,
        "tests_passed": 0,
        "tests_total": 0,
        "reviewed": false,
        "healthy": false
      },
      "tasks": {
        "done": 0,
        "total": 5,
        "items": []
      }
    }
  }
}
```

## Acceptance Criteria

### AC1: Project State File Creation & Updates
**Given** dashboard loads for the first time  
**When** no `project-state.json` exists  
**Then** it creates one by scanning all stories, epics, and evidence  
**And** saves the complete project state to disk

### AC2: Incremental Updates on Refresh
**Given** user clicks "Refresh"  
**When** dashboard reloads  
**Then** it reads `project-state.json` first (instant)  
**Then** checks file mtimes for stories that changed  
**And** only re-parses and updates those stories  
**And** saves back to `project-state.json`

### AC3: AI Coach Complete Context
**Given** AI Chat receives a message  
**When** building system prompt  
**Then** includes entire `project-state.json` as context  
**And** AI knows all epics, all stories, all task progress, all evidence  
**And** can answer "What's the status of Story 3.3?" without parsing files

### AC4: Task Inference from Evidence
**Given** git commit message says "feat(5.3): Task 2 complete"  
**When** evidence collector runs  
**Then** updates `stories["5.3"].tasks.items[1].status = "done"`  
**And** sets `inferred: true` to indicate auto-detected  
**And** persists to `project-state.json`

### AC5: Dual Progress Display
**Given** story has official checkboxes showing 2/8 tasks  
**But** evidence suggests 6/8 tasks are done  
**When** dashboard displays progress  
**Then** shows: "Progress: 6/8 tasks (2 official, 4 inferred)"  
**And** explains discrepancy on hover

### AC6: Performance Target
**Given** project has 20+ stories  
**When** dashboard loads with warm cache  
**Then** loads in <100ms (reading single JSON file)  
**When** refresh with 1 changed story  
**Then** completes in <300ms (only re-parses 1 story + git check)

## Tasks

### Task 1: Design `project-state.json` Schema
- [ ] Finalize JSON schema (as shown above)
- [ ] Define version field for future migrations
- [ ] Add validation for required fields
- [ ] Document schema in README

### Task 2: Create ProjectStateCache Service
- [ ] Create `backend/services/project_state_cache.py`
- [ ] Implement `load()` - read and parse JSON
- [ ] Implement `save()` - write JSON with pretty print
- [ ] Implement `get_story(id)` - quick lookup
- [ ] Implement `update_story(id, data)` - merge updates
- [ ] Handle missing file (create from scratch)

### Task 3: Bootstrap from Existing Data
- [ ] Create `bootstrap_project_state()` function
- [ ] Scan all story files in `_bmad-output/implementation-artifacts/`
- [ ] Parse epics.md for epic structure
- [ ] Populate initial state from current data
- [ ] Call git/test evidence collectors for each story

### Task 4: Integrate with Dashboard API
- [ ] Modify `/api/dashboard` to use ProjectStateCache
- [ ] Load from cache first, then validate
- [ ] Only re-parse stories with changed mtimes
- [ ] Update cache and save on changes
- [ ] Add `cache_age_ms` to response for debugging

### Task 5: Integrate with AI Coach
- [ ] Load `project-state.json` in AICoach constructor
- [ ] Include full project state in system prompt
- [ ] Add "Project Summary" section with epic/story counts
- [ ] AI can now answer questions about ANY story

### Task 6: Implement Task Inference
- [ ] Parse task descriptions for expected deliverables
- [ ] Check file existence for deliverables
- [ ] Parse git commits for task references
- [ ] Update task status with `inferred: true` flag
- [ ] Save inferred status to project-state.json

### Task 7: Update Dashboard UI
- [ ] Display inferred progress in story cards
- [ ] Add visual indicator for inferred vs official
- [ ] Show evidence summary tooltip on hover
- [ ] Update Quick Glance with inferred progress

### Task 8: Write Tests
- [ ] Unit tests for ProjectStateCache
- [ ] Unit tests for task inference
- [ ] Integration test for bootstrap
- [ ] Performance test for cache load time

## Technical Notes

### Why JSON over YAML?
- **Parse speed**: 5-10x faster than YAML
- **Programmatic updates**: Easy to modify specific fields
- **AI-friendly**: Perfect for system prompts
- **Standard**: Every language has native JSON support

### Cache Invalidation Strategy
```
1. On load: Check project-state.json mtime
2. For each story in cache: Check story file mtime
3. If story file newer than cache entry: Re-parse that story
4. If git repo has new commits: Re-run evidence collection
5. Save updated cache
```

### AI Context Size
- Full project-state.json: ~5-10KB typical
- Well within Gemini context window
- Can truncate completed story details if needed

### Migration Path
- `version` field in JSON for future schema changes
- Backward-compatible readers
- Auto-upgrade on load if needed

## Definition of Done
- [ ] `project-state.json` created and maintained automatically
- [ ] Dashboard loads from cache in <100ms
- [ ] Refresh updates only changed stories in <300ms
- [ ] AI Coach receives full project state
- [ ] Task inference working for file + git signals
- [ ] Tests written and passing
- [ ] Works without modifying BMAD Method/agents

## Test Evidence
<!-- Evidence will be added during implementation -->

## Git Commits
<!-- Commits will be tracked here -->

## Review Notes
<!-- Code review feedback will be added here -->

