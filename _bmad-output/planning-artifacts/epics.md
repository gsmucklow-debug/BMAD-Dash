---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: ['f:/BMAD Dash/_bmad-output/planning-artifacts/prd.md', 'f:/BMAD Dash/_bmad-output/planning-artifacts/architecture.md', 'f:/BMAD Dash/_bmad-output/planning-artifacts/ux-design-specification.md']
status: 'complete'
completedAt: '2026-01-09'
---

# BMAD Dash - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for BMAD Dash, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

**Project Orientation & Navigation (FR1-FR8):**
- FR1: View hierarchical project context (Project → Phase → Epic → Story → Task) in breadcrumb navigation
- FR2: View temporal orientation (Done | Current | Next story) in Quick Glance Bar
- FR3: View current phase detection (Analysis, Planning, Solutioning, Implementation, or Unknown)
- FR4: View current epic and story position within the project
- FR5: View current task position within active story
- FR6: Navigate to different epics or stories from the dashboard
- FR7: See visual progress indicators for epic completion (e.g., "3/7 stories complete")
- FR8: See visual progress indicators for story completion (e.g., "6/10 tasks complete")

**Quality Validation & Trust (FR9-FR19):**
- FR9: View Git commit validation status for each story
- FR10: View test execution status (pass/fail count) for each story
- FR11: View timestamp of last test execution for each story
- FR12: Expand Git validation badges to see actual commit messages referencing the story
- FR13: Expand test validation badges to see detailed test results
- FR14: View workflow execution history (which BMAD workflows were run)
- FR15: See overall validation status (✅ VALIDATED when Git + Tests + Workflows complete)
- FR16: View color-coded status indicators (🟢 green, 🔴 red, 🟡 yellow)
- FR17: System detects Git commits that reference story identifiers (e.g., "story-1.3")
- FR18: System discovers and parses test results from common frameworks (pytest, jest)
- FR19: System detects workflow gaps (e.g., dev-story complete but code-review not run)

**AI Coach & Assistance (FR20-FR30):**
- FR20: Access AI coach chat interface from anywhere in the dashboard (right sidebar)
- FR21: Ask project-aware questions to the AI coach (knows current phase, epic, story)
- FR22: Receive AI-suggested next workflows based on current project state
- FR23: View suggested prompts for common questions (displayed in AI coach panel)
- FR24: Copy BMAD workflow commands with one click from AI suggestions
- FR25: View streaming AI responses (tokens appear as generated, not after full response)
- FR26: View AI validation of agent outputs (comparing story claims vs. Git/test reality)
- FR27: Receive AI-detected workflow gap warnings
- FR28: System integrates with current BMAD Method documentation
- FR29: System detects BMAD Method version updates and refreshes documentation context
- FR30: System provides accurate workflow suggestions based on latest BMAD Method best practices

**View Management & Cognitive Adaptation (FR31-FR38):**
- FR31: Switch between Dashboard view (full context with breadcrumbs, Quick Glance, Kanban)
- FR32: Switch to Timeline view (visual workflow history over time)
- FR33: Switch to List view (minimal display for brain fog days)
- FR34: View stories organized in Kanban columns (TODO, IN PROGRESS, REVIEW, COMPLETE)
- FR35: See unified Action Cards combining Story + Task + Command in single UI element
- FR36: Manually trigger dashboard refresh (re-parse BMAD artifacts and update display)
- FR37: System persists user's last selected view mode across sessions
- FR38: System maintains 60fps performance during view transitions

**BMAD Artifact Intelligence (FR39-FR48):**
- FR39: System parses sprint-status.yaml to extract project status and story states
- FR40: System parses epics.md to extract epic definitions and story lists
- FR41: System parses individual story files to extract tasks, acceptance criteria, and status
- FR42: System detects current BMAD phase from artifact analysis
- FR43: System identifies current epic from project-level indicators
- FR44: System identifies current story from in-progress markers or most recent activity
- FR45: System identifies current task within active story
- FR46: System tracks file modification timestamps for stories and artifacts
- FR47: System correlates Git commits to specific stories based on commit messages
- FR48: System detects test files associated with stories

**Workflow Execution Support (FR49-FR54):**
- FR49: View three-layer action guidance (Story level, Task level, Command level)
- FR50: Copy suggested BMAD workflow commands to clipboard with one click
- FR51: View context-specific commands based on current story state
- FR52: View workflow history showing execution sequence
- FR53: System suggests correct next workflow based on story state and BMAD Method
- FR54: System detects missing workflow steps in the execution sequence

