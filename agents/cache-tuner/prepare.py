#!/usr/bin/env python3
"""Cache Tuner - Data Preparation.

Generates synthetic cache access traces with realistic patterns:
- Zipf distribution (80/20 rule)
- Temporal locality
- Periodic bursts
- Scan patterns
"""

import json
import random
import math
from collections import Counter


def generate_access_trace(num_requests=5000, num_unique_keys=200, seed=42):
    """Generate realistic cache access trace.

    Patterns:
    - Zipf distribution: ~20% of keys get ~80% of accesses
    - Temporal locality: recent keys more likely
    - Periodic bursts: some keys accessed every ~500 requests
    - Scan patterns: sequential access that shouldn't pollute cache
    """
    random.seed(seed)

    # Generate keys with Zipf distribution
    keys = [f"key_{i:03d}" for i in range(num_unique_keys)]

    # Zipf weights: key_i has weight 1/i (heavily skewed)
    zipf_weights = [1.0 / (i + 1) for i in range(num_unique_keys)]
    total_weight = sum(zipf_weights)
    zipf_weights = [w / total_weight for w in zipf_weights]

    # Categories
    categories = ["user_profile", "product_page", "search_result", "session_data", "api_response", "static_asset"]

    # Object sizes (typically smaller objects more frequent)
    def get_size():
        # Skewed: most objects small, some large
        if random.random() < 0.7:
            return random.randint(100, 5000)
        else:
            return random.randint(5000, 50000)

    access_trace = []
    burst_keys = random.sample(keys, max(1, num_unique_keys // 10))  # 10% keys have periodic bursts
    burst_pattern = {key: random.randint(400, 600) for key in burst_keys}  # burst every N requests
    last_burst = {key: 0 for key in burst_keys}

    for request_id in range(num_requests):
        timestamp_ms = request_id * 10  # 10ms between requests

        # Decide which key to access
        # Mix: 70% Zipf, 10% temporal locality (recent), 10% bursts, 10% scans
        rnd = random.random()

        if rnd < 0.70:
            # Zipf distribution
            key = random.choices(keys, weights=zipf_weights)[0]
        elif rnd < 0.80:
            # Temporal locality: access one of recent keys
            recent_keys = keys[:max(1, len(keys) // 5)]  # top 20% most frequently accessed
            key = random.choice(recent_keys)
        elif rnd < 0.90:
            # Periodic bursts
            key = random.choice(burst_keys)
        else:
            # Scan pattern: sequential access
            key = keys[request_id % num_unique_keys]

        # Size depends on category
        category = random.choice(categories)
        if category == "user_profile":
            size = random.randint(1000, 10000)
        elif category == "product_page":
            size = random.randint(5000, 50000)
        elif category == "search_result":
            size = random.randint(2000, 30000)
        elif category == "session_data":
            size = random.randint(100, 2000)
        elif category == "api_response":
            size = random.randint(500, 20000)
        else:  # static_asset
            size = random.randint(100, 5000)

        access_trace.append({
            "request_id": request_id,
            "key": key,
            "timestamp_ms": timestamp_ms,
            "object_size_bytes": size,
            "category": category
        })

    return access_trace


def generate_cache_config():
    """Generate cache configuration.

    Constraints are TIGHT to force eviction decisions:
    - max_capacity_bytes: only 500KB (not enough for all objects)
    - max_items: only 100 items (not enough for all 200 unique keys)
    """
    return {
        "max_capacity_bytes": 500000,
        "max_items": 100
    }


def main():
    import sys

    if len(sys.argv) < 2 or sys.argv[1] != "generate":
        print("Usage: python prepare.py generate")
        sys.exit(1)

    print("Generating access trace with 5000 requests, 200 unique keys...")
    trace = generate_access_trace(num_requests=5000, num_unique_keys=200, seed=42)

    with open("access_trace.json", "w") as f:
        json.dump(trace, f, indent=2)
    print(f"  -> access_trace.json ({len(trace)} events)")

    print("Generating cache configuration...")
    config = generate_cache_config()

    with open("cache_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print(f"  -> cache_config.json (capacity={config['max_capacity_bytes']} bytes, items={config['max_items']})")

    # Print summary
    print("\nData Summary:")
    print(f"  Total requests: {len(trace)}")
    print(f"  Unique keys: {len(set(r['key'] for r in trace))}")
    print(f"  Total data volume: {sum(r['object_size_bytes'] for r in trace) / 1e6:.1f}MB")
    print(f"  Cache capacity: {config['max_capacity_bytes'] / 1e3:.0f}KB (not enough!)")
    print(f"  Max items: {config['max_items']} (not enough for all {len(set(r['key'] for r in trace))} keys)")

    # Zipf check
    key_counts = Counter(r['key'] for r in trace)
    top_20_pct = len(key_counts) // 5
    top_20_count = sum(count for _, count in key_counts.most_common(top_20_pct))
    print(f"  Top 20% keys: {top_20_count}/{len(trace)} accesses ({100*top_20_count/len(trace):.1f}%)")


if __name__ == "__main__":
    main()
