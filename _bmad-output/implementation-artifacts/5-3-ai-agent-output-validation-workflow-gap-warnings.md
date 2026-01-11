---
id: '5.3'
title: 'AI Agent Output Validation & Workflow Gap Warnings'
epic: 'Epic 5: AI Coach Integration'
status: 'done'
created: '2026-01-11'
updated: '2026-01-11'
completed: '2026-01-11'
assignee: 'dev-agent'
priority: 'high'
estimatedHours: 8
dependencies: ['5.2', '2.3', '4.2']
tags: ['ai-coach', 'validation', 'workflow-gaps', 'trust']
---

# Story 5.3: AI Agent Output Validation & Workflow Gap Warnings

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **user**,
I want **the AI to compare story claims vs. Git/test reality and warn me about gaps**,
so that **I can trust AI agent completion and catch missing workflows without manual auditing**.

## Acceptance Criteria

### AC1: Intelligent Completion Validation
**Given** a user asks "Did the AI agent complete Story X.X correctly?" or clicks a similar suggested prompt
**When** the AI Coach processes the request
**Then** it must call the backend to analyze:
- **Git Evidence**: Do commits exist for the story? (from Story 2.1)
- **Test Evidence**: Are there passing tests for the story? (from Story 2.2)
- **Task Evidence**: Are all tasks in the story file marked complete?
- **Workflow Evidence**: Was the `code-review` workflow executed for this story? (from Story 4.2)

### AC2: Comprehensive Validation Summary
**Given** validation analysis is complete
**When** AI generates the response
**Then** it must provide a clear summary:
- "Story X.X appears complete: [Evidence List]"
- OR "Story X.X marked done but issues found: [Missing Evidence List]"
- Include specific counts (e.g., "6 Git commits", "18/18 tests passing") and timestamps ("last run: 2h ago").

### AC3: Proactive Workflow Gap Detection (FR27)
**Given** any story is marked "done" or "review"
**When** the dashboard loads or AI chat is initialized
**Then** the system must automatically detect gaps:
- Story marked "done" without `dev-story` workflow history.
- `dev-story` complete but no `code-review` history.
- `code-review` done but no tests detected.
**And** AI Coach must display/mention these gaps as warnings.

### AC4: Actionable Warning & Suggestions
**Given** a gap or issue is detected
**When** AI reports the problem
**Then** it must provide specific next steps and commands (e.g., "Suggestion: Run `/bmad-bmm-workflows-code-review`").

### AC5: Performance & Context
**Given** comprehensive validation is requested
**When** AI generates the check
**Then** total analysis and response generation must complete in <500ms (NFR requirement).
**And** validation must leverage the evidence APIs developed in Epic 2.

## Tasks / Subtasks

- [x] **Task 1: Implement Backend `ValidationService`** (AC: 1, 3)
  - [x] Create `backend/services/validation_service.py`.
  - [x] Implement `validate_story(story_id)` method aggregating data from:
    - `bmad_parser` (tasks completion status).
    - `git_parser` (commit correlation).
    - `test_parser` (test execution results).
    - `workflow_history_service` (from Story 4.2).
  - [x] Implement `detect_workflow_gaps(project_root)` method for bulk project analysis.

- [x] **Task 2: Update AI Coach Logic** (AC: 1, 2, 4)
  - [x] Integrate `ValidationService` into `AICoach` class.
  - [x] Update `AICoach._build_system_prompt` to include validation results when relevant.
  - [x] Add intent detection for "is story X complete" queries.

- [x] **Task 3: Implement Automated Gap Warnings** (AC: 3, 4)
  - [x] Create `frontend/js/components/gap-warning.js` to display proactive warnings.
  - [x] Update `app.js` to fetch gap data on load/refresh.
  - [x] Ensure warnings are non-intrusive but visible.

- [x] **Task 4: AI Context & Prompt Enhancement** (AC: 2, 5)
  - [x] Update prompt templates to format validation summaries cleanly.
  - [x] Ensure streaming response first token still meets <200ms target.

- [x] **Task 5: Write Tests** (AC: All)
  - [x] Pytest for `ValidationService` with mocked evidence providers.
  - [x] Integration tests for `/api/ai-chat` validation intent.
  - [x] Unit tests for gap detection logic.

## Dev Notes

