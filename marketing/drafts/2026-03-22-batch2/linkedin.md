# LinkedIn Drafts — 2026-03-22 (Batch 2)

## api-racer

Your API responds in 86ms because every endpoint uses the same config.

The system profiles each endpoint's traffic, DB queries, and upstream calls — then configures caching, connection pools, batching, and compression per-endpoint.

Target: under 20ms weighted average. No code changes. Just configuration.

github.com/AdiVamsi/agent-hub/tree/master/agents/api-racer

---

## test-shrink

150 tests. 87 seconds. Most of that time is redundant coverage.

The system finds the minimum set of tests that covers 95%+ of your codebase. Respects dependencies. Drops the slow e2e tests when unit tests already cover those lines.

Target: under 15 seconds. Same coverage. No tests deleted — just smarter selection.

github.com/AdiVamsi/agent-hub/tree/master/agents/test-shrink

---

## iac-lint

80 Terraform resources. 67 misconfigurations. Public S3 buckets, open security groups, unencrypted databases, missing tags.

The system writes detection rules that catch them all — without false positives. Each false positive costs 3 points. You can't brute-force it.

Think Checkov, but self-improving. Runs overnight, gets smarter each iteration.

github.com/AdiVamsi/agent-hub/tree/master/agents/iac-lint

---

## cache-tuner

FIFO gives you 52% hit rate. That means half your requests hit the database unnecessarily.

The system experiments with LRU, LFU, size-aware, category-aware, and scan-resistant policies. On realistic Zipf-distributed traffic.

Target: 75%+ hit rate. Same cache size. Just smarter eviction.

github.com/AdiVamsi/agent-hub/tree/master/agents/cache-tuner

---

## bundle-phobia

2.6MB JavaScript bundle. Moment.js, Lodash, D3 — all loaded on every page.

The system replaces heavy deps with lighter alternatives, tree-shakes unused exports, and code-splits large libraries. All validated — nothing breaks.

Target: under 500KB. Same features. Faster first paint.

github.com/AdiVamsi/agent-hub/tree/master/agents/bundle-phobia
