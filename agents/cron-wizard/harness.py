#!/usr/bin/env python3
"""Cron Wizard harness - evaluates scheduling optimizations."""

import json
import re
from pathlib import Path
from collections import defaultdict


class CronParser:
    """Simple cron parser supporting standard patterns: *, numbers, ranges, steps."""

    @staticmethod
    def parse_field(field, min_val, max_val):
        """Parse a single cron field and return set of matching values."""
        if field == "*":
            return set(range(min_val, max_val + 1))

        values = set()
        for part in field.split(","):
            if "/" in part:
                # Handle step syntax: */15, 0-30/5, etc.
                range_part, step = part.split("/")
                step = int(step)
                if range_part == "*":
                    current = min_val
                    while current <= max_val:
                        values.add(current)
                        current += step
                else:
                    # Range with step
                    if "-" in range_part:
                        start, end = map(int, range_part.split("-"))
                    else:
                        start = int(range_part)
                        end = max_val
                    current = start
                    while current <= end and current <= max_val:
                        values.add(current)
                        current += step
            elif "-" in part:
                # Handle range: 1-5
                start, end = map(int, part.split("-"))
                values.update(range(start, end + 1))
            else:
                # Single number
                values.add(int(part))

        return values

    @staticmethod
    def parse(cron_expr):
        """Parse 5-field cron expression. Returns list of matching (hour, minute) tuples for 24h."""
        fields = cron_expr.split()
        if len(fields) != 5:
            raise ValueError(f"Invalid cron: {cron_expr} (need 5 fields)")

        minute, hour, day, month, dow = fields

        # Parse minute (0-59)
        minutes = CronParser.parse_field(minute, 0, 59)

        # Parse hour (0-23)
        hours = CronParser.parse_field(hour, 0, 23)

        # For simplicity, ignore day/month/dow and return all matching hour:minute in 24h
        matches = []
        for h in sorted(hours):
            for m in sorted(minutes):
                matches.append((h, m))

        return matches


def load_manifest():
    """Load job_manifest.json."""
    manifest_path = Path(__file__).parent / "job_manifest.json"
    with open(manifest_path) as f:
        return json.load(f)


def get_schedule_with_optimizations():
    """Load manifest and apply user optimizations."""
    jobs = load_manifest()

    # Import user's optimization function
    from schedule_config import optimize_schedule

    optimizations = optimize_schedule(jobs)

    # Apply optimizations
    for job in jobs:
        if job["job_id"] in optimizations:
            job["current_cron"] = optimizations[job["job_id"]]

    return jobs


def validate_optimizations(jobs, optimizations):
    """Validate that user's optimizations are safe."""
    valid_job_ids = {j["job_id"] for j in jobs}

    for job_id, cron in optimizations.items():
        if job_id not in valid_job_ids:
            raise ValueError(f"Unknown job_id: {job_id}")

        # Validate cron expression
        try:
            CronParser.parse(cron)
        except Exception as e:
            raise ValueError(f"Invalid cron '{cron}' for {job_id}: {e}")


