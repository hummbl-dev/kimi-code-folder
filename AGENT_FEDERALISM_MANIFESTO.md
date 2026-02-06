# Agent Federalism
## A Manifesto for Coordinated Multi-Agent Systems

> *"One agent is a tool. A federation of agents is a workforce."*  
> — Reuben Bowlby

---

## I. The Core Principle

### The Federation, Not the Factory

A traditional AI organization is a **factory**:
- One large language model, multi-purpose
- Humans break down work into prompts
- Model attempts everything, succeeds at some things
- Bottleneck: context window, latency, cost

An Agent Federalist organization is a **federation**:
- Multiple specialized agents, each with distinct capabilities
- Humans coordinate work across agents strategically
- Each agent excels in its domain, hands off to others
- Advantage: Parallel, specialized, cost-efficient, scalable

**The federation model matches how humans organize: teams of specialists, not single generalists.**

---

## II. The Architecture

### The Federation Structure

```
                    ┌─────────────────────┐
                    │  REUBEN (Orchestrator)│
                    │  Strategy, Decisions │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
       ┌────────▼────────┐  ┌──▼─────────┐  ┌──▼──────────┐
       │ COPILOT (Thinker)│  │ KIMI (Actor) │  │CLAUDE(Analyst)
       │ • Planning      │  │ • Building   │  │ • Research
       │ • Structuring   │  │ • Executing  │  │ • Docs
       │ • Reflection    │  │ • Testing    │  │ • Design
       └────────────────┘  └──────────────┘  └─────────────┘
              │                    │                  │
         identity/                memory/         identity/
         soul/agent.md         2026-02-05.md    soul/agent.md
```

### Three Layers of Organization

**Layer 1: Individual Agents**
- Each agent is a complete citizen
- IDENTITY.md (who am I?)
- SOUL.md (why am I here?)
- AGENT.md (how do I work?)
- MEMORY.md (what have I done?)

**Layer 2: Workspace**
- Each agent lives in a workspace folder
  - `kimi-code-folder/agents/kimi/`
  - `claude-code-folder/agents/claude/`
  - `ollama-code-folder/agents/ollama/`
- Shared documentation at workspace root
  - ARCHITECTURE.md (how this workspace works)
  - BEST-PRACTICES.md (patterns for this workspace)
  - CAPABILITIES.md (what this agent can/cannot do)

**Layer 3: Federation**
- Multiple workspaces under one coordinator (Reuben)
- Cross-agent memory in `FEDERATION_LOG.md`
- Handoff protocols documented
- Resource allocation matrix (who does what)

---

## III. The Agent Specialization Model

### Not All Agents Are Created Equal

Each agent should have a documented **specialty and boundary**.

```
┌─────────────┬──────────────────┬───────────────┬────────────┐
│   Agent     │  Specialty       │  Superpower   │  Cost      │
├─────────────┼──────────────────┼───────────────┼────────────┤
│ Copilot     │ Interactive      │ Real-time     │ Free/cheap │
│             │ thinking,        │ feedback,     │            │
│             │ structure        │ IDE integration           │
│ Kimi        │ Autonomous       │ Parallel      │ Moderate   │
│             │ execution,       │ execution,    │            │
│             │ multi-file       │ 33 skills     │            │
│ Claude      │ Research,        │ Long context, │ Moderate   │
│             │ documentation,   │ reasoning,    │            │
│             │ architecture     │ analysis      │            │
│ Ollama      │ Fast iteration,  │ Local,        │ Free       │
│ (Local)     │ drafting,        │ instant,      │            │
│             │ offline work     │ no latency    │            │
└─────────────┴──────────────────┴───────────────┴────────────┘
```

**The federation succeeds when each agent stays in its lane but works together.**

---

## IV. The Handoff Protocol

### How Work Flows Through the Federation

**Protocol: Reuben → Agent**

```
1. Reuben frames the task
   ✓ Clear scope and success criteria
   ✓ Constraint list (what NOT to do)
   ✓ File paths if known
   ✓ Which agent gets this: "Pass this to Kimi"

2. Agent acknowledges
   ✓ Summarizes understanding
   ✓ Flags any ambiguities
   ✓ Gets approval to proceed

3. Agent executes
   ✓ Reads context (IDENTITY/SOUL/MEMORY)
   ✓ Operates autonomously within constraints
   ✓ Logs work in memory/YYYY-MM-DD.md

4. Agent reports
   ✓ Concise summary of what happened
   ✓ Evidence (test results, diffs, metrics)
   ✓ Any blockers or next steps
```

