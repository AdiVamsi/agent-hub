"""Harness for evaluating regex patterns against validation set.

Loads validation_set.json, tests patterns from patterns.py against it,
and reports accuracy metrics.
"""
import json
import re
import sys
from pathlib import Path


def load_validation_set():
    """Load validation_set.json."""
    validation_path = Path(__file__).parent / "validation_set.json"
    with open(validation_path, "r") as f:
        return json.load(f)


def validate_patterns_source():
    """Anti-gaming: verify patterns.py doesn't hardcode test strings."""
    patterns_path = Path(__file__).parent / "patterns.py"
    with open(patterns_path, "r") as f:
        source = f.read()

    # Check for suspicious hardcoding in actual patterns, not docstrings
    # Extract only PATTERNS dict definition
    patterns_start = source.find("PATTERNS = {")
    patterns_end = source.find("}", patterns_start) + 1
    if patterns_start >= 0 and patterns_end > patterns_start:
        patterns_section = source[patterns_start:patterns_end]
        if "validation_set" in patterns_section:
            raise RuntimeError(
                "ERROR: patterns.py PATTERNS dict contains 'validation_set' reference. "
                "Patterns must be general regex, not hardcoded for test cases."
            )

    # Check for common test strings
    suspicious_strings = [
        "example.com", "555-123", "192.168", "2024-01", "localhost"
    ]
    for test_str in suspicious_strings:
        if test_str in source and "PATTERNS" in source:
            line_num = source.split('\n').index([l for l in source.split('\n') if test_str in l][0]) + 1
            # Allow in comments/docstrings, check if in actual pattern
            context_start = max(0, source.find(test_str) - 100)
            context = source[context_start:source.find(test_str) + 100]
            if 'PATTERNS' in context or 'r"' in context or "r'" in context:
                print(f"WARNING: Potential hardcoded test string '{test_str}' near patterns definition")


def validate_pattern_compilation(patterns):
    """Anti-gaming: verify each pattern compiles as valid regex."""
    for pattern_type, pattern_str in patterns.items():
        try:
            re.compile(pattern_str)
        except re.error as e:
            raise RuntimeError(
                f"ERROR: Pattern for '{pattern_type}' is invalid regex: {e}"
            )


def evaluate(baseline=False):
    """Evaluate patterns against validation set.

    Returns: (overall_accuracy, per_type_accuracy, baseline_accuracy)
    """
    # Load validation set
    validation_set = load_validation_set()

    # Import patterns
    from patterns import match, PATTERNS

    # Validate source
    validate_patterns_source()
    validate_pattern_compilation(PATTERNS)

    # Test each case
    results = {ptype: {"correct": 0, "total": 0} for ptype in PATTERNS.keys()}
    all_correct = 0
    all_total = 0

    for test in validation_set:
        pattern_type = test["pattern_type"]
        input_string = test["input_string"]
        expected_match = test["expected_match"]

        predicted_match = match(pattern_type, input_string)
        is_correct = predicted_match == expected_match

        results[pattern_type]["total"] += 1
        if is_correct:
            results[pattern_type]["correct"] += 1
            all_correct += 1
        else:
            # Print failures for debugging
            if not baseline:
                status = "MISS" if expected_match else "FALSE_POS"
                print(f"  {status}: {pattern_type} | {input_string!r} "
                      f"(expected={expected_match}, got={predicted_match})")

        all_total += 1

    # Compute accuracies
    overall_accuracy = all_correct / all_total if all_total > 0 else 0.0

    per_type = {}
    for ptype in sorted(PATTERNS.keys()):
        correct = results[ptype]["correct"]
        total = results[ptype]["total"]
        acc = correct / total if total > 0 else 0.0
        per_type[ptype] = acc
        print(f"{ptype:12s}: {correct:3d}/{total:3d} = {acc:.4f}")

    print(f"\n{'OVERALL':12s}: {all_correct:3d}/{all_total:3d} = {overall_accuracy:.4f}")

    return overall_accuracy, per_type


def compute_baseline():
    """Compute baseline accuracy with simple patterns."""
    from patterns import PATTERNS as BASELINE_PATTERNS

    # Temporarily override with simple baseline patterns
    baseline_patterns = {
        "email": r".+@.+",
        "phone_us": r"\d{3}-\d{3}-\d{4}",
        "ipv4": r"\d+\.\d+\.\d+\.\d+",
        "date_iso": r"\d{4}-\d{2}-\d{2}",
        "url": r"https?://.+",
        "semver": r"\d+\.\d+\.\d+",
    }

    validation_set = load_validation_set()

    all_correct = 0
    all_total = 0

    for test in validation_set:
        pattern_type = test["pattern_type"]
        input_string = test["input_string"]
        expected_match = test["expected_match"]

        pattern_str = baseline_patterns.get(pattern_type)
        if not pattern_str:
            predicted_match = False
        else:
            try:
                predicted_match = bool(re.fullmatch(pattern_str, input_string.strip()))
            except re.error:
                predicted_match = False

        if predicted_match == expected_match:
            all_correct += 1

        all_total += 1

    return all_correct / all_total if all_total > 0 else 0.0


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "baseline":
        print("BASELINE PATTERNS")
        print("=" * 60)
        baseline_acc = compute_baseline()
        print(f"\nBASELINE OVERALL: {baseline_acc:.4f}")

    else:
        print("EVALUATING CURRENT PATTERNS")
        print("=" * 60)
        print()

        overall_accuracy, per_type = evaluate(baseline=False)

        print()
        improvement_pct = 0.0  # Will be set if comparing to baseline
        baseline_acc = compute_baseline()
        if baseline_acc > 0:
            improvement_pct = ((overall_accuracy - baseline_acc) / baseline_acc) * 100

        print(f"RESULT: accuracy={overall_accuracy:.4f} improvement_pct={improvement_pct:.1f}")


if __name__ == "__main__":
    main()
