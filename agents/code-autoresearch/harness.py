#!/usr/bin/env python3
"""Benchmark harness for code-autoresearch. DO NOT MODIFY.

Imports target.py, runs a workload, verifies correctness, measures throughput,
and prints a greppable RESULT line.

Usage:
    python harness.py benchmark  — run benchmark, compare to baseline
    python harness.py baseline   — run benchmark and save as baseline
    python harness.py verify     — only run correctness checks, no timing
"""

import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
BASELINE_PATH = ROOT / ".baseline.json"
WORKLOAD_PATH = ROOT / "workload.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def fingerprint(obj) -> str:
    """Create a stable hash of a Python object for correctness checking."""
    serialized = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def load_workload() -> dict:
    with open(WORKLOAD_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Workload generation — deterministic test inputs
# ---------------------------------------------------------------------------


def generate_test_inputs(data: dict, workload: dict) -> list:
    """Generate deterministic inputs for each workload function."""
    import random as _rng_mod
    rng = _rng_mod.Random(123)  # separate seed from data generation

    products = data["products"]
    reviews = data["reviews"]
    orders = data["orders"]
    users = data["users"]

    inputs = []

    for spec in workload["workload"]:
        func_name = spec["function"]
        calls = spec["calls"]

        for i in range(calls):
            if func_name == "search_products":
                # Diverse search queries
                queries = [
                    "premium widget", "electronics device", "budget tool",
                    "compact portable", "professional kit", "smart system",
                    "deluxe set", "ultra gadget", "classic bundle", "modern hub",
                    "heavy-duty station", "lightweight pro", "essential pack",
                    "advanced max", "elite plus", "trending sale popular",
                    "eco friendly", "bestseller new", "limited exclusive",
                    "sports outdoor", "health beauty", "home kitchen garden",
                    "books music office", "pet food toys", "automotive tools",
                ]
                query = queries[i % len(queries)]
                inputs.append({
                    "function": func_name,
                    "args": (query, products),
                    "kwargs": {},
                })

            elif func_name == "get_product_with_reviews":
                pid = rng.randint(0, 999)
                inputs.append({
                    "function": func_name,
                    "args": (pid, products, reviews),
                    "kwargs": {},
                })

            elif func_name == "generate_recommendations":
                user = users[i % len(users)]
                inputs.append({
                    "function": func_name,
                    "args": (user["purchase_history"], products, reviews),
                    "kwargs": {},
                })

            elif func_name == "generate_invoice":
                order = orders[i % len(orders)]
                inputs.append({
                    "function": func_name,
                    "args": (order["items"], products, 0.08),
                    "kwargs": {},
                })

            elif func_name == "analyze_sales":
                inputs.append({
                    "function": func_name,
                    "args": (orders, products),
                    "kwargs": {},
                })

    return inputs


# ---------------------------------------------------------------------------
# Correctness checking
# ---------------------------------------------------------------------------


def run_correctness_check(data: dict, workload: dict) -> tuple[bool, dict]:
    """Run all functions and return fingerprints of their outputs."""
    from target import (search_products, get_product_with_reviews,
                        generate_recommendations, generate_invoice,
                        analyze_sales)

    func_map = {
        "search_products": search_products,
        "get_product_with_reviews": get_product_with_reviews,
        "generate_recommendations": generate_recommendations,
        "generate_invoice": generate_invoice,
        "analyze_sales": analyze_sales,
    }

    inputs = generate_test_inputs(data, workload)
    fingerprints = {}

    for inp in inputs:
        fn = func_map[inp["function"]]
        try:
            result = fn(*inp["args"], **inp["kwargs"])
        except Exception as e:
            print(f"ERROR: {inp['function']} raised {type(e).__name__}: {e}")
            return False, {}

        key = f"{inp['function']}_{len(fingerprints)}"
        fingerprints[key] = fingerprint(result)

    return True, fingerprints


def verify_against_baseline(current_fps: dict) -> tuple[bool, list]:
    """Compare current fingerprints against stored baseline."""
    if not BASELINE_PATH.exists():
        return True, []  # No baseline to compare against

    with open(BASELINE_PATH) as f:
        baseline = json.load(f)

    baseline_fps = baseline.get("fingerprints", {})
    mismatches = []

    for key in baseline_fps:
        if key not in current_fps:
            mismatches.append(f"Missing output: {key}")
        elif current_fps[key] != baseline_fps[key]:
            mismatches.append(
                f"Output changed: {key} "
                f"(baseline={baseline_fps[key]}, current={current_fps[key]})"
            )

    return len(mismatches) == 0, mismatches


# ---------------------------------------------------------------------------
# Benchmarking
# ---------------------------------------------------------------------------


def run_benchmark(data: dict, workload: dict) -> dict:
    """Run the full workload and measure throughput."""
    from target import (search_products, get_product_with_reviews,
                        generate_recommendations, generate_invoice,
                        analyze_sales)

    func_map = {
        "search_products": search_products,
        "get_product_with_reviews": get_product_with_reviews,
        "generate_recommendations": generate_recommendations,
        "generate_invoice": generate_invoice,
        "analyze_sales": analyze_sales,
    }

    inputs = generate_test_inputs(data, workload)
    num_runs = workload.get("benchmark_runs", 3)

    run_results = []
    for run_idx in range(num_runs):
        latencies = []
        t_start = time.perf_counter()

        for inp in inputs:
            fn = func_map[inp["function"]]
            call_start = time.perf_counter()
            fn(*inp["args"], **inp["kwargs"])
            call_end = time.perf_counter()
            latencies.append((call_end - call_start) * 1000)  # ms

        t_end = time.perf_counter()
        elapsed = t_end - t_start
        rps = len(inputs) / elapsed

        latencies.sort()
        p50_idx = len(latencies) // 2
        p99_idx = int(len(latencies) * 0.99)
        p50 = latencies[p50_idx]
        p99 = latencies[min(p99_idx, len(latencies) - 1)]

        run_results.append({
            "rps": rps,
            "p50": p50,
            "p99": p99,
            "elapsed": elapsed,
        })
        print(f"  Run {run_idx + 1}/{num_runs}: {rps:.1f} req/s "
              f"(p50={p50:.2f}ms, p99={p99:.2f}ms, {elapsed:.2f}s)")

    # Take median across runs
    rps_values = [r["rps"] for r in run_results]
    p50_values = [r["p50"] for r in run_results]
    p99_values = [r["p99"] for r in run_results]

    return {
        "requests_per_second": round(statistics.median(rps_values), 2),
        "latency_p50_ms": round(statistics.median(p50_values), 3),
        "latency_p99_ms": round(statistics.median(p99_values), 3),
        "total_calls": len(inputs),
    }


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


def cmd_benchmark():
    """Run benchmark and compare to baseline."""
    from target import generate_sample_data

    print("Generating test data...")
    data = generate_sample_data()

    workload = load_workload()

    # Correctness check first
    print("\nRunning correctness check...")
    ok, fps = run_correctness_check(data, workload)
    if not ok:
        print("\nRESULT: FAILED — correctness check raised errors")
        sys.exit(1)

    correct, mismatches = verify_against_baseline(fps)
    if not correct:
        print("\nCorrectness check FAILED — outputs differ from baseline:")
        for m in mismatches[:10]:
            print(f"  {m}")
        print("\nRESULT: FAILED — correctness check failed")
        sys.exit(1)

    print("Correctness: PASSED")

    # Benchmark
    print(f"\nRunning benchmark ({workload.get('benchmark_runs', 3)} runs)...")
    results = run_benchmark(data, workload)

    # Compare to baseline
    improvement_pct = 0.0
    baseline_rps = None
    if BASELINE_PATH.exists():
        with open(BASELINE_PATH) as f:
            baseline = json.load(f)
        baseline_rps = baseline.get("requests_per_second", 0)
        if baseline_rps > 0:
            improvement_pct = ((results["requests_per_second"] - baseline_rps)
                               / baseline_rps * 100)

    rps = results["requests_per_second"]
    p50 = results["latency_p50_ms"]
    p99 = results["latency_p99_ms"]

    print(f"\n{'='*60}")
    print(f"  BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"  Requests/second:   {rps:.2f}")
    print(f"  Latency p50:       {p50:.3f} ms")
    print(f"  Latency p99:       {p99:.3f} ms")
    if baseline_rps is not None:
        print(f"  Baseline req/s:    {baseline_rps:.2f}")
        print(f"  Improvement:       {improvement_pct:+.1f}%")
    print(f"  Total calls:       {results['total_calls']}")
    print(f"{'='*60}\n")

    print(f"RESULT: requests_per_second={rps:.2f} "
          f"latency_p50_ms={p50:.3f} latency_p99_ms={p99:.3f} "
          f"improvement_pct={improvement_pct:.1f}")


def cmd_baseline():
    """Run benchmark and save as baseline."""
    from target import generate_sample_data

    print("Generating test data...")
    data = generate_sample_data()

    workload = load_workload()

    # Correctness — generate fingerprints
    print("\nGenerating correctness fingerprints...")
    ok, fps = run_correctness_check(data, workload)
    if not ok:
        print("ERROR: Functions raised errors. Fix target.py first.")
        sys.exit(1)

    # Benchmark
    print(f"\nRunning baseline benchmark ({workload.get('benchmark_runs', 3)} runs)...")
    results = run_benchmark(data, workload)

    # Save baseline
    baseline_data = {
        "requests_per_second": results["requests_per_second"],
        "latency_p50_ms": results["latency_p50_ms"],
        "latency_p99_ms": results["latency_p99_ms"],
        "total_calls": results["total_calls"],
        "fingerprints": fps,
    }
    with open(BASELINE_PATH, "w") as f:
        json.dump(baseline_data, f, indent=2)

    rps = results["requests_per_second"]
    p50 = results["latency_p50_ms"]
    p99 = results["latency_p99_ms"]

    print(f"\n{'='*60}")
    print(f"  BASELINE SAVED")
    print(f"{'='*60}")
    print(f"  Requests/second:   {rps:.2f}")
    print(f"  Latency p50:       {p50:.3f} ms")
    print(f"  Latency p99:       {p99:.3f} ms")
    print(f"  Total calls:       {results['total_calls']}")
    print(f"  Fingerprints:      {len(fps)} outputs recorded")
    print(f"  Saved to:          {BASELINE_PATH}")
    print(f"{'='*60}\n")

    print(f"RESULT: requests_per_second={rps:.2f} "
          f"latency_p50_ms={p50:.3f} latency_p99_ms={p99:.3f} "
          f"improvement_pct=0.0")


def cmd_verify():
    """Run correctness checks only, no timing."""
    from target import generate_sample_data

    print("Generating test data...")
    data = generate_sample_data()

    workload = load_workload()

    print("\nRunning correctness check...")
    ok, fps = run_correctness_check(data, workload)
    if not ok:
        print("VERIFY: FAILED — functions raised errors")
        sys.exit(1)

    correct, mismatches = verify_against_baseline(fps)
    if not correct:
        print("VERIFY: FAILED — outputs differ from baseline:")
        for m in mismatches[:10]:
            print(f"  {m}")
        sys.exit(1)

    if not BASELINE_PATH.exists():
        print("VERIFY: PASSED (no baseline to compare — run `harness.py baseline` first)")
    else:
        print(f"VERIFY: PASSED — all {len(fps)} outputs match baseline")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python harness.py [benchmark|baseline|verify]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "benchmark":
        cmd_benchmark()
    elif cmd == "baseline":
        cmd_baseline()
    elif cmd == "verify":
        cmd_verify()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python harness.py [benchmark|baseline|verify]")
        sys.exit(1)
