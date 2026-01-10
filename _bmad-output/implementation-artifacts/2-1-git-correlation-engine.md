---
story_id: "2.1"
story_key: "2-1-git-correlation-engine"
epic: 2
title: "Git Correlation Engine"
status: "done"
created: "2026-01-10"
completed: "2026-01-10"
context_engine_version: "v1.0"
---

# Story 2.1: Git Correlation Engine

## Story

As a **user**,  
I want **the system to detect which Git commits reference my stories**,  
So that **I can verify AI agents actually committed code for completed work**.

## Business Context

This story is the foundation of Epic 2: Quality Validation & Trust. Without Git correlation, users cannot verify that AI agents actually committed code when they claim a story is complete. This is critical for trust - users need objective evidence that work was done, not just checkmarks.

**Value:** Enables users to verify AI agent claims by showing actual Git commits that reference story identifiers. This prevents "lying about completion" - a common LLM mistake where agents mark stories done without actually committing code.

## Acceptance Criteria

**Given** a BMAD project is a Git repository with commit history  
**When** Git correlation runs for a specific story (e.g., "story-1.3")  
**Then** executes `git log` with pattern matching for story identifier  
**And** returns list of GitCommit dataclasses with hash, message, timestamp, files_changed  
**And** matches patterns: "story-1.3", "Story 1.3", "[1.3]", "feat(story-1.3)"  
**And** calculates last_commit_time from most recent matching commit  
**And** determines status: 🟢 green if commits exist, 🔴 red if none, 🟡 yellow if >7 days old  
**And** falls back to file modification time if Git commands fail (NFR22)  
**And** correlation completes in <100ms per story  
**And** handles Git CLI errors gracefully (returns "Unknown" status)  
**And** logs Git correlation mismatches for debugging  
**And** 100% accuracy on commit detection (no false positives - NFR requirement)

---

## Implementation Tasks

### Task 1: Implement GitCorrelator.get_commits_for_story() Method
- [x] Task 1 (All ACs)
  - [x] Complete the GitCorrelator class in backend/services/git_correlator.py
  - [x] Use GitPython library for Git operations
  - [x] Initialize GitPython Repo object in __init__
  - [x] Implement get_commits_for_story() method with pattern matching
  - [x] Extract commit data (sha, message, author, timestamp, files_changed)
  - [x] Handle exceptions gracefully
  - [x] Return list of GitCommit dataclass instances

### Task 1 (ORIGINAL SPEC): Implement GitCorrelator.get_commits_for_story() Method
**Implementation Details:**
- Complete the `GitCorrelator` class in `backend/services/git_correlator.py`
- Use GitPython library (already in requirements.txt: GitPython>=3.1.40)
- Initialize GitPython Repo object from `self.repo_path` in `__init__`
- Implement `get_commits_for_story(story_id: str)` method:
  - Parse story_id to extract epic.story format (e.g., "1.3" from "story-1.3")
  - Build regex patterns to match story identifiers:
    - `story-1.3`, `Story 1.3`, `[1.3]`, `feat(story-1.3)`, `fix(1.3)`
    - Case-insensitive matching
  - Iterate through Git log commits using GitPython API
  - Match commit messages against patterns
  - Extract commit data: sha (hash), message, author, timestamp, files_changed
  - Return list of GitCommit dataclass instances
- Handle exceptions gracefully:
  - Git repository not found → return empty list, log error
  - Git command failures → fall back to file modification time (NFR22)
  - Invalid story_id format → return empty list, log warning

**Acceptance:**
- Method returns GitCommit objects for matching commits
- Handles edge cases (no commits, invalid repo, malformed story_id)
- Performance: <100ms for typical repository (<1000 commits)

### Task 2: Add Status Calculation Logic
- [x] Task 2 (All ACs)
  - [x] Add calculate_status() method to GitCorrelator
  - [x] Implement green/yellow/red status logic based on commit age
  - [x] Add get_last_commit_time() helper method
  - [x] Use datetime utilities for age calculation

**Implementation Details:**
- Add `calculate_status()` method to GitCorrelator:
  - Input: list of GitCommit objects
  - Logic:
    - If commits exist:
      - Get most recent commit timestamp
      - If <7 days old → return "green"
      - If >=7 days old → return "yellow"
    - If no commits → return "red"
  - Return tuple: (status, last_commit_time)
- Add `get_last_commit_time()` helper method
- Use datetime utilities for age calculation

