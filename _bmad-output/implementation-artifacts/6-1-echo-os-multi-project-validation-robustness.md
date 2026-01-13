---
story_id: "6.1"
title: Echo-OS Multi-Project Validation & Robustness Hardening
status: pending
epic: "epic-6"
priority: critical
tags: [parser, validation, robustness, multi-project, cache, ai-context]
workflow_history: []
---

# Story 6.1: Echo-OS Multi-Project Validation & Robustness Hardening

As a **BMAD Method user**,
I want **BMAD Dash to work reliably on any BMAD project, not just BMAD Dash itself**,
So that **I can use the dashboard to recover lost projects, monitor progress across multiple projects, and trust it works regardless of file naming or structure variations**.

## Acceptance Criteria

### Evidence 1: Echo-OS Dashboard Loads Successfully
- [ ] Navigate to `localhost:5000?project_root=F:/Echo-OS` and dashboard renders without critical errors
- [ ] Breadcrumb navigation displays accurate hierarchy
- [ ] Quick Glance Bar shows Done | Current | Next stories
- [ ] Kanban board displays stories organized by status
- [ ] Page load time <500ms (meets baseline NFR1)
- [ ] Screenshots of working dashboard saved to story completion evidence

### Evidence 2: All Baseline Features Work on Echo-OS
- [ ] Navigation: Breadcrumbs accurate, view mode switching functional (Dashboard/Timeline/List)
- [ ] Validation: Git correlation, test discovery, evidence badges all functional
- [ ] AI Coach: Chat loads, streaming works, project-aware responses accurate
- [ ] Actions: Command copy works, workflow history displayed, gap detection functional
- [ ] Manual refresh completes in <300ms
- [ ] Baseline Documentation feature checklist shows 100% pass rate for Echo-OS

### Evidence 3: Multi-Project Compatibility Matrix Delivered
- [ ] File exists: `docs/validation/multi-project-compatibility-matrix.md`
- [ ] Matrix compares BMAD Dash vs Echo-OS: parser, phase detection, Git correlation, test discovery, cache, AI context, error handling
- [ ] Matrix shows 100% feature parity
- [ ] Matrix documents validated variations (story ID formats, file naming, YAML structures)

### Evidence 4: Zero Critical Parser Errors
- [ ] Echo-OS parses without crashes or 500 errors
- [ ] All 7 Parser Audit Report assumptions validated/fixed
- [ ] Warnings acceptable if gracefully handled with "Unknown" states
- [ ] Updated Parser Audit Report includes "✅ Validated on Echo-OS" annotations

### Evidence 5: Regression Prevention
- [ ] All 272 existing tests pass (BMAD Dash project still works)
- [ ] BMAD Dash dashboard still loads correctly at localhost:5000
- [ ] New multi-project tests added (5-10 tests minimum)

## Implementation Tasks

