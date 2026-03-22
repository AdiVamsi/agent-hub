#!/usr/bin/env python3
"""Harness: Load dependency graph, apply optimizations, calculate bundle size."""

import json
import sys
import copy
from bundle_config import optimize_bundle

def load_dependency_graph(filepath="dependency_graph.json"):
    """Load the dependency graph from JSON."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return data["modules"]

def build_module_map(modules):
    """Build a dict for fast lookups."""
    return {m["module_id"]: m for m in modules}

def count_importers(module_id, modules):
    """Count how many active modules import this module."""
    count = 0
    for m in modules:
        if module_id in m["imports"]:
            count += 1
    return count

def apply_optimizations(modules, config):
    """Apply optimization config and validate operations."""
    modules = copy.deepcopy(modules)  # Deep copy for safety
    module_map = build_module_map(modules)
    invalid_ops = 0

    active_modules = {m["module_id"] for m in modules}

    # 1. Apply replacements
    replacements = config.get("replacements", {})
    for old_id, new_id in replacements.items():
        if old_id not in module_map:
            print(f"  ERROR: Replacement source '{old_id}' not found")
            invalid_ops += 1
            continue

        old_module = module_map[old_id]
        if new_id not in old_module.get("alternatives", {}).values():
            print(f"  ERROR: '{new_id}' is not a valid alternative for '{old_id}'")
            invalid_ops += 1
            continue

        if new_id not in module_map:
            print(f"  ERROR: Replacement target '{new_id}' not found")
            invalid_ops += 1
            continue

        # Validate that new module has same/more exports
        new_module = module_map[new_id]
        if new_module["total_exports"] < old_module["total_exports"]:
            print(f"  ERROR: '{new_id}' has fewer exports than '{old_id}'")
            invalid_ops += 1
            continue

        # Remove old module, replace references
        modules = [m for m in modules if m["module_id"] != old_id]
        active_modules.discard(old_id)

        for m in modules:
            if old_id in m["imports"]:
                m["imports"] = [new_id if x == old_id else x for x in m["imports"]]

        print(f"  ✓ Replaced {old_id} -> {new_id}")

    # Rebuild module_map and active_modules
    module_map = build_module_map(modules)
    active_modules = {m["module_id"] for m in modules}

    # 2. Apply tree shaking
    tree_shake_list = config.get("tree_shake", [])
    for module_id in tree_shake_list:
        if module_id not in module_map:
            print(f"  ERROR: Module '{module_id}' not found for tree-shaking")
            invalid_ops += 1
            continue

        module = module_map[module_id]
        if not module["tree_shakeable"]:
            print(f"  ERROR: Module '{module_id}' is not tree-shakeable")
            invalid_ops += 1
            continue

        if module["has_side_effects"]:
            print(f"  ERROR: Module '{module_id}' has side effects, cannot tree-shake")
            invalid_ops += 1
            continue

        # Reduce size based on exports utilization
        if module["total_exports"] == 0:
            print(f"  SKIP: Module '{module_id}' has 0 total exports, cannot tree-shake")
            continue
        utilization = module["exports_used"] / module["total_exports"]
        module["size_bytes"] = int(module["size_bytes"] * utilization)
        print(f"  ✓ Tree-shook {module_id} ({utilization:.0%} utilization)")

    # 3. Apply code splitting
    code_split_list = config.get("code_split", [])
    async_overhead = 0.20  # 20% overhead per module for async loading

    for module_id in code_split_list:
        if module_id not in module_map:
            print(f"  ERROR: Module '{module_id}' not found for code-splitting")
            invalid_ops += 1
            continue

        module = module_map[module_id]

        # Check if module is imported by many others (too entangled)
        importers = count_importers(module_id, modules)
        if importers > 3:
            print(f"  ERROR: Module '{module_id}' imported by {importers} modules (>3), too entangled for code-splitting")
            invalid_ops += 1
            continue

        # Remove from main bundle entirely — async chunk is loaded on demand
        # The async overhead is the loader stub that stays in the main bundle
        original_size = module["size_bytes"]
        loader_stub_size = int(original_size * async_overhead)  # small stub in main bundle
        modules = [m for m in modules if m["module_id"] != module_id]
        modules.append({
            **module,
            "size_bytes": loader_stub_size,
            "code_split": True
        })
        saved = (original_size - loader_stub_size) / 1024
        print(f"  ✓ Code-split {module_id} (saved {saved:.1f}KB, {loader_stub_size/1024:.1f}KB loader stub remains)")

    # Rebuild module_map
    module_map = build_module_map(modules)
    active_modules = {m["module_id"] for m in modules}

    # 4. Apply removals
    remove_list = config.get("remove", [])
    for module_id in remove_list:
        if module_id not in module_map:
            print(f"  ERROR: Module '{module_id}' not found for removal")
            invalid_ops += 1
            continue

        # Check if any active module imports it
        importers = [m["module_id"] for m in modules if module_id in m["imports"]]
        if importers:
            print(f"  ERROR: Cannot remove '{module_id}' — imported by {importers}")
            invalid_ops += 1
            continue

        modules = [m for m in modules if m["module_id"] != module_id]
        active_modules.discard(module_id)
        print(f"  ✓ Removed {module_id}")

    return modules, invalid_ops

def calculate_bundle_size(modules):
    """Calculate total bundle size in KB."""
    total_bytes = sum(m["size_bytes"] for m in modules)
    return total_bytes / 1024.0

def main():
    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        sys.exit(1)

    command = sys.argv[1]

    # Load dependency graph
    modules = load_dependency_graph()
    baseline_kb = calculate_bundle_size(modules)

    if command == "baseline":
        print(f"Baseline bundle size: {baseline_kb:.1f}KB ({len(modules)} modules)")
        print(f"\nRESULT: bundle_size_kb={baseline_kb:.1f} improvement_pct=0.0")
        return

    elif command == "evaluate":
        print(f"Baseline bundle size: {baseline_kb:.1f}KB ({len(modules)} modules)")
        print()

        # Get config from bundle_config
        config = optimize_bundle(copy.deepcopy(modules))

        if not config or all(not v for v in config.values()):
            print("No optimizations configured. Using baseline.")
            optimized_kb = baseline_kb
            invalid_ops = 0
        else:
            print("Applying optimizations:")
            optimized_modules, invalid_ops = apply_optimizations(modules, config)
            optimized_kb = calculate_bundle_size(optimized_modules)
            penalty_kb = invalid_ops * 50
            if penalty_kb > 0:
                print(f"Invalid operations penalty: +{penalty_kb}KB ({invalid_ops} ops)")
                optimized_kb += penalty_kb

        improvement_pct = ((baseline_kb - optimized_kb) / baseline_kb * 100) if baseline_kb > 0 else 0

        print()
        print(f"RESULT: bundle_size_kb={optimized_kb:.1f} improvement_pct={improvement_pct:.1f}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
