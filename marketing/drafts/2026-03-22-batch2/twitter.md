# Twitter/X Drafts — 2026-03-22 (Batch 2)

## api-racer
1/2: Every endpoint in your API gets the same config. api-racer profiles traffic patterns and sets caching, pools, batching, compression per-endpoint. Baseline: 86ms. Target: <20ms.
2/2: Built on @karpathy's AutoResearch. One config file. One metric. The agent iterates overnight. github.com/AdiVamsi/agent-hub

## test-shrink
1/2: 150 tests, 87 seconds. Most coverage is redundant. test-shrink finds the minimum test set for 95%+ coverage. Respects dependencies. Drops the waste.
2/2: Same coverage. 80% less runtime. Point a coding agent at it. github.com/AdiVamsi/agent-hub

## iac-lint
1/2: 67 security misconfigs in your Terraform. Public S3, open 0.0.0.0/0, unencrypted RDS. iac-lint writes detection rules that find them all — penalized for false positives.
2/2: Self-improving Checkov. Gets smarter every iteration. github.com/AdiVamsi/agent-hub

## cache-tuner
1/2: FIFO cache = 52% hit rate. Half your requests hit the DB for no reason. cache-tuner experiments with LRU, LFU, size-aware policies on your actual traffic.
2/2: Target: 75%+ hits. Same RAM. Smarter eviction. github.com/AdiVamsi/agent-hub

## bundle-phobia
1/2: 2.6MB JS bundle. Moment, Lodash, D3 all on every page. bundle-phobia replaces, tree-shakes, and code-splits. Target: <500KB.
2/2: Your webpack config, optimized overnight by AI. github.com/AdiVamsi/agent-hub
