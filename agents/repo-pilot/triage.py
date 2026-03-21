"""Issue triage rules — the ONE file the agent modifies.

The agent experiments with this file to maximize issues_resolved.
The metric: correctly triaged issues (label + priority + duplicate detection) — higher is better.

issues_resolved = correct_labels + correct_priorities + correct_duplicates - wrong_labels - wrong_priorities - false_duplicates

Each issue has: title, body, labels (to predict), priority (to predict), is_duplicate (to predict).
"""


def get_label_rules() -> list[dict]:
    """Return rules for auto-labeling issues.

    Each rule is a dict with:
        label: str — the label to apply
        keywords: list[str] — if any keyword found in title+body, apply this label
        exclude_keywords: list[str] — don't apply if these are found
        priority_boost: int — bonus to priority if this label matches

    Returns:
        List of labeling rules.
    """
    # BASELINE: no rules — everything gets "needs-triage"
    return []


def get_priority_rules() -> dict:
    """Return rules for auto-prioritizing issues.

    Returns:
        Dict with:
            default_priority: str — "low"|"medium"|"high"|"critical"
            keyword_overrides: dict[str, str] — keyword -> priority override
            label_priorities: dict[str, str] — label -> priority
    """
    return {
        "default_priority": "medium",
        "keyword_overrides": {},
        "label_priorities": {},
    }


def get_duplicate_rules() -> dict:
    """Return rules for detecting duplicate issues.

    Returns:
        Dict with:
            similarity_threshold: float — 0-1, title similarity to flag as duplicate
            title_weight: float — weight for title similarity
            body_weight: float — weight for body similarity
            same_label_bonus: float — bonus if both have same label
            keyword_groups: list[list[str]] — groups of equivalent keywords
    """
    return {
        "similarity_threshold": 0.95,  # very conservative — catches almost nothing
        "title_weight": 1.0,
        "body_weight": 0.0,
        "same_label_bonus": 0.0,
        "keyword_groups": [],
    }


def classify_issue(title: str, body: str) -> dict:
    """Custom classification logic for an issue.

    Args:
        title: issue title
        body: issue body text

    Returns:
        dict with:
            labels: list[str] — predicted labels
            priority: str — predicted priority
            is_duplicate_of: int or None — ID of duplicate issue, or None
            confidence: float — 0-1
    """
    # BASELINE: no classification — returns defaults
    return {
        "labels": ["needs-triage"],
        "priority": "medium",
        "is_duplicate_of": None,
        "confidence": 0.0,
    }