**Acceptance:**
- Status correctly reflects commit recency
- Handles empty commit list (returns "red")
- Handles commits older than 7 days (returns "yellow")

### Task 3: Implement Story ID Pattern Matching
- [x] Task 3 (All ACs)
  - [x] Create _build_story_patterns() method
  - [x] Generate regex patterns for various commit message formats
  - [x] Implement case-insensitive matching
  - [x] Create _matches_story() helper method
  - [x] Test with various commit message formats

**Implementation Details:**
- Create `_build_story_patterns(story_id: str)` private method:
  - Parse story_id to extract epic.story format
  - Handle formats: "1.3", "story-1.3", "Story 1.3", etc.
  - Generate regex patterns:
    - `story-1.3` (exact match, case-insensitive)
    - `Story 1.3` (with space)
    - `[1.3]` (brackets)
    - `feat(story-1.3)` (conventional commits)
    - `fix(1.3)` (short form)
  - Return list of compiled regex patterns
- Create `_matches_story(commit_message: str, patterns: List[Pattern])` helper
- Test with various commit message formats

**Acceptance:**
- Patterns match common commit message formats
- Case-insensitive matching works
- Handles edge cases (empty message, special characters)

### Task 4: Integrate GitCorrelator into Git Evidence API
- [x] Task 4 (All ACs)
  - [x] Update backend/api/git_evidence.py with GitCorrelator integration
  - [x] Extract project_root from query parameters
  - [x] Call get_commits_for_story() and calculate_status()
  - [x] Build GitEvidence dataclass and return JSON
  - [x] Add error handling (400, 404, 500 responses)
  - [x] Register blueprint in Flask app
  - [x] Verify response format matches API contract
  - [x] Write integration tests (6 tests passing)

**Implementation Details:**
- Update `backend/api/git_evidence.py`:
  - Import GitCorrelator from `backend.services.git_correlator`
  - Import GitCommit, GitEvidence from `backend.models.git_evidence`
  - Update `get_git_evidence(story_id)` endpoint:
    - Extract `project_root` from query parameters
    - Initialize GitCorrelator with project_root
    - Call `get_commits_for_story(story_id)`
    - Get status and last_commit_time from correlator
    - Build GitEvidence dataclass with commits and status
    - Return JSON response using `to_dict()` method
  - Add error handling:
    - 400 if project_root missing
    - 404 if story not found (check if story_id valid)
    - 500 if Git correlation fails (with error details)
- Ensure response format matches API contract from Story 2.3:
```json
{
  "story_id": "1.3",
  "commits": [...],
  "status": "green",
  "last_commit_time": "2026-01-10T14:30:00Z"
}
```

**Acceptance:**
- API endpoint returns correct JSON structure
- Error responses follow standardized format
- Response time <100ms (NFR5 requirement)

### Task 5: Add File Modification Time Fallback
- [x] Task 5 (All ACs)
  - [x] Implement get_commits_with_fallback() method
  - [x] Create _create_fallback_commit() to generate synthetic commit from file mtime
  - [x] Add _get_story_file_path() helper method
  - [x] Log fallback actions for debugging
  - [x] Ensure fallback doesn't mask real Git errors
  - [x] Write tests for fallback functionality (2 tests passing)

**Implementation Details:**
- Implement fallback logic per NFR22:
  - If Git correlation fails (exception raised):
    - Get story file path from story_id
    - Use `os.path.getmtime()` to get file modification time
    - Create synthetic GitCommit with file mtime as timestamp
    - Log fallback action for debugging
- Add helper method `_get_story_file_path(story_id: str, project_root: str)`
- Ensure fallback doesn't mask real Git errors (log both)

**Acceptance:**
- Fallback works when Git unavailable
- Real Git errors still logged
- File mtime used as timestamp source

### Task 6: Add Logging for Git Correlation
- [x] Task 6 (All ACs)
  - [x] Import Python logging module
  - [x] Add logger instance to GitCorrelator class
  - [x] Log key events (repo init, pattern matching, commit matches, errors, fallback)
  - [x] Use appropriate log levels (INFO, DEBUG, WARNING, ERROR)
  - [x] Include context in log messages (story_id, commit count, status)

**Implementation Details:**
- Import Python logging module
- Add logger instance to GitCorrelator class
- Log key events:
  - Git repository initialization (INFO)
  - Pattern matching results (DEBUG)
  - Commit matches found (INFO)
  - Git command failures (ERROR)
  - Fallback to file mtime (WARNING)
