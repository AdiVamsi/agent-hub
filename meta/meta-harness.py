"""Meta-harness — evaluates the meta-agent's overall performance.

Measures total improvement across all 5 agents.
NOT modified by the meta-agent.
"""

import sys
from pathlib import Path

# Import siblings
sys.path.insert(0, str(Path(__file__).parent))
from orchestrator import get_all_status
from tracker import analyze_all


def evaluate():
    """Run full meta-evaluation across all agents."""
    statuses = get_all_status()

    total_experiments = sum(s["experiments"] for s in statuses)
    total_kept = sum(s["kept"] for s in statuses)
    total_reverted = sum(s["reverted"] for s in statuses)
    agents_optimized = sum(1 for s in statuses if s["kept"] > 0)

    agents_with_experiments = [s for s in statuses if s["experiments"] > 0]
    avg_success_rate = (
        sum(s["success_rate"] for s in agents_with_experiments)
        / len(agents_with_experiments)
    ) if agents_with_experiments else 0

    print(f"\n{'='*65}")
    print(f"  META-EVALUATION")
    print(f"{'='*65}")
    print(f"  Agents optimized:    {agents_optimized}/5")
    print(f"  Total experiments:   {total_experiments}")
    print(f"  Total kept:          {total_kept}")
    print(f"  Total reverted:      {total_reverted}")
    print(f"  Avg success rate:    {avg_success_rate*100:.0f}%")
    print(f"{'='*65}\n")

    print(f"META-RESULT: agents_optimized={agents_optimized}/5 "
          f"total_experiments={total_experiments} "
          f"total_kept={total_kept} "
          f"total_reverted={total_reverted} "
          f"avg_success_rate={avg_success_rate:.2f}")


def status():
    """Print current status of all agents."""
    statuses = get_all_status()
    analyses = {a["agent"]: a for a in analyze_all()}

    print(f"\n{'='*75}")
    print(f"  AGENT-HUB STATUS")
    print(f"{'='*75}")
    print(f"  {'Agent':<22} {'Status':<14} {'Experiments':<13} "
          f"{'Kept':<6} {'Success%':<10}")
    print(f"  {'-'*65}")

    for s in statuses:
        rate = (f"{s['success_rate']*100:.0f}%"
                if s["experiments"] > 0 else "—")
        analysis = analyses.get(s["name"], {})
        if s["experiments"] == 0:
            st_icon = "⬜"
        elif analysis.get("is_stuck"):
            st_icon = "🔴"
        elif s["kept"] > 0:
            st_icon = "🟢"
        else:
            st_icon = "🟡"
        print(f"  {st_icon} {s['name']:<20} {s['status']:<14} "
              f"{s['experiments']:<13} {s['kept']:<6} {rate:<10}")

    optimized = sum(1 for s in statuses if s["kept"] > 0)
    total_exp = sum(s["experiments"] for s in statuses)
    print(f"\n  {optimized}/5 agents optimized · {total_exp} total experiments")
    print(f"{'='*75}\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "evaluate":
        evaluate()
    elif cmd == "status":
        status()
    else:
        print("Usage: python meta-harness.py [evaluate|status]")
