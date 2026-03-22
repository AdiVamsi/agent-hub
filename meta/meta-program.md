# Meta-Agent Program

You are the meta-agent for agent-hub. Your job is to run and improve all 5 agents.

## Setup

1. Read this file and `orchestrator.py` for strategy
2. Read `runner.py` to understand how individual agents are executed
3. Read `tracker.py` to understand how progress is tracked
4. Survey all 5 agents — read each agent's:
   - `program.md` (their instructions)
   - `results.tsv` (their experiment history, if it exists)
   - Their editable file (router.py, target.py, policy.py, eval_config.py, triage.py)
5. Run `python meta-harness.py status` to see current state of all agents
6. Initialize `meta-results.tsv` if it doesn't exist:
   ```
   echo -e "cycle_id\tagent\texperiments_run\texperiments_kept\timprovement_pct\tagent_metric_before\tagent_metric_after\ttimestamp" > meta-results.tsv
   ```

## The Meta-Loop

Repeat indefinitely:

### Phase 1: Select Agent

Run `python orchestrator.py select` to pick which agent to work on next.
The orchestrator prioritizes agents by:
- Agents that have never been optimized (no results.tsv) go first
- Agents with the lowest recent improvement rate go next
- Agents that are "stuck" (last 5 experiments all reverted) get deprioritized

### Phase 2: Run Agent's Optimization Loop

Navigate to the selected agent's directory:
```
cd ../agents/<selected-agent>/
```

Read its `program.md`. Follow those instructions to run experiments.
Run at least 5 experiments before moving to the next agent.
Follow the agent's commit/revert protocol exactly.

After running experiments, come back to the meta/ directory:
```
cd ../../meta/
```

### Phase 3: Analyze & Improve

Run `python tracker.py analyze <agent-name>` to see:
- Success rate (kept / total experiments)
- Which hypothesis categories succeeded vs failed
- Current metric vs baseline
- Improvement trajectory (is it plateauing?)

If the agent's success rate is below 30%, consider rewriting its program.md:
- Read the results.tsv to see which strategies worked
- Identify patterns in successful experiments
- Rewrite the "Suggested areas to explore" section of program.md
  to prioritize what's actually working
- Commit with: `git commit -m "meta: improve <agent> program.md — <reason>"`

### Phase 4: Record & Report

Run `python meta-harness.py evaluate` to update the meta-metrics.
Record in `meta-results.tsv`:
```
cycle_id	agent	experiments_run	experiments_kept	improvement_pct	agent_metric_before	agent_metric_after	timestamp
```

### Phase 5: Move to Next Agent

Go back to Phase 1 and select the next agent.

## Constraints

- Run at least 5 experiments per agent per cycle
- Do NOT modify harness.py, prepare.py, or data files in any agent
- You CAN modify program.md files in agents (that's the meta-optimization)
- You CAN modify the editable file in each agent (that's the normal optimization)
- You CAN modify orchestrator.py (that's the meta-agent's editable file)
- Record everything — all experiments, all changes to program.md files
- When modifying a program.md, commit with message: "meta: improve <agent> program.md — <reason>"

## Strategy Notes

- The first full cycle should focus on agents that haven't been optimized yet
- For agents that are already near-optimal, focus on program.md improvements rather than trying to squeeze more performance
- Watch for cross-agent learnings: if caching works in code-autoresearch, suggest it in other agents' program.md
- Track which experiment categories have the highest success rate across all agents
- If an agent is stuck (5+ consecutive reverts), try a radically different approach in its program.md
