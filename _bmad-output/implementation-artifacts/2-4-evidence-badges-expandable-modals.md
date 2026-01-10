---
story_id: "2.4"
title: "Evidence Badges & Expandable Modals"
epic: "epic-2"
status: "in-progress"
last_updated: "2026-01-10"
---

# Story 2.4: Evidence Badges & Expandable Modals

As a **user**,
I want **color-coded badges (🟢/🔴/🟡) that expand to show commit and test details**,
So that **I can click for proof instead of trusting checkmarks blindly**.

## Acceptance Criteria

- [ ] **Visualize Status Badges**
    - [ ] Show Git badge with color coding (🟢 commits exist, 🔴 no commits, 🟡 old)
    - [ ] Show Test badge with format "Tests: 12/12" and color coding
    - [ ] Show timestamp badge (e.g., "2h ago", "3 days ago")
    - [ ] Display ✅ VALIDATED when Git 🟢 AND Tests 🟢 AND recent (<24hrs)
    - [ ] Click target size is minimum 44x44px (NFR10)
    - [ ] Badges meet 4.5:1 contrast ratio (NFR11)

- [ ] **Git Evidence Modal**
    - [ ] Clicking Git badge opens modal overlay
    - [ ] Modal shows commit messages, hashes, timestamps, files changed
    - [ ] Expansion feels instant (<50ms - NFR5)

- [ ] **Test Evidence Modal**
    - [ ] Clicking Test badge opens modal overlay
    - [ ] Modal shows total/passing/failing counts
    - [ ] Modal lists failing test names (if any)
    - [ ] Modal shows last run time

- [ ] **UX/UI Requirements**
    - [ ] Modal overlays dashboard (not new page)
    - [ ] Mouse-only operation works perfectly (NFR13)
    - [ ] Progressive disclosure: badges always visible, details on demand (NFR15)

## Implementation Tasks

- [ ] **Create Evidence Modal Component** (`frontend/js/components/evidence-modal.js`)
    - [ ] Implement reusable modal structure with close button and overlay
    - [ ] Add fetch logic for `/api/git-evidence` and `/api/test-evidence`
    - [ ] Create renderers for commit lists and test results

- [ ] **Create Evidence Badge Component** (`frontend/js/components/evidence-badge.js`)
    - [ ] Implement badge rendering with color logic (Green/Red/Yellow)
    - [ ] Add click handlers to trigger modal
    - [ ] Ensure minimum click targets

- [ ] **Update Quick Glance Component** (`frontend/js/components/quick-glance.js`)
    - [ ] Integrate badges into the "Current Focus" section
    - [ ] Pass story ID to badges for data fetching

- [ ] **Main App Integration** (`frontend/js/app.js`)
    - [ ] Initialize global modal container
    - [ ] Handle modal open/close state

- [ ] **Styling**
    - [ ] Add badge and modal styles to `frontend/css/input.css` (Tailwind)
    - [ ] Ensure dark mode compatibility

## Dev Notes

- **Tech Stack**: Vanilla JS (ES6 Modules), Tailwind CSS
- **API**: Use existing `/api/git-evidence/<story_id>` and `/api/test-evidence/<story_id>`
- **State**: Modals should fetch fresh data on open to ensure accuracy (no stale cache)
- **Accessibility**: Ensure modals trap focus and can be closed with ESC key (good practice even if mouse-required)
