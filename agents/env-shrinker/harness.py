#!/usr/bin/env python3
"""
Harness: Evaluate right-sizing recommendations from sizing_rules.py.

Loads infra_inventory.json, imports right_size(), validates SLA constraints,
and computes total monthly cost and improvement percentage.
"""

import json
import sys
from pathlib import Path


def load_inventory(inventory_file):
    """Load infra_inventory.json."""
    with open(inventory_file, "r") as f:
        return json.load(f)


def evaluate(inventory, right_size_func):
    """
    Evaluate right-sizing recommendations.

    Args:
        inventory: dict with resources and instance_types
        right_size_func: function(resource, instance_types) -> str

    Returns:
        dict with total_monthly_cost, improvement_pct, violations
    """
    resources = inventory["resources"]
    instance_types = inventory["instance_types"]
    baseline_cost = sum(r["monthly_cost_usd"] for r in resources)

    total_cost = 0
    violations = []

    for resource in resources:
        recommended_type = right_size_func(resource, instance_types)

        # Verify recommended type exists in catalog
        if recommended_type not in instance_types:
            violations.append({
                "resource_id": resource["resource_id"],
                "error": f"Instance type '{recommended_type}' not in catalog"
            })
            # Keep original cost on invalid recommendation
            total_cost += resource["monthly_cost_usd"]
            continue

        recommended_specs = instance_types[recommended_type]

        # Validate SLA constraints
        cpu_p99 = resource["cpu_p99_pct"]
        memory_p99 = resource["memory_p99_pct"]
        sla_cpu_headroom = resource["sla_cpu_headroom_pct"]
        sla_memory_headroom = resource["sla_memory_headroom_pct"]
        sla_min_iops = resource["sla_min_iops"]

        vcpu = recommended_specs["vcpu"]
        memory_gb = recommended_specs["memory_gb"]
        iops = recommended_specs["iops"]

        violations_found = False

        # CPU constraint
        if cpu_p99 + sla_cpu_headroom > vcpu * 100:
            violations.append({
                "resource_id": resource["resource_id"],
                "error": f"CPU SLA violated: p99={cpu_p99} + headroom={sla_cpu_headroom} > vcpu*100={vcpu*100}"
            })
            violations_found = True

        # Memory constraint
        if memory_p99 + sla_memory_headroom > memory_gb * 100:
            violations.append({
                "resource_id": resource["resource_id"],
                "error": f"Memory SLA violated: p99={memory_p99} + headroom={sla_memory_headroom} > memory_gb*100={memory_gb*100}"
            })
            violations_found = True

        # IOPS constraint
        if iops < sla_min_iops:
            violations.append({
                "resource_id": resource["resource_id"],
                "error": f"IOPS SLA violated: {iops} < {sla_min_iops}"
            })
            violations_found = True

        if violations_found:
            # Apply $100 penalty for SLA violation (revert to original)
            total_cost += resource["monthly_cost_usd"] + 100
        else:
            # Accept recommendation
            total_cost += recommended_specs["monthly_cost"]

    improvement_pct = ((baseline_cost - total_cost) / baseline_cost) * 100 if baseline_cost > 0 else 0

    return {
        "baseline_monthly_cost": baseline_cost,
        "total_monthly_cost": total_cost,
        "improvement_pct": improvement_pct,
        "violations_count": len(violations),
        "violations": violations,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        sys.exit(1)

    command = sys.argv[1]

    # Find infra_inventory.json in same directory as this script
    script_dir = Path(__file__).parent
    inventory_file = script_dir / "infra_inventory.json"

    if not inventory_file.exists():
        print(f"Error: {inventory_file} not found")
        print("Run: python prepare.py generate")
        sys.exit(1)

    # Load inventory
    inventory = load_inventory(inventory_file)

    if command == "baseline":
        # Evaluate with "keep current" strategy to get true baseline cost
        def _keep_current(resource, instance_types):
            return resource["current_instance_type"]
        result = evaluate(inventory, _keep_current)
        print(f"Baseline monthly cost: ${result['total_monthly_cost']:.2f} ({len(inventory['resources'])} resources)")
        if result['violations_count'] > 0:
            print(f"  ({result['violations_count']} existing SLA violations detected)")
        print(f"RESULT: total_monthly_cost=${result['total_monthly_cost']:.2f} improvement_pct=0.0")

    elif command == "evaluate":
        # Import right_size from sizing_rules
        try:
            from sizing_rules import right_size
        except ImportError:
            print("Error: Could not import right_size from sizing_rules.py")
            sys.exit(1)

        # Get true baseline (keep current, with penalties)
        def _keep_current(resource, instance_types):
            return resource["current_instance_type"]
        baseline_result = evaluate(inventory, _keep_current)
        baseline_cost = baseline_result["total_monthly_cost"]

        # Evaluate agent's recommendations
        result = evaluate(inventory, right_size)
        improvement_pct = ((baseline_cost - result['total_monthly_cost']) / baseline_cost * 100) if baseline_cost > 0 else 0

        print(f"Baseline: ${baseline_cost:.2f}  Optimized: ${result['total_monthly_cost']:.2f}")
        print(f"RESULT: total_monthly_cost=${result['total_monthly_cost']:.2f} "
              f"improvement_pct={improvement_pct:.1f}")

        if result['violations_count'] > 0:
            print(f"\nSLA Violations ({result['violations_count']}):")
            for v in result['violations'][:10]:
                print(f"  {v['resource_id']}: {v['error']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
