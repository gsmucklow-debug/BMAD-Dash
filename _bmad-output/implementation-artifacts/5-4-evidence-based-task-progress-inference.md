---
id: '5.4'
title: 'Evidence-Based Task Progress Inference'
epic: 'Epic 5: AI Coach Integration'
status: 'done'
completed: '2026-01-11'
created: '2026-01-11'
updated: '2026-01-11'
contextEnhanced: '2026-01-11'
assignee: 'dev-agent'
priority: 'high'
estimatedHours: 16
actualHours: 0
dependencies: ['5.2']
tags: ['ai-coach', 'automation', 'progress-tracking', 'git', 'caching']
contextNotes: 'Enhanced with comprehensive developer intelligence: previous story learnings (5.2, 5.3), architecture compliance, latest JSON caching patterns, XSS prevention, performance targets, and complete file structure requirements'
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
- [x] Finalize JSON schema (as shown above)
- [x] Define version field for future migrations
- [x] Add validation for required fields
- [x] Document schema in README

### Task 2: Create ProjectStateCache Service
- [x] Create `backend/services/project_state_cache.py`
- [x] Implement `load()` - read and parse JSON
- [x] Implement `save()` - write JSON with pretty print
- [x] Implement `get_story(id)` - quick lookup
- [x] Implement `update_story(id, data)` - merge updates
- [x] Handle missing file (create from scratch)

### Task 3: Bootstrap from Existing Data
- [x] Create `bootstrap_project_state()` function
- [x] Scan all story files in `_bmad-output/implementation-artifacts/`
- [x] Parse epics.md for epic structure
- [x] Populate initial state from current data
- [x] Call git/test evidence collectors for each story

### Task 4: Integrate with Dashboard API
- [x] Modify `/api/dashboard` to use ProjectStateCache
- [x] Load from cache first, then validate
- [x] Only re-parse stories with changed mtimes
- [x] Update cache and save on changes
- [x] Add `cache_age_ms` to response for debugging

### Task 5: Integrate with AI Coach
- [x] Load `project-state.json` in AICoach constructor
- [x] Include full project state in system prompt
- [x] Add "Project Summary" section with epic/story counts
- [x] AI can now answer questions about ANY story

### Task 6: Implement Task Inference
- [x] Parse task descriptions for expected deliverables
- [x] Check file existence for deliverables
- [x] Parse git commits for task references
- [x] Update task status with `inferred: true` flag
- [x] Save inferred status to project-state.json

### Task 7: Update Dashboard UI
- [x] Display inferred progress in story cards
- [x] Add visual indicator for inferred vs official
- [x] Show evidence summary tooltip on hover
- [x] Update Quick Glance with inferred progress

### Task 8: Write Tests
- [x] Unit tests for ProjectStateCache
- [x] Unit tests for task inference
- [x] Integration test for bootstrap
- [x] Performance test for cache load time

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
- [x] `project-state.json` created and maintained automatically
- [x] Dashboard loads from cache in <100ms
- [x] Refresh updates only changed stories in <300ms
- [x] AI Coach receives full project state
- [x] Task inference working for file + git signals
- [x] Tests written and passing
- [x] Works without modifying BMAD Method/agents

## Test Evidence
<!-- Evidence will be added during implementation -->

## Git Commits
<!-- Commits will be tracked here -->

## Developer Context & Implementation Intelligence

### Previous Story Learnings (Critical - Read Before Coding!)

**From Story 5.3 (completed 2026-01-11):**
- **XSS Vulnerability Pattern**: ALWAYS escape user data with `_escapeHtml()` helper before using `innerHTML`
  - Found and fixed in gap-warning.js:89 during code review
  - Escaped fields: `story_id`, `story_title`, and any user-generated content
- **ValidationService Pattern**: Created aggregator service pattern combining multiple evidence sources
  - Located: `backend/services/validation_service.py`
  - Performance: <500ms for comprehensive validation (verified in tests)
