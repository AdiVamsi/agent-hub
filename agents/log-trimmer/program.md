# Log Trimmer — Research Program

Optimizing log filtering rules to reduce log volume while preserving important signals (errors, warnings, key events).

## Problem Statement

Production systems generate massive log volumes. Most logs are noise (DEBUG, routine INFO). The goal is to filter logs aggressively while keeping all critical signals (ERROR, FATAL, key WARN/INFO events) to reduce storage costs and improve observability.

**Baseline:** Keep everything = efficiency_score = 0.0
**Target:** Achieve efficiency_score >= 0.85-0.95 (drop 85-95% of noise while keeping 98%+ of signal)

## Evaluation Metric

```
efficiency_score = (noise_dropped / total_noise) * signal_kept_pct

where:
  - signal_kept_pct = signal_kept / total_signal
  - Must satisfy: signal_kept_pct >= 0.95 (else score = 0)
  - noise_dropped = noise entries correctly filtered out
  - noise_dropped / total_noise = % of noise dropped

In other words:
  - MUST keep >= 95% of all signal logs
  - THEN maximize % of noise dropped
  - Score = (noise % dropped) * (signal % kept)
```

## Log Data Structure

Each log entry has:
- `message` (str): the log line text
- `level` (str): DEBUG, INFO, WARN, ERROR, FATAL
- `source` (str): api, db, auth, cache, scheduler, worker
- `timestamp` (str): ISO timestamp
- `size_bytes` (int): 50-2000 bytes
- `is_signal` (bool): True = important, must keep; False = noise

### Distribution (500 logs)
- 40% DEBUG (~200)
- 30% INFO (~150)
- 15% WARN (~75)
- 10% ERROR (~50)
- 5% FATAL (~25)

### Signal Classification
- **Always signal:** All ERROR and FATAL logs
- **Conditional signal:**
  - WARN with keywords: timeout, retry, circuit
  - INFO with keywords: deploy, startup, shutdown, user_created
  - DEBUG: 5% random (stack traces, slow queries)
- **Everything else:** Noise
- **Ratio:** ~31% signal, ~69% noise

## Hypotheses to Test

### H1: Drop All DEBUG
**Intuition:** DEBUG logs are mostly noise. Maybe 5% are stack traces, but worth sacrificing?

**Implementation:**
```python
if entry["level"] == "DEBUG":
    return False
return True
```

**Expected:** Will drop ~40% of logs, but also drop ~8% of signal (the 5% random DEBUG signals). Score penalty.

---

### H2: Drop DEBUG Except from Specific Sources
**Intuition:** Maybe only certain sources (e.g., `db`, `auth`) emit important DEBUG logs.

**Implementation:**
```python
if entry["level"] == "DEBUG":
    return entry["source"] in ["db", "auth"]
return True
```

**Expected:** Smarter filtering; might preserve more signal.

---

### H3: Keep WARN+ Always
**Intuition:** Anything WARN or higher is important. Drop only DEBUG and INFO noise.

**Implementation:**
```python
level = entry["level"]
if level in ["ERROR", "FATAL", "WARN"]:
    return True
if level == "DEBUG":
    return False
# INFO: check message
return check_info_signal(entry)
```

**Expected:** Keeps all WARN/ERROR/FATAL. Filters noisy INFO. Good baseline.

---

### H4: Keyword-Based Signal Detection
**Intuition:** Certain keywords (error, fail, timeout, exception, deprecated) indicate signal even at DEBUG/INFO.

**Implementation:**
```python
signal_keywords = ["error", "fail", "timeout", "exception", "deprecated", "critical"]
for kw in signal_keywords:
    if kw in entry["message"].lower():
        return True

# Default to level-based rules
if entry["level"] in ["ERROR", "FATAL"]:
    return True
if entry["level"] == "WARN":
    return "timeout" in entry["message"].lower() or "retry" in entry["message"].lower()
return False
```

**Expected:** High recall on signal; may keep some noise with false-positive keywords.

---

### H5: Source-Based Rules
**Intuition:** Some sources (db, auth) have higher signal density. Others (cache, scheduler) are mostly noise.

**Implementation:**
```python
if entry["source"] in ["db", "auth"]:
    return True  # Always keep

if entry["source"] in ["cache"]:
    return entry["level"] in ["ERROR", "FATAL"]

if entry["source"] in ["api", "worker"]:
    return entry["level"] in ["ERROR", "FATAL", "WARN"]

return True
```

