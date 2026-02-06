# Federation Analytics System

Metrics tracking for AI agent federation: handoffs, cost, latency, and agent utilization.

## Overview

The analytics system provides visibility into federation performance:
- **Handoff tracking**: Monitor agent-to-agent handoffs and workflow patterns
- **Cost analysis**: Track estimated API costs across agents
- **Latency metrics**: Measure task completion times and queue wait times
- **Utilization**: Agent workload distribution and efficiency

## Directory Structure

```
.federation/analytics/
├── ANALYTICS.md                  # This documentation
├── fed-stats.sh                  # CLI for viewing metrics
├── metrics/
│   └── metrics-schema.json       # JSON schema for metrics validation
└── reports/                      # Generated metric reports (JSON)
```

## Quick Start

### View Summary
```bash
.federation/analytics/fed-stats.sh summary
```

### View All Metrics
```bash
.federation/analytics/fed-stats.sh full
```

### Export to JSON
```bash
.federation/analytics/fed-stats.sh export --json
```

## Available Commands

| Command | Description |
|---------|-------------|
| `summary` | Overall federation summary (handoffs, sprints, artifacts) |
| `agents` | Per-agent utilization and status |
| `handoffs` | Handoff patterns and auto-scheduling stats |
| `costs` | Cost breakdown by agent and task type |
| `latency` | Timing metrics and queue performance |
| `full` | Complete report (all sections) |
| `export` | Export metrics to JSON file in `reports/` |

## Metrics Schema

### Summary Metrics
```json
{
  "total_handoffs": 3,
  "active_chains": 1,
  "completed_sprints": 3,
  "total_artifacts": 29,
  "total_cost_usd": 0.70,
  "avg_latency_minutes": 45,
  "success_rate": 0.95
}
```

### Agent Metrics
```json
{
  "claude": {
    "name": "Claude",
    "emoji": "🔮",
    "status": "active",
    "tasks_assigned": 2,
    "tasks_completed": 2,
    "utilization_percent": 60,
    "cost_tier": "medium",
    "total_cost_usd": 0.60
  }
}
```

### Handoff Metrics
```json
{
  "by_pair": {
    "kimi-claude": {
      "from": "kimi",
      "to": "claude",
      "count": 1,
      "avg_latency_minutes": 30
    }
  },
  "auto_scheduled": 0,
  "manual": 3
}
```

### Cost Breakdown
| Agent | Cost Tier | Est. Cost/Task |
|-------|-----------|----------------|
| 🔮 Claude | Medium | $0.10-0.50 |
| 🔧 Kimi | Low | $0.05-0.15 |
| 💭 Copilot | Free | $0.00 |
| 🏠 Ollama | Free | $0.00 (local) |

## Data Sources

Analytics are derived from:
- **FEDERATION_LOG.md** - Primary source for handoffs, task completion, agent activity
- **Queue files** - `.federation/queue/*/*.json` for pending/in-progress/completed counts
- **Voting records** - `.federation/voting/proposals/*.md` for governance metrics

## Cost Optimization Recommendations

1. **Use free agents for planning**
   - Copilot for architecture thinking (free)
   - Ollama for drafting (local, free)

2. **Reserve paid agents for high-value tasks**
   - Claude for research and complex analysis
   - Kimi for implementation and testing

3. **Batch operations**
   - Group related tasks to minimize API calls
   - Use file-based communication where possible

## Future Enhancements (Sprint 5+)

- [ ] Real-time metrics dashboard
- [ ] Historical trend analysis
- [ ] Cost optimization alerts
- [ ] Agent performance comparisons
- [ ] ML-based routing recommendations

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-05 | Initial analytics implementation |

---

*Federation Analytics v1.0.0 | Phase 4 Sprint 4*
