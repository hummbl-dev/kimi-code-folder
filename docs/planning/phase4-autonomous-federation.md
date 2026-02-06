# Phase 4: Autonomous Federation
## Planning Document for Self-Coordinating Agent Systems

> *"The federation evolves from human-coordinated to self-organizing."*

---

## Executive Summary

**Phase 4 Objective:** Enable agents to coordinate work autonomously without Reuben micromanaging every handoff.

**Current State (End of Phase 3):**
- ✅ Routing system works (keyword → agent assignment)
- ✅ Federation log tracks handoffs
- ✅ Agent identity stacks established
- ✅ All 4 agents have defined specializations

**Phase 4 Target State:**
- Agents can schedule work with each other
- Agents can vote on approach disagreements
- Self-optimizing resource allocation
- Predictive routing based on success patterns

---

## I. Phase 4 Components

### Component 1: Autonomous Task Scheduling

**Problem:** Currently Reuben must explicitly say "pass to Kimi" for every handoff.

**Solution:** Agents can queue work for other agents based on task completion.

**Implementation Approach:**
```python
# When Claude completes research, auto-queue for Kimi
if task_type == "research" and has_implementation_phase:
    federation.queue_task(
        from_agent="claude",
        to_agent="kimi", 
        task="Implement design from claude/research/output.md",
        priority="normal",
        dependencies=[current_task_id]
    )
```

**Technical Requirements:**
- Task queue system (file-based or simple DB)
- Dependency tracking
- Priority scoring
- Agent availability checking

**MVP:** File-based queue in `.federation/queue/`

---

### Component 2: Agent Voting System

**Problem:** When agents disagree on approach, Reuben must decide.

**Solution:** Agents vote, Reuben only intervenes on ties or high-stakes decisions.

**Use Cases:**
- Architecture approach (microservices vs monolith)
- Tool/library selection
- Deployment strategy

**Implementation:**
```yaml
# .federation/votes/active/architecture-approach.yaml
question: "Should we use Next.js App Router or Pages Router?"
context: docs/architecture/routing-decision.md
votes:
  claude:
    choice: "app-router"
    confidence: 0.85
    reasoning: "Better for server components, aligns with our architecture goals"
  copilot:
    choice: "pages-router"
    confidence: 0.70
    reasoning: "More mature, better ecosystem support"
  kimi:
    choice: "app-router"
    confidence: 0.90
    reasoning: "Claude's research convinced me; execution path is clear"

# Result: app-router wins 2-1
# Action: Proceed with app-router
# If tie or low confidence: Escalate to Reuben
```

**Rules:**
- Majority wins (>50%)
- Minimum 2 agents must vote
- Confidence < 0.70 triggers Reuben review
- Ties escalate to Reuben

---

### Component 3: Self-Optimizing Resource Allocation

**Problem:** Static routing rules don't adapt to actual performance.

**Solution:** Track success metrics per agent-task combination and optimize routing.

**Metrics to Track:**
```json
{
  "routing_performance": {
    "claude": {
      "research_tasks": {
        "count": 15,
        "success_rate": 0.93,
        "avg_time": "45min",
        "rework_rate": 0.07
      },
      "implementation_tasks": {
        "count": 3,
        "success_rate": 0.33,
        "avg_time": "120min",
        "rework_rate": 0.67
      }
    }
  }
}
```

**Optimization Logic:**
```python
# If Kimi has 95% success on "implement" tasks but Claude only 33%,
# boost Kimi's score for future "implement" tasks
def optimize_route(scores, task_type, agent_history):
    for agent in scores:
        history = agent_history[agent][task_type]
        if history['count'] > 5:  # Sufficient data
            success_bonus = (history['success_rate'] - 0.80) * 0.10
            scores[agent] += success_bonus
    return scores
```

---

### Component 4: Predictive Task Routing

**Problem:** Keyword matching is static and limited.

**Solution:** Learn from past routing decisions to predict optimal agent.

**Training Data:**
```json
{
  "training_examples": [
    {
      "task": "Research state management for React",
      "assigned_to": "claude",
      "success": true,
      "time": "35min",
      "features": ["research", "react", "architecture"]
    },
    {
      "task": "Implement auth middleware",
      "assigned_to": "kimi",
      "success": true,
      "time": "20min",
      "features": ["implement", "auth", "middleware"]
    }
  ]
}
```

