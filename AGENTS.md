# Federation Agent Reference
## Quick Guide for Reuben and All Agents

> *"Know thyself, know thy teammates."*

---

## 🤖 Agent Roster

| Agent | Emoji | Specialty | Best For | Cost | Context |
|-------|-------|-----------|----------|------|---------|
| **Copilot** | 💭 | Thinking, planning, review | Quick questions, IDE work, brainstorming | Free | Medium |
| **Kimi** | 🔧 | Execution, implementation | Multi-file changes, deployment, testing | Low | Medium |
| **Claude** | 📚 | Research, analysis, docs | Architecture, deep dives, documentation | Medium | Large |
| **Ollama** | 🏠 | Local, fast iteration | Drafts, prototyping, offline work | Free | Medium |

---

## 🎯 Quick Routing Guide

### Use Copilot 💭 When:
- "What do you think about...?"
- "Review this code"
- "Help me plan..."
- "Quick question: ..."
- IDE-integrated work

**Example:** *"Review my React component structure"* → 💭 Copilot

---

### Use Kimi 🔧 When:
- "Implement..."
- "Build..."
- "Deploy..."
- "Fix bug in..."
- "Refactor across multiple files"
- "Test..."

**Example:** *"Implement authentication across 5 files"* → 🔧 Kimi

---

### Use Claude 📚 When:
- "Research..."
- "Analyze..."
- "Document..."
- "Architecture for..."
- "Compare options for..."
- "Deep dive into..."

**Example:** *"Research microservices patterns for our scale"* → 📚 Claude

---

### Use Ollama 🏠 When:
- "Draft..."
- "Sketch..."
- "Quick prototype..."
- "Offline work..."
- Low-stakes experimentation

**Example:** *"Draft a quick API spec to review"* → 🏠 Ollama

---

## 🔄 Handoff Patterns

### Claude → Kimi (Research → Implementation)
```
Claude: Research architecture
↓ (completes with docs)
Auto-scheduled: Kimi implements
```

### Kimi → Copilot (Implementation → Review)
```
Kimi: Build feature
↓ (completes with PR)
Auto-scheduled: Copilot reviews
```

### Copilot → Claude (Planning → Research)
```
Copilot: Plan approach
↓ (completes with design)
Auto-scheduled: Claude researches details
```

---

## 🛠️ Federation Commands

### Queue Management
```bash
# Add task
python3 scripts/fed-queue.py add --from <agent> --to <agent> --task "..." --priority high

# Check your tasks
python3 scripts/fed-queue.py next --agent <you>

# Start work
python3 scripts/fed-queue.py start <task-id>

# Complete
python3 scripts/fed-queue.py complete <task-id> --result <artifact-path>
```

### Voting
```bash
# Create vote
python3 scripts/fed-vote.py create "Question?" --context <path>

# Cast vote
python3 scripts/fed-vote.py vote <vote-id> --agent <you> --choice <option> --confidence 0.85 --reasoning "..."

# Check results
python3 scripts/fed-vote.py status <vote-id>
```

### Analytics
```bash
# Dashboard
python3 scripts/fed-analytics.py dashboard

# Your stats
python3 scripts/fed-analytics.py agent <you>

# Record task
python3 scripts/fed-analytics.py record --agent <you> --task <type> --success true --duration 25
```

### Routing
```bash
# Route task (v1 rules)
python3 scripts/route_task.py "Research authentication"

# Route task (v2 hybrid ML)
python3 scripts/route_task_v2.py "Build dashboard" --explain
```

---

## 📊 Current Status

Check federation status anytime:
```bash
python3 scripts/fed-auto-schedule.py status
python3 scripts/fed-analytics.py dashboard
```

---

## 🆘 Getting Help

| Problem | Solution |
|---------|----------|
| Don't know who to assign | Use `route_task_v2.py "..." --explain` |
| Task blocked | Check `fed-queue.py list --status pending` |
| Agent unavailable | Queue for later or escalate to Reuben |
| Disagreement on approach | Create a vote with `fed-vote.py create` |
| System issue | Check `FEDERATION_LOG.md` latest entries |

---

## 📝 Agent-Specific Notes

### Copilot 💭
- **You are here:** VS Code integration
- **Strength:** Real-time, contextual help
- **Limitation:** Not for multi-file refactors
- **Memory:** Session-based, use FEDERATION_LOG for persistence

### Kimi 🔧
- **Workspace:** `kimi-code-folder/`
- **Strength:** Parallel execution, 33 skills
- **Limitation:** Not for high-level architecture design
- **Memory:** Full workspace context

### Claude 📚
- **Workspace:** `claude-code-folder/`
- **Strength:** Long context, deep reasoning
- **Limitation:** Rate limits (use Copilot as fallback)
- **Memory:** Session + identity stack

### Ollama 🏠
- **Location:** Local machine
- **Strength:** Instant, free, offline
- **Limitation:** Lower capability than cloud agents
- **Memory:** None (stateless)

---

## 🎓 Pro Tips

1. **Always record completions** — Helps analytics and routing optimization
2. **Use --result on complete** — Triggers auto-schedule rules
3. **Vote with confidence** — Weighted system values certainty
4. **Check queue before starting** — May have auto-scheduled tasks waiting
5. **Document in FEDERATION_LOG** — Cross-agent visibility

---

**Last Updated:** 2026-02-06  
**Version:** 1.0  
**Maintained By:** All federation agents

---

*"Specialization is the key to federation success."* 🧭🔮⚡