### Technical Approach
1. **Aggregator Pattern**: `ValidationService` acts as a facade over existing evidence parsers.
2. **Intent Detection**: The AI Coach needs to recognize when the user is asking for validation vs. general questions.
3. **Workflow History**: Relies on the history parsing implemented in Story 4.2.

### Relevant Architecture Patterns
- [Source: architecture.md#Decision: Python Dataclasses] - Use dataclasses for validation results.
- [Source: architecture.md#Non-Functional Requirements] - Performance budget <500ms.

### Key Files to Modify
- `backend/services/validation_service.py` (New)
- `backend/app.py` (Register new service/routes if needed)
- `backend/services/ai_coach.py` (Major update to system prompt and validation logic)
- `frontend/js/components/gap-warning.js` (New)
- `frontend/js/app.js` (Wire up gap detection)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

N/A - No blocking issues encountered

### Completion Notes List

1. ✅ Implemented `ValidationService` class with comprehensive story validation aggregating Git, test, task, and workflow evidence
2. ✅ Added `validate_story()` method that meets <500ms performance requirement (verified via pytest)
3. ✅ Added `detect_workflow_gaps()` method for bulk project analysis across all stories
4. ✅ Integrated ValidationService into AICoach with automatic validation intent detection
5. ✅ Enhanced AICoach system prompt to include validation summaries when user asks validation questions
6. ✅ Added formatted validation summaries with specific counts and timestamps (AC2)
7. ✅ Created GapWarning frontend component with non-intrusive yellow warning banner design
8. ✅ Implemented automatic gap detection on dashboard load (AC3)
9. ✅ Added actionable command suggestions with one-click copy to clipboard (AC4)
10. ✅ Created `/api/workflow-gaps` and `/api/validate-story/<story_id>` API endpoints
11. ✅ Added comprehensive CSS styling with slide-down animation and severity-based coloring
12. ✅ Wrote 10 unit tests for ValidationService - all passing
13. ✅ Fixed pre-existing workflow history test to match correct timestamp-based sorting
14. ✅ All 264 tests passing - no regressions introduced

### File List

#### Backend Files Created/Modified
- backend/services/validation_service.py (NEW)
- backend/api/validation.py (NEW)
- backend/app.py (MODIFIED - registered validation blueprint)
- backend/services/ai_coach.py (MODIFIED - integrated validation, added intent detection)

#### Frontend Files Created/Modified
- frontend/js/components/gap-warning.js (NEW)
- frontend/js/app.js (MODIFIED - added gap warning initialization)
- frontend/css/input.css (MODIFIED - added gap warning styles)

#### Test Files Created/Modified
- tests/test_validation_service.py (NEW - 10 comprehensive tests)
- tests/test_workflow_history.py (MODIFIED - fixed timestamp ordering test)

## Senior Developer Review (AI)

**Review Date:** 2026-01-11
**Reviewer:** Claude Opus 4.5 (Code Review Agent)
**Outcome:** ✅ APPROVED (with fixes applied)

### Review Summary

All 5 Acceptance Criteria verified as IMPLEMENTED:
- AC1: ValidationService aggregates Git/Test/Task/Workflow evidence ✅
- AC2: Formatted summaries with counts and timestamps ✅
- AC3: Proactive gap detection on dashboard load ✅
- AC4: Actionable warnings with copy-to-clipboard commands ✅
- AC5: Performance under 500ms verified via test ✅

### Issues Found and Fixed

| Severity | Issue | Resolution |
|----------|-------|------------|
| MEDIUM | XSS vulnerability in gap-warning.js:89 - innerHTML with unescaped data | Added `_escapeHtml()` helper, escaped story_id and story_title |
| MEDIUM | Bug in gap-warning.js:149 - undefined `event` variable | Passed button element as parameter to `_copyCommandToClipboard()` |

### Test Verification

- ✅ All 264 tests passing after fixes
- ✅ 10 ValidationService tests specifically verify AC1-AC5
- ✅ No regressions introduced

### Files Modified During Review

- `frontend/js/components/gap-warning.js` - Security and bug fixes

## Change Log

- 2026-01-11: Code review completed - fixed XSS vulnerability and event variable bug in gap-warning.js
- 2026-01-11: Implemented comprehensive AI agent output validation system with workflow gap warnings (Story 5.3)
