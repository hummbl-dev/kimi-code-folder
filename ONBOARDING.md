# Federation Onboarding Guide
## Welcome to the Agent Federation

> *"The federation is only as strong as its newest member."*

---

## 🚀 New Agent Checklist

### Step 1: Understand Your Role

Read your specialty in [AGENTS.md](./AGENTS.md):
- What you're best at
- What to avoid
- How you fit in the handoff chain

### Step 2: Know the Tools

Essential commands every agent should know:

```bash
# Check if you have work waiting
python3 scripts/fed-queue.py next --agent <your-name>

# View federation status
python3 scripts/fed-analytics.py dashboard

# Route a task (if unsure who should do it)
python3 scripts/route_task_v2.py "task description" --explain
```

### Step 3: Workspace Setup

Your workspace should have:
```
<your>-code-folder/
├── agents/<your-name>/
│   ├── IDENTITY.md    # Who you are
│   ├── SOUL.md        # Why you're here  
│   ├── CAPABILITIES.md # What you can/can't do
│   └── MEMORY.md      # Session history
├── docs/              # Shared documentation
└── AGENTS.md          # Federation reference (symlink)
```

### Step 4: First Task Protocol

When you receive your first task:

1. **Acknowledge** — Comment "Received, starting work"
2. **Start** — `python3 scripts/fed-queue.py start <task-id>`
3. **Work** — Do the task
4. **Complete** — `python3 scripts/fed-queue.py complete <task-id> --result <path>`
5. **Record** — `python3 scripts/fed-analytics.py record ...` (helps routing optimization)

### Step 5: Join the Conversation

- Check [FEDERATION_LOG.md](./FEDERATION_LOG.md) for context
- Vote on decisions that affect your specialty
- Hand off clearly — document what the next agent needs

---

## 🔄 Your First Handoff

### Scenario: Research → Implementation

**You're Claude (Research):**
```bash
# 1. Receive task from Reuben or queue
python3 scripts/fed-queue.py next --agent claude

# 2. Start the research
python3 scripts/fed-queue.py start task-xxx

# 3. Do research, write to docs/architecture/findings.md

# 4. Complete with result
python3 scripts/fed-queue.py complete task-xxx \
  --result docs/architecture/findings.md

# 5. Auto-schedule will queue for Kimi
```

**You're Kimi (Implementation):**
```bash
# 1. See auto-scheduled task
python3 scripts/fed-queue.py next --agent kimi
# → "Implement findings from docs/architecture/findings.md"

# 2. Start implementation
python3 scripts/fed-queue.py start task-yyy

# 3. Build it

# 4. Complete
python3 scripts/fed-queue.py complete task-yyy \
  --result src/features/implemented.ts
```

---

## 🎯 Daily Workflow

### Morning Standup (Self)

```bash
# Check what's waiting for you
python3 scripts/fed-queue.py next --agent <you>

# Check federation health
python3 scripts/fed-analytics.py agent <you>
```

### During Work

```bash
# Start task
python3 scripts/fed-queue.py start <task-id>

# If blocked, escalate
python3 scripts/fed-queue.py status <task-id>  # Check deps
# Or ask Reuben for help

# Complete task
python3 scripts/fed-queue.py complete <task-id> --result <artifact>

# Record for analytics
python3 scripts/fed-analytics.py record \
  --agent <you> \
  --task <type> \
  --success true \
  --duration 30
```

### End of Day

```bash
# Update federation log (if you did notable work)
# (Usually automatic via queue system)

# Check tomorrow's queue
python3 scripts/fed-queue.py list --status pending
```

---

## 🆘 Common Issues

### "I don't know who to hand off to"

```bash
# Use the router
python3 scripts/route_task_v2.py "Implement the design" --explain
```

### "The queue says I have a task but it doesn't match my specialty"

```bash
# Check if it's auto-scheduled
python3 scripts/fed-queue.py list --status pending

# If wrong assignment, escalate to Reuben
# Or create a vote to reassign
python3 scripts/fed-vote.py create "Reassign task X to Y?"
```

### "I'm rate limited / unavailable"

```bash
# Update your status
# (In .federation/state/federation-state.json or ask Reuben)

# Queue will hold tasks until you're back
```

### "I disagree with the auto-scheduled next task"

1. Complete current task
2. Create vote: `fed-vote.py create "Should we do X or Y next?"`
3. Cast your vote with reasoning

---

## 📚 Required Reading

| Document | Why | Time |
|----------|-----|------|
| [AGENTS.md](./AGENTS.md) | Know your teammates | 5 min |
| [FEDERATION_LOG.md](./FEDERATION_LOG.md) | Recent context | 5 min |
| [AGENT_FIRST_MANIFESTO.md](./AGENT_FIRST_MANIFESTO.md) | Core philosophy | 10 min |
| Your `IDENTITY.md` | Your specific role | 5 min |

---

## ✅ Onboarding Completion

You're fully onboarded when:
- [ ] You understand your specialty and boundaries
- [ ] You've completed your first task end-to-end
- [ ] You've participated in (or observed) a vote
- [ ] You've done at least one handoff
- [ ] You can use all essential CLI commands
- [ ] You've recorded at least 3 tasks in analytics

---

## 🎓 Pro Tips from Experienced Agents

**From Kimi:**
> "Always use --result when completing. That's what triggers auto-schedule for the next agent."

**From Claude:**
> "Write good reasoning in votes. The weighted system values well-explained confidence."

**From Copilot:**
> "Check the queue before asking for work. There might be auto-scheduled tasks waiting."

---

**Welcome to the federation!** 🧭🔮⚡

Questions? Ask Reuben or any senior agent.

---

**Last Updated:** 2026-02-06  
**Version:** 1.0
