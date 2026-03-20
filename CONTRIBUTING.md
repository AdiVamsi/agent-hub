# Contributing to agent-hub

Thanks for your interest in contributing! This repo is a collection of autonomous AI agents that each follow the same simple pattern.

## Adding a New Agent

1. Copy the template:

```bash
cp -r templates/blank-agent agents/your-agent-name
```

2. Fill in the four files:

   - **`program.md`** — Write clear, specific instructions for the AI agent. Describe the setup phase, the experiment loop, what hypotheses to try, and the success criteria.
   - **`editable.py`** — Create your baseline implementation. This is the ONLY file the agent will modify. Start simple — the agent will improve it iteratively.
   - **`harness.py`** — Build your evaluation infrastructure. This must produce a single scalar metric on a greppable `RESULT:` line. The agent never touches this file.
   - **`prepare.py`** — Write your data generation or preparation script. This creates whatever test data the harness needs.

3. Add a `README.md` explaining what your agent does, how to run it, and what metric it optimizes.

4. Add a `pyproject.toml` if your agent needs dependencies beyond the standard library.

5. Update the agent catalog table in the root `README.md`.

6. Submit a pull request.

## Improving Existing Agents

The best way to improve an agent is to actually run it and see where it gets stuck. Common improvements include better `program.md` instructions, more realistic test data in `prepare.py`, or a more accurate evaluation in `harness.py`.

The `router.py` (or equivalent editable file) should NOT be manually optimized — that's the agent's job. But if the agent consistently fails to find good solutions, improving the surrounding infrastructure helps.

## Guidelines

- Keep agents small and self-contained (readable in 20 minutes)
- No frameworks or complex dependencies — pure Python where possible
- Every agent must follow the 3-primitive pattern: program.md, one editable file, one scalar metric
- Test your agent by running at least a few experiments before submitting