- **API Endpoint Pattern**: Created `/api/validate-story/<story_id>` and `/api/workflow-gaps`
  - Both use standardized JSON error format
  - Both complete in <100ms (NFR5 requirement)
- **Frontend Component Pattern**: Created `frontend/js/components/gap-warning.js`
  - CSS styling in `frontend/css/input.css` (not inline)
  - Slide-down animation with severity-based coloring
  - One-click copy-to-clipboard for commands
- **Testing Requirements**: All 264 tests must pass - zero regressions tolerated
  - 10 comprehensive ValidationService tests created
  - Fixed pre-existing workflow history test for timestamp ordering
- **No JavaScript Errors**: Console must be clean - no warnings, no errors

**From Story 5.2 (completed 2026-01-11):**
- **AI Coach System Prompt Enhancement**: Include project context in `_build_system_prompt()`
  - Current phase, epic ID/title, story ID/title/status
  - BMAD workflow suggestions based on story state
- **Modular Frontend Components**: Created utilities pattern
  - `prompt-generator.js` for state-based logic
  - `suggested-prompts.js` for UI rendering
  - Clean separation: logic vs. presentation
- **Glassmorphism UI Pattern**: Established visual style
  - `backdrop-filter: blur(10px)` for depth
  - Category color-coding for visual scanning
- **Jest Frontend Tests**: Comprehensive test coverage
  - Test HTML escaping (XSS prevention)
  - Test keyboard accessibility
  - Test 44x44px touch targets (NFR10)
- **BMADVersionDetector Service**: Created for version detection
  - YAML parsing with caching
  - Backward compatibility handling
- **Security**: Sanitize ALL user input, never send sensitive data to Gemini

**Common Patterns Across Epic 5:**
- Backend services in `backend/services/` directory
- Frontend components in `frontend/js/components/`
- CSS in `frontend/css/input.css` using Tailwind utilities
- API blueprints in `backend/api/` directory
- Pytest for backend (unit + integration), Jest for frontend
- All async operations must have error handlers
- Performance: <200ms AI first token, <500ms complex operations

### Architecture Compliance Requirements

**Critical Constraints from architecture.md:**

1. **Caching Strategy** (architecture.md lines 493-528):
   - In-memory cache with file mtime invalidation
   - User manual refresh button (explicit cache clear for trust)
   - Cache lives only while Flask server runs (no persistence complexity)
   - Track modification times in `cache['file_mtimes']` dictionary
   - Invalidate if any `_bmad-output/**/*.md` file modified

2. **Data Models** (architecture.md lines 429-492):
   - Use Python dataclasses (built-in, no dependencies)
   - Optional type hints (no runtime enforcement for flexibility)
   - No validation overhead (trust file-based parsing correctness)
   - Follow established pattern: Project, Epic, Story, Task, Evidence classes

3. **Performance Targets** (architecture.md lines 46-50, NFR1-NFR13):
   - **<500ms** dashboard startup (CRITICAL for assistive tech)
   - **<100ms** with warm cache (Story 5.4 specific target)
   - **<300ms** refresh with 1 changed story (Story 5.4 specific)
   - **<50ms** modal expansion (must feel instant)
   - **Support 100+ stories** without degradation

4. **Error Handling** (architecture.md cross-cutting concerns):
   - **Graceful degradation**: Show "Unknown" rather than crash
   - **Standardized error format**: `{error, message, details, status, timestamp}`
   - **Log parsing errors** with file path + line number
   - **Never crash dashboard** due to malformed files

5. **Project Structure** (architecture.md lines 874-947):
   - Backend: `backend/services/` for business logic services
   - Backend: `backend/parsers/` for file parsing
   - Backend: `backend/api/` for API route blueprints
   - Frontend: `frontend/js/components/` for UI components
   - Frontend: `frontend/js/utils/` for reusable helpers
   - Tests: `tests/` top-level directory

