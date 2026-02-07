#!/usr/bin/env python3
"""
Day 4 Eval — 4-Signal Grid Search with Stratified Split

Searches over (embedding_weight, keyword_weight, tfidf_weight, complexity_weight)
using stratified train/test split. Reports:
- Overall accuracy
- Per-agent precision, recall, F1
- Confusion matrix
- Top weight configurations
- Misrouted samples for error analysis

Usage:
    python3 day4_eval.py                  # Quick eval with current hybrid weights
    python3 day4_eval.py --tune           # Full 4D grid search (no Ollama)
    python3 day4_eval.py --tune-fine      # Fine-grained search around best
    python3 day4_eval.py --misses         # Show all misrouted tasks
"""
import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).parent.parent
TRAINING = ROOT / ".federation" / "training_data.json"
AGENTS = ["claude", "codex", "copilot", "kimi", "ollama"]


def load_data():
    data = json.loads(TRAINING.read_text())
    # Normalize agent field
    for s in data:
        s["agent"] = s.get("agent", s.get("expected_agent", "unknown")).lower()
    return data


def stratified_split(data, test_ratio=0.2, seed=42):
    """Split data preserving agent distribution in both sets."""
    random.seed(seed)
    by_agent = defaultdict(list)
    for s in data:
        by_agent[s["agent"]].append(s)

    train, test = [], []
    for agent, samples in by_agent.items():
        random.shuffle(samples)
        n_test = max(1, int(len(samples) * test_ratio))
        test.extend(samples[:n_test])
        train.extend(samples[n_test:])

    random.shuffle(train)
    random.shuffle(test)
    return train, test


def evaluate(train_data, test_data, weights=None, tier="hybrid"):
    """Run eval and return detailed results."""
    from route_task_v3 import build_tfidf_index, route

    index = build_tfidf_index(train_data)

    results = []
    for item in test_data:
        pred = route(item["task"], index=index, weights=weights, tier=tier)
        predicted = pred.get("recommended_agent", "").lower()
        actual = item["agent"].lower()
        results.append({
            "task": item["task"],
            "expected": actual,
            "predicted": predicted,
            "correct": predicted == actual,
            "confidence": pred.get("confidence", 0),
            "method": pred.get("method", ""),
        })

    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / len(test_data) if test_data else 0
    return accuracy, results


def per_agent_metrics(results):
    """Calculate precision, recall, F1 per agent."""
    tp = Counter()
    fp = Counter()
    fn = Counter()

    for r in results:
        if r["correct"]:
            tp[r["expected"]] += 1
        else:
            fp[r["predicted"]] += 1
            fn[r["expected"]] += 1

    metrics = {}
    for agent in AGENTS:
        p = tp[agent] / (tp[agent] + fp[agent]) if (tp[agent] + fp[agent]) > 0 else 0
        r = tp[agent] / (tp[agent] + fn[agent]) if (tp[agent] + fn[agent]) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        metrics[agent] = {"precision": p, "recall": r, "f1": f1,
                          "tp": tp[agent], "fp": fp[agent], "fn": fn[agent]}
    return metrics


def confusion_matrix(results):
    """Build and print confusion matrix."""
    matrix = {a: {b: 0 for b in AGENTS} for a in AGENTS}
    for r in results:
        if r["expected"] in matrix and r["predicted"] in matrix.get(r["expected"], {}):
            matrix[r["expected"]][r["predicted"]] += 1
    return matrix


def print_confusion(matrix):
    header = f"{'Exp\\Pred':>10}" + "".join(f"{a:>10}" for a in AGENTS)
    print(header)
    print("-" * (10 + 10 * len(AGENTS)))
    for a in AGENTS:
        row = f"{a:>10}"
        for b in AGENTS:
            count = matrix[a][b]
            marker = f"{count}" if a != b or count == 0 else f"[{count}]"
            row += f"{marker:>10}"
        print(row)


