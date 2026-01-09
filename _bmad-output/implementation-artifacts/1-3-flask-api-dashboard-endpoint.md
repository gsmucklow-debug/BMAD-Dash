---
story_id: "1.3"
story_key: "1-3-flask-api-dashboard-endpoint"
epic: 1
title: "Flask API - Dashboard Endpoint"
status: "done"
created: "2026-01-09"
completed: "2026-01-09"
context_engine_version: "v1.0"
---

# Story 1.3: Flask API - Dashboard Endpoint

## User Story

As a **user**,  
I want **a backend API that serves complete dashboard data in a single endpoint**,  
So that **the frontend can display my project state without parsing files itself**.

## Business Context

This story delivers the first public API endpoint of BMAD Dash - the `/api/dashboard` endpoint that orchestrates all parsing and data assembly to serve the frontend. This is the bridge between the parsing engine (Stories 1.1-1.2) and the upcoming frontend components (Stories 1.4-1.5).

**Value:** Enables the frontend to get structured project data via a clean REST API, maintaining separation of concerns and allowing the frontend to remain stateless.

## Acceptance Criteria

**Given** Flask server is running on localhost:5000  
**When** GET request to `/api/dashboard?project_root=/path/to/project`  
**Then** returns JSON with `project`, `breadcrumb`, `quick_glance`, and `kanban` data

**And** response includes project name and detected phase

**And** `breadcrumb` data shows Project → Phase → Epic → Story → Task hierarchy

**And** `quick_glance` shows Done story, Current story, Next story with context

**And** `kanban` data organizes stories by status (TODO/IN PROGRESS/REVIEW/COMPLETE)

**And** returns 400 error if `project_root` parameter missing with clear error message

**And** returns 404 error if project path doesn't exist

**And** returns 500 error if parsing fails, with error details in response

**And** cache is used (file mtime checking) to serve responses in <500ms (NFR1 requirement)

**And** CORS is disabled (Flask default for localhost-only operation)

**And** error responses use standardized JSON format: `{error, message, details, status}`

---

## Implementation Tasks

### Task 1: Create Dashboard API Route Handler
**Implementation Details:**
- Update `backend/api/dashboard.py` with complete route implementation
- Implement `@app.route('/api/dashboard', methods=['GET'])` 
- Extract `project_root` from query parameters
- Validate `project_root` parameter exists and path is valid
- Handle missing parameter → return 400 error
- Handle invalid path → return 404 error
- Use `BMADParser` to parse project and build response
- Catch and handle parsing exceptions → return 500 with details

**Acceptance:**
- Route responds to GET `/api/dashboard`
- Query parameter validation works correctly
- Error handling covers all edge cases
- Returns proper HTTP status codes

### Task 2: Build Dashboard Data Structure
**Implementation Details:**
- Use `BMADParser(project_root).parse_project()` to get Project dataclass
- Build `breadcrumb` dict with Project, Phase, Epic, Story, Task
- Build `quick_glance` dict with Done (last completed), Current (in-progress), Next (next todo)
- Build `kanban` dict with stories grouped by status
- Convert all dataclasses to JSON-serializable dicts using `to_dict()` methods
- Ensure response matches frontend's expected structure

**Acceptance:**
- Breadcrumb shows complete hierarchy
- Quick Glance identifies correct Done/Current/Next stories
- Kanban groups stories correctly by status
- All nested objects properly serialized

### Task 3: Implement Response Caching
**Implementation Details:**
- Use existing `Cache` system from Story 1.1
- Cache dashboard response keyed by `project_root`
- Track `sprint-status.yaml` mtime for cache invalidation
- On cache hit: return cached response (skip parsing)
- On cache miss: parse, build response, cache, return
- Ensure cache invalidation works when files change
- Add cache statistics logging for debugging

**Acceptance:**
- First request parses and caches
- Subsequent requests return cached data
- Cache invalidates when sprint-status.yaml changes
- Response time <500ms (leveraging cache)
- No stale data served

### Task 4: Implement Error Handler Decorator
**Implementation Details:**
- Update `backend/utils/error_handler.py` with standardized error responses
- Create `@handle_api_errors` decorator
- Catch `ValueError` → 400 Bad Request
- Catch `FileNotFoundError` → 404 Not Found  
- Catch generic `Exception` → 500 Internal Server Error
- Return JSON: `{"error": "ErrorType", "message": "...", "details": {...}, "status": 400}`
- Log all errors for debugging
- Apply decorator to dashboard route

