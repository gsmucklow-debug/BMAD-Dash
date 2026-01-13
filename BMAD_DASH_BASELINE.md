# BMAD Dash Baseline Behavior Checklist

**Project:** BMAD Dash (the dashboard itself)
**Date:** 2026-01-13
**Purpose:** Reference for validating multi-project behavior on Echo-OS

This document establishes expected baseline behavior when BMAD Dash runs on its own project. Use this to compare against Echo-OS behavior during Story 6.1 validation.

---

## Performance Baseline

### Startup & Load Times
- [ ] **Dashboard Startup:** <500ms from page load to interactive
- [ ] **Artifact Parse Time:** All files parsed in <100ms (warm cache)
- [ ] **First AI Token:** <200ms latency when asking AI first question
- [ ] **View Transitions:** Dashboard → Timeline → List transitions in <100ms with 60fps

**Measured on BMAD Dash:** (To be filled during baseline test)
- Dashboard Startup: ___ms
- Parse Time: ___ms
- AI First Token: ___ms
- View Transition: ___ms

### Memory Usage
- [ ] Dashboard never exceeds 100MB memory usage
- [ ] No memory leaks during view switching (refresh memory after 10 switches)

---

## Functional Baseline

### Core Navigation

**Breadcrumb Navigation**
- [ ] Displays full hierarchy: Project → Phase → Epic → Story → Task
- [ ] Current level is highlighted
- [ ] Shows correct phase detection (should be "Implementation" for BMAD Dash)
- [ ] Shows correct epic (Epic 5 is latest)
- [ ] Shows correct story (5.7 is latest)

**Quick Glance Bar**
- [ ] Done section shows last completed story (5.7)
- [ ] Current section shows current story (should be Epic 5 or none if all done)
- [ ] Next section shows next TODO story
- [ ] Epic progress shows: "7/7 stories complete" (100%)
- [ ] Story task progress visible and accurate

**Project Information**
- [ ] Project name displays as "BMAD-Dash"
- [ ] Phase displays as "Implementation"
- [ ] No error messages in console
- [ ] Dashboard fully loads without JavaScript errors

### Kanban Board

**Dashboard View (Full Context)**
- [ ] Displays 4 columns: TODO, IN PROGRESS, REVIEW, COMPLETE
- [ ] COMPLETE column contains all 7 Epic 5 stories
- [ ] Each story card shows:
  - [ ] Story title (e.g., "Gemini API Integration & Streaming Chat")
  - [ ] Epic reference (epic-5)
  - [ ] Status badge
  - [ ] Evidence badges (Git, Tests, Workflow)

**Timeline View (Workflow History)**
- [ ] Shows visual timeline of workflow execution
- [ ] Most recent workflows appear at top
- [ ] Can click entries to see details
- [ ] Renders in <100ms

**List View (Minimal)**
- [ ] Shows only current story title
- [ ] Shows current task description
- [ ] Shows next action command
- [ ] Clean minimal design with no Kanban columns

### Evidence & Validation

**Git Evidence Badges**
- [ ] 🟢 green badges show for stories with commits
- [ ] Each story has Git badge (Epic 5 stories all committed)
- [ ] Click badge opens modal showing:
  - [ ] Commit messages
  - [ ] Commit hashes
  - [ ] Timestamps
  - [ ] Files changed

**Test Evidence Badges**
- [ ] 🟢 green badges show test status (should show "Tests: 272/272" passing)
- [ ] Click badge opens modal showing:
  - [ ] Total test count
  - [ ] Passing/failing breakdown
  - [ ] Last run timestamp
  - [ ] Failing test names (should be empty - all passing)

**Workflow History**
- [ ] Stories show workflow execution history in frontmatter
- [ ] Displays: dev-story, code-review, etc. with timestamps
- [ ] Gap detection works (flags missing workflows)
- [ ] 🟡 yellow warning if workflow gap detected

