# SQL Optimizer

Automated SQL query optimization through learned rewrite rules and cost estimation.

## Overview

The SQL Optimizer analyzes workloads of SQL queries and applies intelligent rewriting rules to reduce execution cost. It detects common anti-patterns (SELECT *, missing WHERE clauses, subqueries vs. JOINs, etc.) and suggests optimizations.

## Quick Start

```bash
# Generate test workload (50 queries with anti-patterns)
python prepare.py generate

# Evaluate baseline and optimized queries
python harness.py
```

### Example Output

```
RESULT: total_query_cost=45230.5 improvement_pct=32.4

Baseline cost: 67523.2
Optimized cost: 45230.5
Improvement: 32.42%

Top improvements:
  q011: -5000.3 cost
  q014: -3200.1 cost
  q022: -2100.5 cost
```

## How It Works

### Data Preparation (`prepare.py`)

Generates a realistic workload of 50 SQL queries with:
- **Schema:** users, orders, products, order_items tables
- **Indexes:** On common columns (id, user_id, email, status, created_at, category)
- **Anti-patterns:** SELECT *, subqueries, OR chains, missing WHERE/LIMIT clauses, correlated subqueries, unnecessary DISTINCT
- **Metadata:** rows_scanned, has_index, expected_result_hash for cost estimation

### Query Optimization (`rewrite_rules.py`)

The editable optimization module where you implement `optimize_query(query_info)`.

**Available query metadata:**
- `query_id`: Unique identifier
- `sql`: Original SQL string
- `tables_touched`: List of tables referenced
- `estimated_rows_scanned`: Estimated row count from planner
- `has_index`: Dict mapping table names to indexed columns
- `expected_result_hash`: Hash for correctness validation

**Your implementation must:**
1. Parse or analyze the SQL string
2. Apply rewrite rules that maintain semantic equivalence
3. Return optimized SQL string

### Cost Estimation (`harness.py`)

Simulates a query cost estimator using heuristic rules:

| Factor | Multiplier | Condition |
|--------|-----------|-----------|
| Base cost | 1.0 | Full table scan (estimated_rows * 1.0) |
| Index scan | 0.5 | Has indexes; reduced multiplier |
| SELECT * | ×1.5 | Selecting all columns |
| Correlated subquery | ×2.0 | Per correlated subquery |
| Unnecessary DISTINCT | ×1.3 | DISTINCT after GROUP BY or with aggregates |
| No LIMIT | ×1.2 | Large result set (>10k rows) without LIMIT |
| Unindexed predicate | ×1.5 | WHERE clause uses non-indexed column |
| Unnecessary ORDER BY | ×1.1 | ORDER BY in subquery before filtering |

**Metric:** Lower total_query_cost is better.

## Optimization Hypotheses

8 primary optimization strategies:

1. **Replace SELECT * with specific columns** — Reduce memory/I/O cost (1.5x penalty removal)
2. **Add LIMIT clauses** — Eliminate unnecessary row fetches (1.2x penalty removal)
3. **Convert OR chains to IN()** — Better index utilization
4. **Convert subqueries to JOINs** — Avoid repeated subquery execution
5. **Add WHERE clauses with indexes** — Enable index scans vs. full scans
6. **Remove unnecessary DISTINCT** — Skip redundant deduplication (1.3x penalty removal)
7. **Remove ORDER BY in subqueries** — Avoid wasted sorts (1.1x penalty removal)
8. **Use indexed columns in predicates** — Bypass function penalties (1.5x penalty removal)

See `program.md` for detailed hypothesis space and experimental design.

## Example Optimizations

### Before & After: SELECT *

```sql
-- BEFORE (SELECT * penalty: 1.5x)
SELECT * FROM users WHERE status = 'active'

-- AFTER (only needed columns)
SELECT id, name, email FROM users WHERE status = 'active'
```

### Before & After: Subquery to JOIN

```sql
-- BEFORE (correlated subquery: 2.0x penalty)
SELECT * FROM orders WHERE user_id IN (
  SELECT id FROM users WHERE status = 'active'
)

-- AFTER (JOIN: avoids subquery penalty)
SELECT DISTINCT o.* FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.status = 'active'
```

### Before & After: OR to IN()

```sql
-- BEFORE (OR chains harder to optimize)
SELECT * FROM products
WHERE category = 'electronics' OR category = 'books' OR category = 'toys'

-- AFTER (IN() enables index)
SELECT * FROM products
WHERE category IN ('electronics', 'books', 'toys')
```

## Performance Targets

- **Baseline:** 50,000-80,000 cost (unoptimized queries)
- **Target:** 5,000-15,000 cost (70-90% reduction)
- **Headroom:** 15-25 experiments to reach target

Typical optimizations achieve 30-50% improvement. Combining strategies can exceed 70%.

## Use Cases

- **Query Performance Tuning:** Identify and fix expensive queries
- **Workload Optimization:** Batch rewrite rules for consistency
- **Cost Estimation:** Understand query execution cost distribution
- **Educational:** Learn SQL optimization patterns

## Deployment

**Upload your slow queries to agent-hub.dev for automated optimization.**

Comparable SaaS solutions:
- EverSQL: $59/month
- Aiven SQL Optimizer: $99/month
- pganalyze: $49/month

The SQL Optimizer agent is free, fast, and customizable.

## File Structure

```
sql-optimizer/
├── prepare.py          # Workload generation
├── rewrite_rules.py    # Your optimization logic (editable)
├── harness.py          # Cost estimation and evaluation
├── program.md          # Hypothesis space and experimental design
├── README.md           # This file
└── pyproject.toml      # Project metadata
```

## Architecture

```
prepare.py (generate workload.json)
    ↓
rewrite_rules.py (optimize_query function)
    ↓
harness.py (estimate cost, evaluate)
    ↓
RESULT: total_query_cost, improvement_pct
```

## CLI Usage

```bash
# Generate workload
python prepare.py generate

# Evaluate
python harness.py

# Success: improvement_pct > 30% from baseline
```

## Future Enhancements

- Multi-table histogram statistics for better cost estimation
- Cost-based plan search with branch-and-bound
- Machine learning cost predictor
- Real query execution with PostgreSQL backend
- Constraint-based optimization (cardinality, selectivity)
