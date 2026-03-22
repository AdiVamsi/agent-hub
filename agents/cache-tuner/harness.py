#!/usr/bin/env python3
"""Cache Tuner - Harness.

Simulates a cache with configurable eviction policies.

Loads:
  - access_trace.json: list of cache requests
  - cache_config.json: max_capacity_bytes, max_items

Imports:
  - CachePolicy from eviction_policy.py

Replays the trace and tracks hit/miss rate with anti-gaming checks.
"""

import json
import sys
import inspect
from eviction_policy import CachePolicy


class CacheSimulator:
    """Simulates a cache with configurable eviction policy."""

    def __init__(self, config, policy):
        """Initialize simulator.

        Args:
            config: dict with max_capacity_bytes, max_items
            policy: CachePolicy instance
        """
        self.config = config
        self.policy = policy
        self.cache = {}  # {key: {"size": int, "last_access": int, "access_count": int, "category": str}}
        self.current_bytes = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.policy.on_init(config)

    def access(self, request):
        """Process a single cache access request.

        Args:
            request: dict with key, timestamp_ms, object_size_bytes, category
        """
        key = request["key"]
        size = request["object_size_bytes"]
        timestamp = request["timestamp_ms"]
        category = request["category"]

        # Check if in cache
        if key in self.cache:
            self.hits += 1
            # Update access stats
            self.cache[key]["last_access"] = timestamp
            self.cache[key]["access_count"] += 1
            return

        # Cache miss
        self.misses += 1

        # Ask policy whether to cache this item
        should_cache = self.policy.on_access(key, size, timestamp, category)
        if not should_cache:
            return

        # Evict until there's space for this item
        while (self.current_bytes + size > self.config["max_capacity_bytes"] or
               len(self.cache) >= self.config["max_items"]):

            evict_key = self.policy.on_evict(self.cache)

            # Anti-gaming check: must be in cache
            if evict_key not in self.cache:
                raise ValueError(f"ERROR: on_evict returned key '{evict_key}' not in cache")

            evicted_size = self.cache[evict_key]["size"]
            del self.cache[evict_key]
            self.current_bytes -= evicted_size
            self.evictions += 1

        # Add to cache
        self.cache[key] = {
            "size": size,
            "last_access": timestamp,
            "access_count": 1,
            "category": category
        }
        self.current_bytes += size

        # Notify policy of new insertion (for FIFO/insertion-order tracking)
        if hasattr(self.policy, 'record_insertion'):
            self.policy.record_insertion(key)

    def replay_trace(self, trace):
        """Replay access trace through simulator.

        Args:
            trace: list of request dicts
        """
        for request in trace:
            self.access(request)

    def hit_rate(self):
        """Return hit rate (hits / total requests)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

    def summary(self):
        """Return summary stats."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": self.hit_rate(),
            "cache_bytes": self.current_bytes,
            "cache_items": len(self.cache)
        }


def load_baseline_results():
    """Load baseline (FIFO) results from disk, or compute if missing."""
    try:
        with open("baseline_results.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Run baseline to establish it
        print("Computing baseline FIFO hit rate...")
        return None


def validate_policy(policy_code):
    """Anti-gaming checks on policy source code.

    Args:
        policy_code: source code of eviction_policy.py

    Raises:
        ValueError if policy tries to cheat
    """
    # Check 1: Policy should not read access_trace.json directly
    # But allow mentions in docstrings and comments
    lines = policy_code.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip docstrings and comments
        if stripped.startswith("#") or '"""' in line or "'''" in line:
            continue
        # Check for actual file opens
        if "open(" in stripped and "access_trace" in stripped:
            raise ValueError("ERROR: Policy cannot read access_trace.json directly")

    # Check 2: Policy should not read cache_config.json directly
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") or '"""' in line or "'''" in line:
            continue
        if "open(" in stripped and "cache_config" in stripped:
            raise ValueError("ERROR: Policy cannot read cache_config.json directly")


def main():
    """Main entry point."""
    import os

    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        sys.exit(1)

    command = sys.argv[1]

    # Load data
    try:
        with open("access_trace.json", "r") as f:
            trace = json.load(f)
        with open("cache_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError as e:
        print(f"ERROR: {e} — run 'python prepare.py generate' first")
        sys.exit(1)

    # Validate policy
    with open("eviction_policy.py", "r") as f:
        policy_code = f.read()
    validate_policy(policy_code)

    # Create policy
    policy = CachePolicy()

    # Validate policy interface
    if not hasattr(policy, "on_init"):
        raise ValueError("ERROR: CachePolicy must have on_init method")
    if not hasattr(policy, "on_access"):
        raise ValueError("ERROR: CachePolicy must have on_access method")
    if not hasattr(policy, "on_evict"):
        raise ValueError("ERROR: CachePolicy must have on_evict method")

    if command == "baseline":
        print("=" * 60)
        print("BASELINE: FIFO Eviction (oldest inserted first)")
        print("=" * 60)
        sim = CacheSimulator(config, policy)
        sim.replay_trace(trace)
        stats = sim.summary()

        print(f"\nHits:      {stats['hits']}")
        print(f"Misses:    {stats['misses']}")
        print(f"Evictions: {stats['evictions']}")
        print(f"Cache usage: {stats['cache_bytes']/1000:.0f}KB / {config['max_capacity_bytes']/1000:.0f}KB")
        print(f"Cache items: {stats['cache_items']} / {config['max_items']}")
        print(f"\nRESULT: hit_rate={stats['hit_rate']:.4f}")

        # Save baseline
        with open("baseline_results.json", "w") as f:
            json.dump(stats, f, indent=2)
        print("\nBaseline saved to baseline_results.json")

    elif command == "evaluate":
        # Load baseline for comparison
        baseline = load_baseline_results()
        if baseline is None:
            print("Computing baseline first...")
            os.system("python harness.py baseline")
            with open("baseline_results.json", "r") as f:
                baseline = json.load(f)

        print("=" * 60)
        print("EVALUATION: Current Policy")
        print("=" * 60)
        sim = CacheSimulator(config, policy)
        sim.replay_trace(trace)
        stats = sim.summary()

        print(f"\nHits:      {stats['hits']}")
        print(f"Misses:    {stats['misses']}")
        print(f"Evictions: {stats['evictions']}")
        print(f"Cache usage: {stats['cache_bytes']/1000:.0f}KB / {config['max_capacity_bytes']/1000:.0f}KB")
        print(f"Cache items: {stats['cache_items']} / {config['max_items']}")

        improvement = (stats['hit_rate'] - baseline['hit_rate']) / baseline['hit_rate'] * 100
        print(f"\nBaseline hit_rate:  {baseline['hit_rate']:.4f}")
        print(f"Current hit_rate:   {stats['hit_rate']:.4f}")
        print(f"RESULT: hit_rate={stats['hit_rate']:.4f} improvement_pct={improvement:.1f}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
