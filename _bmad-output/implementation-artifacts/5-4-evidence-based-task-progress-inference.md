---
id: '5.4'
title: 'Evidence-Based Task Progress Inference'
epic: 'Epic 5: AI Coach Integration'
status: 'backlog'
created: '2026-01-11'
updated: '2026-01-11'
assignee: 'dev-agent'
priority: 'medium'
estimatedHours: 12
actualHours: 0
dependencies: ['5.2']
tags: ['ai-coach', 'automation', 'progress-tracking', 'git']
---

# Story 5.4: Evidence-Based Task Progress Inference

## User Story
**As a** developer using BMAD Dash  
**I want** the dashboard to automatically infer task completion from evidence (git commits, file changes, tests)  
**So that** I don't have to manually update task checkboxes and the AI Coach always knows my actual progress

## Problem Statement
Currently, task completion status only updates when someone manually edits the story file's checkboxes. This creates:
- **Friction**: Developers must stop to update checkboxes
- **Staleness**: AI Coach sees outdated progress (e.g., "0/8 tasks" when 6 are done)
- **Cognitive load**: Must remember what's done vs. what's checked

## Solution
BMAD Dash acts as an **observer** that infers progress from evidence:
- Git commits referencing tasks/stories
- File existence matching task deliverables
- Test results showing coverage
- Code review workflow completion

This keeps BMAD Dash **external** to the BMAD Method - no custom agents needed.

## Acceptance Criteria

### AC1: File-Based Progress Detection
**Given** a story has tasks with expected deliverables (e.g., "Create suggested-prompts.js")  
**When** the dashboard parses the project  
**Then** it detects if the expected file exists  
**And** infers task as "likely done" if file exists with recent changes

### AC2: Git Commit Correlation
**Given** git commits exist for the current story's timeframe  
**When** AI Coach builds context  
**Then** it includes recent commit messages relevant to the story  
**And** can answer "What work has been committed for this story?"

### AC3: Dual Progress Display
**Given** a story with inferred progress different from checkbox status  
**When** the dashboard displays progress  
**Then** shows both: "Official: 0/8 tasks | Evidence: 6/8 likely complete"  
**And** highlights the discrepancy for user awareness

### AC4: AI Coach Reports Inferred Progress
**Given** AI Coach is asked "What tasks remain?"  
**When** generating response  
**Then** uses inferred status (not just checkboxes)  
**And** explains: "Based on file changes and commits, Task 1-3 appear complete"

### AC5: Task-to-Deliverable Mapping
**Given** story tasks describe expected outputs  
**When** parser analyzes tasks  
**Then** extracts expected file paths/patterns from task descriptions  
**And** maps tasks to their deliverables for verification

### AC6: Test Coverage Correlation
**Given** story has associated test files  
**When** tests have been run  
**Then** infers "Task 7: Write Tests" as in-progress/done based on test file existence and results

## Tasks

### Task 1: Design Task-Deliverable Mapping
- [ ] Analyze task description patterns to extract expected files
- [ ] Create mapping rules (e.g., "Create X.js" → expect file X.js)
- [ ] Handle common patterns: "Create", "Add", "Implement", "Write tests for"
- [ ] Store mappings in parsed story data

### Task 2: Implement File Evidence Collector
- [ ] Create `evidence_collector.py` service
- [ ] Check file existence for mapped deliverables
- [ ] Get file modification times
- [ ] Compare to story start date
- [ ] Calculate confidence score per task

### Task 3: Add Git Commit Correlation
- [ ] Parse git log for commits since story started
- [ ] Filter commits by story ID mentions or file patterns
- [ ] Extract commit messages for AI context
- [ ] Map commits to likely tasks

### Task 4: Update Dashboard API with Inferred Progress
- [ ] Add `inferred_progress` field to story data
- [ ] Include evidence summary per task
- [ ] Return both official and inferred task counts
- [ ] Add `evidence` array to task objects

### Task 5: Update AI Coach Context with Evidence
- [ ] Include inferred progress in system prompt
- [ ] Add recent commit messages to context
- [ ] Update "what tasks remain" logic to use evidence
- [ ] Format evidence clearly in AI responses

### Task 6: Update Dashboard UI for Dual Progress
- [ ] Display inferred progress alongside official
- [ ] Add visual indicator when they differ
- [ ] Show "evidence suggests..." tooltip on hover
- [ ] Keep design minimal and unobtrusive

### Task 7: Write Tests
- [ ] Unit tests for task-deliverable mapping
- [ ] Unit tests for evidence collection
- [ ] Integration test for git correlation
- [ ] Test accuracy on real story files

## Technical Notes

### Evidence Signals (Priority Order)
1. **File Exists** + recent mtime → High confidence task started/done
2. **Git Commit** mentions task → Medium-high confidence
3. **Test File** exists → Medium confidence for test tasks
4. **Code Review ran** → High confidence story is review-ready

### Handling Uncertainty
- Use confidence levels: "likely done", "possibly done", "no evidence"
- Never auto-update checkboxes (user controls official status)
- AI explains its reasoning: "I see suggested-prompts.js was created 2 hours ago..."

### Performance Considerations
- Cache evidence collection (invalidate on file changes)
- Limit git log to last 50 commits
- Only collect evidence for current story (not all stories)

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Evidence collection working for file + git signals
- [ ] AI Coach uses inferred progress in responses
- [ ] Dashboard shows dual progress when relevant
- [ ] Tests written and passing
- [ ] Works without modifying BMAD Method/agents

## Test Evidence
<!-- Evidence will be added during implementation -->

## Git Commits
<!-- Commits will be tracked here -->

## Review Notes
<!-- Code review feedback will be added here -->
