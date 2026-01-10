---
story_id: "2.1"
story_key: "2-1-git-correlation-engine"
epic: 2
title: "Git Correlation Engine"
status: "ready-for-dev"
created: "2026-01-10"
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

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
