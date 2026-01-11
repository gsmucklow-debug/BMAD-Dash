---
story_id: "5.1"
title: "Gemini API Integration & Streaming Chat"
epic: "epic-5"
status: "done"
completed: "2026-01-10"
last_updated: "2026-01-10"
---

# Story 5.1: Gemini API Integration & Streaming Chat

As a **user**,
I want **a right sidebar AI chat that streams responses from Gemini 3 Flash**,
So that **I can ask project-aware questions and get answers in real-time**.

## Acceptance Criteria

### Chat Interface
- [x] **Sidebar Layout**
    - [x] Displays chat interface on the right side of the dashboard (300-400px width).
    - [x] Chat remains accessible/visible from all view modes (Dashboard, Timeline, List).
    - [x] Toggle button allows expanding/collapsing the sidebar.
- [x] **Interaction Elements**
    - [x] Input textarea accepts user questions (multiline support).
    - [x] "Send" button is clickable with minimum 44x44px target size (NFR10).
    - [x] "Clear Chat" option to reset conversation.

### Backend Integration
- [x] **API Endpoint**
    - [x] Implements `POST /api/ai-chat` endpoint.
    - [x] Accepts JSON payload with `message` and `project_context` (phase, epic, story).
- [x] **Gemini Integration**
    - [x] Uses `google-generativeai` SDK to call Gemini 3 Flash model.
    - [x] Injects BMAD Method documentation and project state into the system prompt.
    - [x] Handles API errors gracefully (e.g., rate limits, invalid key).
- [x] **Streaming Response**
    - [x] Returns Server-Sent Events (SSE) stream.
    - [x] Stream format follows `data: {"token": "..."}` pattern.

### Performance & UX
- [x] **Responsiveness**
    - [x] First token appears within <200ms (NFR6).
    - [x] Tokens appear progressively as generated (no buffering full response).
- [x] **Conversation Management**
    - [x] Chat history is maintained during the session (in-memory or localStorage).
    - [x] AI remembers previous turns in the conversation.
- [x] **Content Formatting**
    - [x] Markdown in responses is rendered correctly.
    - [x] Code blocks include a "Copy" button.

### Security
- [x] **Key Management**
    - [x] `GEMINI_API_KEY` is loaded from `.env`.
    - [x] API key is NEVER sent to the frontend.

## Implementation Tasks

### Backend - API & Service
- [x] **Setup Configuration** (`backend/config.py`, `.env`)
    - [x] Add `GEMINI_API_KEY` to environment configuration.
    - [x] Initialize Gemini client.
- [x] **Create AI Service** (`backend/services/ai_coach.py`)
    - [x] Implement `generate_stream(message, context)` function.
    - [x] Construct system prompt with BMAD context.
- [x] **Create API Route** (`backend/api/ai_chat.py`)
    - [x] Implement `POST /api/ai-chat` route handler.
    - [x] Setup SSE response generator.

### Frontend - Components
- [x] **Create Chat Component** (`frontend/js/components/ai-chat.js`)
    - [x] Implement sidebar layout and toggle logic.
    - [x] Implement message list rendering with Markdown support.
    - [x] Implement input area and send logic.
- [x] **Implement Streaming Client** (`frontend/js/api.js`)
    - [x] Add `streamChatResponse` function using `fetch` and `ReadableStream`.
- [x] **Dashboard Integration** (`frontend/js/views/dashboard.js`)
    - [x] Add AI Chat component to the main layout.

### Styling & UX
- [x] **Sidebar Styling** (`frontend/css/input.css`)
    - [x] Fixed position right sidebar with backdrop blur or distinct background.
    - [x] Markdown typography styles for chat messages.
    - [x] Loading state animations (typing indicator).

### Verification
- [x] **Manual Testing**
    - [x] Verify streaming works without buffering.
    - [x] Check first-token latency.
    - [x] Verify context awareness (ask "What phase is this project in?").
- [x] **Automated Tests**
    - [x] Test API endpoint accepts correct payload.
    - [x] Test error handling for missing API key.

### Review Follow-ups (AI)
- [ ] [AI-Review][Low] Refactor `frontend/css/input.css` into smaller modules if it grows larger.
- [ ] [AI-Review][Low] Remove deprecated `sendChatMessage` method from `frontend/js/api.js` when all consumers are migrated.

## Dev Notes

### Architecture Compliance
- **Service Layer:** Keep Gemini logic in `backend/services/` to separate it from route handling.
- **No Database:** Chat history should be transient (frontend state) or optional localStorage, not DB persisted.
- **SSE Pattern:** Use Flask's generator pattern for SSE. Ensure `mimetype='text/event-stream'`.

### Library Requirements
- `google-generativeai` (latest stable).
- `markdown-it` (or similar) for frontend Markdown rendering (via CDN or local asset if avoiding npm deps, check `index.html`). *Note: Architecture prefers vanilla JS, so consider a lightweight raw import or simple regex for basic MD if full library is too heavy, OR check if a standard library was decided. Architecture says "Vanilla JS modules". If a library is needed, `marked` or `markdown-it` from a CDN/local file is acceptable.*

### Previous Learnings (from Story 4.2)
- **Component Reuse:** Ensure `ai-chat.js` is a standalone class/module like `WorkflowHistory`.
- **Error Handling:** Graceful degradation is key. If API fails, UI should show error message but not crash.

### Security Warning
- **NEVER** commit the `.env` file or hardcode the API key.
- Ensure `.gitignore` is respected.

## References
- [Architecture: AI Coach Integration](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/architecture.md#ai-coach-integration-fr28-fr30)
- [UX Design: AI Coach Integration](file:///f:/BMAD%20Dash/_bmad-output/planning-artifacts/ux-design-specification.md#epic-5-ai-coach-integration)
