"""Issue triage rules — the ONE file the agent modifies.

The agent experiments with this file to maximize issues_resolved.
The metric: correctly triaged issues (label + priority + duplicate detection) — higher is better.

issues_resolved = correct_labels*2 + correct_priorities*2 + correct_duplicates*3
               - wrong_labels*1 - wrong_priorities*1 - wrong_duplicates*3

NOTE: The harness only calls classify_issue(title, body). The helper functions
(get_label_rules, get_priority_rules, get_duplicate_rules) are not used by harness.py.
All logic must live in classify_issue().
"""


def get_label_rules() -> list[dict]:
    """Not called by harness — logic is in classify_issue()."""
    return []


def get_priority_rules() -> dict:
    """Not called by harness — logic is in classify_issue()."""
    return {
        "default_priority": "medium",
        "keyword_overrides": {},
        "label_priorities": {},
    }


def get_duplicate_rules() -> dict:
    """Not called by harness — logic is in classify_issue()."""
    return {
        "similarity_threshold": 0.95,
        "title_weight": 1.0,
        "body_weight": 0.0,
        "same_label_bonus": 0.0,
        "keyword_groups": [],
    }


def classify_issue(title: str, body: str) -> dict:
    """Classify an issue into label + priority. All logic lives here.

    Strategy: keyword-based label detection with priority ordering.
    Predict exactly ONE label to maximize precision (avoid wrong-label penalties).
    """
    text = (title + " " + body).lower()

    # --- Label detection (ordered by specificity/priority) ---

    # Security — highest priority label, clear keywords
    if any(kw in text for kw in [
        "security", "vulnerability", "xss", "sql injection", "injection",
        "exploit", "cve-", "cve ", "attack", "privilege escalation",
        "csrf", "remote code execution", "rce", "authentication bypass",
        "authorization bypass", "token leak", "sensitive data exposure",
    ]):
        label = "security"

    # Performance — clear performance keywords
    elif any(kw in text for kw in [
        "slow", "performance", "memory leak", "lag", "optimize", "throughput",
        "bottleneck", "oom", "out of memory", "high cpu", "high memory",
        "latency issue", "response time", "takes too long", "timeout issue",
        "profil", "benchmark",
    ]):
        label = "performance"

    # Breaking change — explicit breaking signals
    elif any(kw in text for kw in [
        "breaking change", "breaking-change", "migration guide", "deprecated",
        "api change", "backward compatibility", "backward incompatible",
        "semver", "major version bump", "breaks existing",
    ]):
        label = "breaking-change"

    # Docs — documentation keywords
    elif any(kw in text for kw in [
        "documentation", "docs update", "update docs", "update readme",
        "typo in", "missing docs", "missing documentation", "readme",
        "tutorial", "add example", "example code", "clarify docs",
        "improve docs", "wiki",
    ]):
        label = "docs"

    # Bug — error/crash/failure keywords (very common, check after niche labels)
    elif any(kw in text for kw in [
        "error:", "runtimeerror", "typeerror", "attributeerror", "valueerror",
        "keyerror", "indexerror", "nameerror", "importerror", "oserror",
        "crash", "crashes", "exception", "traceback", "stack trace",
        "throws unexpected", "throws an exception", "not working",
        "broken", "regression", "incorrect behavior", "wrong output",
        " bug ", "bug:", "segfault", "panic", "unexpected exception",
        "unexpected error", "fails with", "fails when",
    ]):
        label = "bug"

    # Question — help/clarification requests
    elif any(kw in text for kw in [
        "how to ", "how do i", "how can i", "how do you",
        "best practice", "what is the", "what's the best",
        "is it possible", "can i ", "should i ", "wondering if",
        "need help", "help with", "clarify", "confused about",
        "question:", "usage help",
    ]):
        label = "question"

    # Feature request — improvement/addition requests
    elif any(kw in text for kw in [
        "feature request", "new feature", "add support for", "add support to",
        "implement ", "i'd like to request", "would be nice", "would be great",
        "it would be great", "enhancement request", "request for",
        "please add", "could you add", "wish list", "proposal:",
        "feature:", "rfe:",
    ]):
        label = "feature"

    # Broader feature/improvement keywords (lower confidence)
    elif any(kw in text for kw in [
        "add ", "support for", "enable ", "allow ", "new option",
        "improve ", "enhancement", "suggestion",
    ]):
        label = "feature"

    # Broader question keywords
    elif any(kw in text for kw in [
        "help", "question", "ask", "guidance",
    ]):
        label = "question"

    else:
        label = "needs-triage"

    # --- Priority detection ---

    # Security always critical
    if label == "security":
        priority = "critical"

    # Critical override keywords (apply to any label)
    elif any(kw in text for kw in [
        "critical", "urgent", "blocker", "blocking my work",
        "blocking production", "blocks my", "data loss", "data corruption",
        "production down", "service down", "concurrent requests",
        "stack trace attached",
    ]):
        priority = "critical"

    # Label-based priority
    elif label == "bug":
        # High-confidence critical bug signals
        if any(kw in text for kw in [
            "concurrent", "stack trace", "production issue",
            "happens every time", "reproducible every",
        ]):
            priority = "critical"
        # Standard bug quality signals → high
        elif any(kw in text for kw in [
            "expected behavior", "actual behavior",
            "expected: success", "actual: failure",
            "expected:", "actual:",
        ]):
            priority = "high"
        else:
            priority = "medium"

    elif label == "performance":
        priority = "high"

    elif label == "breaking-change":
        priority = "high"

    elif label == "feature":
        if any(kw in text for kw in ["critical", "urgent", "enterprise", "compliance"]):
            priority = "high"
        else:
            priority = "medium"

    elif label in ("docs", "question"):
        priority = "low"

    else:
        priority = "medium"

    return {
        "labels": [label],
        "priority": priority,
        "is_duplicate_of": None,
        "confidence": 0.75,
    }
