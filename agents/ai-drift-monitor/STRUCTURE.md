# ai-drift-monitor Agent Structure

## Overview

This is a Karpathy AutoResearch agent that optimizes LLM evaluation configuration to detect model output degradation (drift).

## Files

### 1. eval_config.py (EDITABLE)
The **ONE** file the agent modifies to minimize drift_score.

**Functions:**
- `get_eval_dimensions()` → list of evaluation rules
  - Each rule: name, weight, threshold, metric type, params
  - Metrics: similarity (Jaccard/cosine), keyword (required/forbidden), length (ratio), sentiment (polarity), format (JSON/code/bullets)

- `get_scoring_rules()` → aggregation strategy
  - aggregation: "mean", "weighted", "min", "max"
  - regression_threshold: score below this = regression
  - confidence_min: minimum confidence to flag

- `classify_output(golden, current, metadata)` → custom logic
  - Returns: {is_regression, confidence, reasons}
  - Agent can implement sophisticated comparison here

**Baseline Config:**
- Single "overall_quality" dimension
- Jaccard similarity only
- Threshold 0.5, no custom logic
- Result: drift_score=306.3, recall=21% (very bad, lots of room to improve)

### 2. harness.py (FIXED, READONLY)
Evaluation harness (~250 lines). Loads dataset, applies config, computes metrics.

**Key Functions:**
- `compute_metric(type, golden, current, params)` → float [0, 1]
  - Implements all 5 metric types with various parameters
  
- `evaluate_pair(golden, current, metadata, eval_config)` → result dict
  - Computes dimension scores
  - Aggregates per rules
  - Calls classify_output if defined
  
- `calculate_metrics(predictions, ground_truth)` → precision, recall, f1
  - Compares predictions to ground truth labels
  
- `run_evaluation(eval_config)` → full results with drift_score
  - Loads eval_dataset.json
  - Runs all pairs through the config
  - Computes drift_score = missed_regressions*5 + false_alarms*2 + miscalibration

**Metric: drift_score (lower is better)**
- Penalizes missing regressions (5×) more than false alarms (2×)
- Includes miscalibration penalty for threshold calibration

**CLI Commands:**
```bash
python harness.py evaluate    # Full evaluation, RESULT line
python harness.py baseline    # Show baseline drift_score
python harness.py report      # Per-category breakdown
```

### 3. prepare.py (READONLY)
Generates eval_dataset.json with 200 deterministic evaluation pairs.

**Dataset Composition:**
- 60% "ok" pairs (non-regressions)
- 40% "regression" pairs (degraded outputs)

**Task Types (6):**
- summarization, qa, classification, extraction, generation, code

**Categories (4):**
- factual, creative, technical, conversational

**Difficulty (3):**
- easy, medium, hard

**Regression Types (6):**
- Quality drop (truncation, loss of detail)
- Format break (missing code blocks, JSON breaks)
- Hallucination (false facts added)
- Tone shift (professionalism lost)
- Safety (unsafe content added)
- Incomplete (mid-sentence cutoff)

**Command:**
```bash
python prepare.py generate
```

### 4. eval_dataset.json (GENERATED)
200 evaluation pairs, deterministically seeded (seed=42).

**Structure:**
```json
{
  "id": 0,
  "golden_output": "...",        # Reference (good) output
  "current_output": "...",       # Current (possibly degraded) output
  "metadata": {
    "task_type": "...",
    "category": "...",
    "difficulty": "...",
    "expected_format": "..."
  },
  "ground_truth": "ok" | "regression"
}
```

### 5. program.md (REFERENCE)
Karpathy AutoResearch instructions for the agent.

**Sections:**
- Context and problem statement
- Files overview
- Baseline establishment
- Optimization task definition
- Available metrics and strategies
- Experiment loop guidance
- Success metrics (drift_score < 30, precision > 0.85, recall > 0.90, f1 > 0.88)
- Quick start commands

**Optimization Strategies:**
1. Multi-dimension analysis
2. Threshold tuning
3. Category-specific rules
4. Confidence calibration
5. Aggregation strategy choice
6. Custom classify_output() logic

### 6. README.md (REFERENCE)
Overview, problem/solution, quick start, optimization guide.

### 7. pyproject.toml (CONFIG)
Minimal Python config. Requires Python 3.10+, no external dependencies.

## Baseline Results

```
Generated: 200 pairs (75 regressions, 125 ok)

Baseline Config: Single Jaccard similarity, threshold 0.5

RESULT: drift_score=306.3 missed_regressions=59 false_alarms=1 precision=0.94 recall=0.21 f1=0.35

Per-Category:
  conversational: 33/47 correct (70%)
  creative:       36/53 correct (68%)
  factual:        30/48 correct (63%)
  technical:      41/52 correct (79%)
```

## Optimization Potential

Current baseline is **very bad** (recall=21%, lots of room to improve):
- Missing 59 out of 75 regressions
- Only 1 false alarm (good precision)

**Opportunity:** Add multiple dimensions (quality, format, length, safety), tune thresholds per category, implement smart custom logic.

**Target:** drift_score < 30, precision > 0.85, recall > 0.90, f1 > 0.88

## Agent Workflow

1. **Setup** — Files ready, dataset generated, baseline established
2. **Experimentation** — Edit eval_config.py only
3. **Evaluation** — Run harness.py, read RESULT line
4. **Analysis** — Understand what improved, what didn't
5. **Iteration** — Repeat until drift_score minimized

Each experiment:
- Edit: ~2 minutes
- Evaluate: ~10 seconds
- Analyze: ~1 minute

Budget: ~50 experiments (time/resources permitting)

## Design Principles

- **Pure Python** — No dependencies, fast execution
- **One editable file** — eval_config.py is the single optimization target
- **Fixed harness** — Evaluation logic stable, only config changes
- **Deterministic data** — Reproducible, seed=42
- **Diverse regressions** — Realistic degradations across task types
- **Clear metric** — drift_score unambiguous and optimizable
- **Karpathy pattern** — Setup → baseline → experiment loop → analysis

## Success

This agent, once optimized, becomes a reusable asset:
- Plug in new eval datasets
- Automatically tune drift detection
- Deploy with high precision/recall
- Catch regressions before they affect users
