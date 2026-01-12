# Story 5.55: Smart Per-Project Cache Layer - Implementation Documentation

## Overview

Story 5.55 implements a smart per-project cache layer that dramatically improves dashboard load performance by caching done stories and only real-time checking in-progress work.

## Performance Improvements

- **Before:** 10-15 second page load (all stories re-processed)
- **After (first load):** <2 seconds (initial cache build)
- **After (cached load):** <500ms (from cache)

## Architecture

### 1. Cache Storage

Cache is stored in `{project_root}/.bmad-cache/stories.json` with the following structure:

```json
{
  "metadata": {
    "project": "BMAD Dash",
    "cached_at": "2026-01-12T14:30:00Z",
    "cache_version": "1"
  },
  "stories": {
    "0.1": {
      "title": "Story Title",
      "status": "done",
      "file_mtime": 1234567890,
      "evidence": {
        "commits": 5,
        "tests_passed": 10,
        "tests_total": 12,
        "healthy": true
      },
      "cached_at": "2026-01-11T10:00:00Z"
    }
  }
}
```

### 2. Smart Invalidation Strategy

The cache uses file modification time (mtime) for intelligent invalidation:

- **Done stories:** If mtime hasn't changed, use cache (skip git/test work)
- **In-progress stories:** Always refresh (real-time accuracy)
- **Changed done stories:** Refresh only that story

### 3. Cache API

#### Backend: `backend/services/smart_cache.py`

Key methods:

- `get_story_evidence(project_root, story_id, story_file_path, story_status)` - Returns cached evidence if valid
- `set_story_evidence(...)` - Stores evidence with invalidation metadata
- `invalidate_story(story_id)` - Forces re-fetch next load
- `clear_project_cache()` - Wipes all cached data
- `get_cache_stats()` - Returns cache statistics

#### Integration: `backend/services/project_state_cache.py`

Modified to use SmartCache in `bootstrap()` method:
- Accepts optional `SmartCache` instance in constructor
- Checks cache before running git/test correlation for done stories
- Stores evidence in cache after collection

#### API Endpoints: `backend/api/dashboard.py`

New endpoints added:

- `GET /api/cache/stats?project_root={path}` - Get cache statistics
- `POST /api/cache/clear?project_root={path}` - Clear all cache
- `POST /api/cache/invalidate/{story_id}?project_root={path}` - Invalidate specific story

#### Frontend: `frontend/js/components/cache-status.js`

- Displays cache status with done story count and last update time
- "Clear Cache" button with confirmation dialog
- Auto-refreshes dashboard after cache clear

## Usage

### For Developers

#### Using SmartCache in Backend

```python
from backend.services.smart_cache import SmartCache

# Initialize cache for a project
smart_cache = SmartCache(project_root)

# Get cached evidence (returns (evidence, cache_hit))
evidence, cache_hit = smart_cache.get_story_evidence(
    story_id="5.4",
    story_file_path="/path/to/5-4-story.md",
    story_status="done"
)

if cache_hit:
    # Use cached evidence - fast!
    pass
else:
    # Collect evidence from git/tests
    evidence = collect_evidence()
    
    # Store in cache for next time
    smart_cache.set_story_evidence(
        story_id="5.4",
        story_file_path="/path/to/5-4-story.md",
        story_status="done",
        evidence=evidence,
        title="Story Title"
    )
```

#### Using ProjectStateCache with SmartCache

```python
from backend.services.project_state_cache import ProjectStateCache
from backend.services.smart_cache import SmartCache

# Initialize SmartCache
smart_cache = SmartCache(project_root)

# Pass to ProjectStateCache
state_cache = ProjectStateCache(cache_file, smart_cache=smart_cache)

# Bootstrap will automatically use SmartCache for done stories
state = state_cache.bootstrap(project_root)
```

### For Users

#### Viewing Cache Status

The dashboard now shows cache status at the top:

```
Cache ● 15 done stories cached Updated 5 min ago  [Clear Cache]
```

#### Clearing Cache

1. Click the "Clear Cache" button
2. Confirm the dialog
3. Dashboard will automatically reload with fresh data

## Cache Invalidation Triggers

Cache is automatically invalidated when:

1. **Story file is modified** - mtime check detects change
2. **Story status changes to active** - in-progress, review, etc. always refresh
3. **Manual clear** - User clicks "Clear Cache" button
4. **Cache version mismatch** - Future versions may use different format

## Multi-Project Support

Each project has its own isolated cache:

- `Project-A/.bmad-cache/stories.json`
- `Project-B/.bmad-cache/stories.json`

This allows working on multiple projects simultaneously without cache conflicts.

## Troubleshooting

### Cache Corruption

If you encounter stale or corrupted cache data:

1. Click "Clear Cache" button in dashboard
2. Or manually delete `.bmad-cache/` directory
3. Dashboard will rebuild cache on next load

### Cache Not Working

If cache is not being used:

1. Check that `.bmad-cache/` directory exists
2. Verify cache file has correct structure
3. Check logs for cache hit/miss messages
4. Ensure story status is "done" (active stories always refresh)

### Performance Issues

If load times are still slow:

1. Check cache stats - should show done stories cached
2. Verify git/test collectors aren't running for done stories
3. Look for "Cache HIT" messages in logs
4. Check that mtime comparison is working correctly

## Testing

Run tests with:

```bash
python -m pytest tests/test_smart_cache.py -v
```

Key test coverage:

- Cache file structure validation
- Cache hit/miss logic
- Mtime-based invalidation
- Active status always refreshes
- Story invalidation
- Cache clearing
- Multi-project isolation
- Cache version handling

## Future Enhancements

Potential improvements for future iterations:

1. **Cache warming** - Pre-warm cache during idle time
2. **Partial cache refresh** - Refresh only changed stories
3. **Cache compression** - Reduce disk usage for large projects
4. **Distributed cache** - Share cache across team members
5. **Cache analytics** - Track cache hit rates and usage patterns

## Files Modified/Created

### Created
- `backend/services/smart_cache.py` - Core cache service
- `frontend/js/components/cache-status.js` - Cache status UI component
- `tests/test_smart_cache.py` - Unit tests

### Modified
- `backend/services/project_state_cache.py` - Integrated SmartCache
- `backend/api/dashboard.py` - Added cache endpoints
- `frontend/js/api.js` - Added cache API methods
- `frontend/js/views/dashboard.js` - Added cache status display
- `.gitignore` - Added `.bmad-cache/` directory

## Acceptance Criteria Status

- ✅ **AC1: First Load Baseline** - Load time <2 seconds, cache file created
- ✅ **AC2: Cached Load Performance** - Load time <500ms, in-progress fresh
- ✅ **AC3: Multi-Project Isolation** - Each project uses isolated cache
- ✅ **AC4: Intelligent Invalidation** - mtime check detects changes
- ✅ **AC5: Cache Consistency** - Invalidated on workflow completion
- ✅ **AC6: Manual Cache Clear** - Clear button in dashboard

## Definition of Done

- ✅ All acceptance criteria met
- ✅ All tasks completed
- ✅ Unit tests passing (>80% coverage for SmartCache)
- ✅ Performance benchmarks show <500ms cached load
- ✅ Integration tests pass (multi-project scenario)
- ✅ Code reviewed and approved
- ✅ `.bmad-cache/` added to `.gitignore`
- ✅ Dashboard loads <500ms on second visit
