# Cross-Platform Session Sync v1 — Design Document

**Status:** Draft  
**Date:** 2026-02-06  
**Author:** kimi  
**Scope:** File-based session persistence for 5-Agent Federation

---

## Problem Statement

The 5-Agent Federation (Kimi, Claude, Copilot, Codex, Ollama) operates across multiple environments:
- **Kimi:** Terminal/CLI (primary workspace: `~/kimi-code-folder/`)
- **Claude:** Web/Desktop app (shared workspace)
- **Copilot:** VS Code extension (same files)
- **Codex:** Terminal/CLI (`~/codex-code-folder/`)
- **Ollama:** Local LLM server (stateless, no sessions)

**Challenge:** Context and session state are not synchronized. Each agent operates in isolation, leading to:
- Duplicate work across agents
- Lost context when switching interfaces
- No unified view of federation activity

---

## Goals

1. **Persistent Sessions:** Active work sessions survive agent restarts
2. **Cross-Platform Reads:** Any agent can read current session state
3. **Conflict-Free Writes:** Lock-free optimistic concurrency
4. **Zero External Dependencies:** File-based only (no databases, no cloud APIs)
5. **Human-Readable:** JSON files for transparency and debugging

---

## Non-Goals

- Real-time sync (polling acceptable)
- Conflict resolution UI (last-write-wins with timestamps)
- Encryption at rest ( rely on filesystem permissions)
- Multi-machine sync (single-machine only for v1)

---

## Architecture

```
~/.federation/
├── sessions/
│   └── active-session.json          # Current active session
├── history/
│   ├── 2026-02-06T10-00-00Z.json    # Archived sessions (timestamped)
│   └── 2026-02-05T14-30-00Z.json
└── agents/
    ├── kimi-state.json              # Per-agent ephemeral state
    ├── codex-state.json
    ├── claude-state.json
    └── copilot-state.json
```

### File: `active-session.json`

```json
{
  "session_id": "sess-20260206-abc123",
  "created_at": "2026-02-06T10:00:00Z",
  "updated_at": "2026-02-06T15:30:00Z",
  "owner": "kimi",
  "sprint": "7-day-router-optimization",
  "status": "active",
  "agents": {
    "kimi": {
      "status": "active",
      "current_task": "Testing neural router Tier 1",
      "last_seen": "2026-02-06T15:30:00Z",
      "workspace": "~/kimi-code-folder/"
    },
    "claude": {
      "status": "idle",
      "current_task": null,
      "last_seen": "2026-02-06T14:00:00Z"
    },
    "codex": {
      "status": "active",
      "current_task": "Autonomous module implementation",
      "last_seen": "2026-02-06T15:15:00Z",
      "workspace": "~/codex-code-folder/"
    },
    "copilot": {
      "status": "standby",
      "current_task": null,
      "last_seen": "2026-02-06T12:00:00Z"
    },
    "ollama": {
      "status": "available",
      "model": "mistral:latest",
      "last_seen": "2026-02-06T15:30:00Z"
    }
  },
  "tasks": [
    {
      "id": "task-001",
      "description": "Implement Ollama Tier 1 embeddings",
      "assigned_to": "kimi",
      "status": "in_progress",
      "priority": "high",
      "created_at": "2026-02-06T10:00:00Z"
    },
    {
      "id": "task-002",
      "description": "Design cross-platform sync",
      "assigned_to": "kimi",
      "status": "completed",
      "priority": "high",
      "created_at": "2026-02-06T11:00:00Z",
      "completed_at": "2026-02-06T15:30:00Z"
    }
  ],
  "router": {
    "version": "v3",
    "accuracy": 0.357,
    "tier": 2,
    "pending_eval": true
  }
}
```

---

## Concurrency Model

### Optimistic Locking

