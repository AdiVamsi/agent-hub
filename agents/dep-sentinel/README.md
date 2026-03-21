# dep-sentinel

**Karpathy's AutoResearch, but for dependency security. Point it at your requirements.txt, wake up to a patched project.**

## The Problem

Dependency vulnerabilities accumulate silently. Every project has outdated packages with known CVEs. Manual auditing is tedious, and figuring out which upgrades are safe takes time most teams don't have.

## The Solution

An AI agent that scans your dependencies against a vulnerability database, forms upgrade strategies, applies them, checks compatibility, and keeps only proven improvements. Let it run overnight — wake up to a patched project with a full audit trail in git.

*"I pointed an AI agent at my project's dependencies. It ran 40 experiments overnight. Found 27 vulnerabilities, patched 22 automatically, all imports still work."*

## How It Works

Same 3-primitive design as [Karpathy's autoresearch](https://github.com/karpathy/autoresearch):

| File | Role | Modified by agent? |
|------|------|--------------------|
| `program.md` | "Minimize vulnerability_score by upgrading dependencies" | No |
| `policy.py` | Dependency upgrade rules and constraints | **Yes** |
| `harness.py` | Security evaluator with compatibility checks | No |

**The metric:** `vulnerability_score` = weighted sum of CVEs (critical=10, high=5, medium=2, low=1). Lower is better.

**The loop:**
1. Agent reads `program.md`
2. Studies `vulndb.json` and current vulnerabilities
3. Edits `policy.py` with upgrade rules
4. Runs `python harness.py evaluate`
5. If score improved AND compatibility >= 0.90 → `git commit`
6. If not → `git reset --hard HEAD`
7. Repeat forever

**The safety net:** `harness.py` checks that all packages imported in `app.py` remain available. Removing a needed dependency costs 0.5 compatibility points. Major version bumps cost 0.1 unless explicitly allowed.

## Quick Start

```bash
cd agents/dep-sentinel
python prepare.py init
python harness.py baseline
python harness.py report
# Point Claude Code at this folder:
# "Read program.md and start optimizing"
```

## Files

```
dep-sentinel/
├── program.md          ← Instructions for the AI agent
├── policy.py           ← The ONE file the agent modifies
├── harness.py          ← Security evaluator (fixed)
├── prepare.py          ← Setup script (fixed)
├── vulndb.json         ← Vulnerability database (27 CVEs)
├── project/
│   ├── requirements.txt  ← Vulnerable dependencies (20 packages)
│   ├── app.py            ← Sample app (imports to check compatibility)
│   └── test_app.py       ← Import tests
├── pyproject.toml
└── results.tsv         ← (created at runtime) experiment log
```

## Vulnerabilities Included

The sample project ships with 20 packages, almost all pinned to vulnerable versions:

- **4 Critical**: pyyaml (RCE), requests (SSRF), cryptography (key extraction), pillow (RCE)
- **6 High**: flask (session bypass), jinja2 (XSS), sqlalchemy (SQLi), urllib3 (header injection), werkzeug (path traversal), celery (deserialization RCE)
- **11 Medium**: setuptools, certifi, numpy, pandas, markupsafe, click, redis, werkzeug (DoS), requests (cert bypass), boto3 (credential leak), cryptography (null deref)
- **6 Low**: jinja2 (info disclosure), gunicorn (log injection), python-dotenv (env override), flask (info disclosure), numpy (DoS), setuptools (DoS)

## Strategy Types

The agent can use several approaches, each with trade-offs:

- **Version pinning** — safest, just bump to fixed version (minor/patch only)
- **Major upgrades** — some fixes require major bumps (sqlalchemy 1→2, urllib3 1→2), need explicit opt-in
- **Package replacement** — swap a vulnerable package for a safer alternative
- **Removal** — remove packages not imported in app.py (no compat penalty)
- **Severity prioritization** — fix criticals first (10 pts each) for fastest score improvement

## Example Results

```
Baseline:      vulnerability_score=98 (4 critical, 6 high, 11 medium, 6 low)
After 12 experiments: vulnerability_score=4 (0 critical, 0 high, 2 medium, 0 low)
Patches applied: 15 version upgrades, 2 major bumps
Compatibility: 0.95 (all imports still work)
```

## Part of [agent-hub](../../README.md)

A collection of AI agents built on Karpathy's AutoResearch pattern.
