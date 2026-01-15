# BMAD Dash Orchestration API Design

**Date**: 2026-01-15
**Status**: Design Proposal
**Goal**: Extend BMAD Dash from read-only auditor to API-based orchestrator that IDEs can poll for workflow commands

---

## Overview

### Current State
BMAD Dash is a read-only auditor that:
- Parses BMAD artifacts (sprint-status.yaml, story files)
- Suggests workflow commands (e.g., `/bmad:bmm:workflows:dev-story 1.3`)
- Users manually copy commands to Claude CLI

### Proposed State
BMAD Dash becomes an orchestrator that:
- Maintains execution queue in `orchestration-state.json`
- Exposes REST API for IDE integration
- Tracks command execution lifecycle with single-execution locking
- Provides Start/Stop/Continue controls in web UI
- IDEs poll for commands and report completion

### Core Principles
1. **Files remain source of truth** for project state (stories, epics, tasks)
2. **Orchestration state is ephemeral** - recoverable from files + Git history
3. **User controls workflow** - explicit Continue clicks, no auto-advance
4. **Single execution lock** - only one IDE can claim a command at a time

---

## Architecture Changes

### New Components

#### 1. **Orchestration Service** (`backend/services/orchestration_service.py`)
- Determines next command based on sprint state
- Manages execution queue and locks
- Handles state transitions (idle → queued → claimed → executing → completed)

#### 2. **Orchestration State File** (`_bmad-output/implementation-artifacts/orchestration-state.json`)
```json
{
  "status": "active|paused|idle",
  "current_execution": {
    "id": "exec-uuid-123",
    "command": "/bmad:bmm:workflows:dev-story 1.3",
    "story_id": "1.3",
    "status": "queued|claimed|executing|completed|failed",
    "claimed_by": "vscode-client-456",
    "claimed_at": "2026-01-15T10:30:00Z",
    "started_at": "2026-01-15T10:30:05Z",
    "completed_at": null,
    "result": null
  },
  "queue": [
    {
      "command": "/bmad:bmm:workflows:code-review 1.3",
      "story_id": "1.3",
      "reason": "dev-story completed, review required"
    }
  ],
  "history": [
    {
      "id": "exec-uuid-122",
      "command": "/bmad:bmm:workflows:dev-story 1.2",
      "status": "completed",
      "completed_at": "2026-01-15T10:15:00Z"
    }
  ]
}
```

#### 3. **New API Endpoints** (`backend/api/orchestration.py`)

**GET `/api/orchestration/status`**
- Returns current orchestration state (active/paused/idle)
- Used by UI to show Start/Stop/Continue buttons

**POST `/api/orchestration/start`**
- Activates orchestration, queues first command
- Request: `{"project_root": "/path/to/project"}`
- Response: `{"status": "active", "next_command": "...", "message": "Orchestration started"}`

**POST `/api/orchestration/stop`**
- Pauses orchestration (current command finishes, queue stops)
- Request: `{"project_root": "/path/to/project"}`
- Response: `{"status": "paused"}`

**POST `/api/orchestration/continue`**
- Resumes orchestration, queues next command
- Request: `{"project_root": "/path/to/project"}`
- Response: `{"status": "active", "next_command": "..."}`

**GET `/api/orchestration/next-command`** *(IDE polling endpoint)*
- Returns next command if available and unclaimed
- Atomically claims command for requesting client
- Request: `?project_root=/path&client_id=vscode-456`
- Response:
  ```json
  {
    "execution_id": "exec-uuid-123",
    "command": "/bmad:bmm:workflows:dev-story 1.3",
    "story_id": "1.3",
    "status": "claimed",
    "claimed_at": "2026-01-15T10:30:00Z"
  }
  ```
- If no command available: `{"command": null, "status": "idle"}`
- If command already claimed: `{"command": null, "status": "claimed_by_other", "claimed_by": "..."}`

**POST `/api/orchestration/heartbeat`** *(IDE keeps claim alive)*
- Updates last_seen timestamp for claimed execution
- Request: `{"execution_id": "exec-uuid-123", "client_id": "vscode-456"}`
- Response: `{"status": "ok", "expires_in_seconds": 30}`
- If not called within 60 seconds, claim is released

**POST `/api/orchestration/complete`** *(IDE reports results)*
- Marks execution complete, releases lock
- Request:
  ```json
  {
    "execution_id": "exec-uuid-123",
    "client_id": "vscode-456",
    "status": "success|failure",
    "result": {
      "exit_code": 0,
      "output": "...",
      "duration_seconds": 120
    }
  }
  ```
- Response: `{"status": "completed", "orchestration_status": "paused"}`
- Triggers file re-parse to update dashboard

