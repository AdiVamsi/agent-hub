#!/usr/bin/env python3
"""
CI Pipeline optimizer harness.

Validates schedules and computes total build time.

CLI:
  python harness.py baseline  — compute baseline (sequential)
  python harness.py evaluate  — evaluate current pipeline_config
"""

import json
import sys
from pathlib import Path

from pipeline_config import optimize_pipeline


def load_pipeline():
    """Load pipeline.json."""
    with open("pipeline.json", "r") as f:
        return json.load(f)


def validate_and_compute(jobs, schedule):
    """
    Validate schedule and compute total_build_time.

    Checks:
      - Every job appears exactly once
      - All dependencies are in earlier stages than the job

    Returns:
        (is_valid, total_build_time, error_message)
    """
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

    # Compute total_build_time
    job_map = {job["name"]: job for job in jobs}
    total_build_time = 0.0
    for stage in schedule:
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
        baseline_data = {"baseline_time": baseline_time}
        with open(".baseline.json", "w") as f:
            json.dump(baseline_data, f)
        print(f"BASELINE: total_build_time={baseline_time:.1f}")
        return

    if command == "evaluate":
        # Compute baseline if not cached
        if Path(".baseline.json").exists():
            with open(".baseline.json", "r") as f:
                baseline_data = json.load(f)
                baseline_time = baseline_data["baseline_time"]
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
