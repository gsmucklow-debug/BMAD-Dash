---
stepsCompleted: [1, 2, 3, 4, 6, 7, 8, 9, 10, 11]
inputDocuments: ['f:/BMAD Dash/_bmad-output/analysis/brainstorming-session-2026-01-08.md', 'f:/BMAD Dash/Docs/BMAD Dash.txt']
workflowType: 'prd'
lastStep: 11
---

# Product Requirements Document - {{project_name}}

**Author:** {{user_name}}
**Date:** {{date}}

## Executive Summary

BMAD Dash is a localhost web dashboard that serves as an "AI Agent Orchestration Auditor" for developers using the BMAD Method. It solves the cognitive re-orientation challenge that occurs when returning to multi-phase, AI-agent-orchestrated projects after breaksespecially critical for users with MS or brain fog.

When developers sit down after time away, they face the question: "Where was I? What did I do? What's next?" BMAD Dash eliminates this friction by auto-parsing BMAD artifacts (epics, stories, git history), validating that AI agents completed work properly, and providing zero-friction next steps with copy-paste BMAD workflow commands.

**Target Users:**
- Primary: Developers with MS/brain fog managing BMAD Method projects
- Secondary: Any BMAD Method user orchestrating multiple AI agents across complex projects

**Core Value:**
The dashboard stays open in the browser while users work in their IDE, providing instant cognitive re-orientation on return without manual reconstruction or leaving their workspace.

### What Makes This Special

**The Quality Trust Gap Solution:** Traditional project trackers show simple status ( Done). BMAD Dash provides **verifiable evidence** through objective, machine-checkable proof:

- **Git validation:** Commits exist for the story (not just marked complete)
- **Test evidence:** Pass/fail count with timestamp (tests actually ran recently)
- **Workflow verification:** Which BMAD agents were executed, not just assumed

This solves a unique challenge in AI-assisted development: **trusting that AI agents delivered what they claimed.** Users see objective proof (Git  + Tests  2h ago) instead of subjective claims, eliminating the "did the agent actually finish?" uncertainty.

**The breakthrough moment:** When users see verifiable evidence instead of status checkmarks, they instantly trust their past work and confidently move forwardcognitive friction disappears.

**Success vision:** BMAD Method adoption accelerates because the cognitive overhead of multi-phase, AI-agent-orchestrated projects is removed. Users with cognitive challenges can manage complex projects with the same confidence as neurotypical developers.

## Project Classification

**Technical Type:** web_app  
**Domain:** Developer Productivity Tool  
**Complexity:** Medium  
**Project Context:** Greenfield - new product

**Classification Rationale:**
- Localhost browser-based dashboard (Flask backend + HTML/JS frontend)
- Developer-focused productivity tool for BMAD Method users
- Medium complexity due to AI integration (Gemini 3 Flash), Git parsing, BMAD artifact analysis, and multi-view architecture
- Standard web development practices with assistive technology UX considerations
- No regulatory compliance requirements


## Success Criteria

### User Success

**Primary Success Moments:**

1. **Instant Re-Orientation (3-second rule)**
   - User returns to BMAD project after break (overnight, between sessions)
   - Opens BMAD Dash in browser
   - Within 3 seconds: breadcrumb navigation + Quick Glance Bar show exact position (Phase > Epic > Story > Task)
   - **Success metric:** Zero mental reconstruction required - user knows "where am I" immediately

2. **Trust Restoration**
   - User views last completed story with quality indicators
   - Sees objective proof:  Git commits exist +  Tests 12/12 passing (2h ago)
   - Confidently proceeds to next story without doubt about past work quality
   - **Success metric:** User trusts AI agent completion and moves forward without verification anxiety

3. **Zero Decision Fatigue**
   - User sees three-layer Action Card (Story + Task + Command)
   - Copies BMAD workflow command with one click
   - Starts work immediately in IDE without "what do I do next?" paralysis
   - **Success metric:** From dashboard open to executing work: <10 seconds

**User Success Statement:** "I can manage complex multi-phase BMAD projects with the same confidence as neurotypical developers, despite MS/brain fog challenges."

### Business Success

**3-Month Success Criteria:**
- **Daily adoption:** BMAD Dash auto-opens on all BMAD project sessions (100% usage rate)
- **Time saved:** Re-orientation time reduced from 5-10 minutes to <10 seconds per session return
- **Confidence indicator:** User proceeds to next task without re-reading story files or git history
- **Reduced cognitive load:** Fewer "lost in project" moments (subjective self-report improvement)

**12-Month Success Criteria:**
- **Sustained value:** Tool remains essential for all BMAD projects (not abandoned)
- **Project complexity:** Ability to manage 3+ simultaneous BMAD projects without cognitive overload
- **Workflow integration:** BMAD Dash becomes automatic part of development setup (like opening IDE)
- **Fundamental improvement:** User says "I couldn't manage BMAD projects effectively without this tool"

**Business Success Statement:** BMAD Dash becomes an indispensable cognitive augmentation tool that enables complex project management despite neurological challenges.

### Technical Success

**Performance Requirements:**
- **Startup speed:** Parse BMAD artifacts + detect phase + generate AI summary in <500ms (instant feel, no loading spinner)
- **UI responsiveness:** All view transitions (Dashboard  Timeline  List) maintain 60fps (critical for brain fog - no janky animations)
- **AI streaming:** Gemini 3 Flash responses stream with <200ms first-token latency (no frozen UI waiting for AI)

