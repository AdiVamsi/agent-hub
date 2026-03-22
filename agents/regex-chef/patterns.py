"""Regex Chef — editable file.

Your job: implement PATTERNS dict mapping pattern_type to a regex pattern string.
The harness tests each pattern against labeled test data.

Metric: accuracy (correct matches / total) — HIGHER is better.
Baseline: very simple patterns that catch obvious cases but miss edge cases.
"""
import re

PATTERNS = {
    "email": r".+@.+",
    "phone_us": r"\d{3}-\d{3}-\d{4}",
    "ipv4": r"\d+\.\d+\.\d+\.\d+",
    "date_iso": r"\d{4}-\d{2}-\d{2}",
    "url": r"https?://.+",
    "semver": r"\d+\.\d+\.\d+",
}


def match(pattern_type: str, input_string: str) -> bool:
    """Test if input_string matches the pattern for pattern_type."""
    pattern = PATTERNS.get(pattern_type)
    if not pattern:
        return False
    try:
        return bool(re.fullmatch(pattern, input_string.strip()))
    except re.error:
        return False