**Acceptance:**
- All errors return standardized JSON format
- HTTP status codes match error types
- Error details included for debugging
- No unhandled exceptions crash the server

### Task 5: Update Flask App Configuration
**Implementation Details:**
- Update `backend/app.py` to register dashboard blueprint
- Import and register `dashboard` blueprint from `backend.api.dashboard`
- Ensure CORS is disabled (default Flask behavior for localhost)
- Configure JSON response settings (disable ASCII escaping, pretty print in debug)
- Add logging configuration for API requests
- Test that route is accessible at `/api/dashboard`

**Acceptance:**
- Dashboard route is registered and accessible
- Flask app starts without errors
- Logging shows API requests
- JSON responses formatted correctly

### Task 6: Write Comprehensive Tests
**Implementation Details:**
- Create `tests/test_api_dashboard.py`
- Test successful dashboard request with valid project
- Test 400 error when `project_root` missing
- Test 404 error when project path doesn't exist
- Test 500 error when parsing fails (malformed YAML)
- Test cache hit scenario (second request faster)
- Test cache invalidation (file change triggers re-parse)
- Test response structure matches specification
- Use pytest-flask for testing Flask endpoints
- Create fixture projects for testing

**Acceptance:**
- All happy path scenarios tested
- All error scenarios tested
- Cache behavior validated
- Response structure validated
- All tests passing

---

## Technical Specifications

### API Endpoint

**Route:** `GET /api/dashboard`

**Query Parameters:**
- `project_root` (required) - Absolute path to project root directory

**Response Format (200 OK):**
```json
{
  "project": {
    "name": "BMAD Dash",
    "phase": "Implementation",
    "root_path": "/path/to/project",
    "sprint_status_mtime": 1234567890.123
  },
  "breadcrumb": {
    "project": "BMAD Dash",
    "phase": "Implementation",
    "epic": {
      "id": "1",
      "title": "Core Orientation System"
    },
    "story": {
      "id": "1.3",
      "title": "Flask API Dashboard Endpoint"
    },
    "task": {
      "id": "task-1",
      "title": "Create Dashboard API Route Handler"
    }
  },
  "quick_glance": {
    "done": {
      "story_id": "1.2",
      "title": "Phase Detection Algorithm",
      "completed": "2026-01-09"
    },
    "current": {
      "story_id": "1.3",
      "title": "Flask API Dashboard Endpoint",
      "status": "in-progress",
      "progress": "2/6 tasks"
    },
    "next": {
      "story_id": "1.4",
      "title": "Frontend Shell & Breadcrumb Navigation"
    }
  },
  "kanban": {
    "todo": [
      {
        "story_id": "1.4",
        "title": "Frontend Shell & Breadcrumb Navigation",
        "epic": 1,
        "tasks": []
      }
    ],
    "in_progress": [
      {
        "story_id": "1.3",
        "title": "Flask API Dashboard Endpoint",
        "epic": 1,
        "tasks": [...]
      }
    ],
    "review": [],
    "done": [
      {
        "story_id": "1.1",
        "title": "BMAD Artifact Parser & Data Models",
        "epic": 1,
        "completed": "2026-01-09"
      },
      {
        "story_id": "1.2",
        "title": "Phase Detection Algorithm",
        "epic": 1,
        "completed": "2026-01-09"
      }
    ]
  }
}
```

**Error Format (4xx/5xx):**
```json
{
  "error": "ValueError",
  "message": "project_root parameter is required",
  "details": {
    "parameter": "project_root",
    "received": null
  },
  "status": 400
}
```

### Dashboard Data Builder Logic

**Breadcrumb Identification:**
1. Project: from `project.name`
2. Phase: from `project.phase` (detected automatically)
3. Epic: find epic with status "in-progress" OR most recent epic with incomplete stories
4. Story: find story with status "in-progress" OR first "ready-for-dev" story
5. Task: find first task with status "todo" in current story

**Quick Glance Identification:**
1. Done: Last story with status "done" (by completion date)
2. Current: First story with status "in-progress" OR "ready-for-dev"
3. Next: First story with status "backlog" OR "todo" after current

