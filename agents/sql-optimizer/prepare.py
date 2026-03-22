"""SQL Optimizer — Data generation.

Generates a workload.json with 50 SQL queries featuring common anti-patterns.
Each query includes schema context and cost estimation metadata.
"""

import json
import hashlib
import random
from typing import Any


def hash_result(query_id: str, seed: int) -> str:
    """Generate deterministic result hash for correctness checking."""
    return hashlib.md5(f"{query_id}_{seed}".encode()).hexdigest()[:8]


def generate_workload(seed: int = 42) -> list[dict[str, Any]]:
    """Generate 50 SQL queries with common anti-patterns.

    Schema:
      users(id, name, email, status, created_at)
      orders(id, user_id, total, status, created_at)
      products(id, name, price, category)
      order_items(id, order_id, product_id, quantity)

    Indexes:
      users(id, email, status)
      orders(id, user_id, created_at)
      products(id, category)
      order_items(id, order_id)
    """
    random.seed(seed)

    queries = []

    # Anti-pattern 1: SELECT * (5 queries)
    queries.append({
        "query_id": "q001",
        "sql": "SELECT * FROM users WHERE status = 'active'",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 5000,
        "has_index": {"users": ["status"]},
        "expected_result_hash": hash_result("q001", seed),
    })

    queries.append({
        "query_id": "q002",
        "sql": "SELECT * FROM orders JOIN users ON orders.user_id = users.id",
        "tables_touched": ["orders", "users"],
        "estimated_rows_scanned": 15000,
        "has_index": {"orders": ["user_id"], "users": ["id"]},
        "expected_result_hash": hash_result("q002", seed),
    })

    queries.append({
        "query_id": "q003",
        "sql": "SELECT * FROM products WHERE category IN ('electronics', 'books')",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 3000,
        "has_index": {"products": ["category"]},
        "expected_result_hash": hash_result("q003", seed),
    })

    queries.append({
        "query_id": "q004",
        "sql": "SELECT * FROM order_items oi JOIN products p ON oi.product_id = p.id",
        "tables_touched": ["order_items", "products"],
        "estimated_rows_scanned": 20000,
        "has_index": {"order_items": ["product_id"], "products": ["id"]},
        "expected_result_hash": hash_result("q004", seed),
    })

    queries.append({
        "query_id": "q005",
        "sql": "SELECT * FROM users u JOIN orders o ON u.id = o.user_id WHERE o.status = 'completed'",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 10000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q005", seed),
    })

    # Anti-pattern 2: Missing WHERE (5 queries)
    queries.append({
        "query_id": "q006",
        "sql": "SELECT user_id, COUNT(*) FROM orders GROUP BY user_id",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 50000,
        "has_index": {"orders": ["id"]},
        "expected_result_hash": hash_result("q006", seed),
    })

    queries.append({
        "query_id": "q007",
        "sql": "SELECT id, name, email FROM users",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 100000,
        "has_index": {"users": ["id"]},
        "expected_result_hash": hash_result("q007", seed),
    })

    queries.append({
        "query_id": "q008",
        "sql": "SELECT product_id, SUM(quantity) FROM order_items GROUP BY product_id",
        "tables_touched": ["order_items"],
        "estimated_rows_scanned": 200000,
        "has_index": {"order_items": ["id"]},
        "expected_result_hash": hash_result("q008", seed),
    })

    queries.append({
        "query_id": "q009",
        "sql": "SELECT id, price, category FROM products",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 50000,
        "has_index": {"products": ["id"]},
        "expected_result_hash": hash_result("q009", seed),
    })

    queries.append({
        "query_id": "q010",
        "sql": "SELECT o.id, o.user_id, o.total FROM orders o",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 100000,
        "has_index": {"orders": ["id"]},
        "expected_result_hash": hash_result("q010", seed),
    })

    # Anti-pattern 3: Subqueries that could be JOINs (6 queries)
    queries.append({
        "query_id": "q011",
        "sql": "SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE status = 'active')",
        "tables_touched": ["orders", "users"],
        "estimated_rows_scanned": 15000,
        "has_index": {"orders": ["user_id"], "users": ["status"]},
        "expected_result_hash": hash_result("q011", seed),
    })

    queries.append({
        "query_id": "q012",
        "sql": "SELECT id, name FROM products WHERE id IN (SELECT product_id FROM order_items WHERE quantity > 5)",
        "tables_touched": ["products", "order_items"],
        "estimated_rows_scanned": 10000,
        "has_index": {"products": ["id"], "order_items": ["product_id"]},
        "expected_result_hash": hash_result("q012", seed),
    })

    queries.append({
        "query_id": "q013",
        "sql": "SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM orders WHERE status = 'cancelled')",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 30000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q013", seed),
    })

    queries.append({
        "query_id": "q014",
        "sql": "SELECT name, (SELECT COUNT(*) FROM orders WHERE user_id = users.id) as order_count FROM users",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 25000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q014", seed),
    })

    queries.append({
        "query_id": "q015",
        "sql": "SELECT * FROM orders WHERE total > (SELECT AVG(total) FROM orders)",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 100000,
        "has_index": {"orders": ["id"]},
        "expected_result_hash": hash_result("q015", seed),
    })

    queries.append({
        "query_id": "q016",
        "sql": "SELECT u.id, u.name FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.status = 'pending')",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 20000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q016", seed),
    })

    # Anti-pattern 4: OR chains that could be IN() (5 queries)
    queries.append({
        "query_id": "q017",
        "sql": "SELECT * FROM products WHERE category = 'electronics' OR category = 'books' OR category = 'toys'",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 10000,
        "has_index": {"products": ["category"]},
        "expected_result_hash": hash_result("q017", seed),
    })

    queries.append({
        "query_id": "q018",
        "sql": "SELECT * FROM orders WHERE status = 'completed' OR status = 'shipped' OR status = 'processing'",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 80000,
        "has_index": {"orders": ["status"]},
        "expected_result_hash": hash_result("q018", seed),
    })

    queries.append({
        "query_id": "q019",
        "sql": "SELECT id, name FROM users WHERE email LIKE '%@gmail.com' OR email LIKE '%@yahoo.com'",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 50000,
        "has_index": {"users": ["email"]},
        "expected_result_hash": hash_result("q019", seed),
    })

    queries.append({
        "query_id": "q020",
        "sql": "SELECT * FROM users WHERE status = 'active' OR status = 'inactive' OR status = 'pending'",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 80000,
        "has_index": {"users": ["status"]},
        "expected_result_hash": hash_result("q020", seed),
    })

    queries.append({
        "query_id": "q021",
        "sql": "SELECT product_id, SUM(quantity) FROM order_items WHERE quantity = 1 OR quantity = 2 OR quantity = 3 GROUP BY product_id",
        "tables_touched": ["order_items"],
        "estimated_rows_scanned": 120000,
        "has_index": {"order_items": ["product_id"]},
        "expected_result_hash": hash_result("q021", seed),
    })

    # Anti-pattern 5: LIKE '%prefix%' with non-indexed LIKE (4 queries)
    queries.append({
        "query_id": "q022",
        "sql": "SELECT * FROM users WHERE name LIKE '%john%'",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 100000,
        "has_index": {"users": ["id"]},
        "expected_result_hash": hash_result("q022", seed),
    })

    queries.append({
        "query_id": "q023",
        "sql": "SELECT id, name FROM products WHERE name LIKE '%phone%' AND price > 500",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 50000,
        "has_index": {"products": ["price"]},
        "expected_result_hash": hash_result("q023", seed),
    })

    queries.append({
        "query_id": "q024",
        "sql": "SELECT * FROM users WHERE email LIKE 'user_%'",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 100000,
        "has_index": {"users": ["email"]},
        "expected_result_hash": hash_result("q024", seed),
    })

    queries.append({
        "query_id": "q025",
        "sql": "SELECT name FROM products WHERE name LIKE '%sale%' OR name LIKE '%deal%'",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 50000,
        "has_index": {"products": ["id"]},
        "expected_result_hash": hash_result("q025", seed),
    })

    # Anti-pattern 6: Unnecessary DISTINCT (4 queries)
    queries.append({
        "query_id": "q026",
        "sql": "SELECT DISTINCT user_id FROM orders",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 100000,
        "has_index": {"orders": ["user_id"]},
        "expected_result_hash": hash_result("q026", seed),
    })

    queries.append({
        "query_id": "q027",
        "sql": "SELECT DISTINCT u.id, u.email FROM users u JOIN orders o ON u.id = o.user_id",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 25000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q027", seed),
    })

    queries.append({
        "query_id": "q028",
        "sql": "SELECT DISTINCT product_id FROM order_items WHERE order_id > 1000",
        "tables_touched": ["order_items"],
        "estimated_rows_scanned": 80000,
        "has_index": {"order_items": ["order_id"]},
        "expected_result_hash": hash_result("q028", seed),
    })

    queries.append({
        "query_id": "q029",
        "sql": "SELECT DISTINCT category FROM products WHERE price > 100",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 50000,
        "has_index": {"products": ["category"]},
        "expected_result_hash": hash_result("q029", seed),
    })

    # Anti-pattern 7: Correlated subqueries (5 queries)
    queries.append({
        "query_id": "q030",
        "sql": "SELECT id, name, (SELECT MAX(total) FROM orders WHERE user_id = users.id) FROM users",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 50000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q030", seed),
    })

    queries.append({
        "query_id": "q031",
        "sql": "SELECT id, name FROM users u WHERE (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) > 5",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 40000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q031", seed),
    })

    queries.append({
        "query_id": "q032",
        "sql": "SELECT product_id, name FROM products p WHERE (SELECT SUM(quantity) FROM order_items WHERE product_id = p.id) > 100",
        "tables_touched": ["products", "order_items"],
        "estimated_rows_scanned": 30000,
        "has_index": {"products": ["id"], "order_items": ["product_id"]},
        "expected_result_hash": hash_result("q032", seed),
    })

    queries.append({
        "query_id": "q033",
        "sql": "SELECT * FROM orders o WHERE total > (SELECT AVG(total) FROM orders WHERE user_id = o.user_id)",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 100000,
        "has_index": {"orders": ["user_id"]},
        "expected_result_hash": hash_result("q033", seed),
    })

    queries.append({
        "query_id": "q034",
        "sql": "SELECT u.id, u.name FROM users u WHERE u.created_at > (SELECT AVG(created_at) FROM users WHERE status = u.status)",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 80000,
        "has_index": {"users": ["status"]},
        "expected_result_hash": hash_result("q034", seed),
    })

    # Anti-pattern 8: Missing LIMIT on potentially large result sets (5 queries)
    queries.append({
        "query_id": "q035",
        "sql": "SELECT * FROM orders ORDER BY created_at DESC",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 100000,
        "has_index": {"orders": ["created_at"]},
        "expected_result_hash": hash_result("q035", seed),
    })

    queries.append({
        "query_id": "q036",
        "sql": "SELECT id, name, email FROM users ORDER BY created_at DESC",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 100000,
        "has_index": {"users": ["created_at"]},
        "expected_result_hash": hash_result("q036", seed),
    })

    queries.append({
        "query_id": "q037",
        "sql": "SELECT * FROM products ORDER BY price DESC",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 50000,
        "has_index": {"products": ["price"]},
        "expected_result_hash": hash_result("q037", seed),
    })

    queries.append({
        "query_id": "q038",
        "sql": "SELECT o.*, u.name FROM orders o JOIN users u ON o.user_id = u.id ORDER BY o.created_at DESC",
        "tables_touched": ["orders", "users"],
        "estimated_rows_scanned": 50000,
        "has_index": {"orders": ["created_at"], "users": ["id"]},
        "expected_result_hash": hash_result("q038", seed),
    })

    queries.append({
        "query_id": "q039",
        "sql": "SELECT product_id, SUM(quantity) as total_qty FROM order_items GROUP BY product_id ORDER BY total_qty DESC",
        "tables_touched": ["order_items"],
        "estimated_rows_scanned": 200000,
        "has_index": {"order_items": ["product_id"]},
        "expected_result_hash": hash_result("q039", seed),
    })

    # Anti-pattern 9: Unnecessary ORDER BY in subqueries (4 queries)
    queries.append({
        "query_id": "q040",
        "sql": "SELECT * FROM (SELECT * FROM orders ORDER BY created_at) WHERE status = 'completed'",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 100000,
        "has_index": {"orders": ["status"]},
        "expected_result_hash": hash_result("q040", seed),
    })

    queries.append({
        "query_id": "q041",
        "sql": "SELECT id, name FROM (SELECT * FROM users ORDER BY id DESC) WHERE status = 'active'",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 100000,
        "has_index": {"users": ["status"]},
        "expected_result_hash": hash_result("q041", seed),
    })

    queries.append({
        "query_id": "q042",
        "sql": "SELECT * FROM (SELECT * FROM products ORDER BY price DESC) WHERE category = 'electronics'",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 50000,
        "has_index": {"products": ["category"]},
        "expected_result_hash": hash_result("q042", seed),
    })

    queries.append({
        "query_id": "q043",
        "sql": "SELECT oi.product_id FROM (SELECT * FROM order_items ORDER BY quantity DESC) oi WHERE oi.quantity > 10",
        "tables_touched": ["order_items"],
        "estimated_rows_scanned": 200000,
        "has_index": {"order_items": ["order_id"]},
        "expected_result_hash": hash_result("q043", seed),
    })

    # Anti-pattern 10: Unindexed predicates (4 queries)
    queries.append({
        "query_id": "q044",
        "sql": "SELECT * FROM users WHERE name = 'John'",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 100000,
        "has_index": {"users": ["id"]},
        "expected_result_hash": hash_result("q044", seed),
    })

    queries.append({
        "query_id": "q045",
        "sql": "SELECT * FROM products WHERE price * 1.1 > 1000",
        "tables_touched": ["products"],
        "estimated_rows_scanned": 50000,
        "has_index": {"products": ["price"]},
        "expected_result_hash": hash_result("q045", seed),
    })

    queries.append({
        "query_id": "q046",
        "sql": "SELECT * FROM orders WHERE YEAR(created_at) = 2024",
        "tables_touched": ["orders"],
        "estimated_rows_scanned": 100000,
        "has_index": {"orders": ["created_at"]},
        "expected_result_hash": hash_result("q046", seed),
    })

    queries.append({
        "query_id": "q047",
        "sql": "SELECT * FROM users WHERE LOWER(email) = 'john@example.com'",
        "tables_touched": ["users"],
        "estimated_rows_scanned": 100000,
        "has_index": {"users": ["email"]},
        "expected_result_hash": hash_result("q047", seed),
    })

    # Additional complex queries (3 queries)
    queries.append({
        "query_id": "q048",
        "sql": "SELECT u.id, u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 50000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q048", seed),
    })

    queries.append({
        "query_id": "q049",
        "sql": "SELECT * FROM orders WHERE id IN (SELECT order_id FROM order_items WHERE product_id IN (SELECT id FROM products WHERE price > 100))",
        "tables_touched": ["orders", "order_items", "products"],
        "estimated_rows_scanned": 40000,
        "has_index": {"orders": ["id"], "order_items": ["order_id"], "products": ["id"]},
        "expected_result_hash": hash_result("q049", seed),
    })

    queries.append({
        "query_id": "q050",
        "sql": "SELECT DISTINCT u.id, u.name FROM users u JOIN orders o ON u.id = o.user_id WHERE o.status IN ('completed', 'shipped') ORDER BY u.id",
        "tables_touched": ["users", "orders"],
        "estimated_rows_scanned": 30000,
        "has_index": {"users": ["id"], "orders": ["user_id"]},
        "expected_result_hash": hash_result("q050", seed),
    })

    return queries


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        workload = generate_workload(seed=42)
        with open("workload.json", "w") as f:
            json.dump(workload, f, indent=2)
        print(f"Generated {len(workload)} queries in workload.json")
    else:
        print("Usage: python prepare.py generate")


if __name__ == "__main__":
    main()
