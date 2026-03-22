# Cache Tuner — AutoResearch Program

## Problem Statement

A web service experiences cache misses due to suboptimal eviction policies. Current FIFO eviction achieves ~30-40% hit rate. The goal is to improve cache hit rate by implementing smarter eviction policies that account for access patterns, object sizes, and categories.

**Cache Constraints:**
- Max capacity: 500 KB (not enough for all objects)
- Max items: 100 (not enough for all 200 unique keys)
- Access pattern: Zipfian distribution (80/20 rule), temporal locality, periodic bursts, scan patterns

## Baseline

**FIFO Eviction:** Evict oldest inserted item.
- Expected hit rate: ~0.30-0.40
- Reason: Doesn't consider frequency or recency; scans pollute cache with sequential keys

## Hypotheses for Improvement

### H1: Least Recently Used (LRU)
Evict the item with the smallest `last_access` timestamp.

**Rationale:** Recent items are more likely to be accessed again (temporal locality).

**Expected improvement:** +15-25% (should handle temporal patterns well).

---

### H2: Least Frequently Used (LFU)
Evict the item with the smallest `access_count`.

**Rationale:** Frequently accessed items (per Zipf distribution) should stay cached.

**Expected improvement:** +20-30% (aligns with 80/20 rule).

---

### H3: Size-Aware Eviction
Evict the largest item first (by `object_size_bytes`).

**Rationale:** Removing one large object frees space for multiple smaller objects, increasing item count.

**Expected improvement:** +10-20% (trades space for item diversity).

---

### H4: Category-Aware Eviction
Assign priorities by category:
- High value: `user_profile`, `session_data` (must keep for correctness)
- Medium value: `api_response`, `product_page`
- Low value: `static_asset`, `search_result` (can be recomputed)

Evict lowest priority items first.

**Rationale:** Application semantics dictate value; some caches are more important than others.

**Expected improvement:** +15-25% (depends on workload mix).

---

### H5: ARC-Style Adaptive Replacement Cache
Maintain two lists:
- T1: Recently accessed once
- T2: Recently accessed multiple times
- Ghost lists: recently evicted keys (to avoid re-caching)

Evict from T1 if it's larger relative to T2, else from T2. Track recently evicted to penalize re-accesses.

**Rationale:** Balances recency vs frequency; avoids thrashing on scan patterns.

**Expected improvement:** +25-35% (handles bursts and scans well).

---

### H6: Scan Resistance
Detect sequential access patterns (key_N → key_N+1 → key_N+2 → ...).

Mark these accesses as non-cacheable (return False from `on_access`).

**Rationale:** Scans pollute cache with one-time accesses; don't cache them.

**Expected improvement:** +10-20% (depends on scan frequency).

---

### H7: LRFU (Frequency + Recency Weighted)
Score each item as: `score = access_count * log(1 + α * (now - last_access))`

Where α controls recency weight. Evict lowest score.

**Rationale:** Combines frequency (multiplicative) and recency (logarithmic); flexible tuning.

**Expected improvement:** +25-35% (can balance both signals).

---

### H8: Size-Weighted Frequency
Score each item as: `score = access_count / (1 + object_size_bytes / avg_size)`

Prefer to keep small, frequent items; evict large, rare items.

**Rationale:** Maximizes hit rate per byte used (efficiency metric).

**Expected improvement:** +20-30% (aligns cache with economics).

---

## Experimental Plan

1. **Baseline (FIFO):** Establish ~0.30-0.40 hit rate.
2. **LFU:** Simple frequency heuristic.
3. **LRU:** Simple recency heuristic.
4. **Size-Aware:** Explore space-efficiency tradeoff.
5. **Category-Aware:** Test semantic hints.
6. **LRFU:** Weighted combination.
7. **Size-Weighted Frequency:** Efficiency-focused.
8. **ARC:** Complex adaptive algorithm.
9. **Scan Resistance:** Pattern detection.
10. **Ensemble methods:** Combine top performers.

**Success criteria:** Hit rate ≥ 0.70 (2x baseline).

**Headroom:** ~15-25 experiments possible before hitting diminishing returns.

## Expected Outcome

Optimal hit rate: **0.70-0.85** with smart eviction (LFU, LRU, LRFU, or ARC variants).
