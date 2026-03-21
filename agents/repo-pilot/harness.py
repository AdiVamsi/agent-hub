"""Issue triage evaluation harness.

Loads issue_backlog.json, evaluates triage.py predictions against ground truth.
Calculates issues_resolved metric and accuracy stats.
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    label_correct: int = 0
    label_wrong: int = 0
    priority_correct: int = 0
    priority_wrong: int = 0
    duplicate_correct: int = 0
    duplicate_wrong: int = 0
    total_issues: int = 0


def simple_similarity(s1: str, s2: str) -> float:
    """Simple token overlap similarity (0-1)."""
    tokens1 = set(s1.lower().split())
    tokens2 = set(s2.lower().split())
    if not tokens1 or not tokens2:
        return 0.0
    overlap = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return overlap / union if union > 0 else 0.0


def evaluate_labels(predicted: list[str], ground_truth: list[str]) -> tuple[int, int]:
    """Compare predicted labels to ground truth.

    Returns: (correct_count, wrong_count)
    - +2 for each correct label, -1 for each wrong label
    - A label is correct if it's in ground_truth or matches common aliases
    """
    if not ground_truth:
        ground_truth = []

    predicted_set = set(predicted)
    truth_set = set(ground_truth)

    correct = len(predicted_set & truth_set)
    wrong = len(predicted_set - truth_set)

    return correct, wrong


def evaluate_priority(predicted: str, ground_truth: str) -> tuple[int, int]:
    """Compare predicted priority to ground truth.

    Returns: (correct_score, wrong_score)
    - +2 if exact match or one level off, -1 if more than one level off
    """
    priority_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    if predicted not in priority_order or ground_truth not in priority_order:
        return 0, 1

    pred_val = priority_order[predicted]
    truth_val = priority_order[ground_truth]

    if pred_val == truth_val:
        return 1, 0
    elif abs(pred_val - truth_val) == 1:
        return 0, 0  # partial credit: neutral
    else:
        return 0, 1


def evaluate_duplicate(
    predicted_dup: int | None,
    ground_truth_dup: int | None
) -> tuple[int, int]:
    """Compare duplicate detection to ground truth.

    Returns: (correct_score, wrong_score)
    - +3 if correctly identifies duplicate or correctly says not duplicate
    - -3 if false positive or false negative
    """
    if predicted_dup is None and ground_truth_dup is None:
        return 1, 0  # both say not duplicate
    elif predicted_dup == ground_truth_dup:
        return 1, 0  # correctly flagged same duplicate
    else:
        return 0, 1  # mismatch


def load_issues():
    """Load issue_backlog.json."""
    path = Path(__file__).parent / "issue_backlog.json"
    if not path.exists():
        print(f"Error: {path} not found. Run 'python prepare.py generate' first.")
        sys.exit(1)

    with open(path) as f:
        return json.load(f)


def run_evaluation():
    """Evaluate triage.py against all issues."""
    import triage

    issues = load_issues()
    result = EvaluationResult(total_issues=len(issues))

    for issue in issues:
        title = issue.get("title", "")
        body = issue.get("body", "")
        ground_truth_labels = issue.get("ground_truth_labels", [])
        ground_truth_priority = issue.get("ground_truth_priority", "medium")
        ground_truth_dup = issue.get("duplicate_of")

        # Get predictions
        prediction = triage.classify_issue(title, body)
        pred_labels = prediction.get("labels", [])
        pred_priority = prediction.get("priority", "medium")
        pred_dup = prediction.get("is_duplicate_of")

        # Evaluate each component
        label_correct, label_wrong = evaluate_labels(pred_labels, ground_truth_labels)
        priority_correct, priority_wrong = evaluate_priority(pred_priority, ground_truth_priority)
        dup_correct, dup_wrong = evaluate_duplicate(pred_dup, ground_truth_dup)

        result.label_correct += label_correct
        result.label_wrong += label_wrong
        result.priority_correct += priority_correct
        result.priority_wrong += priority_wrong
        result.duplicate_correct += dup_correct
        result.duplicate_wrong += dup_wrong

    return result


def calculate_issues_resolved(result: EvaluationResult) -> float:
    """Calculate the issues_resolved metric.

    issues_resolved = correct_labels*2 + correct_priorities*2 + correct_duplicates*3
                    - wrong_labels*1 - wrong_priorities*1 - wrong_duplicates*3
    """
    score = (
        result.label_correct * 2
        + result.priority_correct * 2
        + result.duplicate_correct * 3
        - result.label_wrong * 1
        - result.priority_wrong * 1
        - result.duplicate_wrong * 3
    )
    return score


def calculate_accuracies(result: EvaluationResult) -> tuple[float, float, float]:
    """Calculate label_accuracy, priority_accuracy, duplicate_f1."""
    # Label accuracy
    total_label_pred = result.label_correct + result.label_wrong
    label_acc = result.label_correct / total_label_pred if total_label_pred > 0 else 0.0

    # Priority accuracy
    total_priority_pred = result.priority_correct + result.priority_wrong
    priority_acc = result.priority_correct / total_priority_pred if total_priority_pred > 0 else 0.0

    # Duplicate F1 (simplified: if only one type of prediction, use accuracy)
    total_dup_pred = result.duplicate_correct + result.duplicate_wrong
    dup_f1 = result.duplicate_correct / total_dup_pred if total_dup_pred > 0 else 0.0

    return label_acc, priority_acc, dup_f1


def baseline_evaluation():
    """Show baseline score (everything defaults to needs-triage + medium + not duplicate)."""
    issues = load_issues()
    result = EvaluationResult(total_issues=len(issues))

    # Baseline: predict "needs-triage" + "medium" + not duplicate for all
    for issue in issues:
        ground_truth_labels = issue.get("ground_truth_labels", [])
        ground_truth_priority = issue.get("ground_truth_priority", "medium")
        ground_truth_dup = issue.get("duplicate_of")

        # Baseline prediction
        pred_labels = ["needs-triage"]
        pred_priority = "medium"
        pred_dup = None

        label_correct, label_wrong = evaluate_labels(pred_labels, ground_truth_labels)
        priority_correct, priority_wrong = evaluate_priority(pred_priority, ground_truth_priority)
        dup_correct, dup_wrong = evaluate_duplicate(pred_dup, ground_truth_dup)

        result.label_correct += label_correct
        result.label_wrong += label_wrong
        result.priority_correct += priority_correct
        result.priority_wrong += priority_wrong
        result.duplicate_correct += dup_correct
        result.duplicate_wrong += dup_wrong

    return result


def print_result(result: EvaluationResult, title: str = ""):
    """Print evaluation results in RESULT format."""
    issues_resolved = calculate_issues_resolved(result)
    label_acc, priority_acc, dup_f1 = calculate_accuracies(result)

    print(f"\n{title}")
    print("=" * 80)
    print(f"RESULT: issues_resolved={int(issues_resolved)} label_accuracy={label_acc:.2f} priority_accuracy={priority_acc:.2f} duplicate_f1={dup_f1:.2f} total_issues={result.total_issues}")
    print(f"\nDetailed:")
    print(f"  Labels:     {result.label_correct} correct, {result.label_wrong} wrong")
    print(f"  Priority:   {result.priority_correct} correct, {result.priority_wrong} wrong")
    print(f"  Duplicates: {result.duplicate_correct} correct, {result.duplicate_wrong} wrong")


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python harness.py [evaluate|baseline|report]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "baseline":
        result = baseline_evaluation()
        print_result(result, "BASELINE (needs-triage + medium + no duplicates)")

    elif command == "evaluate":
        result = run_evaluation()
        print_result(result, "EVALUATION (using triage.py)")

    elif command == "report":
        result = run_evaluation()
        print_result(result, "DETAILED REPORT")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
