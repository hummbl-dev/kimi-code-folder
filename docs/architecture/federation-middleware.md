# Federation Middleware Architecture
## Technical Design for Automated Agent Coordination (Phase 3)

**Author:** Claude (Analyst)
**Date:** 2026-02-05
**Status:** Draft / Research Document
**Related:** `AGENT_FEDERALISM_MANIFESTO.md` (Phase 3 requirements)

---

## 1. Executive Summary

Phase 3 of Agent Federalism introduces **Federation Middleware**: a coordination layer that automates agent assignment, tracks cross-agent dependencies, maintains federation logs, and monitors resource usage. This document analyzes three implementation approaches and recommends a path that balances immediate utility with long-term extensibility.

**Key Decision:** Build middleware as a CLI-first routing layer with explicit configuration, evolving toward learned patterns as the federation matures.

---

## 2. Problem Statement

### Current State (Manual Coordination)
```
User → Decides which agent → Frames task → Hands off → Tracks progress manually
```

Reuben currently:
1. Parses each task mentally to determine best agent
2. Frames context manually for each handoff
3. Tracks dependencies in his head or in scattered notes
4. Updates FEDERATION_LOG.md by hand
5. Monitors costs across providers separately

### Target State (Federation Middleware)
```
User → Middleware parses task → Routes to best agent → Tracks dependencies → Logs automatically
```

Middleware should:
1. **Route** tasks to appropriate agents based on signals
2. **Track** which tasks depend on which
3. **Log** all federation activity automatically
4. **Monitor** resource usage and cost per agent

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FEDERATION MIDDLEWARE                        │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   ROUTER    │  │  TRACKER    │  │       LOGGER            │ │
│  │             │  │             │  │                         │ │
│  │ • Pattern   │  │ • Deps      │  │ • FEDERATION_LOG.md     │ │
│  │   matching  │  │ • State     │  │ • Agent memory sync     │ │
│  │ • Agent     │  │ • Blockers  │  │ • Cost roll-up          │ │
│  │   selection │  │             │  │                         │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
│         │                │                      │               │
│         └────────────────┼──────────────────────┘               │
│                          │                                      │
│                    ┌─────▼─────┐                                │
│                    │   CORE    │                                │
│                    │  ENGINE   │                                │
│                    └─────┬─────┘                                │
└──────────────────────────┼──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐       ┌─────────┐        ┌─────────┐
   │ Copilot │       │  Kimi   │        │ Claude  │
   │(Thinker)│       │ (Actor) │        │(Analyst)│
   └─────────┘       └─────────┘        └─────────┘
```

### Core Components

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| **Router** | Match task to best agent | Task text, context | Agent assignment + confidence |
| **Tracker** | Manage task dependencies | Task ID, deps list | Dependency graph, blockers |
| **Logger** | Federated logging | Events from all components | FEDERATION_LOG.md entries |
| **Core Engine** | Orchestration glue | All components | Unified API for coordination |

---

## 4. Three Implementation Approaches

### Approach A: Rule-Based Router (Explicit Configuration)

**Concept:** A CLI tool that matches task text against explicit keyword rules defined in a YAML/JSON config file.

```yaml
# federation-routing.yaml
routes:
  - pattern: "research|analyze|document|architecture"
    agent: claude
    confidence: 0.9

  - pattern: "implement|build|deploy|test|refactor"
    agent: kimi
    confidence: 0.9

  - pattern: "think|plan|review|clarify"
    agent: copilot
    confidence: 0.8

  - pattern: "draft|iterate|prototype"
    agent: ollama
    confidence: 0.7

fallback: copilot  # If no match
```

**CLI Usage:**
```bash
$ fed route "Research the Temporal Workflows library"
# → Agent: claude (confidence: 0.9, matched: "research")

$ fed route "Implement the auth middleware from Claude's design"
# → Agent: kimi (confidence: 0.9, matched: "implement")
```

**Pros:**
- Fully transparent (human-readable rules)
- Zero cold-start (works immediately)
- Easy to debug and adjust
- No ML dependencies or training data
- Aligns with HUMMBL's governance-first philosophy

**Cons:**
- Requires manual rule maintenance
- May miss nuanced task classifications
- Rigid pattern matching won't catch synonyms
- Rules can become stale as agents evolve

**Complexity:** Low (1-2 days to build)

---

### Approach B: ML-Based Classifier (Learned Patterns)

**Concept:** A lightweight classifier trained on past task assignments from FEDERATION_LOG.md, using embeddings to match new tasks.

```
┌──────────────────┐     ┌────────────────┐     ┌─────────────┐
│ Historical Tasks │ ──▶ │ Embedding Model│ ──▶ │ Classifier  │
│ + Agent Labels   │     │ (local/ollama) │     │ (k-NN/SVM)  │
└──────────────────┘     └────────────────┘     └─────────────┘
                                                      │
                                                      ▼
                              ┌────────────────────────────────┐
                              │ New Task → Best Agent + Score  │
                              └────────────────────────────────┘