**Accuracy Requirements:**
- **Phase detection:** 100% accuracy identifying current BMAD phase from artifacts (Phase 1-4 or Unknown)
- **Git validation:** 100% reliable commit detection for stories (no false positives - trust depends on accuracy)
- **Test discovery:** 100% accurate pass/fail status + timestamp detection (verifiable evidence must be correct)
- **Workflow gap detection:** AI coach correctly identifies missing workflows (dev-story done but no code-review) with 95%+ accuracy

**Reliability Requirements:**
- **Zero false trust:** If quality indicators show , the work is actually complete (false positives destroy trust)
- **Graceful degradation:** If AI unavailable, core features (phase detection, Git/test validation, command copy) still work
- **Local-first:** All features work on localhost without internet (except initial Gemini API call)

**Technical Success Statement:** Fast, accurate, trustworthy validation that never breaks user confidence in the tool.

### Measurable Outcomes

**Quantitative Metrics:**
- Re-orientation time: <10 seconds (from dashboard open to executing work)
- Startup performance: <500ms full parse and state detection
- UI frame rate: 60fps maintained across all interactions
- Validation accuracy: 100% for Git commits, 100% for test detection, 95%+ for workflow gaps
- Daily usage rate: 100% of BMAD project sessions after 1 month

**Qualitative Metrics:**
- User self-reports reduced cognitive friction
- User confidently manages complex projects without anxiety
- Tool becomes automatic part of workflow (like opening IDE)
- User says "I trust the dashboard's validation completely"

## Product Scope

### MVP - Minimum Viable Product

**Core Features (All Required for MVP):**

1. **Information Architecture:**
   - Breadcrumb navigation (Project > Phase > Epic > Story > Task)
   - Two-tier display: Quick Glance Bar (Done | Current | Next) + Full Kanban (TODO | IN PROGRESS | REVIEW | COMPLETE)
   - Three-layer Action Card (Story + Task + Command unified in single UI element)

2. **Quality Trust \u0026 Validation:**
   - Color-coded badges:  Git,  Tests: 12/12,  2h ago
   - Expandable details (click badges to see commits, test results)
   - Big visual validation ( VALIDATED when all checks pass)
   - Workflow history showing what BMAD workflows were executed

3. **AI Coach Integration:**
   - Right sidebar chat (project-aware, always accessible)
   - Agent output validation (story claims vs. Git/test reality)
   - Workflow gap detection (missing code-review, tests, etc.)
   - Suggested prompts for common questions
   - Code blocks with one-click copy
   - Streaming responses from Gemini 3 Flash

4. **View Modes:**
   - Dashboard view (full context - default)
   - Timeline view (visual workflow history)
   - List view (minimal for high brain fog days)

5. **Backend \u0026 Parsing:**
   - Flask backend with BMAD artifact parsing
   - Phase detection algorithm (sprint-status.yaml, epics.md frontmatter, story files)
   - Git correlation (commits referencing stories)
   - Test detection (pass/fail count + timestamp)
   - File modification tracking

6. **Visual Design:**
   - Dark theme (reduced visual fatigue)
   - Simple progress bars (Epic: 3/7, Story: 6/10)
   - VSCode-style status indicators
   - No keyboard shortcuts (accessibility - memory burden)

**MVP Success Gate:** All core features working reliably. User can return to any BMAD project, get instant orientation, trust quality validation, and execute next step without cognitive friction.

### Growth Features (Post-MVP)

**Deferred to v2:**
- Advanced filtering/search (eliminated from MVP - unnecessary when dashboard auto-shows state)
- WebSocket push updates (eliminated - manual refresh sufficient for once-per-session use)
- Git post-commit hooks (maybe v2 - real-time validation)
- Multi-project support (v2 - file explorer to switch between BMAD projects)
- Manual rollback UI (mark story back to in-progress with validation)
- Export/import dashboard state

### Vision (Future)

**Long-term possibilities:**
- Learning mode: AI coach detects user patterns ("You tend to forget code-review after dev-story")
- Stuck detection: AI notices story in-progress 3+ days and suggests /correct-course
- Blocker surfacing: AI identifies dependencies ("Story 1.4 depends on Story 1.3 tests passing")
- BMAD Method community sharing: Anonymized workflow patterns to improve method itself
- Cross-project insights: "Your Echo-OS workflow could inform BMAD Dash development"


## User Journeys

### Journey 1: Gary's Morning After - Returning to Echo-OS

Gary sits down at his desk Tuesday morning with his coffee, ready to continue work on Echo-OS. Yesterday feels like a blur - he remembers working on voice capture, running some BMAD workflows, but the details are fuzzy. He opens VSCode and stares at the file tree. "Was I finishing Story 1.3 or starting 1.4? Did the tests pass? What agent do I need to call?"

He opens BMAD Dash in Chrome. Within 3 seconds, the breadcrumb shows: `Echo-OS > Phase 4: Implementation > Epic 1: Core Foundation > Story 1.4: Vector Search > Task 2/5`. The Quick Glance Bar shows "Done: Story 1.3 | Current: Story 1.4 | Next: Story 1.5". No mental reconstruction needed - he knows exactly where he is.

He glances at Story 1.3 in the "Done" column. Green badges glow:  Git (6 commits)  Tests: 18/18 passing (3h ago). A wave of relief - past-him did complete it properly. The AI coach panel suggests: "Ready for Story 1.4: Implement vector search endpoint. Run: `/bmad-bmm-workflows-dev-story`"

The breakthrough moment: Gary clicks the [Copy Command] button, pastes into Antigravity, and starts work in 8 seconds flat. No re-reading story files, no checking git history, no decision paralysis. Just instant orientation and zero-friction execution.

Three months later, Gary hasn't had a single "lost in project" morning. BMAD Dash opens automatically with VSCode, and every session starts with confident clarity instead of anxious reconstruction.