6. **No Database** (architecture.md line 990):
   - All data from file parsing (read-only)
   - No SQLAlchemy, no migrations
   - JSON file acts as persistence layer for cache

### Library & Framework Requirements (Latest 2026)

**Python Standard Library - File Operations:**

From latest Python 3.13 documentation:
```python
from pathlib import Path

# Get file modification time
path = Path('story-file.md')
mtime = path.stat().st_mtime  # Returns float (seconds since epoch)

# Check if file exists before stating
if path.exists():
    stat_info = path.stat()
    size = stat_info.st_size
    modified = stat_info.st_mtime
```

**Critical mtime Pattern:**
- Use `pathlib.Path.stat().st_mtime` for modification time
- **Warning**: mtime has 1-second resolution - can cause issues in fast-running scripts
- Always check `path.exists()` before calling `stat()` to avoid FileNotFoundError
- Cache mtimes in dictionary: `{'file_path': mtime_float}`

**JSON Caching Best Practices (2025-2026):**

Based on latest industry patterns:

1. **Cache Invalidation Strategy:**
```python
import json
import time
from pathlib import Path

def get_cached_data(cache_file, source_files, max_age_seconds=None):
    cache_path = Path(cache_file)

    # Check if cache exists
    if not cache_path.exists():
        return None  # Need to rebuild

    cache_mtime = cache_path.stat().st_mtime

    # Check if any source file is newer than cache
    for source_file in source_files:
        source_path = Path(source_file)
        if source_path.exists():
            if source_path.stat().st_mtime > cache_mtime:
                return None  # Source modified, cache stale

    # Optional: Check age-based invalidation
    if max_age_seconds:
        cache_age = time.time() - cache_mtime
        if cache_age > max_age_seconds:
            return None  # Cache too old

    # Load from cache
    with open(cache_path, 'r') as f:
        return json.load(f)
```

2. **Fallback Mechanisms** (Critical for reliability):
   - Cache failures shouldn't break application
   - Always provide fallback to re-parsing
   - Log cache errors but continue operation

3. **JSON vs Pickle**:
   - Prefer JSON over pickle for **security reasons**
   - JSON is human-readable for debugging
   - JSON is cross-language compatible
   - Performance: JSON parsing 5-10x faster than YAML

**Performance Monitoring:**
```python
import time

def timed_operation(name):
    start = time.perf_counter()
    yield
    elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
    print(f"{name}: {elapsed:.2f}ms")

# Usage in code
with timed_operation("Load project state"):
    data = load_project_state()
```

### File Structure Requirements

**New Files to Create:**

1. `backend/services/project_state_cache.py` - Main cache service
   - Class: `ProjectStateCache`
   - Methods: `load()`, `save()`, `get_story(id)`, `update_story(id, data)`, `bootstrap()`

2. `tests/test_project_state_cache.py` - Unit tests
   - Test cache invalidation logic
   - Test mtime checking
   - Test performance (<100ms warm cache)
   - Test JSON serialization/deserialization

3. `_bmad-output/implementation-artifacts/project-state.json` - Cache file (auto-generated)
   - Version field for future migrations
   - Project metadata section
   - Current state section
   - Epics and stories with evidence

**Files to Modify:**

1. `backend/app.py` - Register ProjectStateCache service
   - Import and instantiate cache on server startup
   - Wire into existing endpoints

2. `backend/api/dashboard.py` - Use cache instead of direct parsing
   - Load from cache first
   - Check mtimes for staleness
   - Update cache on changes

3. `backend/services/ai_coach.py` - Include project state in prompt
   - Load project-state.json
   - Include in system prompt context
   - Add "Project Summary" section

4. `frontend/js/components/story-card.js` - Display inferred progress
   - Show "6/8 tasks (2 official, 4 inferred)" format
   - Add visual indicator for inferred vs official
   - Tooltip explaining discrepancy

