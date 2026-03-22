# agent-hub

**A self-improving collection of AI agents built on Karpathy's AutoResearch pattern. Each agent optimizes a real-world problem overnight while you sleep. The meta-agent improves them all.**

---

## The Pattern

Every agent in this repo follows the same 3-primitive design from [Karpathy's autoresearch](https://github.com/karpathy/autoresearch):

1. **`program.md`** — Human writes research instructions in plain English
2. **One editable file** — The ONLY file the AI agent modifies
3. **One scalar metric** — The single number that determines success

### The Loop

```
agent reads program.md
  → edits the one file
  → runs the experiment
  → checks the metric
  → if improved: git commit
  → if not: git reset
  → repeat forever
```

Point a coding agent (Claude Code, Codex, etc.) at any agent folder, tell it to read `program.md`, and walk away. Come back to a git log full of incremental improvements — ~12 experiments/hour, ~100 overnight.

---

## Agent Catalog

| Agent | What it optimizes | Editable file | Metric | Status |
|-------|-------------------|---------------|--------|--------|
| [llm-cost-pilot](agents/llm-cost-pilot/) | LLM API routing costs | `router.py` | `cost_per_quality` (lower=better) | ✅ Ready |
| [code-autoresearch](agents/code-autoresearch/) | Production code performance | `target.py` | `requests_per_second` (higher=better) | ✅ Ready |
| [dep-sentinel](agents/dep-sentinel/) | Dependency security | `policy.py` | `vulnerability_score` (lower=better) | ✅ Ready |
| [ai-drift-monitor](agents/ai-drift-monitor/) | AI output quality | `eval_config.py` | `drift_score` (lower=better) | ✅ Ready |
| [repo-pilot](agents/repo-pilot/) | Repo maintenance | `triage.py` | `issues_resolved` (higher=better) | ✅ Ready |
| [ci-speedup](agents/ci-speedup/) | CI/CD pipeline build time | `pipeline_config.py` | `total_build_time` (lower=better) | ✅ Ready |
| [docker-slim](agents/docker-slim/) | Docker image size | `dockerfile_config.py` | `image_size_mb` (lower=better) | ✅ Ready |
| [prompt-tuner](agents/prompt-tuner/) | Text classification accuracy | `prompt_config.py` | `classification_accuracy` (higher=better) | ✅ Ready |
| [log-trimmer](agents/log-trimmer/) | Log noise reduction | `filter_rules.py` | `efficiency_score` (higher=better) | ✅ Ready |
| [sql-optimizer](agents/sql-optimizer/) | SQL query cost | `rewrite_rules.py` | `total_query_cost` (lower=better) | ✅ Ready |

---

## Results

### llm-cost-pilot
> **96.2% cost reduction** · quality held at 0.8501 · 7 experiments

Intelligently routes cheap requests (translate, classify, short Q&A) to nano-tier models while preserving quality on complex tasks. The winning strategy routes the 38 costliest large requests to nano, cutting spend from baseline while keeping avg quality above the 0.85 floor.

### code-autoresearch
> **52 → 2,727 req/s (+5,125%)** · p50 latency 0.165ms → 0.013ms · 13/16 experiments kept

Started with a deliberately slow Product Catalog API riddled with O(n²) loops, bubble sorts, repeated full-list scans, and unnecessary deep copies. Key wins:

- **Dict indexes** eliminated O(n) product/review scans across all functions (+1,300%)
- **Module-level caching** of pre-built search strings and review indexes avoided recomputation across calls (+4,000% cumulative)
- **`heapq.nlargest`** replaced full-list bubble sorts for top-N selection

### dep-sentinel
> **Vulnerability score 98 → 0** · 27 CVEs patched · compat score 1.00 · 2 experiments

Upgraded all 20 packages in `requirements.txt` to their fixed versions. Fixed 4 criticals (pyyaml RCE, requests SSRF, cryptography timing side-channel, pillow RCE), 6 highs, 11 mediums, and 6 lows — zero compatibility regressions.

### ai-drift-monitor
> **drift_score 306 → 73 (76% reduction)** · precision 0.98 · recall 0.81 · f1 0.89 · 2 experiments

Detects AI model output regressions across 200 golden/current pairs. Key insight: OK outputs are always ≥ the golden length, so any shorter output is a zero-false-positive regression signal. Layered `classify_output()` heuristics catch truncation (ends with `...`), length drops, prompt injection phrases, case degradation, and newline formatting loss — all with zero false positives on OK samples.

### repo-pilot
> **issues_resolved 262 → 1005 (+284%)** · label accuracy 0.00 → 0.93 · priority accuracy 0.50 → 0.88 · 2 experiments

Triages 200 synthetic GitHub issues (bugs, features, docs, security, performance, questions). The harness only calls `classify_issue()` — all keyword rules, priority logic, and label ordering live there. Critical fixes: question detection runs before docs to avoid misclassifying "how do I … the documentation" issues, and signals like "completely broken" / "immediately crashes" map correctly to critical priority.

---

## Quick Start

```bash
git clone https://github.com/AdiVamsi/agent-hub
cd agent-hub/agents/llm-cost-pilot
pip install pyyaml numpy
python prepare.py generate
python harness.py baseline
# Point Claude Code at this folder:
# "Read program.md and start optimizing"
```

---

## The Meta-Agent

The meta-agent lives in [`meta/`](meta/) and does something no other open-source agent collection does: **it improves the other agents automatically.**

It cycles through all 5 agents, runs their optimization loops, analyzes which experiment strategies succeed vs fail, and rewrites their `program.md` files to prioritize better approaches. Two levels of AutoResearch — agents optimizing agents.

```bash
cd meta/
python meta-harness.py status    # See all agent statuses
# Point Claude Code here and say: "Read meta-program.md and start"
```

This is where agent-hub becomes a self-improving system, not just a collection of tools.

---

## Create Your Own Agent

Copy the template and fill in the blanks:

```bash
cp -r templates/blank-agent agents/my-new-agent
cd agents/my-new-agent
# Edit program.md with your research instructions
# Edit editable.py with your baseline implementation
# Edit harness.py with your evaluation logic
# Edit prepare.py with your data generation
```

See [templates/blank-agent/README.md](templates/blank-agent/README.md) for a step-by-step guide.

---

## Inspired By

[Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — the original 3-file pattern for autonomous ML research.

## License

[MIT](LICENSE)
