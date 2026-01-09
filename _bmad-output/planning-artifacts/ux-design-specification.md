---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: ['f:/BMAD Dash/_bmad-output/planning-artifacts/prd.md', 'f:/BMAD Dash/_bmad-output/analysis/brainstorming-session-2026-01-08.md', 'f:/BMAD Dash/Docs/BMAD Dash.txt']
---

# UX Design Specification {{project_name}}

**Author:** {{user_name}}
**Date:** {{date}}

---

<!-- UX design content will be appended sequentially through collaborative workflow steps -->

## Executive Summary

### Project Vision

BMAD Dash is an "AI Agent Orchestration Auditor" - a localhost web dashboard that serves as assistive technology for developers managing BMAD Method projects. It eliminates cognitive friction when returning to multi-phase, AI-agent-orchestrated projects after breaks, providing instant re-orientation, quality validation through verifiable evidence, and zero-friction next-step execution.

The product addresses a unique challenge at the intersection of AI-assisted development and cognitive accessibility: developers with MS/brain fog need to trust AI agent work without manual verification while managing complex project state across multiple phases, epics, stories, and tasks.

### Target Users

**Primary User: Gary**
- **Role:** Intermediate-level developer with MS and occasional brain fog
- **Context:** Managing multiple BMAD Method projects (Echo-OS, BMAD Dash itself) with AI coding agent assistance
- **Pain Points:** 
  - Cognitive overhead of reconstructing "where am I?" after overnight breaks or between sessions
  - Uncertainty about whether AI agents actually completed work they claimed to complete
  - Decision paralysis about "what do I do next?" without explicit guidance
- **Success Criteria:** Can return to any BMAD project and know exact position + next action within 10 seconds, without manual verification or mental reconstruction

**User Cognitive States:**
- **Clarity Days:** Full cognitive capacity - can handle breadcrumbs, Kanban, progress bars, detailed information
- **Brain Fog Days:** Limited cognitive bandwidth - needs minimal information (List view), larger text, fewer decisions

**Key User Characteristics:**
- Prefers copy-paste workflows over complex terminal interactions
- Values visual indicators over keyboard shortcuts (memory burden)
- Needs tool to adapt to cognitive state, not vice versa
- Uses Edge browser on Windows primarily

### Key Design Challenges

**1. Cognitive Load Balancing**