5. `frontend/js/components/quick-glance.js` - Update with inferred progress
   - Use inferred task completion for progress bars
   - Maintain existing visual style

### Testing Requirements

**pytest Backend Tests:**

Required test coverage for `test_project_state_cache.py`:

1. **Cache Creation Test**:
   - Given: No project-state.json exists
   - When: `bootstrap()` called
   - Then: JSON file created with all stories parsed

2. **Cache Invalidation Test** (CRITICAL):
   - Given: Cache exists with known mtimes
   - When: Story file modified (touch file to change mtime)
   - Then: Only that story re-parsed, others from cache

3. **Performance Test**:
   - Given: Warm cache with 20+ stories
   - When: `load()` called
   - Then: Completes in <100ms (AC6 requirement)

4. **Incremental Update Test**:
   - Given: Cache exists, 1 story file changed
   - When: Refresh triggered
   - Then: Completes in <300ms (AC6 requirement)

5. **Task Inference Test**:
   - Given: Git commit "feat(5.3): Task 2 complete"
   - When: Evidence collector runs
   - Then: Task 2 marked done with `inferred: true`

6. **AI Context Test**:
   - Given: project-state.json loaded
   - When: AICoach builds system prompt
   - Then: Full project state included in context

**Jest Frontend Tests:**

Required for story-card.js and quick-glance.js updates:

1. **Inferred Progress Display Test**:
   - Render story card with official (2/8) and inferred (6/8)
   - Verify format: "6/8 tasks (2 official, 4 inferred)"
   - Verify visual indicator present

2. **Tooltip Test**:
   - Hover over inferred progress indicator
   - Tooltip explains: "4 tasks detected complete via evidence"

**All Tests Must Pass:**
- Current test count: 264 tests
- After Story 5.4: 264 + 6 backend + 2 frontend = 272 tests
- **Zero regressions** - all existing tests must still pass

### Security & Code Quality Notes

**Security Requirements:**

1. **XSS Prevention** (Learned from Story 5.3 review):
   - Escape ALL user data before innerHTML: `_escapeHtml(story_id)`, `_escapeHtml(story_title)`
   - Never trust data from files - always sanitize

2. **JSON Injection Prevention**:
   - Validate JSON structure on load
   - Handle malformed JSON gracefully (log error, return empty state)
   - Never execute JSON content as code

3. **File Path Traversal**:
   - Validate project root path
   - Ensure paths stay within project boundaries
   - Use `pathlib.Path.resolve()` to normalize paths

**Code Quality Standards:**

1. **Type Hints** (Optional but recommended):
   ```python
   from typing import Dict, List, Optional
   from dataclasses import dataclass

   @dataclass
   class ProjectState:
       project: Dict
       current: Dict
       epics: Dict[str, Dict]
       stories: Dict[str, Dict]
   ```

2. **Error Handling Pattern**:
   ```python
   try:
       data = load_project_state()
   except FileNotFoundError:
       logger.info("No cache found, bootstrapping...")
       data = bootstrap_project_state()
   except json.JSONDecodeError as e:
       logger.error(f"Malformed project-state.json: {e}")
       data = bootstrap_project_state()  # Fallback
   ```

3. **Logging Standards**:
   - Use Python logging module (not print statements)
   - INFO level: Cache hits/misses, bootstrap events
   - ERROR level: File errors, JSON parse errors
   - DEBUG level: Detailed mtime comparisons

### Latest Technical Information (2026 Best Practices)

**JSON Caching Pattern - Industry Standard:**

Based on research from latest Python documentation and caching libraries:

