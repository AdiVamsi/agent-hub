"""Schema Guard — Evaluation Harness.

Loads schema_changes.json, runs check_rules.is_breaking_change against each change,
and scores results against ground truth.
"""

import json
import sys
import inspect
from typing import Any, Dict, List


def load_changes() -> List[Dict[str, Any]]:
    """Load schema_changes.json."""
    try:
        with open("schema_changes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: schema_changes.json not found. Run: python prepare.py generate")
        sys.exit(1)


def sanitize_change(change: Dict[str, Any]) -> Dict[str, Any]:
    """Remove ground truth fields to prevent cheating."""
    sanitized = change.copy()
    # Remove fields that would give away the answer
    sanitized.pop("is_breaking", None)
    sanitized.pop("severity", None)
    return sanitized


def check_source_for_cheating(check_rules_module: Any) -> bool:
    """Check if check_rules.py reads schema_changes.json directly."""
    source = inspect.getsource(check_rules_module.is_breaking_change)
    if "schema_changes" in source or "load_changes" in source or "open(" in source:
        print("ERROR: check_rules.py appears to read schema_changes.json directly!")
        print("This is cheating. The function must only use the change parameter.")
        return True
    return False


def score_result(
    predicted: Dict[str, Any],
    ground_truth: Dict[str, Any],
    change_type: str
) -> tuple:
    """Score a single prediction.

    Returns:
        (score, breakdown) where breakdown is a dict with components
    """
    score = 0.0
    breakdown = {
        "tp": 0, "tn": 0, "fp": 0, "fn": 0, "severity_bonus": 0
    }

    predicted_breaking = predicted.get("breaking", False)
    actual_breaking = ground_truth["is_breaking"]

    # Correctness scoring
    if predicted_breaking and actual_breaking:
        # True positive: correctly identified breaking change
        score += 1.0
        breakdown["tp"] = 1

        # Bonus for correct severity on breaking changes
        predicted_severity = predicted.get("severity", "none")
        actual_severity = ground_truth["severity"]
        if predicted_severity == actual_severity:
            score += 0.5
            breakdown["severity_bonus"] = 1
    elif not predicted_breaking and not actual_breaking:
        # True negative: correctly identified non-breaking change
        score += 1.0
        breakdown["tn"] = 1
    elif predicted_breaking and not actual_breaking:
        # False positive: incorrectly flagged as breaking
        score -= 0.5
        breakdown["fp"] = 1
    elif not predicted_breaking and actual_breaking:
        # False negative: missed a breaking change (dangerous!)
        score -= 2.0
        breakdown["fn"] = 1

    return score, breakdown


def evaluate():
    """Run evaluation against all changes."""
    print("Loading schema_changes.json...")
    changes = load_changes()
    print(f"Loaded {len(changes)} schema changes")

    print("\nImporting check_rules.is_breaking_change...")
    try:
        from check_rules import is_breaking_change
    except ImportError as e:
        print(f"Error: Could not import check_rules. {e}")
        sys.exit(1)

    # Anti-cheating check
    import check_rules
    if check_source_for_cheating(check_rules):
        sys.exit(1)

    print("Starting evaluation...\n")

    total_score = 0.0
    all_breakdown = {
        "tp": 0, "tn": 0, "fp": 0, "fn": 0, "severity_bonus": 0
    }

    for i, change in enumerate(changes):
        # Sanitize to prevent cheating
        sanitized = sanitize_change(change)

        try:
            result = is_breaking_change(sanitized)
        except Exception as e:
            print(f"Error on change {i} ({change['change_id']}): {e}")
            sys.exit(1)

        # Validate result
        if not isinstance(result, dict):
            print(f"Error: is_breaking_change must return dict, got {type(result)}")
            sys.exit(1)
        if "breaking" not in result or "severity" not in result or "reason" not in result:
            print(f"Error: result must have 'breaking', 'severity', 'reason'. Got: {result.keys()}")
            sys.exit(1)

        score, breakdown = score_result(result, change, change["change_type"])
        total_score += score

        for key in all_breakdown:
            all_breakdown[key] += breakdown[key]

        # Progress
        if (i + 1) % 20 == 0:
            print(f"Processed {i + 1}/{len(changes)} changes...")

    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Total Score: {total_score:.1f}")
    print(f"  True Positives (TP):      {all_breakdown['tp']} (+1 each)")
    print(f"  True Negatives (TN):      {all_breakdown['tn']} (+1 each)")
    print(f"  False Positives (FP):     {all_breakdown['fp']} (-0.5 each)")
    print(f"  False Negatives (FN):     {all_breakdown['fn']} (-2 each)")
    print(f"  Severity Bonuses:         {all_breakdown['severity_bonus']} (+0.5 each)")
    print("="*60)

    # Improvement vs baseline
    # Baseline: always return breaking=False
    # This gets: TN=45, FN=55 -> score = 45*1 + 55*(-2) = 45 - 110 = -65
    baseline_score = -65
    improvement = total_score - baseline_score
    improvement_pct = (improvement / abs(baseline_score)) * 100 if baseline_score != 0 else 0

    print(f"\nBaseline score (always non-breaking): {baseline_score:.1f}")
    print(f"Your score: {total_score:.1f}")
    print(f"Improvement: {improvement:+.1f} ({improvement_pct:+.1f}%)")
    print("\n" + "="*60)
    print(f"RESULT: detection_score={total_score:.1f} improvement_pct={improvement_pct:.1f}")
    print("="*60)


def baseline():
    """Show what the baseline achieves."""
    print("Baseline: always return breaking=False")
    print("\nWith 55 breaking and 45 non-breaking changes:")
    print("  - All 45 non-breaking correctly identified (TN): +45")
    print("  - All 55 breaking missed (FN):                   -110")
    print("  - Total: 45 - 110 = -65")
    print("\nYour job is to do better than -65!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "baseline":
        baseline()
    elif command == "evaluate":
        evaluate()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
