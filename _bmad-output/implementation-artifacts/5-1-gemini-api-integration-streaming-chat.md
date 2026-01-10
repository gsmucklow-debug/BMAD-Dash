---
story_id: "5.1"
title: "Gemini API Integration & Streaming Chat"
epic: "epic-5"
status: "ready-for-dev"
last_updated: "2026-01-10"
---

# Story 5.1: Gemini API Integration & Streaming Chat

As a **user**,
I want **a right sidebar AI chat that streams responses from Gemini 3 Flash**,
So that **I can ask project-aware questions and get answers in real-time**.

## Acceptance Criteria

### Chat Interface
- [ ] **Sidebar Layout**
    - [ ] Displays chat interface on the right side of the dashboard (300-400px width).
    - [ ] Chat remains accessible/visible from all view modes (Dashboard, Timeline, List).
    - [ ] Toggle button allows expanding/collapsing the sidebar.
- [ ] **Interaction Elements**
    - [ ] Input textarea accepts user questions (multiline support).
    - [ ] "Send" button is clickable with minimum 44x44px target size (NFR10).
    - [ ] "Clear Chat" option to reset conversation.

### Backend Integration
- [ ] **API Endpoint**
    - [ ] Implements `POST /api/ai-chat` endpoint.
    - [ ] Accepts JSON payload with `message` and `project_context` (phase, epic, story).
- [ ] **Gemini Integration**
    - [ ] Uses `google-generativeai` SDK to call Gemini 3 Flash model.
    - [ ] Injects BMAD Method documentation and project state into the system prompt.
    - [ ] Handles API errors gracefully (e.g., rate limits, invalid key).
- [ ] **Streaming Response**
    - [ ] Returns Server-Sent Events (SSE) stream.
    - [ ] Stream format follows `data: {"token": "..."}` pattern.

### Performance & UX
- [ ] **Responsiveness**
    - [ ] First token appears within <200ms (NFR6).
    - [ ] Tokens appear progressively as generated (no buffering full response).
- [ ] **Conversation Management**
    - [ ] Chat history is maintained during the session (in-memory or localStorage).
    - [ ] AI remembers previous turns in the conversation.
- [ ] **Content Formatting**
    - [ ] Markdown in responses is rendered correctly.
    - [ ] Code blocks include a "Copy" button.

### Security
- [ ] **Key Management**
    - [ ] `GEMINI_API_KEY` is loaded from `.env`.
    - [ ] API key is NEVER sent to the frontend.

## Implementation Tasks

### Backend - API & Service
- [ ] **Setup Configuration** (`backend/config.py`, `.env`)
    - [ ] Add `GEMINI_API_KEY` to environment configuration.
    - [ ] Initialize Gemini client.
- [ ] **Create AI Service** (`backend/services/ai_service.py`)
    - [ ] Implement `generate_stream(message, context)` function.
    - [ ] Construct system prompt with BMAD context.
- [ ] **Create API Route** (`backend/api/ai_chat.py`)
    - [ ] Implement `POST /api/ai-chat` route handler.
    - [ ] Setup SSE response generator.

### Frontend - Components
- [ ] **Create Chat Component** (`frontend/js/components/ai-chat.js`)
    - [ ] Implement sidebar layout and toggle logic.
    - [ ] Implement message list rendering with Markdown support.
    - [ ] Implement input area and send logic.
- [ ] **Implement Streaming Client** (`frontend/js/api.js`)
    - [ ] Add `streamChatResponse` function using `fetch` and `ReadableStream`.
- [ ] **Dashboard Integration** (`frontend/js/views/dashboard.js`)
    - [ ] Add AI Chat component to the main layout.

### Styling & UX
- [ ] **Sidebar Styling** (`frontend/css/input.css`)
    - [ ] Fixed position right sidebar with backdrop blur or distinct background.
    - [ ] Markdown typography styles for chat messages.
    - [ ] Loading state animations (typing indicator).

### Verification
- [ ] **Manual Testing**
    - [ ] Verify streaming works without buffering.
    - [ ] Check first-token latency.
    - [ ] Verify context awareness (ask "What phase is this project in?").
- [ ] **Automated Tests**
    - [ ] Test API endpoint accepts correct payload.
    - [ ] Test error handling for missing API key.

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
