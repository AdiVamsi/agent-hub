# Bundle Phobia Research Program

Hypotheses for minimizing JavaScript bundle size while maintaining functionality:

## H1: Replace Moment.js with Day.js
**Rationale**: Moment.js (68KB) is notoriously heavy. Day.js (5KB) provides 90% of the same API with 92% size reduction.
**Expected Impact**: ~63KB savings

## H2: Replace Lodash with Lodash-ES + Tree Shake
**Rationale**: Lodash (72KB) ships as CommonJS. Lodash-ES (72KB) is ESM with proper tree-shaking support. Combined with tree-shaking, unused functions are eliminated.
**Expected Impact**: ~35-45KB savings (50-60% of lodash-es removed via tree-shaking)

## H3: Tree Shake All Eligible Modules
**Rationale**: Many utility libraries (date-fns, ramda, recharts) are tree-shakeable and only partially used. Reducing to actual exports_used/total_exports ratio compounds savings.
**Expected Impact**: ~80-120KB across all modules

## H4: Code-Split Large Visualization Libraries
**Rationale**: D3 (240KB), Chart.js (165KB), Plotly (250KB) are heavy but often lazy-loaded. Code-splitting moves them to async chunks with only 20% overhead per module.
**Expected Impact**: ~400KB from main bundle (traded for smaller async chunks, net ~80-100KB added for async overhead)

## H5: Remove Unused Polyfills and Legacy Support
**Rationale**: Unused-polyfill (35KB) and legacy-support (28KB) are often bundled unnecessarily for modern browser targets.
**Expected Impact**: ~63KB savings if safely unused

## H6: Replace Heavy HTTP Clients
**Rationale**: Axios (14KB) can be replaced with isomorphic-fetch (8KB) or Ky (6KB) for 40-57% reduction in HTTP overhead.
**Expected Impact**: ~8KB savings

## H7: Cascade Replacements + Tree Shaking
**Rationale**: Replace moment->dayjs, then replace lodash->lodash-es, then tree-shake both. Replacements reduce size + tree-shaking picks up the remainder.
**Expected Impact**: ~100-130KB compound savings

## H8: Aggressive Code Splitting for Rarely-Imported Modules
**Rationale**: Modules imported by ≤1-2 other modules (e.g., plotly, jest, mocha) are good code-split candidates since they won't entangle many dependencies.
**Expected Impact**: ~200-250KB from main bundle (async overhead ~40-50KB)

## H9: Replace Large UI Libraries with Lighter Alternatives
**Rationale**: Material-UI (145KB) -> Bootstrap (125KB), or Antd (185KB) -> Bootstrap. Bootstrap is smaller and tree-shakeable.
**Expected Impact**: ~20-60KB per replacement

## H10: Remove Testing Frameworks from Production Bundle
**Rationale**: Jest (125KB) and Mocha (88KB) should never be in production bundles. Safe to remove if not imported by app.
**Expected Impact**: ~213KB if both removable

---

## Measurement Strategy
1. **Baseline**: Run harness with empty config to establish 1200-1500KB baseline.
2. **Iterative Hypothesis Testing**: Test each hypothesis individually, then compound promising ones.
3. **Validation**: Ensure no broken imports after removal/replacement operations.
4. **Target**: 300-500KB final (60-70% reduction from baseline).
