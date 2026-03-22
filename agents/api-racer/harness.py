#!/usr/bin/env python3
"""API Racer — harness. Evaluates endpoint configurations."""

import json
import sys
from pathlib import Path

from endpoint_config import optimize_endpoint


def simulate_response_time(endpoint_info: dict, config: dict) -> float:
    """Simulate response time with optimizations applied."""
    # Baseline calculation
    base_time = 5.0
    db_time = endpoint_info["db_queries"] * 15.0
    upstream_time = endpoint_info["upstream_calls"] * 50.0
    payload_time = endpoint_info["avg_payload_bytes"] * 0.001

    response_time = base_time + db_time + upstream_time + payload_time

    # Apply cache optimization
    cache_ttl = config.get("cache_ttl_seconds", 0)
    if cache_ttl > 0 and endpoint_info["cacheable"]:
        # Cache hit ~80% of the time
        response_time = 0.8 * 2.0 + 0.2 * response_time

    # Apply batch optimization
    batch_enabled = config.get("batch_enabled", False)
    if batch_enabled and endpoint_info["db_queries"] > 2:
        db_time *= 0.4  # 60% reduction in db time
        response_time = base_time + db_time + upstream_time + payload_time

    # Apply connection pool optimization
    pool_size = config.get("connection_pool_size", 1)
    if endpoint_info["upstream_calls"] > 0 and pool_size > 1:
        pool_reduction = min(pool_size / 5.0, 0.7)
        upstream_time *= (1.0 - pool_reduction)
        response_time = base_time + db_time + upstream_time + payload_time

    # Apply compression optimization
    compression_enabled = config.get("compression_enabled", False)
    if compression_enabled and endpoint_info["avg_payload_bytes"] > 1000:
        payload_time *= 0.3  # 70% reduction in payload transfer time
        response_time = base_time + db_time + upstream_time + payload_time

    # Penalty for oversized pools
    needed_db_connections = max(1, endpoint_info["db_queries"])
    db_pool_size = config.get("db_pool_size", 1)
    if db_pool_size > 2 * needed_db_connections:
        response_time += db_pool_size * 0.1

    needed_conn_pool = max(1, endpoint_info["upstream_calls"])
    if pool_size > 2 * needed_conn_pool:
        response_time += pool_size * 0.1

    return response_time


def validate_config(config: dict) -> bool:
    """Validate configuration bounds."""
    cache_ttl = config.get("cache_ttl_seconds", 0)
    if not (0 <= cache_ttl <= 3600):
        return False

    conn_pool = config.get("connection_pool_size", 1)
    if not (1 <= conn_pool <= 50):
        return False

    db_pool = config.get("db_pool_size", 1)
    if not (1 <= db_pool <= 20):
        return False

    return True


def baseline(workload: list) -> float:
    """Calculate baseline avg response time (no optimizations)."""
    total_weighted_time = sum(ep["current_p50_ms"] * ep["calls_per_minute"] for ep in workload)
    total_calls = sum(ep["calls_per_minute"] for ep in workload)
    return total_weighted_time / total_calls if total_calls > 0 else 0


def evaluate(workload: list) -> float:
    """Evaluate all endpoints with optimizations."""
    total_weighted_time = 0
    total_calls = 0
    penalty_count = 0

    for endpoint_info in workload:
        config = optimize_endpoint(endpoint_info)

        # Default values if not provided
        if "cache_ttl_seconds" not in config:
            config["cache_ttl_seconds"] = 0
        if "connection_pool_size" not in config:
            config["connection_pool_size"] = 1
        if "db_pool_size" not in config:
            config["db_pool_size"] = 1
        if "batch_enabled" not in config:
            config["batch_enabled"] = False
        if "compression_enabled" not in config:
            config["compression_enabled"] = False
        if "rate_limit_rpm" not in config:
            config["rate_limit_rpm"] = 0

        # Validate and penalize invalid configs
        if not validate_config(config):
            response_time = endpoint_info["current_p50_ms"] + 100
            penalty_count += 1
        else:
            response_time = simulate_response_time(endpoint_info, config)

        total_weighted_time += response_time * endpoint_info["calls_per_minute"]
        total_calls += endpoint_info["calls_per_minute"]

    avg_response_ms = total_weighted_time / total_calls if total_calls > 0 else 0

    if penalty_count > 0:
        print(f"[warning] {penalty_count} endpoints had invalid configs", file=sys.stderr)

    return avg_response_ms


def main():
    workload_file = Path(__file__).parent / "api_workload.json"

    if not workload_file.exists():
        print("Error: api_workload.json not found. Run: python prepare.py generate", file=sys.stderr)
        sys.exit(1)

    with open(workload_file) as f:
        workload = json.load(f)

    if len(sys.argv) > 1 and sys.argv[1] == "evaluate":
        baseline_ms = baseline(workload)
        optimized_ms = evaluate(workload)
        improvement_pct = ((baseline_ms - optimized_ms) / baseline_ms * 100) if baseline_ms > 0 else 0

        print(f"RESULT: avg_response_ms={optimized_ms:.2f} improvement_pct={improvement_pct:.1f}")

    elif len(sys.argv) > 1 and sys.argv[1] == "baseline":
        baseline_ms = baseline(workload)
        print(f"RESULT: baseline_avg_response_ms={baseline_ms:.2f}")

    else:
        print("Usage: python harness.py [baseline|evaluate]")


if __name__ == "__main__":
    main()
