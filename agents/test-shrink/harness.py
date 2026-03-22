#!/usr/bin/env python3
"""
Test harness for test-shrink optimization.

Evaluates test selection and ordering against:
  1. Coverage requirement (>= 95%)
  2. Dependency constraints
  3. Minimized runtime
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, deque


def load_test_suite():
    """Load test_suite.json."""
    suite_path = Path(__file__).parent / "test_suite.json"
    if not suite_path.exists():
        print(f"Error: {suite_path} not found. Run: python prepare.py generate")
        sys.exit(1)

    with open(suite_path, "r") as f:
        return json.load(f)


def get_all_lines(tests):
    """Get set of all coverable lines across all tests."""
    all_lines = set()
    for test in tests:
        all_lines.update(test["lines_covered"])
    return all_lines


def validate_selection(selected_ids, all_tests, all_lines):
    """Validate selected tests and return metrics."""
    test_by_id = {t["test_id"]: t for t in all_tests}

    # Anti-gaming: check all IDs exist
    for test_id in selected_ids:
        if test_id not in test_by_id:
            raise ValueError(f"Invalid test_id: {test_id}")

    # Calculate coverage
    covered_lines = set()
    for test_id in selected_ids:
        covered_lines.update(test_by_id[test_id]["lines_covered"])

    coverage_pct = (len(covered_lines) / len(all_lines)) * 100 if all_lines else 100

    # Check dependency ordering
    order_map = {test_id: i for i, test_id in enumerate(selected_ids)}
    dependency_violations = 0

    for test_id in selected_ids:
        test = test_by_id[test_id]
        test_pos = order_map[test_id]

        for dep_id in test["depends_on"]:
            if dep_id in order_map:
                dep_pos = order_map[dep_id]
                if dep_pos > test_pos:
                    dependency_violations += 1

    # Calculate runtime
    total_runtime = sum(test_by_id[tid]["runtime_ms"] for tid in selected_ids)

    # Apply penalties
    coverage_penalty = 0
    if coverage_pct < 95:
        coverage_penalty = (95 - coverage_pct) * 1000

    dependency_penalty = dependency_violations * 500

    final_runtime = total_runtime + coverage_penalty + dependency_penalty

    return {
        "selected_count": len(selected_ids),
        "total_count": len(all_tests),
        "coverage_pct": round(coverage_pct, 2),
        "coverage_lines": len(covered_lines),
        "total_lines": len(all_lines),
        "total_runtime_ms": total_runtime,
        "coverage_penalty_ms": coverage_penalty,
        "dependency_violations": dependency_violations,
        "dependency_penalty_ms": dependency_penalty,
        "final_runtime_ms": final_runtime,
    }


def topological_sort_reorder(selected_ids, all_tests):
    """Reorder selected tests to respect dependencies (topological sort)."""
    test_by_id = {t["test_id"]: t for t in all_tests}

    # Build dependency graph for selected tests only
    selected_set = set(selected_ids)
    in_degree = defaultdict(int)
    graph = defaultdict(list)

    for test_id in selected_ids:
        test = test_by_id[test_id]
        # Only count dependencies that are in the selected set
        actual_deps = [d for d in test["depends_on"] if d in selected_set]
        in_degree[test_id] = len(actual_deps)
        for dep in actual_deps:
            graph[dep].append(test_id)

    # Topological sort
    queue = deque([tid for tid in selected_ids if in_degree[tid] == 0])
    ordered = []

    while queue:
        test_id = queue.popleft()
        ordered.append(test_id)

        for dependent in graph[test_id]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    return ordered


def evaluate_baseline(tests):
    """Evaluate baseline: all tests, topologically sorted."""
    all_lines = get_all_lines(tests)
    selected_ids = [t["test_id"] for t in tests]
    selected_ids = topological_sort_reorder(selected_ids, tests)
    metrics = validate_selection(selected_ids, tests, all_lines)
    return metrics


def evaluate_solution(tests):
    """Evaluate solution from test_config.select_and_order()."""
    try:
        from test_config import select_and_order
    except ImportError as e:
        print(f"Error importing select_and_order: {e}")
        sys.exit(1)

    all_lines = get_all_lines(tests)

    try:
        selected_ids = select_and_order(tests)
    except Exception as e:
        print(f"Error calling select_and_order: {e}")
        sys.exit(1)

    # Ensure it returns a list
    if not isinstance(selected_ids, list):
        print(f"Error: select_and_order must return a list, got {type(selected_ids)}")
        sys.exit(1)

    # Optionally reorder to respect dependencies
    selected_ids = topological_sort_reorder(selected_ids, tests)

    metrics = validate_selection(selected_ids, tests, all_lines)
    metrics["selected_ids"] = selected_ids
    return metrics


def main():
    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        sys.exit(1)

    command = sys.argv[1]
    tests = load_test_suite()

    if command == "baseline":
        metrics = evaluate_baseline(tests)
        print("\n=== BASELINE ===")
        print(f"Tests selected: {metrics['selected_count']} / {metrics['total_count']}")
        print(f"Coverage: {metrics['coverage_pct']}% ({metrics['coverage_lines']} / {metrics['total_lines']} lines)")
        print(f"Total runtime: {metrics['total_runtime_ms']}ms")
        print(f"RESULT: total_runtime_ms={metrics['final_runtime_ms']:.1f} improvement_pct=0.0")

    elif command == "evaluate":
        baseline_metrics = evaluate_baseline(tests)
        solution_metrics = evaluate_solution(tests)

        print("\n=== SOLUTION ===")
        print(f"Tests selected: {solution_metrics['selected_count']} / {solution_metrics['total_count']}")
        print(f"Coverage: {solution_metrics['coverage_pct']}% ({solution_metrics['coverage_lines']} / {solution_metrics['total_lines']} lines)")
        print(f"Total runtime: {solution_metrics['total_runtime_ms']}ms")
        if solution_metrics.get("coverage_penalty_ms", 0) > 0:
            print(f"  Coverage penalty: {solution_metrics.get('coverage_penalty_ms', 0)}ms")
        if solution_metrics.get("dependency_violations", 0) > 0:
            print(f"  Dependency violations: {solution_metrics.get('dependency_violations', 0)}")
            print(f"  Dependency penalty: {solution_metrics.get('dependency_penalty_ms', 0)}ms")

        improvement_pct = ((baseline_metrics['final_runtime_ms'] - solution_metrics['final_runtime_ms']) /
                          baseline_metrics['final_runtime_ms'] * 100)

        print(f"\nBaseline runtime: {baseline_metrics['final_runtime_ms']:.1f}ms")
        print(f"Solution runtime: {solution_metrics['final_runtime_ms']:.1f}ms")
        print(f"RESULT: total_runtime_ms={solution_metrics['final_runtime_ms']:.1f} improvement_pct={improvement_pct:.1f}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
