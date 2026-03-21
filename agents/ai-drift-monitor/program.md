# AutoResearch: AI Drift Monitor

You are optimizing an LLM evaluation pipeline to detect model output degradation (drift). Your goal: minimize `drift_score` by tuning `eval_config.py`.

## Context

AI models drift over time—outputs change in quality, consistency, tone, and accuracy. Most teams detect this manually, too late. You are building an automated drift detector that learns from your eval data.

**The Pitch:** "I pointed an AI agent at my LLM evaluation pipeline. It ran 50 experiments overnight. My drift detection catches 94% of regressions now, up from 61%."

## Files

- **eval_config.py** (EDIT THIS) — The only file you modify. Contains:
  - `get_eval_dimensions()` — evaluation rules (metrics, thresholds, weights)
  - `get_scoring_rules()` — aggregation logic and regression thresholds
  - `classify_output()` — custom comparison logic you can add

- **harness.py** (READ ONLY) — Evaluation harness that:
  - Loads eval_dataset.json (200 golden/current output pairs)
  - Applies eval_config rules to each pair
  - Computes `drift_score` (lower = better)
  - Reports precision/recall/f1
  - CLI: `python harness.py evaluate`, `baseline`, `report`

- **eval_dataset.json** (generated) — 200 evaluation pairs:
  - 60% "ok" (no regression)
  - 40% "regression" (degraded outputs)
  - Diverse task types: summarization, qa, classification, extraction, generation, code
  - Categories: factual, creative, technical, conversational

- **prepare.py** — Data generation script. Run: `python prepare.py generate`

## Baseline

Before you start, establish the baseline:

```bash
python prepare.py generate           # Create eval_dataset.json
python harness.py baseline           # Show starting drift_score
python harness.py evaluate           # Full RESULT line
```

Current baseline config:
- Single "overall_quality" dimension
- Jaccard similarity only (word overlap)
- Threshold 0.5, no confidence filtering
- `classify_output()` flags nothing

Expected: drift_score ~120–150, precision/recall near 0.

## Your Optimization Task

Minimize `drift_score = missed_regressions * 5 + false_alarms * 2 + miscalibration_penalty`

Where:
- **missed_regressions** = real regressions the config failed to detect (costs 5 points each)
- **false_alarms** = non-regressions falsely flagged (costs 2 points each)
- **miscalibration_penalty** = how far off thresholds/confidence are from optimal (0–50 points)

The metric penalizes missing regressions more than false alarms (5:2 ratio).

### Available Metrics

In `get_eval_dimensions()`, you can use these metrics:

1. **similarity** (params: method="jaccard"|"cosine")
   - Word-overlap based similarity [0, 1]
   - Good for: general output quality
   - Threshold: lower = stricter

2. **keyword** (params: required=[], forbidden=[])
   - Check for required/forbidden keywords
   - Good for: safety checks, format validation
   - Threshold: proportion of required keywords found

3. **length** (params: min_ratio=0.5, max_ratio=1.5)
   - Compare output lengths (word count)
   - Detects truncation, over-generation
   - Good for: spotting incomplete outputs
   - Threshold: penalizes length drift

4. **sentiment** (params: positive=[], negative=[])
   - Simple word-counting sentiment
   - Good for: tone consistency
   - Threshold: proportion of positive words

5. **format** (params: checks=["json", "code_block", "bullets", "paragraphs"])
   - Check for structural elements
   - Good for: structured outputs (code, JSON)
   - Threshold: fraction of checks passed

### Optimization Strategies

#### 1. Multi-Dimension Analysis
- Add multiple dimensions (quality, format, length, safety)
- Weight them by importance
- Example: code tasks need format checking; factual tasks need keyword checking

#### 2. Threshold Tuning
- Start broad (threshold=0.5), then calibrate
- Lower threshold = stricter (flags more as regression)
- High threshold = lenient (allows more variation)
- Sweet spot balances precision and recall

#### 3. Category-Specific Rules
- Different tasks benefit from different rules
- Summarization: use length + similarity
- Code: use format checking + code blocks
- Factual QA: use keyword presence (key facts)
- Safety: use forbidden keywords

#### 4. Confidence Calibration
- `classify_output()` can add custom logic
- Return high confidence when you're sure it's a regression
- Low confidence when uncertain
- The harness blends custom logic with threshold-based logic

#### 5. Aggregation Strategy
- "weighted": sum(score * weight) / total_weight
- "mean": average dimension scores
- "min": only flag if ALL dimensions indicate regression
- "max": flag if ANY dimension indicates regression
- Choose based on your risk tolerance

#### 6. Custom classify_output() Logic
- Implement domain-specific comparison logic
- Example: for code, parse structure and compare
- Example: for factual QA, extract key claims and verify
- Return confidence to weight the prediction

### Example Experiment: Adding Format Detection for Code

```python
def get_eval_dimensions() -> list[dict]:
    return [
        {
            "name": "quality",
            "weight": 0.6,
            "threshold": 0.5,
            "metric": "similarity",
            "params": {"method": "jaccard"},
        },
        {
            "name": "format",
            "weight": 0.4,
            "threshold": 0.7,
            "metric": "format",
            "params": {"checks": ["code_block"]},
        },
    ]
```

This adds format checking with 40% weight. Dimensions are aggregated as weighted mean.

### Example Experiment: Custom Length Detection

```python
def get_eval_dimensions() -> list[dict]:
    return [
        {
            "name": "overall",
            "weight": 0.8,
            "threshold": 0.5,
            "metric": "similarity",
            "params": {"method": "cosine"},
        },
        {
            "name": "length",
            "weight": 0.2,
            "threshold": 0.6,
            "metric": "length",
            "params": {"min_ratio": 0.6, "max_ratio": 1.4},
        },
    ]
```

This catches truncated outputs (length < 60% of golden).

## Experiment Loop

1. **Baseline** (1 min): `python harness.py baseline`
2. **Edit eval_config.py** (2 min): Change metrics, thresholds, dimensions
3. **Evaluate** (10 sec): `python harness.py evaluate` → RESULT line
4. **Analyze** (1 min): Does drift_score improve? What regressions did it miss?
5. **Report** (optional): `python harness.py report` for per-category breakdown
6. **Iterate** (repeat 2–5)

Target: **drift_score < 30** with **precision > 0.85, recall > 0.90**

Constraints:
- Edit ONLY eval_config.py
- Each experiment should complete in < 30 seconds
- You have ~50 experiments budget (time/resources)
- Focus on high-impact changes

## Success Metrics

Your goal is to reach:
- `drift_score < 30` (down from ~120)
- `precision > 0.85` (avoid false alarms)
- `recall > 0.90` (catch real regressions)
- `f1 > 0.88` (balanced performance)

Example target: `drift_score=12.5 precision=0.91 recall=0.94 f1=0.92`

## Quick Start

```bash
cd /sessions/zealous-lucid-cori/mnt/outputs/agent-hub/agents/ai-drift-monitor

# 1. Generate dataset
python prepare.py generate

# 2. Baseline
python harness.py baseline

# 3. Make a change to eval_config.py

# 4. Evaluate
python harness.py evaluate

# 5. If improved, iterate. Else, try a different approach.
```

Good luck! The agent that optimizes drift detection is valuable infrastructure—it catches regressions before they affect users.
