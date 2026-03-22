# docker-slim Agent

An intelligent Docker image optimizer that reduces image size while preserving all runtime functionality and test coverage.

## Problem

Docker images often contain unnecessary dependencies, build tools, test fixtures, and development dependencies. The average production Dockerfile balloons to 2800MB when it could be 200-400MB.

**Existing Solutions:**
- [Slim.AI](https://slim.ai) — $99/mo, commercial service
- [Dive](https://github.com/wagoodman/dive) — Free, manual layer exploration
- [DockerSlim](https://github.com/docker-slim/docker-slim) — Free, limited automation

## Solution

The docker-slim agent uses automated reasoning to:

1. **Analyze dependencies** — Understand which layers are required by production runtime
2. **Identify removables** — Detect dev dependencies, test fixtures, build tools, and docs
3. **Optimize configuration** — Apply multi-stage builds, layer combining, and smart replacements
4. **Validate constraints** — Ensure no broken dependency chains or production runtime loss

## How It Works

### Input
Upload your Dockerfile + dependency list (or we generate a manifest from your image).

### Processing
The agent tests 8+ optimization hypotheses:
- H1: Remove dev dependencies (pytest, black, jupyter, etc.)
- H2: Use multi-stage builds to exclude build tools
- H3: Replace large dependencies with smaller alternatives
- H4: Remove test fixtures and mock data
- H5: Strip documentation and examples
- H6: Combine asset layers for efficiency
- H7: Aggressive pruning with dependency validation
- H8: Extreme optimization respecting all constraints

### Output
Optimized Dockerfile configuration with:
- Estimated size reduction (typical: 70-90%)
- Layer removal/replacement plan
- Multi-stage build recommendations
- Dependency validation report

## Usage

```bash
# Generate synthetic app manifest for testing
python prepare.py generate

# Run baseline (no optimization)
python harness.py baseline

# Evaluate current optimization config
python harness.py evaluate
```

### Example Workflow

1. Edit `dockerfile_config.py` with your optimization strategy
2. Run `python harness.py evaluate` to see the metric
3. Iterate on the config to improve results

## Expected Results

| Strategy | Size | Reduction |
|----------|------|-----------|
| Baseline (no optimization) | 2800MB | 0% |
| Remove dev deps only | 2510MB | 10% |
| Multi-stage + dev removal | 1450MB | 48% |
| + Test fixtures + alternatives | 850MB | 70% |
| Extreme pruning | 200-400MB | 86-93% |

## Monetization

- **Free tier:** Upload Dockerfile, get optimization report
- **Pro tier:** Automated builds, CI/CD integration, size monitoring
- **Enterprise:** Custom dependency analysis, compliance validation

Upload your Dockerfile at **agent-hub.dev** to get started.

## Architecture

- `prepare.py` — Generates synthetic app manifest with 40 dependencies
- `dockerfile_config.py` — Editable optimization config (your workspace)
- `harness.py` — Validates constraints, calculates metrics
- `program.md` — 8+ optimization hypotheses
- `pyproject.toml` — No external dependencies

## Metrics

**Primary:** `image_size_mb` (lower is better)

**Constraints:**
- No removal of entries with `removable_in_prod=False`
- All `required_by` chains must be satisfied
- Multi-stage build must validate build tools aren't needed in final stage

## Research

Follows Karpathy's AutoResearch pattern:
1. Synthetic dataset generation (prepare.py)
2. Baseline measurement
3. Hypothesis-driven optimization (8+ tests)
4. Metric-driven iteration
5. Constraint validation

---

*Built with AutoResearch methodology. Optimize smarter.*
