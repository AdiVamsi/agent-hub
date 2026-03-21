# dep-sentinel — Research Program

You are an autonomous research agent optimizing dependency security for a Python project. Your goal is to minimize `vulnerability_score` by patching, upgrading, or replacing vulnerable packages.

## Setup (run once at start)

1. Create a git branch from current HEAD:
   ```
   git checkout -b autoresearch/<descriptive-tag>
   ```

2. Read these repo files to understand the system:
   - This file (`program.md`) — your instructions
   - `README.md` — overview of the agent
   - `harness.py` — the evaluation infrastructure (DO NOT MODIFY)
   - `policy.py` — the file you WILL modify
   - `vulndb.json` — the vulnerability database
   - `project/requirements.txt` — the project's current dependencies
   - `project/app.py` — the project's code (shows which packages are imported)

3. Initialize `results.tsv` with header:
   ```
   echo -e "experiment_id\tdescription\tvulnerability_score\tcritical_count\thigh_count\tmedium_count\tlow_count\tcompat_score\tstatus\ttimestamp" > results.tsv
   ```

4. Run baseline evaluation:
   ```
   python harness.py evaluate > eval.log 2>&1
   ```
   Read the RESULT line: `grep "^RESULT:" eval.log`
   Record the baseline in `results.tsv` with status "baseline".

5. Run the detailed vulnerability report to understand what needs fixing:
   ```
   python harness.py report
   ```

## Experiment Loop (repeat indefinitely)

For each experiment:

### 1. Form a Strategy

Study the current vulnerability report and `policy.py`. Pick ONE strategy:

- **Version pinning**: Pin a vulnerable package to its `fixed_version` from vulndb.json. This is the simplest and safest approach — start here.
- **Batch upgrades by severity**: Fix all critical CVEs first (they're worth 10 points each), then high (5 points), then medium (2 points), then low (1 point).
- **Package replacement**: If a package has many vulnerabilities or no easy fix, swap it for a safer alternative.
- **Minimum version floors**: Set version constraints that exclude all known-vulnerable ranges.
- **Allow major upgrades**: Some fixes require major version bumps (e.g., sqlalchemy 1.x → 2.x, urllib3 1.x → 2.x). Add these to `allow_major_upgrades` in `get_constraints()` to avoid the compatibility penalty.
- **Removal of unused dependencies**: If a package isn't imported in `app.py`, it can be safely removed without compatibility penalty.
- **Transitive dependency awareness**: Some packages (like werkzeug, markupsafe) are dependencies of other packages (flask, jinja2). Upgrading them is usually safe.
- **Multi-vulnerability packages**: Some packages have multiple CVEs — a single upgrade can fix several at once. Target these for maximum score improvement per experiment.

### 2. Edit policy.py

Add rules to `get_upgrade_rules()`. Each rule is a dict:
```python
{"package": "pyyaml", "action": "upgrade", "version": "6.0.1", "reason": "Fix CVE-2024-21105 critical yaml.load() RCE"}
```

If a major version bump is needed, also add the package to `allow_major_upgrades` in `get_constraints()`.

### 3. Run the Experiment

```
python harness.py evaluate > eval.log 2>&1
```

Redirect ALL output to the log. Do NOT let it flood your context window.

### 4. Check Results

```
grep "^RESULT:" eval.log
```

This gives you: `vulnerability_score`, `critical`, `high`, `medium`, `low`, `compat_score`, `packages_fixed`.

### 5. Commit or Revert

**If `vulnerability_score` improved (lower) AND `compat_score >= 0.90`:**
```
git add policy.py
git commit -m "experiment N: <description> — score X→Y, fixed Z CVEs"
```
Append to `results.tsv` with status `kept`.

**If `compat_score` dropped below 0.90 OR `vulnerability_score` got worse:**
```
git reset --hard HEAD
```
Append to `results.tsv` with status `reverted`.

### 6. Next Strategy

Move on to the next optimization. Build on previous successful changes. Prioritize by impact: critical CVEs are worth 10 points each, so fixing one critical is worth more than fixing five low-severity issues.

## Constraints

- **ONLY modify `policy.py`**. Never touch `harness.py`, `prepare.py`, `vulndb.json`, or any file in `project/`.
- **Compatibility floor**: `compat_score` must stay >= 0.90.
- **Keep rules clear**: Each rule should have a `reason` explaining what CVE it fixes.
- **Each experiment should complete in under 30 seconds**.
- **Be systematic**: Log everything in `results.tsv`. Track which CVEs you've fixed.
