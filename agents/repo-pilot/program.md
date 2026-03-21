# repo-pilot: AutoResearch for Issue Triage

You are an AI agent optimizing an open-source issue triage system.

## Goal

Maximize `issues_resolved` — the number of issues correctly triaged (labeled, prioritized, deduplicated) — by tuning `triage.py`.

**The metric:** `issues_resolved = correct_labels*2 + correct_priorities*2 + correct_duplicates*3 - wrong_labels*1 - wrong_priorities*1 - wrong_duplicates*3`

Higher is better. The baseline is very negative (everything gets "needs-triage", medium priority, no duplicate detection).

## Setup

1. **Generate issue backlog:**
   ```bash
   python prepare.py generate
   ```
   This creates `issue_backlog.json` — 200 synthetic issues for a web framework project.

2. **Check baseline:**
   ```bash
   python harness.py baseline
   ```
   Record the baseline `issues_resolved` score. It should be very negative.

3. **Run full evaluation:**
   ```bash
   python harness.py evaluate
   ```
   This evaluates `triage.py` against ground truth and prints detailed results.

## THE ONE FILE

**`triage.py`** is the only file you modify.

It defines:
- `get_label_rules()` — rules for auto-labeling issues (keywords, exclude patterns)
- `get_priority_rules()` — rules for prioritizing (defaults, keyword overrides, label-based priorities)
- `get_duplicate_rules()` — rules for duplicate detection (similarity threshold, weights)
- `classify_issue(title, body)` — custom classification logic

Start with the baseline (empty/conservative), then add rules to improve the score.

## Experiment Loop

1. **Understand the data:** Look at a few issues in `issue_backlog.json`. What patterns distinguish bugs from features? What keywords appear in high-priority issues?

2. **Hypothesis:** Pick one aspect to improve. Examples:
   - Add keyword rules for "bug" label (e.g., "crash", "error", "broken", "fail")
   - Add priority rules for security labels (security → critical)
   - Lower duplicate similarity threshold from 0.95 to something more realistic
   - Implement body analysis for duplicate detection

3. **Modify `triage.py`:** Edit ONE function (e.g., `get_label_rules()`) based on your hypothesis.

4. **Evaluate:**
   ```bash
   python harness.py evaluate
   ```
   Compare new `issues_resolved` to previous run. Did it improve?

5. **Iterate:** If improved, keep it and try the next hypothesis. If not, revert and try a different approach.

## Suggested Optimization Areas

### Priority 1: Label Rules
Add keyword-based rules in `get_label_rules()`:
- **bug**: keywords like "crash", "error", "broken", "fail", "exception", "bug", "not working"
- **feature**: keywords like "add", "support", "implement", "request", "enable"
- **docs**: keywords like "documentation", "docs", "typo", "example", "readme"
- **performance**: keywords like "slow", "performance", "memory", "lag", "optimize"
- **security**: keywords like "security", "vulnerability", "xss", "injection", "auth", "token"
- **question**: keywords like "how", "help", "clarify", "usage", "best practice"
- **breaking-change**: keywords like "breaking", "upgrade", "api change", "migration"

Each rule should:
- Target relevant keywords in title+body
- Use exclude keywords to avoid false positives (e.g., "performance" rule shouldn't match "performance improvement request" if it's a feature)
- Set reasonable priority_boost if applicable

### Priority 2: Priority Rules
In `get_priority_rules()`:
- Map labels to priorities: security→critical, bugs→high/critical, features→medium/high, docs→low
- Add keyword overrides: "critical", "urgent", "blocker" → critical; "wontfix", "low-priority" → low
- Consider author_type: first-time contributors often file questions as bugs

### Priority 3: Duplicate Detection
In `get_duplicate_rules()`:
- Lower `similarity_threshold` from 0.95 to ~0.7-0.8 (catches more true duplicates)
- Increase `body_weight` to analyze issue descriptions, not just titles
- Add `keyword_groups` for synonyms:
  - ["crash", "error", "fail", "exception", "broken"]
  - ["slow", "performance", "lag", "optimize"]
  - ["cors", "cross-origin", "cors configuration"]
  - ["authentication", "auth", "login", "session"]

### Priority 4: Custom classify_issue() Logic
Implement content-aware classification:
- Analyze title/body word frequency and patterns
- Use heuristics: issues with "crash" + stack trace → bug
- Match regex patterns for common issue types
- Weight body content for duplicates

## Metrics Explained

The harness prints:
- **issues_resolved**: Overall score. Target: positive value (200+)
- **label_accuracy**: % of predicted labels that match ground truth. Target: 80%+
- **priority_accuracy**: % of predicted priorities that match ground truth. Target: 75%+
- **duplicate_f1**: % of correct duplicate detections. Target: 70%+

## Example Run Sequence

```
Baseline: issues_resolved=-200 (label_acc=0.00, priority_acc=0.50, dup_f1=0.87)

Experiment 1: Add bug label rules
→ issues_resolved=50 (label_acc=0.35, priority_acc=0.50, dup_f1=0.87)  ✓ improved!

Experiment 2: Add feature label rules
→ issues_resolved=100 (label_acc=0.50, priority_acc=0.50, dup_f1=0.87)  ✓ improved!

Experiment 3: Lower duplicate similarity threshold to 0.75
→ issues_resolved=95 (label_acc=0.50, priority_acc=0.50, dup_f1=0.65)  ✗ worse! (too many false positives)
Revert.

Experiment 4: Add priority rules (security→critical, bug→high)
→ issues_resolved=180 (label_acc=0.50, priority_acc=0.70, dup_f1=0.87)  ✓ improved!

...continue until stuck at local optimum (~350 is reasonable for this dataset)
```

## Tips

- **Start simple.** One small change per experiment. Track what improves the score.
- **Read examples.** Look at issues where predictions are wrong. What patterns did you miss?
- **Prioritize by impact.** Label rules affect the most predictions (every issue gets labeled). Start there.
- **Be conservative on duplicates.** False positives (incorrectly flagging duplicates) are costly (-3 each).
- **Test in isolation.** If multiple changes improve score, make them separately to understand which helped.
- **Don't overfit.** Look for general patterns, not one-off rules for specific issues.

## Files

- `triage.py` — the ONE file you edit
- `harness.py` — fixed evaluation engine (don't modify)
- `prepare.py` — generates issue_backlog.json (don't modify)
- `issue_backlog.json` — generated synthetic issues (read-only)
- `program.md` — this file (reference)
- `README.md` — project overview
- `pyproject.toml` — dependencies and metadata

## Success Criteria

- Baseline: `issues_resolved` << 0 (negative)
- After tuning: `issues_resolved` > 0 (ideally 200+)
- Label accuracy > 0.75
- Priority accuracy > 0.65
- Duplicate F1 > 0.60
