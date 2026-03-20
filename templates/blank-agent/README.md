# Blank Agent Template

Use this template to create a new agent for agent-hub.

## How to Use

1. Copy this folder:
   ```bash
   cp -r templates/blank-agent agents/your-agent-name
   ```

2. Fill in each file:

   **`program.md`** — Write your research instructions. This is the "program" that tells the AI agent what to do. Include: setup steps, what hypotheses to explore, how to check results, and when to commit vs revert.

   **`editable.py`** — Write your baseline implementation. This is the ONLY file the agent will modify. Start with the simplest possible version — the agent will improve it.

   **`harness.py`** — Write your evaluation infrastructure. It must: load test data, import and call editable.py, calculate a single scalar metric, and print a `RESULT:` line that the agent can grep for.

   **`prepare.py`** — Write your data generation script. This creates whatever test data the harness needs to evaluate the editable file.

3. Add a `pyproject.toml` if you need dependencies beyond the standard library.

4. Update the agent catalog in the root `README.md`.

## The Pattern

Every agent follows Karpathy's AutoResearch design:

- **One program** (`program.md`) — Human-written instructions
- **One editable file** (`editable.py`) — The only file the agent touches
- **One scalar metric** — The single number that determines success

The agent reads the program, edits the file, runs the evaluation, and commits if the metric improved. Repeat forever.
