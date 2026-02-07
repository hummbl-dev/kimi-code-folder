# Routing Optimization Plan
## From 60% to >90% Accuracy — Full Session

**Date:** Scheduled  
**Duration:** 4-6 hours (full session)  
**Owner:** Kimi 🔧 (Execution Lead)  
**Support:** Claude 📚 (Analysis & Strategy)  
**Goal:** Achieve >90% routing accuracy

---

## Current State

| Metric | Value | Target |
|--------|-------|--------|
| Accuracy | 60% | >90% |
| Training Samples | 243 | 500+ |
| Class Imbalance | kimi:103, copilot:26 (4:1) | 2:1 max |
| Data Quality | ✅ Cleaned (no 'codex') | — |

---

## Session Structure (4-6 Hours)

### Hour 1: Baseline & Diagnostics (60 min)

**Objectives:**
- [ ] Establish accurate baseline with `--tier tier2` (no Ollama)
- [ ] Identify top 10 misrouting patterns
- [ ] Analyze confusion matrix per agent
- [ ] Document current thresholds and weights

**Commands:**
```bash
# Establish baseline
python3 scripts/eval_router.py --tier tier2

# Save results
python3 scripts/eval_router.py --tier tier2 > baseline_tier2.txt
```

**Expected Improvement:** Establish accurate 60% baseline

---

### Hour 2: Threshold & Weight Tuning (90 min)

**Objectives:**
- [ ] Run grid search for optimal weights
- [ ] Tune per-agent confidence thresholds
- [ ] Test 20+ weight combinations

**Commands:**
```bash
# Grid search
python3 scripts/eval_router.py --tune

# Test specific weights
python3 scripts/eval_router.py --weights 0.3,0.5,0.2
python3 scripts/eval_router.py --weights 0.4,0.4,0.2
```

**Expected Improvement:** 60% → 70-75%

---

### Hour 3: Feature Engineering (90 min)

**Objectives:**
- [ ] Add task complexity scoring
- [ ] Implement file extension detection
- [ ] Add multi-step task detection
- [ ] Improve keyword taxonomy

**Expected Improvement:** 75% → 80-82%

---

### Hour 4: Data Augmentation (60 min)

**Objectives:**
- [ ] Generate 100+ synthetic training samples
- [ ] Address class imbalance
- [ ] Rebalance dataset

**Expected Improvement:** 82% → 85-87%

---

### Hour 5: Ensemble & Advanced Techniques (60 min)

**Objectives:**
- [ ] Implement ensemble: rules + TF-IDF + keywords
- [ ] Add confidence-based fallback chain
- [ ] Test ensemble vs individual methods

**Expected Improvement:** 87% → 90-92%

---

### Hour 6: Validation & Documentation (60 min)

**Objectives:**
- [ ] Final evaluation on held-out test set
- [ ] Cross-validation (5-fold)
- [ ] Document final accuracy
- [ ] Update FEDERATION_LOG.md

**Target Achievement:** >90% ✅

---

## Success Criteria

| Checkpoint | Target | Fallback |
|------------|--------|----------|
| Hour 2 end | >70% | Adjust weights |
| Hour 3 end | >80% | More features |
| Hour 4 end | >85% | More data |
| Hour 5 end | >90% | Ensemble tuning |
| Hour 6 end | >90% | Deploy |

---

## Key Strategies

1. **Class Rebalancing**: Address kimi:copilot 4:1 ratio
2. **Threshold Tuning**: Lower kimi (0.35→0.30), adjust ollama (0.50→0.45)
3. **Feature Engineering**: Complexity scoring, file type detection
4. **Ensemble**: Combine rules + TF-IDF + keywords
5. **Active Learning**: Flag uncertain predictions for review

---

## Deliverables

- `baseline_tier2.txt` — Initial accuracy measurement
- `optimal_weights.json` — Best weight configuration
- `route_task_v4_ensemble.py` — Production router
- `FINAL_ACCURACY_REPORT.md` — Results documentation

---

**Ready to schedule when you are.** 🧭🔮⚡
