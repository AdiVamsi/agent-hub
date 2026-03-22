"""SQL Optimizer — evaluation harness.

Loads workload.json, imports optimize_query from rewrite_rules, and evaluates:
- Cost estimation using rule-based heuristics
- Semantic equivalence validation
- Total query cost and improvement percentage
"""

import json
import re
import sys
from typing import Any, Tuple


def load_workload(filename: str = "workload.json") -> list[dict[str, Any]]:
    """Load workload from JSON file."""
    with open(filename, "r") as f:
        return json.load(f)


def has_select_star(sql: str) -> bool:
    """Check if query contains SELECT *."""
    return bool(re.search(r"\bSELECT\s+\*", sql, re.IGNORECASE))


def count_correlated_subqueries(sql: str) -> int:
    """Estimate number of correlated subqueries by looking for WHERE IN/EXISTS with subqueries."""
    # Simple heuristic: count parentheses with SELECT inside
    subqueries = len(re.findall(r"\(\s*SELECT", sql, re.IGNORECASE))
    # Count correlated patterns: reference to outer alias in subquery
    correlated = len(re.findall(r"WHERE\s+.*=\s*\w+\.\w+", sql, re.IGNORECASE))
    return subqueries if correlated > 0 else 0


def has_unnecessary_distinct(sql: str) -> bool:
    """Heuristic: DISTINCT is often unnecessary with aggregates but needed with GROUP BY."""
    has_distinct = bool(re.search(r"\bDISTINCT\b", sql, re.IGNORECASE))
    has_group_by = bool(re.search(r"\bGROUP\s+BY\b", sql, re.IGNORECASE))
    has_aggregate = bool(re.search(r"\b(COUNT|SUM|AVG|MIN|MAX)\s*\(", sql, re.IGNORECASE))
    # DISTINCT is unnecessary when aggregates are present (not GROUP BY)
    return has_distinct and has_aggregate and not has_group_by


def has_large_result_no_limit(sql: str, estimated_rows: int) -> bool:
    """Check if large result set lacks LIMIT."""
    has_limit = bool(re.search(r"\bLIMIT\s+\d+", sql, re.IGNORECASE))
    return estimated_rows > 10000 and not has_limit


def has_unindexed_predicate(sql: str, has_index: dict[str, list[str]]) -> bool:
    """Check if WHERE clause uses non-indexed columns."""
    where_match = re.search(r"\bWHERE\s+(.+?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$)", sql, re.IGNORECASE)
    if not where_match:
        return False

    where_clause = where_match.group(1)
    # Find column references in WHERE
    columns = re.findall(r"\b(\w+)\s*[=><]", where_clause)

    # Check if any column is not indexed
    all_indexed_cols = set()
    for cols in has_index.values():
        all_indexed_cols.update(cols)

    return any(col not in all_indexed_cols for col in columns)


def has_unnecessary_order_by_in_subquery(sql: str) -> bool:
    """Detect ORDER BY in subquery that gets overridden by outer query."""
    # Pattern: (SELECT ... ORDER BY ...) WHERE/GROUP/ORDER
    return bool(re.search(r"\(\s*SELECT\s+.+\bORDER\s+BY\b.+?\)\s+(?:WHERE|GROUP|ORDER)", sql, re.IGNORECASE))


def estimate_query_cost(original_sql: str, optimized_sql: str, query_info: dict[str, Any]) -> Tuple[float, float]:
    """Estimate cost for original and optimized queries using rule-based heuristics.

    Returns:
        (original_cost, optimized_cost)
    """
    estimated_rows = query_info["estimated_rows_scanned"]
    has_index = query_info["has_index"]

    def calc_cost(sql: str) -> float:
        cost = 0.0

        # Base cost: rows scanned
        # Assume indexed lookups are faster (0.1x multiplier)
        if has_index and any(has_index.values()):
            # Has at least one index, slightly reduce base cost
            cost = estimated_rows * 0.5  # Partial index benefit
        else:
            cost = estimated_rows * 1.0  # Full table scan

        # SELECT * penalty (1.5x)
        if has_select_star(sql):
            cost *= 1.5

        # Correlated subquery penalty (2.0x per subquery)
        correlated_count = count_correlated_subqueries(sql)
        cost *= (2.0 ** correlated_count) if correlated_count > 0 else 1.0

        # DISTINCT penalty (1.3x if unnecessary)
        if has_unnecessary_distinct(sql):
            cost *= 1.3

        # No-LIMIT penalty (1.2x on large result sets)
        if has_large_result_no_limit(sql, estimated_rows):
            cost *= 1.2

        # Unindexed predicate penalty (1.5x)
        if has_unindexed_predicate(sql, has_index):
            cost *= 1.5

        # Unnecessary ORDER BY in subquery (1.1x)
        if has_unnecessary_order_by_in_subquery(sql):
            cost *= 1.1

        return cost

    original_cost = calc_cost(original_sql)
    optimized_cost = calc_cost(optimized_sql)

    return original_cost, optimized_cost


