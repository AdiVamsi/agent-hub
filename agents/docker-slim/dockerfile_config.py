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
    return {
        "remove": [],
        "replace": {},
        "multi_stage": False,
    }
