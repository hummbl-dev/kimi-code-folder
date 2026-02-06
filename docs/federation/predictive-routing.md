# Predictive Routing System
## Phase 4 Sprint 5: ML-Enhanced Task Routing

> *"From explicit rules to learned patterns. The federation gets smarter with every task."*

---

## Overview

The Predictive Routing System (v2) combines the explicit rule-based routing of v1 with TF-IDF similarity matching learned from historical task assignments. This hybrid approach maintains transparency while improving accuracy as the federation processes more tasks.

**Status:** ✅ Implemented (Phase 4 Sprint 5)

---

## How It Works

### Hybrid Scoring Formula

```
final_score = (RULE_WEIGHT × rule_score) + (ML_WEIGHT × ml_score × ml_confidence)

Where:
- RULE_WEIGHT = 0.6 (60%)
- ML_WEIGHT = 0.4 (40%)
- ml_confidence = min(1.0, training_samples / 100)
```

### Evolution of ML Confidence

| Training Samples | ML Confidence | Method |
|------------------|---------------|--------|
| 0-9 | 0% | Rule-only |
| 10-49 | 10-49% | Rule-primary, ML-assist |
| 50-99 | 50-99% | **Hybrid** |
| 100+ | 100% | Full hybrid |

---

## Quick Start

### Route a Task (v2)

```bash
# Simple output
python3 scripts/route_task_v2.py "Research authentication patterns"
# → 📚 claude (0.84) [hybrid]

# Detailed breakdown
python3 scripts/route_task_v2.py "Build user dashboard" --explain

# JSON output
python3 scripts/route_task_v2.py "Deploy to production" --json
```

### Compare v1 vs v2

```bash
python3 scripts/route_task_v2.py "Implement caching layer" --compare
```

### Record Training Data

```bash
python3 scripts/route_task_v2.py --train \
  --train-task "Research OAuth2" \
  --agent claude \
  --success true \
  --duration 35
```

---

## Algorithm Details

### TF-IDF Similarity

The system uses a lightweight TF-IDF implementation for semantic similarity:

1. **Tokenization:** Tasks are broken into words (stop words removed)
2. **Term Frequency:** How often each word appears in the task
3. **Inverse Document Frequency:** Rarity of words across all tasks
4. **Cosine Similarity:** Compare new task to historical tasks

### Training Data Format

```jsonl
{"timestamp": "2026-02-05T...", "task": "Research OAuth2", "agent": "claude", "success": true, "duration": 35}
{"timestamp": "2026-02-05T...", "task": "Implement auth", "agent": "kimi", "success": true, "duration": 25}
```

Stored in: `.federation/state/routing-history.jsonl`

---

## CLI Reference

### `route_task_v2.py <task>`

Route a task using hybrid algorithm.

**Output:** `emoji agent (confidence) [method]`

Examples:
```
📚 claude (0.84) [hybrid]
🔧 kimi (0.77) [rule]
```

### `route_task_v2.py --explain <task>`

Show detailed scoring breakdown.

```
Task: Research distributed databases

🎯 Routing Decision
   Agent:      📚 claude
   Confidence: 0.84
   Method:     hybrid

📊 Score Breakdown
   Rule component: 0.95
   ML component:   1.0
   ML confidence:  0.6 (samples: 60)
```

### `route_task_v2.py --compare <task>`

Compare v1 and v2 routing side-by-side.

```
📊 A/B Comparison: v1 vs v2
Task: Implement caching layer

v1 (Rules):     kimi (0.95)
v2 (Hybrid):    kimi (0.84)
Method:         hybrid

✅ Both routers agree
Confidence delta: -0.11
```

### `route_task_v2.py --train`

Record a training example.

**Required flags:**
- `--train-task "..."` — Task description
- `--agent <name>` — Assigned agent
- `--success true|false` — Outcome

**Optional:**
- `--duration <minutes>` — Time taken
- `--notes "..."` — Additional notes

---

## File Structure

