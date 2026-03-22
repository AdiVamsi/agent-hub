"""IaC Lint — editable file.

Available data: infra_resources.json with 80 resources, each having:
  resource_id, resource_type, properties, tags, region, monthly_cost_estimate,
  known_issues (golden answers)

Your job: implement check_resource(resource) returning a list of issue dicts:
  [{"severity": "critical", "category": "security", "rule_id": "S001", "description": "..."}]

The harness compares your findings against known_issues:
  - True positive (found a real issue): +score based on severity
  - False positive (flagged something that isn't an issue): -3 points
  - False negative (missed a real issue): 0 points (no penalty, just missed score)

Metric: compliance_score (sum of TP scores - FP penalties) — HIGHER is better.
Baseline: return empty list (find nothing).
"""


def check_resource(resource: dict) -> list[dict]:
    """Return list of issues found. Baseline: return nothing."""
    return []
