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
    # Greedy critical-path scheduling:
    # At each step, pick the non-parallelizable job with highest critical path value.
    # Pack all ready parallelizable jobs into the same stage.
    # This respects: max 1 non-para job per stage, all deps in earlier stages.

    job_map = {j["name"]: j for j in jobs}

    # Build dependents map (reverse edges)
    dependents = {j["name"]: [] for j in jobs}
    for j in jobs:
        for dep in j.get("dependencies", []):
            dependents[dep].append(j["name"])

    # Critical path: duration + max CP of all dependents
    cp = {}
    def get_cp(name):
        if name in cp:
            return cp[name]
        dur = job_map[name]["duration_seconds"]
        if not dependents[name]:
            cp[name] = dur
        else:
            cp[name] = dur + max(get_cp(d) for d in dependents[name])
        return cp[name]

    for j in jobs:
        get_cp(j["name"])

    completed = set()
    scheduled = set()
    stages = []

    while len(scheduled) < len(jobs):
        ready = [
            j["name"] for j in jobs
            if j["name"] not in scheduled
            and all(d in completed for d in j.get("dependencies", []))
        ]

        para_ready = [n for n in ready if job_map[n].get("parallelizable", True)]
        nonpara_ready = [n for n in ready if not job_map[n].get("parallelizable", True)]

        if nonpara_ready:
            # Pick non-para job with highest critical path (most urgent)
            chosen = max(nonpara_ready, key=lambda n: cp[n])
            stage = [chosen] + para_ready
        elif para_ready:
            stage = para_ready
        else:
            break  # No progress (shouldn't happen with valid DAG)

        stages.append(stage)
        for name in stage:
            scheduled.add(name)
            completed.add(name)

    return stages
