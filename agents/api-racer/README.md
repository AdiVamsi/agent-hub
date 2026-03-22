# API Racer — Optimize API Endpoint Configurations

**Minimize average response time across your API workload through intelligent endpoint configuration.**

## Overview

API Racer automates the optimization of API endpoint configurations to reduce latency and improve user experience. By analyzing your endpoint characteristics (traffic volume, database queries, payload size, upstream dependencies), the system recommends optimal configurations for caching, connection pooling, batching, and compression.

### The Problem

Modern APIs typically operate without systematic optimization:
- Manual tuning is time-consuming and error-prone
- Configuration decisions lack data-driven justification
- Optimization opportunities go unnoticed across hundreds of endpoints
- Teams use guesswork instead of measured improvements

**Baseline**: ~100ms average response time (unoptimized)
**Target**: ~20ms average response time (80% improvement)

## How It Works

### 1. **Workload Analysis**
Provide your API specification (100 endpoints from api_workload.json):
- Endpoint method (GET, POST, PUT, DELETE)
- Traffic volume (calls per minute)
- Payload size (bytes)
- Database queries per request
- Upstream service dependencies
- Cache eligibility

### 2. **Optimization Engine**
Six key optimization levers:

| Lever | Benefit | Best For |
|-------|---------|----------|
| **Caching** | 2ms response (80% hit rate) | Cacheable GET endpoints |
| **Batching** | 60% DB time reduction | Endpoints with 3+ DB queries |
| **Connection Pools** | Up to 70% upstream latency reduction | Endpoints with service dependencies |
| **Compression** | 70% payload transfer reduction | Large responses (>1KB) |
| **Database Pools** | Reduced connection wait time | High-traffic endpoints |
| **Rate Limiting** | Controlled degradation | Overloaded endpoints |

### 3. **Simulation & Evaluation**
- Simulates response time with each configuration
- Weights by traffic volume (calls_per_minute)
- Penalizes oversized pools (memory waste)
- Validates all config bounds (caching, pool sizes)
- Measures improvement percentage

## Usage

### Generate Workload
```bash
python prepare.py generate
```
Creates `api_workload.json` with 100 realistic API endpoints.

### Measure Baseline
```bash
python harness.py baseline
```
Example output:
```
RESULT: baseline_avg_response_ms=105.34
```

### Evaluate Optimization
```bash
python harness.py evaluate
```
Example output:
```
RESULT: avg_response_ms=18.45 improvement_pct=82.5
```

## Configuration API

Edit `endpoint_config.py` and implement `optimize_endpoint(endpoint_info: dict) -> dict`:

```python
def optimize_endpoint(endpoint_info: dict) -> dict:
    """
    Args:
        endpoint_info: {
            'endpoint_id': 'ep_001',
            'method': 'GET',
            'path': '/users/{id}',
            'avg_payload_bytes': 500,
            'calls_per_minute': 100,
            'current_p50_ms': 45.0,
            'current_p99_ms': 120.5,
            'cacheable': True,
            'db_queries': 2,
            'upstream_calls': 1,
            'auth_required': True
        }

    Returns:
        {
            'cache_ttl_seconds': 300,              # 0 = no cache, 1-3600s
            'connection_pool_size': 5,            # 1-50
            'db_pool_size': 5,                    # 1-20
            'batch_enabled': False,               # bool
            'compression_enabled': True,          # bool
            'rate_limit_rpm': 0                   # 0 = no limit, >0 = requests/min
        }
    """
    # Your logic here
    return config
```

### Configuration Bounds
- `cache_ttl_seconds`: 0–3600 (0 = disabled)
- `connection_pool_size`: 1–50
- `db_pool_size`: 1–20
- `batch_enabled`: true/false
- `compression_enabled`: true/false
- `rate_limit_rpm`: 0–unlimited

## Example Optimizations

### High-Traffic GET Endpoint (Cacheable)
```python
if endpoint_info['method'] == 'GET' and endpoint_info['cacheable']:
    if endpoint_info['calls_per_minute'] > 50:
        return {
            'cache_ttl_seconds': 600,
            'compression_enabled': endpoint_info['avg_payload_bytes'] > 1000
        }
```

### Heavy Database Endpoint
```python
if endpoint_info['db_queries'] > 2:
    return {
        'batch_enabled': True,
        'db_pool_size': min(endpoint_info['db_queries'] * 2, 20)
    }
```

### Upstream Service Dependency
```python
if endpoint_info['upstream_calls'] > 0:
    return {
        'connection_pool_size': min(endpoint_info['upstream_calls'] * 3, 50)
    }
```

## Hypotheses & Research Program

See `program.md` for 8+ hypotheses:
1. Cache on cacheable GETs
2. Batch database queries
3. Right-size connection pools
4. Compress large payloads
5. High-traffic prioritization
6. Adaptive cache TTLs
7. Shared connection pools
8. Database pool optimization

## Simulation Model

### Response Time Calculation
```
base_time = 5ms
db_time = db_queries * 15ms
upstream_time = upstream_calls * 50ms
payload_time = avg_payload_bytes * 0.001ms

response_time = base_time + db_time + upstream_time + payload_time
```

### Optimization Impacts
- **Cache hit**: response_time = 0.8 * 2ms + 0.2 * original
- **Batching**: db_time *= 0.4 (if db_queries > 2)
- **Connection pool**: upstream_time *= (1 - min(pool_size/5, 0.7))
- **Compression**: payload_time *= 0.3 (if payload > 1KB)
- **Pool penalty**: response_time += pool_size * 0.1ms (if oversized)

## Metrics

**Primary Metric**: `avg_response_ms` (weighted by calls_per_minute)

**Improvement %**: `(baseline - optimized) / baseline * 100`

**Target Range**: 15–25 experiments to achieve 80% improvement from baseline.

## Comparable Solutions

| Solution | Cost | Key Feature |
|----------|------|-------------|
| **Datadog APM** | $31/host/mo | Real-time monitoring |
| **New Relic** | $0.30/GB | Data-driven insights |
| **Speedscale** | $299/mo | Scenario testing |
| **API Racer** | Upload spec | Automated optimization |

## Getting Started

**Upload your API spec at [agent-hub.dev](https://agent-hub.dev)** for automated optimization analysis and recommendations.

## Development

No external dependencies. Pure Python standard library.

- Python 3.8+
- Uses `json`, `random`, `pathlib`

## Files

- `prepare.py` — Generate realistic API workload
- `endpoint_config.py` — Edit this file with your optimization logic
- `harness.py` — Evaluation engine (read-only)
- `program.md` — Research hypotheses and experimental strategy
- `README.md` — This file
- `pyproject.toml` — Project metadata

## License

MIT
