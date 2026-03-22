"""Agent runner — executes individual agent optimization loops.

This is utility code for the meta-agent. It helps navigate to each
agent's directory and understand their setup.

NOT modified by the meta-agent — only orchestrator.py is editable.
"""

import subprocess
import sys
from pathlib import Path


AGENTS_DIR = Path(__file__).parent.parent / "agents"


def get_agent_path(agent_name: str) -> Path:
    """Get the absolute path to an agent's directory."""
    path = AGENTS_DIR / agent_name
    if not path.exists():
        raise ValueError(f"Agent '{agent_name}' not found at {path}")
    return path


def run_agent_command(agent_name: str, command: str,
                      timeout: int = 120) -> str:
    """Run a command in an agent's directory and return output."""
    agent_path = get_agent_path(agent_name)
    result = subprocess.run(
        command,
        shell=True,
        cwd=str(agent_path),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout + result.stderr


def get_agent_baseline(agent_name: str) -> str:
    """Run the baseline evaluation for an agent."""
    return run_agent_command(agent_name, "python3 harness.py baseline")


def get_agent_evaluation(agent_name: str) -> str:
    """Run the current evaluation for an agent."""
    return run_agent_command(agent_name, "python3 harness.py evaluate")


def read_agent_file(agent_name: str, filename: str) -> str:
    """Read a file from an agent's directory."""
    path = get_agent_path(agent_name) / filename
    if not path.exists():
        return f"(file not found: {filename})"
    return path.read_text()


def list_agents() -> list[str]:
    """List all agent directory names."""
    return sorted([
        d.name for d in AGENTS_DIR.iterdir()
        if d.is_dir() and (d / "program.md").exists()
    ])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "eval" and len(sys.argv) > 2:
        agent_name = sys.argv[2]
        print(f"Evaluating {agent_name}...")
        output = get_agent_evaluation(agent_name)
        print(output)
    else:
        print("Available agents:")
        for name in list_agents():
            path = get_agent_path(name)
            has_results = (path / "results.tsv").exists()
            marker = "(has results)" if has_results else "(no results yet)"
            print(f"  {name} {marker}")
