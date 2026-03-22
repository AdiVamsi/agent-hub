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
    """FIFO baseline: evict oldest inserted item."""

    def __init__(self):
        self.insertion_order = []
        self.config = None

    def on_init(self, config):
        """Initialize with cache configuration."""
        self.config = config
        self.insertion_order = []

    def on_access(self, key, size, timestamp, category):
        """Decide whether to cache this item.

        Args:
            key: cache key
            size: object size in bytes
            timestamp: request timestamp in ms
            category: one of {user_profile, product_page, search_result, session_data, api_response, static_asset}

        Returns:
            bool: True if item should be added to cache
        """
        return True  # FIFO baseline: always cache

    def on_evict(self, cache_state):
        """Decide which key to evict when cache is full.

        Args:
            cache_state: dict of {key: {"size": int, "last_access": int, "access_count": int, "category": str}}

        Returns:
            str: key to evict (must exist in cache_state)
        """
        # FIFO baseline: evict oldest inserted
        if self.insertion_order:
            for key in self.insertion_order:
                if key in cache_state:
                    self.insertion_order.remove(key)
                    return key

        # Fallback: return first key in cache_state
        return next(iter(cache_state))

    def record_insertion(self, key):
        """Helper: track insertion order for FIFO."""
        if key not in self.insertion_order:
            self.insertion_order.append(key)
