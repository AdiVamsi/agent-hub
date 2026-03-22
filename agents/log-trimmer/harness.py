#!/usr/bin/env python3
"""Log Trimmer — Evaluation Harness.

Evaluates filter_rules.py against log_samples.json.
Computes efficiency_score and volume reduction metrics.
"""

import json
import sys
from filter_rules import should_keep

def baseline():
    """Run with baseline filter (keep everything)."""
    # Temporarily replace should_keep with baseline
    from filter_rules import should_keep as _
    import filter_rules
    original = filter_rules.should_keep
    filter_rules.should_keep = lambda entry: True

    evaluate()

    filter_rules.should_keep = original

def evaluate():
    """Load logs, apply filter, compute metrics."""
    # Load log samples
    try:
        with open("log_samples.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        print("ERROR: log_samples.json not found. Run: python prepare.py generate")
        sys.exit(1)

    # Categorize logs
    signal_logs = [log for log in logs if log["is_signal"]]
    noise_logs = [log for log in logs if not log["is_signal"]]

    total_signal = len(signal_logs)
    total_noise = len(noise_logs)
    total_bytes = sum(log["size_bytes"] for log in logs)

    # Apply filter
    signal_kept = sum(1 for log in signal_logs if should_keep(log))
    signal_dropped = total_signal - signal_kept
    noise_kept = sum(1 for log in noise_logs if should_keep(log))
    noise_dropped = total_noise - noise_kept

    bytes_kept = sum(log["size_bytes"] for log in logs if should_keep(log))
    bytes_dropped = total_bytes - bytes_kept

    # Compute metrics
    signal_kept_pct = signal_kept / total_signal if total_signal > 0 else 1.0

    # Penalty: if we drop more than 5% of signal, score = 0
    if signal_kept_pct < 0.95:
        efficiency_score = 0.0
    else:
        efficiency_score = (noise_dropped / total_noise) * signal_kept_pct if total_noise > 0 else signal_kept_pct

    volume_reduction_pct = (bytes_dropped / total_bytes) * 100 if total_bytes > 0 else 0

    # Print results
    print(f"\n{'='*60}")
    print(f"Evaluation Results")
    print(f"{'='*60}")
    print(f"\nSignal Logs (is_signal=True):")
    print(f"  Total: {total_signal}")
    print(f"  Kept: {signal_kept} ({signal_kept_pct*100:.1f}%)")
    print(f"  Dropped: {signal_dropped}")

    print(f"\nNoise Logs (is_signal=False):")
    print(f"  Total: {total_noise}")
    print(f"  Kept: {noise_kept}")
    print(f"  Dropped: {noise_dropped} ({noise_dropped/total_noise*100:.1f}% of noise)")

    print(f"\nVolume:")
    print(f"  Total: {total_bytes:,} bytes ({total_bytes/1024:.1f}KB)")
    print(f"  Kept: {bytes_kept:,} bytes ({bytes_kept/1024:.1f}KB)")
    print(f"  Dropped: {bytes_dropped:,} bytes ({bytes_dropped/1024:.1f}KB)")
    print(f"  Reduction: {volume_reduction_pct:.1f}%")

    print(f"\nMetrics:")
    print(f"  Signal Kept %: {signal_kept_pct*100:.1f}%")
    print(f"  Noise Dropped %: {noise_dropped/total_noise*100:.1f}%")
    print(f"  Efficiency Score: {efficiency_score:.4f}")

    if signal_kept_pct < 0.95:
        print(f"\n  WARNING: Dropped too much signal ({100-signal_kept_pct*100:.1f}% dropped).")
        print(f"  Score = 0.0 (must keep >= 95% of signal)")

    print(f"\nRESULT: efficiency_score={efficiency_score:.4f} improvement_pct={volume_reduction_pct:.1f}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "baseline":
            baseline()
        elif sys.argv[1] == "evaluate":
            evaluate()
        else:
            print("Usage: python harness.py [baseline|evaluate]")
            sys.exit(1)
    else:
        evaluate()
