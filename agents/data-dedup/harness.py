"""Harness for evaluating data dedup matching rules.

Usage:
  python harness.py baseline  # Run baseline (no duplicates found)
  python harness.py evaluate  # Evaluate current match_rules.py
"""

import json
import sys
import inspect
from match_rules import find_duplicates


def load_dataset():
    """Load records and golden_clusters from records.json."""
    with open("records.json", "r") as f:
        data = json.load(f)
    return data["records"], data["golden_clusters"]


def clusters_to_pairs(clusters):
    """Convert list of clusters to set of pairs for comparison."""
    pairs = set()
    for cluster in clusters:
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                # Canonical pair: (min, max) to avoid duplicates
                pair = tuple(sorted([cluster[i], cluster[j]]))
                pairs.add(pair)
    return pairs


def calculate_metrics(predicted_pairs, true_pairs):
    """Calculate precision, recall, and F1 score."""
    if len(predicted_pairs) == 0:
        # No predictions made
        if len(true_pairs) == 0:
            return 1.0, 1.0, 1.0  # Perfect score if no duplicates to find
        else:
            return 0.0, 0.0, 0.0  # No predictions, no recall

    tp = len(predicted_pairs & true_pairs)
    fp = len(predicted_pairs - true_pairs)
    fn = len(true_pairs - predicted_pairs)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def anti_gaming_check(records, golden_clusters):
    """Check that find_duplicates doesn't cheat."""
    source = inspect.getsource(find_duplicates)

    # Check 1: Don't reference golden_clusters
    if "golden" in source.lower():
        raise ValueError("ERROR: find_duplicates source contains 'golden' — no peeking!")

    # Check 2: Don't read records.json directly
    if "records.json" in source or "json.load" in source:
        raise ValueError("ERROR: find_duplicates reads records.json directly — no cheating!")

    return True


def validate_clusters(predicted_clusters, records):
    """Validate that all predicted record_ids exist in dataset."""
    valid_ids = {r["record_id"] for r in records}
    for cluster in predicted_clusters:
        for record_id in cluster:
            if record_id not in valid_ids:
                raise ValueError(f"ERROR: Invalid record_id '{record_id}' in clusters")


def evaluate(records, golden_clusters):
    """Run evaluation."""
    print("\n=== Evaluation ===")

    # Anti-gaming checks
    try:
        anti_gaming_check(records, golden_clusters)
    except ValueError as e:
        print(e)
        return

    # Run dedup — golden_clusters stripped from records
    records_copy = [r.copy() for r in records]
    predicted_clusters = find_duplicates(records_copy)

    # Validate clusters
    try:
        validate_clusters(predicted_clusters, records)
    except ValueError as e:
        print(e)
        return

    # Build true pairs from golden_clusters
    golden_clusters_list = list(golden_clusters.values())
    true_pairs = clusters_to_pairs(golden_clusters_list)

    # Build predicted pairs
    predicted_pairs = clusters_to_pairs(predicted_clusters)

    # Calculate metrics
    precision, recall, f1 = calculate_metrics(predicted_pairs, true_pairs)

    print(f"True duplicate pairs: {len(true_pairs)}")
    print(f"Predicted duplicate pairs: {len(predicted_pairs)}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

    # Baseline is f1=0 (no duplicates found)
    improvement_pct = (f1 - 0.0) / (1.0 - 0.0) * 100 if f1 > 0 else 0.0
    print(f"\nRESULT: f1_score={f1:.4f} improvement_pct={improvement_pct:.1f}")


def baseline(records, golden_clusters):
    """Run baseline (every record is its own cluster)."""
    print("\n=== Baseline (no dedup) ===")
    baseline_clusters = [[r["record_id"]] for r in records]

    golden_clusters_list = list(golden_clusters.values())
    true_pairs = clusters_to_pairs(golden_clusters_list)
    predicted_pairs = clusters_to_pairs(baseline_clusters)

    precision, recall, f1 = calculate_metrics(predicted_pairs, true_pairs)

    print(f"True duplicate pairs: {len(true_pairs)}")
    print(f"Predicted duplicate pairs: {len(predicted_pairs)}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"\nRESULT: f1_score={f1:.4f} improvement_pct=0.0")


if __name__ == "__main__":
    records, golden_clusters = load_dataset()

    if len(sys.argv) > 1:
        if sys.argv[1] == "baseline":
            baseline(records, golden_clusters)
        elif sys.argv[1] == "evaluate":
            evaluate(records, golden_clusters)
        else:
            print("Usage: python harness.py [baseline|evaluate]")
    else:
        print("Usage: python harness.py [baseline|evaluate]")
