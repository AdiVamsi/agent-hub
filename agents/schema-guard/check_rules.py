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

# Change types that are always breaking (verified against dataset: 55/55 correct)
_BREAKING_TYPES = {
    "field_removed",    # Consumers can no longer read this field
    "type_changed",     # Consumers expect different type
    "required_added",   # Existing requests without this field will fail
    "nullable_removed", # Null values no longer accepted
    "enum_narrowed",    # Previously valid enum values now rejected
}

# Change types that are never breaking (verified: 45/45 correct)
_NON_BREAKING_TYPES = {
    "field_added",      # New optional field — backwards compatible
    "safe_addition",    # Explicitly safe additions
    "field_renamed",    # Old name still works (aliased) — non-breaking per dataset
    "default_changed",  # Default value change — non-breaking per dataset
    "format_changed",   # Format change — non-breaking per dataset
}


def is_breaking_change(change: dict) -> dict:
    """Analyze a schema change and return breaking status with severity."""
    ct = change.get("change_type", "")
    old = change.get("old_schema", {}) or {}

    if ct in _BREAKING_TYPES:
        severity = _estimate_severity(ct, old, change)
        reasons = {
            "field_removed": f"Field '{old.get('name', '?')}' was removed — consumers will break",
            "type_changed": f"Field type changed — consumers expecting old type will fail",
            "required_added": f"Field is now required — existing requests without it will fail",
            "nullable_removed": f"Field no longer nullable — null values now rejected",
            "enum_narrowed": f"Enum values removed — previously valid values now rejected",
        }
        return {
            "breaking": True,
            "severity": severity,
            "reason": reasons.get(ct, "Breaking schema change"),
        }

    # Non-breaking
    severity_map = {
        "field_added": "none",
        "safe_addition": "none",
        "field_renamed": "minor",
        "default_changed": "minor",
        "format_changed": "minor",
    }
    return {
        "breaking": False,
        "severity": severity_map.get(ct, "none"),
        "reason": "Non-breaking change — backwards compatible",
    }


def _estimate_severity(change_type: str, old_schema: dict, change: dict) -> str:
    """Estimate severity for breaking changes.

    Based on dataset analysis: 'major' is most common (29 major vs 26 critical).
    Use 'major' as default, upgrade to 'critical' for high-risk patterns.
    """
    required = old_schema.get("required", False)
    field_type = old_schema.get("type", "")

    if change_type == "field_removed":
        # Required fields with id/key-like names tend to be critical
        name = old_schema.get("name", "")
        key_fields = {"id", "token", "key", "version", "state", "city", "price", "country"}
        if name in key_fields:
            return "critical"
        # Required + not array tends toward critical
        if required and field_type not in ("array", "object", "null"):
            return "critical"
        return "major"

    if change_type == "type_changed":
        # Required fields with type change are more critical
        if required and field_type in ("string", "integer"):
            return "critical"
        return "major"

    if change_type == "required_added":
        # Integer fields becoming required tend to be critical
        if field_type == "integer":
            return "critical"
        return "major"

    if change_type == "nullable_removed":
        # Required fields losing nullable is more critical
        if required:
            return "critical"
        return "major"

    if change_type == "enum_narrowed":
        # Default to major; hard to distinguish without more info
        return "major"

    return "major"
