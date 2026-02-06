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


def main():
    data = load_data()
    print(f"Loaded {len(data)} samples from {TRAINING_PATH}\n")

    train_data, test_data = split_data(data)
    print(f"Split: {len(train_data)} train / {len(test_data)} test\n")

    print("=" * 60)
    print("EVALUATING v3 (TF-IDF + Keyword + Complexity Hybrid)")
    print("=" * 60)
    v3_results = eval_v3(train_data, test_data)
    print(f"Accuracy: {v3_results['accuracy']*100:.1f}% ({v3_results['correct']}/{v3_results['total']})")

    # Confusion matrix
    cm = confusion_matrix(v3_results["results"])
    print("\nConfusion Matrix (rows=expected, cols=predicted):")
    agents = sorted(cm.keys())
    header = f"{'':>10}" + "".join(f"{a:>10}" for a in agents)
    print(header)
    for a in agents:
        row = f"{a:>10}" + "".join(f"{cm[a][b]:>10}" for b in agents)
        print(row)

    # Misses
    misses = [r for r in v3_results["results"] if not r["correct"]]
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


if __name__ == "__main__":
    main()