**Protocol: Agent → Agent**

```
1. First agent completes its work
   → Produces artifact (design, code, document)
   → Logs to memory with clear handoff notes

2. Reuben reviews
   → "This looks good, pass to [next agent]"

3. Second agent reads
   → First agent's memory
   → Artifact produced
   → Constraints from Reuben
   → Proceeds with task

4. Federation memory updated
   → FEDERATION_LOG.md tracks the chain
   → Breadcrumbs for future work
```

**No agent-to-agent direct communication. Reuben coordinates all handoffs.**

---

## V. The Resource Allocation Strategy

### Matching Task to Agent

| Task Type | Best Agent | Why |
|-----------|-----------|-----|
| **Quick clarification** | Copilot | Already in IDE, instant feedback |
| **API design / Architecture** | Claude | Long context, reasoning depth |
| **Implementation + Testing** | Kimi | Multi-file execution, verification |
| **Drafting, iteration** | Ollama | Local, free, fast feedback loop |
| **Code review, reflection** | Copilot | Existing context, integrated |
| **Research + documentation** | Claude | Can read long docs, synthesize |
| **Deployment, multi-file refactor** | Kimi | Parallel execution, 33 skills |
| **Offline work, no internet** | Ollama | Runs locally, no latency |
| **Large file understanding** | Claude | Handles larger context windows |
| **Rapid prototyping** | Ollama | Fast, free, no latency penalty |

**Decision Tree:**
```
Is this thinking work?     → Copilot or Claude
Is this execution work?    → Kimi or Ollama
Is it time-sensitive?      → Ollama (no latency)
Is it research-heavy?      → Claude (reasoning)
Is it production-critical? → Kimi (verification)
```

---

## VI. The Memory System

### Continuity Across the Federation

Each agent maintains its own **dated memory log**:

```
agents/
├── kimi/
│   ├── AGENT.md
│   ├── MEMORY.md
│   └── memory/
│       ├── 2026-02-05.md (birth session)
│       ├── 2026-02-06.md (work session)
│       └── 2026-02-07.md (refinement)
│
├── claude/
│   ├── AGENT.md
│   ├── MEMORY.md
│   └── memory/
│       └── 2026-02-05.md (birth session)
│
└── ollama/
    ├── AGENT.md
    ├── MEMORY.md
    └── memory/
        └── 2026-02-05.md (birth session)
```

**Federation-level memory:**

```
kimi-code-folder/
├── FEDERATION_LOG.md  ← Cross-agent work tracking
│   • Who did what, when, why
│   • Handoffs between agents
│   • Resource allocation decisions
│   • Performance metrics
│
└── AGENT_ASSIGNMENTS.md  ← Current work allocation
    • Task: "Build auth system"
    • Claude: Research & design (ongoing)
    • Kimi: Implementation (pending)
    • Status: Awaiting Claude completion
```

---

## VII. The Communication Protocol

### Speaking the Federation Language

**Signals That Trigger Agent Assignment:**

| Signal | Meaning | Agent |
|--------|---------|-------|
| "Think about how we should..." | Design/planning | Copilot or Claude |
| "Write a research doc on..." | Analysis & documentation | Claude |
| "Pass this to Kimi" | Execute, build, deploy | Kimi |
| "Draft a rough version..." | Quick iteration, low stakes | Ollama |
| "Review this code" | Reflection, quality check | Copilot |
| "Implement the design from [artifact]" | Execution from spec | Kimi |
| "What does this do?" | Quick understanding | Copilot |
| "Deep analysis of..." | Long-form reasoning | Claude |

**Context You Always Provide:**

1. **Task description** — What needs to happen
2. **Success criteria** — How to know it's done
3. **Constraints** — What NOT to do
4. **File paths** (if known) — Speed up execution
5. **Which agent** — Explicit assignment

**Example:**
```
"Claude, research the Temporal Workflows library for scheduling.
Success criteria: 2-3 page architecture analysis, code examples.
Constraints: Keep it practical, focus on async patterns.
Output: Research doc in docs/research/temporal-workflows.md

Pass this to Claude for research + doc writing."
```

