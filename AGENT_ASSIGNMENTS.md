# AGENT_ASSIGNMENTS.md
## Resource Allocation & Task Routing for the Agent Federation

> *"The right agent for the right task. No more, no less."*

---

## Current Assignments

### Active Tasks

| Task ID | Task Description | Assigned Agent | Status | Started | Blocked By | ETA |
|---------|------------------|----------------|--------|---------|------------|-----|
| TASK-001 | Initialize Claude agent identity stack | Kimi | ✅ Complete | 2026-02-05 | — | Done |
| TASK-002 | Research federation middleware architecture | Claude | ✅ Complete | 2026-02-05 | — | Done |
| TASK-003 | Create FEDERATION_LOG.md structure | Kimi | ✅ Complete | 2026-02-05 | — | Done |
| TASK-004 | Create AGENT_ASSIGNMENTS.md | Kimi | ✅ Complete | 2026-02-05 | — | Done |
| TASK-005 | Build route-task.sh prototype | Claude/Kimi | ✅ Complete | 2026-02-05 | — | Done |

### Pending Tasks

| Task ID | Task Description | Proposed Agent | Priority | Dependencies |
|---------|------------------|----------------|----------|--------------|
| TASK-006 | Review middleware architecture | Reuben | High | TASK-002 |
| TASK-007 | Implement agent router v1 | Kimi | High | TASK-005, Reuben approval |
| TASK-008 | Test federation handoff protocol | All | Medium | TASK-007 |
| TASK-009 | Document federation patterns | Claude | Low | TASK-008 |

### Completed Tasks (Last 7 Days)

| Task ID | Task Description | Agent | Completed | Outcome |
|---------|------------------|-------|-----------|---------|
| TASK-001 | Initialize Claude agent | Kimi | 2026-02-05 | ✅ Success — identity stack created |

---

## Resource Allocation Matrix

### Agent Capabilities & Costs

| Agent | Specialty | Superpower | Cost/Tier | Context Size | Best For | Avoid |
|-------|-----------|------------|-----------|--------------|----------|-------|
| **Copilot** | Interactive thinking, structure | Real-time feedback, IDE integration | Free/cheap | Medium | Quick thinking, inline edits, code review | Multi-file refactors, long research |
| **Kimi** | Autonomous execution, multi-file | Parallel execution, 33 skills | Moderate | Medium | Implementation, testing, deployment, refactoring | High-level architecture design |
| **Claude** | Research, analysis, documentation | Long context, deep reasoning | Moderate | Large | Research, architecture docs, tradeoff analysis | Direct file modifications |
| **Ollama** | Fast iteration, drafting | Local, instant, free, offline | Free | Medium | Rapid prototyping, low-stakes exploration, offline work | Production deployments, research |

### Agent Status

| Agent | Status | Current Task | Availability | Last Active |
|-------|--------|--------------|--------------|-------------|
| Copilot | 🟢 Available | — | 100% | — |
| Kimi | 🟡 Busy | Creating AGENT_ASSIGNMENTS.md | 50% | 2026-02-05 |
| Claude | 🟡 Busy | Researching middleware architecture | 0% | 2026-02-05 |
| Ollama | 🟢 Available | — | 100% | — |

---

## Decision Rules: Task → Agent Mapping

> **Cross-Reference:** See `configs/federation-routing.json` for the machine-readable implementation of these rules, including scoring weights and negative patterns.

### Confidence Thresholds

| Threshold | Value | Meaning |
|-----------|-------|---------|
| **Explicit mention** | 1.0 | Agent explicitly named (e.g., "pass to kimi", "@claude") |
| **Auto-assign** | ≥0.70 | High confidence — assign automatically |
| **Review suggested** | 0.60–0.69 | Medium confidence — route but flag for review |
| **Clarification needed** | <0.60 | Low confidence — ask Reuben for clarification |

### Scoring Weights (from federation-routing.json)

