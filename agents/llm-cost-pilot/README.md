# llm-cost-pilot

An AI agent that optimizes LLM API routing costs using [Karpathy's AutoResearch](https://github.com/karpathy/autoresearch) pattern. Point a coding agent at this folder and let it reduce your LLM spend overnight.

## How It Works

The agent follows the 3-primitive design:

| File | Role | Modified by agent? |
|------|------|--------------------|
| `program.md` | Research instructions in plain English | No |
| `router.py` | Request routing logic — the ONE editable file | **Yes** |
| `harness.py` | Evaluation infrastructure | No |

**The metric:** `cost_per_quality` = total_cost / avg_quality (lower is better)

**The loop:**
1. Agent reads `program.md`
2. Edits `router.py` with a new routing strategy
3. Runs `python harness.py evaluate`
4. If cost_per_quality improved and quality >= 0.85 → `git commit`
5. If not → `git reset --hard HEAD`
6. Repeat forever

## Quick Start

```bash
# Install dependencies
pip install pyyaml numpy

# Generate synthetic traffic (1000 requests)
python prepare.py generate

# Run baseline (no optimization)
python harness.py baseline

# Run evaluation with current router
python harness.py evaluate

# Start the agent — point Claude Code at this folder:
# "Read program.md and start optimizing"
```

## Files

```
llm-cost-pilot/
├── program.md        ← Instructions for the AI agent
├── router.py         ← The ONE file the agent modifies
├── harness.py        ← Evaluation infrastructure (fixed)
├── prepare.py        ← Traffic generator (fixed)
├── models.yaml       ← Model catalog with pricing
├── pyproject.toml    ← Dependencies
├── traffic/
│   └── sample.jsonl  ← Generated test traffic
├── results.tsv       ← Experiment log (created by agent)
└── analysis.ipynb    ← Visualize results
```

## Model Catalog

| Model | Provider | Tier | Input $/M | Output $/M |
|-------|----------|------|-----------|------------|
| gpt-5-nano | OpenAI | nano | $0.05 | $0.40 |
| gemini-2.5-flash | Google | nano | $0.15 | $0.60 |
| gpt-5-mini | OpenAI | small | $0.25 | $2.00 |
| deepseek-v3 | DeepSeek | small | $0.27 | $1.10 |
| o3-mini | OpenAI | small | $0.55 | $2.20 |
| claude-haiku-4-5 | Anthropic | small | $0.80 | $4.00 |
| gpt-4o | OpenAI | medium | $2.50 | $10.00 |
| claude-sonnet-4-6 | Anthropic | medium | $3.00 | $15.00 |
| gpt-5.2 | OpenAI | large | $1.75 | $14.00 |
| gemini-3.1-pro | Google | large | $2.00 | $12.00 |
| claude-opus-4-6 | Anthropic | flagship | $5.00 | $25.00 |

## Part of [agent-hub](../../README.md)