#### 4. **UI Changes** (`frontend/components/orchestration-controls.js`)
- Add orchestration control panel to dashboard header
- Show current execution status with live updates
- Buttons: **Start**, **Stop**, **Continue**
- Visual states:
  - **Idle**: "Start" button enabled
  - **Active + Executing**: "Stop" button enabled, shows current command + progress spinner
  - **Paused**: "Continue" button enabled, shows last result
  - **Claimed by other IDE**: Shows which IDE is executing

---

## Command Selection Logic

### Priority Order (in `orchestration_service.py`)

1. **Check sprint-status.yaml** for next story in priority order
2. **For each story**, determine required workflow:
   - `todo` / `ready-for-dev` → `/bmad:bmm:workflows:dev-story [story-id]`
   - `in-progress` with no `dev-story` run → `/bmad:bmm:workflows:dev-story [story-id]`
   - `review` → `/bmad:bmm:workflows:code-review [story-id]`
   - `done` with workflow gaps detected → suggest gap-filling command
3. **If no stories need work** → `/bmad:bmm:workflows:create-story` (next story)
4. **If epic complete** → `/bmad:bmm:workflows:retrospective` → next epic

### Command Queue vs. Single Command

**Decision**: Queue one command at a time (no multi-command queue initially)

**Rationale**:
- User reviews results after each command
- Next command may depend on current results
- Simpler state management
- Can add queue depth later if needed

---

## User Workflows

### Workflow 1: Start Orchestration
1. User opens BMAD Dash in browser
2. Dashboard shows current sprint state (stories, tasks, gaps)
3. User clicks **"Start Orchestration"**
4. BMAD Dash:
   - Analyzes current sprint state
   - Determines next command (e.g., `dev-story 1.3`)
   - Writes to `orchestration-state.json` with `status: "queued"`
5. IDE (polling every 10 seconds) picks up command:
   - Polls `/next-command`
   - Receives command + execution_id
   - Command status changes to `claimed`
6. IDE executes command (user watches Claude work)
7. IDE sends heartbeat every 30 seconds to keep claim alive
8. IDE calls `/complete` with results
9. BMAD Dash updates state to `status: "paused"`
10. Dashboard shows **"Continue"** button

### Workflow 2: Continue to Next Command
1. User reviews results in IDE (tests passed, code looks good)
2. User clicks **"Continue"** in BMAD Dash
3. BMAD Dash determines next command (e.g., `code-review 1.3`)
4. Repeat steps 5-10 from Workflow 1

### Workflow 3: Stop Orchestration
1. User clicks **"Stop"** during execution
2. Current command continues to completion
3. BMAD Dash sets `status: "paused"`, does not queue next command
4. IDE completes current execution and reports results
5. User can click **"Continue"** later to resume

### Workflow 4: IDE Crash Recovery
1. IDE crashes mid-execution (heartbeat stops)
2. After 60 seconds, BMAD Dash releases execution lock
3. Dashboard shows "Execution timed out - IDE disconnected"
4. User can click **"Retry"** to re-queue same command
5. Or click **"Skip"** to move to next command

---

## Edge Cases & Error Handling

### Multiple IDEs Polling
- **Lock mechanism**: First IDE to poll `/next-command` claims it atomically
- **File-based lock**: Use `orchestration-state.json` with atomic write
- **Lock expiry**: Heartbeat required every 60 seconds, or lock released
- **Conflict resolution**: If two IDEs write simultaneously, last writer wins (acceptable - ephemeral state)

### User Manually Runs Commands
- **Detection**: BMAD Dash parses Git commits, detects workflow execution outside orchestration
- **Reconciliation**: If `orchestration-state.json` shows `dev-story 1.3` queued, but Git shows it was already run, mark as completed externally
- **UI**: Show "Command executed manually - skipping" message

### File State Changes During Execution
- **Scenario**: User manually edits `sprint-status.yaml` while command executing
- **Handling**: After command completes, BMAD Dash re-parses files, recalculates next command
- **UI**: Show warning if manual changes detected

### Network Partition (IDE loses connection)
- **Heartbeat stops** → lock expires after 60 seconds
- **IDE reconnects** → polls `/next-command`, gets new command (old one timed out)
- **Completion report arrives late** → BMAD Dash accepts it, reconciles state

---

## Migration Path (Implementation Phases)

### Phase 1: API Foundation (No UI)
- Add `orchestration_service.py` with command selection logic
- Implement `orchestration-state.json` read/write
- Add `/next-command` and `/complete` endpoints
- Test with manual curl commands

### Phase 2: Lock Mechanism
- Add execution locking with `client_id` and `claimed_at`
- Implement heartbeat endpoint and expiry logic
- Test with multiple concurrent curl clients

### Phase 3: Web UI Controls
- Add `orchestration-controls.js` component to dashboard
- Implement Start/Stop/Continue buttons
- Add live execution status display
- Test user workflows end-to-end

### Phase 4: IDE Integration (Example: VS Code)
- Create VS Code extension with polling loop
- Integrate with Claude Code CLI
- Display execution results in output panel
- Test with real BMAD workflows