**VALIDATED Status**
- [ ] 🟢 green "✅ VALIDATED" badge when all evidence present:
  - [ ] Git commits exist
  - [ ] Tests passing
  - [ ] Workflow complete

---

## AI Coach Baseline

### Chat Interface

**Sidebar & Accessibility**
- [ ] Right sidebar visible in all views
- [ ] Chat input accepts text (44x44px minimum click target)
- [ ] "Send" button responsive
- [ ] Accessible via mouse clicks only (no keyboard required)

### Streaming Response
- [ ] First token appears in <200ms
- [ ] Tokens stream progressively (visible word-by-word)
- [ ] Chat history maintained during session
- [ ] Code blocks have "Copy" button

### Suggested Prompts
- [ ] Sidebar displays suggested prompts on load:
  - [ ] "What should I do next?"
  - [ ] "Did the AI agent complete Story X correctly?"
  - [ ] "What's the status of my current epic?"
  - [ ] "Show me the acceptance criteria for this story"
- [ ] Prompts are context-aware (change based on current story)
- [ ] Clicking prompt inserts text and generates response

### Project-Aware Q&A
- [ ] AI knows current phase: "Implementation"
- [ ] AI knows current epic: "Epic 5: AI Coach Integration"
- [ ] AI knows all stories and can answer: "What's Story 5.2 about?"
- [ ] AI provides workflow suggestions based on story state
- [ ] AI can validate agent outputs (asks about git/test evidence)

### AI Output Validation
- [ ] When asked "Did the AI complete Story X?", AI responds with:
  - [ ] Commit count and recency
  - [ ] Test count and status
  - [ ] Task completion status
  - [ ] Workflow execution history
  - [ ] Overall validation (✅ VALID or ⚠️ ISSUES DETECTED)

### Workflow Gap Detection
- [ ] AI detects when workflows are missing
- [ ] Example: "Story marked done but no code-review workflow found"
- [ ] AI suggests next workflow to run
- [ ] 🟡 yellow warning in gap-detection component

---

## Technical Baseline

### Error Handling

**Graceful Degradation**
- [ ] If Gemini API unavailable, dashboard still works
- [ ] Missing files show "Unknown" rather than errors
- [ ] Malformed YAML returns error message with file location
- [ ] Dashboard never crashes, always shows something

**Console**
- [ ] No JavaScript errors in browser console
- [ ] No warnings (except maybe deprecation notices)
- [ ] API responses include proper error format:
  ```json
  {
    "error": "not_found",
    "message": "Story not found",
    "details": "Story 99.99 does not exist",
    "status": 404
  }
  ```

### API Response Times

**Dashboard Endpoint** (`/api/dashboard?project_root=...`)
- [ ] Returns in <500ms
- [ ] Includes: project, breadcrumb, quick_glance, kanban data
- [ ] Cache used (mtime checking on artifacts)

**Evidence Endpoints** (`/api/git-evidence/<story_id>`, `/api/test-evidence/<story_id>`)
- [ ] Returns in <100ms
- [ ] Includes commit/test data with proper formatting
- [ ] Handles missing stories gracefully (404 with details)

**AI Chat Endpoint** (`/api/ai-chat`)
- [ ] Establishes SSE stream
- [ ] First token in <200ms
- [ ] Streams until complete
- [ ] Handles API errors gracefully

### Cache Behavior

**Cache Hit (Warm Cache)**
- [ ] After first load, refreshing with no file changes takes <100ms
- [ ] Cache age indicator shows in API response
- [ ] Project state maintained across requests

**Cache Invalidation**
- [ ] Modifying a story file invalidates only that story's cache
- [ ] Modifying sprint-status.yaml invalidates entire cache
- [ ] Manual "Refresh" button clears cache immediately
- [ ] Mtime checking prevents stale data (within 1-second granularity)

---

## Data Accuracy Baseline

