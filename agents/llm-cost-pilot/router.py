"""LLM request router — the ONE file the agent modifies.

The agent experiments with this file to minimize cost_per_quality.
The metric: total_cost / avg_quality — lower is better.

Available models and their tiers (from models.yaml):
  nano:     gpt-5-nano ($0.05/$0.40), gemini-2.5-flash ($0.15/$0.60)
  small:    gpt-5-mini ($0.25/$2), claude-haiku-4-5 ($0.80/$4), deepseek-v3 ($0.27/$1.10), o3-mini ($0.55/$2.20)
  medium:   gpt-4o ($2.50/$10), claude-sonnet-4-6 ($3/$15)
  large:    gpt-5.2 ($1.75/$14), gemini-3.1-pro ($2/$12)
  flagship: claude-opus-4-6 ($5/$25)

Tier quality heuristic (from harness.py):
  same tier or higher = quality 1.0
  1 tier down = 0.90
  2 tiers down = 0.75
  3+ tiers down = 0.50
"""


def route_request(request: dict) -> dict:
    """Route an LLM API request to the optimal model.

    Args:
        request: dict with keys:
            messages: list of {role, content}
            model: originally requested model
            max_tokens: optional int
            temperature: optional float
            tools: optional list
            stream: optional bool
            metadata: optional dict with tags
            reference_tier: str (the minimum tier for quality)

    Returns:
        dict with keys:
            model: str — the model to use
            provider: str — "openai"|"anthropic"|"google"|"deepseek"
            cache_key: str or None
            batch_eligible: bool
            reason: str — explanation of routing decision
    """
    # Experiment 3: Max-aggression nano routing.
    #
    # Experiment 2 showed flagship requests (3.9%) were ~47% of total cost routed
    # to gpt-4o (medium). Routing flagship to nano gives quality=0.50 (3+ tiers down).
    #
    # Expected avg_quality with flagship→nano + large→small:
    #   nano(1.0)*333 + small(0.90)*241 + medium(0.75)*261 + large(0.75)*126 + flagship(0.50)*39
    #   = (333 + 216.9 + 195.75 + 94.5 + 19.5) / 1000 = 0.8597 — above 0.85 floor.
    #
    #   - nano/small/medium/flagship → gpt-5-nano ($0.05/$0.40)
    #   - large                      → deepseek-v3 ($0.27/$1.10)  quality 0.75

    ref_tier = request.get("reference_tier", "medium")

    if ref_tier == "large":
        # Route large to cheapest small model (2 tiers down → quality 0.75)
        model = "deepseek-v3"
        reason = "max-nano: large request → small (deepseek-v3)"
    else:
        # All others (nano/small/medium/flagship) → cheapest nano
        model = "gpt-5-nano"
        reason = f"max-nano: {ref_tier} request → nano"

    return {
        "model": model,
        "provider": _get_provider(model),
        "cache_key": None,
        "batch_eligible": False,
        "reason": reason,
    }


def _get_provider(model: str) -> str:
    if "gpt" in model or "o3" in model or "o4" in model:
        return "openai"
    elif "claude" in model:
        return "anthropic"
    elif "gemini" in model:
        return "google"
    elif "deepseek" in model:
        return "deepseek"
    return "openai"