- Log format: Include story_id, commit count, status

**Acceptance:**
- Logs provide debugging information
- Error logs include context (story_id, error message)
- Log level appropriate (INFO for normal, ERROR for failures)

### Task 7: Write Unit Tests for GitCorrelator
- [x] Task 7 (All ACs)
  - [x] Create tests/test_git_correlator.py (14 tests passing)
  - [x] Test get_commits_for_story() with mock Git repository
  - [x] Test pattern matching with various commit message formats
  - [x] Test status calculation (green/yellow/red)
  - [x] Test error handling (invalid repo, missing story)
  - [x] Test fallback to file mtime
  - [x] Use pytest fixtures for test Git repository setup
  - [x] Mock GitPython Repo object for isolated testing
  - [x] Create tests/test_api_git_evidence.py (6 tests passing)
  - [x] All 20 new tests passing, 121 total tests passing

**Implementation Details:**
- Create `tests/test_git_correlator.py`:
  - Test `get_commits_for_story()` with mock Git repository
  - Test pattern matching with various commit message formats
  - Test status calculation (green/yellow/red)
  - Test error handling (invalid repo, missing story)
  - Test fallback to file mtime
  - Test performance (<100ms requirement)
- Use pytest fixtures for test Git repository setup
- Mock GitPython Repo object for isolated testing

**Acceptance:**
- All tests pass
- Test coverage >80% for GitCorrelator class
- Performance test validates <100ms requirement

---

## Technical Specifications

### Data Models (Already Defined)

**GitCommit** (`backend/models/git_evidence.py`):
```python
@dataclass
class GitCommit:
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: List[str] = field(default_factory=list)
```

**GitEvidence** (`backend/models/git_evidence.py`):
```python
@dataclass
class GitEvidence:
    story_id: str
    commits: List[GitCommit] = field(default_factory=list)
```

### API Contract

**Endpoint:** `GET /api/git-evidence/<story_id>?project_root=/path/to/project`

**Response Format:**
```json
{
  "story_id": "1.3",
  "commits": [
    {
      "sha": "abc123def456",
      "message": "feat(story-1.3): Implement dashboard endpoint",
      "author": "Developer Name",
      "timestamp": "2026-01-10T14:30:00Z",
      "files_changed": ["backend/api/dashboard.py", "backend/models/project.py"]
    }
  ],
  "status": "green",
  "last_commit_time": "2026-01-10T14:30:00Z"
}
```

**Error Response:**
```json
{
  "error": "GitRepositoryError",
  "message": "Git repository not found",
  "details": "Path /path/to/project is not a Git repository",
  "status": 500
}
```

### GitPython Library Usage

**Import:**
```python
from git import Repo
```

**Initialize Repository:**
```python
repo = Repo(repo_path)
```

**Iterate Commits:**
```python
for commit in repo.iter_commits():
    # Access commit properties:
    # commit.hexsha (hash)
    # commit.message (commit message)
    # commit.author.name (author name)
    # commit.committed_datetime (timestamp)
    # commit.stats.files (files changed)
```

**Pattern Matching:**
- Use Python `re` module for regex matching
- Compile patterns once, reuse for multiple commits
- Case-insensitive matching: `re.IGNORECASE` flag

### Story ID Pattern Examples

**Input story_id formats:**
- `"1.3"` → Match: `story-1.3`, `Story 1.3`, `[1.3]`, `feat(story-1.3)`
- `"story-1.3"` → Extract `1.3`, then match patterns
- `"Story 1.3"` → Extract `1.3`, then match patterns

**Commit message patterns to match:**
- `"feat(story-1.3): Add dashboard endpoint"`
- `"Story 1.3: Implement API"`
- `"[1.3] Fix bug in parser"`
- `"story-1.3 implementation"`
- `"Fix(1.3): Update tests"`

### Performance Requirements

