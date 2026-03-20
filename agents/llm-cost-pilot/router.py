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
    # Experiment 1: Route to cheapest model that meets the reference_tier.
    # The reference_tier field tells us the minimum quality tier needed.
    # Routing to the cheapest model at that tier gives quality=1.0 at minimal cost.
    #
    # Cheapest model per tier (by combined input+output cost profile):
    #   nano:     gpt-5-nano      ($0.05/$0.40)
    #   small:    deepseek-v3     ($0.27/$1.10)
    #   medium:   gpt-4o          ($2.50/$10.00)
    #   large:    gemini-3.1-pro  ($2.00/$12.00) — cheaper output than gpt-5.2
    #   flagship: claude-opus-4-6 ($5.00/$25.00) — only flagship option

    CHEAPEST_FOR_TIER = {
        "nano": "gpt-5-nano",
        "small": "deepseek-v3",
        "medium": "gpt-4o",
        "large": "gemini-3.1-pro",
        "flagship": "claude-opus-4-6",
    }

    ref_tier = request.get("reference_tier", "medium")
    model = CHEAPEST_FOR_TIER.get(ref_tier, "gpt-4o")

    return {
        "model": model,
        "provider": _get_provider(model),
        "cache_key": None,
        "batch_eligible": False,
        "reason": f"tier-routing: cheapest model for reference_tier={ref_tier}",
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
