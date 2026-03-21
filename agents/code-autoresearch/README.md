# code-autoresearch

**Karpathy's AutoResearch, but for your production code. Point it at a slow API, wake up to faster code with proven benchmarks.**

## The Problem

Production code accumulates performance debt. Manual profiling and optimization is tedious. Most developers know their code is slow but don't have time to fix it.

## The Solution

An AI agent that studies your code, forms optimization hypotheses, implements them, benchmarks, and keeps only proven improvements. 96 experiments overnight = weeks of manual optimization.

*"I pointed an AI agent at my slow Flask API. It ran 96 experiments overnight. My endpoints are 34% faster. Here are the git commits."*

## How It Works

Same 3-primitive design as [Karpathy's autoresearch](https://github.com/karpathy/autoresearch):

| File | Role | Modified by agent? |
|------|------|--------------------|
| `program.md` | "Optimize target.py to maximize requests_per_second" | No |
| `target.py` | The code being optimized | **Yes** |
| `harness.py` | Benchmark runner with correctness verification | No |

**The metric:** `requests_per_second` (higher = better)

**The loop:**
1. Agent reads `program.md`
2. Studies `target.py` for performance problems
3. Edits `target.py` with ONE optimization
4. Runs `python harness.py benchmark`
5. If req/s improved AND correctness passes → `git commit`
6. If not → `git reset --hard HEAD`
7. Repeat forever

**The safety net:** `harness.py` verifies that all function outputs remain identical to the baseline. The agent can't "optimize" by returning wrong results.

## Quick Start

```bash
pip install pyyaml
python prepare.py init
python harness.py baseline
# Point Claude Code at this folder:
# "Read program.md and start optimizing"
```

## Files

```
code-autoresearch/
├── program.md       ← Instructions for the AI agent
├── target.py        ← The ONE file the agent modifies (intentionally slow API)
├── harness.py       ← Benchmark runner with correctness checks (fixed)
├── prepare.py       ← Setup script (fixed)
├── workload.json    ← Benchmark workload definition
├── pyproject.toml   ← Dependencies
├── .baseline.json   ← (created at runtime) baseline metrics + fingerprints
└── results.tsv      ← (created at runtime) experiment log
```

## Intentional Performance Problems in target.py

The included `target.py` is a product catalog API with deliberate performance issues that an agent can find and fix:

- **O(n²) search** with nested loops and `str()` conversion for matching
- **Bubble sort** instead of Python's built-in `sorted()`
- **N+1 query pattern** scanning all reviews to find matches for one product
- **Missing caching** — recomputes average ratings for all 1000 products on every call
- **Linear scans** where dict lookups would work (finding products by ID)
- **String concatenation** with `+=` in loops instead of `join()`
- **Redundant recomputation** — calculates subtotals and totals multiple times
- **Materialized lists** where generators would work

## Workload

| Function | Calls | What it tests |
|----------|-------|---------------|
| `search_products` | 50 | Text search across 1000 products |
| `get_product_with_reviews` | 50 | Product + review lookup |
| `generate_recommendations` | 10 | Personalized recommendations |
| `generate_invoice` | 30 | Invoice generation |
| `analyze_sales` | 5 | Full sales analytics |

Total: 145 function calls per benchmark run, median of 3 runs.

## Example Results

```
Baseline:             ~45 req/s
After optimization:   ~150+ req/s  (+230%)

Typical optimizations kept:
  - Dict lookup for products by ID
  - functools.lru_cache for ratings
  - sorted() replacing bubble sort
  - str.join() replacing += concatenation
  - Generator expressions for aggregation
```

## Part of [agent-hub](../../README.md)

A collection of AI agents built on Karpathy's AutoResearch pattern.
