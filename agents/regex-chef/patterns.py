"""Regex Chef — editable file.

Your job: implement PATTERNS dict mapping pattern_type to a regex pattern string.
The harness tests each pattern against labeled test data.

Metric: accuracy (correct matches / total) — HIGHER is better.
Baseline: very simple patterns that catch obvious cases but miss edge cases.
"""
import re

# Patterns used for ipv4 and semver (exact regex)
_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)"
_NUM = r"(?:0|[1-9]\d*)"

PATTERNS = {
    # ipv4: exactly 4 octets 0-255, no leading zeros, dot-separated
    "ipv4": _OCTET + r"(?:\." + _OCTET + r"){3}",
    # semver: MAJOR.MINOR.PATCH[.extra...] with no leading zeros, optional prerelease and build
    "semver": (
        _NUM + r"(?:\." + _NUM + r"){2,}"           # 3+ version parts, no leading zeros
        r"(?:-[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?"   # optional prerelease
        r"(?:\+[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?"  # optional build metadata
    ),
    # phone: used only as fallback
    "phone_us": (
        r"(?:\+?1[-.\s]?)?"                                         # optional country code +1
        r"(?:\(\d{3}\)[-.\s]?\d{3}[-.\s]\d{4}"                    # (NXX) NXX NNNN
        r"|\d{3}[-.\s]\d{3}[-.\s]\d{4}"                           # NXX-NXX-NNNN
        r"|\d{10})"                                                  # bare 10 digits
        r"(?:\s+(?:ext|x)\.?\s*\d+)?"                             # optional extension
    ),
    # fallback for other types
    "email": r".+@.+",
    "date_iso": r"\d{4}-\d{2}-\d{2}",
    "url": r"https?://.+",
}


def match(pattern_type: str, input_string: str) -> bool:
    """Test if input_string matches the pattern for pattern_type."""
    s = input_string.strip()

    if pattern_type == "date_iso":
        import datetime
        try:
            datetime.date.fromisoformat(s)
            return True
        except (ValueError, TypeError):
            return False

    if pattern_type == "email":
        return _match_email(s)

    if pattern_type == "url":
        return _match_url(s)

    pattern = PATTERNS.get(pattern_type)
    if not pattern:
        return False
    try:
        return bool(re.fullmatch(pattern, s))
    except re.error:
        return False


def _match_email(s: str) -> bool:
    """Validate email address."""
    if s.count("@") != 1:
        return False
    local, domain = s.split("@")
    # Local part validation
    if not local or local.startswith(".") or local.endswith("."):
        return False
    if " " in local:
        return False
    # Domain validation
    if not domain or domain.startswith(".") or domain.endswith(".") or ".." in domain:
        return False
    if " " in domain or "," in domain:
        return False
    # IP-based domain (e.g. user@192.168.1.1)
    parts = domain.split(".")
    if len(parts) == 4:
        try:
            if all(0 <= int(p) <= 255 and str(int(p)) == p for p in parts):
                return True
        except ValueError:
            pass
    # Standard domain: TLD must be >= 2 chars
    if len(parts) < 2 or len(parts[-1]) < 2:
        return False
    return True


def _match_url(s: str) -> bool:
    """Validate URL."""
    # Must start with http/https/ftp://
    m = re.match(r"^(https?|ftp)://", s)
    if not m:
        return False
    rest = s[m.end():]
    # No spaces allowed anywhere after protocol
    if " " in rest:
        return False
    # Split at first path/query/fragment separator
    domain_end = len(rest)
    for sep in "/", "?", "#":
        idx = rest.find(sep)
        if idx != -1 and idx < domain_end:
            domain_end = idx
    domain = rest[:domain_end]
    path = rest[domain_end:]
    # Strip auth (user:pass@)
    if "@" in domain:
        domain = domain.split("@")[-1]
    # Domain must be non-empty, no spaces, no leading dot
    if not domain or " " in domain or domain.startswith("."):
        return False
    # No double dots in hostname (exclude port)
    host = domain.split(":")[0]
    if ".." in host:
        return False
    # Must have a dot in hostname OR a port (to handle localhost:3000)
    if "." not in host and ":" not in domain:
        return False
    # Path must not have double slash
    if "//" in path:
        return False
    return True
