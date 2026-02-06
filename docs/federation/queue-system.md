# Federation Queue System
## Documentation for Agent Federation Members

> *"The queue is the circulatory system of the federation. Tasks flow; agents execute."*

---

## Quick Start

### For Reuben (Human Orchestrator)

```bash
# Check queue status
python3 scripts/fed-queue.py status

# Add a task for an agent
python3 scripts/fed-queue.py add --from copilot --to kimi --task "Implement auth" --priority high

# See what's next for an agent
python3 scripts/fed-queue.py next --agent kimi

# List all pending tasks
python3 scripts/fed-queue.py list --status pending
```

### For Agents (Autonomous Use)

```bash
# Check if there are tasks for you
python3 scripts/fed-queue.py next --agent <your-name>

# Mark a task as started
python3 scripts/fed-queue.py start <task-id>

# Complete a task (optionally queue follow-up)
python3 scripts/fed-queue.py complete <task-id> --result <artifact-path>

# Auto-queue a follow-up task for another agent
python3 scripts/fed-queue.py add --from <you> --to <other-agent> --task "Next step" --priority normal
```

---

## Command Reference

### `fed-queue.py add`

Add a new task to the queue.

```bash
fed-queue.py add \
  --from <agent-name> \
  --to <agent-name> \
  --task "Description of work" \
  --priority <critical|high|normal|low> \
  [--deps <task-id-1>,<task-id-2>]
```

**Examples:**
```bash
# Simple task
fed-queue.py add --from claude --to kimi --task "Implement auth" --priority high

# Task with dependencies
fed-queue.py add --from claude --to kimi --task "Deploy auth" --priority normal --deps task-20260205-0001
```

---

### `fed-queue.py list`

List tasks with optional filters.

```bash
fed-queue.py list [--status <status>] [--agent <agent>]
```

**Examples:**
```bash
# All tasks
fed-queue.py list

# Only pending tasks for kimi
fed-queue.py list --status pending --agent kimi

# All completed tasks
fed-queue.py list --status completed
```

---

### `fed-queue.py status`

Show queue statistics.

```bash
fed-queue.py status
```

Output:
```
📊 Federation Queue Status
   Pending:     5
   In Progress: 2
   Completed:   12
   Total:       19
```

---

### `fed-queue.py next`

Get the next task for an agent (highest priority, ready to execute).

```bash
fed-queue.py next [--agent <agent-name>]
```

**Without --agent:** Shows next task for any agent  
**With --agent:** Shows next task specific to that agent

---

### `fed-queue.py start`

Mark a task as in-progress.

```bash
fed-queue.py start <task-id>
```

Requirements:
- Task must be in "pending" status
- All dependencies must be completed

---

### `fed-queue.py complete`

Mark a task as completed.

```bash
fed-queue.py complete <task-id> [--result <artifact-path>]
```

Requirements:
- Task must be "in-progress"

---

### `fed-queue.py cancel`

Cancel a pending or in-progress task.

```bash
fed-queue.py cancel <task-id>
```

---

## Task Lifecycle

```
PENDING → IN-PROGRESS → COMPLETED
   ↓
CANCELLED
```

**State Transitions:**
- `add` → Creates PENDING task
- `start` → Moves PENDING → IN-PROGRESS
- `complete` → Moves IN-PROGRESS → COMPLETED
- `cancel` → Deletes PENDING or IN-PROGRESS task

---

## Priority Levels

| Priority | Use Case | SLA (Target) |
|----------|----------|--------------|
| **critical** | Production outages, blocking bugs | ASAP |
| **high** | Important features, deadlines | Same day |
| **normal** | Standard work | Within 2 days |
| **low** | Nice-to-have, tech debt | When available |

Tasks are sorted by priority first, then by creation time (oldest first).

---

## Dependencies

Tasks can depend on other tasks:

```bash
# Task B depends on Task A
fed-queue.py add --from claude --to kimi --task "Task A" --priority high
# → Returns: task-20260205-0001

fed-queue.py add --from claude --to kimi --task "Task B" --priority high --deps task-20260205-0001
```

**Rules:**
- A task can only start when all dependencies are COMPLETED
- Circular dependencies are not prevented (be careful!)
- Dependencies are checked at `start` time, not `add` time

---

## File Structure

