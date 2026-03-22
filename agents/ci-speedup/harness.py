#!/usr/bin/env python3
"""
CI Pipeline optimizer harness.

Validates schedules and computes total build time.

CLI:
  python harness.py baseline  — compute baseline (sequential)
  python harness.py evaluate  — evaluate current pipeline_config
"""

import hashlib
import json
import sys
from pathlib import Path

from pipeline_config import optimize_pipeline


def load_pipeline():
    """Load pipeline.json."""
    with open("pipeline.json", "r") as f:
        return json.load(f)


def compute_pipeline_hash(jobs):
    """Compute a hash of the pipeline data for baseline validation."""
    pipeline_json = json.dumps(jobs, sort_keys=True)
    return hashlib.sha256(pipeline_json.encode()).hexdigest()


def validate_and_compute(jobs, schedule):
    """
    Validate schedule and compute total_build_time.

    Checks:
      - Schedule is a list of lists of strings
      - Every job appears exactly once
      - All dependencies are in earlier stages than the job
      - No non-parallelizable jobs share a stage

    Returns:
        (is_valid, total_build_time, error_message)
    """
    # Check return type: schedule should be list[list[str]]
    if not isinstance(schedule, list):
        return False, 999999, f"Schedule must be a list, got {type(schedule).__name__}"

    for i, stage in enumerate(schedule):
        if not isinstance(stage, list):
            return False, 999999, f"Stage {i} must be a list, got {type(stage).__name__}"
        if len(stage) == 0:
            return False, 999999, f"Stage {i} is empty"
        for job_name in stage:
            if not isinstance(job_name, str):
                return False, 999999, f"Stage {i} contains non-string job name: {job_name}"

    # Check every job appears exactly once
    scheduled_jobs = set()
    for stage in schedule:
        for job_name in stage:
            if job_name in scheduled_jobs:
                return False, 999999, f"Job '{job_name}' appears multiple times"
            scheduled_jobs.add(job_name)

    job_names = {job["name"] for job in jobs}
    if scheduled_jobs != job_names:
        missing = job_names - scheduled_jobs
        extra = scheduled_jobs - job_names
        msg = ""
        if missing:
            msg += f"Missing jobs: {missing}. "
        if extra:
            msg += f"Extra jobs: {extra}."
        return False, 999999, msg

    # Build a map of job_name -> stage_index for dependency checking
    job_to_stage = {}
    for stage_idx, stage in enumerate(schedule):
        for job_name in stage:
            job_to_stage[job_name] = stage_idx

    # Check dependencies
    job_map = {job["name"]: job for job in jobs}
    for job_name, stage_idx in job_to_stage.items():
        job = job_map[job_name]
        for dep in job.get("dependencies", []):
            if dep not in job_to_stage:
                return False, 999999, f"Dependency '{dep}' not found for job '{job_name}'"
            dep_stage = job_to_stage[dep]
            if dep_stage >= stage_idx:
                return False, 999999, (
                    f"Dependency violation: job '{job_name}' (stage {stage_idx}) "
                    f"depends on '{dep}' (stage {dep_stage})"
                )

    # Check that non-parallelizable jobs don't share a stage
    for stage_idx, stage in enumerate(schedule):
        non_parallelizable_jobs = [
            job_name for job_name in stage
            if not job_map[job_name].get("parallelizable", True)
        ]
        if len(non_parallelizable_jobs) > 1:
            return False, 999999, (
                f"Stage {stage_idx} has {len(non_parallelizable_jobs)} non-parallelizable jobs: "
                f"{non_parallelizable_jobs}. Non-parallelizable jobs cannot share a stage."
            )

    # Compute total_build_time
    total_build_time = 0.0
    for stage_idx, stage in enumerate(schedule):
        # Check stage is non-empty (already checked above, but defensive)
        if len(stage) == 0:
            return False, 999999, f"Stage {stage_idx} is empty"
        max_duration = max(job_map[job_name]["duration_seconds"] for job_name in stage)
        total_build_time += max_duration

    return True, total_build_time, ""


def compute_baseline(jobs):
    """Baseline: run all jobs sequentially."""
    schedule = [[job["name"]] for job in jobs]
    is_valid, total_time, error = validate_and_compute(jobs, schedule)
    return total_time


def main():
    if len(sys.argv) < 2:
        print("Usage: python harness.py [baseline|evaluate]")
        sys.exit(1)

    command = sys.argv[1]
    jobs = load_pipeline()

    if command == "baseline":
        baseline_time = compute_baseline(jobs)
        pipeline_hash = compute_pipeline_hash(jobs)
        baseline_data = {
            "baseline_time": baseline_time,
            "pipeline_hash": pipeline_hash
        }
        with open(".baseline.json", "w") as f:
            json.dump(baseline_data, f)
        print(f"BASELINE: total_build_time={baseline_time:.1f}")
        return

    if command == "evaluate":
        # Compute baseline if not cached, and validate pipeline hasn't changed
        pipeline_hash = compute_pipeline_hash(jobs)
        if Path(".baseline.json").exists():
            with open(".baseline.json", "r") as f:
                baseline_data = json.load(f)
                baseline_time = baseline_data["baseline_time"]
                cached_hash = baseline_data.get("pipeline_hash")
                # Invalidate baseline if pipeline changed
                if cached_hash and cached_hash != pipeline_hash:
                    print("BASELINE INVALIDATED: pipeline.json has changed")
                    baseline_time = compute_baseline(jobs)
        else:
            baseline_time = compute_baseline(jobs)

        # Get schedule from pipeline_config
        schedule = optimize_pipeline(jobs)

        # Validate and compute
        is_valid, total_time, error = validate_and_compute(jobs, schedule)

        if not is_valid:
            print(f"VALIDATION FAILED: {error}")
            print(f"RESULT: total_build_time=999999.0 improvement_pct=0.0")
            return

        improvement_pct = ((baseline_time - total_time) / baseline_time) * 100
        print(f"RESULT: total_build_time={total_time:.1f} improvement_pct={improvement_pct:.1f}")
        return

    print(f"Unknown command: {command}")
    sys.exit(1)


if __name__ == "__main__":
    main()
