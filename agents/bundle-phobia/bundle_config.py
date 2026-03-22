"""Bundle Phobia — editable file for optimization strategies.

Available data: dependency_graph.json with 60 modules, each having:
  module_id, size_bytes, imports, exports_used, total_exports,
  tree_shakeable, has_side_effects, alternatives

Your job: implement optimize_bundle(modules) returning a config dict:
  {
    "replacements": {"moment": "dayjs", ...},  # swap modules for smaller alternatives
    "tree_shake": ["lodash-es", ...],  # list of modules to tree-shake
    "code_split": ["d3", ...],  # list of modules to lazy-load (not in main bundle)
    "remove": ["unused-polyfill", ...]  # modules to remove entirely
  }

The harness calculates bundle size:
  - Start with all modules
  - Apply replacements (swap sizes, must keep same exports)
  - Apply tree shaking (reduce to exports_used/total_exports ratio, only if tree_shakeable)
  - Apply code splitting (removed from main bundle, 20% async overhead added)
  - Apply removals (must not break imports — no module can import a removed module)
  - Invalid operations are penalized: +50KB per invalid op

Metric: bundle_size_kb — LOWER is better.
Baseline: return empty config (no optimizations).
"""

def optimize_bundle(modules: list[dict]) -> dict:
    """Return bundle optimization config. Baseline: no optimizations."""
    return {}
