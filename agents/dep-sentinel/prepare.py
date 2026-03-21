#!/usr/bin/env python3
"""Setup script for dep-sentinel. DO NOT MODIFY.

Usage:
    python prepare.py init  — verify files exist, run baseline evaluation
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VULNDB_PATH = ROOT / "vulndb.json"
REQUIREMENTS_PATH = ROOT / "project" / "requirements.txt"
APP_PATH = ROOT / "project" / "app.py"


def cmd_init():
    print("=" * 60)
    print("  dep-sentinel — Setup")
    print("=" * 60)

    # Step 1: Verify files exist
    print("\n[1/3] Verifying project files...")
    for path, label in [
        (VULNDB_PATH, "vulndb.json"),
        (REQUIREMENTS_PATH, "project/requirements.txt"),
        (APP_PATH, "project/app.py"),
    ]:
        if path.exists():
            print(f"  {label}: OK")
        else:
            print(f"  {label}: MISSING")
            sys.exit(1)

    # Step 2: Summarize vulnerability database
    print("\n[2/3] Scanning vulnerability database...")
    with open(VULNDB_PATH) as f:
        vulndb = json.load(f)["vulnerabilities"]

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    packages = set()
    for v in vulndb:
        counts[v["severity"]] = counts.get(v["severity"], 0) + 1
        packages.add(v["package"])

    total = len(vulndb)
    print(f"  Total vulnerabilities: {total}")
    print(f"    Critical: {counts['critical']}")
    print(f"    High:     {counts['high']}")
    print(f"    Medium:   {counts['medium']}")
    print(f"    Low:      {counts['low']}")
    print(f"  Affected packages: {len(packages)}")

    # Step 3: Run baseline
    print("\n[3/3] Running baseline evaluation...")
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
    print(f"  Found {total} vulnerabilities across {len(packages)} packages.")
    print("  Point your agent at program.md to start patching.")
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
