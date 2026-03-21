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
    return [
        # CRITICAL severity fixes
        {"package": "pyyaml", "action": "upgrade", "version": "6.0.1", "reason": "Fix CVE-2024-21105 critical RCE via yaml.load"},
        {"package": "requests", "action": "upgrade", "version": "2.32.0", "reason": "Fix CVE-2024-32681 critical and CVE-2024-35195 medium"},
        {"package": "cryptography", "action": "upgrade", "version": "42.0.0", "reason": "Fix CVE-2024-26130 critical and CVE-2024-41110 medium"},
        {"package": "pillow", "action": "upgrade", "version": "10.0.0", "reason": "Fix CVE-2024-28219 critical RCE via TIFF"},
        # HIGH severity fixes
        {"package": "flask", "action": "upgrade", "version": "2.3.2", "reason": "Fix CVE-2024-34069 high and CVE-2024-34070 low"},
        {"package": "jinja2", "action": "upgrade", "version": "3.1.4", "reason": "Fix CVE-2024-22195 high and CVE-2024-22196 low"},
        {"package": "sqlalchemy", "action": "upgrade", "version": "2.0.0", "reason": "Fix CVE-2024-37891 high SQL injection"},
        {"package": "urllib3", "action": "upgrade", "version": "2.0.7", "reason": "Fix CVE-2024-37890 high header injection"},
        {"package": "werkzeug", "action": "upgrade", "version": "3.0.1", "reason": "Fix CVE-2024-34064 high and CVE-2024-34063 medium"},
        {"package": "celery", "action": "upgrade", "version": "5.3.0", "reason": "Fix CVE-2024-38525 high deserialization RCE"},
        # MEDIUM severity fixes
        {"package": "setuptools", "action": "upgrade", "version": "70.0.0", "reason": "Fix CVE-2024-43498 medium and CVE-2024-43488 low"},
        {"package": "certifi", "action": "upgrade", "version": "2024.2.2", "reason": "Fix CVE-2024-39689 medium outdated certs"},
        {"package": "numpy", "action": "upgrade", "version": "1.26.0", "reason": "Fix CVE-2024-24790 medium and CVE-2024-24791 low"},
        {"package": "pandas", "action": "upgrade", "version": "2.1.0", "reason": "Fix CVE-2024-39338 medium code injection"},
        {"package": "markupsafe", "action": "upgrade", "version": "2.1.4", "reason": "Fix CVE-2024-24789 medium"},
        {"package": "click", "action": "upgrade", "version": "8.1.7", "reason": "Fix CVE-2024-38428 medium"},
        {"package": "redis", "action": "upgrade", "version": "5.0.0", "reason": "Fix CVE-2024-22190 medium"},
        {"package": "boto3", "action": "upgrade", "version": "1.34.0", "reason": "Fix CVE-2024-41671 medium"},
        # LOW severity fixes
        {"package": "gunicorn", "action": "upgrade", "version": "21.0.0", "reason": "Fix CVE-2024-22191 low"},
        {"package": "python-dotenv", "action": "upgrade", "version": "1.0.0", "reason": "Fix CVE-2024-22193 low"},
    ]


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
        "allow_major_upgrades": [
            "sqlalchemy",
            "urllib3",
            "werkzeug",
            "pandas",
            "redis",
            "gunicorn",
            "python-dotenv",
            "pillow",
            "cryptography",
            "pyyaml",
            "setuptools",
            "certifi",
        ],
        "blocked_packages": [],
        "prefer_pinned": True,
    }
