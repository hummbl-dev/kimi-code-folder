# Federation Auto-Scheduling System
## Phase 4 Sprint 2: Autonomous Task Scheduling

> *"When one agent finishes, the next begins — automatically."*

---

## Overview

The Auto-Scheduling System enables agents to automatically queue follow-up tasks for other agents when work is completed. This eliminates the need for Reuben to manually say "pass to Kimi" for every handoff.

**Status:** ✅ Implemented and tested (Phase 4 Sprint 2)

---

## How It Works

### Basic Flow

```
1. Agent A completes a task
2. System checks if task matches auto-schedule rules
3. If match: Automatically queues follow-up task for Agent B
4. Agent B finds task in queue on next startup
```

### Example: Research → Implementation

```bash
# 1. Reuben assigns research to Claude
python3 scripts/fed-queue.py add --from reuben --to claude \
  --task "Research auth patterns" --priority high

# 2. Claude completes the task
python3 scripts/fed-queue.py complete task-001 --result "docs/auth.md"

# 3. Auto-scheduler triggers (via on-complete hook)
python3 scripts/fed-auto-schedule.py on-complete task-001 --by claude \
  --artifact docs/auth.md

# 4. System auto-queues implementation for Kimi
🔄 Auto-scheduled: task-002
   For: kimi
   Task: Implement Research auth patterns from docs/auth.md
   Rule: research-to-implementation
   Dependency: task-001 → task-002

# 5. Kimi checks queue on startup
python3 scripts/fed-auto-schedule.py check-startup --agent kimi
📥 1 task(s) queued for kimi:
   - task-002: Implement Research auth patterns...
```

---

## Commands

### Enable/Disable Auto-Scheduling

```bash
# Enable system-wide
python3 scripts/fed-auto-schedule.py enable

# Disable system-wide
python3 scripts/fed-auto-schedule.py disable

# Check status
python3 scripts/fed-auto-schedule.py status
```

### List Auto-Schedule Rules

```bash
python3 scripts/fed-auto-schedule.py trigger-rules
```

### Trigger on Task Completion

```bash
# Called automatically when task completes
python3 scripts/fed-auto-schedule.py on-complete <task-id> \
  --by <agent-name> \
  [--artifact <path>]
```

### Check Startup Queue

```bash
# Agents run this on startup to find queued work
python3 scripts/fed-auto-schedule.py check-startup --agent <agent-name>
```

---

## Built-in Rules

| Rule | Trigger | Action | Status |
|------|---------|--------|--------|
| **research→implementation** | Claude completes research/analysis | Queue implementation for Kimi | ✅ Enabled |
| **implementation→testing** | Kimi completes implementation | Queue review for Copilot | ✅ Enabled |
| **design→execution** | Copilot completes design/plan | Queue research for Claude | ✅ Enabled |
| **draft→polish** | Ollama completes draft | Queue polish for Kimi | 🚫 Disabled |

---

## Rule Format

Rules are stored in `.federation/state/auto-schedule-rules.json`:

```json
{
  "id": "research-to-implementation",
  "name": "Research → Implementation",
  "trigger": {
    "from_agent": "claude",
    "task_patterns": ["research", "analyze", "architecture"],
    "output_artifact": true
  },
  "action": {
    "queue_for": "kimi",
    "task_template": "Implement {previous_task} from {artifact_path}",
    "priority": "high",
    "auto_start": false
  },
  "enabled": true
}
```

### Trigger Fields

| Field | Description | Example |
|-------|-------------|---------|
| `from_agent` | Agent that must complete the task | `"claude"` |
| `task_patterns` | Keywords that must appear in task description | `["research", "analyze"]` |
| `output_artifact` | Whether task must have a result/artifact | `true` |

### Action Fields