**Kanban Grouping:**
1. TODO: stories with status "backlog" or "todo"
2. IN PROGRESS: stories with status "ready-for-dev" or "in-progress"
3. REVIEW: stories with status "review"
4. DONE: stories with status "done"

**Status Mapping:**
```python
STATUS_GROUPS = {
    "todo": ["backlog", "todo"],
    "in_progress": ["ready-for-dev", "in-progress"],
    "review": ["review"],
    "done": ["done", "complete"]
}
```

### Cache Strategy

**Cache Key:** `f"dashboard_{project_root}"`

**Invalidation Triggers:**
- `sprint-status.yaml` mtime changes
- Any story file mtime newer than cached time
- Manual refresh via `/api/refresh` endpoint

**Cache Storage:**
```python
cache = Cache()
cache_key = f"dashboard_{project_root}"
sprint_status_path = os.path.join(project_root, "_bmad-output/implementation-artifacts/sprint-status.yaml")

# Try cache
cached_response = cache.get(cache_key, sprint_status_path)
if cached_response:
    return jsonify(cached_response), 200

# Parse and cache
response = build_dashboard_response(project_root)
cache.set(cache_key, response, sprint_status_path)
return jsonify(response), 200
```

### Error Handling Pattern

```python
from backend.utils.error_handler import handle_api_errors

@app.route('/api/dashboard')
@handle_api_errors
def get_dashboard():
    project_root = request.args.get('project_root')
    
    if not project_root:
        raise ValueError("project_root parameter is required")
    
    if not os.path.exists(project_root):
        raise FileNotFoundError(f"Project not found: {project_root}")
    
    # Parse and build response
    parser = BMADParser(project_root)
    project = parser.parse_project()
    
    if not project:
        raise Exception("Failed to parse project")
    
    response = build_dashboard_response(project)
    return jsonify(response), 200
```

### Performance Requirements

- **First Load (cache miss):** <500ms (NFR1)
- **Cached Load (cache hit):** <50ms
- **Parsing Time:** <200ms (from Story 1.1 requirement)
- **Response Assembly:** <100ms
- **JSON Serialization:** <50ms

**Total Budget:** 500ms
- Parsing: 200ms
- Cache check: 5ms
- Response building: 100ms
- Serialization: 50ms
- Network/Flask overhead: 145ms buffer

---

## Files to Create/Modify

**API Handler:**
- `backend/api/dashboard.py` - Full implementation of dashboard endpoint

**Error Handling:**
- `backend/utils/error_handler.py` - Standardized error decorator

**App Configuration:**
- `backend/app.py` - Register dashboard blueprint

**Tests:**
- `tests/test_api_dashboard.py` - NEW FILE - Comprehensive API tests

**Total:** 4 files (1 new, 3 modified)

---

## Dependencies

**Completed Stories:**
- ✅ Story 0.1: Project Scaffold (Flask app exists)
- ✅ Story 1.1: BMAD Parser & Data Models (parser ready)
- ✅ Story 1.2: Phase Detection (phase detection working)

**Required For:**
- Story 1.4: Frontend Shell (needs this API to fetch data)
- Story 1.5: Quick Glance Bar (uses quick_glance from this API)

---

## Testing Strategy

### Unit Tests
- Test breadcrumb identification logic
- Test quick_glance story selection
- Test kanban status grouping
- Test error handler decorator

### Integration Tests  
- Test full dashboard endpoint with real BMAD Dash project
- Test cache hit/miss scenarios
- Test error responses (400, 404, 500)
- Test response structure validation

### Performance Tests
- Measure cache hit response time (<50ms requirement)
- Measure cache miss response time (<500ms requirement)
- Validate no memory leaks with repeated requests

---

## Status

**Current Status:** ready-for-dev  
**Created:** 2026-01-09  
**Epic:** 1 (Core Orientation System)  
**Dependencies:** Story 0.1, 1.1, 1.2 (all complete)

**Next Steps:**
1. Implement dashboard endpoint route handler
2. Build data structure builders (breadcrumb, quick_glance, kanban)
3. Integrate caching with mtime checking
4. Add error handling and validation
5. Write comprehensive tests
6. Verify <500ms performance requirement
7. Move to Story 1.4 (Frontend Shell)
