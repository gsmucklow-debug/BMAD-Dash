---
story_id: "1.2"
story_key: "1-2-phase-detection-algorithm"
epic: 1
title: "Phase Detection Algorithm"
status: "done"
created: "2026-01-09"
completed: "2026-01-09"
context_engine_version: "v1.0"
---

# Story 1.2: Phase Detection Algorithm

## User Story

As a **developer using BMAD Dash**,  
I want **the system to automatically detect which phase my project is in (Analysis, Planning, Solutioning, Implementation)**,  
So that **I can instantly understand my project's current state without manual inspection**.

## Business Context

Phase detection is a core capability of BMAD Dash's "instant re-orientation" value proposition. Users (especially those with MS/brain fog) need to know "Where am I?" immediately upon opening the dashboard. The phase detection algorithm analyzes the presence of specific BMAD artifacts to determine the current workflow phase.

**Value:** Enables automatic breadcrumb navigation and contextual UI adaptation based on project phase.

## Acceptance Criteria

**Given** a BMAD project with artifacts in `_bmad-output/`  
**When** the phase detector analyzes the project structure  
**Then** it correctly identifies the phase as "Implementation" when `sprint-status.yaml` exists

**And** it identifies "Solutioning" phase when `architecture.md` exists but no sprint-status

**And** it identifies "Planning" phase when `prd.md` exists but no architecture

**And** it identifies "Analysis" phase when only brainstorming/product-brief files exist

**And** it returns "Unknown" for unrecognized or empty project structures

**And** detection completes in <100ms (NFR3 requirement)

**And** the algorithm checks multiple potential locations for each artifact

**And** no crashes occur for missing directories or files

---

## Implementation Summary

### ✅ Completed Implementation

**Note:** This story was implemented as part of Story 1.1 (BMAD Artifact Parser) since phase detection is intrinsically linked to artifact parsing.

**Implementation Location:** `backend/services/phase_detector.py`

### Core Methods Implemented

**1. `detect_phase(root_path: str) -> str`**
- Primary detection method
- Checks artifact presence in priority order
- Returns phase string: "Analysis" | "Planning" | "Solutioning" | "Implementation" | "Unknown"

**Detection Logic (Priority Order):**
```
1. Implementation → Check for sprint-status.yaml
2. Solutioning → Check for architecture.md
3. Planning → Check for prd.md
4. Analysis → Check for brainstorming.md or product-brief.md
5. Unknown → No recognizable artifacts
```

**2. `detect_phase_from_data(project_data: dict) -> str`**
- Alternative method for parsed data
- Used when project data is already loaded
- Same phase priority logic

### Artifact Search Locations

The algorithm checks **multiple locations** for flexibility:

**For sprint-status.yaml:**
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/sprint-status.yaml`
- `sprint-status.yaml` (project root)

**For architecture.md:**
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/architecture.md`
- `architecture.md` (project root)

**For prd.md:**
- `_bmad-output/planning-artifacts/prd.md`
- `_bmad-output/prd.md`
- `prd.md` (project root)

**For analysis files:**
- `brainstorming.md`, `product-brief.md`, `ideas.md`
- Checked in planning-artifacts, bmad-output, and root

### Test Coverage

**File:** `tests/test_phase_detector.py`  
**Tests:** 22 comprehensive tests

**Test Categories:**
1. **Basic Detection** - All 5 phases correctly identified
2. **Priority Testing** - Ensures correct phase when multiple artifacts exist
3. **Alternative Locations** - Validates multi-location search
4. **Error Handling** - Non-existent paths, empty paths, missing directories
5. **Performance** - Validates <100ms execution time
6. **Data-based Detection** - Alternative method validation

**Test Results:** 22/22 passing ✅

### Key Implementation Details

**Graceful Error Handling:**
```python
if not root_path or not os.path.exists(root_path):
    return "Unknown"
```

**Performance Optimization:**
- Simple `os.path.exists()` checks (no file reads)
- Short-circuit evaluation (stops at first match)
- No expensive operations
- Typical execution: <10ms

**Extensibility:**
- Easy to add new phases
- Simple to add new artifact patterns
- Configurable search paths

---

## Files Created/Modified

**Implementation:**
- `backend/services/phase_detector.py` - ✅ Complete (120 lines)

**Tests:**
- `tests/test_phase_detector.py` - ✅ Complete (22 tests, all passing)

---

## Acceptance Criteria Verification

✅ Correctly identifies "Implementation" phase (sprint-status.yaml exists)  
✅ Correctly identifies "Solutioning" phase (architecture.md exists)  
✅ Correctly identifies "Planning" phase (prd.md exists)  
✅ Correctly identifies "Analysis" phase (brainstorming files exist)  
✅ Returns "Unknown" for unrecognized structures  
✅ Phase detection completes in <100ms (typically <10ms)  
✅ Checks multiple artifact locations  
✅ No crashes on missing directories/files  

---

## Integration with Other Components

**Used By:**
- `BMADParser.parse_project()` - Automatically detects phase when parsing
- `Project` dataclass - Phase field populated during initialization
- Future: Breadcrumb component (Story 1.4)
- Future: Dashboard API (Story 1.3)

**Dependencies:**
- Python standard library (`os` module only)
- No external dependencies required

---

## Performance Validation

**Requirement:** <100ms (NFR3)  
**Actual Performance:** <10ms typical, <50ms worst case  
**Test Validation:** Performance test included in test suite

**Performance Test:**
```python
def test_phase_detection_performance(self, tmp_path):
    start = time.time()
    phase = PhaseDetector.detect_phase(str(tmp_path))
    elapsed = (time.time() - start) * 1000
    assert elapsed < 100  # Passes consistently
```

---

## Status

**Current Status:** ✅ **DONE**  
**Created:** 2026-01-09  
**Completed:** 2026-01-09 (implemented as part of Story 1.1)  
**Epic:** 1 (Core Orientation System)  
**Dependencies:** Story 0.1 (Project Scaffold) - COMPLETE

**Implementation Note:** Completed alongside Story 1.1 as the phase detection algorithm is tightly coupled with artifact parsing. Rather than duplicate effort, both stories were implemented together efficiently.

**Tests:** 22/22 passing ✅  
**Performance:** <10ms typical (well under 100ms requirement) ✅  
**All Acceptance Criteria Met:** YES ✅

---

## Next Steps

1. ✅ Story 1.2 complete - phase detection fully functional
2. → Proceed to Story 1.3: Flask API Dashboard Endpoint
3. → API will expose phase detection via `/api/dashboard` endpoint
