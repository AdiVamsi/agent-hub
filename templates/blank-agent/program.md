# [Agent Name] — Research Program

You are an autonomous research agent optimizing [WHAT YOU'RE OPTIMIZING].

## Setup (run once at start)

1. Create a git branch:
   ```
   git checkout -b autoresearch/<descriptive-tag>
   ```

2. Read the repo files to understand the system:
   - This file (`program.md`)
   - `editable.py` — the file you WILL modify
   - `harness.py` — the evaluation infrastructure (DO NOT MODIFY)

3. Verify data exists. If not, tell the human to run: `python prepare.py generate`

4. Initialize `results.tsv`:
   ```
   echo -e "experiment_id\tdescription\t[YOUR_METRIC]\tstatus\ttimestamp" > results.tsv
   ```

5. Run baseline: `python harness.py evaluate > eval.log 2>&1`

## Experiment Loop (repeat indefinitely)

### 1. Form a Hypothesis
[Describe the kinds of hypotheses the agent should explore]

### 2. Edit editable.py
Implement your hypothesis. Keep the code clean and well-commented.

### 3. Run the Experiment
```
python harness.py evaluate > eval.log 2>&1
```

### 4. Check Results
```
grep "^RESULT:" eval.log
```

### 5. Commit or Revert
- If [YOUR_METRIC] improved: `git commit`
- If not: `git reset --hard HEAD`

## Constraints
- ONLY modify `editable.py`
- [YOUR QUALITY CONSTRAINTS]
- Each experiment should complete in under 60 seconds
