"""harness.py — Evaluation harness for prompt tuning.

Loads eval_dataset.json, runs classification, computes metrics.
- Accuracy: correct / total
- Precision per class: TP / (TP + FP)
- Recall per class: TP / (TP + FN)
- F1 per class: 2 * (precision * recall) / (precision + recall)
- Confusion matrix summary
"""

import json
import sys
from pathlib import Path
from prompt_config import classify_text


VALID_LABELS = {"bug_report", "feature_request", "question", "praise", "spam"}


class EvaluationHarness:
    """Evaluation harness for text classification."""

    def __init__(self, dataset_path: str = "eval_dataset.json"):
        """Initialize the harness with a dataset."""
        self.dataset_path = dataset_path
        self.dataset = None
        self.predictions = []
        self.true_labels = []
        self.baseline_accuracy = None

    def load_dataset(self) -> bool:
        """Load evaluation dataset from JSON file."""
        if not Path(self.dataset_path).exists():
            print(f"Error: Dataset file not found: {self.dataset_path}")
            return False

        try:
            with open(self.dataset_path, "r") as f:
                self.dataset = json.load(f)
            print(f"Loaded {len(self.dataset)} examples from {self.dataset_path}")
            return True
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return False

    def compute_baseline(self) -> float:
        """Compute baseline accuracy (always predict majority class)."""
        if not self.dataset:
            return 0.0

        # Majority class is 'bug_report' (30%)
        correct = sum(1 for ex in self.dataset if ex["true_label"] == "bug_report")
        self.baseline_accuracy = correct / len(self.dataset)
        return self.baseline_accuracy

    def evaluate(self) -> bool:
        """Run classification on all examples and compute metrics."""
        if not self.dataset:
            print("Error: No dataset loaded")
            return False

        self.predictions = []
        self.true_labels = []

        print(f"\nEvaluating {len(self.dataset)} examples...")
        for i, example in enumerate(self.dataset):
            text = example["text"]
            true_label = example["true_label"]

            try:
                pred = classify_text(text)

                # Validate prediction
                if pred not in VALID_LABELS:
                    print(
                        f"Error at example {i}: classify_text returned invalid label '{pred}'. "
                        f"Must be one of {VALID_LABELS}"
                    )
                    return False

                self.predictions.append(pred)
                self.true_labels.append(true_label)

            except Exception as e:
                print(f"Error classifying example {i}: {e}")
                return False

        return True

    def compute_metrics(self) -> dict:
        """Compute accuracy, precision, recall, F1 per class."""
        if not self.predictions or not self.true_labels:
            return {}

        # Overall accuracy
        correct = sum(1 for p, t in zip(self.predictions, self.true_labels) if p == t)
        accuracy = correct / len(self.predictions)

        metrics = {
            "classification_accuracy": accuracy,
            "total_examples": len(self.predictions),
            "correct": correct
        }

        # Per-class metrics
        per_class = {}
        for label in VALID_LABELS:
            tp = sum(
                1 for p, t in zip(self.predictions, self.true_labels)
                if p == label and t == label
            )
            fp = sum(
                1 for p, t in zip(self.predictions, self.true_labels)
                if p == label and t != label
            )
            fn = sum(
                1 for p, t in zip(self.predictions, self.true_labels)
                if p != label and t == label
            )

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                2 * (precision * recall) / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )

            per_class[label] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "tp": tp,
                "fp": fp,
                "fn": fn
            }

        metrics["per_class"] = per_class
        return metrics

    def compute_confusion_matrix(self) -> dict:
        """Compute confusion matrix."""
        if not self.predictions or not self.true_labels:
            return {}

        matrix = {}
        for true_label in VALID_LABELS:
            matrix[true_label] = {}
            for pred_label in VALID_LABELS:
                count = sum(
                    1 for p, t in zip(self.predictions, self.true_labels)
                    if t == true_label and p == pred_label
                )
                matrix[true_label][pred_label] = count

        return matrix

    def print_results(self, metrics: dict, confusion_matrix: dict):
        """Print evaluation results."""
        if not metrics:
            print("No metrics to display")
            return

        accuracy = metrics["classification_accuracy"]
        improvement_pct = (
            (accuracy - self.baseline_accuracy) / self.baseline_accuracy * 100
            if self.baseline_accuracy > 0
            else 0.0
        )

        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        print(f"RESULT: classification_accuracy={accuracy:.4f} improvement_pct={improvement_pct:.1f}")
        print(f"Correct: {metrics['correct']} / {metrics['total_examples']}")
        print(f"Baseline accuracy: {self.baseline_accuracy:.4f}")

        print("\n" + "-"*60)
        print("PER-CLASS METRICS")
        print("-"*60)
        for label, stats in metrics["per_class"].items():
            print(f"\n{label}:")
            print(f"  Precision: {stats['precision']:.4f}")
            print(f"  Recall:    {stats['recall']:.4f}")
            print(f"  F1:        {stats['f1']:.4f}")
            print(f"  TP: {stats['tp']}, FP: {stats['fp']}, FN: {stats['fn']}")

        print("\n" + "-"*60)
        print("CONFUSION MATRIX")
        print("-"*60)
        # Header
        labels = sorted(VALID_LABELS)
        header_label = "True \\ Pred"
        print(f"{header_label:<20}", end="")
        for label in labels:
            print(f"{label:<15}", end="")
        print()

        # Rows
        for true_label in labels:
            print(f"{true_label:<20}", end="")
            for pred_label in labels:
                count = confusion_matrix[true_label][pred_label]
                print(f"{count:<15}", end="")
            print()

        print("="*60)

    def run_baseline(self):
        """Run baseline evaluation (always predict majority class)."""
        if not self.load_dataset():
            return

        baseline = self.compute_baseline()
        print(f"\nBaseline accuracy (always predict 'bug_report'): {baseline:.4f}")
        print(f"This is the expected accuracy with default classify_text().")

    def run_evaluate(self):
        """Run full evaluation."""
        if not self.load_dataset():
            return

        self.compute_baseline()

        if not self.evaluate():
            print("Evaluation failed")
            sys.exit(1)

        metrics = self.compute_metrics()
        confusion = self.compute_confusion_matrix()

        self.print_results(metrics, confusion)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        print("  baseline  - Show baseline accuracy")
        print("  evaluate  - Run full evaluation")
        sys.exit(1)

    command = sys.argv[1]
    harness = EvaluationHarness()

    if command == "baseline":
        harness.run_baseline()
    elif command == "evaluate":
        harness.run_evaluate()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