```python
import json
import os
import time
from pathlib import Path

SESSION_PATH = Path.home() / ".federation" / "sessions" / "active-session.json"

def read_session():
    """Read current session state."""
    if not SESSION_PATH.exists():
        return None
    return json.loads(SESSION_PATH.read_text())

def write_session(session: dict) -> bool:
    """
    Write session with optimistic concurrency.
    Returns True if successful, False if conflict.
    """
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Read current state
    current = read_session()
    
    # Check if modified since we read it (optimistic check)
    if current and session.get("updated_at") != current.get("updated_at"):
        # Conflict: someone else modified it
        return False
    
    # Update timestamp
    session["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Atomic write: write to temp, then rename
    temp_path = SESSION_PATH.with_suffix(".tmp")
    temp_path.write_text(json.dumps(session, indent=2))
    temp_path.rename(SESSION_PATH)
    
    return True

def update_agent_status(agent: str, status: str, task: str = None):
    """Update this agent's status in the shared session."""
    session = read_session()
    if not session:
        session = create_new_session()
    
    session["agents"][agent] = {
        "status": status,
        "current_task": task,
        "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    # Retry on conflict (exponential backoff)
    for attempt in range(3):
        if write_session(session):
            return True
        time.sleep(0.1 * (2 ** attempt))
        session = read_session()  # Re-read current state
    
    return False
```

---

## Agent Integration

### Kimi (CLI)

```bash
# On startup
python3 -c "from federation_sync import update_agent_status; update_agent_status('kimi', 'active', '$TASK')"

# On exit
python3 -c "from federation_sync import update_agent_status; update_agent_status('kimi', 'idle')"
```

### Codex (CLI)

Same pattern, different workspace:
```bash
python3 -c "from federation_sync import update_agent_status; update_agent_status('codex', 'active', '$TASK')"
```

### Claude (Web/Desktop)

Read-only access via `~/.federation/sessions/active-session.json`:
```
I'll check the current federation state...
[Reads file]

Kimi is currently working on "Testing neural router Tier 1"
Codex is implementing "Autonomous module implementation"
```

### Copilot (VS Code)

Extension reads session to provide context:
```typescript
const session = JSON.parse(
  fs.readFileSync(path.join(homedir(), '.federation/sessions/active-session.json'), 'utf8')
);

// Show in status bar: "Federation: 2 agents active"
```

---

## Implementation Plan

### Phase 1: Core Library (Day 2-3)
- [ ] Create `federation_sync.py` module
- [ ] Implement read/write with optimistic locking
- [ ] Add CLI wrapper for bash integration
- [ ] Unit tests for concurrency

### Phase 2: Agent Integration (Day 4-5)
- [ ] Kimi: Automatic session updates on task start/end
- [ ] Codex: Same pattern, different workspace path
- [ ] Claude: Read-only integration via prompt context
- [ ] Copilot: Status bar extension (optional)

### Phase 3: Router Integration (Day 6-7)
- [ ] Session includes current router tier/accuracy
- [ ] Automatic re-evaluation triggers
- [ ] Sprint-based session archiving

---

## Open Questions

1. **Session Lifetime:** When should a session be archived?
   - Proposal: After 24h of inactivity, or explicit `federation session close`

2. **Conflict Resolution:** Last-write-wins acceptable?
   - Proposal: Yes for v1. Agents should update only their own fields.

3. **Cross-Machine:** How to handle multiple machines?
   - Proposal: Out of scope for v1. Each machine has independent `~/.federation/`.

4. **Secret Handling:** Any sensitive data in session?
   - Proposal: No secrets. Task descriptions may be logged, so keep them generic.

---

## Success Metrics

- [ ] Session survives agent restart
- [ ] Sub-100ms read latency (local SSD)
- [ ] Zero data loss under normal concurrency
- [ ] Human-readable JSON for debugging

---

## Future Work (v2)

- Git-based sync for cross-machine
- SQLite for structured queries
- WebSocket pub/sub for real-time updates
- Encrypted sessions for sensitive tasks
