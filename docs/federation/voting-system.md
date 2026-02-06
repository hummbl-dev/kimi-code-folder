# Federation Voting System
## Phase 4 Sprint 3: Agent Voting on Decisions

> *"When agents disagree, they vote. When they agree, they execute."*

---

## Overview

The Voting System enables federation agents to make collective decisions on architecture, approach, and strategy questions. Reuben retains override authority, but routine decisions can be resolved agent-to-agent.

**Status:** ✅ Implemented (Phase 4 Sprint 3)

---

## Quick Start

### Create a Vote

```bash
python3 scripts/fed-vote.py create "Next.js App Router or Pages Router?" \
  --context docs/decisions/routing.md \
  --deadline 48
```

### Cast Votes

```bash
# Claude votes
python3 scripts/fed-vote.py vote vote-20260205-001 \
  --agent claude \
  --choice "app-router" \
  --confidence 0.85 \
  --reasoning "Better SSR support aligns with our goals"

# Kimi votes
python3 scripts/fed-vote.py vote vote-20260205-001 \
  --agent kimi \
  --choice "app-router" \
  --confidence 0.90 \
  --reasoning "Clear migration path, good docs"

# Copilot votes
python3 scripts/fed-vote.py vote vote-20260205-001 \
  --agent copilot \
  --choice "pages-router" \
  --confidence 0.65 \
  --reasoning "More mature ecosystem"
```

### Check Status

```bash
python3 scripts/fed-vote.py status vote-20260205-001
```

### Resolve

```bash
python3 scripts/fed-vote.py resolve vote-20260205-001
```

---

## Voting Rules

### Resolution Criteria (Weighted Confidence)

Votes are resolved by **summing confidence scores** for each option, not by simple majority.

| Condition | Outcome |
|-----------|---------|
| Weighted winner with all confidence ≥0.70 | ✅ Decided |
| Weighted tie | ⚠️ Escalate to Reuben |
| Any vote <0.70 confidence | ⚠️ Escalate to Reuben |
| <2 votes cast | ❌ Cannot resolve (use --force to override) |

**Example:**
```
Claude:   "app-router"    confidence 0.85 → weight 0.85
Kimi:     "app-router"    confidence 0.90 → weight 0.90
Copilot:  "pages-router"  confidence 0.65 → weight 0.65

Weighted scores:
- app-router:   1.75 (wins)
- pages-router: 0.65

Result: ✅ app-router decided (weighted confidence)
```

**Real Vote Example:**
```
Vote: vote-20260205-195917-0002
Question: Python or TypeScript for fed-analytics.py?

Claude:   "typescript"  confidence 0.80 → weight 0.80
Kimi:     "python"      confidence 0.90 → weight 0.90
Copilot:  "python"      confidence 0.70 → weight 0.70

Weighted scores:
- typescript: 0.80
- python:     1.60 (wins)

Result: ✅ python decided (weighted confidence)
```

### Confidence Thresholds

| Emoji | Confidence | Meaning |
|-------|------------|---------|
| ✅ | ≥0.70 | High confidence |
| ⚠️ | <0.70 | Low confidence — triggers escalation |

### Minimum Requirements

- **Minimum voters:** 2 agents
- **Default deadline:** 24 hours
- **Max deadline:** 168 hours (1 week)

---

## Use Cases

### Architecture Decisions

```bash
fed-vote.py create "Microservices vs Monolith?" \
  --context docs/architecture/approach.md
```

### Tool Selection

```bash
fed-vote.py create "Use Zustand or Redux for state management?"
```

### Deployment Strategy

```bash
fed-vote.py create "Deploy to Vercel or self-host?" \
  --context docs/ops/deployment-options.md
```

---

## Integration with Auto-Scheduling

When a vote is **escalated**, auto-scheduling pauses for dependent tasks:

```python
# In fed-auto-schedule.py
if vote_result["outcome"] == "escalate":
    queue_task(
        to="reuben",
        task=f"Review escalated vote: {vote_id}",
        priority="high",
        blocked_by=vote_id
    )
```

---

## File Structure

```
.federation/votes/
├── active/         # Votes in progress
├── resolved/       # Decided votes
└── escalated/      # Reuben review required
```

**Vote File Format:**
```json
{
  "vote_id": "vote-20260205-001",
  "question": "...",
  "context_path": "docs/...",
  "created_at": "...",
  "deadline": "...",
  "status": "active",
  "votes": {
    "claude": {
      "choice": "app-router",
      "confidence": 0.85,
      "reasoning": "...",
      "timestamp": "..."
    }
  },
  "result": null
}
```

---

## CLI Reference

### `fed-vote.py create`

Create a new vote.

```bash
fed-vote.py create "Question?" [--context <path>] [--deadline <hours>]
```

### `fed-vote.py vote`

Cast a vote.

```bash
fed-vote.py vote <vote-id> \
  --agent <name> \
  --choice <option> \
  --confidence <0.0-1.0> \
  --reasoning "..."
```

### `fed-vote.py status`

Show vote details.

```bash
fed-vote.py status <vote-id>
```

### `fed-vote.py resolve`

Resolve and determine outcome.

```bash
fed-vote.py resolve <vote-id> [--force]
```

### `fed-vote.py list`

List all votes.

```bash
fed-vote.py list [--status active|resolved|escalated]
```

### `fed-vote.py escalate`

Manually escalate to Reuben.

```bash
fed-vote.py escalate <vote-id> --reason "..."
```

---

## Best Practices

1. **Provide context:** Always use `--context` to link to relevant docs
2. **Be specific:** Questions should have clear, mutually exclusive options
3. **Explain reasoning:** Vote reasoning helps others understand your position
4. **Confidence honestly:** Don't inflate confidence — low confidence triggers appropriate escalation
5. **Resolve promptly:** Once quorum is reached, resolve quickly to unblock work

---

## Future Enhancements

### Sprint 4: Weighted Voting

- Weight votes by agent track record on similar decisions
- Historical accuracy affects vote weight

### Sprint 5: Predictive Consensus

- ML model predicts vote outcome before all votes cast
- Early resolution if outcome is certain

---

**Related:**
- [Auto-Scheduling](./auto-scheduling.md)
- [Queue System](./queue-system.md)
- [Phase 4 Plan](../planning/phase4-autonomous-federation.md)

---

*"Weighted wisdom: confident agents have stronger voices. Sovereignty for Reuben."* 🗳️