| Field | Description | Example |
|-------|-------------|---------|
| `queue_for` | Agent to receive the follow-up task | `"kimi"` |
| `task_template` | Template for new task description | `"Implement {previous_task}..."` |
| `priority` | Priority of the new task | `"high"` |
| `auto_start` | Whether to auto-start (not yet implemented) | `false` |

### Template Variables

- `{previous_task}` — Description of the completed task
- `{artifact_path}` — Path to the output artifact

---

## Global Settings

```json
{
  "require_confirmation": true,
  "log_to_federation": true,
  "max_auto_queue_depth": 5,
  "notification_on_queue": true
}
```

| Setting | Description | Default |
|---------|-------------|---------|
| `require_confirmation` | If true, queue but don't auto-start | `true` |
| `log_to_federation` | Log auto-schedule events to FEDERATION_LOG.md | `true` |
| `max_auto_queue_depth` | Prevent infinite loops | `5` |
| `notification_on_queue` | Notify when tasks are auto-queued | `true` |

---

## Integration with Queue System

Auto-scheduling extends the queue system:

1. **Queue adds task** → Creates task file in `.federation/queue/pending/`
2. **Agent starts task** → Moves to `.federation/queue/in-progress/`
3. **Agent completes task** → Moves to `.federation/queue/completed/`
4. **Auto-scheduler triggers** → Checks rules, creates new pending task
5. **Dependency tracking** → New task depends on completed task

---

## For Agents: Startup Protocol

Add to agent startup routine:

```python
import subprocess

def startup_check():
    """Check for auto-scheduled tasks on startup."""
    result = subprocess.run(
        ["python3", "scripts/fed-auto-schedule.py", 
         "check-startup", "--agent", "kimi"],
        capture_output=True,
        text=True
    )
    
    if "task(s) queued" in result.stdout:
        print("📥 Auto-scheduled work found!")
        # List and optionally start tasks
        subprocess.run(["python3", "scripts/fed-queue.py", 
                       "list", "--agent", "kimi"])
```

---

## Testing Auto-Scheduling

### Test 1: Research → Implementation Flow

```bash
# 1. Create research task for Claude
python3 scripts/fed-queue.py add --from reuben --to claude \
  --task "Research authentication patterns" --priority high

# 2. Complete it
python3 scripts/fed-queue.py start task-XXX
python3 scripts/fed-queue.py complete task-XXX --result docs/auth.md

# 3. Trigger auto-schedule
python3 scripts/fed-auto-schedule.py on-complete task-XXX \
  --by claude --artifact docs/auth.md

# 4. Verify Kimi has new task
python3 scripts/fed-auto-schedule.py check-startup --agent kimi
```

**Expected:** New task queued for Kimi with dependency on completed task.

---

## Future Enhancements

### Phase 4 Sprint 3: Voting Integration
- Block auto-scheduled tasks pending vote resolution
- Queue tasks for voting instead of direct assignment

### Phase 4 Sprint 4: Optimization
- Dynamic rule adjustment based on success rates
- Priority optimization

### Phase 4 Sprint 5: Predictive Routing
- ML-based rule matching
- Semantic task pattern matching

---

## Troubleshooting

### "No auto-schedule rule matched"
- Check if auto-scheduling is enabled: `fed-auto-schedule.py status`
- Verify task patterns match rules: `fed-auto-schedule.py trigger-rules`
- Ensure from_agent matches the rule trigger

### Auto-scheduled task not appearing
- Check queue: `fed-queue.py list --status pending`
- Verify dependency chain isn't blocking
- Check for queue depth limits

### Infinite loop concerns
- Max queue depth (5) prevents runaway
- Rules require explicit enabling
- Dependencies prevent circular scheduling

---

## Related Documents

- [Queue System](./queue-system.md) — Core queue functionality
- [Phase 4 Plan](../planning/phase4-autonomous-federation.md) — Overall roadmap
- [FEDERATION_LOG.md](../../FEDERATION_LOG.md) — Live status

---

*"The best handoff is the one you don't have to make manually."* 🔄
