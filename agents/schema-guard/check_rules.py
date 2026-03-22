"""Schema Guard — editable file.

Available data: schema_changes.json with 100 schema change pairs.

Your job: implement is_breaking_change(change) -> dict with:
  - breaking: bool (is this a breaking change?)
  - severity: str ("critical"/"major"/"minor"/"none")
  - reason: str (explanation)

The harness scores:
  - Correctly identified breaking: +1
  - Correctly identified non-breaking: +1
  - Missed breaking (false negative): -2 (dangerous!)
  - False alarm (false positive): -0.5 (annoying but not dangerous)
  - Correct severity on breaking changes: +0.5 bonus

Metric: detection_score (sum of scores) — HIGHER is better.
Baseline: always return breaking=False (misses everything).
"""


def is_breaking_change(change: dict) -> dict:
    """Analyze a schema change.

    Args:
        change: dict with keys:
            - change_id: str
            - endpoint: str (e.g., "/users/{id}")
            - method: str (GET/POST/PUT/DELETE/PATCH)
            - version_from, version_to: str
            - old_schema: dict with fields (name, type, required, description, ...)
            - new_schema: dict with fields (or None if field removed)
            - change_type: str (one of the 10 types)

    Returns:
        dict with:
            - breaking: bool
            - severity: str ("critical"/"major"/"minor"/"none")
            - reason: str (explanation)

    HYPOTHESIS LIST (to implement):
    1. Field removal is always breaking
    2. Type changes are breaking (string->int, bool->string, etc.)
    3. Making a field required that was optional is breaking
    4. Removing enum values (narrowing) is breaking
    5. Removing nullable is breaking (null was valid, now isn't)
    6. Format changes can be breaking (email->uuid breaks consumers)
    7. Field additions that are NOT required are NOT breaking
    8. Safe additions and defaults are non-breaking

    SEVERITY SCORING:
    - critical: field removed, or required field removal, or type change on core fields
    - major: type change on non-critical fields, enum narrowing, nullable removed
    - minor: format changes, renames, default changes
    - none: safe additions
    """

    # BASELINE: always say non-breaking
    return {
        "breaking": False,
        "severity": "none",
        "reason": "No check implemented"
    }