def validate_semantic_equivalence(original_sql: str, optimized_sql: str, query_info: dict[str, Any]) -> bool:
    """Basic semantic equivalence check: same tables touched."""
    tables = set(query_info["tables_touched"])

    # Extract table names from SQL
    def extract_tables(sql: str) -> set[str]:
        # Simple regex: FROM <table> or JOIN <table>
        from_tables = re.findall(r"\b(?:FROM|JOIN)\s+(?:AS\s+)?\b(\w+)", sql, re.IGNORECASE)
        return set(from_tables)

    original_tables = extract_tables(original_sql)
    optimized_tables = extract_tables(optimized_sql)

    # Check that tables are exactly the same (strict equality)
    return original_tables == optimized_tables


def validate_where_predicates(original_sql: str, optimized_sql: str) -> bool:
    """Verify that WHERE clause predicates are preserved in optimized query."""
    # Extract WHERE clause conditions (simple heuristic)
    original_where = re.search(r"\bWHERE\s+(.+?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$)", original_sql, re.IGNORECASE)
    optimized_where = re.search(r"\bWHERE\s+(.+?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$)", optimized_sql, re.IGNORECASE)

    if not original_where:
        # No WHERE clause in original, so optimized should not add restrictions
        return not optimized_where or optimized_where.group(1).strip() == original_where.group(1).strip() if optimized_where else True

    # Check that key predicate terms are present in optimized query
    original_terms = re.findall(r"\b\w+\s*[=><]", original_where.group(1), re.IGNORECASE)
    for term in original_terms:
        if term not in optimized_sql:
            return False
    return True


def evaluate_workload(workload: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate entire workload.

    Returns:
        {
            "total_original_cost": float,
            "total_optimized_cost": float,
            "improvement_pct": float,
            "query_results": [...]
        }
    """
    from rewrite_rules import optimize_query

    total_original_cost = 0.0
    total_optimized_cost = 0.0
    query_results = []

    for query_info in workload:
        original_sql = query_info["sql"]

        try:
            optimized_sql = optimize_query(query_info)

            # Input validation: check return type and non-empty result
            if not isinstance(optimized_sql, str):
                print(f"Error: {query_info['query_id']} optimize_query returned non-string type", file=sys.stderr)
                optimized_sql = original_sql
            elif not optimized_sql.strip():
                print(f"Error: {query_info['query_id']} optimize_query returned empty string", file=sys.stderr)
                optimized_sql = original_sql

        except Exception as e:
            print(f"Error optimizing {query_info['query_id']}: {e}", file=sys.stderr)
            optimized_sql = original_sql

        # Validate semantic equivalence
        if not validate_semantic_equivalence(original_sql, optimized_sql, query_info):
            print(f"Warning: {query_info['query_id']} may not be semantically equivalent", file=sys.stderr)

        # Validate WHERE clause predicates are preserved
        if not validate_where_predicates(original_sql, optimized_sql):
            print(f"Warning: {query_info['query_id']} WHERE clause predicates may not be preserved", file=sys.stderr)

        original_cost, optimized_cost = estimate_query_cost(original_sql, optimized_sql, query_info)

        total_original_cost += original_cost
        total_optimized_cost += optimized_cost

        query_results.append({
            "query_id": query_info["query_id"],
            "original_cost": original_cost,
            "optimized_cost": optimized_cost,
            "improvement": original_cost - optimized_cost,
        })

    improvement_pct = 0.0
    if total_original_cost > 0:
        improvement_pct = (total_original_cost - total_optimized_cost) / total_original_cost * 100

    return {
        "total_original_cost": total_original_cost,
        "total_optimized_cost": total_optimized_cost,
        "improvement_pct": improvement_pct,
        "query_results": query_results,
    }


def print_results(results: dict[str, Any]) -> None:
    """Print evaluation results."""
    print(f"\nRESULT: total_query_cost={results['total_optimized_cost']:.1f} improvement_pct={results['improvement_pct']:.1f}")
    print(f"\nBaseline cost: {results['total_original_cost']:.1f}")
    print(f"Optimized cost: {results['total_optimized_cost']:.1f}")
    print(f"Improvement: {results['improvement_pct']:.2f}%")

    # Show top improvements
    top_improvements = sorted(results["query_results"], key=lambda x: x["improvement"], reverse=True)[:5]
    if top_improvements and top_improvements[0]["improvement"] > 0:
        print("\nTop improvements:")
        for qr in top_improvements:
            print(f"  {qr['query_id']}: -{qr['improvement']:.1f} cost")


def main():
    """CLI entry point."""
    try:
        workload = load_workload()
    except FileNotFoundError:
        print("Error: workload.json not found. Run: python prepare.py generate", file=sys.stderr)
        sys.exit(1)

    results = evaluate_workload(workload)
    print_results(results)


if __name__ == "__main__":
    main()
