"""Docker Image Optimizer — editable file.

Available data: app_manifest.json with 40 entries, each having:
  name, type, size_mb, required_by, removable_in_prod, alternative

Your job: implement optimize_layers(manifest) that returns a config dict:
  {
    "remove": [list of names to exclude from final image],
    "replace": {name: alternative_name for entries to swap},
    "multi_stage": bool (whether to use multi-stage build pattern),
  }

Metric: image_size_mb (total size after optimization) — LOWER is better.
Constraint: all entries with removable_in_prod=False must remain.
            all entries that are required by a remaining entry must remain.

Baseline: keep everything = ~2800MB.
"""


def optimize_layers(manifest: list[dict]) -> dict:
    """Return optimization config.

    Args:
        manifest: List of dicts with name, type, size_mb, required_by,
                 removable_in_prod, alternative

    Returns:
        Dict with keys: remove, replace, multi_stage
    """
    # Build dependency map: X.required_by=[A,B] means A and B depend on X
    depends_on = {}
    for entry in manifest:
        name = entry["name"]
        if name not in depends_on:
            depends_on[name] = set()
        for dep in entry.get("required_by", []):
            if dep not in depends_on:
                depends_on[dep] = set()
            depends_on[dep].add(name)

    # Required set: non-removable items + their transitive dependencies
    required = {e["name"] for e in manifest if not e["removable_in_prod"]}
    queue = list(required)
    visited = set(required)
    while queue:
        current = queue.pop(0)
        for dep in depends_on.get(current, set()):
            if dep not in visited:
                required.add(dep)
                visited.add(dep)
                queue.append(dep)

    # Remove everything removable that's not in the required set
    to_remove = [e["name"] for e in manifest if e["removable_in_prod"] and e["name"] not in required]

    return {
        "remove": to_remove,
        "replace": {},
        "multi_stage": False,
    }