### Journey 2: The Brain Fog Day - Switching to Minimal View

It's Wednesday afternoon, and Gary can feel the brain fog settling in thick. The Full Kanban view with breadcrumbs, progress bars, and all the details suddenly feels overwhelming - too much visual information competing for his limited cognitive bandwidth.

He clicks the view switcher and selects "List" - the minimal view designed for exactly this situation. The dashboard transforms: just the essentials against the dark theme. Current task in large text: "Story 1.4: Implement vector search endpoint - Task 2/5: Write API route handler". Below it, a single Action Card with the command ready to copy.

No Kanban columns, no timeline, no progress visualization - just what he needs right now. The AI coach is still there in the sidebar, but quieter, with just one suggested action instead of multiple prompts.

The critical moment: Even on a challenging cognitive day, Gary can still see what to do next and execute it. He copies the command, switches to his IDE, and makes incremental progress. The tool adapts to his cognitive state instead of demanding he adapt to it.

By the end of the day, Gary has completed two small tasks. On a pre-BMAD-Dash brain fog day, he would have spent the day feeling lost and accomplished nothing. Now, the minimal view keeps him functional even when his brain isn't.

### Journey 3: Trust Validation - Did the Agent Actually Finish?

Gary returns Monday morning after a weekend away. He'd asked the BMAD Dev agent to complete Story 1.5 (Knowledge Base Integration) Friday afternoon before logging off. The story file shows Status: "done" and all checkboxes are ticked. But that nagging doubt creeps in - "Did the AI agent actually deliver, or did it just mark things complete?"

He opens BMAD Dash and navigates to Story 1.5 in the "Done" column. The status shows  VALIDATED with green badges. He clicks the Git badge - a modal expands showing 12 actual commit messages: "feat(story-1.5): Add LanceDB integration", "feat(story-1.5): Implement embedding search", "test(story-1.5): Add integration tests". Real commits, referencing the story properly.

He clicks the Tests badge. Another modal: "Tests: 24/24 passing. Last run: Saturday 4:23 PM". Not just marked complete - the tests actually ran and passed after the Friday work session.

The validation moment: Gary sees the Workflow History showing `/bmad-bmm-workflows-dev-story` executed Friday 3:15 PM, followed by `/bmad-bmm-workflows-code-review` at 4:10 PM. The agent followed the proper sequence, and the evidence proves it.

He confidently clicks "Story 1.6" without a second of doubt. The Quality Trust Gap - that unique uncertainty of AI-assisted development - is completely eliminated. He has objective, verifiable proof instead of subjective hope.

Six months later, Gary has never once had to manually verify an AI agent's work. BMAD Dash's validation system has become his source of truth, and his confidence in AI-assisted development is absolute.

### Journey Requirements Summary

These three journeys reveal the following core capabilities needed:

**Navigation \u0026 Orientation:**
- Breadcrumb navigation with real-time phase/epic/story/task context
- Quick Glance Bar for temporal orientation (Done | Current | Next)
- Full Kanban board with story status visualization
- View mode switching (Dashboard/Timeline/List) for cognitive state adaptation

**Quality Validation \u0026 Trust:**
- Git correlation engine (detect commits referencing stories)
- Test discovery and status tracking (pass/fail + when last ran)
- Workflow execution logging (which BMAD agents were run)
- Visual trust indicators ( VALIDATED when all checks pass)
- Expandable evidence modals (click Git/Test badges to see proof)

**AI Coach Integration:**
- Context-aware next-step suggestions based on current story
- One-click command copying for BMAD workflow execution
- Right sidebar chat for project-aware assistance
- Suggested prompts for common questions

**Accessibility \u0026 UX:**
- Dark theme for reduced visual fatigue
- Minimal view mode for high brain fog days
- Fast startup (\u003c500ms) for instant orientation
- Progressive disclosure (overview always visible, details on demand)
- Color-coded badges for instant status scanning
- No keyboard shortcuts (memory burden for accessibility)

**Backend Capabilities:**
- BMAD artifact parsing (epics.md, story files, sprint-status.yaml)
- Phase detection algorithm
- Git commit correlation and analysis
- Test file discovery and status extraction
- File modification tracking
- Gemini 3 Flash AI integration for coach panel


## Innovation \u0026 Novel Patterns

### Detected Innovation Areas

**Core Innovation: AI Agent Orchestration Auditor**

BMAD Dash represents a fundamentally new product category that emerges from the intersection of AI-assisted development and BMAD Method workflows. Traditional project dashboards track human work ("What did I do?"). BMAD Dash validates AI agent work ("Did the AI agent actually deliver what it claimed?").

This innovation addresses a problem that didn't exist 2 years ago: **the Quality Trust Gap in AI-assisted development**. As developers increasingly orchestrate multiple AI coding agents across complex projects, they face a unique challengetrusting that automated agents completed work properly without manual verification. BMAD Dash solves this through objective, machine-checkable proof instead of subjective status claims.

**Novel Combination of Technologies:**

BMAD Dash combines several established concepts in an unprecedented way:
- **Assistive technology principles** (cognitive load management, progressive disclosure) applied to developer tools
- **AI agent workflow validation** (comparing claims vs. Git/test reality)
- **BMAD Method artifact intelligence** (phase detection, epic/story parsing)
- **Real-time evidence correlation** (Git commits + test results + workflow execution logs)

This specific combination is unique to this moment in software development historywhere AI agents are capable enough to code autonomously but not yet trusted enough to work unsupervised.

**Innovation Signals:**
- "Verifiable evidence vs. status claims" - challenging the assumption that completion checkboxes are sufficient
- "Cognitive augmentation for AI orchestration" - applying assistive tech to the emerging skill of managing AI agents
- "Trust through proof, not faith" - rethinking how developers validate automated work

