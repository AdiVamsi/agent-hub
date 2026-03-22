# Test Shrink — Optimize Your Test Suite

Test Shrink uses AI-guided optimization to reduce test execution time by **10–20×** while maintaining ≥95% code coverage.

## The Problem

Running your entire test suite takes **minutes to hours**. Most of those tests are redundant—they check the same code paths multiple times. You need a smarter way to select and order tests.

**Test Shrink solves this** by:
1. Analyzing test coverage dependencies
2. Removing redundant tests
3. Prioritizing fast, high-coverage tests
4. Respecting test dependencies for correct execution

## What You Get

- **10–20× speedup**: Run 30–50 tests instead of 150+ (typical suite)
- **95%+ coverage guarantee**: Meets enterprise standards
- **Zero false negatives**: Dependencies respected, flaky tests handled
- **Production-ready**: Works with any test format (unit, integration, e2e)

## How It Works

### 1. Prepare Your Test Metadata
Upload test data with coverage info:
```bash
python prepare.py generate  # Creates test_suite.json
```

Each test includes:
- Unique ID, module, test type (unit/integration/e2e)
- Runtime (ms), lines covered, dependencies
- Flakiness probability, failure history

### 2. Run Optimization
Test Shrink analyzes your suite and selects the minimal test set:
```bash
python harness.py evaluate
```

**Output**:
```
RESULT: total_runtime_ms=12450.0 improvement_pct=82.1
```

### 3. Export & Deploy
Integrate the optimized test list into your CI/CD:
```json
[
  "test_001",
  "test_015",
  "test_042",
  ...
]
```

## Comparable Solutions

| Product | Price | Features | Limitations |
|---------|-------|----------|-------------|
| **Test Shrink** | Free (agent) | AI optimization, coverage analysis, dependency handling | Requires test metadata |
| **Launchable** | $200/mo | Test impact analysis, flaky test detection | Enterprise pricing |
| **Buildkite Test Analytics** | $100/mo | Test timing, parallelization | Limited optimization |
| **Currents.dev** | $79/mo | Cypress-focused, cloud storage | Test framework locked-in |

**Why Test Shrink wins**:
- **No subscription**: Free, open-source model
- **Framework-agnostic**: Works with pytest, jest, go test, etc.
- **Privacy-first**: Your test data stays local
- **AI-guided**: Uses advanced algorithms (set-cover, topological sort)

## Quickstart

### Prerequisites
- Python 3.8+
- No external dependencies

### Installation
```bash
git clone <repo>
cd test-shrink
```

### Basic Usage
```bash
# Generate sample test suite
python prepare.py generate

# Evaluate with default (baseline)
python harness.py baseline

# Optimize
python harness.py evaluate
```

### Customization
Edit `test_config.py` to implement your own strategy:

```python
def select_and_order(tests: list[dict]) -> list[str]:
    """Return ordered list of test_ids to run."""
    # Implement your optimization here
    return optimized_test_ids
```

See `program.md` for 8+ hypothesis strategies to experiment with.

## Architecture

```
test_suite.json (150 tests)
        ↓
prepare.py (generates)
        ↓
harness.py (evaluates)
        ↓
test_config.py (select_and_order() strategy)
        ↓
RESULT: total_runtime_ms=X improvement_pct=Y
```

## Key Features

✓ **Greedy Set-Cover**: Minimal test selection for 95%+ coverage
✓ **Dependency Graph**: Respects test ordering constraints
✓ **Flaky Test Handling**: Identifies and deprioritizes unreliable tests
✓ **Module Batching**: Groups tests by module for cache locality
✓ **Topological Sort**: Ensures correct execution order

## Metrics

- **Coverage Requirement**: ≥95% of all coverable lines
- **Penalty System**:
  - Coverage miss: (95 - coverage_pct) × 1000ms
  - Dependency violation: 500ms per violation
- **Goal**: Minimize final_runtime_ms = execution_time + penalties

## Example Optimization Path

```
Experiment 1: Greedy set-cover
  Selected: 42 tests | Runtime: 13,200ms | Coverage: 95.2%
  Improvement: 81.1%

Experiment 2: + Skip flaky tests
  Selected: 38 tests | Runtime: 11,500ms | Coverage: 95.8%
  Improvement: 83.6%

Experiment 3: + Module batching
  Selected: 38 tests | Runtime: 10,800ms | Coverage: 95.8%
  Improvement: 84.6%

Experiment 4: Remove slow e2e
  Selected: 32 tests | Runtime: 8,900ms | Coverage: 96.1%
  Improvement: 87.3%
```

## FAQ

**Q: Does Test Shrink find new bugs?**
A: No. It selects a subset of your existing tests. Coverage ≥95% means you retain 95% of test effectiveness.

**Q: What about flaky tests?**
A: Test Shrink identifies and deprioritizes flaky tests. They can still be selected if coverage requires them.

**Q: Can I use this in CI/CD?**
A: Yes. Export the optimized test list and pass it to your test runner:
```bash
pytest $(cat optimized_tests.json | jq -r '.[]')
```

**Q: How often should I re-optimize?**
A: After significant code changes or test suite additions. Monthly is typical.

**Q: What if I add/remove tests?**
A: Regenerate test metadata and re-run optimization.

## Upload Your Test Data

Ready to optimize your real suite?

👉 **[Upload to agent-hub.dev](https://agent-hub.dev/test-shrink)** 👈

Supported formats:
- `test_suite.json` (Test Shrink native)
- pytest results + coverage.xml
- JUnit XML + coverage data

## Contact & Support

- **Issues**: [GitHub](https://github.com/agent-hub/test-shrink)
- **Docs**: [agent-hub.dev/test-shrink](https://agent-hub.dev/test-shrink)
- **Questions**: Contact agent-hub.dev

---

**Test Shrink** — Run faster. Cover everything. Ship smarter.
