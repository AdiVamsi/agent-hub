# Docker Slim Agent — Optimization Hypotheses

## Problem
Docker images often contain unnecessary dependencies, build tools, test fixtures, and development dependencies that bloat the final image. The baseline unoptimized image is ~2800MB, but production images should be 200-400MB.

## Objective
Optimize Dockerfile configuration by removing non-essential layers while preserving all runtime functionality and test coverage.

## Hypotheses to Test

### H1: Remove All Dev Dependencies
**Assumption:** pytest, coverage, black, pylint, flake8, jupyter, ipython are only needed during development.
**Action:** Remove all entries with type=dev_dep.
**Expected Impact:** Save ~290MB (25+12+8+10+15+9+150+45+3).
**Validation:** No production runtime dependency breaks.

### H2: Remove Build Tools from Final Stage
**Assumption:** gcc, make, cmake, git, curl are only needed during multi-stage build.
**Action:** Set multi_stage=True, remove gcc, make, cmake, git, curl, downloads, repo_setup.
**Expected Impact:** Save ~295MB (200+15+35+40+8+2+5), plus 15% reduction bonus = ~349MB saved.
**Validation:** Verify required_by chains (numpy, scipy, opencv still in final image).

### H3: Use Smaller Alternatives
**Assumption:** node_modules (full) can be replaced with node_modules_prod (minimal production dependencies).
**Action:** Replace node_modules with node_modules_prod (200MB → 50MB).
**Expected Impact:** Save ~200MB.
**Validation:** frontend_build still works with production deps.

### H4: Aggressive Multi-Stage Build
**Assumption:** Combine H2 + H3: use multi-stage, remove dev deps, use alternatives.
**Action:** multi_stage=True, remove all dev_deps and build_tools, replace node_modules.
**Expected Impact:** Save ~(290+349+200) = ~839MB cumulative.
**Target:** ~1960MB remaining.

### H5: Remove Test Fixtures and Mock Data
**Assumption:** test-fixtures and mock-data are not needed in production (tests run separately).
**Action:** Remove test_tool entries: tests, mock-data, test-fixtures.
**Expected Impact:** Save ~360MB (10+150+200).
**Validation:** Runtime app still works; tests are in build stage only.

### H6: Combine Asset Layers
**Assumption:** Multiple small asset layers can be combined into fewer Docker layers.
**Action:** Set combine_layers=[["node_modules_prod", "webpack"], ["docs", "examples"]].
**Expected Impact:** Save ~10MB in layer metadata; cleaner Dockerfile.
**Note:** Minor impact, mainly organizational.

### H7: Remove Documentation and Examples
**Assumption:** docs, examples, and debug-tools are not needed in production containers.
**Action:** Remove config entries: docs, examples, debug-tools, .git.
**Expected Impact:** Save ~290MB (120+60+30+80).
**Validation:** App functionality unchanged; docs can be served separately.

### H8: Extreme Pruning with Dependency Checking
**Assumption:** Remove everything that's removable_in_prod=True while respecting required_by chains.
**Action:** Remove all removable_in_prod=True entries that have no dependents in production.
**Expected Impact:** Very aggressive — analyze required_by chains carefully.
**Validation:** Must verify no broken dependencies.

## Experiment Order

1. **Test H1 alone:** Remove dev deps → measure baseline reduction.
2. **Test H2 alone:** Multi-stage build → measure with build tools removed.
3. **Test H3 alone:** Replace node_modules → measure alternative impact.
4. **Test H5 alone:** Remove test fixtures → validate test infrastructure is independent.
5. **Test H7 alone:** Remove docs/examples → measure config bloat.
6. **Test H1+H2:** Combine dev removal + multi-stage.
7. **Test H1+H2+H3:** Add alternative replacement.
8. **Test H1+H2+H3+H5:** Remove test fixtures too.
9. **Test H1+H2+H3+H5+H7:** All non-critical removals.
10. **Test H8:** Extreme pruning with dependency validation.

## Success Metrics

- **Baseline:** ~2800MB (no optimization)
- **Conservative:** ~1800MB (remove dev deps only)
- **Moderate:** ~1200MB (remove dev + build tools, multi-stage)
- **Aggressive:** ~600MB (remove dev, build, tests, docs, use alternatives)
- **Optimal Target:** ~200-400MB (full pruning respecting dependencies)

## Constraints

1. **No broken dependencies:** All entries in required_by must be satisfied.
2. **Preserve production runtime:** All entries with removable_in_prod=False must remain.
3. **Multi-stage validation:** Build tools removed from final stage must still satisfy their dependents during build.

## Resources

- app_manifest.json: 40 entries with sizes, types, and dependency chains.
- dockerfile_config.py: Editable configuration file where optimizations are specified.
- harness.py: Validates config, calculates metrics, detects broken dependencies.
