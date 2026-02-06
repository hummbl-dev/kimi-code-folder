# Predictive Routing System

ML-enhanced task routing using TF-IDF vectorization and cosine similarity.

## Overview

The predictive routing system uses machine learning to intelligently match tasks to agents based on:

1. **TF-IDF Vectorization** - Extract features from task descriptions
2. **Cosine Similarity** - Match tasks to agent capability profiles
3. **Historical Learning** - Learn from past task completions
4. **Confidence Calibration** - Combine multiple signals for final routing decision

## Components

### Feature Extractor (`feature_extractor.py`)

- Tokenizes and normalizes task descriptions
- Removes stop words
- Extracts n-grams (unigrams, bigrams, trigrams)
- Computes TF-IDF vectors
- Estimates task complexity
- Identifies task domains

### Similarity Engine (`similarity_engine.py`)

- Maintains agent capability profiles
- Computes cosine similarity between tasks and agents
- Ranks agents by match confidence
- Generates routing explanations

### Historical Learner (`historical_learner.py`)

- Scans completed tasks from queue
- Updates agent profiles based on success/failure
- Tracks performance metrics
- Enables continuous improvement

### ML Router (`scripts/route_task_ml.py`)

- Main CLI interface for predictive routing
- Combines keyword-based and ML-based routing
- Provides detailed explanations
- JSON output support

## Usage

### Basic Routing

```bash
python scripts/route_task_ml.py "Implement user authentication API"
```

Output:
```
Task: Implement user authentication API
Recommended Agent: kimi
Confidence: 87%
Method: ml_similarity
Auto-assign: Yes

Explanation: 🔧 Kimi (Execution); Strong semantic similarity (85%); Domain alignment (implementation)
```

### Detailed Explanation

```bash
python scripts/route_task_ml.py "Research middleware patterns" --explain
```

### JSON Output

```bash
python scripts/route_task_ml.py "Design database schema" --explain --json
```

### Router Statistics

```bash
python scripts/route_task_ml.py --stats
```

### Disable ML (Keyword Fallback)

```bash
python scripts/route_task_ml.py "Test the API" --no-ml
```

## API Usage

```python
from scripts.route_task_ml import MLRouter

router = MLRouter(use_ml=True)

result = router.route_task(
    description="Implement OAuth2 authentication flow",
    task_type="implementation",
    explain=True
)

print(result["recommended_agent"])  # "kimi"
print(result["confidence"])         # 0.87
```

## Scoring Algorithm

The final confidence score is computed as:

```
confidence = (
    similarity_score * 0.4 +      # Semantic similarity
    domain_match * 0.3 +          # Domain alignment
    keyword_match * 0.2 +         # Keyword overlap
    historical_bias * 0.1         # Past performance
)
```

## Thresholds

| Threshold | Value | Action |
|-----------|-------|--------|
| Auto-assign | ≥0.75 | Automatically assign task |
| Clarification | 0.60-0.74 | Suggest agent, seek confirmation |
| Manual | <0.60 | Manual assignment required |

## Data Files

Data is stored in `.federation/predictor/data/`:

- `agent_profiles.json` - Agent capability profiles
- `idf_cache.json` - IDF values for terms
- `learning_log.json` - Historical learning events

## Agent Profiles

Initial profiles are defined with:

| Agent | Specialty | Base Success Rate | Domains |
|-------|-----------|-------------------|---------|
| 🔮 Claude | Research & Analysis | 92% | research, design, documentation |
| 🔧 Kimi | Execution | 94% | implementation, testing, deployment |
| 💭 Copilot | Thinking & Planning | 88% | planning, review |
| 🏠 Ollama | Local Drafting | 75% | drafting, prototyping |

## Learning

The system learns from completed tasks:

1. Scans `.federation/queue/completed/` for finished tasks
2. Updates agent success rates
3. Reinforces capability vectors
4. Tracks average task duration

To trigger learning:

```python
from .federation.predictor.historical_learner import HistoricalLearner

learner = HistoricalLearner()
result = learner.learn_from_all_completed()
print(f"Learned from {result['learned']} tasks")
```

## Testing

Run the predictor modules directly:

```bash
# Test feature extraction
python .federation/predictor/feature_extractor.py

# Test similarity matching
python .federation/predictor/similarity_engine.py

# Test learning
python .federation/predictor/historical_learner.py
```

## Future Enhancements

- [ ] Deep learning models for complex tasks
- [ ] Multi-agent task decomposition
- [ ] Real-time performance monitoring
- [ ] A/B testing framework for routing strategies

---

*Predictive Routing v1.0.0 | Phase 4 Sprint 5*
