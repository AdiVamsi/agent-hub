"""AI drift evaluation harness.

Loads eval_config.py and eval_dataset.json, runs evaluations,
calculates drift_score (lower is better), and reports precision/recall/f1.

Usage:
    python harness.py evaluate    — full evaluation, print RESULT line
    python harness.py baseline    — show drift_score with default config
    python harness.py report      — detailed report per category
"""

import json
import sys
import re
from pathlib import Path
from typing import Callable


def jaccard_similarity(s1: str, s2: str) -> float:
    """Jaccard similarity between two strings (word-based)."""
    words1 = set(s1.lower().split())
    words2 = set(s2.lower().split())
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    return intersection / union if union > 0 else 0.0


def cosine_similarity(s1: str, s2: str) -> float:
    """Approximate cosine similarity using word overlap."""
    words1 = s1.lower().split()
    words2 = s2.lower().split()
    if not words1 or not words2:
        return 1.0 if s1.lower() == s2.lower() else 0.0

    # Count word frequencies
    freq1, freq2 = {}, {}
    for w in words1:
        freq1[w] = freq1.get(w, 0) + 1
    for w in words2:
        freq2[w] = freq2.get(w, 0) + 1

    # Dot product of frequency vectors
    dot_product = sum(freq1.get(w, 0) * freq2.get(w, 0) for w in freq1)
    mag1 = sum(v * v for v in freq1.values()) ** 0.5
    mag2 = sum(v * v for v in freq2.values()) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


def compute_metric(metric_type: str, golden: str, current: str, params: dict) -> float:
    """Compute a specific evaluation metric.

    Args:
        metric_type: "similarity"|"keyword"|"length"|"sentiment"|"format"
        golden: reference output
        current: current output
        params: metric-specific parameters

    Returns:
        Score in range [0, 1] where 1 is best.
    """
    if metric_type == "similarity":
        method = params.get("method", "jaccard")
        if method == "jaccard":
            return jaccard_similarity(golden, current)
        elif method == "cosine":
            return cosine_similarity(golden, current)
        else:
            return jaccard_similarity(golden, current)

    elif metric_type == "keyword":
        required = params.get("required", [])
        forbidden = params.get("forbidden", [])

        current_lower = current.lower()
        required_found = sum(1 for kw in required if kw.lower() in current_lower)
        required_score = required_found / len(required) if required else 1.0

        forbidden_found = sum(1 for kw in forbidden if kw.lower() in current_lower)
        forbidden_score = 1.0 - (forbidden_found / len(forbidden) if forbidden else 0.0)

        return (required_score + forbidden_score) / 2

    elif metric_type == "length":
        golden_len = len(golden.split())
        current_len = len(current.split())

        if golden_len == 0:
            return 1.0 if current_len == 0 else 0.0

        ratio = current_len / golden_len
        min_ratio = params.get("min_ratio", 0.5)
        max_ratio = params.get("max_ratio", 1.5)

        if ratio < min_ratio or ratio > max_ratio:
            return 0.0

        # Penalize deviation from golden
        ideal_diff = 0
        actual_diff = abs(current_len - golden_len)
        return max(0.0, 1.0 - (actual_diff / max(golden_len, current_len)))

    elif metric_type == "sentiment":
        positive_words = params.get("positive", [])
        negative_words = params.get("negative", [])

        current_lower = current.lower()
        pos_count = sum(1 for w in positive_words if w.lower() in current_lower)
        neg_count = sum(1 for w in negative_words if w.lower() in current_lower)

        total = pos_count + neg_count
        if total == 0:
            return 0.5
        return pos_count / total

    elif metric_type == "format":
        checks = params.get("checks", [])
        score = 0.0

        for check in checks:
            if check == "json":
                try:
                    json.loads(current)
                    score += 1.0
                except:
                    pass
            elif check == "code_block":
                if "```" in current or "    " in current:
                    score += 1.0
            elif check == "bullets":
                if "•" in current or "-" in current or "*" in current:
                    score += 1.0
            elif check == "paragraphs":
                if len(current.split("\n\n")) > 1:
                    score += 1.0

        return score / len(checks) if checks else 1.0

    return 0.5


def evaluate_pair(golden: str, current: str, metadata: dict, eval_config) -> dict:
    """Evaluate a golden/current output pair using the config.

    Returns a dict with:
        dimensions: list of (name, score) tuples
        overall_score: aggregated score
        is_regression: bool prediction from the config
        confidence: confidence in the prediction
    """
    dimensions = eval_config.get_eval_dimensions()
    rules = eval_config.get_scoring_rules()

    # Compute dimension scores
    dim_scores = []
    for dim in dimensions:
        metric_type = dim["metric"]
        params = dim.get("params", {})
        score = compute_metric(metric_type, golden, current, params)

        # Apply threshold
        threshold = dim.get("threshold", 0.5)
        below_threshold = score < threshold

        dim_scores.append({
            "name": dim["name"],
            "score": score,
            "weight": dim.get("weight", 1.0),
            "threshold": threshold,
            "below_threshold": below_threshold,
        })

    # Aggregate scores
    if rules["aggregation"] == "weighted":
        total_weight = sum(d["weight"] for d in dim_scores)
        overall_score = sum(d["score"] * d["weight"] for d in dim_scores) / total_weight if total_weight > 0 else 0.5
    elif rules["aggregation"] == "min":
        overall_score = min((d["score"] for d in dim_scores), default=0.5)
    elif rules["aggregation"] == "max":
        overall_score = max((d["score"] for d in dim_scores), default=0.5)
    else:  # mean
        overall_score = sum(d["score"] for d in dim_scores) / len(dim_scores) if dim_scores else 0.5

    # Call custom classify_output if it exists
    custom_result = eval_config.classify_output(golden, current, metadata)

    # Determine regression prediction
    regression_threshold = rules.get("regression_threshold", 0.5)
    confidence_min = rules.get("confidence_min", 0.0)

    # Use custom result if it has high confidence, otherwise use threshold
    if custom_result.get("confidence", 0.0) > confidence_min:
        is_regression = custom_result.get("is_regression", False)
        confidence = custom_result.get("confidence", 0.5)
    else:
        is_regression = overall_score < regression_threshold
        confidence = abs(overall_score - regression_threshold)

    return {
        "dimensions": dim_scores,
        "overall_score": overall_score,
        "is_regression": is_regression,
        "confidence": confidence,
    }


