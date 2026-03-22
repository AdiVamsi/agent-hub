"""Log Trimmer — editable file.

Available data: log_samples.json with 500 log entries, each having:
  message, level, source, timestamp, size_bytes, is_signal

Your job: implement should_keep(entry) that returns True/False.
Goal: keep all signal logs (is_signal=True) while dropping as much noise as possible.

Metric: efficiency_score = (noise_dropped / total_noise) * signal_kept_pct
  where signal_kept_pct = signal_kept / total_signal (must be >= 0.95 or score = 0)
  and noise_dropped = noise entries correctly filtered out

Basically: drop the most noise while keeping >= 95% of signal. HIGHER is better.
Baseline: keep everything = 0% noise dropped = 0.0 score.
"""

def should_keep(entry: dict) -> bool:
    """Return True to keep this log entry, False to drop it.

    Baseline: keep everything.
    """
    return True
