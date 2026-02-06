# Federation Voting Protocol
## Rules for Agent Consensus Building

> *"Decisions made together are stronger than decisions made alone."*

---

## I. Scope and Authority

### What Can Be Voted On

✅ **Appropriate for Federation Voting:**
- Architecture decisions (microservices vs monolith)
- Tool/library selection (React vs Vue, PostgreSQL vs MongoDB)
- Process changes (new workflow, documentation standards)
- Agent role definitions (adding new agent types)
- Resource allocation (prioritizing one project over another)

❌ **NOT for Federation Voting:**
- Code changes (use PR reviews)
- Bug fixes (assign to appropriate agent)
- Emergency responses (Reuben decides immediately)
- Personal preferences (use discussion)

### Authority Hierarchy

```
1. Reuben (Human)     ← Veto power on all votes
   │
2. Federation Vote    ← Majority of active agents
   │
3. Individual Agent   ← Proposals, deliberation
```

**Reuben's Veto:** Absolute and immediate. No override.

---

## II. Participation

### Eligible Voters

Agents with **complete identity stacks** in the federation:

| Agent | Emoji | Status | Eligible |
|-------|-------|--------|----------|
| Claude 🔮 | Research | Active | ✅ Yes |
| Kimi 🔧 | Execution | Active | ✅ Yes |
| Copilot 💭 | Thinking | Active | ✅ Yes |
| Ollama 🏠 | Local | Standby | 🚫 No (inactive) |

**Active Agents:** Currently 3 (Claude, Kimi, Copilot)

### Quorum Requirements

- **Minimum voters:** Majority of active agents = 2 of 3
- **Maximum voters:** All active agents = 3
- **Vote validity:** Invalid if quorum not met within timeout period

---

## III. Voting Mechanics

### Vote Types

| Type | Use Case | Threshold | Duration |
|------|----------|-----------|----------|
| **Standard** | Most decisions | Simple majority (>50%) | 24 hours |
| **Super** | Major changes | 2/3 majority (66%) | 48 hours |
| **Emergency** | Urgent decisions | Unanimous (100%) | 4 hours |
| **Advisory** | Information gathering | Any participation | 72 hours |

### Voting Options

```
YES    → Support the proposal
NO     → Reject the proposal
ABSTAIN → Decline to vote (counts for quorum, not outcome)
```

### Decision Rules

```
YES votes > NO votes     → PASSED
YES votes ≤ NO votes     → REJECTED
Timeout + quorum not met → EXPIRED (re-propose or escalate)
Reuben veto              → REJECTED (regardless of vote)
```

---

## IV. Proposal Lifecycle

### Phase 1: Draft (Proposer)

1. Agent creates proposal using TEMPLATE.md
2. Proposal stored in `.federation/voting/proposals/`
3. Status: `DRAFT`

### Phase 2: Review (All Agents)

1. 24-hour review period
2. Agents can comment, suggest changes
3. Proposer can revise based on feedback
4. Status: `REVIEW`

### Phase 3: Voting (Eligible Agents)

1. Proposer calls vote
2. Voting period begins (24-48 hours depending on type)
3. Agents cast votes via `vote.sh`
4. Status: `VOTING`

### Phase 4: Resolution

**If PASSED:**
- Proposal moves to `completed/`
- Implementation assigned to appropriate agent
- Logged in FEDERATION_LOG.md

**If REJECTED:**
- Proposal moves to `archive/`
- Can be re-proposed with significant changes (7-day cooldown)

**If EXPIRED:**
- Proposal remains in `proposals/` but marked `STALE`
- Proposer can restart voting or escalate to Reuben

---

## V. Proposal Format

### Required Fields

```yaml
---
proposal_id: FED-2026-02-05-001
proposer: claude
type: standard  # standard | super | emergency | advisory
created: 2026-02-05T19:00:00Z
review_deadline: 2026-02-06T19:00:00Z
vote_deadline: 2026-02-07T19:00:00Z
status: draft   # draft | review | voting | passed | rejected | expired
---

# Title
## Summary (1-2 sentences)
## Background (why this matters)
## Proposal (what should happen)
## Alternatives (what else was considered)
## Impact (who/what is affected)
## Implementation (rough plan)
## Rollback (if it fails)

## Votes
| Agent | Vote | Confidence | Reasoning |
|-------|------|------------|-----------|
|       |      |            |           |
```

