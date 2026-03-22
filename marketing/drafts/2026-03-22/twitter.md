# Twitter/X Drafts — 2026-03-22

## ci-speedup

Thread 1/2: Your CI takes 30 minutes because every job runs sequentially. ci-speedup parallelizes the pipeline automatically — topological sort, critical path analysis, cache-group merging. Baseline: 1,790s. Target: <600s.

Thread 2/2: Built on @karpathy's AutoResearch pattern. One config file. One metric. The agent iterates overnight. github.com/AdiVamsi/agent-hub

---

## docker-slim

Thread 1/2: 2.6GB Docker images because of gcc, pytest, node_modules, and .git still in prod. docker-slim identifies what to remove, what to replace, and applies multi-stage builds. Target: <400MB.

Thread 2/2: No Dockerfile rewriting. Just a config file that the agent optimizes iteration by iteration. github.com/AdiVamsi/agent-hub

---

## prompt-tuner

Thread 1/2: 200 labeled tickets. 30% accuracy with the baseline. prompt-tuner builds keyword dictionaries, regex patterns, and weighted scoring rules until it hits 90%+. No LLM API calls needed.

Thread 2/2: Your prompt logic, optimized overnight by a coding agent. github.com/AdiVamsi/agent-hub

---

## log-trimmer

Thread 1/2: 69% of your logs are noise. log-trimmer writes filtering rules that drop it while keeping 95%+ of real signal. Volume reduction: 60-70%. Cost savings: immediate.

Thread 2/2: Like Datadog Log Management — but open source and self-improving. github.com/AdiVamsi/agent-hub

---

## sql-optimizer

Thread 1/2: SELECT * everywhere. Correlated subqueries. Missing indexes. sql-optimizer rewrites 50 queries and cuts total cost from 2.3M to under 15K. No database migration required.

Thread 2/2: Point @AnthropicAI Claude Code at the folder. Come back to faster queries. github.com/AdiVamsi/agent-hub
