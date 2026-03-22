#!/usr/bin/env python3
"""
Generate test_suite.json with 150 realistic test cases.

Each test has:
  - test_id: test_001 to test_150
  - module: one of 8 modules
  - test_type: unit/integration/e2e
  - runtime_ms: realistic durations
  - lines_covered: set of line IDs (e.g., "auth:10")
  - depends_on: list of test_ids (dependencies)
  - flaky_rate: 0.0-0.15 probability
  - last_failed: bool
"""

import json
import random
from pathlib import Path


MODULES = ["auth", "users", "orders", "payments", "inventory", "notifications", "analytics", "admin"]
LINES_PER_MODULE = 100  # 800 total lines across 8 modules


def generate_test_suite(seed=42):
    """Generate 150 test cases with realistic properties."""
    random.seed(seed)
    tests = []

    # Track coverage to ensure good distribution
    coverage_map = {module: set(range(1, LINES_PER_MODULE + 1)) for module in MODULES}

    # Distribute tests: ~50% unit, ~35% integration, ~15% e2e
    test_ids = [f"test_{i:03d}" for i in range(1, 151)]
    random.shuffle(test_ids)

    unit_count = 75
    integration_count = 52
    e2e_count = 23

    unit_tests = test_ids[:unit_count]
    integration_tests = test_ids[unit_count:unit_count + integration_count]
    e2e_tests = test_ids[unit_count + integration_count:]

    # Generate unit tests
    for test_id in unit_tests:
        module = random.choice(MODULES)
        lines = random.sample(range(1, LINES_PER_MODULE + 1), random.randint(5, 15))
        tests.append({
            "test_id": test_id,
            "module": module,
            "test_type": "unit",
            "runtime_ms": random.randint(5, 50),
            "lines_covered": [f"{module}:{line}" for line in lines],
            "depends_on": [],
            "flaky_rate": round(random.uniform(0.0, 0.08), 2),
            "last_failed": random.random() < 0.1,
        })

    # Generate integration tests (depend on 1-3 unit tests)
    for test_id in integration_tests:
        module = random.choice(MODULES)
        lines = random.sample(range(1, LINES_PER_MODULE + 1), random.randint(15, 30))
        dependencies = random.sample(unit_tests, random.randint(1, 3))
        tests.append({
            "test_id": test_id,
            "module": module,
            "test_type": "integration",
            "runtime_ms": random.randint(100, 500),
            "lines_covered": [f"{module}:{line}" for line in lines],
            "depends_on": dependencies,
            "flaky_rate": round(random.uniform(0.02, 0.12), 2),
            "last_failed": random.random() < 0.15,
        })

    # Generate e2e tests (depend on 2-5 integration tests)
    for test_id in e2e_tests:
        module = random.choice(MODULES)
        lines = random.sample(range(1, LINES_PER_MODULE + 1), random.randint(25, 40))
        dependencies = random.sample(integration_tests, random.randint(2, 5))
        tests.append({
            "test_id": test_id,
            "module": module,
            "test_type": "e2e",
            "runtime_ms": random.randint(1000, 5000),
            "lines_covered": [f"{module}:{line}" for line in lines],
            "depends_on": dependencies,
            "flaky_rate": round(random.uniform(0.05, 0.15), 2),
            "last_failed": random.random() < 0.2,
        })

    # Sort by test_id for consistency
    tests.sort(key=lambda t: t["test_id"])

    return tests


def main():
    import sys

    if len(sys.argv) < 2 or sys.argv[1] != "generate":
        print("Usage: python prepare.py generate")
        sys.exit(1)

    tests = generate_test_suite(seed=42)

    # Save to test_suite.json
    output_path = Path(__file__).parent / "test_suite.json"
    with open(output_path, "w") as f:
        json.dump(tests, f, indent=2)

    # Print summary
    total_lines = set()
    for test in tests:
        total_lines.update(test["lines_covered"])

    print(f"Generated {len(tests)} tests")
    print(f"Total unique lines covered: {len(total_lines)}")
    print(f"Saved to {output_path}")

    # Print breakdown
    by_type = {}
    for test in tests:
        t_type = test["test_type"]
        by_type[t_type] = by_type.get(t_type, 0) + 1

    for t_type, count in sorted(by_type.items()):
        print(f"  {t_type}: {count}")


if __name__ == "__main__":
    main()
