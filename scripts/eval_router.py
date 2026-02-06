#!/usr/bin/env python3
"""
Router Evaluation Harness — A/B test v2 vs v3

Splits training data into train/test, measures accuracy.
No external dependencies.
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

TRAINING_PATH = Path(__file__).parent.parent / ".federation" / "training_data.json"


def load_data() -> list[dict]:
    if not TRAINING_PATH.exists():
        print(f"No training data at {TRAINING_PATH}")
        sys.exit(1)
    return json.loads(TRAINING_PATH.read_text())


def split_data(data: list[dict], test_ratio: float = 0.2, seed: int = 42):
    """Stratified train/test split."""
    random.seed(seed)
    random.shuffle(data)
    split_idx = int(len(data) * (1 - test_ratio))
    return data[:split_idx], data[split_idx:]


def eval_v3(train_data: list[dict], test_data: list[dict]) -> dict:
    """Evaluate route_task_v3 on test set."""
    from route_task_v3 import build_tfidf_index, route

    # Build index from train split only
    index = build_tfidf_index(train_data)

    correct = 0
    results = []
    for item in test_data:
        prediction = route(item["task"], index=index)
        predicted_agent = prediction.get("recommended_agent", "").lower()
        actual = item["agent"].lower()
        is_correct = predicted_agent == actual
        if is_correct:
            correct += 1
        results.append({
            "task": item["task"],
            "expected": actual,
            "predicted": predicted_agent,
            "correct": is_correct,
            "confidence": prediction.get("confidence", 0),
            "tier": prediction.get("tier", 2)
        })

    accuracy = correct / len(test_data) if test_data else 0
    return {
        "accuracy": round(accuracy, 4),
        "correct": correct,
        "total": len(test_data),
        "results": results
    }


def confusion_matrix(results: list[dict]) -> dict:
    """Build confusion matrix from results."""
    agents = sorted(set(r["expected"] for r in results) | set(r["predicted"] for r in results))
    matrix = {a: {b: 0 for b in agents} for a in agents}
    for r in results:
        if r["expected"] in matrix and r["predicted"] in matrix.get(r["expected"], {}):
            matrix[r["expected"]][r["predicted"]] += 1
    return matrix


def eval_v3_with_weights(train_data: list[dict], test_data: list[dict], weights: tuple) -> dict:
    """Evaluate route_task_v3 with specific weights."""
    from route_task_v3 import build_tfidf_index, route

    # Build index from train split only
    index = build_tfidf_index(train_data)

    correct = 0
    for item in test_data:
        prediction = route(item["task"], index=index, weights=weights)
        predicted_agent = prediction.get("recommended_agent", "").lower()
        actual = item["agent"].lower()
        if predicted_agent == actual:
            correct += 1

    accuracy = correct / len(test_data) if test_data else 0
    return {
        "accuracy": round(accuracy, 4),
        "correct": correct,
        "total": len(test_data),
        "weights": weights
    }


def tune_weights(data: list[dict], step: float = 0.1) -> dict:
    """
    Grid search optimal weights for (tfidf, keyword, complexity).
    Returns best configuration and all results.
    """
    train_data, test_data = split_data(data)
    print(f"Tuning with {len(train_data)} train / {len(test_data)} test\n")
    
    best = {"accuracy": 0, "weights": None}
    all_results = []
    
    # Grid search: weights must sum to ~1.0
    weights_options = []
    for tfidf in [round(x * step, 1) for x in range(0, int(1/step) + 1)]:
        for keyword in [round(x * step, 1) for x in range(0, int(1/step) + 1)]:
            complexity = round(1.0 - tfidf - keyword, 1)
            if 0 <= complexity <= 1.0:
                weights_options.append((tfidf, keyword, complexity))
    
    print(f"Testing {len(weights_options)} weight combinations...")
    
    for weights in weights_options:
        result = eval_v3_with_weights(train_data, test_data, weights)
        all_results.append(result)
        if result["accuracy"] > best["accuracy"]:
            best = result
            print(f"  New best: {weights} → {result['accuracy']*100:.1f}%")
    
    return best, all_results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Router evaluation harness")
    parser.add_argument("--tune", action="store_true", help="Run weight tuning grid search")
    parser.add_argument("--weights", type=str, help="Custom weights as 'tfidf,keyword,complexity' (e.g., '0.3,0.5,0.2')")
    args = parser.parse_args()

    data = load_data()
    print(f"Loaded {len(data)} samples from {TRAINING_PATH}\n")

    if args.tune:
        print("=" * 60)
        print("TUNING WEIGHTS (Grid Search)")
        print("=" * 60)
        best, all_results = tune_weights(data)
        print(f"\n{'='*60}")
        print("BEST CONFIGURATION")
        print(f"{'='*60}")
        print(f"  Weights: {best['weights']}")
        print(f"  Accuracy: {best['accuracy']*100:.1f}%")
        print(f"  ({best['correct']}/{best['total']} correct)")
        
        # Show top 5
        print(f"\nTop 5 configurations:")
        sorted_results = sorted(all_results, key=lambda x: x["accuracy"], reverse=True)[:5]
        for i, r in enumerate(sorted_results, 1):
            print(f"  {i}. {r['weights']} → {r['accuracy']*100:.1f}%")
        return

    train_data, test_data = split_data(data)
    print(f"Split: {len(train_data)} train / {len(test_data)} test\n")

    # Use custom weights if provided
    weights = None
    if args.weights:
        parts = [float(x) for x in args.weights.split(",")]
        if len(parts) == 3:
            weights = tuple(parts)
            print(f"Using custom weights: {weights}\n")

    print("=" * 60)
    print("EVALUATING v3 (TF-IDF + Keyword + Complexity Hybrid)")
    print("=" * 60)
    
    if weights:
        v3_results = eval_v3_with_weights(train_data, test_data, weights)
    else:
        v3_results = eval_v3(train_data, test_data)
    
    print(f"Accuracy: {v3_results['accuracy']*100:.1f}% ({v3_results['correct']}/{v3_results['total']})")

    # Confusion matrix
    # Re-run to get full results for matrix
    from route_task_v3 import build_tfidf_index, route
    index = build_tfidf_index(train_data)
    results = []
    for item in test_data:
        prediction = route(item["task"], index=index, weights=weights) if weights else route(item["task"], index=index)
        results.append({
            "task": item["task"],
            "expected": item["agent"].lower(),
            "predicted": prediction.get("recommended_agent", "").lower(),
            "correct": prediction.get("recommended_agent", "").lower() == item["agent"].lower(),
            "confidence": prediction.get("confidence", 0),
            "tier": prediction.get("tier", 2)
        })
    
    cm = confusion_matrix(results)
    print("\nConfusion Matrix (rows=expected, cols=predicted):")
    agents = sorted(cm.keys())
    header = f"{'':>10}" + "".join(f"{a:>10}" for a in agents)
    print(header)
    for a in agents:
        row = f"{a:>10}" + "".join(f"{cm[a][b]:>10}" for b in agents)
        print(row)

    # Misses
    misses = [r for r in results if not r["correct"]]
    if misses:
        print(f"\nMisrouted ({len(misses)}):")
        for m in misses:
            print(f"  Task: {m['task'][:60]}...")
            print(f"    Expected: {m['expected']} | Got: {m['predicted']} (conf: {m.get('confidence', '?')}, tier: {m.get('tier', '?')})")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  v3 hybrid:  {v3_results['accuracy']*100:.1f}%")
    print(f"  Total samples: {len(data)}")
    print(f"  Training samples: {len(train_data)}")
    print(f"  Test samples: {len(test_data)}")
    if weights:
        print(f"  Weights: {weights}")


if __name__ == "__main__":
    main()
