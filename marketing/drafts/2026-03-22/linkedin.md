# LinkedIn Drafts — 2026-03-22

## ci-speedup

Your CI pipeline runs 28 jobs sequentially in 1,790 seconds.

The system parallelizes them into stages, respects every dependency, and hits ~600s on the first pass.

No YAML surgery. No pipeline rewrite. Just point a coding agent at it and come back to a faster build.

Built on Karpathy's AutoResearch pattern — one file, one metric, infinite iterations.

github.com/AdiVamsi/agent-hub/tree/master/agents/ci-speedup

---

## docker-slim

Your Docker image is 2.6GB because nobody cleans up dev deps, build tools, and test fixtures.

The system identifies what's safe to remove, swaps in smaller alternatives, and applies multi-stage patterns — all while verifying nothing breaks.

Baseline 2,639MB. Target: under 400MB. Zero manual Dockerfile editing.

github.com/AdiVamsi/agent-hub/tree/master/agents/docker-slim

---

## prompt-tuner

You have 200 labeled support tickets. You need a classifier that works without calling an LLM API on every request.

The system iterates on keyword rules, regex patterns, and weighted scoring until accuracy climbs from 30% to 90%+.

Think of it as optimizing your prompt logic overnight — without spending a dollar on API calls.

github.com/AdiVamsi/agent-hub/tree/master/agents/prompt-tuner

---

## log-trimmer

69% of your logs are noise. Health checks, cache hits, heartbeats — drowning out the errors that matter.

The system writes filtering rules that drop the noise while keeping 95%+ of signal intact. Volume drops by 60-70% on the first pass.

Comparable to Datadog Log Management at $0.10/GB — except this runs locally and improves itself.

github.com/AdiVamsi/agent-hub/tree/master/agents/log-trimmer

---

## sql-optimizer

50 queries hitting your database. SELECT * everywhere. Correlated subqueries. Missing indexes. Missing LIMIT clauses.

The system rewrites them: specific columns, JOINs instead of subqueries, IN() instead of OR chains. Baseline cost 2.3M. Target: under 15K.

Point a coding agent at it and wake up to a faster database.

github.com/AdiVamsi/agent-hub/tree/master/agents/sql-optimizer
