# Code Review: Story 3.1 & Bug Fixes

**Story**: 3.1 Hash-Based Router & View Mode Switching
**Status**: Review
**Date**: 2026-01-10

## Summary
The implementation of the Hash-Based Router and View Switcher meets the core acceptance criteria and NFRs. The 4 associated bug fixes in the backend and frontend appear correct and addressed the described issues. However, an adversarial review has identified 4 specific issues that need to be addressed before merging.

## Findings

### 1. Router Race Condition (UX/Stability)
**Severity**: Medium
**Location**: `frontend/js/router.js`
**Issue**: The `handleRoute` method uses `setTimeout` to delay rendering for 80ms to allow for a fade-out animation. However, it does not cancel any pending timeouts. If a user triggers multiple hash changes rapidly (e.g., clicking "Dashboard" then "Timeline" quickly), multiple timeouts will be scheduled, leading to multiple renders overlapping and potential state inconsistency.
**Recommendation**: Store the timeout ID and clear any existing timeout at the start of `handleRoute`.

### 2. Hardcoded Project Root (Configuration)
**Severity**: Low
**Location**: `frontend/js/app.js`
**Issue**: `DEFAULT_PROJECT_ROOT` is hardcoded to `'F:/BMAD Dash'`. While `localStorage` overrides this, shipping hardcoded absolute paths specific to one environment is poor practice and can lead to confusion for other users or environments.
**Recommendation**: Set `DEFAULT_PROJECT_ROOT` to an empty string or a relative path, or require the user to input it on first load if not found in local storage.

### 3. Coupled Transition Timing (Maintainability)
**Severity**: Low
**Location**: `frontend/js/router.js`
**Issue**: The JavaScript hardcodes `80` ms for the transition delay, while the CSS injection (via `style.transition`) hardcodes `0.08s`. These values are implicitly coupled. If a developer changes the CSS timing without updating the JS constant (or vice-versa), the animation logic will break (rendering before fade-out completes, or lagging).
**Recommendation**: Define a constant for the transition duration and use it to generate the CSS string and the timeout value dynamically.

### 4. Shadow Test Coverage (Testing)
**Severity**: Medium
**Location**: `tests/test_router.py`
**Issue**: The current tests for `Router` (e.g., `test_router_has_handleRoute_method`) only verify that the method *exists* as a string in the file. They do **not** verify the behavior (i.e., that `handleRoute` actually executes the callback associated with the hash). Code could be broken logic-wise but still pass these tests.
**Recommendation**: Add a test that actually imports the class (if possible in the test environment) or mocks the behavior verification more deeply. Since we are testing JS with Pytest, we are limited, but we should at least verify the logic structure via regex or syntax checking, or verify the *logic* in a JS test runner. (Given the constraint, we can improve the regex check to ensure `this.routes[hash]()` or similar call exists).

## Verified Items
- ✅ **Bug Fix 1**: "Last Completed" sorting logic correctly handles date and ID.
- ✅ **Bug Fix 2**: Breadcrumb epic detection correctly prioritizes active work.
- ✅ **Bug Fix 3**: Quick Glance handles empty states gracefully.
- ✅ **Bug Fix 4**: Review status is correctly included in "Current" story logic.
- ✅ **Security**: `escapeHtml` is properly used in `quick-glance.js`.
- ✅ **Performance**: NFR targets (500ms load, <100ms transition) are addressed code-wise.

## Action Items
1. Fix Router race condition.
2. Remove hardcoded path.
3. Decouple transition timing constants.
4. (Optional) Improve test robustness for JS logic.
