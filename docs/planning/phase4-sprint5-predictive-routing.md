# Phase 4 Sprint 5: Predictive Routing

## Overview

Implement ML-enhanced task routing using TF-IDF vectorization and cosine similarity to intelligently match tasks to agents based on historical performance and task characteristics.

## Goals

1. **Intelligent Task Matching**: Use NLP/TF-IDF to extract task features and match to agent specialties
2. **Historical Learning**: Learn from past task completions to improve routing accuracy
3. **Confidence Calibration**: Adjust confidence scores based on historical success rates
4. **Performance Prediction**: Predict task completion time and success probability per agent

## Architecture

```
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   Task Input    │────▶│  Feature Extraction │────▶│  TF-IDF Vector  │
│  (description)  │     │  (tokenization)     │     │  (sparse)       │
└─────────────────┘     └─────────────────────┘     └────────┬────────┘
                                                             │
                              ┌──────────────────────────────┘
                              ▼
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  Agent Profile  │────▶│  Similarity Match   │────▶│  Ranked Agents  │
│  (historical)   │     │  (cosine sim)       │     │  (w/ scores)    │
└─────────────────┘     └─────────────────────┘     └────────┬────────┘
                                                             │
                              ┌──────────────────────────────┘
                              ▼
                       ┌─────────────────────┐
                       │  Confidence Fusion  │
                       │  (keyword + ML)     │
                       └────────┬────────────┘
                                │
                                ▼
                       ┌─────────────────────┐
                       │   Agent Assignment  │
                       │   (auto/manual)     │
                       └─────────────────────┘
```

## Components

### 1. Feature Extractor (`predictor/feature_extractor.py`)

- Tokenizes task descriptions
- Extracts keywords and n-grams
- Removes stop words
- Creates TF-IDF vectors

### 2. Similarity Engine (`predictor/similarity_engine.py`)

- Calculates cosine similarity between task and agent profiles
- Maintains agent capability vectors
- Computes match scores

### 3. Historical Learner (`predictor/historical_learner.py`)

- Reads completed tasks from queue/completed/
- Updates agent performance metrics
- Adjusts capability vectors based on success/failure

### 4. Confidence Calibrator (`predictor/calibrator.py`)

- Maps similarity scores to confidence (0-1)
- Factors in historical accuracy
- Applies agent-specific bias corrections

### 5. Predictive Router (`scripts/route_task_ml.py`)

- Main entry point for ML-enhanced routing
- Combines keyword-based and ML-based scores
- Provides explanation for routing decisions

## Scoring Algorithm

```python
# Combined confidence score
final_confidence = (
    keyword_confidence * 0.4 +      # From existing routing
    similarity_score * 0.4 +         # From TF-IDF matching
    historical_bias * 0.2            # From past performance
)
```

## Data Structures

### Agent Profile
```json
{
  "agent_id": "claude",
  "capability_vector": {"research": 0.95, "architecture": 0.90, ...},
  "task_history": ["task-001", "task-002", ...],
  "success_rate": 0.92,
  "avg_duration": 45.5,
  "specialty_keywords": ["research", "analysis", "documentation"],
  "last_updated": "2026-02-06T01:00:00Z"
}
```

### Task Features
```json
{
  "task_id": "task-123",
  "tfidf_vector": {"implement": 0.8, "function": 0.6, ...},
  "complexity_score": 0.7,
  "domain": "implementation",
  "estimated_tokens": 1500
}
```

## Implementation Plan

### Phase 5.1: Core ML Infrastructure
- [ ] Feature extraction module
- [ ] TF-IDF vectorization
- [ ] Similarity calculation
- [ ] Basic routing integration

### Phase 5.2: Historical Learning
- [ ] Task completion tracking
- [ ] Agent profile updates
- [ ] Performance metrics calculation
- [ ] Feedback loop implementation

### Phase 5.3: Confidence Calibration
- [ ] Similarity-to-confidence mapping
- [ ] Historical accuracy integration
- [ ] Agent bias correction
- [ ] Threshold tuning

### Phase 5.4: Integration & Testing
- [ ] Route task ML wrapper
- [ ] Fallback to keyword routing
- [ ] Explanation generation
- [ ] Unit tests (target: 10+ tests)

## API Design

```python
# Predictive routing
from scripts.route_task_ml import route_task_ml

result = route_task_ml(
    task_description="Implement user authentication with JWT tokens",
    use_ml=True,
    explain=True
)

# Returns:
{
    "recommended_agent": "kimi",
    "confidence": 0.87,
    "explanation": {
        "keyword_match": 0.85,
        "similarity_score": 0.88,
        "historical_bias": 0.89,
        "reasoning": "High similarity to past implementation tasks. "
                     "Keyword 'implement' matches Kimi's specialty. "
                     "Historical success rate: 94%"
    },
    "alternatives": [
        {"agent": "copilot", "confidence": 0.62},
        {"agent": "claude", "confidence": 0.45}
    ]
}
```

## Success Criteria

1. **Accuracy**: ML routing matches manual assignment > 80% of the time
2. **Confidence**: Average confidence > 0.75 for auto-assigned tasks
3. **Learning**: System improves accuracy by > 10% after 20 tasks
4. **Performance**: Routing decision < 100ms
5. **Fallback**: Graceful degradation to keyword routing if ML fails

## Future Enhancements (Post-Sprint)

- Deep learning models for complex task understanding
- Multi-agent task decomposition
- Predictive queue scheduling based on agent availability
- Anomaly detection for routing failures

---

*Sprint 5: Predictive Routing | Phase 4 Autonomous Federation*
