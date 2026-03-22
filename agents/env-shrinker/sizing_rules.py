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
    """Return recommended instance type. Baseline: keep current type unchanged."""
    return resource["current_instance_type"]
