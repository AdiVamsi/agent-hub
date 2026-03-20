#!/usr/bin/env python3
"""Evaluation harness for llm-cost-pilot. DO NOT MODIFY.

Loads traffic, routes each request through router.py, scores quality and cost,
and prints a greppable RESULT line.

Usage:
    python harness.py evaluate   — run full evaluation
    python harness.py baseline   — show cost with no routing (original models)
"""

import json
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent
MODELS_PATH = ROOT / "models.yaml"
TRAFFIC_PATH = ROOT / "traffic" / "sample.jsonl"


def load_models():
    with open(MODELS_PATH) as f:
        data = yaml.safe_load(f)
    return data["models"], data["tier_ranking"]


def load_traffic():
    requests = []
    with open(TRAFFIC_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                requests.append(json.loads(line))
    return requests


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def estimate_tokens(messages: list) -> tuple[int, int]:
    """Estimate input and output tokens from messages (~4 chars per token)."""
    input_chars = sum(len(m.get("content", "")) for m in messages)
    input_tokens = max(input_chars // 4, 10)
    # Estimate output as roughly proportional to input, capped
    output_tokens = min(input_tokens, 500)
    return input_tokens, output_tokens


def calculate_cost(model_name: str, input_tokens: int, output_tokens: int,
                   models: dict) -> float:
    """Calculate cost in dollars for a request."""
    if model_name not in models:
        # Unknown model — assume medium-tier pricing
        return (input_tokens / 1_000_000) * 2.50 + (output_tokens / 1_000_000) * 10.00
    m = models[model_name]
    input_cost = (input_tokens / 1_000_000) * m["input_cost_per_m"]
    output_cost = (output_tokens / 1_000_000) * m["output_cost_per_m"]
    return input_cost + output_cost


def quality_score(routed_tier: str, reference_tier: str, tier_ranking: dict) -> float:
    """Score quality based on how the routed model's tier compares to the reference.

    same tier or higher → 1.0
    1 tier below → 0.90
    2 tiers below → 0.75
    3+ tiers below → 0.50
    """
    routed_rank = tier_ranking.get(routed_tier, 2)
    ref_rank = tier_ranking.get(reference_tier, 2)
    diff = ref_rank - routed_rank  # positive means we went lower
    if diff <= 0:
        return 1.0
    elif diff == 1:
        return 0.90
    elif diff == 2:
        return 0.75
    else:
        return 0.50


def get_model_tier(model_name: str, models: dict) -> str:
    """Get the tier for a model name."""
    if model_name in models:
        return models[model_name]["tier"]
    # Guess from name
    if "nano" in model_name or "flash" in model_name:
        return "nano"
    if "mini" in model_name or "haiku" in model_name:
        return "small"
    if "opus" in model_name:
        return "flagship"
    if "pro" in model_name or "5.2" in model_name:
        return "large"
    return "medium"


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def evaluate(use_router: bool = True):
    """Run evaluation. If use_router=False, use original models (baseline)."""
    models, tier_ranking = load_models()
    traffic = load_traffic()

    if not traffic:
        print("ERROR: No traffic data. Run: python prepare.py generate")
        sys.exit(1)

    if use_router:
        from router import route_request

    total_cost = 0.0
    baseline_cost = 0.0
    quality_scores = []

    for req in traffic:
        input_tokens, output_tokens = estimate_tokens(req.get("messages", []))
        max_tokens = req.get("max_tokens", 500)
        output_tokens = min(output_tokens, max_tokens)

        # Baseline cost (original model)
        original_model = req.get("model", "gpt-4o")
        b_cost = calculate_cost(original_model, input_tokens, output_tokens, models)
        baseline_cost += b_cost

        if use_router:
            result = route_request(req)
            routed_model = result.get("model", original_model)
        else:
            routed_model = original_model

        # Cost
        cost = calculate_cost(routed_model, input_tokens, output_tokens, models)
        total_cost += cost

        # Quality
        routed_tier = get_model_tier(routed_model, models)
        ref_tier = req.get("reference_tier", "medium")
        q = quality_score(routed_tier, ref_tier, tier_ranking)
        quality_scores.append(q)

    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    cost_per_quality = total_cost / avg_quality if avg_quality > 0 else float("inf")
    savings_pct = ((baseline_cost - total_cost) / baseline_cost * 100) if baseline_cost > 0 else 0

    label = "EVALUATE" if use_router else "BASELINE"
    print(f"\n{'='*60}")
    print(f"  {label} RESULTS")
    print(f"{'='*60}")
    print(f"  Requests evaluated:  {len(traffic)}")
    print(f"  Baseline cost:       ${baseline_cost:.4f}")
    print(f"  Routed cost:         ${total_cost:.4f}")
    print(f"  Savings:             {savings_pct:.1f}%")
    print(f"  Avg quality:         {avg_quality:.4f}")
    print(f"  Cost per quality:    ${cost_per_quality:.4f}")
    print(f"{'='*60}\n")

    # Greppable result line
    print(f"RESULT: total_cost={total_cost:.4f} avg_quality={avg_quality:.4f} "
          f"cost_per_quality={cost_per_quality:.4f} savings_pct={savings_pct:.1f} "
          f"requests={len(traffic)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python harness.py [evaluate|baseline]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "evaluate":
        evaluate(use_router=True)
    elif cmd == "baseline":
        evaluate(use_router=False)
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python harness.py [evaluate|baseline]")
        sys.exit(1)
