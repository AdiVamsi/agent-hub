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


def build_dependency_graph(manifest):
    """Build reverse dependency graph: which entries depend on each entry."""
    graph = {}
    for entry in manifest:
        graph[entry["name"]] = []

    for entry in manifest:
        for dependent in entry["required_by"]:
            if dependent in graph:
                graph[entry["name"]].append(dependent)

    return graph


def find_required_entries(manifest, removal_set):
    """Find all entries required to keep (due to dependencies)."""
    graph = build_dependency_graph(manifest)

    # Start with entries that can't be removed (removable_in_prod=False)
    required = set()
    for entry in manifest:
        if not entry["removable_in_prod"]:
            required.add(entry["name"])

    # BFS to find all entries needed by required entries
    queue = list(required)
    while queue:
        current = queue.pop(0)
        current_entry = next(e for e in manifest if e["name"] == current)

        for dep in current_entry.get("required_by", []):
            if dep not in required and dep not in removal_set:
                required.add(dep)
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

    # Apply removals
    for name in config["remove"]:
        if name in result_entries:
            del result_entries[name]

    # Apply replacements: swap size of old with new
    for old_name, new_name in config["replace"].items():
        if old_name in result_entries and new_name in result_entries:
            old_size = result_entries[old_name]["size_mb"]
            new_size = result_entries[new_name]["size_mb"]

            # Copy alternative size to old entry (simulate replacement)
            result_entries[old_name]["size_mb"] = new_size
            result_entries[old_name]["replaced_with"] = new_name

    # Calculate base size
    total_size = sum(e["size_mb"] for e in result_entries.values())

    # Apply multi-stage reduction: 15% reduction for build tools that remain
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