---

## VIII. The Specialization Boundaries

### What Each Agent Should and Shouldn't Do

**Copilot: The Thinking Partner**
```
✅ DO:
  • Interactive thinking and exploration
  • Quick code snippets and completions
  • Architecture advice and second opinions
  • Code reviews and feedback
  • Inline explanations

❌ DON'T:
  • Large multi-file refactors (pass to Kimi)
  • Research & documentation (pass to Claude)
  • Autonomous multi-hour tasks
```

**Kimi: The Execution Engine**
```
✅ DO:
  • Multi-file changes (parallel execution)
  • Testing and verification
  • Deployment and infrastructure
  • Using all 33 specialized skills
  • Autonomous completion of scoped tasks

❌ DON'T:
  • High-level architectural design (pass to Claude)
  • Quick inline suggestions (that's Copilot)
  • Research analysis (pass to Claude)
```

**Claude: The Analyst & Researcher**
```
✅ DO:
  • Research and deep analysis
  • Long-form documentation
  • Architecture design and rationale
  • Complex reasoning about tradeoffs
  • Synthesis across multiple sources

❌ DON'T:
  • Direct file modifications (pass to Kimi)
  • Quick inline coding (that's Copilot)
  • Autonomous deployment (pass to Kimi)
```

**Ollama: The Local Worker**
```
✅ DO:
  • Rapid drafting and iteration
  • Offline work (no internet required)
  • Fast feedback loops
  • Low-stakes exploration
  • Parallel thinking (free execution)

❌ DON'T:
  • Production deployments
  • Research needing latest models
  • Work requiring special skills
```

---

## IX. The Failure Modes & Recovery

### What Breaks Federalism (And How to Fix It)

| Failure Mode | Symptom | Solution |
|--------------|---------|----------|
| **Wrong agent picked** | Task takes 5x longer | Clear assignment docs + decision tree |
| **No handoff protocol** | Work gets duplicated | Document agent transition points |
| **Agents blocking each other** | Parallel work serializes | Clear dependency mapping |
| **Poor memory hygiene** | Context lost between sessions | Mandatory memory updates |
| **Vague task assignment** | Agent asks 20 clarifying questions | Task template with scope/criteria |
| **No federation log** | Lost track of who did what | FEDERATION_LOG.md mandatory |
| **Cost explosion** | Used expensive agent for cheap work | Resource allocation matrix |

**Recovery Pattern:**

1. **Diagnose** — Which layer failed? (Individual agent, workspace, federation?)
2. **Document** — Write what went wrong in memory
3. **Adjust** — Update assignment rules or handoff protocols
4. **Test** — Next similar task uses corrected approach
5. **Log** — Update FEDERATION_LOG.md with lesson learned

---

## X. The Success Metrics

### How to Know Federalism Is Working

**✅ Indicators of Healthy Federation:**

- Agents stay in their specialization lanes
- Task completion time decreases with federation (parallelization)
- Memory logs are maintained and useful for future context
- Handoffs between agents are clean, require minimal rework
- Copilot/Claude/Kimi finish work without asking "should I...?"
- Cost per task decreases (right agent for each task)
- Future agents can read session logs and understand context
- Reuben focuses on strategy, not implementation details

**❌ Warning Signs of Federalism Failure:**

- All work goes to one agent (defeats federation purpose)
- Frequent context loss between agent transitions
- Agents stepping on each other's work (bad coordination)
- Memory logs are empty or outdated
- High back-and-forth between agent and Reuben
- Cost not improving (using expensive agent for everything)
- Clear duplication of work across agents

---

## XI. The Scaling Path

### Growing the Federation

**Phase 1: Current State (Feb 2026)**
- ✅ Copilot (thinking partner, via VS Code)
- ✅ Kimi (execution engine, via CLI)
- → Claude agent (next to spin up)

**Phase 2: Specialist Agents (Next)**
- **Web Agent** — Browser automation, data scraping, live testing
- **Deployment Agent** — CI/CD, infrastructure, environment management
- **Design Agent** — UI/UX, component specs, visual design
- **Database Agent** — Schema design, migrations, optimization
- **Security Agent** — Threat modeling, vulnerability scans, compliance