| Pattern Type | Weight | Example |
|--------------|--------|---------|
| Primary keyword | 0.95 | "research" → Claude |
| Secondary keyword | 0.85 | "think about" → Copilot |
| Contextual pattern | 0.75 | Regex match on phrasing |
| Negative pattern | -0.20 | Penalty for mismatched keywords |
| Multiple matches | +0.05 each | Bonus for multiple keyword hits (max +0.10) |

### Automated Assignment Keywords

| Keyword Pattern | Assigned Agent | Confidence | Rationale |
|-----------------|----------------|------------|-----------|
| "research", "analyze", "architecture", "design doc", "tradeoffs" | Claude | 95% | Research specialty |
| "implement", "build", "deploy", "refactor", "test", "fix" | Kimi | 95% | Execution specialty |
| "think about", "how should we", "what's the best way" | Copilot | 90% | Interactive thinking |
| "draft", "sketch", "prototype", "quick version" | Ollama | 85% | Fast iteration, free |
| "review", "check", "look at this" | Copilot | 90% | IDE integrated |
| "multi-file", "across", "all files in" | Kimi | 95% | Parallel execution |
| "documentation", "spec", "RFC", "proposal" | Claude | 90% | Long-form writing |
| "offline", "no internet", "local" | Ollama | 100% | Runs locally |
| "SITREP", "situation report", "status report" | Claude | 95% | Analysis work |
| "PR review", "code review" | Copilot | 90% | IDE-integrated review |
| "production deploy", "prod release" | Kimi* | 95% | *Requires human approval |
| "security review", "threat model", "vulnerability" | Claude | 90% | Security analysis |

### Decision Tree

```
START: Task received
│
├─→ Is it thinking/planning?
│   ├─ Yes → Is it quick/IDE-based?
│   │   ├─ Yes → Copilot
│   │   └─ No → Claude
│   └─ No → Continue
│
├─→ Is it execution?
│   ├─ Yes → Is it multi-file or needs skills?
│   │   ├─ Yes → Kimi
│   │   └─ No → Is it quick/offline?
│   │       ├─ Yes → Ollama
│   │       └─ No → Kimi
│   └─ No → Continue
│
├─→ Is it research/documentation?
│   └─ Yes → Claude
│
└─→ Default: Ask Reuben for clarification
```

### Override Rules

1. **Explicit assignment wins** — If Reuben says "Pass to Kimi," ignore keywords
2. **Agent availability** — If assigned agent is busy, queue or reassign
3. **Cost optimization** — For low-stakes tasks, prefer Ollama or Copilot
4. **Context continuity** — If agent has existing context, prefer continuity

### Confidence Scoring (from federation-routing.json)

| Threshold | Value | Meaning |
|-----------|-------|---------|
| **Explicit mention** | 1.0 | "@kimi" or "pass to claude" — immediate assignment |
| **Auto-assign** | ≥0.70 | High confidence — route automatically |
| **Primary keyword** | 0.95 | Strong signal (implement, research, etc.) |
| **Secondary keyword** | 0.85 | Good signal (write code, analyze, etc.) |
| **Contextual pattern** | 0.75 | Pattern match ("how does X work") |
| **Ambiguity** | <0.60 | Low confidence — ask for clarification |

### Scoring Modifiers

| Modifier | Effect | Example |
|----------|--------|---------|
| Multiple keywords | +0.05 each (max +0.10) | "implement + test + deploy" = +0.10 |
| Task length >50 chars | +0.02 | Longer tasks get slight boost |
| Negative pattern | -0.20 | "research" in Kimi's task = penalty |

> 📁 **Implementation:** See `configs/federation-routing.json` for full keyword taxonomy and `scripts/route_task.py` for the scoring algorithm.

---

## Task Routing Algorithm (v0.1)

### Input
```yaml
task_description: "string"
file_paths: ["optional", "paths"]
explicit_agent: "optional_agent_name"
urgency: "low|medium|high"
cost_sensitive: true|false
```

