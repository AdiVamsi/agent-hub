#!/usr/bin/env python3
"""API Racer — prepare stage. Generates api_workload.json with 100 API endpoints."""

import json
import random
import sys
from pathlib import Path


def generate_workload(seed=42, count=100):
    """Generate realistic API endpoint scenarios."""
    random.seed(seed)

    methods = ["GET", "GET", "GET", "GET", "POST", "POST", "POST", "PUT", "PUT", "DELETE"]
    path_templates = [
        "/users", "/users/{id}", "/users/{id}/profile", "/users/{id}/settings",
        "/orders", "/orders/{id}", "/orders/{id}/items", "/orders/{id}/status",
        "/products", "/products/{id}", "/products/{id}/details", "/products/{id}/reviews",
        "/posts", "/posts/{id}", "/posts/{id}/comments", "/posts/{id}/likes",
        "/auth/login", "/auth/logout", "/auth/refresh", "/auth/verify",
        "/search", "/search/users", "/search/products", "/search/orders",
        "/analytics", "/analytics/users", "/analytics/orders", "/analytics/products",
        "/settings", "/settings/general", "/settings/security", "/settings/notifications",
        "/notifications", "/notifications/{id}", "/notifications/read", "/notifications/unsubscribe",
        "/billing", "/billing/invoices", "/billing/invoices/{id}", "/billing/payment-methods",
        "/reports", "/reports/sales", "/reports/users", "/reports/performance",
        "/data/export", "/data/import", "/data/sync", "/data/validate",
        "/cache/clear", "/cache/status", "/health", "/health/db", "/health/services",
    ]

    endpoints = []
    for i in range(count):
        method = random.choice(methods)
        path = random.choice(path_templates)

        # Realistic payload: GETs small, POSTs/PUTs larger
        if method == "GET":
            avg_payload_bytes = random.randint(100, 500)
        elif method in ["POST", "PUT"]:
            avg_payload_bytes = random.randint(500, 3000)
        else:  # DELETE
            avg_payload_bytes = random.randint(50, 200)

        # Traffic distribution: 80/20 rule
        if random.random() < 0.2:
            calls_per_minute = random.randint(100, 1000)
        else:
            calls_per_minute = random.randint(1, 50)

        # Database and upstream calls
        if method == "GET":
            db_queries = random.randint(0, 3)
            upstream_calls = random.randint(0, 2)
        elif method in ["POST", "PUT"]:
            db_queries = random.randint(1, 5)
            upstream_calls = random.randint(0, 2)
        else:  # DELETE
            db_queries = random.randint(1, 2)
            upstream_calls = 0

        # Cacheable: mostly GETs
        cacheable = method == "GET" and random.random() < 0.8

        # Auth required: varies
        auth_required = random.random() < 0.7

        # Response time formula: db_queries*15ms + upstream_calls*50ms + payload*0.001ms + 5ms
        base_time = 5
        db_time = db_queries * 15
        upstream_time = upstream_calls * 50
        payload_time = avg_payload_bytes * 0.001

        p50_ms = base_time + db_time + upstream_time + payload_time
        p99_ms = p50_ms * 2.5 + random.randint(5, 50)

        endpoints.append({
            "endpoint_id": f"ep_{i:03d}",
            "method": method,
            "path": path,
            "avg_payload_bytes": avg_payload_bytes,
            "calls_per_minute": calls_per_minute,
            "current_p50_ms": round(p50_ms, 2),
            "current_p99_ms": round(p99_ms, 2),
            "cacheable": cacheable,
            "db_queries": db_queries,
            "upstream_calls": upstream_calls,
            "auth_required": auth_required,
        })

    return endpoints


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        workload = generate_workload(seed=42, count=100)
        output_file = Path(__file__).parent / "api_workload.json"
        with open(output_file, "w") as f:
            json.dump(workload, f, indent=2)
        print(f"Generated {len(workload)} endpoints -> {output_file}")
        print(f"Baseline avg_response_ms: {sum(ep['current_p50_ms'] * ep['calls_per_minute'] for ep in workload) / sum(ep['calls_per_minute'] for ep in workload):.2f}")
    else:
        print("Usage: python prepare.py generate")


if __name__ == "__main__":
    main()
