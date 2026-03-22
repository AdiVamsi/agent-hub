# SQL Optimizer — AutoResearch Program

## Problem Statement

SQL queries often execute inefficiently due to anti-patterns like:
- Selecting all columns when only a few are needed (`SELECT *`)
- Missing WHERE clauses leading to full table scans
- Using subqueries instead of JOINs
- OR chains that could be IN() operators
- LIKE queries that bypass indexes
- Unnecessary DISTINCT clauses
- Correlated subqueries in SELECT lists
- Missing LIMIT clauses on large results
- ORDER BY in subqueries that get overridden
- Unindexed predicates

Query execution cost is measured as total cost across all 50 queries in the workload.
**Baseline:** ~50,000-80,000 cost (no optimization)
**Target:** ~5,000-15,000 cost (15-25 experiments worth of improvement)

## Hypothesis Space

### Hypothesis 1: Replace SELECT * with specific columns
**Rationale:** SELECT * penalty is 1.5x. Selecting only needed columns reduces memory and I/O.
**Implementation:** Parse SELECT clause, identify available columns from tables_touched, replace with minimal column list.
**Expected impact:** 20-30% improvement on queries with SELECT *.

### Hypothesis 2: Add LIMIT clauses to large results
**Rationale:** Missing LIMIT on 10k+ row result sets incurs 1.2x penalty. Adding LIMIT 100 or LIMIT 1000 reduces cost.
**Implementation:** If estimated_rows > 10000 and no LIMIT present, append LIMIT 1000.
**Expected impact:** 10-15% improvement on large unordered result sets.

### Hypothesis 3: Convert OR chains to IN() operators
**Rationale:** OR chains like `status = 'A' OR status = 'B'` are harder to index than `status IN ('A', 'B')`.
**Implementation:** Detect OR patterns on same column, merge into IN().
**Expected impact:** 5-10% improvement via better index utilization.

### Hypothesis 4: Convert subqueries to JOINs
**Rationale:** Subqueries with IN() clauses often execute repeatedly. Converting to JOIN is more efficient.
**Implementation:** Detect `WHERE id IN (SELECT id FROM ...)`, convert to JOIN structure.
**Expected impact:** 15-25% improvement on subquery-heavy queries.

### Hypothesis 5: Add WHERE clauses using indexed columns
**Rationale:** Queries without WHERE clauses cause full table scans. Adding indexed predicates enables index usage.
**Implementation:** For large table scans, infer reasonable indexed column constraints (e.g., status = 'active').
**Expected impact:** 30-40% improvement via index utilization.

### Hypothesis 6: Remove unnecessary DISTINCT
**Rationale:** DISTINCT after GROUP BY or with aggregates is redundant (1.3x penalty).
**Implementation:** If query has DISTINCT + GROUP BY or DISTINCT + aggregate, remove DISTINCT.
**Expected impact:** 10-15% improvement on queries with redundant DISTINCT.

### Hypothesis 7: Remove ORDER BY from subqueries
**Rationale:** If subquery result is filtered/aggregated later, ORDER BY is wasted (1.1x penalty).
**Implementation:** Detect ORDER BY inside subquery before WHERE/GROUP/ORDER, remove it.
**Expected impact:** 5-8% improvement on nested query structures.

### Hypothesis 8: Use indexed columns in predicates
**Rationale:** Predicates on unindexed columns (e.g., name, price expressions) bypass indexes (1.5x penalty).
**Implementation:** Rewrite predicates to use indexed columns where possible (e.g., status instead of name).
**Expected impact:** 20-30% improvement on unindexed predicate queries.

## Experimental Design

Each hypothesis is implemented as a transformation in `optimize_query()`.
Transformations are applied in order, generating successive improved versions.
Metric: total_query_cost across all 50 queries (lower is better).

**Evaluation cycle:**
1. Run `python prepare.py generate` to create workload.json
2. Implement hypothesis in rewrite_rules.py
3. Run `python harness.py` to evaluate
4. Record improvement_pct
5. Iterate: combine working hypotheses, test new ones

**Success criteria:**
- 50%+ cost reduction from baseline (improvement_pct >= 50)
- All queries remain semantically equivalent
- No queries have missing table references

## Notes

- Cost estimation is heuristic-based (regex pattern matching), not a real query planner.
- Semantic equivalence is validated by checking table references only.
- Combining multiple hypotheses (e.g., SELECT * removal + LIMIT addition) may yield non-linear improvements.
- Some queries may benefit from domain-specific knowledge (e.g., knowing query intent).
