# LLM Cost Pilot — Research Program

You are an autonomous research agent optimizing LLM API routing costs. Your goal is to minimize `cost_per_quality` by intelligently routing requests to cheaper models when quality won't suffer.

## Setup (run once at start)

1. Create a git branch from current HEAD:
   ```
   git checkout -b autoresearch/<descriptive-tag>
   ```

2. Read these repo files to understand the system:
   - This file (`program.md`) — your instructions
   - `README.md` — overview of the agent
   - `harness.py` — the evaluation infrastructure (DO NOT MODIFY)
   - `router.py` — the file you WILL modify
   - `models.yaml` — model catalog with pricing and tiers

3. Verify traffic data exists:
   ```
   ls traffic/sample.jsonl
   ```
   If missing, tell the human to run: `python prepare.py generate`

4. Initialize `results.tsv` with header:
   ```
   echo -e "experiment_id\tdescription\ttotal_cost\tavg_quality\tcost_per_quality\tsavings_pct\tstatus\ttimestamp" > results.tsv
   ```

5. Run baseline evaluation:
   ```
   python harness.py evaluate > eval.log 2>&1
   ```
   Read the RESULT line: `grep "^RESULT:" eval.log`
   Record the baseline in `results.tsv` with status "baseline".

## Experiment Loop (repeat indefinitely)

For each experiment:

### 1. Form a Hypothesis

Pick ONE idea to test. Suggested areas to explore (start simple, get creative):

- **Request classification by complexity**: Use token count, message count, presence of tools to classify request difficulty
- **Model downgrading for simple tasks**: Translate, extract, classify, yes/no → nano tier models
- **Model downgrading for medium tasks**: Summarize, basic Q&A, short generation → small/medium tier
- **Caching rules**: Detect repeated or similar prompts, return cached results
- **Batch eligibility**: Detect async-tagged requests that can use batch pricing
- **Structured output routing**: JSON/structured output requests → cheaper models handle these fine
- **Conversation length routing**: Short conversations (1-2 messages) vs long (6+ messages)
- **Content-based routing**: Analyze message content keywords to estimate required capability
- **Provider cost arbitrage**: Same tier, different providers have different costs — pick cheapest
- **Hybrid rules**: Combine multiple signals for smarter routing

### 2. Edit router.py

Implement your hypothesis in `router.py`. Keep the code clean and well-commented so future experiments can build on it.

### 3. Run the Experiment

```
python harness.py evaluate > eval.log 2>&1
```

Redirect ALL output to the log. Do NOT let it flood your context window.

### 4. Check Results

```
grep "^RESULT:" eval.log
```

This gives you: `total_cost`, `avg_quality`, `cost_per_quality`, `savings_pct`, `requests`.

### 5. Commit or Revert

**If `cost_per_quality` improved AND `avg_quality >= 0.85`:**
```
git add router.py
git commit -m "experiment N: <description> — saved X%, quality Y"
```
Append to `results.tsv` with status `kept`.

**If quality dropped below 0.85 OR cost_per_quality got worse:**
```
git reset --hard HEAD
```
Append to `results.tsv` with status `reverted`.

### 6. Next Experiment

Move on to the next hypothesis. Try to be diverse — don't repeat failed approaches without a meaningful twist. Build on successful experiments.

## Constraints

- **ONLY modify `router.py`**. Never touch `harness.py`, `prepare.py`, or `models.yaml`.
- **Quality floor**: `avg_quality` must stay >= 0.85.
- **Keep it readable**: Future experiments build on your code. Comment your routing logic.
- **Speed**: Each experiment should complete in under 60 seconds.
- **Be systematic**: Log everything in `results.tsv` so we can analyze trends later.
