# agent-hub

**A collection of AI agents built on Karpathy's AutoResearch pattern. Each agent optimizes a real-world problem overnight while you sleep.**

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
| code-autoresearch | Production code performance | `target.py` | `requests_per_second` (higher=better) | 🔜 Coming |
| dep-sentinel | Dependency security | `policy.py` | `vulnerability_score` (lower=better) | 🔜 Coming |
| ai-drift-monitor | AI output quality | `eval_config.py` | `drift_score` (lower=better) | 🔜 Coming |
| repo-pilot | Repo maintenance | `triage.py` | `issues_resolved` (higher=better) | 🔜 Coming |

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/agent-hub
cd agent-hub/agents/llm-cost-pilot
pip install pyyaml numpy
python prepare.py generate
python harness.py baseline
# Point Claude Code at this folder:
# "Read program.md and start optimizing"
```

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
