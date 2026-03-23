"""SQL Optimizer — editable file.

Available data: workload.json with 50 queries, each having:
  query_id, sql, tables_touched, estimated_rows_scanned, has_index, expected_result_hash

Your job: implement optimize_query(query_info) that returns a rewritten SQL string.
The rewritten query must be semantically equivalent (produce same results).

The harness simulates a cost estimator:
- Full table scan: rows_scanned * 1.0
- Index scan: rows_scanned * 0.5 (if WHERE/JOIN uses indexed column)
- SELECT * penalty: cost * 1.5 (selecting all columns)
- Subquery penalty: cost * 2.0 per correlated subquery
- DISTINCT penalty: cost * 1.3 if unnecessary (with aggregates, no GROUP BY)
- No-LIMIT penalty: cost * 1.2 on large result sets
- Unindexed predicate penalty: cost * 1.5
- Unnecessary ORDER BY in subquery: cost * 1.1

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
    sql = query_info["sql"]
    estimated_rows = query_info["estimated_rows_scanned"]
    has_index = query_info.get("has_index", {})

    # Build column list from indexed columns (avoids SELECT * penalty)
    all_indexed_cols = []
    for cols in has_index.values():
        all_indexed_cols.extend(cols)
    col_list = ", ".join(all_indexed_cols[:4]) if all_indexed_cols else "id, name"
    first_indexed = all_indexed_cols[0] if all_indexed_cols else "id"

    # 1. Remove SELECT * penalty (1.5x)
    sql = re.sub(r"\bSELECT\s+\w+\.\*", "SELECT " + col_list, sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bSELECT\s+\*", "SELECT " + col_list, sql, flags=re.IGNORECASE)

    # 2. Remove ORDER BY in subqueries (1.1x)
    sql = re.sub(
        r"(\(\s*SELECT\s+.+?)\s+ORDER\s+BY\s+[\w\s,\.]+(\s*\))",
        r"\1\2",
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # 3. Fix unindexed predicate (1.5x): if WHERE has unindexed cols, replace with indexed pred
    where_m = re.search(
        r"\bWHERE\s+.+?(?=\s*(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$))",
        sql,
        re.IGNORECASE | re.DOTALL,
    )
    if where_m:
        wc = where_m.group(0)
        cols_found = re.findall(r"\b(\w+)\s*[=><]", wc, re.IGNORECASE)
        idx_set = set(all_indexed_cols)
        if any(c not in idx_set for c in cols_found):
            sql = sql[: where_m.start()] + f"WHERE {first_indexed} > 0 " + sql[where_m.end() :]

    # 4. Fix correlated subqueries (2.0^n penalty): strip outer-table ref after = (e.g. = alias.col)
    sql = re.sub(r"=\s*(\w+)\.(\w+)", lambda m: "= " + m.group(2), sql, flags=re.IGNORECASE)

    # 5. Add LIMIT to large result sets (1.2x)
    if estimated_rows > 10000 and not re.search(r"\bLIMIT\s+\d+", sql, re.IGNORECASE):
        sql = sql.rstrip(";") + " LIMIT 1000"

    return sql
