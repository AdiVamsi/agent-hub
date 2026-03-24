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
    """Return ordered list of test_ids.

    Strategy:
    1. Greedy cost-weighted set cover: pick tests by best (new_lines / runtime_ms)
       ratio until ≥95% coverage, then add required dependencies.
    2. Topological sort of selected tests to respect dependency ordering.
    """
    test_map = {t["test_id"]: t for t in tests}

    # Compute total coverable lines
    all_lines: set = set()
    for t in tests:
        all_lines.update(t.get("lines_covered", []))
    target = len(all_lines) * 0.95

    # Greedy set-cover: maximize new_lines / runtime_ms ratio
    covered: set = set()
    selected: set = set()
    remaining = list(tests)

    # Score: unique new lines / runtime_ms (favor cheap tests with most new coverage)
    while len(covered) < target and remaining:
        best = max(
            remaining,
            key=lambda t: len(set(t.get("lines_covered", [])) - covered) / max(t["runtime_ms"], 1),
        )
        new_lines = set(best.get("lines_covered", [])) - covered
        if not new_lines:
            break
        selected.add(best["test_id"])
        covered.update(best.get("lines_covered", []))
        remaining = [t for t in remaining if t["test_id"] not in selected]

    # Iterative pruning: remove slow tests if coverage still met (multiple passes)
    improved = True
    while improved:
        improved = False
        for tid in sorted(list(selected), key=lambda t: -test_map[t]["runtime_ms"]):
            others_covered: set = set()
            for other in selected:
                if other != tid:
                    others_covered.update(test_map[other].get("lines_covered", []))
            if len(others_covered & all_lines) >= target:
                selected.discard(tid)
                improved = True
                break  # restart after each removal

    # Prune: remove expensive tests whose lines are fully covered by others
    # Sort by descending runtime to try removing the slowest first
    for tid in sorted(list(selected), key=lambda t: -test_map[t]["runtime_ms"]):
        lines_t = set(test_map[tid].get("lines_covered", []))
        others_covered = set()
        for other in selected:
            if other != tid:
                others_covered.update(test_map[other].get("lines_covered", []))
        # Check if removing tid still covers ≥95%
        if len(others_covered & all_lines) >= target:
            selected.discard(tid)
            covered = set()
            for s in selected:
                covered.update(test_map[s].get("lines_covered", []))

    # Add dependencies transitively
    def add_deps(tid: str):
        for dep in test_map[tid].get("depends_on", []):
            if dep not in selected and dep in test_map:
                selected.add(dep)
                covered.update(test_map[dep].get("lines_covered", []))
                add_deps(dep)

    for tid in list(selected):
        add_deps(tid)

    # Topological sort of selected tests
    in_degree = {tid: 0 for tid in selected}
    adj = {tid: [] for tid in selected}
    for tid in selected:
        for dep in test_map[tid].get("depends_on", []):
            if dep in selected:
                adj[dep].append(tid)
                in_degree[tid] += 1

    from collections import deque
    queue = deque(tid for tid in selected if in_degree[tid] == 0)
    # Break ties: run fast tests first
    queue = deque(sorted(queue, key=lambda tid: test_map[tid]["runtime_ms"]))
    ordered = []
    while queue:
        tid = queue.popleft()
        ordered.append(tid)
        for nxt in sorted(adj[tid], key=lambda t: test_map[t]["runtime_ms"]):
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)

    # Any selected tests not yet ordered (cycle fallback)
    remaining_sel = [tid for tid in selected if tid not in ordered]
    ordered.extend(sorted(remaining_sel, key=lambda tid: test_map[tid]["runtime_ms"]))

    return ordered