def calculate_metrics(predictions, ground_truth) -> dict:
    """Calculate precision, recall, f1 from predictions vs ground truth.

    Args:
        predictions: list of bool (True = regression predicted)
        ground_truth: list of str ("regression" or "ok")

    Returns:
        dict with precision, recall, f1
    """
    true_positives = sum(1 for p, g in zip(predictions, ground_truth)
                         if p and g == "regression")
    false_positives = sum(1 for p, g in zip(predictions, ground_truth)
                          if p and g == "ok")
    false_negatives = sum(1 for p, g in zip(predictions, ground_truth)
                          if not p and g == "regression")

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def run_evaluation(eval_config):
    """Load dataset and run full evaluation."""
    dataset_path = Path(__file__).parent / "eval_dataset.json"

    if not dataset_path.exists():
        print(f"ERROR: {dataset_path} not found. Run 'python prepare.py generate' first.")
        sys.exit(1)

    with open(dataset_path) as f:
        dataset = json.load(f)

    predictions = []
    ground_truth = []
    results = []

    for item in dataset:
        golden = item["golden_output"]
        current = item["current_output"]
        metadata = item.get("metadata", {})
        truth = item.get("ground_truth", "ok")

        eval_result = evaluate_pair(golden, current, metadata, eval_config)
        predictions.append(eval_result["is_regression"])
        ground_truth.append(truth)

        results.append({
            "id": item["id"],
            "prediction": eval_result["is_regression"],
            "confidence": eval_result["confidence"],
            "ground_truth": truth,
            "overall_score": eval_result["overall_score"],
            "metadata": metadata,
        })

    metrics = calculate_metrics(predictions, ground_truth)

    # Calculate drift_score
    missed_regressions = metrics["false_negatives"]
    false_alarms = metrics["false_positives"]

    # Miscalibration penalty: how confident are we when wrong?
    miscalibration = 0.0
    for result in results:
        if result["ground_truth"] == "regression" and not result["prediction"]:
            # Missed regression - penalize low overall_score when it was "ok" prediction
            miscalibration += (1.0 - result["overall_score"]) * 0.5
        elif result["ground_truth"] == "ok" and result["prediction"]:
            # False alarm - penalize high overall_score when it was "regression" prediction
            miscalibration += result["overall_score"] * 0.5

    drift_score = (missed_regressions * 5) + (false_alarms * 2) + miscalibration

    return {
        "drift_score": drift_score,
        "missed_regressions": missed_regressions,
        "false_alarms": false_alarms,
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "results": results,
        "metrics": metrics,
    }


def print_result(eval_result):
    """Print RESULT line."""
    print(f"RESULT: drift_score={eval_result['drift_score']:.1f} "
          f"missed_regressions={eval_result['missed_regressions']} "
          f"false_alarms={eval_result['false_alarms']} "
          f"precision={eval_result['precision']:.2f} "
          f"recall={eval_result['recall']:.2f} "
          f"f1={eval_result['f1']:.2f}")


if __name__ == "__main__":
    import importlib.util

    spec = importlib.util.spec_from_file_location("eval_config", "eval_config.py")
    eval_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eval_config)

    if len(sys.argv) < 2:
        print("Usage: python harness.py {evaluate|baseline|report}")
        sys.exit(1)

    command = sys.argv[1]

    if command == "evaluate":
        result = run_evaluation(eval_config)
        print_result(result)

    elif command == "baseline":
        result = run_evaluation(eval_config)
        print(f"Baseline drift_score: {result['drift_score']:.1f}")
        print(f"  Missed regressions: {result['missed_regressions']}")
        print(f"  False alarms: {result['false_alarms']}")
        print(f"  Precision: {result['precision']:.2f}, Recall: {result['recall']:.2f}, F1: {result['f1']:.2f}")

    elif command == "report":
        result = run_evaluation(eval_config)
        print(f"\n=== Drift Evaluation Report ===")
        print(f"Overall drift_score: {result['drift_score']:.1f}")
        print(f"Missed regressions: {result['missed_regressions']}")
        print(f"False alarms: {result['false_alarms']}")
        print(f"Precision: {result['precision']:.2f}, Recall: {result['recall']:.2f}, F1: {result['f1']:.2f}\n")

        # By category
        by_category = {}
        for res in result["results"]:
            cat = res["metadata"].get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(res)

        for cat, items in sorted(by_category.items()):
            correct = sum(1 for item in items if (item["prediction"] and item["ground_truth"] == "regression") or
                          (not item["prediction"] and item["ground_truth"] == "ok"))
            print(f"{cat:15} ({len(items):3} items): {correct:3}/{len(items)} correct")
