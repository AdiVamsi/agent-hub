#!/usr/bin/env python3
"""Prepare stage: Generate simulated JS project dependency graph."""

import json
import random
import sys

def generate_dependency_graph(seed=42):
    """Generate a realistic 60-module dependency graph with realistic sizes."""
    random.seed(seed)

    # Define module pool with realistic sizes and characteristics
    modules_data = {
        # Core framework
        "react": {"size": 42000, "tree_shakeable": False, "has_side_effects": False, "total_exports": 25},
        "react-dom": {"size": 38000, "tree_shakeable": False, "has_side_effects": False, "total_exports": 15},
        "react-router": {"size": 28000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 12},

        # Utility libraries
        "lodash": {"size": 72000, "tree_shakeable": False, "has_side_effects": False, "total_exports": 320},
        "lodash-es": {"size": 72000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 320},
        "moment": {"size": 68000, "tree_shakeable": False, "has_side_effects": True, "total_exports": 3},
        "dayjs": {"size": 5000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 3},
        "axios": {"size": 14000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 8},
        "isomorphic-fetch": {"size": 8000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 2},

        # Visualization
        "d3": {"size": 240000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 150},
        "d3-lite": {"size": 85000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 150},
        "chart.js": {"size": 165000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 8},
        "recharts": {"size": 95000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 18},
        "plotly": {"size": 250000, "tree_shakeable": False, "has_side_effects": True, "total_exports": 12},

        # UI components
        "material-ui": {"size": 145000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 200},
        "bootstrap": {"size": 125000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 80},
        "antd": {"size": 185000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 150},

        # Validation
        "yup": {"size": 32000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 15},
        "joi": {"size": 48000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 20},
        "zod": {"size": 18000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 12},

        # Polyfills and compat
        "core-js": {"size": 92000, "tree_shakeable": False, "has_side_effects": True, "total_exports": 1},
        "babel-polyfill": {"size": 110000, "tree_shakeable": False, "has_side_effects": True, "total_exports": 1},

        # Styling
        "styled-components": {"size": 35000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 8},
        "emotion": {"size": 32000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 6},
        "tailwindcss": {"size": 45000, "tree_shakeable": True, "has_side_effects": True, "total_exports": 3},

        # State management
        "redux": {"size": 8000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 12},
        "zustand": {"size": 5000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 8},
        "recoil": {"size": 22000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 15},
        "mobx": {"size": 24000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 20},

        # HTTP & networking
        "node-fetch": {"size": 10000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 3},
        "ky": {"size": 6000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 4},
        "got": {"size": 28000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 5},

        # Form handling
        "formik": {"size": 38000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 20},
        "react-hook-form": {"size": 12000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 15},

        # Utilities
        "uuid": {"size": 4000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 3},
        "date-fns": {"size": 45000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 85},
        "ramda": {"size": 58000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 280},
        "underscore": {"size": 51000, "tree_shakeable": False, "has_side_effects": False, "total_exports": 100},
        "clsx": {"size": 2500, "tree_shakeable": True, "has_side_effects": False, "total_exports": 2},

        # Animation
        "framer-motion": {"size": 42000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 25},
        "react-spring": {"size": 36000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 18},

        # Testing (often in bundle by mistake)
        "jest": {"size": 125000, "tree_shakeable": False, "has_side_effects": True, "total_exports": 20},
        "mocha": {"size": 88000, "tree_shakeable": False, "has_side_effects": True, "total_exports": 15},

        # Unused polyfills
        "unused-polyfill": {"size": 35000, "tree_shakeable": False, "has_side_effects": True, "total_exports": 1},
        "legacy-support": {"size": 28000, "tree_shakeable": False, "has_side_effects": True, "total_exports": 1},

        # App module
        "app": {"size": 15000, "tree_shakeable": True, "has_side_effects": False, "total_exports": 8},
    }

    # Define dependencies and alternatives
    dep_graph = {}
    for module_id, props in modules_data.items():
        dep_graph[module_id] = {
            "module_id": module_id,
            "size_bytes": props["size"],
            "tree_shakeable": props["tree_shakeable"],
            "has_side_effects": props["has_side_effects"],
            "total_exports": props["total_exports"],
            "imports": [],
            "exports_used": 0,
            "alternatives": {}
        }

    # Define alternatives (replacement mappings)
    alternatives_map = {
        "moment": {"dayjs": "dayjs"},
        "lodash": {"lodash-es": "lodash-es"},
        "axios": {"isomorphic-fetch": "isomorphic-fetch", "ky": "ky"},
        "d3": {"d3-lite": "d3-lite"},
        "chart.js": {"recharts": "recharts"},
        "plotly": {"recharts": "recharts"},
        "material-ui": {"bootstrap": "bootstrap"},
        "antd": {"bootstrap": "bootstrap"},
        "joi": {"zod": "zod"},
        "yup": {"zod": "zod"},
        "ramda": {"lodash-es": "lodash-es"},
        "underscore": {"lodash-es": "lodash-es"},
    }

    for module_id, alternatives in alternatives_map.items():
        if module_id in dep_graph:
            dep_graph[module_id]["alternatives"] = alternatives

    # Define realistic dependency tree
    dependency_structure = {
        "app": ["react", "react-dom", "react-router", "lodash", "moment", "axios", "d3", "chart.js", "material-ui", "redux", "styled-components"],
        "react": ["react-router"],
        "react-router": ["react"],
        "redux": ["react"],
        "material-ui": ["react", "styled-components", "clsx"],
        "bootstrap": ["clsx"],
        "antd": ["react", "styled-components"],
        "d3": ["ramda"],
        "chart.js": ["moment"],
        "plotly": ["d3", "moment"],
        "react-hook-form": ["react", "zod"],
        "formik": ["react", "yup", "lodash"],
        "framer-motion": ["react"],
        "react-spring": ["react"],
        "recharts": ["react", "d3-lite"],
        "recoil": ["react"],
        "mobx": ["react"],
        "axios": ["isomorphic-fetch"],
        "got": ["node-fetch"],
        "date-fns": ["uuid"],
        "jest": ["mocha"],
        "babel-polyfill": ["core-js"],
        "tailwindcss": ["clsx"],
        "emotion": ["styled-components"],
    }

    # Build import lists
    for module_id, imports in dependency_structure.items():
        if module_id in dep_graph:
            dep_graph[module_id]["imports"] = imports

    # Calculate exports_used based on imports
    for module_id in dep_graph:
        import_count = 0
        for other_id, imports in dependency_structure.items():
            if module_id in imports:
                import_count += 1

        # Simulate that importers use 30-80% of available exports
        utilization_ratio = random.uniform(0.3, 0.8)
        exports_used = max(1, int(dep_graph[module_id]["total_exports"] * utilization_ratio))
        dep_graph[module_id]["exports_used"] = exports_used

    modules_list = list(dep_graph.values())

    # Calculate baseline size
    total_size = sum(m["size_bytes"] for m in modules_list)

    return {
        "modules": modules_list,
        "baseline_size_bytes": total_size,
        "num_modules": len(modules_list)
    }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        data = generate_dependency_graph(seed=42)
        with open("dependency_graph.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated dependency_graph.json with {data['num_modules']} modules")
        print(f"Baseline size: {data['baseline_size_bytes'] / 1024:.1f}KB")
    else:
        print("Usage: python prepare.py generate")

if __name__ == "__main__":
    main()
