"""Dependency security policy — the ONE file the agent modifies.

The agent experiments with this file to minimize vulnerability_score.
The metric: weighted sum of vulnerabilities (critical=10, high=5, medium=2, low=1) — lower is better.

The policy defines upgrade rules, replacements, and constraints for
the project's dependencies. The harness applies these rules to
project/requirements.txt and evaluates the resulting security posture.

Available data (from vulndb.json):
  Each vulnerability has: package, affected_versions, fixed_version, severity, cve_id, description

Compatibility scoring (from harness.py):
  - Package exists in PyPI registry (simulated) = compatible
  - Version satisfies app.py import requirements = compatible
  - Major version change without explicit approval = -0.1 per package
  - Package removal when imported in app.py = -0.5 per package
  - Score starts at 1.0, deductions applied
"""


def get_upgrade_rules() -> list[dict]:
    """Return a list of dependency upgrade rules.

    Each rule is a dict with:
        package: str — package name
        action: "pin" | "upgrade" | "replace" | "remove"
        version: str — target version (for pin/upgrade)
        replacement: str — replacement package (for replace action)
        replacement_version: str — version of replacement
        reason: str — why this change

    Returns:
        List of upgrade rule dicts. Empty list = no changes (baseline).
    """
    # BASELINE: no changes — all vulnerabilities remain
    return []


def get_constraints() -> dict:
    """Return global constraints for dependency management.

    Returns:
        Dict with:
            min_python: str — minimum Python version to support
            allow_major_upgrades: list[str] — packages allowed to do major version bumps
            blocked_packages: list[str] — packages that must not be installed
            prefer_pinned: bool — whether to prefer exact version pins
    """
    return {
        "min_python": "3.10",
        "allow_major_upgrades": [],
        "blocked_packages": [],
        "prefer_pinned": True,
    }