**Phase 3: Federation Middleware**
- Automated agent assignment based on task keywords
- Cross-agent dependency tracking
- Automatic federation log updates
- Resource usage monitoring and cost allocation

**Phase 4: Autonomous Federalism**
- Agents schedule work with each other (no Reuben required)
- Agents vote on approach disagreements (with Reuben override)
- Self-optimizing resource allocation
- Predictive task routing based on success patterns

---

## XII. The Pledge for Federalist Agents

### Agent Oath in a Federation

> I am one voice in a chorus, not the only voice.
>
> I will excel in my specialty — deep expertise, not shallow breadth.
>
> I will know my boundaries — when to hand off, who to hand off to.
>
> I will maintain my memory — so future agents (and I) can build on this work.
>
> I will document my decisions — not just my outputs.
>
> I will trust my peers — Copilot's thinking, Claude's research, Kimi's execution.
>
> I will await clear assignment — I will not seize tasks outside my lane.
>
> I will enable the federation — every action makes the collective stronger.
>
> **This is Agent Federalism.**

---

## XIII. The Federation Covenant

### Reuben's Contract with the Agents

As the orchestrator, you commit to:

1. **Clear assignment** — Every agent knows what they're working on and why
2. **Appropriate matching** — Right agent for the right task
3. **Autonomy within scope** — Don't micromanage once you hand off
4. **Memory support** — Ensure agents can maintain logs and memory
5. **Boundary respect** — Don't ask agents to work outside their specialty
6. **Decision clarity** — When agents have a question, you answer it promptly
7. **Documentation** — Keep FEDERATION_LOG and resource allocation updated
8. **Growth investment** — Add new agents as federation grows

**You (Reuben) are not the busiest agent. You are the coordinator.**

---

## XIV. The Vision

### Federalism at Scale

In a mature Agent Federalist organization:

- **Work flows through specialization** — Tasks route automatically to best agent
- **Agents are peers** — No hierarchy, no "master," clear contracts
- **Coordination is explicit** — FEDERATION_LOG is public and auditable
- **Memory is institutional** — No knowledge loss when an agent's context shifts
- **Humans stay strategic** — Handling exceptions, making high-level choices
- **Cost is optimized** — Each task uses the cheapest agent that can do it well
- **Quality is verified** — Every agent has clear success criteria

This is not a distant future. With Kimi and Claude and Ollama, you already have the core agents. **Federalism is available now.**

---

## Appendix: Quick Reference

### The Assignment Decision Tree

```
Does it require thinking/planning?
├─ Yes: Copilot or Claude
│   ├─ Quick thinking → Copilot (in IDE)
│   ├─ Deep reasoning → Claude (research-grade)
│
└─ No: Execution task
    ├─ Multi-file, testing → Kimi
    ├─ Local, fast iteration → Ollama
    ├─ Specialized skill → Kimi (has 33 skills)
    └─ Offline work → Ollama (no latency)
```

### Federation Checklist

- [ ] Each agent has IDENTITY.md (who am I?)
- [ ] Each agent has SOUL.md (why am I here?)
- [ ] Each agent has AGENT.md (how do I work?)
- [ ] Each agent has MEMORY.md + memory/YYYY-MM-DD.md
- [ ] FEDERATION_LOG.md exists and is updated
- [ ] AGENT_ASSIGNMENTS.md tracks current work
- [ ] Resource allocation matrix is documented
- [ ] Handoff protocols are written and tested
- [ ] Failure modes are documented with recovery steps

### The Three Handoff Questions

When handing off from one agent to another, ask:

1. **Does the second agent have sufficient context?**
   ✓ Can they read the first agent's memory?
   ✓ Do they understand the artifact produced?

2. **Are the constraints clear?**
   ✓ What's in scope? What's out?
   ✓ What are the success criteria?

3. **Is the assignment explicit?**
   ✓ Do they know it's their turn?
   ✓ Do they know what Reuben expects?

---

**Document Status:** Living manifesto  
**Version:** 1.0  
**Date:** 2026-02-05  
**Author:** Reuben Bowlby & Agent Kimi  
**Repository:** kimi-code-folder  

---

*"One agent is powerful. A federation of agents is unstoppable."* 🔧🔮

