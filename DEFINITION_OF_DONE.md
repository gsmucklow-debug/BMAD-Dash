# Definition of Done - BMAD Dash

**Last Updated:** 2026-01-13
**Updated After:** Epic 5 Retrospective - Integration Validation Gap

A story is considered **DONE** only when ALL of the following criteria are met.

---

## Code Quality

- [ ] Code is written and reviewed
- [ ] Code follows project conventions (naming, structure, file organization)
- [ ] No hardcoded values (except where necessary with comments explaining why)
- [ ] No dead code or debug statements left in
- [ ] Error handling is complete (no silent failures)
- [ ] Logging is in place for debugging (Python logging, not print statements)

## Testing

- [ ] All acceptance criteria have test coverage
- [ ] Unit tests pass locally (100% pass rate required)
- [ ] Integration tests pass (if applicable to the story)
- [ ] No new test failures or regressions (all existing tests still pass)
- [ ] Test code is clean and maintainable

**Specific Requirements:**
- Backend (Python): pytest tests in `/tests/` directory
- Frontend (JavaScript): Jest tests alongside components
- Both: Minimum 80% code coverage for critical paths

## Code Review

- [ ] Code reviewed by another team member (or lead)
- [ ] Reviewer approved changes
- [ ] All review comments resolved (not just marked as resolved)
- [ ] No console errors or warnings
- [ ] No security issues (XSS, injection, path traversal, etc.)

## End-to-End Verification (NEW - Critical Addition)

**This is the most important change from Epic 5 learning. Unit tests are NOT sufficient.**

- [ ] **Feature works in the actual application UI**
  - Not just: "unit test passes"
  - But: "I can open BMAD Dash and see/use the feature"
- [ ] **Manual testing completed in live dashboard**
  - Test on project with at least one real story
  - Verify feature works with actual data
  - Take screenshot or record interaction
- [ ] **User interaction verified**
  - Not just: "API endpoint works"
  - But: "Frontend calls the endpoint and displays result"
  - "User can click button and see expected outcome"
- [ ] **Performance measured in context**
  - For caching stories: show Dashboard load time, not just cache unit test speed
  - For UI stories: show actual render time, not just component test speed
  - For API stories: test with real data payload, not minimal mock data

### Red Flags for E2E Verification Failure

❌ **Do NOT mark story done if:**
- [ ] "Unit tests pass but I haven't manually tested it"
- [ ] "API endpoint works but I haven't tested it through the UI"
- [ ] "Cache is fast in tests but I don't know if dashboard uses it"
- [ ] "Performance improved on paper but I didn't measure actual impact"
- [ ] "Feature works for my test case but might break for edge cases"

### How to Document E2E Verification

In the story file, add evidence:
```markdown
## E2E Verification
- ✅ Tested on BMAD Dash project
- ✅ Feature works as expected
- ✅ Dashboard loads in 450ms (acceptable)
- ✅ No console errors
- ✅ Screenshot: [feature_screenshot.png](link)
```

## Performance

- [ ] Story meets its NFR (Non-Functional Requirement) targets
  - Check story file for performance targets
  - Common targets: <500ms load, <100ms operation, <200ms first token (AI)
- [ ] Performance measured in REAL dashboard context (not isolated tests)
- [ ] Performance degradation minimal (not slower than before)

## Documentation

- [ ] Story file updated with current status and completion details
- [ ] Code comments added where logic is non-obvious
- [ ] No "TODO" comments left (either implement or remove)
- [ ] README updated if new features affect user workflow

## Deployment Readiness

- [ ] Story doesn't break existing features
- [ ] Configuration is complete (`.env`, settings, etc.)
- [ ] No missing dependencies or setup requirements
- [ ] Backward compatible (won't break if deployed alongside other work)

## Story File Record

- [ ] Story status set to "done"
- [ ] Completion date recorded
- [ ] Dev notes documented (what was learned, challenges, solutions)
- [ ] Git commits referenced in story file
- [ ] Test evidence linked
- [ ] Review feedback addressed
- [ ] Workflows documented (dev-story, code-review completed)

---

## Definition of Done for Different Story Types

### UI/Frontend Stories

**Additional Requirements:**
- [ ] Feature tested in all view modes (Dashboard, Timeline, List)
- [ ] Feature works with mouse clicks only (no keyboard required)
- [ ] Responsive design (works with different window sizes)
- [ ] Dark theme applied consistently
- [ ] Click targets meet 44x44px minimum (NFR10)
- [ ] Contrast ratio meets 4.5:1 (NFR11 - WCAG AA standard)

### Backend/API Stories

**Additional Requirements:**
- [ ] API endpoint responds in required time (<100ms typical)
- [ ] Error responses include proper format: `{error, message, details, status}`
- [ ] API tested with real data (not just mocks)
- [ ] CORS headers correct (should be disabled for localhost)
- [ ] Rate limiting or timeouts configured

### Caching/Performance Stories

**Additional Requirements (Critical):**
- [ ] Performance improvement verified in actual dashboard load (not just unit test)
- [ ] Network tab shows reduced requests/payload (screenshot evidence)
- [ ] Warm cache tested (should be significantly faster)
- [ ] Cache invalidation strategy documented and tested
- [ ] Performance target met: measurement in milliseconds documented

### Integration Stories (Connecting Components)

**Additional Requirements:**
- [ ] All connected components tested together
- [ ] Data flows correctly between components
- [ ] No missing data or mismatches between systems
- [ ] User sees unified, working feature (not broken components)

### AI/LLM Stories

**Additional Requirements:**
- [ ] AI responses tested with various project states
- [ ] Streaming works (first token latency <200ms)
- [ ] Error handling when API unavailable
- [ ] System prompt verified (AI has correct context)
- [ ] Security verified (no API key leakage, input sanitized)

---

## Sign-Off

Once a story meets ALL Definition of Done criteria:

1. **Developer:** "This story is done"
   - All criteria above met
   - E2E verification documented
   - Story file updated

2. **Code Reviewer:** "Code approved"
   - Reviews code quality, tests, and E2E evidence
   - Verifies no safety/security issues
   - Comments on findings

3. **QA/Tester:** "Feature verified working"
   - Independently tests feature in dashboard
   - Confirms it works as intended
   - Logs any issues

4. **Scrum Master:** "Story marked DONE"
   - Updates sprint-status.yaml
   - Confirms all criteria met
   - Story moves to "done" status

---

## Why This Definition of Done Matters

**Epic 5 Learning:** Stories marked "done" passed unit tests but didn't work end-to-end:
- Story 5.2: AI context wasn't actually injected into prompts
- Story 5.4: Cache existed but dashboard didn't use it
- Result: Failed review, 3 recovery stories needed

**The Fix:** E2E verification catches these gaps before they become production issues.

**Key Principle:** The only way to know a feature works is to use it in the actual system with real data.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | **Initial Definition of Done**<br/>Added E2E Verification requirement (new in Epic 5)<br/>Added performance measurement in context<br/>Added type-specific requirements |