### Market Context \u0026 Competitive Landscape

**Emerging Problem Space:**

As of early 2026, AI coding agents (Cursor, Claude Code, Windsurf, Copilot) have reached production-quality autonomy. Developers now routinely delegate entire stories to AI agents, creating a new challenge: **How do you trust work you didn't write?**

Existing project trackers (Jira, Linear, GitHub Projects) assume human developers who can verify their own work. They track "what's done" but not "is it actually done correctly." BMAD Dash fills this gap.

**Competitive Analysis:**

- **Traditional project trackers** (Jira, Linear): Track status but don't validate AI agent output
- **GitHub Actions/CI dashboards**: Show test results but don't correlate to story completion or detect workflow gaps
- **BMAD Method itself**: Provides the methodology but no dashboard for cognitive re-orientation
- **Developer analytics tools** (WakaTime, Clockify): Track time but not work quality or AI agent reliability

**BMAD Dash's unique position:** First tool designed specifically for validating and orchestrating AI agent workflows within a structured development methodology (BMAD Method).

### Validation Approach

**Three-Tier Validation Strategy:**

1. **Personal Validation (Primary)**
   - Daily use on Echo-OS and future BMAD projects
   - Subjective metric: Does it eliminate the "did the agent finish?" doubt?
   - Success indicator: Gary confidently proceeds to next story without manual verification

2. **Evidence Accuracy (Technical)**
   - Git correlation correctly identifies incomplete work (catches false completion claims)
   - Test detection accurately reports pass/fail status with current timestamps
   - Workflow gap detection identifies missing steps (dev-story done but no code-review)
   - Success metric: 95%+ accuracy on validation checks (measured against manual inspection)

3. **Time Savings (Measurable)**
   - Re-orientation time drops from 5-10 minutes to \u003c10 seconds per session return
   - Success metric: Quantifiable time savings tracked over 3-month adoption period

**Validation Timeline:**
- **Week 1-2:** Core validation features working (Git + Test correlation)
- **Month 1:** Daily usage on Echo-OS with subjective confidence assessment
- **Month 3:** Accuracy metrics + time savings data confirm innovation delivers value

### Risk Mitigation

**Innovation Risks \u0026 Fallback Strategies:**

**Risk 1: AI Validation Complexity**
- **Challenge:** Gemini 3 Flash analysis proves unreliable or too slow for validation needs
- **Fallback:** Degrade to "smart project tracker" without AI coach features
- **Core value retained:** Git/test validation + phase detection + breadcrumb navigation still provide instant orientation
- **Mitigation:** Build validation engine first, add AI coach as enhancement layer

**Risk 2: Git Correlation Brittleness**
- **Challenge:** Detecting commits that reference stories proves too fragile (false positives/negatives from varying commit message formats)
- **Fallback:** Simpler status indicators based on file modification times + story file checkboxes
- **Core value retained:** Temporal orientation (Done | Current | Next) + command suggestions still eliminate decision paralysis
- **Mitigation:** Start with loose pattern matching (story-X.X anywhere in commit), tighten over time

**Risk 3: Test Discovery Failure**
- **Challenge:** Test file detection/parsing fails for different test frameworks or patterns
- **Fallback:** Manual test status entry or simple "tests exist" indicator without pass/fail details
- **Core value retained:** Git validation + AI coach + navigation still provide value
- **Mitigation:** Support common test frameworks first (pytest, jest), expand based on need

**Graceful Degradation Principle:**

BMAD Dash is architected with layered value:
1. **Layer 1 (Core):** Phase detection + breadcrumb navigation + Quick Glance Bar = instant orientation
2. **Layer 2 (Validation):** Git correlation + test detection = quality trust
3. **Layer 3 (Intelligence):** AI coach + workflow gap detection = orchestration guidance

Each layer adds value but doesn't depend on layers above it. If innovation features fail, the tool remains useful as a cognitive augmentation dashboard.

**Success Definition:**

Innovation succeeds if BMAD Dash becomes indispensable for managing AI-assisted BMAD projectsnot because it's clever, but because it eliminates cognitive friction and trust anxiety that wouldn't exist without AI agents.


## Web Application Specific Requirements

### Project-Type Overview

BMAD Dash is a **single-page application (SPA)** with a Flask backend serving both API endpoints and static assets. The frontend uses client-side JavaScript for view routing (Dashboard/Timeline/List) and dynamic content updates without page reloads.

**Architecture Pattern:**
- **Backend:** Flask (Python 3.10+) serves API + static files
- **Frontend:** Vanilla JavaScript SPA (no framework overhead for simplicity)
- **Communication:** RESTful API for data fetching, Gemini 3 Flash API for AI coach
- **State Management:** Client-side state for current view, filters, expanded modals
- **Routing:** Client-side routing for `/dashboard`, `/timeline`, `/list` views

### Technical Architecture Considerations

**Browser Matrix:**

**Primary Target:**
- Microsoft Edge (latest stable) - Primary browser for Gary
- Modern Chromium-based browsers (Chrome, Edge, Brave) - Latest 2 versions

**Not Supported:**
- Internet Explorer (deprecated)
- Safari (not a Windows browser)
- Firefox (optional support if trivial, but not required)

**Why Modern-Only:**
- Localhost tool for personal use (not public-facing)
- Can leverage modern JavaScript features (ES2020+, async/await, fetch API, CSS Grid)
- No legacy browser polyfills needed = faster development
- Dark theme uses modern CSS custom properties

**Responsive Design:**

**Viewport Strategy:** Desktop-optimized (laptop/desktop screen sizes)