### Story Parsing
- [ ] **Total stories detected:** 23 stories across Epics 0-5
- [ ] **Epic counts:**
  - Epic 0: 1 story (0.1)
  - Epic 1: 5 stories (1.1-1.5)
  - Epic 2: 4 stories (2.1-2.4)
  - Epic 3: 3 stories (3.1-3.3)
  - Epic 4: 2 stories (4.1-4.2)
  - Epic 5: 7 stories (5.1-5.7)
- [ ] **Task counts:** Each story has appropriate task count
- [ ] **Status accuracy:** Story statuses match sprint-status.yaml

### Git Correlation
- [ ] **Commits found for each story:** All stories have git references
- [ ] **No false positives:** No commits incorrectly attributed to stories
- [ ] **Recency detected:** Last commit time accurate within 1 minute

### Test Discovery
- [ ] **Test count accurate:** 272 total tests found
- [ ] **Pass/fail ratio:** All 272 passing (0 failing)
- [ ] **Test framework detected:** pytest and jest patterns recognized
- [ ] **Timestamp accurate:** Last test run time within 1 hour

### Phase Detection
- [ ] **Current phase:** "Implementation" (sprint-status.yaml present)
- [ ] **Epic detection:** Current epic is "Epic 5"
- [ ] **Story detection:** Latest story is "5.7"
- [ ] **Task detection:** Appropriate current task shown

---

## UI/UX Baseline

### Visual Design
- [ ] Dark theme (#1a1a1a background) applied globally
- [ ] Reduced visual clutter, generous whitespace
- [ ] No flashing or annoying animations
- [ ] Color-coded indicators (🟢🔴🟡) clearly visible
- [ ] Text readable (14px minimum font size)

### Responsiveness
- [ ] Click targets 44x44px minimum (NFR10)
- [ ] Buttons responsive to clicks
- [ ] Modals open instantly (<50ms)
- [ ] No janky or stuttering animations
- [ ] Hover states visible on interactive elements

### Accessibility
- [ ] All features accessible via mouse only
- [ ] No keyboard shortcuts required
- [ ] Modal overlays don't trap focus
- [ ] Can navigate without JavaScript enhancements

---

## Test Results Summary

**Date Tested:** ___________
**Tester:** ___________

### Performance Results
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Dashboard Startup | <500ms | ___ms | ✅/⚠️/❌ |
| Parse Time (warm) | <100ms | ___ms | ✅/⚠️/❌ |
| AI First Token | <200ms | ___ms | ✅/⚠️/❌ |
| View Transition | <100ms | ___ms | ✅/⚠️/❌ |
| Memory Usage | <100MB | ___MB | ✅/⚠️/❌ |

### Functional Results
| Feature | Expected | Actual | Status |
|---------|----------|--------|--------|
| Breadcrumb Nav | ✓ | ✓/✗ | ✅/❌ |
| Quick Glance | ✓ | ✓/✗ | ✅/❌ |
| Kanban Board | ✓ | ✓/✗ | ✅/❌ |
| Git Evidence | ✓ | ✓/✗ | ✅/❌ |
| Test Evidence | ✓ | ✓/✗ | ✅/❌ |
| AI Coach | ✓ | ✓/✗ | ✅/❌ |
| Project-Aware Q&A | ✓ | ✓/✗ | ✅/❌ |
| Workflow Gap Detection | ✓ | ✓/✗ | ✅/❌ |

### Issues Found
```
(None expected on BMAD Dash - this is just the checklist template)
```

---

## Notes for Echo-OS Testing

When testing on Echo-OS, compare:
1. **Does it match these performance numbers?** (May be different depending on project size)
2. **Do all features work?** (Same UI, same AI coaching)
3. **Are stories parsed correctly?** (Depends on Echo-OS' story ID format)
4. **Is data accurate?** (Git commits, test counts, status)
5. **Any console errors?** (Should be none)

If behavior differs from this baseline, it's either:
- **Expected:** Different project structure (ignore)
- **Bug:** Code doesn't handle Echo-OS format (fix needed)
- **Investigation Needed:** Ask which assumption was violated