```

**Training Data Source:**
```bash
# Extract from FEDERATION_LOG.md
$ fed train --source federation-log.md --model ollama/nomic-embed-text
# → Model saved to .federation/classifier.pkl
```

**CLI Usage:**
```bash
$ fed route "Help me understand how the payment flow works"
# → Agent: claude (confidence: 0.87, model: learned)
```

**Pros:**
- Learns from actual usage patterns
- Handles synonyms and semantic similarity
- Improves as federation log grows
- Can catch patterns humans miss

**Cons:**
- Requires training data (cold-start problem)
- "Black box" decisions harder to audit
- Depends on embedding model availability
- May drift or make surprising assignments
- More complex to maintain and debug

**Complexity:** Medium-High (1-2 weeks, plus ongoing training)

---

### Approach C: Hybrid Pattern Matcher (Structured + Fuzzy)

**Concept:** Rule-based core with semantic similarity fallback. Explicit rules catch clear signals; fuzzy matching handles ambiguous cases.

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID ROUTER                            │
│                                                             │
│   ┌─────────────────────────┐    ┌────────────────────────┐│
│   │    RULE ENGINE          │    │   SEMANTIC FALLBACK    ││
│   │                         │    │                        ││
│   │  IF pattern matches     │    │  Embed task text       ││
│   │  → Return agent + 0.9   │    │  Compare to agent      ││
│   │  ELSE → Fallback        │    │  profile embeddings    ││
│   │                         │    │  → Return closest      ││
│   └───────────┬─────────────┘    └───────────┬────────────┘│
│               │                              │              │
│               └──────────┬───────────────────┘              │
│                          ▼                                  │
│                   ┌─────────────┐                           │
│                   │ FINAL PICK  │                           │
│                   │ + Confidence│                           │
│                   └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

**Configuration:**
```yaml
# federation-routing.yaml
mode: hybrid

rules:
  # High-confidence explicit patterns (tried first)
  - pattern: "pass this to (claude|kimi|copilot|ollama)"
    extract: true  # Extract agent name from capture group
    confidence: 1.0

  - pattern: "research|analyze|synthesize"
    agent: claude
    confidence: 0.9

semantic_fallback:
  enabled: true
  model: ollama/nomic-embed-text
  agent_profiles:
    claude: "research, documentation, architecture, analysis, reasoning"
    kimi: "implementation, testing, deployment, multi-file, execution"
    copilot: "thinking, planning, review, quick questions, clarification"
    ollama: "drafting, prototyping, local work, fast iteration"
  threshold: 0.6  # Below this, ask user to clarify
```

**CLI Usage:**
```bash
$ fed route "Research the Temporal Workflows library"
# → Agent: claude (confidence: 0.9, source: rule)

$ fed route "Help me figure out the best approach for caching"
# → Agent: copilot (confidence: 0.72, source: semantic)