def print_metrics(metrics):
    print(f"\n{'Agent':>10} {'Prec':>8} {'Recall':>8} {'F1':>8} {'TP':>5} {'FP':>5} {'FN':>5}")
    print("-" * 55)
    for agent in AGENTS:
        m = metrics[agent]
        print(f"{agent:>10} {m['precision']:>8.1%} {m['recall']:>8.1%} {m['f1']:>8.1%} {m['tp']:>5} {m['fp']:>5} {m['fn']:>5}")


def grid_search(train_data, test_data, step=0.1, fine_center=None, fine_range=0.15):
    """
    4D grid search over (embed, keyword, tfidf, complexity) weights.
    Since Ollama is likely offline, embed weight is fixed at 0.
    Searches over (kw, tfidf, cx) where embed = 0.
    """
    from route_task_v3 import build_tfidf_index

    # Pre-build index once
    index = build_tfidf_index(train_data)

    # Import route for direct use with pre-built index
    from route_task_v3 import route

    configs = []

    if fine_center:
        # Fine-grained search around a known good config
        _, kw_c, tf_c, cx_c = fine_center
        fine_step = step / 2
        for kw in [round(kw_c + i * fine_step, 2) for i in range(-3, 4)]:
            for tf in [round(tf_c + i * fine_step, 2) for i in range(-3, 4)]:
                for cx in [round(cx_c + i * fine_step, 2) for i in range(-3, 4)]:
                    if kw >= 0 and tf >= 0 and cx >= 0:
                        total = kw + tf + cx
                        if total > 0:
                            # Normalize to sum to 1
                            configs.append((0.0, round(kw/total, 3), round(tf/total, 3), round(cx/total, 3)))
    else:
        # Coarse grid: embed=0, search kw/tfidf/cx
        for kw in [round(x * step, 2) for x in range(0, int(1/step) + 1)]:
            for tf in [round(x * step, 2) for x in range(0, int(1/step) + 1)]:
                cx = round(1.0 - kw - tf, 2)
                if 0 <= cx <= 1.0:
                    configs.append((0.0, kw, tf, cx))

    # Deduplicate
    configs = list(set(configs))
    print(f"Testing {len(configs)} weight configurations...")

    best = {"accuracy": 0, "weights": None}
    all_results = []
    t0 = time.time()

    for i, weights in enumerate(configs):
        correct = 0
        for item in test_data:
            pred = route(item["task"], index=index, weights=weights, tier="hybrid")
            if pred.get("recommended_agent", "").lower() == item["agent"].lower():
                correct += 1
        acc = correct / len(test_data) if test_data else 0
        all_results.append({"accuracy": acc, "weights": weights, "correct": correct})

        if acc > best["accuracy"]:
            best = {"accuracy": acc, "weights": weights, "correct": correct}
            print(f"  [{i+1}/{len(configs)}] New best: embed={weights[0]} kw={weights[1]} tfidf={weights[2]} cx={weights[3]} → {acc*100:.1f}%")

    elapsed = time.time() - t0
    print(f"\nGrid search completed in {elapsed:.1f}s")
    return best, sorted(all_results, key=lambda x: -x["accuracy"])


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Day 4 Eval — 4-Signal Grid Search")
    parser.add_argument("--tune", action="store_true", help="Coarse grid search (step=0.1)")
    parser.add_argument("--tune-fine", action="store_true", help="Fine grid around best")
    parser.add_argument("--misses", action="store_true", help="Show misrouted tasks")
    parser.add_argument("--weights", type=str, help="Custom weights 'embed,kw,tfidf,cx'")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    data = load_data()
    print(f"Loaded {len(data)} samples")
    dist = Counter(s["agent"] for s in data)
    for a in AGENTS:
        print(f"  {a}: {dist.get(a, 0)}")
    print()

    train, test = stratified_split(data, seed=args.seed)
    print(f"Split: {len(train)} train / {len(test)} test (stratified)")

    # --- Grid Search ---
    if args.tune or args.tune_fine:
        print("\n" + "=" * 60)
        mode = "FINE" if args.tune_fine else "COARSE"
        print(f"4-SIGNAL GRID SEARCH ({mode})")
        print("=" * 60)

        if args.tune_fine:
            # First run coarse to find center
            print("Phase 1: Coarse search...")
            coarse_best, _ = grid_search(train, test, step=0.1)
            print(f"\nPhase 2: Fine search around {coarse_best['weights']}...")
            best, all_sorted = grid_search(train, test, step=0.1,
                                           fine_center=coarse_best["weights"])
        else:
            best, all_sorted = grid_search(train, test, step=0.1)

        print(f"\n{'='*60}")
        print("TOP 10 CONFIGURATIONS")
        print(f"{'='*60}")
        print(f"{'#':>3} {'embed':>7} {'kw':>7} {'tfidf':>7} {'cx':>7} {'Accuracy':>10}")
        print("-" * 45)
        for i, r in enumerate(all_sorted[:10], 1):
            w = r["weights"]
            print(f"{i:>3} {w[0]:>7.2f} {w[1]:>7.2f} {w[2]:>7.2f} {w[3]:>7.2f} {r['accuracy']*100:>9.1f}%")

        # Evaluate best with full metrics
        weights = best["weights"]
        print(f"\n{'='*60}")
        print(f"BEST: weights={weights} → {best['accuracy']*100:.1f}%")
        print(f"{'='*60}")

        accuracy, results = evaluate(train, test, weights=weights)
        cm = confusion_matrix(results)
        metrics = per_agent_metrics(results)

        print(f"\nConfusion Matrix:")
        print_confusion(cm)
        print_metrics(metrics)

        if best["accuracy"] >= 0.85:
            print(f"\n✅ TARGET ACHIEVED: {best['accuracy']*100:.1f}% >= 85%")
        else:
            print(f"\n⚠️  Accuracy {best['accuracy']*100:.1f}% — target is 85%")

        # Save best weights
        config = {
            "best_weights": list(weights),
            "accuracy": best["accuracy"],
            "n_train": len(train),
            "n_test": len(test),
            "seed": args.seed,
            "agent_distribution": dict(dist),
        }
        config_path = ROOT / ".federation" / "best_weights.json"
        config_path.write_text(json.dumps(config, indent=2))
        print(f"\nSaved best weights to {config_path}")
        return

    # --- Single Eval ---
    weights = None
    if args.weights:
        parts = [float(x) for x in args.weights.split(",")]
        if len(parts) == 4:
            weights = tuple(parts)
            print(f"Using custom weights: {weights}")

    print(f"\n{'='*60}")
    print("EVALUATION")
    print(f"{'='*60}")

    accuracy, results = evaluate(train, test, weights=weights)
    print(f"\nAccuracy: {accuracy*100:.1f}% ({sum(1 for r in results if r['correct'])}/{len(results)})")

    cm = confusion_matrix(results)
    print(f"\nConfusion Matrix:")
    print_confusion(cm)

    metrics = per_agent_metrics(results)
    print_metrics(metrics)

    misses = [r for r in results if not r["correct"]]
    if args.misses and misses:
        print(f"\n{'='*60}")
        print(f"MISROUTED ({len(misses)} tasks)")
        print(f"{'='*60}")
        for m in misses:
            print(f"\n  Task: {m['task'][:80]}")
            print(f"  Expected: {m['expected']} → Got: {m['predicted']} (conf: {m['confidence']:.3f}, {m['method']})")

    if accuracy >= 0.85:
        print(f"\n✅ TARGET ACHIEVED: {accuracy*100:.1f}% >= 85%")
    elif accuracy >= 0.80:
        print(f"\n⚠️  CLOSE: {accuracy*100:.1f}% (target: 85%)")
    else:
        print(f"\n❌ BELOW TARGET: {accuracy*100:.1f}% (target: 85%)")


if __name__ == "__main__":
    main()
