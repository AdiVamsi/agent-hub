"""Meta-agent orchestrator — the ONE file the meta-agent modifies.

Controls which agent to run next and how to prioritize work.
The meta-agent improves this over time to maximize total_improvement_rate.
"""

import csv
import sys
from pathlib import Path
from datetime import datetime


AGENTS_DIR = Path(__file__).parent.parent / "agents"

AGENTS = [
    {
        "name": "llm-cost-pilot",
        "editable": "router.py",
        "metric": "cost_per_quality",
        "direction": "lower",  # lower is better
    },
    {
        "name": "code-autoresearch",
        "editable": "target.py",
        "metric": "requests_per_second",
        "direction": "higher",  # higher is better
    },
    {
        "name": "dep-sentinel",
        "editable": "policy.py",
        "metric": "vulnerability_score",
        "direction": "lower",
    },
    {
        "name": "ai-drift-monitor",
        "editable": "eval_config.py",
        "metric": "drift_score",
        "direction": "lower",
    },
    {
        "name": "repo-pilot",
        "editable": "triage.py",
        "metric": "issues_resolved",
        "direction": "higher",
    },
    {
        "name": "ci-speedup",
        "editable": "pipeline_config.py",
        "metric": "total_build_time",
        "direction": "lower",
    },
    {
        "name": "docker-slim",
        "editable": "dockerfile_config.py",
        "metric": "image_size_mb",
        "direction": "lower",
    },
    {
        "name": "prompt-tuner",
        "editable": "prompt_config.py",
        "metric": "classification_accuracy",
        "direction": "higher",
    },
    {
        "name": "log-trimmer",
        "editable": "filter_rules.py",
        "metric": "efficiency_score",
        "direction": "higher",
    },
    {
        "name": "sql-optimizer",
        "editable": "rewrite_rules.py",
        "metric": "total_query_cost",
        "direction": "lower",
    },
    {
        "name": "api-racer",
        "editable": "endpoint_config.py",
        "metric": "avg_response_ms",
        "direction": "lower",
    },
    {
        "name": "test-shrink",
        "editable": "test_config.py",
        "metric": "total_runtime_ms",
        "direction": "lower",
    },
    {
        "name": "iac-lint",
        "editable": "lint_rules.py",
        "metric": "compliance_score",
        "direction": "higher",
    },
    {
        "name": "cache-tuner",
        "editable": "eviction_policy.py",
        "metric": "hit_rate",
        "direction": "higher",
    },
    {
        "name": "bundle-phobia",
        "editable": "bundle_config.py",
        "metric": "bundle_size_kb",
        "direction": "lower",
    },
    {
        "name": "data-dedup",
        "editable": "match_rules.py",
        "metric": "f1_score",
        "direction": "higher",
    },
    {
        "name": "env-shrinker",
        "editable": "sizing_rules.py",
        "metric": "total_monthly_cost",
        "direction": "lower",
    },
    {
        "name": "regex-chef",
        "editable": "patterns.py",
        "metric": "accuracy",
        "direction": "higher",
    },
    {
        "name": "schema-guard",
        "editable": "check_rules.py",
        "metric": "detection_score",
        "direction": "higher",
    },
    {
        "name": "cron-wizard",
        "editable": "schedule_config.py",
        "metric": "schedule_score",
        "direction": "higher",
    },
]


def _load_results(agent_name: str) -> list[dict]:
    """Load an agent's results.tsv."""
    results_path = AGENTS_DIR / agent_name / "results.tsv"
    if not results_path.exists():
        return []
    rows = []
    with open(results_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def select_next_agent() -> dict:
    """Select which agent to optimize next.

    Priority:
    1. Agents with no results.tsv (never optimized)
    2. Agents with lowest recent improvement rate
    3. Round-robin as tiebreaker

    Returns:
        Agent dict with name, editable, metric, direction, and selection reason.
    """
    unoptimized = []
    optimized = []

    for agent in AGENTS:
        results = _load_results(agent["name"])
        if not results:
            unoptimized.append(agent)
        else:
            kept = sum(1 for r in results if r.get("status", "").lower() == "kept")
            agent_copy = dict(agent)
            agent_copy["experiment_count"] = len(results)
            agent_copy["kept_count"] = kept
            agent_copy["success_rate"] = kept / len(results) if results else 0

            # Check if stuck (last 5 all reverted)
            recent = results[-5:] if len(results) >= 5 else results
            recent_kept = sum(1 for r in recent
                              if r.get("status", "").lower() == "kept")
            agent_copy["recently_stuck"] = recent_kept == 0 and len(recent) >= 5
            optimized.append(agent_copy)

    # Priority 1: never optimized agents first
    if unoptimized:
        selected = dict(unoptimized[0])
        selected["reason"] = "never optimized — no results.tsv found"
        return selected

    # Priority 2: agents that aren't stuck, sorted by fewest experiments
    not_stuck = [a for a in optimized if not a.get("recently_stuck")]
    stuck = [a for a in optimized if a.get("recently_stuck")]

    if not_stuck:
        not_stuck.sort(key=lambda a: a.get("experiment_count", 0))
        selected = not_stuck[0]
        selected["reason"] = (
            f"fewest experiments ({selected['experiment_count']}), "
            f"success rate {selected['success_rate']*100:.0f}%"
        )
        return selected

    # All agents are stuck — pick the one with highest success rate historically
    if stuck:
        stuck.sort(key=lambda a: a.get("success_rate", 0), reverse=True)
        selected = stuck[0]
        selected["reason"] = (
            f"all agents stuck — picking highest historical success rate "
            f"({selected['success_rate']*100:.0f}%)"
        )
        return selected

    # Fallback: first agent
    selected = dict(AGENTS[0])
    selected["reason"] = "fallback — round-robin"
    return selected


def get_agent_status(agent_name: str) -> dict:
    """Get current optimization status for an agent."""
    results = _load_results(agent_name)
    if not results:
        return {"status": "not_started", "experiments": 0, "kept": 0, "reverted": 0}

    kept = sum(1 for r in results if r.get("status", "").lower() == "kept")
    reverted = sum(1 for r in results if "revert" in r.get("status", "").lower())

    return {
        "status": "optimized" if kept > 0 else "attempted",
        "experiments": len(results),
        "kept": kept,
        "reverted": reverted,
        "success_rate": kept / len(results) if results else 0,
    }


def get_all_status() -> list[dict]:
    """Get status for all agents."""
    statuses = []
    for agent in AGENTS:
        status = get_agent_status(agent["name"])
        status["name"] = agent["name"]
        status["metric"] = agent["metric"]
        status["direction"] = agent["direction"]
        statuses.append(status)
    return statuses


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "select":
        agent = select_next_agent()
        print(f"\nSELECTED: {agent['name']}")
        print(f"  Reason:   {agent['reason']}")
        print(f"  Editable: {agent.get('editable', '?')}")
        print(f"  Metric:   {agent.get('metric', '?')} ({agent.get('direction', '?')} is better)")
        print(f"  Path:     agents/{agent['name']}/")

    elif cmd == "status":
        statuses = get_all_status()
        print(f"\n{'Agent':<22} {'Status':<14} {'Experiments':<13} "
              f"{'Kept':<6} {'Reverted':<10} {'Success%':<10}")
        print("-" * 75)
        for s in statuses:
            rate = (f"{s['success_rate']*100:.0f}%"
                    if s["experiments"] > 0 else "—")
            print(f"{s['name']:<22} {s['status']:<14} {s['experiments']:<13} "
                  f"{s['kept']:<6} {s['reverted']:<10} {rate:<10}")

    else:
        print("Usage: python orchestrator.py [select|status]")
