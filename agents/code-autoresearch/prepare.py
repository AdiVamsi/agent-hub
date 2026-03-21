#!/usr/bin/env python3
"""Setup script for code-autoresearch. DO NOT MODIFY.

Usage:
    python prepare.py init  — verify target.py works, run initial baseline
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent


def cmd_init():
    """Initialize the agent: verify data, run self-test, establish baseline."""
    print("=" * 60)
    print("  code-autoresearch — Setup")
    print("=" * 60)

    # Step 1: Verify target.py loads and generates data
    print("\n[1/3] Verifying target.py...")
    try:
        from target import generate_sample_data
        data = generate_sample_data()
        print(f"  Products: {len(data['products'])}")
        print(f"  Reviews:  {len(data['reviews'])}")
        print(f"  Orders:   {len(data['orders'])}")
        print(f"  Users:    {len(data['users'])}")
        assert len(data["products"]) == 1000
        assert len(data["reviews"]) == 5000
        assert len(data["orders"]) == 500
        assert len(data["users"]) == 200
        print("  OK")
    except Exception as e:
        print(f"  FAILED: {e}")
        print("  Fix target.py before continuing.")
        sys.exit(1)

    # Step 2: Run self-test
    print("\n[2/3] Running self-test...")
    try:
        from target import (search_products, get_product_with_reviews,
                            generate_recommendations, generate_invoice,
                            analyze_sales)

        results = search_products("premium widget", data["products"])
        assert len(results) > 0, "search returned no results"
        print(f"  search_products: OK ({len(results)} results)")

        result = get_product_with_reviews(42, data["products"], data["reviews"])
        assert result["product"] is not None
        print(f"  get_product_with_reviews: OK")

        recs = generate_recommendations(
            data["users"][0]["purchase_history"],
            data["products"], data["reviews"]
        )
        assert len(recs) == 5
        print(f"  generate_recommendations: OK")

        inv = generate_invoice(data["orders"][0]["items"], data["products"], 0.08)
        assert inv["total"] > 0
        print(f"  generate_invoice: OK")

        analysis = analyze_sales(data["orders"], data["products"])
        assert analysis["total_revenue"] > 0
        print(f"  analyze_sales: OK")
    except Exception as e:
        print(f"  FAILED: {e}")
        sys.exit(1)

    # Step 3: Run baseline
    print("\n[3/3] Running initial baseline benchmark...")
    import subprocess
    result = subprocess.run(
        [sys.executable, "harness.py", "baseline"],
        cwd=ROOT,
        capture_output=False,
    )
    if result.returncode != 0:
        print("  Baseline failed. Check harness.py output above.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  Setup complete!")
    print("  Baseline saved to .baseline.json")
    print("  Point your agent at program.md to start optimizing.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prepare.py init")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "init":
        cmd_init()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python prepare.py init")
        sys.exit(1)
