# Cron Wizard

Optimize your cron job scheduling to minimize resource contention and missed execution windows.

## Problem

Your cron jobs cluster at predictable times (top of hour, midnight), causing:
- **Resource contention:** Multiple jobs competing for CPU, IO, network, or memory simultaneously
- **Missed deadlines:** Jobs starting outside their preferred execution windows
- **Dependency violations:** Jobs starting before their dependencies finish
- **Low utilization:** Idle periods followed by peaks

Monitoring tools like **Cronitor** ($20/mo), **Healthchecks.io** ($20/mo), or **PagerDuty** ($39/mo) alert you *after* problems occur. Cron Wizard *prevents* them.

## Solution

Upload your `crontab` (40+ jobs with metadata) to **agent-hub.dev**. Cron Wizard:

1. **Analyzes** your current schedule for contention, window violations, and dependencies
2. **Generates** optimizations using constraint-satisfaction logic
3. **Simulates** 24 hours to predict contention scores
4. **Delivers** a new schedule with zero missed windows and minimal resource conflicts

## Quick Start

### 1. Prepare Your Manifest
Generate `job_manifest.json` (or upload your own):
```bash
python prepare.py generate
```

### 2. Review Hypotheses
Read `program.md` for 8+ optimization strategies.

### 3. Implement Your Optimization
Edit `schedule_config.py`:
```python
def optimize_schedule(jobs: list[dict]) -> dict:
    """Return {job_id: new_cron_expression}."""
    # Your scheduling logic here
    return {0
    
        "backup-db-primary": "0 2 * * *",  # Move to 2am
        "send-reports": "30 1 * * *",       # Stagger to 1:30am
    }
```

### 4. Evaluate
```bash
python harness.py          # Score your optimization
python harness.py baseline # View baseline score
```

### Output
```
RESULT: schedule_score=245.3 improvement_pct=+145%
```

## Job Manifest Schema

```json
{
  "job_id": "backup-db-primary",
  "priority": 5,
  "current_cron": "0 0 * * *",
  "duration_minutes": 45,
  "resource_type": "io",
  "resource_weight": 9,
  "depends_on": [],
  "deadline_minutes": 240,
  "preferred_window": {"start_hour": 2, "end_hour": 6}
}
```

- **priority:** 1-5 (5=highest; missed deadlines cost more)
- **duration_minutes:** How long the job runs
- **resource_type:** "cpu", "io", "network", or "memory"
- **resource_weight:** 1-10 (how much of that resource it uses)
- **depends_on:** List of job_ids that must complete first
- **deadline_minutes:** Max minutes after scheduled time before "missed"
- **preferred_window:** Ideal execution hours (e.g., 2-6am overnight)

## Scoring

**schedule_score = base(1000) − contention − window_misses − dependency_violations**

Higher score = better schedule. Baseline: ~−200 to −400. Optimal: ~+100 to +300.

### Contention Penalty
For each concurrent job pair on the same resource:
```
penalty = resource_weight × (num_concurrent_jobs − 1)
```

### Window Miss Penalty
For each job starting outside preferred_window:
```
penalty = 10 × priority
```

### Dependency Penalty
For each job starting before a dependency finishes:
```
penalty = 20 × priority
```

## Example Optimization

**Baseline** (40 jobs at default times):
```
schedule_score = -342.5
contention_penalty = 450.0
window_miss_penalty = 85.0
dependency_penalty = 60.0
```

**Optimized** (spread across hours, separate IO/CPU, align windows):
```
schedule_score = 156.2
contention_penalty = 125.0
window_miss_penalty = 0.0
dependency_penalty = 0.0
improvement = +498.7 (+145%)
```

## Use Cases

- **SaaS platforms:** Optimize database backups, cache warming, and metrics collection
- **E-commerce:** Stagger batch processing, reconciliation, and nightly aggregations
- **Data pipelines:** Schedule ETL jobs to avoid resource conflicts
- **Microservices:** Coordinate health checks, log aggregation, and cleanup across 100+ jobs

## API Reference (Forthcoming)

Coming soon: Upload crontabs via API, receive optimized schedules via webhook.

## License

MIT
