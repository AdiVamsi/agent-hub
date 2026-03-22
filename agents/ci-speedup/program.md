# CI Pipeline Optimizer — AutoResearch Program

## Objective
Minimize CI/CD pipeline total build time by optimizing job scheduling and parallelization.

**Metric:** `total_build_time` = sum of max(duration) per stage (lower is better)

**Baseline:** ~3600 seconds (all jobs sequential)

**Target:** ~400-800 seconds (proper parallelization + critical path optimization)

---

## Setup Phase

### 1. Create branch
```bash
git init
git config user.email "agent@example.com"
git config user.name "CI Optimizer Agent"
git add -A
git commit -m "Initial: baseline pipeline, ready for optimization"
```

### 2. Read files and understand the structure
- `pipeline.json`: 30 jobs with dependencies, durations, cache_keys, parallelizable flags
- `pipeline_config.py`: THE EDITABLE FILE — contains `optimize_pipeline(jobs) -> schedule`
- `harness.py`: Fixed evaluation harness (do NOT modify)
- Expected structure: each job has `name`, `duration_seconds`, `dependencies`, `cache_key`, `parallelizable`

### 3. Run baseline
```bash
python prepare.py generate
python harness.py baseline
```

Expected output: `BASELINE: total_build_time=XXXX.X`

Record the baseline value (should be ~3600 seconds).

### 4. Initialize results tracking
Create `results.tsv`:
```
iteration	strategy	total_build_time	improvement_pct	notes
0	baseline	3600.0	0.0	Sequential baseline
```

---

## Hypotheses to Test

### Hypothesis 1: Topological Sort + Greedy Parallelization
**Idea:** Build a dependency DAG, then schedule jobs level-by-level using topological layers.
- Jobs with no dependencies go in stage 1
- Jobs whose dependencies are all completed go in the next stage
- Within a stage, put as many jobs as possible (up to memory/resource limits)

**Expected improvement:** 30-40%

**Implementation:** Use a level-based topological sort; after finishing a stage, schedule all ready jobs in parallel.

### Hypothesis 2: Critical Path Analysis
**Idea:** Find the longest dependency chain (critical path). Schedule critical path jobs early in their own stages to minimize idle time on the critical path.
- Non-critical jobs can be sprinkled in empty slots

**Expected improvement:** 40-50%

**Implementation:** Compute critical path length for each job (longest path to end). Prioritize scheduling high-critical-path jobs.

### Hypothesis 3: Cache-Key Grouping
**Idea:** Jobs with the same `cache_key` share artifacts. Group them in adjacent stages to maximize cache hits and reduce redundancy.
- If multiple jobs generate/use the same cache_key, run them close together

**Expected improvement:** 10-20% (modest, but adds to other strategies)

**Implementation:** Build cache dependency graph; schedule jobs with shared cache_keys in overlapping stages if dependencies allow.

### Hypothesis 4: Parallelizable Flag Exploitation
**Idea:** Jobs marked `parallelizable=True` can run in the same stage without conflicts.
- Jobs marked `parallelizable=False` are sequential and should run alone or with very careful stage placement

**Expected improvement:** 5-15% (mostly captured by earlier hypotheses, but refinement)

**Implementation:** When building stages, prioritize fitting parallelizable jobs together.

### Hypothesis 5: Dependency Relaxation (Lower-Cost Approximation)
**Idea:** Some dependencies might be "soft" (not hard blocks). Experiment with relaxing them slightly:
- If a job depends on A and B, but A takes much longer, run job early with just B done (cache miss penalty < time saved)
- This is risky, so use only for jobs explicitly marked as suitable

**Expected improvement:** 5-15% (high risk; test on safe jobs only)

**Implementation:** Add a flag `relaxable_deps=True` on safe jobs; allow relaxed scheduling.

### Hypothesis 6: Stage Compaction
**Idea:** Minimize the number of stages by packing jobs more aggressively.
- Instead of one job per stage, fit as many independent jobs as possible per stage
- Use a greedy bin-packing approach

**Expected improvement:** 20-35%

**Implementation:** For each stage, greedily add as many ready jobs as possible; advance to next stage only when no more can fit.

### Hypothesis 7: Weighted Longest Processing Time (LPT)
**Idea:** Schedule longer-duration jobs first (within dependency constraints).
- Longer jobs should run early to leave time for other jobs to complete in parallel

**Expected improvement:** 10-25%

**Implementation:** When deciding which ready jobs to schedule next, prioritize by duration (longest first).

### Hypothesis 8: Multi-Objective Optimization
**Idea:** Combine strategies: topological sort + critical path + LPT + cache grouping.
- Run all earlier hypotheses; apply them in layers

**Expected improvement:** 60-75%

**Implementation:** Build a composite scheduler that applies all strategies together.

### Hypothesis 9: Machine Learning / Heuristic Search
**Idea:** Use simulated annealing or genetic algorithm to search the schedule space.
- Start with a greedy schedule; perturb and accept improvements

**Expected improvement:** 65-80%

**Implementation:** Define a perturbation function (swap jobs in schedule); accept if total_time improves.

### Hypothesis 10: Constraint Relaxation with Backtracking
**Idea:** If a greedy scheduler gets stuck, try relaxing constraints, schedule, then back-propagate

**Expected improvement:** 50-70%

---

## Commit/Revert Protocol

After each experiment:

1. Run evaluation:
   ```bash
   python harness.py evaluate
   ```
   Expected output: `RESULT: total_build_time=X.X improvement_pct=Y.Y`

2. If improvement > 0:
   ```bash
   git add pipeline_config.py
   git commit -m "hypothesis-N: +X% improvement (total_time=Y.Y)"
   ```
   Add result to `results.tsv`

3. If no improvement or regression:
   ```bash
   git checkout pipeline_config.py
   ```
   Move to next hypothesis.

4. After each iteration, update `results.tsv`:
   ```
   iteration	strategy	total_build_time	improvement_pct	notes
   ...
   5	critical-path	850.0	76.3	Critical path analysis + greedy parallelization
   ```

---

## Constraints

- **ONLY modify:** `pipeline_config.py`
- **DO NOT modify:** `harness.py`, `prepare.py`, `pipeline.json`
- **All changes:** Must respect dependency constraints (no cycles, no invalid orderings)
- **Validation:** Harness will reject invalid schedules (metric = 999999)

---

## Success Criteria

- Baseline: ~3600 seconds
- Target achieved: < 800 seconds (78% improvement)
- Stretch goal: < 400 seconds (89% improvement)

---

## Experiment Workflow

```
1. Read pipeline.json and understand structure
2. Run baseline
3. For each hypothesis (1-10):
   a. Design the scheduling algorithm
   b. Implement in optimize_pipeline()
   c. Run harness.py evaluate
   d. If improvement, commit; else revert
   e. Record in results.tsv
4. Analyze results, identify best combination
5. Try multi-objective combination
6. Final result and summary
```

---

## Notes

- Dependency DAG is acyclic (no circular dependencies)
- Some jobs are independent, some form chains
- Cache sharing is optional but can reduce redundancy
- The harness computes total_build_time deterministically
- Determinism: same schedule always produces same total_time