- **Primary:** 1920x1080 (standard desktop resolution)
- **Minimum:** 1366x768 (laptop screen minimum comfortable size)
- **Not mobile-responsive:** Explicitly desktop-only (no mobile/tablet layouts needed)

**Layout Considerations:**
- Two-column layout (main dashboard + right sidebar AI coach)
- Breadcrumb navigation at top (always visible)
- Quick Glance Bar below breadcrumbs
- Full Kanban board in main area
- Sidebar fixed width (300-400px), main area flexible

**No Need For:**
- Mobile breakpoints
- Touch gesture support
- Hamburger menus or collapsed navigation
- Tablet-specific layouts

**Performance Targets:**

**Startup Performance:**
- **Page load:** \u003c500ms from Flask serving HTML to interactive dashboard
- **Full parse:** \u003c500ms for BMAD artifact parsing + phase detection + initial render
- **Total cold start:** \u003c1 second from URL load to usable dashboard

**Runtime Performance:**
- **View switching:** \u003c100ms transition between Dashboard/Timeline/List (60fps smooth animations)
- **Git badge click:** \u003c50ms to expand modal with commit details (feels instant)
- **Test badge click:** \u003c50ms to expand modal with test results
- **AI coach streaming:** \u003c200ms first-token latency from Gemini 3 Flash
- **Refresh action:** \u003c300ms full re-parse and dashboard update

**Memory Constraints:**
- Keep memory usage \u003c100MB for frontend JS (parsing large epics/stories)
- No memory leaks on view switching or modal open/close

**Why These Targets:**
- Instant feel (\u003c500ms) critical for cognitive load reduction
- 60fps animations prevent visual jarring for users with brain fog
- Fast AI responses maintain conversation flow

**SEO Strategy:**

**Not Applicable:** BMAD Dash is a localhost-only tool, not publicly indexable.

- No meta tags for search engines needed
- No sitemap.xml or robots.txt
- No structured data markup
- No social media Open Graph tags
- No canonical URLs or redirects

**Focus Instead On:**
- Fast initial render for perceived performance
- Clear document title (`BMAD Dash - [Project Name]`) for browser tab identification

**Accessibility Level:**

**Assistive Technology Approach:**

BMAD Dash is designed from the ground up as assistive technology for users with MS/brain fog. The accessibility approach focuses on **cognitive load management** rather than WCAG compliance checklists.

**Core Accessibility Features (Already Designed):**
1. **Dark theme** - Reduces visual fatigue and glare sensitivity
2. **High contrast** - Color-coded badges ( green,  red,  yellow) easily distinguishable
3. **Progressive disclosure** - Overview always visible, details expandable on demand
4. **Multiple view modes** - Switch to List view for minimal cognitive load on brain fog days
5. **No keyboard shortcuts** - Eliminates memory burden (click-based interaction only)
6. **Large click targets** - Buttons and badges sized for easy clicking without precision
7. **Clear visual hierarchy** - Breadcrumbs \u003e Quick Glance \u003e Kanban \u003e Details (top-to-bottom importance)

**WCAG Considerations:**

While not pursuing formal WCAG 2.1 AA compliance (not required for personal use), the design naturally aligns with several success criteria:

- **1.4.3 Contrast** - Dark theme with high-contrast text meets minimums
- **1.4.13 Content on Hover** - No hover-only content; expandable clicks instead
- **2.1.1 Keyboard** - All functionality accessible via mouse clicks (no keyboard traps)
- **2.4.8 Location** - Breadcrumb navigation shows user's location in hierarchy
- **3.2.4 Consistent Identification** - Color-coded badges consistent across all stories

**Not Implementing:**
- Screen reader optimization (not needed by primary user)
- Keyboard-only navigation (intentionally avoided due to memory burden)
- Multi-language support (English only)

**Accessibility Success Criteria:**

Success = Tool adapts to user's cognitive state rather than demanding the user adapt to the tool.

### Implementation Considerations

**Flask Backend Architecture:**

**Responsibilities:**
1. **Serve static assets** - HTML, CSS, JavaScript files
2. **Parse BMAD artifacts** - Read epics.md, story files, sprint-status.yaml
3. **Phase detection** - Determine current BMAD phase from artifacts
4. **Git correlation** - Execute git commands to find commits referencing stories
5. **Test discovery** - Scan for test files and parse results
6. **API endpoints** - Provide JSON data to frontend

**API Endpoints (RESTful):**
- `GET /api/status` - Full project status (phase, epics, stories, current task)
- `GET /api/story/\u003cid\u003e` - Detailed story info with Git commits and test results
- `GET /api/git/\u003cstory-id\u003e` - Git commits for specific story
- `GET /api/tests/\u003cstory-id\u003e` - Test results for specific story
- `POST /api/ai/chat` - Proxy to Gemini 3 Flash with project context
- `POST /api/refresh` - Trigger re-parse of BMAD artifacts

**Frontend JavaScript Architecture:**

**Module Structure:**
- `app.js` - Main application initialization and routing
- `dashboard.js` - Dashboard view rendering
- `timeline.js` - Timeline view rendering
- `list.js` - Minimal list view rendering
- `api.js` - API client for backend communication
- `ai-coach.js` - AI chat sidebar with streaming response handling
- `state.js` - Client-side state management

**State Management:**
- No heavyweight framework (React/Vue) - vanilla JS for simplicity
- Simple state object with current view, expanded modals, chat history
- Event-driven updates on user interaction

**Styling:**
- **CSS approach:** Vanilla CSS (no Tailwind or CSS-in-JS)
- **Design system:** Dark theme with CSS custom properties for colors
- **Layout:** CSS Grid for main dashboard, Flexbox for components
- **Animations:** CSS transitions for view switching and modal expansion (60fps)

