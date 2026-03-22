"""CI Pipeline Optimizer — editable file.

Available data: pipeline.json with 30 jobs, each having:
  - name: job identifier string
  - duration_seconds: integer, job execution time
  - dependencies: list of job names this job depends on
  - cache_key: string or null, shared artifact identifier
  - parallelizable: boolean, whether job can run in parallel with others

Your job: implement optimize_pipeline(jobs) that returns a schedule.
The schedule is a list of "stages" — each stage is a list of job names that run in parallel.
All jobs in a stage start simultaneously. A stage doesn't start until the previous stage finishes.
Dependencies must be respected: if job B depends on job A, B must be in a later stage than A.

Metric: total_build_time (sum of max duration in each stage) — LOWER is better.
Baseline: 1790 seconds (all jobs sequential, sum of all durations).
Target: 500-700 seconds (60-72% improvement).

The harness calls: schedule = optimize_pipeline(jobs)
"""


def optimize_pipeline(jobs: list[dict]) -> list[list[str]]:
    """Return a schedule: list of stages, each stage is a list of job names.

    Baseline: one job per stage (fully sequential).

    Args:
        jobs: List of job dicts with keys: name, duration_seconds, dependencies, cache_key, parallelizable

    Returns:
        List of stages, where each stage is a list of job names.
        All jobs in a stage run in parallel.
        A job cannot start until all its dependencies are completed.
    """
    # Baseline: one job per stage (fully sequential)
    return [[job["name"]] for job in jobs]
