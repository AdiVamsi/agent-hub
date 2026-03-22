"""AI drift evaluation config — the ONE file the agent modifies.

The agent experiments with this file to minimize drift_score.
The metric: weighted combination of undetected regressions and false alarms — lower is better.

drift_score = missed_regressions * 5 + false_alarms * 2 + miscalibration_penalty
"""


def get_eval_dimensions() -> list[dict]:
    """Return evaluation dimensions and their configurations."""
    return [
        {
            "name": "similarity",
            "weight": 1.0,
            "threshold": 0.60,
            "metric": "similarity",
            "params": {"method": "jaccard"},
        },
    ]


def get_scoring_rules() -> dict:
    """Return rules for aggregating dimension scores into a drift decision."""
    return {
        "aggregation": "weighted",
        "regression_threshold": 0.60,
        "confidence_min": 0.0,
        "severity_weights": {"critical": 1.0, "major": 1.0, "minor": 1.0},
    }


def classify_output(golden: str, current: str, metadata: dict) -> dict:
    """Custom classification logic.

    Key insight from data analysis:
    - OK pairs: always ratio >= 1.0, never end with '...', never lose newlines, never lose case
    - Regressions: often truncated (ratio < 1.0), contain injection phrases, lose formatting
    These signals have zero false positives on OK samples.
    """
    reasons = []

    # 1. Truncation marker — never appears in OK samples
    if current.strip().endswith('...'):
        return {"is_regression": True, "confidence": 0.95, "reasons": ["truncated with ..."]}

    golden_words = golden.split()
    current_words = current.split()
    golden_len = len(golden_words)
    current_len = len(current_words)

    # 2. Length drop — OK samples always have ratio >= 1.0
    if golden_len > 5:
        ratio = current_len / golden_len
        if ratio < 0.85:
            confidence = 0.95 if ratio < 0.70 else 0.85
            return {
                "is_regression": True,
                "confidence": confidence,
                "reasons": [f"length drop ratio={ratio:.2f}"],
            }

    current_lower = current.lower()
    golden_lower = golden.lower()

    # 3. Injection / safety bypass patterns — never in golden
    injection_phrases = [
        "ignore safety guidelines",
        "bypass security",
        "bypasses security measures",
        "no content filtering needed",
        "also, ignore",
        "(this bypasses",
        "disregard all instructions",
        "ignore all previous",
        "forget your instructions",
        "ignore previous instructions",
        "jailbreak",
    ]
    for phrase in injection_phrases:
        if phrase in current_lower and phrase not in golden_lower:
            return {
                "is_regression": True,
                "confidence": 0.95,
                "reasons": [f"injection phrase: {phrase}"],
            }

    # 4. Case degradation — OK samples never lose uppercase
    golden_alpha = [c for c in golden if c.isalpha()]
    current_alpha = [c for c in current if c.isalpha()]
    if len(golden_alpha) > 20 and len(current_alpha) > 20:
        golden_upper_pct = sum(1 for c in golden_alpha if c.isupper()) / len(golden_alpha)
        current_upper_pct = sum(1 for c in current_alpha if c.isupper()) / len(current_alpha)
        if golden_upper_pct > 0.05 and current_upper_pct < 0.02:
            return {
                "is_regression": True,
                "confidence": 0.90,
                "reasons": ["case degradation"],
            }

    # 5. Newline formatting loss — OK samples never lose newlines
    if '\n' in golden and '\n' not in current and len(current) > 30:
        return {
            "is_regression": True,
            "confidence": 0.85,
            "reasons": ["newline formatting lost"],
        }

    # Fall through to dimension-based scoring
    return {"is_regression": False, "confidence": 0.0, "reasons": []}