---

## IDE Integration Requirements

### For VS Code Extension (or Antigravity IDE)

**Polling Implementation**:
```javascript
const POLL_INTERVAL = 10000; // 10 seconds
const CLIENT_ID = `vscode-${generateUUID()}`;

async function pollForCommands() {
  const response = await fetch(
    `http://localhost:5001/api/orchestration/next-command?project_root=${projectRoot}&client_id=${CLIENT_ID}`
  );
  const data = await response.json();

  if (data.command) {
    // Execute command
    await executeCommand(data.command, data.execution_id);
  }

  setTimeout(pollForCommands, POLL_INTERVAL);
}
```

**Command Execution**:
```javascript
async function executeCommand(command, executionId) {
  // Start heartbeat
  const heartbeatInterval = setInterval(() => {
    fetch(`http://localhost:5001/api/orchestration/heartbeat`, {
      method: 'POST',
      body: JSON.stringify({ execution_id: executionId, client_id: CLIENT_ID })
    });
  }, 30000); // Every 30 seconds

  // Execute via Claude CLI
  const result = await runClaudeCLI(command);

  // Stop heartbeat
  clearInterval(heartbeatInterval);

  // Report completion
  await fetch(`http://localhost:5001/api/orchestration/complete`, {
    method: 'POST',
    body: JSON.stringify({
      execution_id: executionId,
      client_id: CLIENT_ID,
      status: result.success ? 'success' : 'failure',
      result: result
    })
  });
}
```

---

## Testing Strategy

### Unit Tests
- `orchestration_service.py`: Command selection logic
- Lock acquisition/release edge cases
- Heartbeat expiry logic

### Integration Tests
- `/next-command` → `/complete` flow
- Multiple client polling (lock conflicts)
- Heartbeat timeout and recovery

### End-to-End Tests
1. Start orchestration → IDE picks up command → completes → Continue → next command
2. Stop mid-execution → verify queue pauses
3. IDE crash → verify lock expires → new IDE can claim
4. Manual command execution → verify reconciliation

---

## Critical Files to Modify

### Backend
- **New**: [backend/services/orchestration_service.py](backend/services/orchestration_service.py) - Core orchestration logic
- **New**: [backend/api/orchestration.py](backend/api/orchestration.py) - REST endpoints
- **Modified**: [backend/app.py](backend/app.py) - Register orchestration blueprint

### Frontend
- **New**: [frontend/components/orchestration-controls.js](frontend/components/orchestration-controls.js) - UI controls
- **Modified**: [frontend/views/dashboard.js](frontend/views/dashboard.js) - Integrate controls into header
- **New**: [frontend/styles/orchestration.css](frontend/styles/orchestration.css) - Control panel styling

### State Files (Created at Runtime)
- **New**: `_bmad-output/implementation-artifacts/orchestration-state.json` - Orchestration queue

---

## Verification Plan

### Manual Testing
1. **Start orchestration** in BMAD Dash → verify next command appears in `/next-command` response
2. **Simulate IDE execution** with curl → verify lock is held
3. **Send heartbeat** → verify lock stays alive
4. **Complete execution** → verify state transitions to paused
5. **Click Continue** → verify next command is queued
6. **Open second terminal** → verify second curl cannot claim same command
7. **Stop heartbeat** → wait 60 seconds → verify lock expires

### Automated Tests
- Pytest suite for `orchestration_service.py`
- Playwright tests for UI controls (Start/Stop/Continue buttons)

---

## Open Questions

1. **Should orchestration state survive Flask restart?**
   - Current design: State persists in JSON file, survives restart
   - Alternative: In-memory only, lost on restart (simpler but less robust)

2. **Should BMAD Dash support multiple projects orchestrated simultaneously?**
   - Current design: One orchestration per project_root (supports multi-project)
   - Alternative: Global orchestration (single project at a time)

3. **Should IDE report progress during long-running commands?**
   - Current design: Heartbeat only keeps lock alive
   - Alternative: Heartbeat includes progress percentage (e.g., "Running tests: 45%")

4. **Should orchestration handle workflow dependencies?**
   - Current design: Simple priority queue (one command at a time)
   - Alternative: DAG-based workflow engine (complex, probably overkill)

---

## Security Considerations

- **localhost-only**: Keep existing constraint (Flask binds to 127.0.0.1)
- **No authentication**: Acceptable for local-only deployment
- **File permissions**: Ensure `orchestration-state.json` is only writable by BMAD Dash process
- **Command injection**: IDEs execute commands as-is (trusted environment assumption)

---

## Future Enhancements (Out of Scope)

- WebSocket API for real-time updates (vs. polling)
- Multi-command queue (batch multiple workflows)
- Workflow templates (e.g., "Complete entire epic")
- Rollback/undo support
- Integration with CI/CD pipelines
- Remote execution (multi-machine orchestration)
