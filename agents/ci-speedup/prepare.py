#!/usr/bin/env python3
"""
Generates synthetic CI pipeline data for optimization.

CLI: python prepare.py generate
Outputs: pipeline.json
"""

import json
import random
import sys


def generate_pipeline(seed=42, num_jobs=30):
    """Generate a synthetic CI pipeline with realistic job dependencies."""
    random.seed(seed)

    # Define job templates with realistic names and typical durations
    job_templates = [
        # Fast jobs (linting, type checking)
        ("lint", 15, False, "lint-cache"),
        ("typecheck", 20, False, "typecheck-cache"),

        # Unit tests (can be parallelized)
        ("unit-tests-api", 45, True, "unit-cache"),
        ("unit-tests-web", 35, True, "unit-cache"),
        ("unit-tests-worker", 40, True, "unit-cache"),

        # Build jobs
        ("build-frontend", 120, False, "build-frontend-cache"),
        ("build-backend", 95, False, "build-backend-cache"),
        ("build-worker", 85, False, "build-worker-cache"),
        ("build-docker", 150, False, "docker-cache"),

        # Integration tests (depends on builds)
        ("integration-tests-api", 80, True, "integration-cache"),
        ("integration-tests-web", 70, True, "integration-cache"),
        ("integration-tests-worker", 75, True, "integration-cache"),

        # End-to-end tests
        ("e2e-tests-critical", 120, False, "e2e-cache"),
        ("e2e-tests-flows", 110, False, "e2e-cache"),
        ("e2e-tests-edge-cases", 100, False, "e2e-cache"),

        # Security and quality
        ("security-scan", 60, False, "security-cache"),
        ("sast-analysis", 50, False, "sast-cache"),
        ("dependency-check", 25, False, None),
        ("code-coverage", 35, False, "coverage-cache"),

        # Database and infrastructure
        ("db-migrations-test", 40, False, "db-cache"),
        ("infra-validate", 30, False, None),

        # Documentation and artifacts
        ("docs-build", 30, False, "docs-cache"),
        ("api-docs-generate", 20, False, None),

        # Performance and profiling
        ("performance-tests", 90, False, "perf-cache"),
        ("memory-profiler", 45, False, None),

        # Deployment staging
        ("deploy-staging", 120, False, None),
        ("smoke-tests-staging", 60, False, "smoke-cache"),
        ("health-check-staging", 25, False, None),
    ]

    jobs = []
    job_names = []

    # Create jobs with deterministic structure - first define all job names
    for i, (name, duration, parallelizable, cache_key) in enumerate(job_templates[:num_jobs]):
        job_names.append(name)

    # Now create the job list with realistic dependencies
    for i, (name, duration, parallelizable, cache_key) in enumerate(job_templates[:num_jobs]):
        dependencies = []

        # Define dependency chains
        if "integration" in name:
            # Integration tests depend on builds
            if "api" in name:
                dependencies = ["build-backend"]
            elif "web" in name:
                dependencies = ["build-frontend"]
            elif "worker" in name:
                dependencies = ["build-worker"]
        elif "e2e" in name:
            # E2E tests depend on docker build and previous stages
            dependencies = ["build-docker", "db-migrations-test"]
        elif "deploy" in name:
            # Deployment depends on all tests
            dependencies = ["e2e-tests-critical", "security-scan"]
        elif "smoke" in name:
            # Smoke tests depend on deployment
            dependencies = ["deploy-staging"]
        elif "build-docker" == name:
            # Docker build depends on all individual builds
            dependencies = ["build-frontend", "build-backend", "build-worker"]
        elif "performance-tests" == name:
            # Performance tests need the docker image
            dependencies = ["build-docker"]
        elif name in ["unit-tests-api", "unit-tests-web", "unit-tests-worker"]:
            # Unit tests depend on lint and typecheck
            dependencies = ["lint", "typecheck"]
        elif name in ["code-coverage", "sast-analysis"]:
            # Coverage and SAST run after unit tests
            dependencies = ["unit-tests-api", "unit-tests-web"]
        elif name == "db-migrations-test":
            # DB migrations after typecheck
            dependencies = ["typecheck"]
        elif name == "docs-build":
            # Docs can run after typecheck
            dependencies = ["typecheck"]
        elif name == "health-check-staging":
            # Health checks after smoke tests
            dependencies = ["smoke-tests-staging"]
        elif name in ["security-scan", "dependency-check"]:
            # Security runs early but after lint
            dependencies = ["lint"]
        elif name == "infra-validate":
            # Infrastructure validation early
            dependencies = ["typecheck"]
        elif name == "api-docs-generate":
            # API docs after build-backend
            dependencies = ["build-backend"]
        elif name == "memory-profiler":
            # Memory profiling after build
            dependencies = ["build-backend"]

        # Validate all dependencies exist in job_names, then filter to only jobs before this one
        invalid_deps = [d for d in dependencies if d not in job_names]
        if invalid_deps:
            print(f"Warning: Job '{name}' has invalid dependencies: {invalid_deps}", file=sys.stderr)

        # Filter to only include dependencies that exist AND come before this job in the list
        dependencies = [d for d in dependencies if d in job_names and job_names.index(d) < i]

        jobs.append({
            "name": name,
            "duration_seconds": duration,
            "dependencies": dependencies,
            "cache_key": cache_key,
            "parallelizable": parallelizable,
        })

    return jobs


def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare.py generate")
        sys.exit(1)

    if sys.argv[1] == "generate":
        pipeline = generate_pipeline(seed=42, num_jobs=30)

        with open("pipeline.json", "w") as f:
            json.dump(pipeline, f, indent=2)

        total_time = sum(job["duration_seconds"] for job in pipeline)
        print(f"Generated {len(pipeline)} jobs")
        print(f"Total sequential time: {total_time} seconds")
        print(f"Saved to pipeline.json")
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