**Build \u0026 Deployment:**

**For MVP:**
- No build step needed (vanilla JS + CSS)
- Flask serves files directly from `/static` directory
- Development = Production (localhost-only)

**Future (Post-MVP):**
- Optional bundling with esbuild or Vite for faster load times
- CSS minification for smaller file sizes
- But keep it simple - avoid complex build pipelines


## Project Scoping \u0026 Phased Development

### MVP Strategy \u0026 Philosophy

**MVP Approach:** Complete Problem-Solving MVP

BMAD Dash uses a **"complete vision"** MVP approach rather than incremental iteration. This is strategically necessary because the product is assistive technology for cognitive challengesa partial solution doesn't eliminate cognitive friction, it just creates different friction.

**Strategic Rationale:**
- **Assistive tech cannot be "half-built"** - Either it eliminates cognitive load or it doesn't
- **Personal use = no market risk** - Not validating product-market fit with external users
- **Innovation requires full stack** - AI validation only works with Git correlation + test detection + phase awareness together
- **Brain fog days demand completeness** - If minimal List view missing, user stuck on bad days

**MVP Success Gate:** All core capabilities working reliably. User can return to any BMAD project, get instant orientation, trust quality validation, and execute next step without cognitive friction.

### MVP Feature Set (Phase 1) - Complete Vision

**All Features from Brainstorming Session Are MVP:**

As defined in Success Criteria (Step 3), the MVP includes all 8 feature categories with no deferrals:

1. **Information Architecture**
   - Breadcrumb navigation (Project \u003e Phase \u003e Epic \u003e Story \u003e Task)
   - Two-tier display: Quick Glance Bar (Done | Current | Next) + Full Kanban
   - Three-layer Action Card (Story + Task + Command)

2. **Quality Trust \u0026 Validation**
   - Color-coded badges ( Git,  Tests,  timestamp)
   - Expandable commit/test details
   - Big visual validation ( VALIDATED)
   - Workflow history

3. **AI Coach Integration**
   - Right sidebar project-aware chat
   - Agent output validation
   - Workflow gap detection
   - One-click command copying
   - Streaming Gemini 3 Flash responses

4. **View Modes (All 3 Required for MVP)**
   - Dashboard view (full context)
   - Timeline view (visual history)
   - List view (minimal for brain fog days)

5. **Backend \u0026 Parsing**
   - Flask backend with BMAD artifact parsing
   - Phase detection algorithm
   - Git correlation engine
   - Test discovery and status tracking

6. **Visual Design**
   - Dark theme
   - Progress bars (Epic/Story level)
   - VSCode-style indicators
   - No keyboard shortcuts

**Why Everything Is MVP:**

Each component addresses a specific cognitive need identified in First Principles Thinking:
- **Phase Awareness**  Breadcrumbs + phase detection
- **Temporal Orientation**  Quick Glance Bar (Done | Current | Next)
- **Quality Trust**  Git/test badges with verifiable evidence
- **Zero-Friction Execution**  Three-layer Action Card with copy-paste commands
- **Cognitive State Adaptation**  Multiple view modes (Dashboard/Timeline/List)

Removing any component breaks the assistive technology value proposition.

### Post-MVP Features (Version 2+)

**Deferred from MVP** (as defined in Step 3 - Growth Features):
- Advanced filtering/search
- WebSocket push updates
- Git post-commit hooks (real-time validation)
- Multi-project support (file explorer to switch BMAD projects)
- Manual rollback UI (mark story back to in-progress)
- Export/import dashboard state

**Why Deferred:**
- Not essential for core cognitive re-orientation
- Can be added after validating MVP solves the primary problem
- Complexity doesn't justify MVP inclusion

### Long-Term Vision (Phase 3)

**Future Possibilities** (as identified in Innovation section):
- Learning mode (AI detects user patterns and workflow gaps)
- Stuck detection (AI notices 3+ day stalled stories, suggests `/correct-course`)
- Blocker surfacing (AI identifies dependencies automatically)
- BMAD Method community sharing (anonymized workflow patterns)
- Cross-project insights (Echo-OS patterns inform other projects)

**Vision Success:** BMAD Dash evolves from personal tool to community knowledge platform for BMAD Method best practices.

### Risk Mitigation Strategy

**Technical Risks:**

**Risk 1: AI Validation Complexity**
- **Mitigation:** Layered architecture with graceful degradation
- **Layer 1 (Core):** Phase detection + navigation works without AI
- **Layer 2 (Validation):** Git/test correlation works without AI coach
- **Layer 3 (Intelligence):** AI coach enhances but isn't required
- **Fallback:** If Gemini 3 Flash fails, core features remain functional

**Risk 2: Git Correlation Brittleness**
- **Mitigation:** Start with loose pattern matching (`story-X.X` anywhere in commit)
- **Validation:** Test with Echo-OS commit history during development
- **Fallback:** Use file modification times if commit correlation fails
- **Evolution:** Tighten patterns based on real usage

**Risk 3: Test Discovery Complexity**
- **Mitigation:** Support common frameworks first (pytest for Python, jest for JS)
- **Validation:** Test with Echo-OS test suite during development
- **Fallback:** Manual test status entry if auto-detection fails
- **Evolution:** Add framework support based on actual project needs

**Market Risks:**

**Not Applicable** - Personal use tool, no external market validation needed.

**Success validation happens through:**
1. Daily usage on Echo-OS (primary validation)
2. Time savings measurement (5-10 min  \u003c10 sec)
3. Subjective confidence assessment (trust restoration working?)

**Resource Risks:**

