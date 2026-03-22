# API Racer — AutoResearch Program

## Problem
API endpoint configurations significantly impact response times and user experience. Most teams rely on manual tuning or rules-of-thumb, missing optimization opportunities. Average response times typically range from 80-120ms with no systematic optimization.

## Objective
Minimize average response time across a workload of 100 API endpoints by optimizing endpoint configurations (caching, connection pools, batching, compression). Target: reduce from ~100ms baseline to ~15-30ms.

## Hypotheses

### H1: Enable caching on cacheable GET endpoints
**Rationale**: GET endpoints flagged as cacheable can serve cached responses in ~2ms vs. original latency. With 80% cache hit rate, this should dramatically reduce response times for high-traffic cacheable endpoints.

**Experiment**: For all endpoints where `cacheable=true` and `method=GET`, set `cache_ttl_seconds` to 300-3600 seconds and measure improvement.

---

### H2: Batch database queries on heavy endpoints
**Rationale**: Endpoints with 3+ database queries can batch them into a single query, reducing round-trip time by ~60%. This is especially effective on POST/PUT endpoints that modify multiple tables.

**Experiment**: For endpoints with `db_queries > 2`, enable `batch_enabled=true` and verify the 60% DB time reduction materializes.

---

### H3: Right-size connection pools for upstream calls
**Rationale**: Endpoints making upstream service calls benefit from connection pooling, reducing latency by ~min(pool_size/5, 0.7). However, oversized pools waste memory (penalty: pool_size * 0.1ms if pool > 2x needed).

**Experiment**: For endpoints with `upstream_calls > 0`, incrementally increase `connection_pool_size` from 1 to the optimal point (e.g., upstream_calls * 3), balancing latency reduction vs. memory overhead.

---

### H4: Enable compression on large payloads
**Rationale**: Payloads > 1KB benefit from compression, reducing transfer time by ~70%. This is particularly effective on GET endpoints returning rich data (products, posts, analytics).

**Experiment**: For endpoints with `avg_payload_bytes > 1000`, enable `compression_enabled=true` and measure the payload transfer time reduction.

---

### H5: Optimize by traffic volume (high-traffic first)
**Rationale**: The overall metric is weighted by `calls_per_minute`. Focusing optimizations on high-traffic endpoints (top 20% by volume) will have the largest impact on the overall average.

**Experiment**: Rank endpoints by `calls_per_minute`, apply aggressive optimizations to the top 20, measure total improvement. Compare with uniform optimization.

---

### H6: Tune cache TTLs by endpoint volatility
**Rationale**: Different endpoints have different data volatility. High-traffic, stable endpoints (e.g., product catalogs) can use long TTLs (3600s). Volatile endpoints (e.g., user notifications) need short TTLs (60-300s) to balance freshness and performance.

**Experiment**: Classify endpoints by data volatility (using db_queries as a proxy: more queries = more volatile), set cache_ttl accordingly, measure improvement vs. uniform TTL.

---

### H7: Pool sharing between similar endpoints
**Rationale**: Endpoints sharing the same upstream service can share connection pools (e.g., all product-related endpoints sharing a product-service pool). This reduces per-endpoint memory while maintaining latency benefits.

**Experiment**: Group endpoints by path prefix (e.g., `/products*`, `/orders*`), assign shared connection pools, measure memory efficiency and latency.

---

### H8: Database pool size optimization
**Rationale**: Similar to connection pools, database pool sizing balances latency reduction (more connections = lower wait time) with memory overhead. Optimal size is ~db_queries * 2, with diminishing returns beyond.

**Experiment**: For each endpoint, set `db_pool_size = max(1, min(db_queries * 2, 20))` and measure improvement vs. default pool size of 1. Verify penalty kicks in if pool > 2x needed.

---

## Experimental Strategy

### Phase 1: Baseline & Single-Knob Optimization
1. Measure baseline (no optimizations): expected ~80-120ms
2. Test each hypothesis individually (H1-H8) to quantify individual improvements
3. Identify which optimizations have highest ROI per endpoint

### Phase 2: Combination & Interaction
4. Apply top-performing optimizations in combination
5. Test interaction effects (e.g., cache + compression, batching + pooling)
6. Identify synergies and conflicts

### Phase 3: Refinement & Tuning
7. Fine-tune parameters (cache TTL values, pool sizes) for maximum improvement
8. Test on different workload distributions
9. Converge on optimal configuration across all 100 endpoints

### Phase 4: Validation & Guardrails
10. Verify no invalid configs (bounds checking)
11. Test penalty mechanism for oversized pools
12. Measure final improvement pct: target ~80% (120ms → 20ms) or better

## Success Criteria
- **Baseline**: ~100ms average response time (no optimizations)
- **Target**: ~20ms average response time (80% improvement)
- **Iterations**: 15-25 experiments headroom within hypothesis space
- **Metric**: `(baseline_ms - optimized_ms) / baseline_ms * 100` improvement percentage