$ fed route "Do the thing"
# → Confidence too low (0.41). Please clarify or specify agent.
```

**Pros:**
- Best of both worlds (transparent + intelligent)
- Works immediately with rules, improves with semantics
- Graceful degradation (rules work without embedding model)
- Clear audit trail (knows source of each decision)
- Can tune rule/semantic weighting

**Cons:**
- More complex than pure rules
- Still requires embedding model for fallback
- Two systems to maintain
- Need to calibrate confidence thresholds

**Complexity:** Medium (3-5 days for core, ongoing tuning)

---

## 5. Comparison Matrix

| Criterion | A: Rules | B: ML | C: Hybrid |
|-----------|----------|-------|-----------|
| **Time to first working version** | 1-2 days | 1-2 weeks | 3-5 days |
| **Cold-start capability** | Full | None | Full (rules) |
| **Auditability** | Excellent | Poor | Good |
| **Handles ambiguity** | Poor | Good | Good |
| **Maintenance burden** | Medium | High | Medium |
| **Governance alignment** | Excellent | Moderate | Good |
| **Extensibility** | Limited | High | High |
| **Dependencies** | None | Ollama/embedding | Optional Ollama |
| **Learning from usage** | Manual | Automatic | Semi-automatic |

---

## 6. Recommendation

### Start with Approach C (Hybrid), Built Iteratively

**Phase 1 (Week 1):** Rule-based core only
- Implement `fed route` CLI with YAML config
- Cover 80% of common task patterns
- No semantic fallback yet
- Ship and use in daily federation work

**Phase 2 (Week 2-3):** Add dependency tracking + logging
- Implement `fed track` for dependency management
- Auto-update FEDERATION_LOG.md on each routing decision
- Add `fed status` to show current assignments

**Phase 3 (Week 4+):** Add semantic fallback
- Add embedding-based fallback for ambiguous tasks
- Train agent profiles on actual federation log data
- Tune confidence thresholds based on real usage

**Phase 4 (Ongoing):** Resource monitoring
- Add cost tracking per agent
- Dashboard for federation health metrics
- Alerts for anomalous patterns

### Rationale

1. **Governance alignment:** Rules-first respects HUMMBL's "governance-first" principle. Every routing decision is explainable from config.

2. **Iterative delivery:** Useful from day 1. No need to wait for training data or ML infrastructure.

3. **Graceful evolution:** The hybrid architecture allows adding ML later without replacing the core. If semantic fallback proves unreliable, disable it; rules still work.

4. **Practical constraint:** You already have 50+ agents in the workspace. A simple routing layer that works today is more valuable than a sophisticated one that ships in a month.

---

## 7. Implementation Sketch

### Core Data Structures

```typescript
// federation-core.ts

interface TaskRoute {
  taskId: string;
  taskText: string;
  assignedAgent: AgentName;
  confidence: number;
  source: 'rule' | 'semantic' | 'explicit' | 'fallback';
  matchedPattern?: string;
  timestamp: Date;
}

interface TaskDependency {
  taskId: string;
  dependsOn: string[];  // Task IDs this task is blocked by
  blocks: string[];     // Task IDs waiting on this task
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
}

interface FederationLogEntry {
  timestamp: Date;
  eventType: 'route' | 'handoff' | 'complete' | 'block' | 'unblock';
  taskId: string;
  agent: AgentName;
  details: Record<string, unknown>;
}
```

### CLI Interface

```bash
# Core routing
fed route "task description"           # Returns best agent
fed route --agent kimi "task"          # Override with explicit agent

# Dependency tracking
fed track --depends-on TASK-1 "new task"  # Create with dependency
fed status                                 # Show all tasks and blockers
fed complete TASK-2                        # Mark complete, unblock dependents

# Logging and metrics
fed log                                # Tail FEDERATION_LOG.md
fed metrics                            # Show cost/usage per agent
fed metrics --agent claude             # Filter to one agent
```

### File Layout

```
kimi-code-folder/
├── .federation/
│   ├── config.yaml           # Routing rules
│   ├── tasks.json            # Active task state
│   ├── deps.json             # Dependency graph
│   └── metrics.json          # Usage counters
├── FEDERATION_LOG.md         # Human-readable log (auto-updated)
└── bin/
    └── fed                   # CLI entrypoint
```

---

## 8. Open Questions for Reuben

Before implementation, these decisions need human input:

1. **Where should middleware live?**
   - `kimi-code-folder/` (Kimi maintains it)?
   - `shared-hummbl-space/` (shared infrastructure)?
   - New repo (`federation-middleware/`)?

2. **Explicit assignment syntax?**
   - Current: "Pass this to Kimi" (prose)
   - Alternative: `@kimi research auth patterns` (mention syntax)
   - Alternative: `--agent kimi` (CLI flag)

3. **Cost tracking granularity?**
   - Per task?
   - Per agent per day?
   - Both?

4. **Conflict resolution?**
   - If two rules match with equal confidence, which wins?
   - Proposal: First match wins, or require explicit agent

---

## 9. Next Actions

| Action | Owner | Priority |
|--------|-------|----------|
| Review this architecture doc | Reuben | High |
| Answer open questions above | Reuben | High |
| Implement Phase 1 (rules-based CLI) | Kimi | After approval |
| Create `federation-routing.yaml` seed | Claude | After approval |
| Document in AGENT_ASSIGNMENTS.md | Claude | After approval |

---

**Document Status:** Ready for Review
**Confidence:** High on approach, medium on timeline
**Source:** Analysis of AGENT_FEDERALISM_MANIFESTO.md Phase 3 requirements