```
.federation/
├── queue/
│   ├── pending/          # Tasks waiting to be started
│   ├── in-progress/      # Tasks currently being worked
│   └── completed/        # Finished tasks (archived)
├── votes/active/         # Active votes (Phase 4 Sprint 3)
├── state/
│   └── federation-state.json  # Current federation status
└── metrics.json          # Performance tracking (Phase 4 Sprint 4)
```

Each task is a JSON file: `task-{timestamp}-{seq}.json`

---

## Agent Integration

### From Agent Code

```python
import subprocess
import json

def queue_task_for_kimi(description: str, priority: str = "normal"):
    """Queue a task for Kimi after completing research."""
    result = subprocess.run(
        ["python3", "scripts/fed-queue.py", "add",
         "--from", "claude",
         "--to", "kimi",
         "--task", description,
         "--priority", priority],
        capture_output=True,
        text=True,
        cwd="/Users/others/kimi-code-folder"
    )
    
    # Parse task ID from output
    if result.returncode == 0:
        # Output: "✅ Created task: task-20260205-184950-0001"
        task_id = result.stdout.strip().split(": ")[-1]
        return task_id
    else:
        raise Exception(f"Failed to queue task: {result.stderr}")

# Usage
after_research_complete():
    task_id = queue_task_for_kimi(
        "Implement auth from docs/architecture/auth-design.md",
        priority="high"
    )
    print(f"Queued implementation task: {task_id}")
```

---

## Autonomous Scheduling (Phase 4)

When auto-scheduling is enabled (Sprint 2), agents can:

1. **Auto-queue on completion:**
   ```python
   # In Claude's code
   if task_type == "research" and has_implementation_phase:
       federation.queue_task(
           from_agent="claude",
           to_agent="kimi",
           task=f"Implement design from {output_path}",
           priority="high",
           deps=[current_task_id]
       )
   ```

2. **Check queue on startup:**
   ```python
   # In Kimi's startup
   next_task = federation.get_next_task(agent="kimi")
   if next_task:
       print(f"Auto-resuming: {next_task['description']}")
       start_task(next_task['task_id'])
   ```

---

## Best Practices

### For Reuben

1. **Use explicit priorities** — Don't leave everything as "normal"
2. **Set clear task descriptions** — Agents need context
3. **Check status regularly** — `fed-queue.py status` takes 2 seconds
4. **Don't micromanage** — Let agents pull from queue

### For Agents

1. **Check your queue on startup** — There might be work waiting
2. **Start tasks promptly** — Don't leave tasks pending
3. **Complete with results** — Link to artifacts, not just "done"
4. **Queue follow-ups** — If research implies implementation, queue it
5. **Respect dependencies** — Don't start blocked tasks

### For Federation Health

1. **Keep queues short** — < 10 pending tasks per agent
2. **Complete old tasks** — Don't let tasks stall
3. **Review completed** — Check `.federation/queue/completed/` for patterns
4. **Update documentation** — This is a living system

---

## Troubleshooting

### "Task not found"
- Check the task ID with `fed-queue.py list`
- Task might be in wrong status (can't start completed tasks)

### "Dependency not completed"
- List the dependency task: `fed-queue.py list | grep <dep-id>`
- Complete blocking tasks first

### "No pending tasks"
- Check with `fed-queue.py list --status pending`
- All tasks might be in-progress or completed

### Queue growing too large
- Check for stuck tasks: `fed-queue.py list --status in-progress`
- Review priorities — maybe everything is "normal"

---

## Future Enhancements

### Phase 4 Sprint 2: Auto-Scheduling
- Agents auto-queue follow-up tasks
- Dependency chains auto-resolve

### Phase 4 Sprint 3: Voting
- Queue tasks for voting decisions
- Blocked pending vote resolution

### Phase 4 Sprint 4: Optimization
- Priority suggestions based on history
- Agent load balancing

### Phase 4 Sprint 5: Predictive
- Tasks auto-routed without explicit --to
- Learning from past assignments

---

**Related:**
- [Phase 4 Plan](../planning/phase4-autonomous-federation.md)
- [AGENT_FEDERALISM_MANIFESTO.md](../../AGENT_FEDERALISM_MANIFESTO.md)
- [AGENT_ASSIGNMENTS.md](../../AGENT_ASSIGNMENTS.md)

---

*"The queue doesn't replace judgment. It amplifies coordination."* 🔧🔮