Must provide enough information for instant orientation (Project  Phase  Epic  Story  Task hierarchy) without overwhelming the user, especially on brain fog days. This requires surgical precision in:
- Information hierarchy (what's always visible vs. expandable on demand)
- Visual density (spacing, grouping, progressive disclosure)
- Adaptive complexity (Dashboard view vs. List view cognitive load difference)

**Design Tension:** Completeness vs. Simplicity - User needs comprehensive context but can't handle dense information walls on challenging days.

**2. Trust Indicator Design**

Git commit validation and test execution status badges must build instant credibility. Color coding ( green,  red,  yellow), timestamps, and expandable details need to:
- Communicate status at a glance (no reading required)
- Support deeper investigation without leaving main view
- Never show false positives (trust depends on 100% accuracy)
- Feel objective and machine-generated (not subjective human claims)

**Design Tension:** Glanceable vs. Verifiable - Must be instantly scannable while providing detailed proof on demand.

**3. Adaptive Coherence**

Three view modes (Dashboard/Timeline/List) serve different cognitive states but must feel like one cohesive product:
- **Dashboard:** Full context with breadcrumbs, Quick Glance Bar, Kanban, AI coach sidebar
- **Timeline:** Visual workflow history to understand project progression over time
- **List:** Minimal display showing only current task and next action

Users switching from Dashboard to List on brain fog days shouldn't feel they're using a "different app." Visual language, interaction patterns, and mental model must remain consistent.

**Design Tension:** Consistency vs. Adaptation - Same product identity across radically different information densities.

**4. Performance Perception**

\u003c500ms startup is a hard requirement for assistive technology. UI must feel instant:
- 60fps view transitions (no janky animations that jar cognitively)
- \u003c50ms modal expansion (Git/test badge details)
- \u003c200ms AI streaming first token (conversation flow maintained)

Waiting creates cognitive load and anxiety. Every millisecond delay compounds the mental friction we're trying to eliminate.

**Design Tension:** Rich Features vs. Instant Feel - Comprehensive functionality without performance compromise.

### Design Opportunities

**1. Pioneer Assistive Tech UX for Developers**

Opportunity to create new design patterns specifically for developers with cognitive challenges. This hasn't been done before - existing developer tools (IDEs, project trackers, CI dashboards) assume neurotypical cognitive capacity.

**Innovation Area:** Cognitive state-adaptive interfaces for technical users. Could establish patterns applicable to broader developer accessibility movement.

**2. Verifiable Evidence UI Pattern**

Innovate on "proof, not promises" interface design. Instead of generic status indicators ( Done), show machine-checkable evidence:
- Actual Git commit messages (not just "commits exist")
- Actual test pass/fail counts with timestamps (not just "tests passing")
- Actual workflow execution history (which BMAD agents ran, when)

**Innovation Area:** Trust-building interfaces for AI-assisted work validation. Could influence how future dev tools present AI agent outputs.

**3. AI Agent Validation Interface**

Create the first user interface specifically for validating AI coding agent outputs. The combination of:
- Sidebar AI coach with project-aware context
- Workflow gap detection (dev-story done but no code-review)
- Evidence correlation (story claims vs. Git/test reality)
- Streaming responses for natural conversation

...represents a new UX category that didn't exist before AI coding agents reached production quality.

**Innovation Area:** Human-AI collaboration interfaces for code quality assurance. First-mover advantage in emerging space.

**4. BMAD Method Dashboard Standard**

Opportunity to define THE reference UX for BMAD Method project dashboards, creating value beyond personal use:
- Establish visual language for BMAD phases, epics, stories, tasks
- Create interaction patterns for BMAD artifact visualization
- Define standard for BMAD workflow orchestration UIs
- Potentially useful for broader BMAD Method community adoption


## Core User Experience

### Defining Experience

**The "Return to Project" Core Loop:**

BMAD Dash's core experience is built around the daily ritual of returning to a BMAD project after breaks (overnight, between sessions, after interruptions). This interaction happens multiple times per day and defines the product's entire value proposition.

**The Perfect Return Experience (3-10 seconds):**
1. User opens BMAD Dash in browser tab
2. Dashboard loads instantly (\u003c500ms) with breadcrumb navigation and Quick Glance Bar visible
3. User scans current position (Project  Phase  Epic  Story  Task) and temporal context (Done | Current | Next)
4. User sees suggested workflow command in Action Card
5. User clicks [Copy Command] button
6. User pastes into Antigravity chat and starts work

**If this core loop fails, the entire assistive technology value collapses.** Every design decision must optimize for this 3-10 second flow.

### Platform Strategy

**Web Application (Localhost)**
- Flask backend serving API + static HTML/CSS/JavaScript
- Edge browser (latest Chromium) on Windows as primary target
- Desktop-optimized viewports (1920x1080 primary, 1366x768 minimum)
- Single-page application with client-side routing (no page reloads)
- Always-online (localhost, no offline mode required)

**Interaction Model:**
- Mouse-driven interface (click-based, no touch gestures)
- No keyboard shortcuts (eliminates memory burden for accessibility)
- All functionality accessible via clicks (progressive disclosure through expandable elements)

**Performance as Platform Requirement:**
- \u003c500ms startup (Flask parse + frontend render)
- 60fps UI transitions (cognitive load sensitivity requires smooth animations)
- \u003c50ms modal expansion (feels instant, no perceived delay)
- \u003c200ms AI streaming first token (maintains conversation flow)

### Effortless Interactions

**1. Status Scanning (Zero Reading Required)**
- Color-coded badges ( green,  red,  yellow) communicate status at a glance
- No text parsing needed - pattern recognition sufficient for orientation
- High contrast ensures instant recognition even on brain fog days

**2. Evidence Inspection (One-Click Verification)**
- Click Git badge  modal expands with actual commit messages
- Click Test badge  modal shows pass/fail count + timestamp + results
- Close modal  return to exact dashboard position (no navigation, no context loss)
- **Delight moment:** Seeing ACTUAL commits (not just "commits exist") feels like x-ray vision into project truth

**3. Command Execution (Copy-Paste Workflow)**
- See "Run: `/bmad-bmm-workflows-dev-story`" in Action Card
- Click [Copy Command] button  clipboard populated
- Paste into Antigravity  command executes immediately
- No typing, no memorization, no decision paralysis

**4. Cognitive Adaptation (Instant UI Simplification)**
- Brain fog sets in  Click "List" view button
- UI instantly transforms to minimal display (current task + next action only)
- \u003c100ms transition maintains 60fps smoothness
- No configuration dialogs, no lost context, no decisions required

**5. AI Assistance (Streaming Conversation)**
- Type question in sidebar chat  streaming response appears token-by-token
- AI suggests workflows with context ("Story 1.5 complete, run `/bmad-bmm-workflows-code-review`")
- Code blocks include one-click copy buttons
- No waiting for full response - conversation feels natural

### Critical Success Moments

**1. The "Dashboard Open" Moment (First 3 Seconds)**
- **Trigger:** User opens BMAD Dash browser tab after break
- **Success Criteria:** 
  - Breadcrumb + Quick Glance Bar visible immediately
  - Current position clear (Phase, Epic, Story, Task)
  - Load time \u003c500ms (no spinner, no perceived wait)
- **Why Make-or-Break:** If orientation takes \u003e3 seconds or feels slow, tool creates cognitive load instead of eliminating it. Core purpose fails.

**2. The "Trust Validation" Moment**
- **Trigger:** User clicks Git or Test badge to verify AI agent work
- **Success Criteria:**
  - Modal expands \u003c50ms (feels instant)
  - Shows actual commit messages or test results (not summary)
  - Timestamp proves recency ("Tests: 24/24 passing, ran 2h ago")
- **Why Make-or-Break:** This is where "Quality Trust Gap" is solved or perpetuated. One false positive destroys trust permanently. Accuracy must be 100%.

**3. The "Brain Fog Rescue" Moment**
- **Trigger:** User experiencing high cognitive load clicks "List" view
- **Success Criteria:**
  - UI simplifies to show only current task + next action
  - Transition \u003c100ms, maintains 60fps
  - Dark theme, large text, minimal decisions
- **Why Make-or-Break:** Assistive tech must adapt to user's cognitive state. If List view doesn't provide relief, tool fails users on their most challenging days.

**4. The "Command Execution" Moment**
- **Trigger:** User sees suggested workflow command, clicks [Copy]
- **Success Criteria:**
  - One-click copy to clipboard
  - Command format correct for direct Antigravity execution
  - No manual editing required
- **Why Make-or-Break:** "Zero-friction execution" - any friction creates decision paralysis the tool is meant to eliminate. From dashboard to executing work must be \u003c10 seconds total.

### Experience Principles

**Guiding Principles for All UX Decisions:**

**1. Instant Orientation Over Comprehensive Information**
- Show just enough context for immediate understanding (breadcrumbs, Quick Glance Bar, current task)
- Use progressive disclosure for deeper investigation (expandable badges, modal details)
- **Priority:** User knows "where am I" within 3 seconds, not "here's everything about the project"

**2. Proof Over Promises**
- Display objective, machine-checkable evidence (actual commits, actual test results with timestamps)
- Never show status without verifiable backing (Git  means commits exist, not "Git is configured")
- **Trust is earned through transparency, not asserted through checkboxes**

**3. Adapt to User, Not Vice Versa**
- Tool changes based on cognitive state (Dashboard  List view on brain fog days)
- No configuration burden, no memorization required (no keyboard shortcuts to remember)
- **Interface serves user's current capacity, not their ideal capacity**

**4. Zero-Friction Execution**
- Every user action completes in 1 click maximum (copy command, expand badge, switch view)
- Eliminate decision points that cause paralysis (AI suggests exact workflow, not options menu)
- **Waiting creates cognitive load** - performance IS UX (60fps, \u003c500ms startup, \u003c50ms modals)

**5. Graceful Degradation Maintains Value**
- If AI fails, core navigation still works (breadcrumbs, Quick Glance, Kanban)
- If Git correlation fails, file timestamps provide fallback status
- **Partial functionality better than complete failure** - never block user from making progress


## Desired Emotional Response

### Primary Emotional Goals

**Core Emotional Experience: From Anxiety to Confidence in \u003c10 Seconds**

BMAD Dash's primary emotional objective is **relief** - the lifting of cognitive burden when returning to complex projects. Users should transition from "Where was I? What's done? What's next?" (anxiety/confusion) to "I know exactly where I am and what to do" (calm/confidence) within 3-10 seconds.

**Primary Emotions:**
- **Relief** - "I don't have to reconstruct my mental model of the project"
- **Confidence** - "I can trust this status is accurate because I can verify it"
- **Calm** - "I know exactly what to do next, no decision paralysis"
- **Empowered** - "This tool adapts to me (brain fog days), I don't have to adapt to it"

**Differentiating Emotional Quality:**

The key emotion that separates BMAD Dash from competitors is **trust through transparency**. Traditional project trackers evoke "hopeful skepticism" - users see status indicators but don't fully trust them without manual verification. BMAD Dash should evoke **verified certainty** - status is backed by machine-checkable evidence (actual commits, actual tests, actual timestamps).

**Success Emotion:**

When users tell others about BMAD Dash, the feeling should be **"This tool saved me"** - more profound than "this is cool" or "this is useful." For developers with cognitive challenges, the tool addresses a genuine pain point. The emotion is gratitude + relief, not just satisfaction.

### Emotional Journey Mapping

**1. First Discovery (Initial Setup)**
- **Emotional State:** Cautious optimism  "Will this actually help or is it another thing to manage?"
- **Design Goal:** Prove value within first 10 seconds of use
- **Success Moment:** User opens dashboard, sees instant project orientation, realizes "I didn't have to reconstruct anything"

**2. Daily Return to Project (Core Loop)**
- **Emotional Transition:** Anxiety  Calm  Trust  Readiness
- **Journey Flow:**
  - **Before opening:** Low-level anxiety ("I need to figure out where I left off")
  - **Dashboard loads:** Immediate calm (breadcrumbs + Quick Glance Bar visible)
  - **Status scan:** Trust builds (Git , Tests , green badges)
  - **Action ready:** Confidence ("I can copy this command and start work now")
- **Design Goal:** Each step reinforces positive emotion, eliminates friction

**3. Trust Validation Check (Evidence Inspection)**
- **Emotional State:** Skepticism  Verification  Trust
- **Journey Flow:**
  - User questions: "Did the AI agent actually complete this?"
  - Clicks Git badge  Modal shows actual commit messages
  - Reads evidence  Trust restored ("This is objectively true")
- **Design Goal:** Make verification effortless and conclusive

**4. Error or Failure State (Red Badges)**
- **Emotional State:** Informed concern (not panic)
- **Journey Flow:**
  - User sees red Test badge (5/24 tests failing)
  - Clicks badge  Modal shows which tests failed, when
  - User has actionable information, not vague anxiety
- **Design Goal:** Show objective state without creating panic. User should feel "I know what's wrong" not "Something broke and I don't know what"

**5. Brain Fog Day (Cognitive Adaptation)**
- **Emotional State:** Overwhelmed  Relieved
- **Journey Flow:**
  - User experiencing high cognitive load
  - Clicks "List" view  Dashboard simplifies instantly
  - Relief: "The tool adapted to me, I didn't have to struggle"
- **Design Goal:** Tool responsiveness to cognitive state builds trust and dependence

**6. Habitual Use (Long-term Relationship)**
- **Emotional State:** Positive dependence  "I need this daily"
- **Success Indicator:** Tool becomes invisible infrastructure - user doesn't consciously think about it, just relies on it
- **Design Goal:** BMAD Dash becomes part of daily workflow ritual, feels essential not optional

### Micro-Emotions

**Critical Micro-Emotional States (Make-or-Break):**

**1. Confidence \u003e Confusion** (CRITICAL)
- **Why:** Cognitive accessibility depends on instant clarity
- **Design Support:** Clear visual hierarchy, breadcrumbs always visible, temporal orientation (Done | Current | Next) unambiguous
- **Failure Mode:** If user has to "figure out" the dashboard, assistive tech value collapses

**2. Trust \u003e Skepticism** (CRITICAL)
- **Why:** "Quality Trust Gap" innovation lives or dies on this
- **Design Support:** Verifiable evidence (actual commits, actual tests), 100% accuracy or show "unknown" state, timestamps prove recency
- **Failure Mode:** One false positive destroys trust permanently

**3. Calm \u003e Anxiety** (CRITICAL)
- **Why:** Tool's purpose is to reduce cognitive load, not increase it
- **Design Support:** Dark theme, no flashing notifications, no time-limited actions, performance feels instant (\u003c500ms)
- **Failure Mode:** Waiting or friction creates anxiety the tool is meant to eliminate

**4. Accomplishment \u003e Frustration** (HIGH)
- **Why:** Zero-friction execution creates flow state
- **Design Support:** One-click command copy, AI suggests exact workflow (no option paralysis), evidence inspection is one click
- **Failure Mode:** Extra clicks or decisions compound cognitive load

**5. Delight \u003e Satisfaction** (MODERATE)
- **Why:** Nice-to-have but not required for assistive tech success
- **Design Support:** Git badge "x-ray vision" moment, smooth 60fps transitions, streaming AI responses
- **Note:** Delight reinforces emotional connection but isn't core requirement

**6. Belonging \u003e Isolation** (NOT APPLICABLE)
- **Why:** Personal tool, not social product
- **Note:** Skipped - no community or collaboration features in MVP

### Design Implications

**Emotion-Driven UX Decisions:**

**Relief (Cognitive Burden Lifted)**
- **Design Choice:** Breadcrumb navigation always visible at top (never scroll to find position)
- **Design Choice:** Quick Glance Bar shows Done | Current | Next without interaction
- **Design Choice:** \u003c500ms startup means no waiting-induced anxiety
- **Rationale:** User should never have to "work" to understand where they are

**Confidence (Trust Through Transparency)**
- **Design Choice:** Color-coded badges link to actual evidence ( Git = click to see commits)
- **Design Choice:** 100% accuracy requirement - show "Unknown" state rather than false positive
- **Design Choice:** Timestamps on all status indicators (tests ran 2h ago, not just "passing")
- **Rationale:** Trust is earned through verifiable proof, not asserted through checkboxes

**Calm (Decision Paralysis Eliminated)**
- **Design Choice:** AI coach suggests ONE workflow command, not multiple options menu
- **Design Choice:** Action Card shows exact next step (Story + Task + Command)
- **Design Choice:** Dark theme, no auto-dismiss notifications, no time-pressure interactions
- **Rationale:** Every decision point creates cognitive load - minimize choices

**Empowered (Adaptation to User)**
- **Design Choice:** Three view modes (Dashboard/Timeline/List) with persistent state across sessions
- **Design Choice:** List view accessible via one click (no configuration dialogs)
- **Design Choice:** No keyboard shortcuts to memorize (mouse-only interactions)
- **Rationale:** Tool changes to match user's cognitive state - no adaptation burden on user

**Trust (Verification Without Friction)**
- **Design Choice:** \u003c50ms modal expansion feels instant (no perceived delay)
- **Design Choice:** Modals show actual commit messages, actual test output, actual error logs
- **Design Choice:** Evidence is one click away, never requires navigation or context loss
- **Rationale:** Verification should be effortless - if it's hard to check, users won't trust it

**Moments of Delight (Strategic Enhancement):**

1. **Git Badge Reveal** - Expanding to see actual commit messages feels like gaining x-ray vision into project truth
2. **AI Streaming Response** - Tokens appearing smoothly (not waiting for full response) creates conversational intimacy
3. **60fps View Transitions** - Smooth animations feel premium and reduce visual jarring on brain fog days

### Emotional Design Principles

**Guiding Principles for Emotional UX:**

**1. Eliminate Negative Emotions Before Creating Positive Ones**
- For assistive technology, absence of frustration/anxiety/confusion is more important than presence of delight
- **Priority Order:** Remove barriers first (cognitive load, friction, waiting), add delight second
- **Design Test:** "Does this create any negative emotion?" trumps "Does this create delight?"

**2. Trust is Earned Through Transparency, Never Asserted**
- Every status claim must be verifiable with one click
- Show objective evidence (commits, tests, timestamps) not subjective assessments ("looks good")
- **Design Principle:** If we can't prove it with machine-checkable evidence, show "Unknown" state

**3. Performance IS Emotional Design**
- Waiting creates anxiety - \u003c500ms startup is emotional requirement, not just technical
- Smooth 60fps animations reduce visual jarring (critical for brain fog sensitivity)
- **Design Principle:** Every millisecond of delay compounds cognitive load and erodes calm

**4. Adapt to User's State, Never Demand Adaptation**
- Brain fog days require different interface (List view) - tool must change, user shouldn't struggle
- No memorization required (keyboard shortcuts), no configuration burden
- **Design Principle:** Interface serves user's current capacity, not their ideal capacity

**5. Zero-Friction Execution Builds Flow State**
- Every extra click or decision interrupts momentum
- One-click actions (copy command, expand badge, switch view) eliminate decision paralysis
- **Design Principle:** User should go from "open dashboard" to "executing work" in \u003c10 seconds total


## UX Pattern Analysis \u0026 Inspiration

### Inspiring Products Analysis

**1. Things 3 (Task Manager) - Complexity Without Overwhelm**

**UX Excellence:**
- Temporal organization: "Today" view shows only what matters now, reducing decision paralysis
- Progressive disclosure: Inbox  Today  Projects (simple first, complexity on demand)
- Single-action focus: Each task has ONE next action, no option menus
- Dark mode mastery: Clean, calm aesthetic with minimal visual noise
- Instant task capture: Quick entry form creates zero friction for adding tasks

**Relevance to BMAD Dash:**
Things 3 proves that handling complexity doesn't require showing everything at once. Their "Today" view model directly inspired Quick Glance Bar (Done | Current | Next) - focus on temporal position over comprehensive project display.

**2. Calm (Meditation App) - Cognitive State Design**

**UX Excellence:**
- Reduces visual stimulation: Dark backgrounds, gentle colors, no sudden movements
- No time pressure: No countdowns, no urgency cues, user controls all pacing
- Gentle animations: Slow, smooth transitions that never jar or startle
- Minimal decisions: "Start session" button - one clear action path
- Ambient calm: Creates soothing environment through design restraint

**Relevance to BMAD Dash:**
Calm demonstrates how UI can actively reduce cognitive load rather than adding to it. Their dark calm aesthetic and "no urgency cues" philosophy directly supports BMAD Dash's assistive technology mission for users with brain fog.

**3. GitKraken (Git GUI) - Evidence Visualization**

**UX Excellence:**
- Visual commit history: Timeline shows actual commits with messages, authors, timestamps
- One-click drill-down: Click commit  see exactly what changed (files + code diffs)
- Branch visualization: Complex Git graphs made comprehensible through visual design
- Color-coded status: Green/red/yellow branches communicate state at pattern-recognition level
- Timestamp prominence: "2h ago" shown clearly (recency proves data freshness)

**Relevance to BMAD Dash:**
GitKraken's expandable evidence pattern (summary  click  full detail) is EXACTLY what BMAD Dash needs for Git/Test badges. Their proof is in showing actual commits, not just "commits exist" - this implements "trust through transparency."

**4. macOS Focus Modes - Adaptive UI**

**UX Excellence:**
- Instant state switching: Control Center  Focus Mode  UI adapts immediately
- Persistent preferences: Mode settings save (user never reconfigures)
- Visual mode feedback: System UI changes to indicate active mode
- No configuration burden: Pre-configured modes (Do Not Disturb, Work, Sleep)
- Contextual suggestions: System proposes mode based on time/activity

**Relevance to BMAD Dash:**
macOS proves that UI can adapt to user state without configuration dialogs. Their one-click mode switching (with persistent preferences the user doesn't have to manually save) directly inspired BMAD Dash's Dashboard/Timeline/List view system for cognitive state adaptation.

### Transferable UX Patterns

**Navigation Patterns:**

**1. Temporal Focus (from Things 3)**
- **Pattern:** "Today" view prioritizes immediate context over comprehensive project view
- **BMAD Dash Adaptation:** Quick Glance Bar (Done | Current | Next) shows temporal position first, full hierarchy second
- **Why Effective:** Brain fog days need "what NOW" not "show me everything"

**2. Progressive Hierarchy (from Things 3 + GitKraken)**
- **Pattern:** Breadcrumbs show full path, display shows current level detail
- **BMAD Dash Adaptation:** Breadcrumb (Project  Phase  Epic  Story  Task) always visible, main view shows current Story's tasks (not all stories simultaneously)
- **Why Effective:** Provides context without overwhelm - user knows position without seeing everything at once

**3. One-Click Drill-Down (from GitKraken)**
- **Pattern:** Click commit  detail panel expands in-place (no navigation away)
- **BMAD Dash Adaptation:** Click Git/Test badge  modal expands over dashboard  close returns to exact scroll position
- **Why Effective:** Investigation without losing place - critical for cognitive load management

**Interaction Patterns:**

**4. Single-Path Actions (from Calm + Things 3)**
- **Pattern:** One button, one clear outcome ("Start Meditation" / "Add to Today")
- **BMAD Dash Adaptation:** [Copy Command] button (not "Copy" vs "Edit" vs "View Details" menu)
- **Why Effective:** Eliminates decision paralysis - user knows exactly what clicking does

**5. Persistent State (from macOS Focus Modes)**
- **Pattern:** Mode selection saves, doesn't reset on app restart
- **BMAD Dash Adaptation:** View mode (Dashboard/Timeline/List) persists across browser sessions
- **Why Effective:** Brain fog days repeat - don't make user re-select List view daily

**6. Instant Mode Switching (from macOS Focus Modes)**
- **Pattern:** Control Center  Focus  UI adapts immediately (\u003c100ms)
- **BMAD Dash Adaptation:** Click "List" view  Dashboard transforms instantly (60fps transition, \u003c100ms completion)
- **Why Effective:** Cognitive state changes quickly - tool must match that responsiveness

**Visual Patterns:**

**7. Dark Calm Aesthetic (from Calm + Things 3)**
- **Pattern:** Dark backgrounds, subtle gradients, generous whitespace, muted accent colors
- **BMAD Dash Adaptation:** Dark theme with deep gray backgrounds (#1a1a1a), white text, muted green/red/yellow badges
- **Why Effective:** Reduces visual fatigue and glare sensitivity (MS symptom management)

**8. Color-Coded Status Without Reading (from GitKraken)**
- **Pattern:** Green/Red/Yellow communicate state at pattern-recognition level (not text parsing)
- **BMAD Dash Adaptation:**  Git badge = green (good),  Tests badge = red (needs attention),  Unknown = yellow
- **Why Effective:** Scanning faster than reading - critical for instant orientation within 3-second target

**9. Generous Breathing Room (from Calm)**
- **Pattern:** Elements surrounded by whitespace (darkspace for dark themes), not packed densely
- **BMAD Dash Adaptation:** Kanban cards have padding, badges have margin, layouts avoid cramming
- **Why Effective:** Visual density increases cognitive load - space aids scanning and reduces overwhelm

**Evidence \u0026 Trust Patterns:**

**10. Timestamp Prominence (from GitKraken)**
- **Pattern:** "2h ago" or "Yesterday" shown next to every commit
- **BMAD Dash Adaptation:** Test badge shows "Tests: 24/24 passing, ran 2h ago" (recency proves freshness)
- **Why Effective:** Trust depends on knowing evidence is current, not stale - timestamps build confidence

**11. Expandable Detail Panel (from GitKraken)**
- **Pattern:** Summary view  click  full detail (commit message, diff, files changed)
- **BMAD Dash Adaptation:** Badge summary  click  modal (commit list with messages OR test results with failure details)
- **Why Effective:** Glanceable summary + verifiable evidence without leaving dashboard context

### Anti-Patterns to Avoid

**1. Jira/Linear Information Walls**
- **Anti-Pattern:** Show every field, every property, every option on one screen
- **Why Harmful:** Cognitive overwhelm - user drowns in irrelevant data when they just need to know "where am I?"
- **BMAD Dash Alternative:** Progressive disclosure - breadcrumbs + Quick Glance + Kanban (essentials), modals for details only when needed

**2. GitHub Actions "Endless Scrolling Logs"**
- **Anti-Pattern:** Test failures buried in 5000-line console output requiring manual searching
- **Why Harmful:** Finding information creates cognitive load instead of eliminating it
- **BMAD Dash Alternative:** Show summary (5/24 tests failing)  click  show WHICH tests failed with line references (not full console dump)

**3. Notion/Confluence "Configuration Hell"**
- **Anti-Pattern:** 47 settings, 12 view customizations, endless personalization options
- **Why Harmful:** Decision fatigue from configuration, not from actually using the tool
- **BMAD Dash Alternative:** Three pre-configured views (Dashboard/Timeline/List), persistent state, zero settings menus to navigate

**4. Slack "Notification Anxiety"**
- **Anti-Pattern:** Red badges, @ mentions, unread counts create constant urgency pressure
- **Why Harmful:** Creates anxiety the tool is meant to eliminate - opposite of calm cognitive state
- **BMAD Dash Alternative:** No notifications, no urgency cues, no "unread" counts, user controls all timing and refresh

**5. Traditional Kanban "Drag-and-Drop Complexity"**
- **Anti-Pattern:** Stories move between columns via dragging - requires motor precision + mental state management
- **Why Harmful:** Motor precision challenge for some MS users, unnecessary interaction complexity
- **BMAD Dash Alternative:** Stories auto-position based on BMAD artifact status (sprint-status.yaml) - no manual dragging needed

**6. IDEs "Keyboard Shortcut Dependence"**
- **Anti-Pattern:** VSCode power users memorize 50+ keyboard shortcuts for efficiency
- **Why Harmful:** Memory burden incompatible with brain fog - shortcuts forgotten between sessions
- **BMAD Dash Alternative:** All functionality via mouse clicks, no shortcuts to remember (intentionally less "efficient" but more accessible)

**7. Jira "Multi-Step Workflow Transitions"**
- **Anti-Pattern:** Update story status requires: Click story  Click transition  Select workflow  Add comment  Confirm
- **Why Harmful:** Friction compounds cognitive load - each extra step creates decision point
- **BMAD Dash Alternative:** Status auto-updates from Git/test evidence parsing (no manual workflow needed)

### Design Inspiration Strategy

**What to Adopt Directly (Use As-Is):**

-  **Things 3's "Today" focus**  Quick Glance Bar (Done | Current | Next) for temporal orientation
-  **Calm's dark aesthetic**  Dark theme with generous breathing room and muted colors
-  **GitKraken's expandable evidence**  Click badge  modal with actual commit/test data
-  **macOS Focus Modes' instant switching**  One-click view mode changes with \u003c100ms transitions

**What to Adapt (Modify for BMAD Dash Context):**

-  **Things 3's "Headings" grouping**  Adapt to Kanban columns (TODO, IN PROGRESS, REVIEW, DONE) for story organization
-  **GitKraken's commit timeline**  Adapt to Timeline view (workflow execution history, not just commits)
-  **Calm's user-controlled pacing**  Adapt to "no auto-refresh" (user manually triggers dashboard update)

**What to Avoid (Conflicts with Design Goals):**

-  **Jira's information density**  Conflicts with cognitive load reduction mission
-  **Slack's urgency cues**  Conflicts with calm/anxiety-free emotional design goals
-  **Notion's configuration complexity**  Conflicts with zero-friction execution principle

**Unique to BMAD Dash (Novel Patterns, Not Borrowed):**

-  **Verifiable evidence badges** - Git/Test correlation with actual commit/test data (unique to AI agent validation use case)
-  **Three-tier Action Card** - Story + Task + Command unified in single UI element (not seen in other tools)
-  **BMAD Method phase awareness** - Automatic phase detection and workflow gap detection (specific to BMAD ecosystem)
-  **Cognitive state adaptation** - Three distinct views serving different brain fog levels (assistive tech innovation)

**Integration Strategy:**

This analysis establishes BMAD Dash's design foundation: **Adopt proven cognitive load patterns (Things 3, Calm), adapt evidence visualization excellence (GitKraken), avoid common productivity tool pitfalls (Jira, Slack), and innovate where BMAD Method + AI agent validation creates unique needs.**

Every borrowed pattern serves the core mission: eliminate cognitive friction for developers with MS/brain fog managing AI-assisted BMAD projects.


## Design System Foundation

### Design System Choice

**Selected: Tailwind CSS (Utility-First Framework)**

BMAD Dash will use Tailwind CSS as its design system foundation. This choice prioritizes rapid development speed while maintaining full design control for assistive technology requirements.

### Rationale for Selection

**Speed to Working UI (Primary Driver):**
- Dark theme implementation is trivial (`dark:` prefix on utilities)
- Responsive layouts with grid/flexbox utilities avoid manual media queries
- Color-coded badges use semantic color classes (`bg-green-500`, `bg-red-500`, `bg-yellow-500`)
- Transitions and animations built-in (`transition-all duration-100`)
- No need to write repetitive CSS for common patterns

**Assistive Technology Compatibility:**
- Full control over spacing (`p-4`, `gap-2`) for generous breathing room
- Precise color control for high-contrast requirements
- Custom utilities can be added for BMAD-specific needs
- No component opinions - we build exactly what we need

**Maintenance Considerations:**
- Single dependency (minimal compared to full frameworks)
- Stable API (Tailwind v3+ has mature, consistent patterns)
- AI coding agents familiar with Tailwind (easier for Cursor/Claude assistance)
- JIT compiler generates only used CSS (small bundle size)

**Tradeoffs Accepted:**
- One npm dependency vs. zero (vanilla CSS)
- Learning utility class names (acceptable for faster development)
- Build step required (acceptable for localhost tool)

### Implementation Approach

**Tailwind Configuration:**

1. **Installation:** `npm install -D tailwindcss`
2. **Config file:** `tailwind.config.js` with dark mode enabled
3. **Build:** Tailwind CLI or Vite integration for development
4. **Production:** Purged CSS for minimal file size (not critical for localhost but good practice)

**Dark Theme Strategy:**

\\\javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // Enable dark mode with class strategy
  theme: {
    extend: {
      colors: {
        // BMAD Dash custom colors
        'bmad-dark': '#1a1a1a',
        'bmad-gray': '#2d2d2d',
        'bmad-text': '#e0e0e0',
      }
    }
  }
}
\\\

**Component Strategy:**

- Use Tailwind utilities for 90% of styling
- Create custom CSS only where Tailwind lacks expressiveness
- Build components as vanilla JS + Tailwind classes (no React/Vue overhead)

**Responsive Strategy:**

- Desktop-first (primary: 1920x1080, minimum: 1366x768)
- Use Tailwind breakpoints sparingly (mobile not required)
- Focus on 1080p  768p scaling

### Customization Strategy

**Design Tokens (via Tailwind Config):**

\\\javascript
extend: {
  spacing: {
    '18': '4.5rem', // Custom spacing for BMAD layouts
  },
  fontSize: {
    'bmad-sm': '14px', // Minimum readable size (accessibility)
    'bmad-base': '16px',
  },
  transitionDuration: {
    '50': '50ms', // \u003c50ms for instant feel (modals)
    '100': '100ms', // \u003c100ms for view transitions
  }
}
\\\

**Custom Utilities for BMAD Patterns:**

\\\css
/* Custom Tailwind utilities for BMAD-specific needs */
@layer utilities {
  .bmad-badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }
  
  .bmad-modal {
    @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center;
  }
}
\\\

**Component Classes:**

- Breadcrumbs: Tailwind utilities + custom separator
- Quick Glance Bar: CSS Grid with Tailwind
- Kanban Cards: Flexbox with Tailwind + custom shadows
- Action Cards: Layered divs with Tailwind borders
- Modals: Fixed positioning with Tailwind backdrop

**Performance Optimization:**

- JIT mode generates only used classes
- Purge unused CSS in production build
- Keep custom CSS minimal (\u003c5% of total styles)