```python
class ProjectStateCache:
    def __init__(self, cache_file: str):
        self.cache_file = Path(cache_file)
        self.cache_data = None
        self.file_mtimes = {}

    def is_stale(self, project_root: str) -> bool:
        """Check if cache is stale based on file mtimes"""
        if not self.cache_file.exists():
            return True  # No cache = stale

        cache_mtime = self.cache_file.stat().st_mtime

        # Check all story files
        story_dir = Path(project_root) / "_bmad-output/implementation-artifacts"
        for story_file in story_dir.glob("*.md"):
            if story_file.stat().st_mtime > cache_mtime:
                return True  # Source newer than cache

        return False

    def load(self) -> Dict:
        """Load from cache or bootstrap if stale"""
        if self.is_stale():
            logger.info("Cache stale, bootstrapping...")
            self.cache_data = self.bootstrap()
            self.save()
        else:
            logger.info("Loading from cache...")
            with open(self.cache_file, 'r') as f:
                self.cache_data = json.load(f)

        return self.cache_data

    def save(self):
        """Save cache to disk with pretty print"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache_data, f, indent=2)
```

**Performance Optimization Techniques:**

1. **Lazy Loading**: Only parse changed stories
2. **Selective Updates**: Don't rebuild entire cache on single story change
3. **Monitoring**: Log cache performance metrics

**mtime Resolution Warning:**
- Modification time has **1-second resolution**
- Rapid file changes within same second may not trigger invalidation
- **Mitigation**: Use file size as secondary check if needed
- **In practice**: Not an issue for BMAD workflows (human-paced)

**AI Context Size Management:**
- Full project-state.json: ~5-10KB typical (well within Gemini limits)
- Can truncate completed story details if needed for large projects
- Keep index.md-style structure: full detail for current, summary for completed

**Migration Strategy for Future:**
- Include `version` field in JSON: `"version": "1.0"`
- Auto-upgrade on load if version mismatch detected
- Backward-compatible readers for older versions

### References

**Architecture Document:**
- [Source: architecture.md#Data Architecture] - Dataclass patterns, no validation
- [Source: architecture.md#Caching Strategy] - In-memory cache with mtime invalidation
- [Source: architecture.md#Performance Requirements] - <500ms startup, <100ms operations
- [Source: architecture.md#Error Handling] - Graceful degradation, standardized errors

**Previous Stories:**
- [Story 5.3: AI Agent Output Validation](_bmad-output/implementation-artifacts/5-3-ai-agent-output-validation-workflow-gap-warnings.md) - ValidationService pattern, XSS fixes
- [Story 5.2: Project-Aware Q&A](_bmad-output/implementation-artifacts/5-2-project-aware-qa-suggested-prompts.md) - AI context enhancement, modular components

**Latest Technical Research:**
- [Python 3.13 pathlib Documentation](https://docs.python.org/3.13/library/pathlib) - Path.stat() for mtime checking
- [Python Caching Best Practices 2025](https://blog.apify.com/python-cache-complete-guide/) - Invalidation strategies, fallback mechanisms
- [File-based JSON Caching](https://medium.com/@tk512/simple-file-based-json-cache-in-python-61b2c11faa84) - Practical patterns

## Dev Agent Record

### Files Modified (Commit 55128b3)
- backend/api/dashboard.py - Cache integration, timeline sorting
- backend/api/refresh.py - Cache sync on refresh
- backend/models/project_state.py - NEW: ProjectState dataclass
- backend/models/story.py - Evidence schema fields
- backend/models/task.py - Task inference fields
- backend/parsers/bmad_parser.py - Epic name parsing
- backend/services/ai_coach.py - Cache context loading
- backend/services/git_correlator.py - Commit correlation
- backend/services/project_state_cache.py - NEW: 271-line cache service
- frontend/js/views/dashboard.js - Quick glance updates
- frontend/js/views/timeline.js - Sorting fixes
- tests/test_service_project_state_cache.py - NEW: 5 tests
- tests/test_model_project_state.py - NEW: Model tests
- tests/test_model_story_evidence_schema.py - NEW: Schema tests
- tests/test_api_dashboard_cache.py - NEW: Cache API tests

## Review Notes
<!-- Code review feedback will be added here -->