**User Experience & Accessibility (FR55-FR60):**
- FR55: View dashboard in dark theme (reduced visual fatigue)
- FR56: Interact with all features via mouse clicks (no keyboard shortcut requirements)
- FR57: View high-contrast color-coded indicators (green/red/yellow distinctly visible)
- FR58: Expand details on demand (progressive disclosure)
- FR60: System maintains responsive UI during Git parsing and test discovery operations
- FR61: Execute story status transitions (e.g., ready-for-dev -> in-progress -> review -> done) via AI coach suggested actions

### Non-Functional Requirements

**Performance (NFR1-NFR9):**
- NFR1: Dashboard startup (page load to interactive) must complete in <500ms
- NFR2: BMAD artifact parsing must complete in <500ms
- NFR3: Phase detection algorithm must execute in <100ms
- NFR4: View transitions must maintain 60fps with <100ms completion time
- NFR5: Modal expansion must feel instant (<50ms response time)
- NFR6: AI coach streaming must deliver first token within <200ms
- NFR7: Manual refresh must complete in <300ms
- NFR8: Frontend memory usage must remain <100MB
- NFR9: No memory leaks during view switching or modal operations

**Accessibility (NFR10-NFR18):**
- NFR10: Minimum click target size of 44x44px
- NFR11: Color-coded indicators must meet 4.5:1 contrast ratio
- NFR12: Dark theme must be default and enforced
- NFR13: All functionality accessible via mouse clicks only
- NFR14: Minimum 14px font size for readability
- NFR15: Progressive disclosure keeps overview visible at all times
- NFR16: View mode selection persists across sessions
- NFR17: No time-limited interactions
- NFR18: No flashing or strobing animations

**Reliability & Graceful Degradation (NFR19-NFR25):**
- NFR19: Core Layer functions without AI coach operational
- NFR20: Validation Layer functions without AI coach operational
- NFR21: Core navigation and validation work if Gemini API unavailable
- NFR22: Falls back to file modification time if Git commit format unexpected
- NFR23: Allows manual test status entry if test discovery fails
- NFR24: Shows "Unknown" state rather than error for malformed artifacts
- NFR25: Never loses user's view mode preference due to errors

**Maintainability (NFR26-NFR31):**
- NFR26: Codebase uses vanilla JavaScript/CSS (no framework dependency)
- NFR27: Backend uses Flask with minimal dependencies
- NFR28: No complex build pipeline required
- NFR29: Code architecture supports AI coding agent assistance
- NFR30: Configuration is file-based (no database setup)
- NFR31: Deployment is localhost-only (no server infrastructure)

**Integration (NFR32-NFR37):**
- NFR32: Parses current BMAD Method artifact formats
- NFR33: Detects and adapts to BMAD Method version changes
- NFR34: Integrates with BMAD Method documentation for AI coach context
- NFR35: Supports Gemini 3 Flash API for AI coach functionality
- NFR36: Executes Git commands for commit correlation
- NFR37: Detects common test frameworks (pytest, jest)

### Additional Requirements

**From Architecture:**

