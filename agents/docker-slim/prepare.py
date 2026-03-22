#!/usr/bin/env python3
"""Generate synthetic application manifest for Docker optimization."""

import json
import random
import sys


def generate_manifest(seed=42):
    """Generate app_manifest.json with 40 realistic dependencies/layers."""
    random.seed(seed)

    # Realistic entries with types, sizes, and characteristics
    entries = [
        # Runtime dependencies (production-critical)
        {"name": "python", "type": "runtime_dep", "size_mb": 50, "required_by": ["numpy", "pandas", "flask"], "removable_in_prod": False, "alternative": None},
        {"name": "numpy", "type": "runtime_dep", "size_mb": 120, "required_by": ["pandas", "scipy"], "removable_in_prod": False, "alternative": None},
        {"name": "pandas", "type": "runtime_dep", "size_mb": 95, "required_by": ["app"], "removable_in_prod": False, "alternative": None},
        {"name": "scipy", "type": "runtime_dep", "size_mb": 85, "required_by": ["ml_inference"], "removable_in_prod": False, "alternative": None},
        {"name": "flask", "type": "runtime_dep", "size_mb": 15, "required_by": ["app"], "removable_in_prod": False, "alternative": None},
        {"name": "requests", "type": "runtime_dep", "size_mb": 10, "required_by": ["app"], "removable_in_prod": False, "alternative": None},
        {"name": "pillow", "type": "runtime_dep", "size_mb": 45, "required_by": ["image_processing"], "removable_in_prod": False, "alternative": None},
        {"name": "opencv", "type": "runtime_dep", "size_mb": 180, "required_by": ["image_processing"], "removable_in_prod": False, "alternative": None},
        {"name": "ml_inference", "type": "runtime_dep", "size_mb": 320, "required_by": ["app"], "removable_in_prod": False, "alternative": None},
        {"name": "image_processing", "type": "runtime_dep", "size_mb": 60, "required_by": ["app"], "removable_in_prod": False, "alternative": None},

        # Build tools (often removable in production)
        {"name": "gcc", "type": "build_tool", "size_mb": 200, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "make", "type": "build_tool", "size_mb": 15, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "git", "type": "build_tool", "size_mb": 40, "required_by": ["repo_setup"], "removable_in_prod": True, "alternative": None},
        {"name": "repo_setup", "type": "build_tool", "size_mb": 5, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "cmake", "type": "build_tool", "size_mb": 35, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "curl", "type": "build_tool", "size_mb": 8, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "downloads", "type": "build_tool", "size_mb": 2, "required_by": [], "removable_in_prod": True, "alternative": None},

        # Dev dependencies
        {"name": "pytest", "type": "dev_dep", "size_mb": 25, "required_by": ["tests"], "removable_in_prod": True, "alternative": None},
        {"name": "coverage", "type": "dev_dep", "size_mb": 12, "required_by": ["tests"], "removable_in_prod": True, "alternative": None},
        {"name": "pytest-cov", "type": "dev_dep", "size_mb": 8, "required_by": ["tests"], "removable_in_prod": True, "alternative": None},
        {"name": "black", "type": "dev_dep", "size_mb": 10, "required_by": ["linting"], "removable_in_prod": True, "alternative": None},
        {"name": "pylint", "type": "dev_dep", "size_mb": 15, "required_by": ["linting"], "removable_in_prod": True, "alternative": None},
        {"name": "flake8", "type": "dev_dep", "size_mb": 9, "required_by": ["linting"], "removable_in_prod": True, "alternative": None},
        {"name": "linting", "type": "dev_dep", "size_mb": 3, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "jupyter", "type": "dev_dep", "size_mb": 150, "required_by": ["notebooks"], "removable_in_prod": True, "alternative": None},
        {"name": "ipython", "type": "dev_dep", "size_mb": 45, "required_by": ["notebooks"], "removable_in_prod": True, "alternative": None},
        {"name": "notebooks", "type": "dev_dep", "size_mb": 5, "required_by": [], "removable_in_prod": True, "alternative": None},

        # Test tools
        {"name": "tests", "type": "test_tool", "size_mb": 10, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "mock-data", "type": "test_tool", "size_mb": 150, "required_by": ["tests"], "removable_in_prod": True, "alternative": None},
        {"name": "test-fixtures", "type": "test_tool", "size_mb": 200, "required_by": ["tests"], "removable_in_prod": True, "alternative": None},

        # Assets and config
        {"name": "node_modules", "type": "asset", "size_mb": 250, "required_by": ["frontend_build"], "removable_in_prod": True, "alternative": "node_modules_prod"},
        {"name": "node_modules_prod", "type": "asset", "size_mb": 50, "required_by": [], "removable_in_prod": False, "alternative": None},
        {"name": "webpack", "type": "build_tool", "size_mb": 80, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "frontend_build", "type": "asset", "size_mb": 5, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": ".git", "type": "config", "size_mb": 80, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "docs", "type": "config", "size_mb": 120, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "examples", "type": "config", "size_mb": 60, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "debug-tools", "type": "config", "size_mb": 30, "required_by": [], "removable_in_prod": True, "alternative": None},
        {"name": "app", "type": "runtime_dep", "size_mb": 25, "required_by": [], "removable_in_prod": False, "alternative": None},
        {"name": "setuptools", "type": "build_tool", "size_mb": 12, "required_by": [], "removable_in_prod": True, "alternative": None},
    ]

    return entries


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        manifest = generate_manifest(seed=42)

        with open("app_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        total_size = sum(entry["size_mb"] for entry in manifest)
        print(f"Generated app_manifest.json with {len(manifest)} entries")
        print(f"Total unoptimized size: {total_size}MB")
    else:
        print("Usage: python prepare.py generate")


if __name__ == "__main__":
    main()
