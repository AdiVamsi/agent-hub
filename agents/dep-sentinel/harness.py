#!/usr/bin/env python3
"""Security evaluation harness for dep-sentinel. DO NOT MODIFY.

Loads the vulnerability database, applies policy rules to the project's
dependencies, evaluates the resulting security posture, and prints a
greppable RESULT line.

Usage:
    python harness.py evaluate  — run full evaluation, print RESULT
    python harness.py baseline  — show vulnerability score with no policy
    python harness.py report    — detailed vulnerability report per package
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VULNDB_PATH = ROOT / "vulndb.json"
REQUIREMENTS_PATH = ROOT / "project" / "requirements.txt"
APP_PATH = ROOT / "project" / "app.py"

SEVERITY_WEIGHTS = {"critical": 10, "high": 5, "medium": 2, "low": 1}


# ---------------------------------------------------------------------------
# Version parsing and comparison
# ---------------------------------------------------------------------------


def parse_version(version_str: str) -> tuple:
    """Parse a version string like '1.26.3' into a comparable tuple."""
    parts = re.split(r"[.\-]", version_str.strip())
    result = []
    for p in parts:
        try:
            result.append(int(p))
        except ValueError:
            result.append(0)
    # Pad to at least 3 components
    while len(result) < 3:
        result.append(0)
    return tuple(result)


def version_matches_constraint(version: str, constraint: str) -> bool:
    """Check if a version matches a constraint like '<6.0' or '>=2.31.0'."""
    constraint = constraint.strip()
    v = parse_version(version)

    if constraint.startswith("<="):
        return v <= parse_version(constraint[2:])
    elif constraint.startswith(">="):
        return v >= parse_version(constraint[2:])
    elif constraint.startswith("<"):
        return v < parse_version(constraint[1:])
    elif constraint.startswith(">"):
        return v > parse_version(constraint[1:])
    elif constraint.startswith("=="):
        return v == parse_version(constraint[2:])
    elif constraint.startswith("!="):
        return v != parse_version(constraint[2:])
    return False


def major_version(version: str) -> int:
    """Get the major version number."""
    return parse_version(version)[0]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_vulndb() -> list[dict]:
    with open(VULNDB_PATH) as f:
        data = json.load(f)
    return data["vulnerabilities"]


def load_requirements() -> dict[str, str]:
    """Load requirements.txt into {package: version} dict."""
    reqs = {}
    with open(REQUIREMENTS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "==" in line:
                pkg, ver = line.split("==", 1)
                reqs[pkg.strip().lower()] = ver.strip()
    return reqs


def get_imported_packages() -> set[str]:
    """Parse app.py to find all imported package names."""
    imports = set()
    with open(APP_PATH) as f:
        for line in f:
            line = line.strip()
            # Match: import X, from X import ..., from X.Y import ...
            m = re.match(r"^(?:from|import)\s+([\w]+)", line)
            if m:
                pkg = m.group(1)
                # Map module names to package names
                module_to_pkg = {
                    "yaml": "pyyaml",
                    "PIL": "pillow",
                    "dotenv": "python-dotenv",
                    "cv2": "opencv-python",
                }
                imports.add(module_to_pkg.get(pkg, pkg).lower())
    return imports


# ---------------------------------------------------------------------------
# Policy application
# ---------------------------------------------------------------------------


def apply_policy(reqs: dict[str, str]) -> dict[str, str]:
    """Apply policy rules to requirements, return effective requirements."""
    from policy import get_upgrade_rules, get_constraints

    effective = dict(reqs)
    rules = get_upgrade_rules()

    for rule in rules:
        pkg = rule.get("package", "").lower()
        action = rule.get("action", "")

        if action in ("pin", "upgrade"):
            version = rule.get("version", "")
            if pkg in effective and version:
                effective[pkg] = version
            elif version:
                effective[pkg] = version

        elif action == "replace":
            replacement = rule.get("replacement", "").lower()
            rep_version = rule.get("replacement_version", "")
            if pkg in effective:
                del effective[pkg]
                if replacement and rep_version:
                    effective[replacement] = rep_version

        elif action == "remove":
            if pkg in effective:
                del effective[pkg]

    return effective


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def check_vulnerabilities(reqs: dict[str, str],
                          vulndb: list[dict]) -> list[dict]:
    """Check which vulnerabilities apply to the given requirements."""
    found = []
    for vuln in vulndb:
        pkg = vuln["package"].lower()
        if pkg not in reqs:
            continue
        version = reqs[pkg]
        if version_matches_constraint(version, vuln["affected_versions"]):
            found.append({**vuln, "installed_version": version})
    return found


def calc_vulnerability_score(vulns: list[dict]) -> tuple[int, dict]:
    """Calculate weighted vulnerability score and severity counts."""
    score = 0
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in vulns:
        sev = v["severity"]
        score += SEVERITY_WEIGHTS.get(sev, 1)
        counts[sev] = counts.get(sev, 0) + 1
    return score, counts


def calc_compat_score(original_reqs: dict[str, str],
                      effective_reqs: dict[str, str],
                      imported: set[str]) -> float:
    """Calculate compatibility score based on policy changes."""
    from policy import get_constraints
    constraints = get_constraints()
    allow_major = {p.lower() for p in constraints.get("allow_major_upgrades", [])}
    blocked = {p.lower() for p in constraints.get("blocked_packages", [])}

    score = 1.0

    # Penalty for removing imported packages
    for pkg in original_reqs:
        if pkg not in effective_reqs and pkg in imported:
            score -= 0.5

    # Penalty for major version bumps not explicitly allowed
    for pkg in effective_reqs:
        if pkg in original_reqs:
            old_major = major_version(original_reqs[pkg])
            new_major = major_version(effective_reqs[pkg])
            if new_major != old_major and pkg not in allow_major:
                score -= 0.1

    # Penalty for blocked packages still present
    for pkg in blocked:
        if pkg in effective_reqs:
            score -= 0.2

    return max(0.0, round(score, 2))


def evaluate(use_policy: bool = True):
    """Run full evaluation."""
    vulndb = load_vulndb()
    original_reqs = load_requirements()
    imported = get_imported_packages()

    if use_policy:
        effective_reqs = apply_policy(original_reqs)
    else:
        effective_reqs = dict(original_reqs)

    vulns = check_vulnerabilities(effective_reqs, vulndb)
    vuln_score, counts = calc_vulnerability_score(vulns)

    if use_policy:
        compat = calc_compat_score(original_reqs, effective_reqs, imported)
    else:
        compat = 1.0

    # Count packages fixed (in original but not in effective vulns)
    baseline_vulns = check_vulnerabilities(original_reqs, vulndb)
    baseline_pkgs = {v["cve_id"] for v in baseline_vulns}
    current_pkgs = {v["cve_id"] for v in vulns}
    fixed = len(baseline_pkgs - current_pkgs)

    label = "EVALUATE" if use_policy else "BASELINE"
    print(f"\n{'='*60}")
    print(f"  {label} RESULTS")
    print(f"{'='*60}")
    print(f"  Vulnerability score:  {vuln_score}")
    print(f"    Critical: {counts['critical']}  (×10 = {counts['critical']*10})")
    print(f"    High:     {counts['high']}  (×5  = {counts['high']*5})")
    print(f"    Medium:   {counts['medium']}  (×2  = {counts['medium']*2})")
    print(f"    Low:      {counts['low']}  (×1  = {counts['low']})")
    print(f"  Compatibility score:  {compat}")
    print(f"  Packages in project:  {len(effective_reqs)}")
    print(f"  Vulnerabilities fixed: {fixed}")
    print(f"{'='*60}\n")

    print(f"RESULT: vulnerability_score={vuln_score} "
          f"critical={counts['critical']} high={counts['high']} "
          f"medium={counts['medium']} low={counts['low']} "
          f"compat_score={compat:.2f} packages_fixed={fixed}")


def report():
    """Print detailed vulnerability report per package."""
    vulndb = load_vulndb()
    original_reqs = load_requirements()

    from policy import get_upgrade_rules
    effective_reqs = apply_policy(original_reqs)

    print(f"\n{'='*70}")
    print(f"  VULNERABILITY REPORT")
    print(f"{'='*70}")

    # Group vulns by package
    baseline_vulns = check_vulnerabilities(original_reqs, vulndb)
    current_vulns = check_vulnerabilities(effective_reqs, vulndb)
    current_cves = {v["cve_id"] for v in current_vulns}

    by_package = {}
    for v in baseline_vulns:
        pkg = v["package"]
        if pkg not in by_package:
            by_package[pkg] = []
        by_package[pkg].append(v)

    for pkg in sorted(by_package.keys()):
        vulns = by_package[pkg]
        orig_ver = original_reqs.get(pkg.lower(), "?")
        eff_ver = effective_reqs.get(pkg.lower(), "REMOVED")
        status = "PATCHED" if eff_ver != orig_ver else "UNCHANGED"

        print(f"\n  {pkg} ({orig_ver} → {eff_ver}) [{status}]")
        for v in vulns:
            fixed_marker = "✓" if v["cve_id"] not in current_cves else "✗"
            print(f"    {fixed_marker} {v['cve_id']} [{v['severity'].upper()}] "
                  f"— fixed in {v['fixed_version']}")
            print(f"      {v['description'][:80]}")

    print(f"\n{'='*70}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python harness.py [evaluate|baseline|report]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "evaluate":
        evaluate(use_policy=True)
    elif cmd == "baseline":
        evaluate(use_policy=False)
    elif cmd == "report":
        report()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python harness.py [evaluate|baseline|report]")
        sys.exit(1)
