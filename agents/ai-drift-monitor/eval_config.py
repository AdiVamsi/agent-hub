"""AI drift evaluation config — the ONE file the agent modifies.

The agent experiments with this file to minimize drift_score.
The metric: weighted combination of undetected regressions and false alarms — lower is better.

drift_score = missed_regressions * 5 + false_alarms * 2 + miscalibration_penalty

The config defines:
- Evaluation dimensions (quality, consistency, safety, format compliance, etc.)
- Scoring weights per dimension
- Threshold calibration for flagging drift
- Rules for which output patterns indicate regression
"""


def get_eval_dimensions() -> list[dict]:
    """Return evaluation dimensions and their configurations.

    Each dimension is a dict with:
        name: str — dimension name
        weight: float — importance weight (0-1, should sum to ~1.0)
        threshold: float — drift threshold (0-1). Score below this = regression detected
        metric: str — "similarity"|"keyword"|"length"|"sentiment"|"format"
        params: dict — metric-specific parameters

    Returns:
        List of evaluation dimension configs.
    """
    # BASELINE: single dimension, poor calibration
    return [
        {
            "name": "overall_quality",
            "weight": 1.0,
            "threshold": 0.5,
            "metric": "similarity",
            "params": {"method": "jaccard"},
        },
    ]


def get_scoring_rules() -> dict:
    """Return rules for aggregating dimension scores into a drift decision.

    Returns:
        Dict with:
            aggregation: str — "mean"|"weighted"|"min"|"max"
            regression_threshold: float — overall score below this = regression
            confidence_min: float — minimum confidence to flag (0-1)
            severity_weights: dict — weights for different severity levels
    """
    return {
        "aggregation": "mean",
        "regression_threshold": 0.5,
        "confidence_min": 0.0,
        "severity_weights": {"critical": 1.0, "major": 1.0, "minor": 1.0},
    }


def classify_output(golden: str, current: str, metadata: dict) -> dict:
    """Custom classification logic for comparing outputs.

    The agent can add sophisticated comparison logic here.

    Args:
        golden: the reference (good) output
        current: the current model output to evaluate
        metadata: dict with task_type, difficulty, category, etc.

    Returns:
        dict with:
            is_regression: bool — True if current is worse than golden
            confidence: float — 0-1 confidence in the assessment
            reasons: list[str] — why this was flagged
    """
    # BASELINE: flag nothing — no drift detection
    return {
        "is_regression": False,
        "confidence": 0.0,
        "reasons": [],
    }