def simulate_24_hours(jobs):
    """Simulate 24 hours in 5-minute slots. Return contention and penalty scores."""
    # Create lookup for job execution times
    job_exec_times = {}  # {job_id: [(hour, minute), ...]}
    job_by_id = {j["job_id"]: j for j in jobs}

    for job in jobs:
        try:
            matches = CronParser.parse(job["current_cron"])
            job_exec_times[job["job_id"]] = matches
        except Exception as e:
            print(f"Warning: Failed to parse cron for {job['job_id']}: {e}")
            job_exec_times[job["job_id"]] = []

    # Simulate 24 hours in 5-minute slots (288 slots = 1440 minutes / 5)
    slots = 24 * 60 // 5  # 288 slots
    running_jobs = defaultdict(list)  # {slot: [running job info]}

    # For each job, determine which slots it runs in
    for job_id, exec_times in job_exec_times.items():
        job = job_by_id[job_id]
        duration_slots = (job["duration_minutes"] + 4) // 5  # Round up to nearest slot

        for hour, minute in exec_times:
            start_slot = hour * 12 + minute // 5  # Convert to slot index
            for slot_offset in range(duration_slots):
                slot = start_slot + slot_offset
                if slot < slots:
                    running_jobs[slot].append(
                        {
                            "job_id": job_id,
                            "start_slot": start_slot,
                            "start_minute": hour * 60 + minute,
                            "hour": hour,
                            "minute": minute,
                        }
                    )

    # Calculate contention score (lower is better, so we'll negate for final score)
    contention_score = 0.0
    for slot, jobs_in_slot in running_jobs.items():
        # Group by resource type
        resources = defaultdict(list)
        for job_info in jobs_in_slot:
            job = job_by_id[job_info["job_id"]]
            resources[job["resource_type"]].append(job)

        # For each resource, sum penalties for concurrent jobs
        for resource_type, concurrent_jobs in resources.items():
            if len(concurrent_jobs) > 1:
                # Penalty = sum of (resource_weight * number_of_other_jobs)
                for job in concurrent_jobs:
                    weight = job["resource_weight"]
                    penalty = weight * (len(concurrent_jobs) - 1)
                    contention_score += penalty

    # Calculate window miss penalties
    window_miss_score = 0.0
    for job_id, exec_times in job_exec_times.items():
        job = job_by_id[job_id]
        preferred = job["preferred_window"]
        start_hour = preferred["start_hour"]
        end_hour = preferred["end_hour"]

        for hour, minute in exec_times:
            if hour < start_hour or hour > end_hour:
                window_miss_score += 10 * job["priority"]

    # Calculate dependency penalties
    dependency_score = 0.0
    for job_id, exec_times in job_exec_times.items():
        job = job_by_id[job_id]
        depends_on = job["depends_on"]

        if not depends_on or not exec_times:
            continue

        for hour, minute in exec_times:
            job_start_minute = hour * 60 + minute

            # Check each dependency
            for dep_id in depends_on:
                if dep_id not in job_exec_times:
                    continue

                dep_job = job_by_id[dep_id]
                dep_duration = dep_job["duration_minutes"]
                dep_exec_times = job_exec_times[dep_id]

                if not dep_exec_times:
                    dependency_score += 20 * job["priority"]
                    continue

                # Find closest prior execution of dependency
                dep_times = sorted([h * 60 + m for h, m in dep_exec_times])

                # Find latest execution time that's before our job start
                latest_prior = None
                for dep_start in dep_times:
                    if dep_start <= job_start_minute:
                        latest_prior = dep_start

                if latest_prior is not None:
                    # Check if dependency finishes before this job starts
                    dep_finish = latest_prior + dep_duration
                    if dep_finish > job_start_minute:
                        # Dependency still running when job starts!
                        dependency_score += 20 * job["priority"]
                else:
                    # No prior execution; closest is a future one
                    closest_future = min([t for t in dep_times if t > job_start_minute], default=None)
                    if closest_future is None or closest_future + dep_duration > job_start_minute:
                        dependency_score += 20 * job["priority"]

    # Final score: higher is better. Negate contention/penalties.
    # Base score is high, subtract penalties
    base_score = 1000.0
    schedule_score = base_score - contention_score - window_miss_score - dependency_score

    return {
        "schedule_score": schedule_score,
        "contention_penalty": contention_score,
        "window_miss_penalty": window_miss_score,
        "dependency_penalty": dependency_score,
        "base_score": base_score,
    }


def evaluate():
    """Evaluate current schedule."""
    jobs = get_schedule_with_optimizations()
    results = simulate_24_hours(jobs)

    baseline_jobs = load_manifest()
    baseline_results = simulate_24_hours(baseline_jobs)

    improvement = results["schedule_score"] - baseline_results["schedule_score"]
    improvement_pct = (improvement / abs(baseline_results["schedule_score"])) * 100 if baseline_results[
        "schedule_score"
    ] != 0 else 0

    print("=" * 60)
    print("CRON WIZARD EVALUATION")
    print("=" * 60)
    print(f"Baseline score:       {baseline_results['schedule_score']:.1f}")
    print(f"Current score:        {results['schedule_score']:.1f}")
    print(f"Improvement:          {improvement:+.1f}")
    print(f"Improvement %:        {improvement_pct:+.1f}%")
    print()
    print("Breakdown (current):")
    print(f"  Contention penalty:   {results['contention_penalty']:.1f}")
    print(f"  Window miss penalty:  {results['window_miss_penalty']:.1f}")
    print(f"  Dependency penalty:   {results['dependency_penalty']:.1f}")
    print()
    print("Breakdown (baseline):")
    print(f"  Contention penalty:   {baseline_results['contention_penalty']:.1f}")
    print(f"  Window miss penalty:  {baseline_results['window_miss_penalty']:.1f}")
    print(f"  Dependency penalty:   {baseline_results['dependency_penalty']:.1f}")
    print("=" * 60)
    print(f"RESULT: schedule_score={results['schedule_score']:.1f} improvement_pct={improvement_pct:+.1f}%")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "baseline":
        print("Generating baseline...")
        baseline_jobs = load_manifest()
        results = simulate_24_hours(baseline_jobs)
        print(f"BASELINE: schedule_score={results['schedule_score']:.1f}")
    else:
        evaluate()
