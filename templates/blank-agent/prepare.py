#!/usr/bin/env python3
"""Data preparation — DO NOT MODIFY (after initial setup).

Replace this with your data generation or preparation logic.
It should create whatever test data harness.py needs.

Usage:
    python prepare.py generate   — create test data
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"


def generate(n: int = 1000):
    """Generate test data. Replace with your data generation logic."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / "test.jsonl"

    items = []
    for i in range(n):
        # Replace with your data generation logic
        item = {"id": i, "input": f"sample_{i}"}
        items.append(item)

    with open(output_path, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

    print(f"Generated {n} items → {output_path}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "generate"
    if cmd == "generate":
        generate()
    else:
        print(f"Usage: python prepare.py generate")