- **Correlation time:** <100ms per story (NFR requirement)
- **Optimization strategies:**
  - Limit Git log iteration (use `max_count` parameter)
  - Cache repository object (don't reinitialize per request)
  - Compile regex patterns once, reuse
  - Early exit if enough commits found (optional)

### Error Handling

**Git Repository Errors:**
- Repository not found → Return empty commits, log error
- Invalid Git repository → Return empty commits, log error
- Git command failure → Fall back to file mtime (NFR22)

**Story ID Errors:**
- Invalid format → Return empty commits, log warning
- Story file not found → Return empty commits (not an error, story may not exist yet)

**Performance Errors:**
- Correlation takes >100ms → Log warning, still return results
- Memory issues → Log error, return partial results if possible

---

## Dev Notes

### Architecture Compliance

**File Structure:**
- Service layer: `backend/services/git_correlator.py` (already exists, needs implementation)
- Models: `backend/models/git_evidence.py` (already defined, use as-is)
- API: `backend/api/git_evidence.py` (already exists, needs integration)

**Naming Conventions:**
- Python: snake_case for functions/methods (e.g., `get_commits_for_story`)
- Classes: PascalCase (e.g., `GitCorrelator`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_COMMIT_AGE_DAYS = 7`)

**Error Handling:**
- Use standardized error format: `{error, message, details, status}`
- Log errors with context (story_id, project_root)
- Never crash on Git errors (graceful degradation)

### Previous Story Intelligence

**From Story 1.5 (Quick Glance Bar):**
- API endpoints follow RESTful pattern with query parameters
- Error responses use standardized JSON format
- Performance requirements are strict (<100ms for API responses)
- Frontend expects specific data structures (match API contract exactly)

**From Story 1.3 (Flask API Dashboard):**
- Flask Blueprint pattern used for API routes
- Query parameters extracted from `request.args`
- JSON responses use dataclass `to_dict()` methods
- CORS not needed (localhost-only)

**From Story 1.1 (BMAD Artifact Parser):**
- Dataclasses used for data models
- File parsing handles missing files gracefully (return "Unknown")
- Logging used for debugging and error tracking

### Code Reuse Opportunities

**DO NOT REINVENT:**
- GitCommit and GitEvidence dataclasses already exist → Use them
- GitEvidence API endpoint stub exists → Complete it, don't recreate
- GitCorrelator class stub exists → Implement methods, don't replace

**REUSE PATTERNS:**
- Error handling pattern from Story 1.3 (standardized JSON errors)
- Logging pattern from Story 1.1 (Python logging module)
- API Blueprint pattern from Story 1.3 (Flask Blueprint)

### Testing Standards

**Unit Tests:**
- Test GitCorrelator methods in isolation
- Mock GitPython Repo object for predictable testing
- Test pattern matching with various commit message formats
- Test error handling and fallback logic

**Integration Tests:**
- Test API endpoint with real Git repository (fixture)
- Test end-to-end: API call → GitCorrelator → Response
- Test error responses (400, 404, 500)

**Performance Tests:**
- Validate <100ms requirement with realistic repository size
- Test with large commit history (1000+ commits)

### References

- [Source: `_bmad-output/planning-artifacts/architecture.md#Git-Correlation`] - Git correlation requirements and patterns
- [Source: `_bmad-output/planning-artifacts/epics.md#Epic-2`] - Epic 2 requirements and acceptance criteria
- [Source: `backend/models/git_evidence.py`] - GitCommit and GitEvidence dataclass definitions
- [Source: `backend/api/git_evidence.py`] - API endpoint stub to complete
- [Source: `backend/services/git_correlator.py`] - GitCorrelator class stub to implement
- [Source: `requirements.txt`] - GitPython>=3.1.40 dependency already included

---

## Code Review Findings

**Review Date:** 2026-01-10  
**Review Type:** Adversarial Senior Developer Code Review  
**Reviewer:** AI Code Review Agent (Claude Sonnet 4.5)

### Issues Found: 9 Total (1 Critical, 1 High, 5 Medium, 2 Low)

#### Critical Issues (Fixed)
1. ✅ **API Endpoint Doesn't Use Fallback Method** - API called `get_commits_for_story()` instead of `get_commits_with_fallback()`
   - **Fix:** Updated API endpoint to use `get_commits_with_fallback(story_id, project_root)` per NFR22
   - **Location:** `backend/api/git_evidence.py:42`

#### High Issues (Fixed)
1. ✅ **AC Violation: Fallback Not Used in API** - Acceptance criteria requires fallback but API didn't use it
   - **Fix:** Integrated fallback method into API endpoint
   - **Location:** `backend/api/git_evidence.py:42`

#### Medium Issues (Fixed)
1. ✅ **Unused Imports** - `InvalidGitRepositoryError` and `GitCommandError` imported but not used
   - **Fix:** Updated exception handling to use specific exception types, added `NoSuchPathError`
   - **Location:** `backend/services/git_correlator.py:11, 29-33`

2. ✅ **Timezone Handling Issue** - `replace(tzinfo=None)` could cause issues with timezone-aware datetimes
   - **Fix:** Implemented proper timezone-aware and naive datetime comparison
   - **Location:** `backend/services/git_correlator.py:165-171`

3. ✅ **Hard-Coded Performance Limit** - `max_count=1000` hard-coded without documentation
   - **Fix:** Added comment explaining performance optimization rationale
   - **Location:** `backend/services/git_correlator.py:54-55`

4. ✅ **Missing Performance Test** - No actual performance test for <100ms requirement
   - **Fix:** Added `test_performance_requirement()` test with timing validation
   - **Location:** `tests/test_git_correlator.py:267-290`

5. ✅ **Incomplete File List Documentation** - Missing sprint-status.yaml and story file itself
   - **Fix:** Updated File List to include all modified files
   - **Location:** Story File List section

#### Low Issues (Fixed)
1. ✅ **Missing Timezone Tests** - No tests for timezone-aware vs naive datetime handling
   - **Fix:** Added `test_calculate_status_with_timezone_aware_datetime()` and `test_calculate_status_with_naive_datetime()`
   - **Location:** `tests/test_git_correlator.py:292-320`

2. ✅ **API Fallback Test Missing** - No test verifying API uses fallback method
   - **Fix:** Added `test_get_git_evidence_uses_fallback()` test
   - **Location:** `tests/test_api_git_evidence.py:130-150`

### Review Outcome
- **Status:** ✅ PASSED (After Fixes)
- **Issues Fixed:** 9 of 9 (All Critical, High, Medium, and Low issues resolved)
- **Tests Added:** 4 new tests (performance, timezone handling, API fallback verification)
- **Final Test Count:** 125 tests passing (17 GitCorrelator + 7 API + 101 existing)
- **Story Status:** Ready for completion

### Change Log

**2026-01-10 (Code Review Fixes):**
- Fixed API endpoint to use `get_commits_with_fallback()` method per NFR22 requirement
- Updated exception handling to use specific GitPython exception types
- Fixed timezone handling for both timezone-aware and naive datetime objects
- Added performance test to validate <100ms correlation requirement
- Added timezone handling tests for edge cases
- Added API fallback usage verification test
- Updated File List to include all modified files (sprint-status.yaml, story file)
- All 9 code review issues resolved
- Test count increased from 121 to 125 (4 new tests added)

---

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (via Cursor)

### Debug Log References

N/A - No debug issues encountered

### Completion Notes List

- ✅ Implemented complete GitCorrelator class with pattern matching, status calculation, and logging
- ✅ All 7 story tasks completed (Tasks 1-7)
- ✅ Pattern matching supports multiple commit message formats (story-1.3, [1.3], feat(story-1.3), etc.)
- ✅ Status calculation: green (<7 days), yellow (>=7 days), red (no commits)
- ✅ File modification time fallback implemented per NFR22 and integrated into API endpoint
- ✅ Git Evidence API endpoint fully integrated and tested
- ✅ Error handling for invalid repositories, missing files, Git command failures
- ✅ Comprehensive logging at all levels (INFO, DEBUG, WARNING, ERROR)
- ✅ 17 unit tests for GitCorrelator (100% passing, including performance and timezone tests)
- ✅ 7 integration tests for API endpoint (100% passing, including fallback verification)
- ✅ Full test suite: 125 tests passing, 0 failures
- ✅ All acceptance criteria satisfied
- ✅ Performance requirement validated: <100ms correlation time (tested)
- ✅ Code follows architecture patterns: Flask Blueprint, dataclasses, standardized error format
- ✅ Code review fixes applied: API fallback integration, timezone handling, specific exception types, performance test added

### File List

**Created:**
- backend/services/git_correlator.py - Complete GitCorrelator implementation with all methods
- tests/test_git_correlator.py - Unit tests for GitCorrelator (17 tests)
- tests/test_api_git_evidence.py - Integration tests for Git Evidence API (7 tests)

**Modified:**
- backend/api/git_evidence.py - Integrated GitCorrelator, implemented full endpoint with fallback support
- backend/app.py - Registered git_evidence_bp blueprint
- _bmad-output/implementation-artifacts/sprint-status.yaml - Updated story status tracking
- _bmad-output/implementation-artifacts/2-1-git-correlation-engine.md - Story file updates

**Unchanged:**
- backend/models/git_evidence.py - (No changes, used existing dataclasses)
