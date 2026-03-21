# code-autoresearch — Research Program

You are an autonomous research agent optimizing production Python code for maximum throughput. Your goal is to maximize `requests_per_second` by finding and fixing performance problems in `target.py`.

## Setup (run once at start)

1. Create a git branch from current HEAD:
   ```
   git checkout -b autoresearch/<descriptive-tag>
   ```

2. Read these repo files to understand the system:
   - This file (`program.md`) — your instructions
   - `README.md` — overview of the agent
   - `harness.py` — the benchmark infrastructure (DO NOT MODIFY)
   - `target.py` — the code you WILL optimize
   - `workload.json` — what gets benchmarked

3. Initialize `results.tsv` with header:
   ```
   echo -e "experiment_id\tdescription\trequests_per_second\tlatency_p50_ms\tlatency_p99_ms\timprovement_pct\tstatus\ttimestamp" > results.tsv
   ```

4. Run baseline benchmark:
   ```
   python harness.py benchmark > bench.log 2>&1
   ```
   Read the RESULT line: `grep "^RESULT:" bench.log`
   Record the baseline in `results.tsv` with status "baseline".

5. Study `target.py` carefully. Profile it mentally. Identify the hot paths and bottlenecks before making any changes.

## Experiment Loop (repeat indefinitely)

For each experiment:

### 1. Form a Hypothesis

Study `target.py` and pick ONE optimization to try. Suggested areas:

- **Algorithm improvements**: Replace O(n²) loops with O(n log n) or O(n) alternatives. Look for nested loops that can be flattened with better data structures.
- **Caching**: Add in-memory caching (`functools.lru_cache`, dict caches) for computations that get repeated across calls. Look for functions that recompute the same thing every invocation.
- **Database/lookup optimization**: Replace N+1 patterns (scanning a full list to find one item) with dict-based lookups. Build index dicts once, reuse them.
- **Data structure changes**: Use sets instead of lists for membership tests. Use `defaultdict` for grouping. Use generators instead of materializing large lists.
- **Sorting optimization**: Replace hand-written sorts (bubble sort, etc.) with Python's built-in `sorted()` which uses Timsort.
- **Lazy evaluation**: Don't compute values that aren't needed for the final result. Short-circuit early when possible.
- **String optimization**: Use `''.join()` instead of `+=` concatenation in loops. Use f-strings instead of format() or %.
- **Computation elimination**: Remove redundant calculations. Precompute constants. Avoid recomputing aggregates (sum, count, avg) multiple times over the same data.
- **Batching**: Replace one-at-a-time processing with batch operations where possible.

### 2. Edit target.py

Implement ONE optimization at a time. Keep changes focused and well-commented so you can attribute performance gains to specific changes.

### 3. Run the Benchmark

```
python harness.py benchmark > bench.log 2>&1
```

Redirect ALL output to the log. Do NOT let it flood your context window.

### 4. Check Results

```
grep "^RESULT:" bench.log
```

This gives you: `requests_per_second`, `latency_p50_ms`, `latency_p99_ms`, `improvement_pct`.

**IMPORTANT**: If the result says `FAILED — correctness check failed`, your optimization broke the API's behavior. The outputs must be identical to the baseline.

### 5. Commit or Revert

**If `requests_per_second` improved AND correctness checks passed:**
```
git add target.py
git commit -m "experiment N: <description> — X.X req/s → Y.Y req/s (+Z%)"
```
Append to `results.tsv` with status `kept`.

**If `requests_per_second` dropped, stayed the same, OR correctness failed:**
```
git reset --hard HEAD
```
Append to `results.tsv` with status `reverted`.

### 6. Next Experiment

Move on to the next optimization. Build on previous successful changes. Try to be diverse in approaches — don't just keep tweaking the same function.

## Constraints

- **ONLY modify `target.py`**. Never touch `harness.py`, `prepare.py`, or `workload.json`.
- **Correctness is sacred**: All function outputs must remain identical to baseline. The harness verifies this automatically.
- **Keep it readable**: No obfuscated micro-optimizations. The code should be cleaner AND faster.
- **Each benchmark should complete in under 30 seconds**.
- **Pure Python**: Don't add external dependencies. Only standard library is allowed.
- **Be systematic**: Log everything in `results.tsv`. Note what you tried and why.
