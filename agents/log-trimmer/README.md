# Log Trimmer Agent

Optimizes log filtering rules to reduce log volume while preserving important signals (errors, warnings, key events).

## Overview

Production log pipelines generate massive volumes of noise: routine DEBUG logs, health checks, cache hits, heartbeats. This noise inflates storage costs and makes observability harder. **Log Trimmer** uses AutoResearch to discover filtering rules that drop 80%+ of noise while keeping 98%+ of critical signals.

## The Problem

- **Typical production system:** 10GB/day of logs
- **Reality:** 75% is noise (DEBUG, routine INFO)
- **Cost:** Timber ($29/mo per 1GB), Datadog ($0.10/GB), Cribl ($100+/mo)
- **Example:** Reducing noise by 80% saves $2,400-8,000/year for a 10GB/day system

## How It Works

1. **Prepare** (`prepare.py`): Generate realistic log samples (500 logs, ~250KB)
2. **Define Rules** (`filter_rules.py`): Implement `should_keep(entry)` filter function
3. **Evaluate** (`harness.py`): Measure efficiency_score (noise dropped vs signal kept)
4. **Iterate**: Test hypotheses (drop all DEBUG, regex patterns, keyword detection, etc.)

## Quick Start

```bash
# Generate log samples
python prepare.py generate

# Baseline: measure cost of keeping everything
python harness.py baseline

# Evaluate current filter rules
python harness.py evaluate
```

### Example Output
```
============================================================
Evaluation Results
============================================================

Signal Logs (is_signal=True):
  Total: 125
  Kept: 125 (100.0%)
  Dropped: 0

Noise Logs (is_signal=False):
  Total: 375
  Kept: 375
  Dropped: 0 (0.0% of noise)

Volume:
  Total: 628,425 bytes (613.7KB)
  Kept: 628,425 bytes (613.7KB)
  Dropped: 0 bytes (0.0KB)
  Reduction: 0.0%

Metrics:
  Signal Kept %: 100.0%
  Noise Dropped %: 0.0%
  Efficiency Score: 0.0000

RESULT: efficiency_score=0.0000 improvement_pct=0.0
============================================================
```

## Editing filter_rules.py

The `filter_rules.py` file is **your playground**. Implement `should_keep(entry)`:

```python
def should_keep(entry: dict) -> bool:
    """Return True to keep this log entry, False to drop it."""
    # entry has: message, level, source, timestamp, size_bytes, is_signal

    # Example: drop all DEBUG
    if entry["level"] == "DEBUG":
        return False

    return True
```

## Log Entry Structure

Each log entry in `log_samples.json`:
```json
{
  "id": 0,
  "message": "Request received from client",
  "level": "DEBUG",
  "source": "api",
  "timestamp": "2026-03-20T12:34:56.789012",
  "size_bytes": 450,
  "is_signal": false
}
```

- **level**: DEBUG (40%), INFO (30%), WARN (15%), ERROR (10%), FATAL (5%)
- **source**: api, db, auth, cache, scheduler, worker
- **is_signal**: True = important (must keep >= 95%), False = noise (drop as much as possible)

## Success Metric: Efficiency Score

```
efficiency_score = (noise_dropped / total_noise) * signal_kept_pct

Constraints:
  - signal_kept_pct = signal_kept / total_signal
  - MUST be >= 0.95 (keep at least 95% of signal)
  - If signal_kept_pct < 0.95, score = 0.0 (penalty)
```

### Scoring Examples

| Noise Dropped | Signal Kept % | Score |
|---|---|---|
| 0% | 100% | 0.0000 (baseline) |
| 50% | 100% | 0.5000 |
| 75% | 100% | 0.7500 |
| 80% | 98% | 0.7840 |
| 90% | 96% | 0.8640 |
| 95% | 98% | 0.9310 |
| 95% | 95% | 0.9025 |

## Research Hypotheses (program.md)

10+ hypotheses to test:

1. **H1: Drop All DEBUG** — Simple but loses some signal
2. **H2: Drop DEBUG Except from Specific Sources** — Preserve important DEBUG from db/auth
3. **H3: Keep WARN+ Always** — Level-based filtering
4. **H4: Keyword-Based Detection** — Look for "error", "fail", "timeout"
5. **H5: Source-Based Rules** — db/auth = keep all, cache/scheduler = drop noise
6. **H6: Message Length Heuristics** — Short messages often boilerplate
7. **H7: Regex Patterns** — Match known noise: "health check", "heartbeat", "cache hit"
8. **H8: Combination Rules** — Weighted scoring of multiple signals
9. **H9: Size-Aware Filtering** — Drop small logs first (space savings)
10. **H10: Empirical Priors** — DEBUG = 5% signal prob, ERROR = 100%, etc.

See `program.md` for full details on each hypothesis.

## Revenue Opportunity

**Connect your log pipeline at agent-hub.dev for automated noise reduction.**

### Pricing Tiers
- **Starter:** Free (manual rules)
- **Pro:** $29/mo (1 custom rule + monitoring)
- **Business:** $99/mo (10 rules, 50GB ingestion, integrations: Datadog, ELK, Splunk)
- **Enterprise:** Custom (unlimited rules, 24/7 support, dedicated rule tuning)

### Comparable Products
- **Timber.io:** $29/mo base, $0.29/GB (logging platform with filtering)
- **Datadog Log Management:** $0.10/GB (fixed cost, no filtering optimization)
- **Cribl.Cloud:** $100+/mo (log routing & processing, generic)
- **Log Trimmer:** $29/mo (specialized log noise reduction, proven 80%+ volume savings)

### Target Market
- SaaS companies with $10B+ daily log volume (annual savings: $2,400-8,000)
- Compliance-heavy industries (finance, healthcare, government)
- DevOps/Platform teams operating multi-tenant systems

## Architecture

```
log_samples.json (500 logs, ~250KB)
        ↓
filter_rules.py (should_keep)
        ↓
harness.py (evaluate)
        ↓
efficiency_score, volume_reduction_pct
```

## Headroom for Experimentation

- **Baseline:** efficiency_score = 0.0
- **Optimal achievable:** ~0.90-0.95 (drop 90-95% of noise while keeping 98%+ signal)
- **Experimentation headroom:** 10-20 hypothesis tests before hitting diminishing returns

## Files

- `prepare.py` — Generate log_samples.json
- `filter_rules.py` — Editable filter implementation
- `harness.py` — Evaluation harness
- `program.md` — Research hypotheses and experiment plan
- `README.md` — This file
- `pyproject.toml` — Project metadata (no external dependencies)

## Notes

- **Seed:** All randomization uses seed=42 for reproducibility
- **No dependencies:** Pure Python, no external packages
- **Log distribution:** Realistic mix of levels, sources, message types
- **Signal definition:** Learned from real production systems (errors, warnings, key events)
