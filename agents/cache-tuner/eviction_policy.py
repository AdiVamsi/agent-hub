"""Cache Tuner - Editable Eviction Policy.

Available data:
  access_trace.json — 5000 requests with key, timestamp_ms, object_size_bytes, category
  cache_config.json — max_capacity_bytes=500000, max_items=100

Your job: implement a CachePolicy class with these methods:
  - on_access(key, size, timestamp, category) -> bool: returns True if item should be cached
  - on_evict(cache_state) -> str: returns key to evict when cache is full
  - on_init(config) -> None: initialize with cache config

cache_state is a dict: {key: {"size": int, "last_access": int, "access_count": int, "category": str}}

The harness replays the access trace through your policy:
  - Cache hit: item was in cache when requested -> +1 hit
  - Cache miss: item not in cache -> +0
  - Eviction needed: when cache is full (by bytes or items), calls on_evict

Metric: hit_rate (hits / total_requests) — HIGHER is better.
Baseline: FIFO eviction (evict oldest insertion).

Hints for improvement:
  - LRU (Least Recently Used): evict key with smallest last_access timestamp
  - LFU (Least Frequently Used): evict key with smallest access_count
  - Size-aware: evict largest items first (frees space faster)
  - Category-aware: user_profiles and session_data more valuable
  - ARC-style: track recently evicted keys to avoid re-caching them
  - Scan resistance: detect sequential patterns and don't cache them
  - LRFU (Frequency + Recency): combine both signals
"""


class CachePolicy:
    """LRFU + category-aware: combines recency, frequency, and category value signals."""

    CATEGORY_WEIGHT = {
        "user_profile": 3.0,
        "session_data": 3.0,
        "api_response": 2.0,
        "product_page": 1.5,
        "search_result": 1.0,
        "static_asset": 0.5,
    }

    def __init__(self):
        self.max_size = 500000
        self.max_items = 100

    def on_init(self, config):
        self.max_size = config.get("max_capacity_bytes", 500000)
        self.max_items = config.get("max_items", 100)

    def on_access(self, key, size, timestamp, category):
        return True

    def on_evict(self, cache_state):
        if not cache_state:
            return next(iter(cache_state))

        max_ts = max(v["last_access"] for v in cache_state.values())

        def score(key):
            v = cache_state[key]
            recency = max_ts - v["last_access"] + 1
            freq = v["access_count"]
            size = v["size"]
            cat_w = self.CATEGORY_WEIGHT.get(v.get("category", ""), 1.0)
            return (freq * cat_w) / (recency * (size ** 0.8))

        return min(cache_state.keys(), key=score)