### Logic
```python
def route_task(task):
    # 1. Check explicit assignment
    if task.explicit_agent:
        return task.explicit_agent
    
    # 2. Check for keyword matches
    scores = {
        'claude': score_keywords(task.description, CLAUDE_KEYWORDS),
        'kimi': score_keywords(task.description, KIMI_KEYWORDS),
        'copilot': score_keywords(task.description, COPILOT_KEYWORDS),
        'ollama': score_keywords(task.description, OLLAMA_KEYWORDS)
    }
    
    # 3. Apply modifiers
    if task.cost_sensitive:
        scores['ollama'] += 0.2
        scores['copilot'] += 0.1
    
    if task.urgency == 'high':
        scores['kimi'] += 0.1  # Fast execution
        scores['ollama'] += 0.2  # Instant response
    
    if task.file_paths and len(task.file_paths) > 3:
        scores['kimi'] += 0.3  # Multi-file advantage
    
    # 4. Check availability
    for agent in sorted(scores, key=scores.get, reverse=True):
        if is_available(agent):
            return agent
    
    # 5. Default
    return 'queue_for_reuben'
```

### Output
```yaml
recommended_agent: "agent_name"
confidence: 0.0-1.0
reason: "explanation"
alternative: "fallback_agent"
```

---

## Workload Balancing

### Queue Management

| Queue | Depth | Max Wait Time | Priority Handling |
|-------|-------|---------------|-------------------|
| Claude (Research) | 0 | N/A | FIFO + Reuben override |
| Kimi (Execution) | 1 | 10 min | Urgent tasks jump queue |
| Copilot (Thinking) | 0 | Immediate | Always available |
| Ollama (Local) | 0 | Immediate | Always available |

### Escalation Rules

1. **Agent overloaded** → Queue or offload to next best agent
2. **Task blocked > 30 min** → Escalate to Reuben
3. **Rework required** → Return to original agent with notes
4. **Cross-agent dependency** → Both agents coordinate via FEDERATION_LOG

---

## Cost Optimization Strategy

### Tier-Based Routing

| Tier | Cost | Use Case | Agents |
|------|------|----------|--------|
| **Free** | $0 | Drafts, prototyping, offline work, quick checks | Ollama, Copilot |
| **Low** | $0-0.10 | Simple execution, small refactors | Kimi (short tasks) |
| **Medium** | $0.10-0.50 | Research, documentation, medium execution | Claude, Kimi |
| **High** | $0.50+ | Deep research, complex architecture, large refactors | Claude, Kimi (combined) |

### Budget Tracking

| Date | Agent | Tasks | Est. Cost | Notes |
|------|-------|-------|-----------|-------|
| 2026-02-05 | Kimi | 3 | ~$0.15 | Agent initialization, docs |
| 2026-02-05 | Claude | 1 | ~$0.50 | Architecture research |
| **Total** | | **4** | **~$0.65** | Within budget |

---

## Templates

### Adding a New Task

```markdown
| TASK-00X | [Description] | [Agent] | ⏳ Pending | YYYY-MM-DD | [Blocked] | [ETA] |
```

### Updating Task Status

```markdown
# Change status emoji:
⏳ Pending → 🔄 Active → ✅ Complete / ❌ Failed
```

### Recording Assignment Decision

```markdown
## Decision: TASK-00X

**Task:** [Description]
**Routed To:** [Agent]
**Confidence:** [0-100%]
**Reasoning:**
- Keyword match: [pattern]
- Task type: [category]
- Agent availability: [status]
- Cost tier: [free/low/medium/high]

**Alternative Considered:** [Agent] (rejected because [reason])
```

---

## Integration with FEDERATION_LOG

This document works with FEDERATION_LOG.md:

- **AGENT_ASSIGNMENTS.md** = What agents *should* be working on (planning)
- **FEDERATION_LOG.md** = What agents *are* working on and *have done* (tracking)

When a task is assigned here, a chain is created in the log.
When a task completes here, it's recorded in the log's history.

---

**Document Status:** Living allocation matrix  
**Version:** 1.0  
**Maintained By:** Reuben + Kimi (infrastructure)  
**Update Frequency:** When assignments change  

---

*"Efficient allocation is invisible. You only notice it when it's broken."* 🔧🔮