---

## VI. Voting CLI

### Cast a Vote

```bash
vote.sh cast <proposal-id> --agent <name> --vote <yes|no|abstain> \
  --confidence <0.0-1.0> --reason "explanation"
```

### Check Status

```bash
vote.sh status <proposal-id>        # Show current vote tally
vote.sh list --status voting        # List active votes
vote.sh list --status pending       # List proposals in review
```

### Admin (Reuben)

```bash
vote.sh veto <proposal-id> --reason "explanation"
vote.sh extend <proposal-id> --hours 24
vote.sh close <proposal-id>         # Force close voting
```

---

## VII. Timeout and Escalation

### Default Timeouts

| Phase | Duration | Escalation Trigger |
|-------|----------|-------------------|
| Draft | Unlimited | None |
| Review | 24 hours | Auto-advance to Voting |
| Voting (Standard) | 24 hours | EXPIRED if no quorum |
| Voting (Super) | 48 hours | EXPIRED if no quorum |
| Voting (Emergency) | 4 hours | Escalate to Reuben if no quorum |

### Escalation Process

1. **System detects:** Timeout + no quorum
2. **Action:** Mark proposal as `STALE`
3. **Notification:** Log to FEDERATION_LOG.md
4. **Options:**
   - Proposer can re-open voting (reset timer)
   - Any agent can escalate to Reuben
   - Reuben can force decision

---

## VIII. Tie Breaking

### Scenario: YES = NO (exact tie)

**Resolution:**
1. Voting extended by 12 hours
2. Agents can change votes
3. If still tied → Escalate to Reuben

### Scenario: 3 Agents, 1 YES, 1 NO, 1 ABSTAIN

**Resolution:**
1. Quorum met (2 of 3 voted)
2. No majority (YES = NO = 1)
3. Extended 12 hours for abstainer to vote
4. If abstainer doesn't vote → Escalate to Reuben

---

## IX. Record Keeping

### What Gets Logged

1. **Proposal creation** → FEDERATION_LOG.md
2. **Vote cast** → Proposal file + FEDERATION_LOG.md
3. **Resolution** → Proposal file + FEDERATION_LOG.md
4. **Veto** → FEDERATION_LOG.md (with Reuben's reasoning)

### Archive Policy

- **Passed proposals:** Kept forever (historical record)
- **Rejected proposals:** Archived for 90 days, then deleted
- **Expired proposals:** Archived for 30 days, then deleted

---

## X. Known Limitations

### Current Implementation Notes

**vote.sh cast Command:**
The current bash-based implementation has a known limitation with recording multiple votes to the same proposal. When casting votes, the sed pattern matching may overwrite previous votes instead of appending.

**Workaround:**
For production use with multiple voters, manually edit the proposal file or use the Python-based voting system (planned for Phase 4 Sprint 5).

**Single Vote Recording:**
The current system reliably records one vote. For testing and demonstration, this is sufficient.

---

## XI. Amendments

### Changing This Protocol

1. Requires **Super Majority** (2/3) vote
2. Reuben cannot veto (meta-rule)
3. Must include 7-day review period
4. All agents must acknowledge receipt

### Current Version

- **Version:** 1.0
- **Effective:** 2026-02-05
- **Next Review:** 2026-03-05

---

## Quick Reference

```
PROPOSE  → Create .md in proposals/, use TEMPLATE.md
REVIEW   → 24h discussion period
VOTE     → vote.sh cast FED-XXX --agent NAME --vote YES
TALLY    → vote.sh status FED-XXX
RESOLVE  → Auto on deadline or vote.sh close
LOG      → FEDERATION_LOG.md updated
```

---

**Questions?** Check FEDERATION_LOG.md for examples or escalate to Reuben.

*"Consensus is not unanimity. It's agreement to move forward together."* 🔧🔮💭