**Risk: Solo Development Slower Than Expected**
- **Mitigation 1:** Use AI coding agents (Cursor, Claude Code) to accelerate development
- **Mitigation 2:** Vanilla JS/CSS (no framework learning curve)
- **Mitigation 3:** Flask simplicity (Python backend, no complex deployment)
- **Contingency:** If timeline extends, core Layer 1 features ship first, Layer 2/3 added incrementally

**Risk: Burnout or Health Issues**
- **Mitigation:** MVP designed for AI-assisted development by BMAD Method itself
- **Self-dogfooding:** Use BMAD Dash to manage BMAD Dash development
- **Contingency:** Tool remains useful even if some advanced features incomplete

### MVP Success Criteria Alignment

**From Step 3 Success Criteria, MVP Must Deliver:**

**User Success:**
-  Instant re-orientation within 3 seconds
-  Trust restoration through verifiable evidence
-  Zero decision fatigue with ready-to-copy commands

**Technical Success:**
-  \u003c500ms startup performance
-  60fps UI responsiveness
-  100% accuracy on Git/test validation (no false trust)

**Business Success (Personal Use):**
-  Daily adoption on all BMAD projects
-  Tool becomes indispensable within 3 months

**Alignment Confirmation:** All MVP features directly support these success criteria. No scope creep, no feature bloat.


## Functional Requirements

### Project Orientation \u0026 Navigation

- **FR1:** User can view hierarchical project context (Project  Phase  Epic  Story  Task) in breadcrumb navigation
- **FR2:** User can view temporal orientation (Done | Current | Next story) in Quick Glance Bar
- **FR3:** User can view current phase detection (Analysis, Planning, Solutioning, Implementation, or Unknown)
- **FR4:** User can view current epic and story position within the project
- **FR5:** User can view current task position within active story
- **FR6:** User can navigate to different epics or stories from the dashboard
- **FR7:** User can see visual progress indicators for epic completion (e.g., "3/7 stories complete")
- **FR8:** User can see visual progress indicators for story completion (e.g., "6/10 tasks complete")

### Quality Validation \u0026 Trust

- **FR9:** User can view Git commit validation status for each story
- **FR10:** User can view test execution status (pass/fail count) for each story
- **FR11:** User can view timestamp of last test execution for each story
- **FR12:** User can expand Git validation badges to see actual commit messages referencing the story
- **FR13:** User can expand test validation badges to see detailed test results
- **FR14:** User can view workflow execution history (which BMAD workflows were run)
- **FR15:** User can see overall validation status ( VALIDATED when Git + Tests + Workflows complete)
- **FR16:** User can view color-coded status indicators ( green for passing,  red for failing,  yellow for missing)
- **FR17:** System can detect Git commits that reference story identifiers (e.g., "story-1.3")
- **FR18:** System can discover and parse test results from common frameworks (pytest, jest)
- **FR19:** System can detect workflow gaps (e.g., dev-story complete but code-review not run)

### AI Coach \u0026 Assistance

- **FR20:** User can access AI coach chat interface from anywhere in the dashboard (right sidebar)
- **FR21:** User can ask project-aware questions to the AI coach (knows current phase, epic, story)
- **FR22:** User can receive AI-suggested next workflows based on current project state
- **FR23:** User can view suggested prompts for common questions (displayed in AI coach panel)
- **FR24:** User can copy BMAD workflow commands with one click from AI suggestions
- **FR25:** User can view streaming AI responses (tokens appear as generated, not after full response)
- **FR26:** User can view AI validation of agent outputs (comparing story claims vs. Git/test reality)
- **FR27:** User can receive AI-detected workflow gap warnings (e.g., "Story marked done but no tests found")
- **FR28:** System can integrate with current BMAD Method documentation (docs.bmad-method.org)
- **FR29:** System can detect BMAD Method version updates and refresh documentation context
- **FR30:** System can provide accurate workflow suggestions based on latest BMAD Method best practices

### View Management \u0026 Cognitive Adaptation

- **FR31:** User can switch between Dashboard view (full context with breadcrumbs, Quick Glance, Kanban)
- **FR32:** User can switch to Timeline view (visual workflow history over time)
- **FR33:** User can switch to List view (minimal display for brain fog days)
- **FR34:** User can view stories organized in Kanban columns (TODO, IN PROGRESS, REVIEW, COMPLETE)
- **FR35:** User can see unified Action Cards combining Story + Task + Command in single UI element
- **FR36:** User can manually trigger dashboard refresh (re-parse BMAD artifacts and update display)
- **FR37:** System can persist user's last selected view mode across sessions
- **FR38:** System can maintain 60fps performance during view transitions

### BMAD Artifact Intelligence

- **FR39:** System can parse sprint-status.yaml to extract project status and story states
- **FR40:** System can parse epics.md to extract epic definitions and story lists
- **FR41:** System can parse individual story files to extract tasks, acceptance criteria, and status
- **FR42:** System can detect current BMAD phase from artifact analysis (sprint-status, frontmatter)
- **FR43:** System can identify current epic from project-level indicators
- **FR44:** System can identify current story from in-progress markers or most recent activity
- **FR45:** System can identify current task within active story
- **FR46:** System can track file modification timestamps for stories and artifacts
- **FR47:** System can correlate Git commits to specific stories based on commit messages
- **FR48:** System can detect test files associated with stories

### Workflow Execution Support

- **FR49:** User can view three-layer action guidance (Story level, Task level, Command level)
- **FR50:** User can copy suggested BMAD workflow commands to clipboard with one click
- **FR51:** User can view context-specific commands based on current story state (e.g., `/bmad-bmm-workflows-dev-story`)
- **FR52:** User can view workflow history showing execution sequence (dev-story  code-review  etc.)
- **FR53:** System can suggest correct next workflow based on story state and BMAD Method best practices
- **FR54:** System can detect missing workflow steps in the execution sequence