**Implementation Options:**

| Approach | Complexity | Accuracy | Maintenance |
|----------|------------|----------|-------------|
| Simple TF-IDF similarity | Low | Medium | Low |
| Rule-based with ML weights | Medium | High | Medium |
| Full ML classifier (scikit-learn) | High | Very High | High |

**Recommendation:** Start with TF-IDF similarity, evolve to rule-based ML weights.

---

## II. Technical Architecture

### Directory Structure

```
kimi-code-folder/
├── .federation/                    # NEW: Phase 4 infrastructure
│   ├── queue/                      # Pending tasks
│   │   ├── pending/
│   │   ├── in-progress/
│   │   └── completed/
│   ├── votes/                      # Active votes
│   │   └── active/
│   ├── state.json                  # Current federation state
│   ├── metrics.json                # Performance tracking
│   └── routing-history.jsonl       # Training data
│
├── configs/
│   ├── federation-routing.json     # v1.1 (current)
│   └── federation-routing-v2.json  # NEW: ML-enhanced routing
│
└── scripts/
    ├── route_task.py               # v1.0 (current)
    ├── route_task_v2.py            # NEW: Predictive routing
    ├── fed-queue.py                # NEW: Queue management
    ├── fed-vote.py                 # NEW: Voting system
    └── fed-analytics.py            # NEW: Metrics & optimization
```

### Core Data Models

**Task Queue Entry:**
```json
{
  "task_id": "task-2026-02-06-001",
  "status": "pending",
  "created_at": "2026-02-06T10:00:00Z",
  "from_agent": "claude",
  "to_agent": "kimi",
  "description": "Implement auth from claude's design",
  "priority": "high",
  "dependencies": ["task-2026-02-06-000"],
  "context": {
    "artifact_path": "docs/architecture/auth-design.md",
    "constraints": ["use_jwt", "support_oauth"]
  }
}
```

**Vote Record:**
```json
{
  "vote_id": "vote-2026-02-06-001",
  "question": "Next.js App Router vs Pages Router",
  "context_url": "docs/decisions/routing-approach.md",
  "deadline": "2026-02-06T18:00:00Z",
  "votes": {
    "claude": {"choice": "app-router", "confidence": 0.85, "reasoning": "..."},
    "copilot": {"choice": "pages-router", "confidence": 0.70, "reasoning": "..."}
  },
  "result": null,
  "escalated_to": null
}
```

---

## III. Implementation Roadmap

### Sprint 1: Foundation (Week 1)

**Goals:**
- [ ] Create `.federation/` directory structure
- [ ] Implement file-based task queue (`fed-queue.py`)
- [ ] Add queue status command: `fed status`
- [ ] Basic queue operations: add, list, complete

**Deliverables:**
- `.federation/queue/` working
- `scripts/fed-queue.py` functional
- Documentation in `docs/federation/queue-system.md`

---

### Sprint 2: Autonomous Scheduling (Week 2)

**Goals:**
- [ ] Agents can auto-queue tasks for other agents
- [ ] Dependency resolution
- [ ] Priority handling
- [ ] Integration with FEDERATION_LOG.md

**Deliverables:**
- Auto-queue triggers in research tasks
- Dependency tracking working
- Queue visualizations

**Example Flow:**
```
Claude completes: docs/architecture/auth-design.md
→ Auto-queues: TASK-002 for Kimi
→ Kimi sees: "Implement auth-design.md" in queue
→ Kimi executes → Marks complete
→ Federation log updated
```

---

### Sprint 3: Voting System (Week 3)

**Goals:**
- [ ] Vote creation: `fed vote create "question"`
- [ ] Agent voting interface
- [ ] Vote resolution logic
- [ ] Escalation to Reuben

**Deliverables:**
- `scripts/fed-vote.py` functional
- Voting UI in agent sessions
- Escalation notifications

**Test Case:**
Architecture decision with 3 agents voting, 1 dissenting → Resolution or escalation.

---

### Sprint 4: Analytics & Optimization (Week 4)

**Goals:**
- [ ] Metrics collection system
- [ ] Performance tracking per agent-task
- [ ] Simple optimization (boost high performers)
- [ ] Dashboard: `fed analytics`

