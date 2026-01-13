---
story_id: "5.5"
reviewer: "Adversarial Agent"
date: "2026-01-12"
status: "requires_changes"
---

# Code Review: Story 5.5 (AI Context & Caching)

## Summary
The implementation meets the functional requirements (AC1, AC2) but exhibits fragility and potential scalability issues that must be addressed before sign-off. The caching strategy is an improvement but the "active story" invalidation logic is naive.

## Critical Issues (Must Fix)

### 1. Hardcoded External Dependency
*   **Location**: `backend/services/ai_coach.py` lines 79-80
*   **Issue**: `requests.get('http://docs.bmad-method.org', ...)`
*   **Impact**: If this domain changes or goes down, the "AI Coach" feature will hang or log errors. Hardcoding HTTP (not HTTPS) is also a bad practice.
*   **Fix**: Move URL to `Config` / env vars. Use HTTPS.

### 2. Fragile HTML Parsing
*   **Location**: `backend/services/ai_coach.py` lines 87-91
*   **Issue**: `BeautifulSoup` usage with specific tag decomposition (`script`, `style`, `nav`, `footer`).
*   **Impact**: Any changes to the underlying documentation site's DOM structure (e.g., changing `nav` to a `div` with a class) will break the content extraction, potentially feeding garbage to the AI.
*   **Fix**: Use a more robust extraction method or a dedicated raw/markdown content endpoint if available.

### 3. Naive Token Truncation
*   **Location**: `backend/services/ai_coach.py` line 101-102
*   **Issue**: `cleaned_text[:8000]`
*   **Impact**: Cutting off at a hard byte limit can slice in the middle of a sentence or, worse, a code block, confusing the LLM. It also ignores the logical structure of the documentation.
*   **Fix**: Implement semantic truncation (cut at nearest paragraph/header before limit).

## Major Issues (Should Fix)

### 4. Performance Bottleneck for Active Stories
*   **Location**: `backend/services/project_state_cache.py` line 201
*   **Issue**: `Active stories always refresh` - triggering `git_correlator` and `test_discoverer` on every sync.
*   **Impact**: As the project grows, if `git log` or `pytest --collect-only` takes >1s, the dashboard will feel sluggish whenever an active story exists.
*   **Fix**: Implement a file-watcher or mtime check for active stories too. Only re-run git/test discovery if files in the story's scope have changed.

### 5. Error Handling Blind Spots
*   **Location**: `backend/services/project_state_cache.py`
*   **Issue**: Exceptions during evidence collection are logged as warnings (lines 236, 250), but the `story.evidence` dict might remain in an inconsistent state (keys missing).
*   **Impact**: Frontend components expecting keys like `commits` or `tests_passed` might throw JS errors if they are missing (undefined).
*   **Fix**: Ensure `story.evidence` is initialized with default "empty/failure" values before attempting collection, so the strictly typed frontend doesn't crash on missing props.

## Security & NFRs
*   **NFR-Security**: `requests` call does not verify SSL (using HTTP).
*   **NFR-Performance**: `BeautifulSoup` parsing on every cache miss (1 hour expiry) adds latency to the first request. Ideally, this should be a background job.

## Recommendation
**CHANGES REQUESTED**. Fix Critical Issues 1-3. Address Major Issue 5 (Safety defaults) to prevent frontend crashes. Issue 4 can be deferred if performance is currently acceptable (<500ms).
