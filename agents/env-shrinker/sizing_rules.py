"""
Env Shrinker — Editable File

Available data: infra_inventory.json with 60 resources and instance_types catalog.

Your job: implement right_size(resource, instance_types) -> str
returning the recommended instance_type for this resource.

Constraints (harness checks these):
  - New type must have enough vCPU: cpu_p99 + sla_cpu_headroom <= vcpu * 100
  - New type must have enough memory: memory_p99 + sla_memory_headroom <= memory_gb * 100
  - New type must meet min IOPS
  - Must stay in same instance family prefix (m5 -> m5, r5 -> r5, c5 -> c5, t3 -> t3, etc.)

Metric: total_monthly_cost (sum of all resources after right-sizing) — LOWER is better.
Baseline: return current instance type unchanged.
Strategy: Find the smallest instance type in the same family that meets all SLA constraints.
"""


def right_size(resource: dict, instance_types: dict) -> str:
    """Return the cheapest instance type across ALL families that meets all SLA constraints."""
    current = resource["current_instance_type"]

    # SLA requirements
    cpu_need = resource["cpu_p99_pct"] + resource["sla_cpu_headroom_pct"]
    mem_need = resource["memory_p99_pct"] + resource["sla_memory_headroom_pct"]
    iops_need = resource["sla_min_iops"]

    # Sort all instance types by monthly cost (cheapest first)
    candidates = sorted(instance_types.items(), key=lambda x: x[1]["monthly_cost"])

    # Find cheapest type that meets all constraints
    for itype, specs in candidates:
        vcpu = specs.get("vcpu", 0)
        memory_gb = specs.get("memory_gb", 0)
        iops = specs.get("iops", 0)

        if (cpu_need <= vcpu * 100 and
                mem_need <= memory_gb * 100 and
                iops_need <= iops):
            return itype

    # No valid type found — keep current
    return current