**Deliverables:**
- `scripts/fed-analytics.py`
- `.federation/metrics.json` populated
- Optimization rules active

**Example:**
After 20 "implement" tasks:
- Kimi: 95% success → +0.05 routing boost
- Claude: 60% success → no boost
- Ollama: 30% success → -0.05 routing penalty

---

### Sprint 5: Predictive Routing (Week 5-6)

**Goals:**
- [ ] Collect training data (routing history)
- [ ] Implement TF-IDF similarity matching
- [ ] Hybrid routing: rules + ML
- [ ] A/B test vs v1 routing

**Deliverables:**
- `scripts/route_task_v2.py`
- 100+ training examples
- Accuracy measurement: target >90%

---

## IV. Success Metrics

### Phase 4 Completion Criteria

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Reuben handoffs per day | 10+ | <3 | Count in FEDERATION_LOG |
| Auto-queued tasks | 0 | 50%+ of tasks | Queue analysis |
| Voting resolution rate | N/A | 80% without escalation | Vote records |
| Routing accuracy | ~85% | >92% | Success rate tracking |
| Avg task completion time | Baseline | -20% | Time tracking |

### Quality Gates

- [ ] Queue system: 7 days without data loss
- [ ] Voting: 5 votes resolved, <20% escalation
- [ ] Optimization: Measurable improvement in success rates
- [ ] Predictive routing: >90% accuracy on test set

---

## V. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Agents queue work in infinite loops | **HIGH** | Max queue depth per agent, cycle detection |
| Voting deadlocks | **MEDIUM** | Timeout + auto-escalate, quorum requirements |
| Over-optimization (wrong agent for task) | **MEDIUM** | Human review for novel task types, confidence thresholds |
| Data loss in queue | **HIGH** | Git-backed queue, atomic writes, backups |
| Privacy in voting (agents see each other's reasoning) | **LOW** | Acceptable — federation requires transparency |
| Complexity explosion | **MEDIUM** | Strict MVP, defer edge cases, document everything |

---

## VI. Integration Points

### With Existing Systems

| Existing | Integration | Change |
|----------|-------------|--------|
| FEDERATION_LOG.md | Queue events auto-log | Append queue operations |
| AGENT_ASSIGNMENTS.md | Add auto-assignment rules | Update decision tree |
| federation-routing.json | v2 config for predictive | New file, migration path |
| Agent SOUL.md | Add autonomy principles | Minor updates |

### Human Override Points

Reuben retains control via:
1. **Queue override:** `fed queue cancel <task-id>`
2. **Vote escalation:** Always can override vote results
3. **Routing override:** `--agent <name>` forces assignment
4. **Emergency stop:** `fed pause` halts autonomous operations

---

## VII. Next Actions

### Immediate (This Session)

1. **Review this plan** — Reuben approves scope and priorities
2. **Clarify sequencing** — Parallel vs sequential sprints
3. **Define MVP boundaries** — What's in/out for first release

### Sprint 1 Kickoff (Next Session)

1. Create `.federation/` directory structure
2. Implement basic queue system
3. Test with simple task flow

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Autonomous Handoff** | Agent A queues work for Agent B without human intervention |
| **Vote Quorum** | Minimum agents required for valid vote (default: 2) |
| **Routing Confidence** | ML model certainty in agent selection (0.0-1.0) |
| **Task Dependency** | Task B cannot start until Task A completes |
| **Escalation** | Routing decision to human (Reuben) |

## Appendix B: Related Documents

- [AGENT_FEDERALISM_MANIFESTO.md](../../AGENT_FEDERALISM_MANIFESTO.md) — Phase 3 vision
- [FEDERATION_LOG.md](../../FEDERATION_LOG.md) — Current tracking
- [AGENT_ASSIGNMENTS.md](../../AGENT_ASSIGNMENTS.md) — Routing rules
- [federation-middleware.md](../architecture/federation-middleware.md) — Claude's architecture

---

**Document Status:** Planning phase  
**Version:** 1.0  
**Date:** 2026-02-05  
**Author:** Kimi (with Copilot/Claude input from Phase 3)  
**Review Status:** Pending Reuben approval  

---

*"From coordinated to autonomous. From human-managed to self-organizing. This is Phase 4."* 🔧🔮⚡
