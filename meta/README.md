# meta-agent

**The agent that improves all other agents.**

While each agent in agent-hub optimizes a specific problem, the meta-agent optimizes the agents themselves. It cycles through all 5 agents, runs their AutoResearch loops, analyzes what's working, and improves their program.md instruction files.

## How It Works

```
meta-agent reads all 5 agents
  → Picks the agent with lowest recent improvement
  → Runs its AutoResearch loop (5+ experiments)
  → Analyzes results: which hypotheses worked?
  → Rewrites the agent's program.md to prioritize successful strategies
  → Moves to next agent
  → Repeats — agents get better every cycle
```

## Two Levels of Optimization

**Level 1**: The meta-agent runs each agent's normal experiment loop (editing router.py, target.py, etc.)

**Level 2**: The meta-agent improves each agent's `program.md` based on which strategies succeed vs fail. The instruction files themselves get optimized.

## Quick Start

```bash
cd meta/
python meta-harness.py status    # See current state of all agents
python orchestrator.py select    # See which agent to work on next
python tracker.py                # See experiment analysis for all agents

# Run the meta-agent:
# Point Claude Code at this directory and say:
# "Read meta-program.md and start the meta-loop"
```

## The Meta-Metric

`total_improvement_rate` — average improvement across all 5 agents per cycle.

## Files

| File | Role | Modified by |
|------|------|------------|
| `meta-program.md` | Meta-agent instructions | Human |
| `orchestrator.py` | Scheduling + strategy | Meta-agent (editable) |
| `meta-harness.py` | Evaluation | Nobody (fixed) |
| `runner.py` | Agent execution helper | Nobody (fixed) |
| `tracker.py` | Progress analysis | Nobody (fixed) |

## Part of [agent-hub](../README.md)