```
.federation/state/
├── routing-history.jsonl      # Training data (one record per line)
└── routing-v2-config.json     # v2 configuration (weights, thresholds)

scripts/
├── route_task.py              # v1: Rule-based router
└── route_task_v2.py           # v2: Hybrid router (this system)
```

---

## A/B Testing

### Manual Comparison

```bash
# Test a batch of tasks
for task in "Research X" "Implement Y" "Plan Z"; do
    echo "=== $task ==="
    python3 scripts/route_task_v2.py "$task" --compare
    echo ""
done
```

### Accuracy Measurement

To measure routing accuracy:

1. Run both routers on test set
2. Compare predictions to actual outcomes
3. Track metrics:
   - Agreement rate (v1 vs v2)
   - Success rate by router
   - Confidence calibration

---

## Migration Path

### From v1 to v2

1. **Parallel operation:** Run both routers, log differences
2. **Training phase:** Record 50+ tasks to build ML confidence
3. **Validation:** Compare accuracy on held-out test set
4. **Switchover:** Update scripts to use v2 as default

### Backwards Compatibility

v2 maintains full compatibility with v1:
- Same emoji output format
- Same confidence thresholds
- Falls back to rules when ML confidence is low

---

## Best Practices

### Recording Training Data

1. **Be consistent:** Record every task, not just successes
2. **Include failures:** Failed tasks teach what NOT to route
3. **Add context:** Use notes for unusual cases
4. **Track duration:** Helps identify efficiency patterns

### When to Use v2

| Scenario | Recommendation |
|----------|----------------|
| New federation (< 50 tasks) | Stick with v1 |
| Established (50+ tasks) | Use v2 for hybrid benefits |
| Research-heavy tasks | v2 excels at semantic matching |
| Edge cases | v1 rules more predictable |

---

## Performance Characteristics

| Metric | v1 (Rules) | v2 (Hybrid) |
|--------|------------|-------------|
| Cold start | ✅ Immediate | ⚠️ Needs 10+ samples |
| Accuracy (mature) | ~85% | Target: >90% |
| Transparency | ✅ Fully explainable | ⚠️ ML component is "gray box" |
| Adaptability | ❌ Static | ✅ Learns from data |
| Speed | ✅ Fast | ⚠️ Slightly slower (TF-IDF calc) |

---

## Example Session

```bash
# Check current training samples
$ python3 scripts/route_task_v2.py "test" --explain | grep "samples"
# → ML confidence:  0.6 (samples: 60)

# Route a task
$ python3 scripts/route_task_v2.py "Research blockchain integration"
📚 claude (0.84) [hybrid]

# See the breakdown
$ python3 scripts/route_task_v2.py "Research blockchain" --explain
Task: Research blockchain
🎯 Routing Decision
   Agent:      📚 claude
   Confidence: 0.84
   Method:     hybrid
📊 Score Breakdown
   Rule component: 0.95  # "research" keyword = 0.95
   ML component:   1.0   # TF-IDF similarity to research tasks
   ML confidence:  0.6   # 60 samples / 100

# Record outcome for continuous learning
$ python3 scripts/route_task_v2.py --train \
  --train-task "Research blockchain" \
  --agent claude \
  --success true \
  --duration 45
✅ Recorded training example (sample #61)
```

---

## Future Enhancements

### Beyond TF-IDF

- **Word embeddings:** Use pre-trained vectors (Word2Vec, GloVe)
- **Neural classification:** Small neural network on top of embeddings
- **Agent feedback loop:** Use success rates to weight training examples

### Integration

- **Analytics system:** Feed routing outcomes into `fed-analytics.py`
- **Auto-scheduling:** Use v2 for auto-queue agent selection
- **Voting system:** ML recommendations as "votes"

---

**Related:**
- [Analytics System](./analytics-system.md) — Track routing outcomes
- [Voting System](./voting-system.md) — Agent decision making
- [Phase 4 Plan](../planning/phase4-autonomous-federation.md)

---

*"Every task teaches the federation. Every routing decision makes the next one smarter."* 🧠⚡