- **Project Initialization (Story 0.1 Priority):** Manual project setup (no starter template) - create complete directory structure, initialize requirements.txt and package.json, set up .env template
- **Data Models:** Python dataclasses for in-memory models (Project, Epic, Story, Task, GitEvidence, GitCommit, TestEvidence)
- **Caching:** In-memory cache with file mtime invalidation (automatic freshness checking)
- **API Pattern:** Simple REST JSON endpoints (5 routes total: dashboard, git-evidence, test-evidence, ai-chat, refresh)
- **Frontend State:** Stateless (localStorage for view mode preference only)
- **Frontend Routing:** Hash-based routing for view modes (#/dashboard, #/timeline, #/list)
- **Component Architecture:** Vanilla JS modules (one file per component)
- **Error Handling:** Standardized JSON error format with details
- **Environment Config:** .env file for Gemini API key
- **Naming Conventions:** Python snake_case, JavaScript camelCase, API kebab-case
- **Project Structure:** 43 files defined in complete directory tree
- **No Authentication:** Localhost-only tool, no login required
- **No Database:** File-based parsing only
- **Server-Sent Events:** For AI streaming responses

**From UX Design:**

- **Dark Theme Mandatory:** Deep gray background (#1a1a1a), muted accents for reduced cognitive load
- **Color-Coded Status Without Reading:** 🟢/🔴/🟡 badges for instant status scanning
- **Progressive Disclosure:** Breadcrumbs + Quick Glance always visible, details expandable on demand
- **Generous Breathing Room:** Whitespace between elements to reduce visual density
- **Temporal Focus:** Quick Glance Bar shows Done | Current | Next (three states only)
- **One-Click Drill-Down:** Modal overlays for Git/Test evidence (not new pages)
- **Instant Mode Switching:** View mode transitions <100ms with smooth animations
- **Persistent State:** View mode preference saved in localStorage
- **No Keyboard Shortcuts:** Mouse-only operation to reduce memory burden
- **Calm Aesthetic:** Reduced stimulation, no time pressure UI elements, gentle animations
- **Three View Modes:**
  - Dashboard (full context - default): Breadcrumbs + Quick Glance + Kanban + AI chat
  - Timeline (workflow history): Visual history of BMAD workflow execution over time
  - List (minimal for brain fog): Current task + next action only, minimal visual elements
- **Tailwind CSS v3+:** JIT mode, dark mode via 'class' strategy, custom BMAD-specific utilities

### FR Coverage Map

**Epic 0: Project Foundation**
- Architecture requirement: Manual project setup with 43-file structure

**Epic 1: Core Orientation System (18 FRs)**
- FR1: View hierarchical breadcrumb navigation (Project → Phase → Epic → Story → Task)
- FR2: View Quick Glance Bar (Done | Current | Next temporal orientation)
- FR3: View current phase detection
- FR4: View current epic and story position
- FR5: View current task position within active story
- FR6: Navigate to different epics/stories from dashboard
- FR7: See visual progress indicators for epic completion
- FR8: See visual progress indicators for story completion
- FR39: System parses sprint-status.yaml
- FR40: System parses epics.md
- FR41: System parses individual story files
- FR42: System detects current BMAD phase
- FR43: System identifies current epic
- FR44: System identifies current story
- FR45: System identifies current task
- FR46: System tracks file modification timestamps
- FR47: System correlates Git commits to stories
- FR48: System detects test files associated with stories
- FR55: View dashboard in dark theme
- FR59: System loads dashboard in <500ms
- FR60: System maintains responsive UI during parsing

**Epic 2: Quality Validation & Trust (14 FRs)**
- FR9: View Git commit validation status for each story
- FR10: View test execution status (pass/fail count)
- FR11: View timestamp of last test execution
- FR12: Expand Git badges to see commit messages
- FR13: Expand test badges to see detailed results
- FR14: View workflow execution history
- FR15: See overall validation status (✅ VALIDATED)
- FR16: View color-coded status indicators (🟢/🔴/🟡)
- FR17: System detects Git commits referencing story IDs
- FR18: System discovers and parses test results (pytest, jest)
- FR19: System detects workflow gaps
- FR56: Interact via mouse clicks only
- FR57: View high-contrast color-coded indicators
- FR58: Expand details on demand (progressive disclosure)

**Epic 3: Multi-View Dashboard (8 FRs)**
- FR31: Switch to Dashboard view (full context)
- FR32: Switch to Timeline view (workflow history)
- FR33: Switch to List view (minimal for brain fog)
- FR34: View stories in Kanban columns (TODO/IN PROGRESS/REVIEW/COMPLETE)
- FR35: See unified Action Cards (Story + Task + Command)
- FR36: Manually trigger dashboard refresh
- FR37: System persists view mode across sessions
- FR38: System maintains 60fps during view transitions

**Epic 4: Zero-Friction Execution (6 FRs)**
- FR49: View three-layer action guidance (Story/Task/Command)
- FR50: Copy BMAD workflow commands with one click
- FR51: View context-specific commands based on story state
- FR52: View workflow history showing execution sequence
- FR53: System suggests correct next workflow
- FR54: System detects missing workflow steps

**Epic 5: AI Coach Integration (11 FRs)**
- FR20: Access AI coach chat from anywhere (right sidebar)
- FR21: Ask project-aware questions to AI coach
- FR22: Receive AI-suggested next workflows
- FR23: View suggested prompts for common questions
- FR24: Copy BMAD workflow commands from AI suggestions
- FR25: View streaming AI responses
- FR26: View AI validation of agent outputs
- FR27: Receive AI workflow gap warnings
- FR28: System integrates with BMAD Method documentation
- FR29: System detects BMAD Method version updates
- FR30: System provides accurate workflow suggestions

**Coverage Summary:**
- Total FRs: 60
- Mapped to Epics: 57 explicit mappings
- Cross-cutting (appear in multiple): 3 (dark theme, accessibility, performance)

## Epic List

### Epic 0: Project Foundation
**User Outcome:** Development environment is ready, project structure exists, and basic infrastructure is functional. Developers can begin implementing features.

**What Users Can Accomplish:** Set up the complete BMAD Dash project from scratch with all necessary files, dependencies, and configurations in place.

**FRs Covered:** Architecture requirements (manual project setup with 43-file structure)

---

### Epic 1: Core Orientation System
**User Outcome:** Users can instantly see where they are in their BMAD project (phase, epic, story, task) and understand temporal context (Done | Current | Next).

**What Users Can Accomplish:**
- Open BMAD Dash and within 3 seconds know exactly where they are in their project
- See breadcrumb navigation showing Project → Phase → Epic → Story → Task hierarchy
- View Quick Glance Bar showing Done | Current | Next stories
- Trust that the dashboard accurately detects project phase and current work
- Navigate dark-themed interface optimized for cognitive load reduction

**FRs Covered:** FR1-FR8, FR39-FR48, FR55, FR59-FR60 (18 FRs)

---

### Epic 2: Quality Validation & Trust
**User Outcome:** Users can verify AI agent work through objective evidence (Git commits, test results) and trust completion status without manual checking.

**What Users Can Accomplish:**
- View color-coded validation badges (🟢/🔴/🟡) showing Git commits exist
- See test execution status with pass/fail counts and timestamps
- Click evidence badges to expand and see actual commit messages and test details
- Verify workflow execution history (which BMAD workflows were run)
- Trust ✅ VALIDATED status when all quality checks pass
- Identify workflow gaps (e.g., story marked done but no code review executed)

**FRs Covered:** FR9-FR19, FR56-FR58 (14 FRs)

---

### Epic 3: Multi-View Dashboard
**User Outcome:** Users can adapt the dashboard interface to their current cognitive state, switching between full context, visual timeline, or minimal list view.

**What Users Can Accomplish:**
- Switch to Dashboard view for full Kanban board with all stories visible
- Switch to Timeline view to see visual workflow history over time
- Switch to List view for minimal cognitive load on brain fog days
- See stories organized in Kanban columns (TODO, IN PROGRESS, REVIEW, COMPLETE)
- View unified Action Cards combining Story + Task + Command
- Manually refresh dashboard to re-parse BMAD artifacts
- Have view mode preference persist across browser sessions

**FRs Covered:** FR31-FR38 (8 FRs)

---

### Epic 4: Zero-Friction Execution
**User Outcome:** Users can immediately execute the next workflow step with one-click command copying, eliminating "what do I do next?" decision paralysis.

**What Users Can Accomplish:**
- View three-layer action guidance (Story level, Task level, Command level)
- Copy BMAD workflow commands to clipboard with one click
- See context-specific command suggestions based on current story state
- View workflow history showing execution sequence
- Receive intelligent suggestions for the correct next workflow
- Identify missing workflow steps automatically

**FRs Covered:** FR49-FR54 (6 FRs)

---

### Epic 5: AI Coach Integration
**User Outcome:** Users can get project-aware assistance, validate AI agent outputs, and receive intelligent workflow suggestions through Gemini 3 Flash integration.

**What Users Can Accomplish:**
- Access AI coach chat from anywhere via right sidebar
- Ask project-aware questions (AI knows current phase, epic, story)
- View streaming AI responses with <200ms first token latency
- Receive AI-suggested next workflows based on project state
- See suggested prompts for common questions
- Copy BMAD workflow commands from AI suggestions with one click
- Get AI validation of agent outputs (comparing story claims vs. Git/test reality)
- Receive AI-detected workflow gap warnings
- Benefit from BMAD Method documentation integration for accurate suggestions

**FRs Covered:** FR20-FR30 (11 FRs)

## Epic 0: Project Foundation

**User Outcome:** Development environment is ready, project structure exists, and basic infrastructure is functional.

### Story 0.1: Project Scaffold & Development Environment Setup

As a **developer**,
I want **the complete BMAD Dash project structure created with all necessary files, dependencies, and configurations**,
So that **I can begin implementing features immediately without manual setup**.

**Acceptance Criteria:**

**Given** the BMAD Dash project doesn't exist yet
**When** the project scaffold is executed
**Then** the complete 43-file directory structure is created following the architecture document
**And** `requirements.txt` contains all Python dependencies (Flask>=3.0.0, google-generativeai>=0.3.0, PyYAML>=6.0, GitPython>=3.1.40, python-dotenv>=1.0.0, pytest>=7.4.0, pytest-flask>=1.3.0)
**And** `package.json` contains Tailwind CSS devDependencies with build/watch scripts
**And** `tailwind.config.js` is configured with darkMode: 'class', custom colors, and BMAD-specific utilities
**And** `.env.template` exists with placeholder for GEMINI_API_KEY
**And** `.gitignore` excludes `.env`, `frontend/css/output.css`, and `__pycache__`
**And** `README.md` contains project description and setup instructions
**And** `backend/__init__.py` and all module `__init__.py` files exist
**And** `frontend/index.html` exists with dark theme structure and Tailwind CSS link
**And** running `pip install -r requirements.txt` succeeds
**And** running `npm install` succeeds
**And** running `npm run build:css` generates `frontend/css/output.css`
**And** all directory paths match the architecture document exactly

## Epic 1: Core Orientation System

**User Outcome:** Users can instantly see where they are in their BMAD project (phase, epic, story, task) and understand temporal context (Done | Current | Next).

### Story 1.1: BMAD Artifact Parser & Data Models

As a **developer**,
I want **Python dataclasses and parsers that can read BMAD artifacts (sprint-status.yaml, epics.md, story files)**,
So that **the backend can extract project state and provide it to the frontend**.

**Acceptance Criteria:**

**Given** a BMAD project with `_bmad-output/` artifacts
**When** the BMAD parser is executed with a project root path
**Then** `Project` dataclass is populated with name and detected phase
**And** `Epic` dataclasses are created from epics.md frontmatter
**And** `Story` dataclasses are created from story files in `_bmad-output/implementation/`
**And** `Task` dataclasses are extracted from story file task lists
**And** YAML frontmatter is correctly parsed from all artifact files
**And** Markdown content is separated from frontmatter
**And** File modification timestamps are tracked for all artifacts
**And** Malformed YAML returns graceful error with file path, not crash
**And** Missing files return "Unknown" state rather than exception
**And** Parser completes in <200ms for projects with 100 stories (FR59 requirement)
**And** All 7 dataclasses defined: Project, Epic, Story, Task, GitEvidence, GitCommit, TestEvidence

### Story 1.2: Phase Detection Algorithm

As a **user**,
I want **the dashboard to automatically detect my current BMAD phase**,
So that **I know if I'm in Analysis, Planning, Solutioning, or Implementation without checking files manually**.

**Acceptance Criteria:**

**Given** a BMAD project with artifacts
**When** phase detection runs
**Then** returns "Analysis" if only brainstorming/PRD files exist
**And** returns "Planning" if PRD complete but no Architecture
**And** returns "Solutioning" if Architecture exists but no epics/stories
**And** returns "Implementation" if sprint-status.yaml and story files exist
**And** returns "Unknown" if artifact structure doesn't match expected patterns
**And** detection completes in <100ms (NFR3 requirement)
**And** phase is stored in Project dataclass for frontend access

### Story 1.3: Flask API - Dashboard Endpoint

As a **user**,
I want **a backend API that serves complete dashboard data**,
So that **the frontend can display my project state without parsing files itself**.

**Acceptance Criteria:**

**Given** Flask server is running on localhost:5000
**When** GET request to `/api/dashboard?project_root=/path/to/project`
**Then** returns JSON with project, breadcrumb, quick_glance, kanban data
**And** response includes project name and detected phase
**And** breadcrumb data shows Project  Phase  Epic  Story  Task hierarchy
**And** quick_glance shows Done story, Current story, Next story
**And** kanban data organizes stories by status (TODO/IN PROGRESS/REVIEW/COMPLETE)
**And** returns 400 error if project_root parameter missing
**And** returns 404 error if project path doesn't exist
**And** returns 500 error if parsing fails, with error details in response
**And** cache is used (file mtime checking) to serve <500ms (NFR1 requirement)
**And** CORS is disabled (Flask default for localhost)

### Story 1.4: Frontend Shell & Breadcrumb Navigation

As a **user**,
I want **a dark-themed SPA that shows my project hierarchy in breadcrumbs**,
So that **I can instantly see where I am: Project  Phase  Epic  Story  Task**.

**Acceptance Criteria:**

**Given** the frontend is loaded at localhost:5000
**When** the page renders
**Then** `index.html` is served with dark theme (#1a1a1a background)
**And** breadcrumb component displays at top of page
**And** breadcrumb shows Project  Phase  Epic  Story  Task with arrows
**And** current level in breadcrumb is highlighted
**And** Tailwind CSS classes are applied correctly (dark theme)
**And** `app.js` fetches `/api/dashboard` on page load
**And** `breadcrumb.js` component renders navigation from API data
**And** page loads and becomes interactive in <500ms (NFR1 requirement)
**And** no JavaScript errors in console
**And** ES6 modules load correctly (no transpilation needed)

### Story 1.5: Quick Glance Bar & Progress Indicators

As a **user**,
I want **a Quick Glance Bar showing Done | Current | Next stories with progress bars**,
So that **I understand my temporal position in the project at a glance**.

**Acceptance Criteria:**

**Given** the dashboard is loaded
**When** Quick Glance Bar renders below breadcrumbs
**Then** displays three sections: Done | Current | Next
**And** Done section shows title of last completed story
**And** Current section shows title of in-progress story (highlighted)
**And** Next section shows title of next TODO story
**And** Epic progress bar shows "3/7 stories complete" format
**And** Story progress bar shows "6/10 tasks complete" format
**And** progress bars use VSCode-style visual indicators
**And** generous whitespace between sections (UX requirement)
**And** temporal focus is instantly scannable (<3 seconds to orient)
**And** component renders in <100ms after data fetch (NFR4 requirement)

## Epic 2: Quality Validation & Trust

**User Outcome:** Users can verify AI agent work through objective evidence (Git commits, test results) and trust completion status without manual checking.

### Story 2.1: Git Correlation Engine

As a **user**,
I want **the system to detect which Git commits reference my stories**,
So that **I can verify AI agents actually committed code for completed work**.

**Acceptance Criteria:**

**Given** a BMAD project is a Git repository with commit history
**When** Git correlation runs for a specific story (e.g., "story-1.3")
**Then** executes `git log` with pattern matching for story identifier
**And** returns list of GitCommit dataclasses with hash, message, timestamp, files_changed
**And** matches patterns: "story-1.3", "Story 1.3", "[1.3]", "feat(story-1.3)"
**And** calculates last_commit_time from most recent matching commit
**And** determines status:  green if commits exist,  red if none,  yellow if >7 days old
**And** falls back to file modification time if Git commands fail (NFR22)
**And** correlation completes in <100ms per story
**And** handles Git CLI errors gracefully (returns "Unknown" status)
**And** logs Git correlation mismatches for debugging
**And** 100% accuracy on commit detection (no false positives - NFR requirement)

### Story 2.2: Test Discovery & Result Parsing

As a **user**,
I want **the system to find test files and parse their results**,
So that **I can see pass/fail counts and verify tests actually ran**.

**Acceptance Criteria:**

**Given** a BMAD project has test files (pytest or jest)
**When** test discovery runs for a story
**Then** searches for test files matching story pattern (e.g., `test_story_1_3.py`, `story-1.3.test.js`)
**And** parses pytest output for total/passing/failing test counts
**And** parses jest output for total/passing/failing test counts
**And** extracts last_run_time from test result file modification time
**And** extracts failing_test_names list for detailed feedback
**And** determines status:  green if all passing,  red if any failing,  yellow if >24hrs old
**And** returns TestEvidence dataclass with total_tests, passing_tests, failing_tests
**And** allows manual test status entry if auto-discovery fails (NFR23)
**And** discovery completes in <100ms per story
**And** handles missing test files gracefully (returns "Unknown" status)
**And** 100% accurate pass/fail reporting (NFR requirement)

### Story 2.3: Evidence API Endpoints

As a **user**,
I want **API endpoints that serve Git and test evidence for stories**,
So that **the frontend can display validation badges and expandable details**.

**Acceptance Criteria:**

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

### Story 2.4: Evidence Badges & Expandable Modals

As a **user**,
I want **color-coded badges (//) that expand to show commit and test details**,
So that **I can click for proof instead of trusting checkmarks blindly**.

**Acceptance Criteria:**

**Given** the Kanban board displays stories
**When** a story card renders
**Then** shows Git badge with color coding ( commits exist,  no commits,  old)
**And** shows Test badge with format "Tests: 12/12" and color coding
**And** shows timestamp badge (e.g., "2h ago", "3 days ago")
**And** displays  VALIDATED when Git  AND Tests  AND recent (<24hrs)
**And** click target size is minimum 44x44px (NFR10)
**And** badges meet 4.5:1 contrast ratio (NFR11)
**When** user clicks Git badge
**Then** modal expands showing commit messages, hashes, timestamps, files changed
**And** modal expansion feels instant (<50ms - NFR5)
**And** modal overlays dashboard (not new page - UX requirement)
**When** user clicks Test badge
**Then** modal expands showing total/passing/failing counts, failing test names, last run time
**And** modal expansion feels instant (<50ms)
**And** mouse-only operation works perfectly (NFR13)
**And** progressive disclosure: badges always visible, details on demand (NFR15)

## Epic 3: Multi-View Dashboard

**User Outcome:** Users can adapt the dashboard interface to their current cognitive state, switching between full context, visual timeline, or minimal list view.

### Story 3.1: Hash-Based Router & View Mode Switching

As a **user**,
I want **to switch between Dashboard, Timeline, and List views using clickable buttons**,
So that **I can adapt the interface to my current cognitive state**.

**Acceptance Criteria:**

**Given** the frontend is loaded
**When** page initializes
**Then** hash-based router listens for `#/dashboard`, `#/timeline`, `#/list` routes
**And** default route is `#/dashboard` if no hash present
**And** view switcher buttons appear at top of page (Dashboard | Timeline | List)
**And** current view button is highlighted
**When** user clicks "Dashboard" button
**Then** URL changes to `#/dashboard`
**And** Dashboard view renders with Kanban board
**And** transition completes in <100ms with 60fps animation (NFR4)
**When** user clicks "Timeline" button
**Then** URL changes to `#/timeline`
**And** Timeline view renders (placeholder for now - detailed in Story 3.2)
**And** transition completes in <100ms with 60fps
**When** user clicks "List" button
**Then** URL changes to `#/list`
**And** List view renders (minimal - detailed in Story 3.3)
**And** transition completes in <100ms with 60fps
**And** selected view mode is saved to localStorage (FR37)
**And** on next page load, last selected view mode is restored
**And** all functionality accessible via mouse clicks only (NFR13)

### Story 3.2: Kanban Board & Timeline View

As a **user**,
I want **a full Kanban board showing stories in TODO/IN PROGRESS/REVIEW/COMPLETE columns**,
So that **I can see all project work organized by status**.

**Acceptance Criteria:**

**Given** Dashboard view is active
**When** Kanban board renders
**Then** displays 4 columns: TODO | IN PROGRESS | REVIEW | COMPLETE
**And** each column shows stories filtered by status from API data
**And** stories display as cards with title, epic reference, status badges
**And** unified Action Card shown for current story (Story + Task + Command preview)
**And** generous whitespace between cards (UX requirement)
**And** board renders in <100ms after data fetch
**And** supports 100+ stories without performance degradation (NFR8, NFR9)
**When** Timeline view is active
**Then** displays workflow execution history over time (visual timeline)
**And** shows which BMAD workflows were run and when
**And** timeline entries are clickable to see workflow details
**And** most recent workflows appear at top
**And** timeline renders in <100ms
**And** no memory leaks when switching views (NFR9)

### Story 3.3: Minimal List View & Manual Refresh

As a **user**,
I want **a minimal List view for brain fog days that shows only current task and next action**,
So that **I can function even when full Kanban view is overwhelming**.

**Acceptance Criteria:**

**Given** List view is active
**When** minimal view renders
**Then** displays only: current story title, current task description, next action command
**And** background remains dark theme (#1a1a1a)
**And** text is large (minimum 14px font - NFR14)
**And** no Kanban columns, no progress bars, no timeline - just essentials
**And** copy command button is prominent and easy to click (44x44px - NFR10)
**And** view renders in <50ms (minimal content)
**And** reduces cognitive load by showing 3 items max
**When** user clicks "Refresh Dashboard" button (in any view)
**Then** POST request to `/api/refresh?project_root=/path` clears cache
**And** dashboard re-parses all BMAD artifacts
**And** updated data is displayed
**And** refresh completes in <300ms (NFR7)
**And** user's current view mode is preserved during refresh
**And** no time-limited interactions or auto-dismiss (NFR17)

## Epic 4: Zero-Friction Execution

**User Outcome:** Users can immediately execute the next workflow step with one-click command copying, eliminating "what do I do next?" decision paralysis.

### Story 4.1: Three-Layer Action Card & One-Click Command Copy

As a **user**,
I want **a unified Action Card showing Story + Task + Command with one-click copy**,
So that **I can go from "what do I do next?" to executing work in <10 seconds**.

**Acceptance Criteria:**

**Given** the dashboard is displaying the current story
**When** Action Card component renders
**Then** displays three layers in single unified card:
**Layer 1 (Story Level):** Story title and acceptance criteria summary
**Layer 2 (Task Level):** Current task description (e.g., "Task 2/5: Write API route handler")
**Layer 3 (Command Level):** BMAD workflow command based on story state
**And** command suggestions are context-specific:
- If story status is TODO  suggests `/bmad-bmm-workflows-dev-story`
- If story status is IN PROGRESS  suggests continuing dev-story or `/bmad-bmm-workflows-code-review`
- If story status is REVIEW  suggests `/bmad-bmm-workflows-code-review`
- If story status is COMPLETE  suggests next story's command
**And** "Copy Command" button is prominent (44x44px minimum - NFR10)
**When** user clicks "Copy Command" button
**Then** command text is copied to clipboard
**And** visual feedback shows "Copied!" for 2 seconds
**And** copy action completes instantly (<20ms)
**And** user can paste command directly into Antigravity/IDE
**And** Action Card renders in <50ms
**And** all three layers visible simultaneously (no tabs or hidden sections)
**And** generous spacing between layers (UX requirement)

### Story 4.2: Workflow History & Gap Detection

As a **user**,
I want **to see which BMAD workflows were executed and detect missing steps**,
So that **I can verify I followed the proper sequence and catch skipped workflows**.

**Acceptance Criteria:**

**Given** a story has workflow execution history
**When** workflow history component renders
**Then** displays execution sequence with timestamps:
- `/bmad-bmm-workflows-dev-story` executed at "2026-01-09 10:30 AM"
- `/bmad-bmm-workflows-code-review` executed at "2026-01-09 11:15 AM"
**And** each workflow entry shows name, timestamp, and status
**And** workflows are ordered chronologically (most recent first)
**And** system detects common workflow gaps:
- Story marked "done" but no `/bmad-bmm-workflows-dev-story` found
- Dev-story complete but no `/bmad-bmm-workflows-code-review` executed
- Code-review done but no tests found
**When** workflow gap is detected
**Then** displays warning: " Missing: code-review workflow"
**And** suggests next correct workflow to run
**And** gap detection runs automatically on dashboard load
**And** detection completes in <50ms
**And** workflow history is parsed from story file frontmatter or Git commit messages
**And** if workflow history unavailable, shows "Unknown" rather than crashing (NFR24)

## Epic 5: AI Coach Integration

**User Outcome:** Users can get project-aware assistance, validate AI agent outputs, and receive intelligent workflow suggestions through Gemini 3 Flash integration.

### Story 5.1: Gemini API Integration & Streaming Chat

As a **user**,
I want **a right sidebar AI chat that streams responses from Gemini 3 Flash**,
So that **I can ask project-aware questions and get answers in real-time**.

**Acceptance Criteria:**

**Given** Gemini API key is configured in `.env` file
**When** AI chat sidebar renders
**Then** displays chat interface on right side of dashboard (300-400px width)
**And** chat remains accessible from all views (Dashboard/Timeline/List)
**And** input textarea accepts user questions
**And** "Send" button is clickable (44x44px minimum - NFR10)
**When** user types question and clicks "Send"
**Then** POST request to `/api/ai-chat` with message and project context
**And** backend calls Gemini 3 Flash API with:
- User's question
- Current project state (phase, epic, story, task)
- BMAD Method documentation context
**And** streams response using Server-Sent Events (SSE)
**And** first token appears within <200ms (NFR6)
**And** tokens appear progressively as generated (not waiting for full response)
**And** chat history is maintained during session
**And** code blocks in responses have "Copy" button
**And** API key is never sent to frontend (stored backend-only - security requirement)
**And** if Gemini API fails, chat shows error but dashboard still works (NFR21)
**And** streaming completes without memory leaks (NFR9)
**And** supports **One-Click Status Transitions** (e.g., AI suggests "Mark as Done" after successful review, and clicking a generated command updates the story file/sprint-status.yaml via a dedicated backend endpoint, intelligently track tasks, stories, epics and tasks)

### Story 5.2: Project-Aware Q&A & Suggested Prompts

As a **user**,
I want **AI suggestions based on my current project state with ready-to-click prompts**,
So that **I don't have to think about what to ask**.

**Acceptance Criteria:**

**Given** AI chat is loaded
**When** sidebar renders
**Then** displays suggested prompts based on current context:
- "What should I do next?"
- "Did the AI agent complete Story 1.3 correctly?"
- "What's the status of my current epic?"
- "Show me the acceptance criteria for this story"
**And** suggested prompts change based on project state:
- If story is TODO  "How do I start this story?"
- If story is IN PROGRESS  "What tasks remain in this story?"
- If story is REVIEW  "Should I run code-review now?"
**When** user clicks a suggested prompt
**Then** prompt text is inserted into chat input
**And** AI response is generated automatically
**And** AI knows current phase, epic, story, task from project context
**When** user asks "What should I do next?"
**Then** AI suggests correct next BMAD workflow based on story state
**And** provides copy-paste command ready to execute
**And** explains why this workflow is next in the sequence
**And** responses reference BMAD Method documentation for accuracy (FR28)
**And** AI detects BMAD Method version from project config (FR29)
**And** suggestions are accurate based on latest BMAD best practices (FR30)

### Story 5.3: AI Agent Output Validation & Workflow Gap Warnings

As a **user**,
I want **the AI to compare story claims vs. Git/test reality and warn me about gaps**,
So that **I can trust AI agent completion and catch missing workflows**.

**Acceptance Criteria:**

**Given** a story is marked "done" in sprint-status.yaml
**When** user asks "Did the AI agent complete Story 1.3 correctly?"
**Then** AI analyzes story claims vs. evidence:
- Checks if Git commits exist for story
- Checks if tests were run and passed
- Checks if all tasks in story file are marked complete
- Checks if code-review workflow was executed
**And** AI provides validation summary:
" Story 1.3 appears complete:
- 6 Git commits found (last: 2h ago)
- Tests: 18/18 passing (last run: 2h ago)
- All 5 tasks marked complete
- Code review executed at 11:15 AM"
**Or** AI detects issues:
" Story 1.3 marked done but issues found:
- Git commits exist 
- Tests: 0 found  (no test files detected)
- Code review workflow missing 
Suggestion: Run `/bmad-bmm-workflows-code-review` and add tests"
**And** AI detects workflow gaps automatically (FR27):
- Story marked done without dev-story workflow
- Dev-story complete but no code-review
- Code-review done but no tests found
**And** AI warnings are actionable with specific next steps
**And** AI validation leverages Git and test evidence from Epic 2
**And** validation runs in <500ms for comprehensive check
**And** AI responses maintain conversation context across multiple questions
