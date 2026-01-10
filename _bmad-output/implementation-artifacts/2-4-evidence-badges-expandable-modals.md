---
story_id: "2.4"
title: "Evidence Badges & Expandable Modals"
epic: "epic-2"
status: "done"
last_updated: "2026-01-10"
completed: "2026-01-10"
---

# Story 2.4: Evidence Badges & Expandable Modals

As a **user**,
I want **color-coded badges (🟢/🔴/🟡) that expand to show commit and test details**,
So that **I can click for proof instead of trusting checkmarks blindly**.

## Acceptance Criteria

- [x] **Visualize Status Badges**
    - [x] Show Git badge with color coding (🟢 commits exist, 🔴 no commits, 🟡 old)
    - [x] Show Test badge with format "Tests: 12/12" and color coding
    - [x] Show timestamp badge (e.g., "2h ago", "3 days ago")
    - [x] Display ✅ VALIDATED when Git 🟢 AND Tests 🟢 AND recent (<24hrs)
    - [x] Click target size is minimum 44x44px (NFR10)
    - [x] Badges meet 4.5:1 contrast ratio (NFR11)

- [x] **Git Evidence Modal**
    - [x] Clicking Git badge opens modal overlay
    - [x] Modal shows commit messages, hashes, timestamps, files changed
    - [x] Expansion feels instant (<50ms - NFR5)

- [x] **Test Evidence Modal**
    - [x] Clicking Test badge opens modal overlay
    - [x] Modal shows total/passing/failing counts
    - [x] Modal lists failing test names (if any)
    - [x] Modal shows last run time

- [x] **UX/UI Requirements**
    - [x] Modal overlays dashboard (not new page)
    - [x] Mouse-only operation works perfectly (NFR13)
    - [x] Progressive disclosure: badges always visible, details on demand (NFR15)

## Implementation Tasks

- [x] **Create Evidence Modal Component** (`frontend/js/components/evidence-modal.js`)
    - [x] Implement reusable modal structure with close button and overlay
    - [x] Add fetch logic for `/api/git-evidence` and `/api/test-evidence`
    - [x] Create renderers for commit lists and test results

- [x] **Create Evidence Badge Component** (`frontend/js/components/evidence-badge.js`)
    - [x] Implement badge rendering with color logic (Green/Red/Yellow)
    - [x] Add click handlers to trigger modal
    - [x] Ensure minimum click targets

- [x] **Update Quick Glance Component** (`frontend/js/components/quick-glance.js`)
    - [x] Integrate badges into the "Current Focus" section
    - [x] Pass story ID to badges for data fetching

- [x] **Main App Integration** (`frontend/js/app.js`)
    - [x] Initialize global modal container
    - [x] Handle modal open/close state

- [x] **Styling**
    - [x] Add badge and modal styles to `frontend/css/input.css` (Tailwind)
    - [x] Ensure dark mode compatibility

## Dev Notes

- **Tech Stack**: Vanilla JS (ES6 Modules), Tailwind CSS
- **API**: Use existing `/api/git-evidence/<story_id>` and `/api/test-evidence/<story_id>`
- **State**: Modals should fetch fresh data on open to ensure accuracy (no stale cache)
- **Accessibility**: Ensure modals trap focus and can be closed with ESC key (good practice even if mouse-required)

## Completion Notes

- **Parser Fix**: Also fixed `bmad_parser.py` to parse flat `development_status` format in `sprint-status.yaml`
- **Files Created**: `evidence-modal.js`, `evidence-badge.js`
- **Files Modified**: `quick-glance.js`, `app.js`, `input.css`, `bmad_parser.py`
- **Tests**: All 175 tests passing
