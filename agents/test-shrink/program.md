# Test Shrink — Research Program

## Objective
Optimize test suite execution order and selection to minimize total runtime while maintaining ≥95% code coverage.

## Key Metrics
- **Primary**: `total_runtime_ms` (lower is better)
- **Constraints**:
  - Coverage ≥ 95% (penalty: (95 - coverage_pct) * 1000ms)
  - Dependency ordering respected (penalty: 500ms per violation)

## Baseline
- **All tests in original order**: ~70,000ms
- **Tests selected**: 150 / 150
- **Coverage**: 100% (800/800 lines)

## Expected Optimized Range
- **Target**: 8,000–15,000ms (15–25× improvement)
- **Tests selected**: 30–50 tests covering 95%+ lines
- **Coverage**: ≥95% (760/800 lines)

## 8+ Hypothesis to Explore

### 1. **Remove Redundant Tests (Set Cover)**
**Insight**: Many tests overlap in line coverage. A small subset can cover 95% of lines.

**Approach**:
- Find minimal set of tests covering ≥95% of all lines using greedy set-cover algorithm
- Prioritize tests with high unique coverage
- Remove tests whose lines are entirely covered by others

**Expected gain**: 60–70% runtime reduction
**Hypothesis order**: First (highest impact)

---

### 2. **Prioritize Fast Unit Tests over E2E**
**Insight**: Unit tests (5–50ms) cover fundamentals. Many e2e tests (1000–5000ms) cover the same lines.

**Approach**:
- For each line, track which tests cover it (unit, integration, e2e)
- Prefer unit tests for coverage when available
- Remove e2e tests that are covered by unit+integration combination

**Expected gain**: 40–50% (e2e tests are expensive)
**Hypothesis order**: Second

---

### 3. **Greedy Set-Cover with Cost Weighting**
**Insight**: Weighted set-cover prioritizes fast tests covering many unique lines.

**Approach**:
- Weight = lines_covered / runtime_ms (coverage efficiency)
- Iteratively pick test with best weight
- Remove selected test's lines from uncovered set
- Repeat until 95% coverage

**Expected gain**: 50–60% improvement
**Hypothesis order**: First alternative

---

### 4. **Topological Sort for Dependency Ordering**
**Insight**: Dependencies must be respected or penalties apply.

**Approach**:
- Build dependency DAG from selected tests
- Apply Kahn's algorithm (topological sort)
- Ensure no violation (dependent runs before dependency)

**Expected gain**: Eliminates 500ms per violation
**Hypothesis order**: Required (not optional)

---

### 5. **Skip Flaky Tests with Low Coverage**
**Insight**: Tests with high flaky_rate (>0.12) and coverage overlap are risk/reward negative.

**Approach**:
- Identify flaky tests (flaky_rate > 0.12)
- Remove if coverage is fully covered by non-flaky tests
- Keep flaky if unique coverage is >5% of remaining

**Expected gain**: 10–15% (few flaky tests survive filtering)
**Hypothesis order**: Fourth

---

### 6. **Module-Based Batching for Cache Locality**
**Insight**: Grouping tests by module exploits CPU cache locality and shared fixtures.

**Approach**:
- Partition selected tests by module
- Sort within module by test_type (unit → integration → e2e)
- Concatenate modules

**Expected gain**: 0–5% (minor, mostly framework-dependent)
**Hypothesis order**: After coverage optimization

---

### 7. **Remove Slow E2E Tests with Redundant Coverage**
**Insight**: E2E tests (1000–5000ms) often verify workflows already covered by unit+integration.

**Approach**:
- Identify e2e tests in selected set
- For each e2e test, check if its lines are covered by unit+integration
- Remove redundant e2e tests

**Expected gain**: 30–40% (if e2e heavy in initial solution)
**Hypothesis order**: Third

---

### 8. **Prioritize Recently Failed Tests**
**Insight**: Tests that failed recently (last_failed=true) should run first for quick feedback.

**Approach**:
- Reorder final selection: recently_failed tests first, then others
- Maintains coverage and dependencies

**Expected gain**: 0% (time metric unchanged, improves feedback time)
**Hypothesis order**: After coverage optimization

---

## Experimentation Plan (15–25 experiments)

| Exp | Strategy | Expected Runtime (ms) | Notes |
|-----|----------|----------------------|-------|
| 0 | Baseline (all tests) | ~70,000 | Control |
| 1 | Greedy set-cover | ~12,000–15,000 | Core algorithm |
| 2 | + Topological sort | ~12,000–15,000 | Respect deps |
| 3 | + Skip flaky | ~10,000–12,000 | Remove noise |
| 4 | + Module batching | ~9,500–11,500 | Cache locality |
| 5 | Remove slow e2e | ~8,000–10,000 | Redundancy pruning |
| 6 | Unit first heuristic | ~11,000–14,000 | Alternative to #1 |
| 7 | Priority heap (weight) | ~9,500–12,000 | Cost optimization |
| ... | Ablations & combinations | 8,000–15,000 | Sensitivity analysis |

## Success Criteria
- **Minimum**: 10× improvement (≤7,000ms) with ≥95% coverage
- **Target**: 15× improvement (≤4,500ms) with ≥95% coverage
- **Stretch**: 20× improvement (≤3,500ms) with ≥96% coverage

## Key Implementation Details

### Data Structure
```python
{
  "test_id": "test_001",
  "module": "auth",
  "test_type": "unit",
  "runtime_ms": 25,
  "lines_covered": ["auth:1", "auth:5", "auth:10"],
  "depends_on": [],
  "flaky_rate": 0.08,
  "last_failed": false
}
```

### Algorithm Pseudocode (Set Cover)
```
uncovered = all_lines
selected = []

while uncovered and coverage < 95%:
  best_test = argmax(test in tests: |test.lines & uncovered| / test.runtime)
  selected.append(best_test)
  uncovered -= best_test.lines

topological_sort(selected)
return selected
```

## Notes
- Complexity: O(n × m) where n=tests, m=lines (manageable for 150 tests, 800 lines)
- Dependency DAG reduces final count to 30–50 tests
- Coverage threshold tuning: 95% chosen for safe margin (true coverage ~98–100%)
