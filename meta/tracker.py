"""Progress tracker — analyzes experiment history across all agents.

Reads results.tsv from each agent, identifies patterns in successful
vs failed experiments, and provides data for the meta-agent to use
when improving program.md files.

NOT modified by the meta-agent.
"""

import csv
import sys
from pathlib import Path
from collections import Counter


AGENTS_DIR = Path(__file__).parent.parent / "agents"


def load_results(agent_name: str) -> list[dict]:
    """Load an agent's results.tsv as a list of dicts."""
    results_path = AGENTS_DIR / agent_name / "results.tsv"
    if not results_path.exists():
        return []

    results = []
    with open(results_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            results.append(row)
    return results


def analyze_agent(agent_name: str) -> dict:
    """Analyze an agent's experiment history."""
    results = load_results(agent_name)

    if not results:
        return {
            "agent": agent_name,
            "total_experiments": 0,
            "status": "not_started",
        }

    total = len(results)
    kept = [r for r in results if r.get("status", "").lower() == "kept"]
    reverted = [r for r in results if "revert" in r.get("status", "").lower()]
    baseline = [r for r in results if r.get("status", "").lower() == "baseline"]

    # Analyze descriptions for strategy patterns
    kept_words = Counter()
    reverted_words = Counter()
    for r in kept:
        desc = r.get("description", "").lower()
        for word in desc.split():
            if len(word) > 3:
                kept_words[word] += 1
    for r in reverted:
        desc = r.get("description", "").lower()
        for word in desc.split():
            if len(word) > 3:
                reverted_words[word] += 1

    # Check recent trajectory
    recent = results[-5:] if len(results) >= 5 else results
    recent_kept = sum(1 for r in recent
                      if r.get("status", "").lower() == "kept")
    is_stuck = recent_kept == 0 and len(recent) >= 5
    is_plateauing = (len(recent) >= 3 and
                     recent_kept > 0 and
                     recent_kept < len(recent) * 0.3)

    return {
        "agent": agent_name,
        "total_experiments": total,
        "kept": len(kept),
        "reverted": len(reverted),
        "baseline_count": len(baseline),
        "success_rate": len(kept) / total if total > 0 else 0,
        "is_stuck": is_stuck,
        "is_plateauing": is_plateauing,
        "recent_success_rate": recent_kept / len(recent) if recent else 0,
        "common_in_kept": kept_words.most_common(10),
        "common_in_reverted": reverted_words.most_common(10),
    }


def analyze_all() -> list[dict]:
    """Analyze all agents."""
    agents = [
        d.name for d in AGENTS_DIR.iterdir()
        if d.is_dir() and (d / "program.md").exists()
    ]
    return [analyze_agent(name) for name in sorted(agents)]


def print_agent_analysis(analysis: dict):
    """Pretty-print a single agent's analysis."""
    name = analysis["agent"]
    print(f"\n{'='*60}")
    print(f"  {name} — Analysis")
    print(f"{'='*60}")
    print(f"  Total experiments: {analysis['total_experiments']}")
    print(f"  Kept:              {analysis.get('kept', 0)}")
    print(f"  Reverted:          {analysis.get('reverted', 0)}")
    rate = analysis.get('success_rate', 0)
    print(f"  Success rate:      {rate*100:.0f}%")

    if analysis.get("is_stuck"):
        print(f"  ⚠️  STUCK — last 5 experiments all reverted")
    elif analysis.get("is_plateauing"):
        print(f"  📊 Plateauing — recent success rate dropping")
    elif analysis["total_experiments"] == 0:
        print(f"  🆕 Not started yet")
    elif analysis.get("kept", 0) > 0:
        print(f"  ✅ Active — making progress")

    if analysis.get("common_in_kept"):
        words = [w for w, _ in analysis["common_in_kept"][:5]]
        print(f"  Successful strategies mention: {', '.join(words)}")
    if analysis.get("common_in_reverted"):
        words = [w for w, _ in analysis["common_in_reverted"][:5]]
        print(f"  Failed strategies mention:     {', '.join(words)}")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyze" and len(sys.argv) > 2:
        agent_name = sys.argv[2]
        analysis = analyze_agent(agent_name)
        print_agent_analysis(analysis)
    else:
        analyses = analyze_all()
        print(f"\n{'Agent':<22} {'Experiments':<13} {'Kept':<6} "
              f"{'Reverted':<10} {'Success%':<10} {'Status':<15}")
        print("-" * 76)
        for a in analyses:
            rate = (f"{a.get('success_rate', 0)*100:.0f}%"
                    if a["total_experiments"] > 0 else "—")
            if a["total_experiments"] == 0:
                st = "not started"
            elif a.get("is_stuck"):
                st = "STUCK"
            elif a.get("is_plateauing"):
                st = "plateauing"
            elif a.get("kept", 0) > 0:
                st = "active"
            else:
                st = "attempted"
            print(f"{a['agent']:<22} {a['total_experiments']:<13} "
                  f"{a.get('kept', 0):<6} {a.get('reverted', 0):<10} "
                  f"{rate:<10} {st:<15}")
