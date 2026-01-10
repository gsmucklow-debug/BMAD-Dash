---
story_id: "2.3"
story_key: "2-3-evidence-api-endpoints"
epic: 2
title: "Evidence API Endpoints"
status: "ready-for-dev"
created: "2026-01-10"
completed: ""
context_engine_version: "v1.0"
---

# Story 2.3: Evidence API Endpoints

## Story

As a **user**,  
I want **API endpoints that serve Git and test evidence for stories**,  
So that **the frontend can display validation badges and expandable details**.

## Business Context

This story is part of Epic 2: Quality Validation & Trust. The frontend needs REST API endpoints to fetch Git commit evidence and test evidence for stories. These endpoints will power the validation badges and expandable modals in Story 2.4.

**Value:** Enables frontend to display real-time validation status (Git commits, test results) without parsing files directly. Provides standardized JSON responses that frontend can consume reliably.

**Dependencies:** 
- Uses `GitCorrelator` service from Story 2.1
- Uses `TestDiscoverer` service from Story 2.2
- Follows Flask Blueprint pattern from `backend/api/git_evidence.py`
- Will be consumed by Story 2.4 (Evidence Badges & Expandable Modals)

## Acceptance Criteria

**Given** Flask server is running  
**When** GET request to `/api/git-evidence/<story_id>?project_root=/path`  
**Then** returns JSON with commits array, status, last_commit_time  
**And** each commit includes hash, message, timestamp, files_changed  
**And** returns <100ms response time (NFR5 requirement)  
**When** GET request to `/api/test-evidence/<story_id>?project_root=/path`  
**Then** returns JSON with total, passing, failing, status, last_run_time, failing_test_names  
**And** returns <100ms response time (NFR5 requirement)  
**And** both endpoints return 400 if parameters missing  
**And** both endpoints return 404 if story not found  
**And** both endpoints return 500 with error details if parsing fails  
**And** responses use standardized error format: {error, message, details, status}

---

## Implementation Tasks

- [ ] ### Task 1: Implement Test Evidence API Endpoint

**Implementation Details:**
- Complete the `get_test_evidence()` function in `backend/api/test_evidence.py`
- Extract `project_root` from query parameters (required)
- Validate `project_root` parameter exists (return 400 if missing)
- Initialize `TestDiscoverer` with project_root
- Call `get_test_evidence_for_story(story_id, project_root)` to get TestEvidence
- Convert TestEvidence to dict using `to_dict()` method
- Return JSON response with status 200
- Handle exceptions and return standardized error format (500 status)
- Log INFO on success, ERROR on failure
- Ensure response time <100ms (NFR5 requirement)

**Acceptance:**
- Endpoint returns TestEvidence JSON with all fields
- Returns 400 if project_root missing
- Returns 500 with error details if parsing fails
- Response time <100ms
- Uses standardized error format

- [ ] ### Task 2: Register Test Evidence Blueprint in Flask App

**Implementation Details:**
- Import `test_evidence_bp` in `backend/app.py`
- Register blueprint: `app.register_blueprint(test_evidence_bp)`
- Ensure blueprint is registered after git_evidence blueprint (for consistency)
- Verify endpoint is accessible at `/api/test-evidence/<story_id>`

**Acceptance:**
- Blueprint registered correctly
- Endpoint accessible via Flask app
- No import errors or registration conflicts

- [ ] ### Task 3: Add Error Handling for Story Not Found

**Implementation Details:**
- In both endpoints, check if story_id is valid format
- If TestDiscoverer/GitCorrelator returns empty results, consider if story exists
- Return 404 status with standardized error format if story not found
- Error format: `{error: "StoryNotFound", message: "Story {story_id} not found", details: "...", status: 404}`
- Log WARNING when story not found

**Acceptance:**
- Returns 404 for invalid/non-existent story IDs
- Uses standardized error format
- Logs appropriately

- [ ] ### Task 4: Validate Response Format Consistency

**Implementation Details:**
- Ensure test-evidence endpoint response matches git-evidence format structure
- Both should include: story_id, status, timestamp fields
- TestEvidence response should include: total_tests, pass_count, fail_count, failing_test_names
- GitEvidence response should include: commits array with full commit details
- Verify JSON serialization handles datetime objects correctly

**Acceptance:**
- Response formats are consistent between endpoints
- Datetime objects serialize to ISO format strings
- All required fields present in responses

- [ ] ### Task 5: Add Performance Validation

**Implementation Details:**
- Add timing measurements to both endpoints
- Log WARNING if response time exceeds 100ms (NFR5 requirement)
- Use `time.perf_counter()` for accurate timing
- Consider caching if performance issues arise (future optimization)

