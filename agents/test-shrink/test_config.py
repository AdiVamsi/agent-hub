"""Test Shrink — editable file.

Available data: test_suite.json with 150 tests, each having:
  test_id, module, test_type, runtime_ms, lines_covered, depends_on,
  flaky_rate, last_failed

Your job: implement select_and_order(tests) returning a list of test_ids
to run, in order. The returned subset must:
  1. Cover at least 95% of all coverable lines (coverage_threshold)
  2. Respect dependency ordering (if A depends on B, B comes first)
  3. Minimize total runtime

The harness calculates:
  - total_runtime_ms: sum of runtime for selected tests
  - coverage_pct: |lines covered by selected| / |all lines|
  - If coverage < 95%: penalty of (95 - coverage) * 1000ms added to runtime
  - Dependency violations: each violation adds 500ms penalty

Metric: total_runtime_ms — LOWER is better.
Baseline: return all tests in original order (no optimization).
"""


def select_and_order(tests: list[dict]) -> list[str]:
    """Return ordered list of test_ids. Baseline: all tests, original order."""
    return [t["test_id"] for t in tests]
