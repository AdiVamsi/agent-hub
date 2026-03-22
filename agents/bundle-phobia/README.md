# Bundle Phobia

Optimize JavaScript bundle configuration to minimize total bundle size while keeping all features functional.

## Problem

JavaScript bundles are getting larger. A typical modern web app includes:
- React + React-DOM (80KB)
- Build tools & loaders (100KB)
- UI libraries (100-200KB)
- Utility libraries (100-300KB)
- Polyfills & legacy support (50-100KB)
- Unused code (30-50%)

**Result**: 1-3MB bundles that slow down page load, hurt SEO, and drain mobile battery.

## Solution

Bundle Phobia uses automated analysis to:
1. **Replace** heavy libraries with lighter alternatives (moment → dayjs: 92% smaller)
2. **Tree-shake** only used exports from utility libraries (lodash: 50-60% reduction)
3. **Code-split** large visualization libs to async chunks (d3, chart.js)
4. **Remove** unused dependencies and polyfills

Expected outcome: **60-70% bundle size reduction** (1.5MB → 400-500KB).

## How It Works

### 1. Prepare
```bash
python prepare.py generate
```
Generates `dependency_graph.json` with 60 realistic modules (React, Lodash, Moment, D3, etc.), their sizes, dependencies, and available alternatives.

### 2. Optimize
Edit `bundle_config.py` and implement the `optimize_bundle(modules)` function. Return a config dict:

```python
def optimize_bundle(modules: list[dict]) -> dict:
    return {
        "replacements": {"moment": "dayjs", "lodash": "lodash-es"},
        "tree_shake": ["lodash-es", "date-fns", "ramda"],
        "code_split": ["d3", "chart.js", "plotly"],
        "remove": ["jest", "mocha", "unused-polyfill"]
    }
```

Each operation is validated:
- **Replacements**: Alternative must exist and have enough exports
- **Tree-shaking**: Only for tree-shakeable modules without side effects
- **Code-splitting**: Module can't be imported by >3 other modules (too entangled)
- **Removals**: No active module can depend on removed module

Invalid operations incur +50KB penalty each.

### 3. Evaluate
```bash
python harness.py
```
Applies your config to the dependency graph and reports:
```
Baseline bundle size: 1456.2KB (60 modules)

Applying optimizations:
  ✓ Replaced moment -> dayjs
  ✓ Tree-shook lodash-es (45% utilization)
  ✓ Code-split d3 (added 48.0KB async chunk)
  ✓ Removed jest

RESULT: bundle_size_kb=523.4 improvement_pct=64.1
```

## Competitors

- **Bundlephobia.com**: Free, online, but manual analysis per package
- **webpack-bundle-analyzer**: Free, but requires webpack integration and manual optimization decisions
- **Packtracker**: $49/mo, CI/CD integration, tracks over time

## Use Case: Upload Your Real Bundle

Coming soon to **agent-hub.dev**: Upload your `package.json` or bundle analysis, and Bundle Phobia will:
- Scan your actual dependency tree
- Recommend replacements and removals
- Suggest code-split opportunities
- Show estimated size savings
- Generate an optimized bundle config

## Example Optimizations

| Operation | Savings |
|-----------|---------|
| Replace moment → dayjs | ~63 KB |
| Replace lodash → lodash-es + tree-shake | ~45 KB |
| Remove jest + mocha | ~213 KB |
| Code-split d3 + chart.js + plotly | ~400 KB from main (80-100 KB net) |
| Tree-shake all eligible modules | ~80-120 KB |
| **Total potential** | **~600-800 KB (60-70% reduction)** |

---

## Files

- `prepare.py`: Generate dependency graph with 60 modules
- `bundle_config.py`: Your editable optimization strategy
- `harness.py`: Validator and bundle size calculator
- `program.md`: Research hypotheses for bundle optimization
- `README.md`: This file
- `pyproject.toml`: Project metadata (no external dependencies)
