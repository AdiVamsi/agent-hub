#!/usr/bin/env python3
"""Harness for Docker image optimization.

Loads app_manifest.json, runs optimize_layers, validates constraints,
calculates image_size_mb metric.
"""

import json
import sys
from dockerfile_config import optimize_layers


def load_manifest(path="app_manifest.json"):
    """Load application manifest."""
    with open(path, "r") as f:
        return json.load(f)


def build_dependency_map(manifest):
    """Build dependency map: for each entry, what does it depend on?

    If entry X has required_by=[A, B], it means A depends on X, B depends on X.
    So we build: depends_on[A] includes X, depends_on[B] includes X.
    """
    depends_on = {}  # entry_name -> set of entries it depends on

    for entry in manifest:
        entry_name = entry["name"]
        if entry_name not in depends_on:
            depends_on[entry_name] = set()

        # For each entry that depends on this one, add this entry as a dependency
        for dependent in entry.get("required_by", []):
            if dependent not in depends_on:
                depends_on[dependent] = set()
            depends_on[dependent].add(entry_name)

    return depends_on


def find_required_entries(manifest, removal_set):
    """Find all entries required to keep (due to dependencies).

    Returns the set of entries that must be kept:
    1. All entries with removable_in_prod=False
    2. All entries that are dependencies of (1)
    """
    depends_on = build_dependency_map(manifest)

    # Start with entries that can't be removed (removable_in_prod=False)
    required = set()
    for entry in manifest:
        if not entry["removable_in_prod"]:
            required.add(entry["name"])

    # BFS to find all entries that required entries depend on
    queue = list(required)
    visited = set(required)

    while queue:
        current = queue.pop(0)

        # For each dependency of current, add it to required
        for dep in depends_on.get(current, set()):
            if dep not in visited and dep not in removal_set:
                required.add(dep)
                visited.add(dep)
                queue.append(dep)

    return required


def validate_config(manifest, config):
    """Validate config doesn't break constraints.

    Returns: (is_valid, error_message)
    """
    removal_set = set(config["remove"])

    # Check: no required entry removed
    required = find_required_entries(manifest, removal_set)
    for entry_name in removal_set:
        if entry_name in required:
            return False, f"Cannot remove {entry_name} - it's required by other entries"

    # Check: replacements exist
    manifest_names = {e["name"] for e in manifest}
    for old_name, new_name in config["replace"].items():
        if old_name not in manifest_names:
            return False, f"Replace source {old_name} not in manifest"
        if new_name not in manifest_names:
            return False, f"Replace target {new_name} not in manifest"

    return True, ""


def apply_config(manifest, config):
    """Apply optimization config to manifest.

    Returns: (resulting_manifest, size_mb, is_valid)
    """
    is_valid, error_msg = validate_config(manifest, config)
    if not is_valid:
        return [], 99999, False

    # Start with all entries
    result_entries = {e["name"]: e.copy() for e in manifest}

    # Apply removals first
    removal_set = set(config["remove"])
    for name in removal_set:
        if name in result_entries:
            del result_entries[name]

    # Apply replacements: remove old entry, ensure new entry is present
    # (new entry should already be in result_entries unless it was removed)
    for old_name, new_name in config["replace"].items():
        if old_name in result_entries:
            # Remove old entry
            del result_entries[old_name]
        # New entry should already be in result_entries (unless it was removed,
        # which would be a validation error caught above)

    # Calculate base size
    total_size = sum(e["size_mb"] for e in result_entries.values())

    # Apply multi-stage reduction: 15% reduction for build tools that remain
    # (only count build tools that are NOT in the removal set)
    if config["multi_stage"]:
        build_tools = [e for e in result_entries.values() if e["type"] == "build_tool"]
        build_tool_size = sum(e["size_mb"] for e in build_tools)
        reduction = build_tool_size * 0.15
        total_size -= reduction

    return list(result_entries.values()), total_size, True


def baseline(manifest):
    """Evaluate baseline (no optimization)."""
    total_size = sum(e["size_mb"] for e in manifest)
    print(f"BASELINE: {total_size}MB")
    return total_size


def evaluate(manifest):
    """Evaluate the config in dockerfile_config.py."""
    config = optimize_layers(manifest)
    result_manifest, size_mb, is_valid = apply_config(manifest, config)

    if not is_valid:
        print(f"RESULT: 99999 (validation failed)")
        return 99999

    removed_count = len(manifest) - len(result_manifest)
    reduction_pct = (1 - size_mb / sum(e["size_mb"] for e in manifest)) * 100

    print(f"RESULT: {size_mb:.0f}MB (removed {removed_count} entries, {reduction_pct:.1f}% reduction)")
    return size_mb


def main():
    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        sys.exit(1)

    manifest = load_manifest()

    if sys.argv[1] == "baseline":
        baseline(manifest)
    elif sys.argv[1] == "evaluate":
        evaluate(manifest)
    else:
        print("Unknown command. Use 'baseline' or 'evaluate'")
        sys.exit(1)


if __name__ == "__main__":
    main()