### User Experience \u0026 Accessibility

- **FR55:** User can view dashboard in dark theme (reduced visual fatigue)
- **FR56:** User can interact with all features via mouse clicks (no keyboard shortcut requirements)
- **FR57:** User can view high-contrast color-coded indicators (green/red/yellow distinctly visible)
- **FR58:** User can expand details on demand (progressive disclosure - overview always visible, details hidden until clicked)
- **FR59:** System can load and display dashboard in \u003c500ms from startup
- **FR60:** System can maintain responsive UI during Git parsing and test discovery operations


## Non-Functional Requirements

### Performance

**Critical Performance Targets** (already defined in Success Criteria and Web App requirements):

- **NFR1:** Dashboard startup (page load to interactive) must complete in \u003c500ms
- **NFR2:** BMAD artifact parsing (sprint-status.yaml, epics.md, story files) must complete in \u003c500ms
- **NFR3:** Phase detection algorithm must execute in \u003c100ms
- **NFR4:** View transitions (Dashboard  Timeline  List) must maintain 60fps with \u003c100ms completion time
- **NFR5:** Modal expansion (Git badge, Test badge) must feel instant (\u003c50ms response time)
- **NFR6:** AI coach streaming must deliver first token within \u003c200ms of request
- **NFR7:** Manual refresh (re-parse artifacts) must complete in \u003c300ms
- **NFR8:** Frontend memory usage must remain \u003c100MB during normal operation
- **NFR9:** No memory leaks during view switching or modal open/close operations

**Performance Rationale:**
- Instant feel (\u003c500ms) is CRITICAL for cognitive load reduction
- 60fps animations prevent visual jarring for users with brain fog
- Fast AI responses maintain conversation flow and reduce waiting anxiety

### Accessibility

**Assistive Technology Requirements:**

- **NFR10:** All interactive elements must have minimum click target size of 44x44px (easy clicking without precision)
- **NFR11:** Color-coded indicators must meet minimum contrast ratio of 4.5:1 ( green,  red,  yellow distinctly visible)
- **NFR12:** Dark theme must be default and enforced (no light mode option to avoid accidental switch)
- **NFR13:** All functionality must be accessible via mouse clicks only (no required keyboard shortcuts)
- **NFR14:** Text must use minimum 14px font size for readability
- **NFR15:** Progressive disclosure must keep overview visible at all times (no hidden critical information)
- **NFR16:** View mode selection must persist across sessions (user doesn't re-select List view on brain fog days)
- **NFR17:** No time-limited interactions (no auto-dismiss notifications or timed actions)
- **NFR18:** No animations that flash or strobe (seizure risk for users with MS)

**Accessibility Rationale:**
- Cognitive load management is the PRIMARY product goal
- Tool must adapt to user's cognitive state, not demand adaptation from user
- Assistive tech approach prioritized over WCAG checklist compliance

### Reliability \u0026 Graceful Degradation

**Layered Architecture Resilience:**

- **NFR19:** Core Layer (breadcrumbs, phase detection, Quick Glance) must function without AI coach operational
- **NFR20:** Validation Layer (Git correlation, test discovery) must function without AI coach operational
- **NFR21:** If Gemini 3 Flash API unavailable, core navigation and validation features remain functional
- **NFR22:** If Git commits use unexpected formats, system falls back to file modification time-based status
- **NFR23:** If test discovery fails, system allows manual test status entry or shows "unknown" instead of crashing
- **NFR24:** If BMAD artifact parsing encounters unknown formats, system shows "Unknown" state rather than error
- **NFR25:** System must never lose user's view mode preference due to errors

**Reliability Rationale:**
- Solo user depends on tool daily - graceful degradation prevents total failure
- Layered value architecture (Layer 1  2  3) ensures partial functionality on failures
- Error handling prioritizes "keep working with less features" over "crash completely"

### Maintainability

**Solo Developer Constraints:**

- **NFR26:** Codebase must use vanilla JavaScript/CSS (no framework learning curve or dependency maintenance)
- **NFR27:** Backend must use Flask with minimal dependencies (Python standard library preferred)
- **NFR28:** No complex build pipeline required for development or deployment (serve static files directly)
- **NFR29:** Code architecture must support AI coding agent assistance (clear module boundaries, minimal magic)
- **NFR30:** Configuration must be file-based (no database setup required)
- **NFR31:** Deployment must be localhost-only (no server, DNS, SSL, or hosting infrastructure)

**Maintainability Rationale:**
- Solo developer with MS needs low-maintenance architecture
- Vanilla stack reduces dependency updates and breaking changes
- AI coding agents can more easily work with simple, explicit code
- BMAD Dash development should use BMAD Method itself (self-dogfooding)

### Integration

**BMAD Method Ecosystem Integration:**

- **NFR32:** System must parse current BMAD Method artifact formats (sprint-status.yaml, epics.md, story files)
- **NFR33:** System must detect and adapt to BMAD Method version changes in project config
- **NFR34:** System must integrate with BMAD Method documentation (docs.bmad-method.org) for AI coach context
- **NFR35:** System must support Gemini 3 Flash API for AI coach functionality
- **NFR36:** System must execute Git commands for commit correlation (git log with pattern matching)
- **NFR37:** System must detect common test frameworks (pytest for Python, jest for JavaScript/TypeScript)

**Integration Rationale:**
- BMAD Dash exists within BMAD Method ecosystem
- Tight integration with BMAD artifacts is core value proposition
- AI coach effectiveness depends on current BMAD Method documentation access

