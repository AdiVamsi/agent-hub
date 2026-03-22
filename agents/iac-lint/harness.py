#!/usr/bin/env python3
"""Harness to evaluate IaC lint compliance rules."""

import json
import sys
from pathlib import Path
from difflib import SequenceMatcher


def load_resources(data_file):
    """Load infra_resources.json."""
    with open(data_file, "r") as f:
        data = json.load(f)
    return data["resources"]


def fuzzy_match(str1: str, str2: str, threshold: float = 0.5) -> bool:
    """Check if two strings are similar enough (fuzzy match)."""
    if not str1 or not str2:
        return False
    ratio = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return ratio >= threshold


def findings_match(finding: dict, known_issue: dict) -> bool:
    """
    Check if a finding matches a known issue.
    Match criteria:
    - Same severity
    - Same category
    - Fuzzy description match (key terms overlap)
    """
    # Severity and category must match exactly
    if finding.get("severity") != known_issue.get("severity"):
        return False
    if finding.get("category") != known_issue.get("category"):
        return False

    # Description: fuzzy match to avoid exact string dependency
    finding_desc = finding.get("description", "").lower()
    known_desc = known_issue.get("description", "").lower()

    # Simple fuzzy: check if key terms (words of length > 2) overlap
    finding_words = set(w for w in finding_desc.split() if len(w) > 2)
    known_words = set(w for w in known_desc.split() if len(w) > 2)

    if not finding_words or not known_words:
        return finding_desc == known_desc

    overlap = len(finding_words & known_words)
    total = len(finding_words | known_words)

    # Require at least 50% term overlap
    return total > 0 and (overlap / total) >= 0.5


def evaluate_resource(resource: dict, findings: list[dict]) -> dict:
    """
    Compare findings against known_issues.
    Returns {true_positives, false_positives, false_negatives, score}
    """
    known_issues = resource.get("known_issues", [])

    tp = 0
    fp = 0
    fn = 0

    matched_known = set()

    # Check each finding
    for finding in findings:
        # Validation: severity and description required
        if not finding.get("severity") or not finding.get("description"):
            fp += 1
            continue

        # Allowed severities
        if finding.get("severity") not in ["critical", "high", "medium", "low"]:
            fp += 1
            continue

        # Try to match against known issues
        found_match = False
        for idx, known_issue in enumerate(known_issues):
            if findings_match(finding, known_issue):
                tp += 1
                matched_known.add(idx)
                found_match = True
                break

        if not found_match:
            fp += 1

    # Unmatched known issues = false negatives
    fn = len(known_issues) - len(matched_known)

    # Scoring
    severity_scores = {"critical": 10, "high": 5, "medium": 2, "low": 1}
    tp_score = sum(
        severity_scores.get(known_issues[i].get("severity"), 0)
        for i in matched_known
    )
    fp_penalty = fp * 3

    score = tp_score - fp_penalty

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "score": score
    }


def evaluate_all(resources: list[dict], check_func) -> dict:
    """Evaluate check function across all resources."""
    total_score = 0.0
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_possible = 0

    for resource in resources:
        findings = check_func(resource)

        # Ensure findings is a list
        if not isinstance(findings, list):
            findings = []

        result = evaluate_resource(resource, findings)

        total_score += result["score"]
        total_tp += result["true_positives"]
        total_fp += result["false_positives"]
        total_fn += result["false_negatives"]
        total_possible += len(resource.get("known_issues", []))

    # Improvement percentage: theoretical max is all issues caught at max severity
    severity_scores = {"critical": 10, "high": 5, "medium": 2, "low": 1}
    theoretical_max = 0
    for resource in resources:
        for issue in resource.get("known_issues", []):
            theoretical_max += severity_scores.get(issue.get("severity"), 0)

    if theoretical_max > 0:
        improvement_pct = (total_score / theoretical_max) * 100
    else:
        improvement_pct = 0.0

    return {
        "compliance_score": round(total_score, 1),
        "improvement_pct": round(improvement_pct, 1),
        "true_positives": total_tp,
        "false_positives": total_fp,
        "false_negatives": total_fn,
        "total_possible_issues": total_possible,
        "theoretical_max": theoretical_max
    }


def main():
    import importlib.util

    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        sys.exit(1)

    command = sys.argv[1]
    agent_dir = Path(__file__).parent

    # Load resources
    resources_file = agent_dir / "infra_resources.json"
    if not resources_file.exists():
        print(f"Error: {resources_file} not found. Run 'python prepare.py generate' first.")
        sys.exit(1)

    resources = load_resources(resources_file)

    if command == "baseline":
        # Baseline: return empty list for everything
        def baseline_check(resource):
            return []

        result = evaluate_all(resources, baseline_check)
        print(f"BASELINE: compliance_score={result['compliance_score']} improvement_pct={result['improvement_pct']}")

    elif command == "evaluate":
        # Load lint_rules.py
        lint_rules_file = agent_dir / "lint_rules.py"
        spec = importlib.util.spec_from_file_location("lint_rules", lint_rules_file)
        lint_rules = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lint_rules)

        result = evaluate_all(resources, lint_rules.check_resource)
        print(f"RESULT: compliance_score={result['compliance_score']} improvement_pct={result['improvement_pct']}")
        print(f"  TP={result['true_positives']} FP={result['false_positives']} FN={result['false_negatives']} out of {result['total_possible_issues']} issues")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