### Phase 1: Baseline Validation (Find the Breaks)
- [ ] Verify Echo-OS project access at F:/Echo-OS
- [ ] Document Echo-OS current state (phase, epics, stories, what's "lost")
- [ ] Point BMAD Dash at Echo-OS and document all failures
- [ ] Create initial Multi-Project Compatibility Matrix
- [ ] Use Parser Audit Report's 7 assumptions as validation checklist
- [ ] Use Baseline Documentation to verify feature parity expectations

### Phase 2: Systematic Fixes (Full-Stack Robustness)

#### Parser Layer Fixes
- [ ] Handle story ID format variations (5-1, 5.1, 5_1, story-5-1)
- [ ] Implement flexible file naming discovery (multiple glob patterns)
- [ ] Add defensive YAML parsing with graceful fallbacks
- [ ] Improve phase detection with multiple heuristics
- [ ] Add parser unit tests for format variations

#### Cache Layer Fixes
- [ ] Implement project-keyed cache isolation (project_root in cache key)
- [ ] Verify cache invalidation works across different projects
- [ ] Test loading BMAD Dash and Echo-OS sequentially for data leakage
- [ ] Add cache isolation tests

#### API Layer Fixes
- [ ] Improve error messages for malformed artifacts
- [ ] Implement graceful degradation for missing/partial data
- [ ] Add helpful error context (file paths, expected formats)
- [ ] Test API error handling with Echo-OS edge cases

#### Frontend Layer Fixes
- [ ] Handle missing/partial data without breaking UI
- [ ] Display "Unknown" states gracefully
- [ ] Improve error messages shown to users
- [ ] Test UI with Echo-OS data variations

#### AI Context Layer Fixes
- [ ] Ensure system prompt adapts to actual parsed project state
- [ ] Test AI coach responses on Echo-OS for accuracy
- [ ] Verify suggested prompts appropriate for Echo-OS context
- [ ] Add AI context generation tests

### Phase 3: Validation & Artifacts (Prove It Works)
- [ ] Re-run Echo-OS through dashboard—all baseline features work
- [ ] Complete Multi-Project Compatibility Matrix with 100% feature parity
- [ ] Update Parser Audit Report with "✅ Validated on Echo-OS" annotations
- [ ] Create Error Handling Documentation (docs/operations/error-handling-guide.md)
- [ ] Run full BMAD Dash test suite (272 tests must pass)
- [ ] Verify BMAD Dash project still loads correctly
- [ ] Add robustness tests (5-10 new tests covering multi-project scenarios)
- [ ] Take screenshots of Echo-OS dashboard for evidence

## High-Risk Areas

### Risk Area 1: Story ID Format Flexibility
- **Location:** `backend/parsers/bmad_parser.py`
- **Fix:** Regex patterns supporting multiple formats
- **Validation:** Parser Audit Report assumption #1 resolved

### Risk Area 2: File Naming Variations
- **Location:** `backend/parsers/bmad_parser.py`
- **Fix:** Multiple glob patterns, directory scanning fallback
- **Validation:** Compatibility Matrix documents supported patterns

### Risk Area 3: YAML Frontmatter Structure
- **Location:** `backend/parsers/yaml_parser.py`
- **Fix:** Defensive parsing with get() fallbacks
- **Validation:** Echo-OS artifacts parse without crashes

### Risk Area 4: Phase Detection Accuracy
- **Location:** `backend/services/phase_detector.py`
- **Fix:** Strengthen with multiple heuristics, confidence scores
- **Validation:** Manual verification of detected phase

### Risk Area 5: Cache Isolation
- **Location:** `backend/services/cache_service.py`
- **Fix:** Project-keyed cache
- **Validation:** Sequential loading test for data leakage

### Risk Area 6: AI Context Generation
- **Location:** `backend/services/ai_service.py`
- **Fix:** Dynamic context generation
- **Validation:** AI accuracy test on Echo-OS

## Deliverables

1. **Multi-Project Compatibility Matrix** (`docs/validation/multi-project-compatibility-matrix.md`)
2. **Updated Parser Audit Report** (`docs/phase2/parser-audit-report.md`)
3. **Robustness Test Suite** (5-10 new tests in `backend/tests/`)
4. **Error Handling Documentation** (`docs/operations/error-handling-guide.md`)

## Prerequisites

- [ ] Echo-OS project exists at F:/Echo-OS and is accessible
- [ ] Echo-OS is a Git repository (for Git correlation testing)
- [ ] Parser Audit Report located
- [ ] Baseline Documentation located
- [ ] Definition of Done updated document located
- [ ] BMAD Dash baseline snapshot captured (272 tests passing, screenshots, performance metrics)

## Contingency Planning

**Stories 6.2+ triggered by:**
- Architectural issues requiring redesign (can't be fixed in Story 6.1)
- Performance degradation requiring optimization at scale
- BMAD Method version incompatibility
- Critical security/data integrity issues

**Non-triggers (handle in Story 6.1):**
- Parser format flexibility (expected)
- Error handling improvements (expected)
- Cache performance tuning (expected)
- AI context generation fixes (expected)

## Design Reference

See detailed design document: `docs/plans/2026-01-13-epic-6-multi-project-validation-design.md`

## Estimated Effort

**Total:** 10-17 hours (1-2 days)
- Phase 1 (Validation): 2-3 hours
- Phase 2 (Fixes): 4-6 hours
- Phase 3 (Artifacts): 2-3 hours
- Code Review: 1-2 hours

## Success Metrics

✅ Story complete when:
1. Echo-OS dashboard works perfectly (100% feature parity)
2. Multi-Project Compatibility Matrix delivered
3. Zero regressions on BMAD Dash (272 tests passing)
4. Parser robustness validated (handles format variations)
5. Gary can use dashboard to recover Echo-OS project