**Expected:** Aggressive filtering on noisy sources.

---

### H6: Message Length Heuristics
**Intuition:** Short messages are often boilerplate health checks ("OK", "Health check passed"). Long messages are often errors with stack traces.

**Implementation:**
```python
msg_len = len(entry["message"])
if msg_len < 30 and entry["level"] == "DEBUG":
    return False  # Likely boilerplate
if msg_len > 100:
    return True  # Likely important
return entry["level"] in ["ERROR", "FATAL", "WARN"]
```

**Expected:** Filters out short DEBUG logs (health checks, heartbeats).

---

### H7: Combine Level + Source + Message-Length Heuristics
**Intuition:** Use level severity, message length as quality signals, and source as a secondary factor.

**Implementation:**
```python
# Always keep high-severity logs
if entry["level"] in ["ERROR", "FATAL"]:
    return True

# WARN: keep if contains signal keywords
if entry["level"] == "WARN":
    return any(kw in entry["message"].lower() for kw in ["timeout", "retry", "circuit"])

# INFO: keep if contains deployment/lifecycle keywords
if entry["level"] == "INFO":
    return any(kw in entry["message"].lower() for kw in ["deploy", "startup", "shutdown", "user_created"])

# DEBUG: keep only if long (likely stack trace) or from high-signal sources
if entry["level"] == "DEBUG":
    msg_len = len(entry["message"])
    is_from_signal_source = entry["source"] in ["db", "auth"]
    return msg_len > 100 or is_from_signal_source

return False
```

**Expected:** Good balance of recall (catching signal) and precision (dropping noise).

---

### H8: Combination Rules (Weighted Scoring)
**Intuition:** Combine level, keywords, source, and message length into a weighted score.

**Implementation:**
```python
score = 0

# Level score
if entry["level"] == "FATAL":
    score += 10
elif entry["level"] == "ERROR":
    score += 8
elif entry["level"] == "WARN":
    score += 5
elif entry["level"] == "INFO":
    score += 2
else:  # DEBUG
    score += 0

# Source score
if entry["source"] in ["db", "auth"]:
    score += 3
elif entry["source"] in ["api"]:
    score += 1
else:
    score = max(0, score - 1)

# Keyword score
signal_kw = ["timeout", "retry", "circuit", "error", "fail"]
for kw in signal_kw:
    if kw in entry["message"].lower():
        score += 2

# Message length score
if len(entry["message"]) > 100:
    score += 2
if len(entry["message"]) < 20:
    score -= 1

return score >= 5
```

**Expected:** Balances multiple factors. Fine-tunable via weights.

---

### H9: Size-Aware Filtering
**Intuition:** Larger logs take more storage. Drop small noise logs first, keep large ERROR logs.

**Implementation:**
```python
# Always keep high-level signals
if entry["level"] in ["ERROR", "FATAL"]:
    return True
if entry["level"] == "WARN":
    return "timeout" in entry["message"].lower() or "retry" in entry["message"].lower()

# Drop small DEBUG logs (likely boilerplate)
if entry["level"] == "DEBUG" and entry["size_bytes"] < 100:
    return False

# Keep INFO only if important
if entry["level"] == "INFO":
    return any(kw in entry["message"].lower() for kw in ["deploy", "startup", "shutdown", "user_created"])

return False
```

**Expected:** Aggressive volume reduction while preserving signal.

---


## Experiment Plan

1. **Baseline**: evaluate() with default should_keep (keep all) → efficiency_score = 0.0
2. **H1-H9**: Implement each hypothesis, measure efficiency_score, volume_reduction_pct
3. **Combine Winners**: Take best hypotheses (e.g., H7 + H4) and iterate
4. **Tune Parameters**: Adjust thresholds, keyword lists, weights
5. **Validate**: Ensure signal_kept_pct >= 0.95 on every iteration

## Success Criteria

- **Minimum:** efficiency_score >= 0.50 (keep 95%+ signal, drop 50%+ noise)
- **Target:** efficiency_score >= 0.80 (keep 95%+ signal, drop 80%+ noise)
- **Stretch:** efficiency_score >= 0.90 (keep 98%+ signal, drop 90%+ noise)

## Tools

- `python prepare.py generate` → generate log_samples.json
- `python harness.py baseline` → measure baseline
- `python harness.py evaluate` → measure current filter_rules.py
- Edit `filter_rules.py` → implement hypotheses
