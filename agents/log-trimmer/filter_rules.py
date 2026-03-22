"""Log Trimmer — editable file.

Available data: log_samples.json with 500 log entries.
Each entry has the following fields (is_signal is NOT available):
  message (str): the log line text
  level (str): DEBUG, INFO, WARN, ERROR, FATAL
  source (str): api, db, auth, cache, scheduler, worker
  timestamp (str): ISO timestamp
  size_bytes (int): 50-2000 bytes

Your job: implement should_keep(entry) that returns True/False.
Goal: keep all signal logs while dropping as much noise as possible.

Metric: efficiency_score = (noise_dropped / total_noise) * signal_kept_pct
  where signal_kept_pct = signal_kept / total_signal (must be >= 0.95 or score = 0)
  and noise_dropped = noise entries correctly filtered out

Basically: drop the most noise while keeping >= 95% of signal. HIGHER is better.
Baseline: keep everything = 0% noise dropped = 0.0 score.
"""

def should_keep(entry: dict) -> bool:
    """Return True to keep this log entry, False to drop it.

    Available fields: message, level, source, timestamp, size_bytes
    (is_signal is NOT available to prevent cheating)

    Baseline: keep everything.
    """
    # Verify is_signal is not in entry (safety check)
    if "is_signal" in entry:
        raise ValueError("is_signal should not be passed to should_keep()")
    return True