**Acceptance:**
- Endpoints log warnings if slow
- Response times measured and logged
- Performance meets <100ms requirement

- [ ] ### Task 6: Write Integration Tests

**Implementation Details:**
- Create `tests/test_api_test_evidence.py` following pattern from `tests/test_api_git_evidence.py`
- Test successful test evidence retrieval
- Test missing project_root parameter (400 error)
- Test invalid story_id (404 error)
- Test error handling (500 error)
- Test response format matches expected structure
- Test performance requirement (<100ms)
- Use Flask test client for endpoint testing

**Acceptance:**
- Integration tests cover all scenarios
- Tests follow patterns from test_api_git_evidence.py
- All tests pass
- Tests validate response format and error handling

---

## Dev Notes

### Architecture Patterns

**Flask Blueprint Pattern:**
- Follow `git_evidence.py` pattern exactly
- Blueprint in `backend/api/test_evidence.py`
- Register in `backend/app.py`
- Use same error handling and logging patterns

**Error Handling:**
- Standardized error format: `{error, message, details, status}`
- 400: Missing required parameters
- 404: Story not found
- 500: Internal server errors (parsing failures, exceptions)
- All errors logged appropriately

**Service Integration:**
- Use `TestDiscoverer.get_test_evidence_for_story(story_id, project_root)`
- Service already handles all edge cases (no tests, parsing failures, etc.)
- API layer just wraps service calls with HTTP handling

**Performance:**
- Response time <100ms (NFR5 requirement)
- TestDiscoverer already optimized for <100ms per story
- API overhead should be minimal (<10ms)
- Log warnings if performance degrades

### File Structure

```
backend/
  api/
    test_evidence.py          # TestEvidence API endpoint (implement here)
    git_evidence.py           # Reference implementation pattern
  app.py                      # Register test_evidence_bp blueprint
tests/
  test_api_test_evidence.py   # Integration tests for test evidence endpoint
```

### Testing Standards

**Integration Tests:**
- Test successful retrieval with real TestDiscoverer
- Test error scenarios (missing params, invalid story, parsing failures)
- Test response format validation
- Test performance requirement
- Follow patterns from `tests/test_api_git_evidence.py`

**Test Patterns:**
- Use Flask test client (`app.test_client()`)
- Mock TestDiscoverer if needed for error scenarios
- Validate JSON response structure
- Check status codes and error formats

### Previous Story Intelligence (Story 2.1 & 2.2)

**Learnings from Git Evidence API:**
- Use Flask Blueprint pattern for modular endpoints
- Extract project_root from query parameters
- Validate required parameters early (return 400 if missing)
- Use standardized error format for consistency
- Log INFO on success, ERROR on failures
- Handle exceptions gracefully with try/except blocks
- Return appropriate HTTP status codes

**Code Patterns:**
- Blueprint definition: `test_evidence_bp = Blueprint('test_evidence', __name__)`
- Route decorator: `@test_evidence_bp.route('/api/test-evidence/<story_id>', methods=['GET'])`
- Error response: `jsonify({error, message, details, status}), status_code`
- Success response: `jsonify(evidence.to_dict()), 200`
- Logging: `logger.info()` for success, `logger.error()` for failures

**Files Created/Modified:**
- `backend/api/git_evidence.py` - Reference implementation (Story 2.1)
- `tests/test_api_git_evidence.py` - Integration test pattern (Story 2.1)
- `backend/services/test_discoverer.py` - Service to use (Story 2.2)

### References

- [Source: `_bmad-output/planning-artifacts/epics.md#Story-2.3`] - Story requirements and acceptance criteria
- [Source: `backend/api/git_evidence.py`] - Reference implementation pattern
- [Source: `backend/services/test_discoverer.py`] - TestDiscoverer service to use
- [Source: `tests/test_api_git_evidence.py`] - Integration test patterns
- [Source: `backend/models/test_evidence.py`] - TestEvidence dataclass definition

### Project Structure Notes

**Alignment:**
- Follows established Flask Blueprint pattern (`backend/api/`)
- Uses existing TestDiscoverer service (`backend/services/`)
- Test structure matches existing patterns (`tests/test_api_*.py`)

**No Conflicts:**
- TestEvidence API endpoint stub exists but returns 501 (ready for implementation)
- Blueprint already defined, just needs implementation
- No conflicts with existing code

---

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent if issues encountered_

### Completion Notes List

_To be filled by dev agent upon completion_

### File List

_To be filled by dev agent upon completion_

---

## Change Log

_To be filled by dev agent upon completion_
