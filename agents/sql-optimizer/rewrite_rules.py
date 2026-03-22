"""SQL Optimizer — editable file.

Available data: workload.json with 50 queries, each having:
  query_id, sql, tables_touched, estimated_rows_scanned, has_index, expected_result_hash

Your job: implement optimize_query(query_info) that returns a rewritten SQL string.
The rewritten query must be semantically equivalent (produce same results).

The harness simulates a cost estimator:
- Full table scan: rows_scanned * 1.0
- Index scan: rows_scanned * 0.1 (if WHERE/JOIN uses indexed column)
- SELECT * penalty: cost * 1.5 (selecting all columns)
- Subquery penalty: cost * 2.0 per correlated subquery
- DISTINCT penalty: cost * 1.3 if unnecessary
- No-LIMIT penalty: cost * 1.2 on large result sets

Metric: total_query_cost (sum of costs) — LOWER is better.
Baseline: return query unchanged.
"""

import re
from typing import Any


def optimize_query(query_info: dict[str, Any]) -> str:
    """Return optimized SQL. Baseline: return original query unchanged.

    Args:
        query_info: Dictionary with keys:
            - query_id: str
            - sql: str (original query)
            - tables_touched: list[str]
            - estimated_rows_scanned: int
            - has_index: dict[str, list[str]]
            - expected_result_hash: str

    Returns:
        Optimized SQL string (must be semantically equivalent).
    """
    return query_info["sql"]
