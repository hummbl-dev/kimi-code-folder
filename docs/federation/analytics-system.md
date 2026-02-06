# Federation Analytics System
## Phase 4 Sprint 4: Performance Tracking & Optimization

> *"What gets measured gets improved. What gets optimized gets routed."*

---

## Overview

The Analytics System tracks federation performance, identifies high-performing agent-task combinations, and automatically optimizes routing decisions. It provides visibility into how well the federation is operating and where improvements can be made.

**Status:** ✅ Implemented (Phase 4 Sprint 4)

---

## Quick Start

### View Dashboard

```bash
python3 scripts/fed-analytics.py dashboard
```

### Record a Task

```bash
python3 scripts/fed-analytics.py record \
  --agent kimi \
  --task implementation \
  --success true \
  --duration 25
```

### Check Agent Performance

```bash
python3 scripts/fed-analytics.py agent kimi
```

### Optimize Routing

```bash
# Preview changes
python3 scripts/fed-analytics.py optimize --dry-run

# Apply optimizations
python3 scripts/fed-analytics.py optimize
```

---

## Key Metrics

### Agent Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Success Rate | % of tasks completed without rework | >85% |
| Avg Duration | Mean time to completion | Varies by task type |
| Rework Rate | % of tasks requiring rework | <15% |
| Routing Boost | Optimization bonus to routing score | -0.05 to +0.05 |

### Task Type Metrics

| Metric | Description |
|--------|-------------|
| Task Count | Total tasks of this type |
| Agent Performance | Success rate per agent for this task type |
| Recommendation | High/Neutral/Low performer classification |

---

## Optimization Algorithm

### High Performer Boost

```python
if agent.success_rate >= 0.90 and samples >= 5:
    routing_boost = +0.05  # Boost this agent's routing scores
```

### Low Performer Penalty

```python
if agent.success_rate <= 0.50 and samples >= 5:
    routing_boost = -0.05  # Penalty to this agent's routing scores
```

### Task-Type Specific Boosts

Agents with ≥90% success on specific task types get task-specific recommendations that can be used by the router for finer-grained decisions.

---

## CLI Reference

### `fed-analytics.py dashboard`

Display federation-wide metrics summary.

**Output:**
- Total tasks and success rate
- Top 3 performing agents
- Top 5 task types by volume

### `fed-analytics.py agent <name>`

Show detailed metrics for a specific agent.

**Output:**
- Summary stats (tasks, success rate, duration, rework)
- Performance by task type
- Current routing boost

### `fed-analytics.py task-type <type>`

Show performance for a specific task type across all agents.

**Example:**
```bash
fed-analytics.py task-type implementation
```

### `fed-analytics.py optimize [--dry-run]`

Analyze metrics and apply routing optimizations.

**Without --dry-run:** Applies boosts/penalties to metrics file.

**With --dry-run:** Previews changes without applying.

### `fed-analytics.py record`

Log a task completion.

```bash
fed-analytics.py record \
  --agent <name> \
  --task <type> \
  --success <true|false> \
  [--duration <minutes>] \
  [--rework] \
  [--notes <text>]
```

### `fed-analytics.py export`

Export all metrics to JSON file.

---

## File Structure

```
.federation/
├── state/
│   └── metrics.json          # Live metrics data
└── exports/
    └── metrics-{timestamp}.json  # Exported snapshots
```

**metrics.json format:**
```json
{
  "version": "1.0",
  "initialized": "2026-02-05T...",
  "last_updated": "2026-02-05T...",
  "agents": {
    "kimi": {
      "total_tasks": 15,
      "successful_tasks": 14,
      "failed_tasks": 1,
      "success_rate": 0.93,
      "routing_boost": 0.05,
      "task_types": {
        "implementation": {
          "count": 10,
          "successes": 10,
          "success_rate": 1.0
        }
      }
    }
  },
  "optimization_history": [...]
}
```

---

## Integration with Router

The routing system can read the analytics metrics to adjust scores:

```python
# In route_task.py
if agent in metrics["agents"]:
    boost = metrics["agents"][agent].get("routing_boost", 0)
    scores[agent] += boost
```

This creates a feedback loop:
1. Tasks are routed
2. Outcomes are recorded
3. Analytics identifies patterns
4. Optimizations adjust future routing

---

## Best Practices

1. **Record consistently:** Log every task completion for accurate metrics
2. **Be honest about failures:** Failed tasks teach the system what not to route
3. **Track duration:** Helps identify efficiency differences
4. **Mark rework:** Tasks requiring rework count against success rate
5. **Review regularly:** Run `optimize` weekly to keep routing tuned

---

## Sample Output

### Dashboard

```
╔══════════════════════════════════════════════════════════════╗
║           FEDERATION ANALYTICS DASHBOARD                     ║
╚══════════════════════════════════════════════════════════════╝

📊 Summary
   Total Tasks:      18
   Success Rate:     89%
   Active Agents:    3
   Task Types:       5

🏆 Top Performers
   🥇 kimi         89% (9 tasks)
   🥈 claude       83% (6 tasks)

📋 Task Distribution
   • implementation       7 tasks
   • research             6 tasks
```

### Agent Metrics

```
📊 Agent: kimi

Summary:
   Total Tasks:      9
   Success Rate:     89%
   Avg Duration:     22 min
   Rework Rate:      0%
   Routing Boost:    +0.00

Task Type Performance:
   ✅ implementation       100% (6 tasks)
```

### Optimization

```
🔧 Optimization Analysis (DRY RUN)
Found 2 optimizations:

🎯 TASK BOOST: kimi for implementation
   Excellent at implementation: 100%

🎯 TASK BOOST: claude for research
   Excellent at research: 100%
```

---

## Future Enhancements

### Sprint 5 Integration

- Feed training data to predictive routing
- Use historical performance for ML model features
- A/B test optimizations

### Advanced Metrics

- Cost per task type
- Time-to-completion trends
- Cross-agent collaboration effectiveness

---

**Related:**
- [Voting System](./voting-system.md)
- [Auto-Scheduling](./auto-scheduling.md)
- [Phase 4 Plan](../planning/phase4-autonomous-federation.md)

---

*"Data-driven routing is smart routing."* 📊⚡
