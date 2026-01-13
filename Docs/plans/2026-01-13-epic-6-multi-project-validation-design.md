# Epic 6: Multi-Project Validation & Robustness - Design Document

**Date:** 2026-01-13
**Author:** Gary (Project Lead) + Design Collaboration
**Status:** Approved for Implementation
**Epic ID:** epic-6

---

## Table of Contents

1. [Epic 6 Overview & Rationale](#section-1-epic-6-overview--rationale)
2. [Story 6.1 Structure & Approach](#section-2-story-61-structure--approach)
3. [Evidence-Based Acceptance Criteria](#section-3-evidence-based-acceptance-criteria)
4. [Anticipated Fix Categories & Risk Areas](#section-4-anticipated-fix-categories--risk-areas)
5. [Deliverables & Prerequisites](#section-5-deliverables--prerequisites)
6. [Contingency Planning - Stories 6.2+ Triggers](#section-6-contingency-planning---stories-62-triggers)
7. [Epic 6 Integration with Existing Documentation](#section-7-epic-6-integration-with-existing-documentation)

---

## Section 1: Epic 6 Overview & Rationale

### Epic 6: Multi-Project Validation & Robustness

**User Outcome:** BMAD Dash works reliably across different BMAD projects with varied structures, file naming conventions, and project states. Users can confidently use the dashboard on any BMAD Method project.

### Strategic Context

Epic 5 delivered a feature-complete dashboard, but it's only been tested on one project: BMAD Dash itself. This creates unknown risks—hardcoded assumptions, parsing brittleness, or cache behavior that only works for BMAD Dash's specific structure. Before recommending the dashboard for production use on other projects, we must validate it works on a real, different BMAD project.

### Why Echo-OS is the Perfect Test

Echo-OS is Gary's lost BMAD project at F:/Echo-OS. It's ideal for validation because:

1. **Real-world complexity:** Not a toy project, actual work Gary needs to recover
2. **Different structure:** Different epic/story naming, different phase, different size
3. **Unknown state:** Gary got lost, meaning the project may have gaps, incomplete workflows, or unusual states
4. **Dual value:** Validates dashboard robustness AND helps Gary recover his project

### Epic Scope

Story 6.1 is the primary delivery vehicle—a comprehensive validation + fix cycle on Echo-OS. Stories 6.2+ exist as contingency if Story 6.1 uncovers architectural issues that can't be fixed in a single story (e.g., parser requires fundamental redesign).

---

## Section 2: Story 6.1 Structure & Approach

### Story 6.1: Echo-OS Multi-Project Validation & Robustness Hardening

**Story Goal:**

Run BMAD Dash on Echo-OS project and achieve 100% feature parity with BMAD Dash baseline. Fix all parser, cache, AI context, and error handling issues discovered during validation. Produce Multi-Project Compatibility Matrix as reusable validation artifact.

### Three-Phase Approach

#### Phase 1: Baseline Validation (Find the Breaks)

- Point BMAD Dash at F:/Echo-OS
- Document every failure: parser errors, missing data, incorrect phase detection, cache issues
- Create initial Multi-Project Compatibility Matrix comparing BMAD Dash vs Echo-OS behavior
- Use Parser Audit Report's 7 assumptions as validation checklist
- Use Baseline Documentation to verify feature parity

#### Phase 2: Systematic Fixes (Full-Stack Robustness)

- **Parser Layer:** Handle story ID format variations (5-1 vs 5.1), flexible file naming, YAML structure tolerance
- **Cache Layer:** Ensure cache invalidation works across different project sizes and structures
- **API Layer:** Improve error messages, graceful degradation when artifacts malformed
- **Frontend Layer:** Handle missing/partial data without breaking UI
- **AI Context Layer:** Ensure AI coach receives correct project state for varied structures

#### Phase 3: Validation & Artifacts (Prove It Works)

- Re-run Echo-OS through dashboard—all baseline features must work
- Complete Multi-Project Compatibility Matrix showing 100% feature parity
- Document all assumptions fixed (update Parser Audit Report with "Validated on Echo-OS")
- Zero critical errors (warnings acceptable if gracefully handled)

---

## Section 3: Evidence-Based Acceptance Criteria

### Story 6.1 is "DONE" when the following evidence exists:

#### Evidence 1: Echo-OS Dashboard Loads Successfully

- Navigate to `localhost:5000?project_root=F:/Echo-OS`
- Dashboard renders without critical errors (500/404 responses)
- Breadcrumb navigation displays: Project → Phase → Epic → Story → Task
- Quick Glance Bar shows: Done | Current | Next stories
- Kanban board displays stories organized by status
- Page load time <500ms (meets NFR1 baseline)
- Screenshots of working dashboard included in story completion evidence

#### Evidence 2: All Baseline Features Work on Echo-OS

- **Navigation:** Breadcrumbs accurate, view mode switching works (Dashboard/Timeline/List)
- **Validation:** Git correlation finds commits, test discovery works, evidence badges display correctly
- **AI Coach:** Chat loads, streaming works, project-aware responses, suggested prompts appropriate
- **Actions:** Command copy works, workflow history displayed, gap detection functional
- **Manual refresh:** Re-parsing completes in <300ms
- Feature checklist from Baseline Documentation shows 100% pass rate

#### Evidence 3: Multi-Project Compatibility Matrix Created

- New artifact: `docs/validation/multi-project-compatibility-matrix.md`
- Matrix compares BMAD Dash vs Echo-OS across:
  - Parser behavior (story ID formats, file naming, YAML structures)
  - Phase detection accuracy
  - Git correlation accuracy
  - Test discovery success rate
  - Cache performance (load times, invalidation correctness)
  - AI context accuracy
  - Error handling (graceful degradation examples)
- Matrix shows 100% feature parity (all features work on both projects)
- Matrix includes "Validated Variations" section documenting what flexibility was added

#### Evidence 4: Zero Critical Parser Errors

- Parser handles Echo-OS artifact structure without crashes
- All 7 assumptions from Parser Audit Report tested and validated/fixed
- Error logs show zero `500` errors for Echo-OS parsing
- Warnings acceptable if non-blocking (e.g., "Story 3.2 has no tests found - showing Unknown status")
- Updated Parser Audit Report with "✅ Validated on Echo-OS" annotations

#### Evidence 5: Regression Prevention

- All 272 existing tests still pass (zero regressions on BMAD Dash project)
- BMAD Dash project still loads correctly at `localhost:5000?project_root=F:/BMAD Dash`
- New tests added for multi-project variations discovered during validation (estimated 5-10 new tests)

---

## Section 4: Anticipated Fix Categories & Risk Areas

### Based on Parser Audit Report and baseline analysis, Story 6.1 should be prepared to handle these fix categories:

#### High-Risk Area 1: Story ID Format Flexibility

- **Risk:** Parser expects `5-1` format, Echo-OS might use `5.1` or `story-5-1`
- **Fix:** Regex pattern matching supporting multiple formats: `5-1`, `5.1`, `5_1`, `story-5-1`
- **Location:** `backend/parsers/bmad_parser.py` story ID extraction logic
- **Validation:** Parser Audit Report assumption #1 marked resolved

#### High-Risk Area 2: File Naming Variations

- **Risk:** BMAD Dash uses `5-1-story-title.md`, Echo-OS might use `story-5.1-title.md` or `5.1-title.md`
- **Fix:** Flexible file discovery using multiple glob patterns, fallback to directory scanning
- **Location:** `backend/parsers/bmad_parser.py` file discovery methods
- **Validation:** Multi-Project Compatibility Matrix documents supported naming patterns

#### High-Risk Area 3: YAML Frontmatter Structure

- **Risk:** Different BMAD projects might have different frontmatter keys or nesting
- **Fix:** Defensive parsing with `get()` fallbacks, schema validation with helpful error messages
- **Location:** `backend/parsers/yaml_parser.py`
- **Validation:** Echo-OS artifacts parse without crashes, missing fields show "Unknown" gracefully

#### High-Risk Area 4: Phase Detection Accuracy

- **Risk:** Echo-OS might be in different phase, algorithm might misdetect due to artifact differences
- **Fix:** Strengthen phase detection with multiple heuristics, log confidence scores
- **Location:** `backend/services/phase_detector.py`
- **Validation:** Manual verification of Echo-OS phase vs. detected phase

#### High-Risk Area 5: Cache Invalidation Across Projects

- **Risk:** Cache might not properly isolate BMAD Dash vs Echo-OS data, leading to stale or mixed data
- **Fix:** Project-keyed cache with project_root in cache key
- **Location:** `backend/services/cache_service.py`
- **Validation:** Load both projects sequentially, verify no data leakage

#### High-Risk Area 6: AI Context Generation for Varied Structures

- **Risk:** AI system prompt assumes BMAD Dash structure, might provide wrong context for Echo-OS
- **Fix:** Dynamic context generation adapting to actual parsed project state
- **Location:** `backend/services/ai_service.py` system prompt builder
- **Validation:** Ask AI "What's my current story?" on Echo-OS, verify accuracy

---

## Section 5: Deliverables & Prerequisites

### Story 6.1 Deliverables

#### Deliverable 1: Multi-Project Compatibility Matrix

- **File:** `docs/validation/multi-project-compatibility-matrix.md`
- **Purpose:** Reusable validation checklist for future BMAD projects
- **Sections:**
  - Feature Comparison Table (BMAD Dash vs Echo-OS - all features, all passing)
  - Validated Variations (Story ID formats, file naming, YAML structures supported)
  - Known Limitations (if any remain after fixes)
  - Validation Procedure (how to validate new BMAD projects in future)
- **Value:** Turns Epic 6 into repeatable process for validating any BMAD project

#### Deliverable 2: Updated Parser Audit Report

- **File:** `docs/phase2/parser-audit-report.md` (updated)
- **Changes:** Each of 7 assumptions annotated with "✅ Validated on Echo-OS" or "✅ Fixed for multi-project support"
- **Purpose:** Closes the loop on prep work, documents what was learned

#### Deliverable 3: Robustness Test Suite

- **Files:** New tests in `backend/tests/` covering multi-project scenarios
- **Coverage:** Story ID format variations, file naming patterns, YAML structure flexibility, cache isolation
- **Purpose:** Prevent regressions when adding future features

#### Deliverable 4: Error Handling Documentation

- **File:** `docs/operations/error-handling-guide.md`
- **Content:** How dashboard gracefully degrades (missing artifacts, malformed YAML, Git unavailable, test discovery fails)
- **Purpose:** Users know what to expect when pointing dashboard at unusual projects

### Prerequisites Before Starting Story 6.1

#### Prerequisite 1: Echo-OS Project Access Verified

- Confirm F:/Echo-OS exists and is accessible
- Document Echo-OS current state: What phase? How many epics/stories? What's "lost" about it?
- Ensure Echo-OS is a Git repository (for Git correlation testing)

#### Prerequisite 2: Prep Work Documents Located

- Locate Parser Audit Report (completed)
- Locate Baseline Documentation (completed)
- Locate updated Definition of Done (completed)
- If these aren't in `docs/phase2/`, document actual locations for Story 6.1 developer

#### Prerequisite 3: BMAD Dash Baseline Snapshot

- Run full test suite on BMAD Dash: 272 tests passing
- Load BMAD Dash dashboard, take screenshots of all views (Dashboard/Timeline/List)
- Document current performance metrics (load time, parse time)
- Purpose: Regression baseline to ensure Echo-OS fixes don't break BMAD Dash

---

## Section 6: Contingency Planning - Stories 6.2+ Triggers

### Story 6.1 Goal: Complete Epic 6 in one story

However, Stories 6.2+ exist as contingency if Story 6.1 uncovers issues requiring additional work.

### What triggers Story 6.2+?

#### Trigger 1: Architectural Issues Discovered

- **Example:** Parser architecture fundamentally assumes single project structure, needs redesign for multi-project support
- **Why separate story:** Architectural changes require new design phase, can't be "fixed" in Story 6.1
- **Story 6.2 scope:** "Parser Architecture Redesign for Multi-Project Support"

#### Trigger 2: Performance Degradation on Echo-OS

- **Example:** Echo-OS is 10x larger than BMAD Dash, load time exceeds 2000ms (fails NFR1 by 4x)
- **Why separate story:** Performance optimization at scale requires profiling, algorithm changes, separate validation
- **Story 6.2 scope:** "Performance Optimization for Large BMAD Projects"

#### Trigger 3: Echo-OS Uses Incompatible BMAD Method Version

- **Example:** Echo-OS uses BMAD Method v2.0, BMAD Dash built for v1.0, artifact formats incompatible
- **Why separate story:** Multi-version support is separate feature, not a "fix"
- **Story 6.2 scope:** "BMAD Method Version Compatibility Layer"

#### Trigger 4: Critical Security or Data Integrity Issue

- **Example:** Cache isolation broken, Echo-OS data leaking into BMAD Dash cache, corruption risk
- **Why separate story:** Security issues require thorough audit, testing, documentation beyond validation scope
- **Story 6.2 scope:** "Multi-Project Cache Security Hardening"

### Non-Triggers (Handle in Story 6.1)

- Parser format flexibility (expected, core to Story 6.1)
- Error handling improvements (expected, core to Story 6.1)
- Cache performance tuning (expected, core to Story 6.1)
- AI context generation fixes (expected, core to Story 6.1)
- UI/UX polish for error states (expected, core to Story 6.1)

### Decision Point

At end of Story 6.1, review findings and determine:

- **Epic 6 Complete:** If all evidence criteria met, Echo-OS works with 100% feature parity
- **Story 6.2 Required:** If architectural/performance/security issue discovered that can't be resolved in Story 6.1 scope

---

## Section 7: Epic 6 Integration with Existing Documentation

### How Epic 6 Fits into BMAD Dash Project

#### Update to epics.md

Add Epic 6 after Epic 5 with this structure:

```markdown
### Epic 6: Multi-Project Validation & Robustness
**User Outcome:** BMAD Dash works reliably across different BMAD projects with varied structures, file naming conventions, and project states. Users can confidently use the dashboard on any BMAD Method project.

**What Users Can Accomplish:**
- Point BMAD Dash at any BMAD project (not just BMAD Dash itself)
- Trust that parser handles story ID format variations (5-1, 5.1, 5_1)
- See graceful error messages when artifacts are malformed or missing
- Validate multi-project compatibility using reusable compatibility matrix
- Benefit from cache isolation between different projects
- Receive accurate AI coach suggestions regardless of project structure

**FRs Covered:** Multi-project robustness (new requirement emerging from Epic 5 retrospective)
```

#### Story 6.1 Template

```markdown
### Story 6.1: Echo-OS Multi-Project Validation & Robustness Hardening

As a **BMAD Method user**,
I want **BMAD Dash to work reliably on any BMAD project, not just BMAD Dash itself**,
So that **I can use the dashboard to recover lost projects, monitor progress across multiple projects, and trust it works regardless of file naming or structure variations**.

**Acceptance Criteria:**

**Evidence 1: Echo-OS Dashboard Loads Successfully**
- Navigate to `localhost:5000?project_root=F:/Echo-OS` and dashboard renders without critical errors
- Breadcrumb navigation displays accurate hierarchy
- Quick Glance Bar shows Done | Current | Next stories
- Kanban board displays stories organized by status
- Page load time <500ms (meets baseline NFR1)
- Screenshots of working dashboard saved to story completion evidence

**Evidence 2: All Baseline Features Work on Echo-OS**
- Navigation: Breadcrumbs accurate, view mode switching functional (Dashboard/Timeline/List)
- Validation: Git correlation, test discovery, evidence badges all functional
- AI Coach: Chat loads, streaming works, project-aware responses accurate
- Actions: Command copy works, workflow history displayed, gap detection functional
- Manual refresh completes in <300ms
- Baseline Documentation feature checklist shows 100% pass rate for Echo-OS

**Evidence 3: Multi-Project Compatibility Matrix Delivered**
- File exists: `docs/validation/multi-project-compatibility-matrix.md`
- Matrix compares BMAD Dash vs Echo-OS: parser, phase detection, Git correlation, test discovery, cache, AI context, error handling
- Matrix shows 100% feature parity
- Matrix documents validated variations (story ID formats, file naming, YAML structures)

**Evidence 4: Zero Critical Parser Errors**
- Echo-OS parses without crashes or 500 errors
- All 7 Parser Audit Report assumptions validated/fixed
- Warnings acceptable if gracefully handled with "Unknown" states
- Updated Parser Audit Report includes "✅ Validated on Echo-OS" annotations

**Evidence 5: Regression Prevention**
- All 272 existing tests pass (BMAD Dash project still works)
- BMAD Dash dashboard still loads correctly at localhost:5000
- New multi-project tests added (5-10 tests minimum)
```

---

## Implementation Strategy

### Recommended Workflow for Story 6.1

1. **Prerequisites verification** (30 minutes)
   - Verify Echo-OS access
   - Locate prep work documents
   - Capture BMAD Dash baseline snapshot

2. **Phase 1: Baseline Validation** (2-3 hours)
   - Point dashboard at Echo-OS
   - Document all failures systematically
   - Create initial compatibility matrix

3. **Phase 2: Systematic Fixes** (4-6 hours)
   - Fix parser issues (story ID, file naming, YAML)
   - Fix cache isolation
   - Fix AI context generation
   - Improve error handling

4. **Phase 3: Validation & Artifacts** (2-3 hours)
   - Re-run Echo-OS validation
   - Complete compatibility matrix
   - Update parser audit report
   - Add robustness tests
   - Document error handling

5. **Code Review & Documentation** (1-2 hours)
   - Run `/bmad-bmm-workflows-code-review`
   - Ensure all deliverables complete
   - Verify regression tests pass

**Total Estimated Effort:** 10-17 hours (1-2 days)

---

## Success Metrics

### Epic 6 is successful when:

1. **Echo-OS dashboard works perfectly** (100% feature parity with BMAD Dash)
2. **Multi-Project Compatibility Matrix delivered** (reusable validation artifact)
3. **Zero regressions on BMAD Dash** (272 tests still passing)
4. **Parser robustness validated** (handles format variations gracefully)
5. **Gary can use dashboard to recover Echo-OS project** (real-world value delivered)

---

## Conclusion

Epic 6 transforms BMAD Dash from a "works on one project" tool to a "works on any BMAD project" tool. By validating on Echo-OS—a real, lost project with unknown structure—we gain confidence that the dashboard is robust enough for production use across all BMAD Method projects.

The evidence-based acceptance criteria ensure Story 6.1 is objectively complete. The contingency planning for Stories 6.2+ provides flexibility if architectural issues emerge. The deliverables (compatibility matrix, updated audit report, robustness tests, error handling guide) ensure Epic 6's learnings benefit future validation efforts.

**Ready for Implementation:** This design document is approved and Story 6.1 is ready to execute using `/bmad-bmm-workflows-dev-story`.

---

**Design Status:** ✅ APPROVED
**Next Step:** Execute Story 6.1 using dev-story workflow
**Document Version:** 1.0
**Last Updated:** 2026-01-13
